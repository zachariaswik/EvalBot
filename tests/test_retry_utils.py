"""Tests for src/retry_utils.py — retry/fallback/timeout logic."""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest

import src.retry_utils as ru
from src.retry_utils import (
    AgentTimeoutError,
    FallbackState,
    StartupTimeoutError,
    _classify_error,
    _execute_with_timeout,
    _is_connection_error,
    execute_with_retry,
    get_fallback_stats,
    reset_fallback_state,
    reset_startup_timer,
    should_attempt_recovery,
)


# ---------------------------------------------------------------------------
# Error classification
# ---------------------------------------------------------------------------

class TestClassifyError:
    def test_agent_timeout_error(self):
        assert _classify_error(AgentTimeoutError("timed out")) == "agent_timeout"

    def test_timeout_keyword(self):
        assert _classify_error(Exception("Request timed out after 30s")) == "timeout"

    def test_timed_out_keyword(self):
        assert _classify_error(Exception("connection timed out")) in ("timeout", "connection_reset")

    def test_connection_reset(self):
        assert _classify_error(Exception("connection reset by peer")) == "connection_reset"

    def test_502_server_error(self):
        assert _classify_error(Exception("502 Bad Gateway")) == "server_error"

    def test_503_server_error(self):
        assert _classify_error(Exception("503 Service Unavailable")) == "server_error"

    def test_504_server_error(self):
        # "504 gateway error" (no "timeout" word) → server_error
        assert _classify_error(Exception("504 gateway error")) == "server_error"

    def test_504_gateway_timeout_classified_as_timeout(self):
        # "504 Gateway Timeout" contains the word "timeout", which is checked first
        # in _classify_error, so it returns "timeout", not "server_error".
        assert _classify_error(Exception("504 Gateway Timeout")) == "timeout"

    def test_other_error(self):
        assert _classify_error(ValueError("invalid input")) == "other"
        assert _classify_error(RuntimeError("unexpected state")) == "other"


# ---------------------------------------------------------------------------
# Connection error detection
# ---------------------------------------------------------------------------

class TestIsConnectionError:
    def test_connection_reset(self):
        assert _is_connection_error(Exception("connection reset by peer"))

    def test_errno_54(self):
        assert _is_connection_error(Exception("errno 54 connection reset"))

    def test_errno_60(self):
        assert _is_connection_error(Exception("errno 60 operation timed out"))

    def test_apiconnectionerror(self):
        assert _is_connection_error(Exception("APIConnectionError: failed"))

    def test_readtimeout(self):
        assert _is_connection_error(Exception("ReadTimeout occurred"))

    def test_invalid_response(self):
        assert _is_connection_error(Exception("invalid response from server"))

    def test_not_connection_error_value_error(self):
        assert not _is_connection_error(ValueError("bad input"))

    def test_not_connection_error_auth_fail(self):
        assert not _is_connection_error(Exception("authentication failed"))

    def test_not_connection_error_rate_limit(self):
        assert not _is_connection_error(Exception("rate limit exceeded (429)"))


# ---------------------------------------------------------------------------
# Fallback state management
# ---------------------------------------------------------------------------

class TestFallbackState:
    def setup_method(self):
        reset_fallback_state()

    def test_reset_clears_active(self):
        ru._fallback_state.active = True
        reset_fallback_state()
        assert not ru._fallback_state.active

    def test_reset_clears_fallback_count(self):
        ru._fallback_state.fallback_count = 5
        reset_fallback_state()
        assert ru._fallback_state.fallback_count == 0

    def test_reset_startup_timer(self):
        ru._startup_start_time = 12345.0
        reset_startup_timer()
        assert ru._startup_start_time is None


class TestShouldAttemptRecovery:
    def setup_method(self):
        reset_fallback_state()

    def test_returns_false_when_not_in_fallback(self):
        ru._fallback_state.active = False
        assert not should_attempt_recovery()

    def test_returns_false_when_insufficient_successes(self):
        ru._fallback_state.active = True
        ru._fallback_state.consecutive_successes = 1  # below RECOVERY_CHECK_INTERVAL (3)
        ru._fallback_state.last_failure_time = time.time() - 9999  # cooldown passed
        assert not should_attempt_recovery()

    def test_returns_false_when_cooldown_not_elapsed(self):
        from src.config import RECOVERY_CHECK_INTERVAL, RECOVERY_COOLDOWN
        ru._fallback_state.active = True
        ru._fallback_state.consecutive_successes = RECOVERY_CHECK_INTERVAL
        ru._fallback_state.last_failure_time = time.time()  # just now
        assert not should_attempt_recovery()

    def test_returns_true_when_ready(self):
        from src.config import RECOVERY_CHECK_INTERVAL
        ru._fallback_state.active = True
        ru._fallback_state.consecutive_successes = RECOVERY_CHECK_INTERVAL
        ru._fallback_state.last_failure_time = time.time() - 9999  # well past cooldown
        assert should_attempt_recovery()


# ---------------------------------------------------------------------------
# Timeout execution
# ---------------------------------------------------------------------------

class TestExecuteWithTimeout:
    def test_success_no_timeout(self):
        result = _execute_with_timeout(lambda: 42, timeout=None)
        assert result == 42

    def test_success_with_generous_timeout(self):
        result = _execute_with_timeout(lambda: "hello", timeout=10)
        assert result == "hello"

    def test_raises_agent_timeout_error_on_slow_func(self):
        def slow():
            time.sleep(10)
            return "done"
        with pytest.raises(AgentTimeoutError):
            _execute_with_timeout(slow, timeout=1)

    def test_propagates_exceptions(self):
        with pytest.raises(ValueError, match="boom"):
            _execute_with_timeout(lambda: (_ for _ in ()).throw(ValueError("boom")), timeout=5)


# ---------------------------------------------------------------------------
# execute_with_retry
# ---------------------------------------------------------------------------

class TestExecuteWithRetry:
    def setup_method(self):
        reset_fallback_state()
        reset_startup_timer()

    def test_success_on_first_attempt(self):
        result = execute_with_retry(
            func=lambda: "great success",
            model_name="openai/gpt-4o",
            agent_number=1,
        )
        assert result["result"] == "great success"
        assert result["retry_count"] == 0
        assert not result["fallback_occurred"]
        assert not result["recovery_occurred"]
        assert result["intended_model"] == "openai/gpt-4o"
        assert result["actual_model"] == "openai/gpt-4o"

    def test_non_connection_error_raises_immediately(self):
        """Non-connection errors should not be retried."""
        call_count = [0]

        def raises_value_error():
            call_count[0] += 1
            raise ValueError("bad schema")

        with pytest.raises(ValueError, match="bad schema"):
            execute_with_retry(
                func=raises_value_error,
                model_name="openai/gpt-4o",
                agent_number=1,
            )
        # Should fail fast, not retry
        assert call_count[0] == 1

    def test_connection_error_retries_and_succeeds(self):
        call_count = [0]

        def flaky():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("connection reset by peer")
            return "recovered"

        with patch("src.retry_utils.time.sleep"):
            result = execute_with_retry(
                func=flaky,
                model_name="openai/gpt-4o",
                agent_number=1,
            )

        assert result["result"] == "recovered"
        assert result["retry_count"] >= 2

    def test_all_retries_exhausted_triggers_fallback(self):
        """After all primary retries fail, the fallback function is used."""
        fallback_called = [False]

        def always_fails():
            raise Exception("connection reset by peer")

        def fallback_func():
            fallback_called[0] = True
            return "fallback success"

        with patch("src.retry_utils.time.sleep"):
            result = execute_with_retry(
                func=always_fails,
                model_name="openai/gpt-4o",
                agent_number=1,
                fallback_func=fallback_func,
            )

        assert result["result"] == "fallback success"
        assert result["fallback_occurred"] is True
        assert fallback_called[0]

    def test_result_metadata_on_fallback(self):
        """RetryResult fields are correct when fallback is used."""
        from src.config import get_fallback_model_for_agent

        def always_fails():
            raise Exception("connection reset")

        def fallback():
            return "done"

        with patch("src.retry_utils.time.sleep"):
            result = execute_with_retry(
                func=always_fails,
                model_name="openai/primary",
                agent_number=1,
                fallback_func=fallback,
            )

        assert result["intended_model"] == "openai/primary"
        assert result["actual_model"] == get_fallback_model_for_agent(1)
        assert result["fallback_occurred"] is True

    def test_startup_timeout_raises_before_retry(self, monkeypatch):
        """StartupTimeoutError is raised if total budget exceeded."""
        # Set startup timer to far in the past
        ru._startup_start_time = time.time() - 99999

        with pytest.raises(StartupTimeoutError):
            execute_with_retry(
                func=lambda: "ok",
                model_name="openai/gpt-4o",
                agent_number=1,
            )

    def test_agent_timeout_triggers_fallback(self):
        """AgentTimeoutError skips retries and goes straight to fallback."""
        fallback_called = [False]

        def slow_agent():
            raise AgentTimeoutError("exceeded 7 minutes")

        def fallback():
            fallback_called[0] = True
            return "fast fallback"

        with patch("src.retry_utils.time.sleep"):
            result = execute_with_retry(
                func=slow_agent,
                model_name="openai/slow",
                agent_number=1,
                fallback_func=fallback,
            )

        assert fallback_called[0]
        assert result["result"] == "fast fallback"


# ---------------------------------------------------------------------------
# Error models
# ---------------------------------------------------------------------------

class TestErrorModels:
    def test_agent_timeout_is_exception(self):
        e = AgentTimeoutError("timed out after 420s")
        assert isinstance(e, Exception)
        assert "420" in str(e)

    def test_startup_timeout_stores_elapsed_and_limit(self):
        e = StartupTimeoutError(elapsed=650.0, limit=600.0)
        assert e.elapsed == 650.0
        assert e.limit == 600.0

    def test_startup_timeout_custom_message(self):
        e = StartupTimeoutError(elapsed=100.0, limit=60.0, message="custom msg")
        assert str(e) == "custom msg"

    def test_startup_timeout_default_message(self):
        e = StartupTimeoutError(elapsed=100.0, limit=60.0)
        assert "100" in str(e)
        assert "60" in str(e)


# ---------------------------------------------------------------------------
# get_fallback_stats
# ---------------------------------------------------------------------------

class TestGetFallbackStats:
    def setup_method(self):
        reset_fallback_state()

    def test_initial_state(self):
        stats = get_fallback_stats()
        assert stats["fallback_active"] is False
        assert stats["fallback_count"] == 0
        assert stats["consecutive_successes"] == 0
        assert stats["primary_model"] is None

    def test_reflects_fallback_activation(self):
        ru._fallback_state.active = True
        ru._fallback_state.primary_model = "openai/primary"
        ru._fallback_state.fallback_count = 2
        stats = get_fallback_stats()
        assert stats["fallback_active"] is True
        assert stats["primary_model"] == "openai/primary"
        assert stats["fallback_count"] == 2
