"""Retry and fallback utilities for LLM API calls."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from threading import Thread
from typing import Any, Callable, TypedDict

from .config import (
    AGENT_TIMEOUT,
    FALLBACK_MODEL,
    RECOVERY_CHECK_INTERVAL,
    RECOVERY_COOLDOWN,
    RETRY_ATTEMPTS,
    RETRY_BASE_DELAY,
    TOTAL_STARTUP_TIMEOUT,
    get_fallback_model_for_agent,
)


class RetryResult(TypedDict):
    """Result of retry execution with metadata."""
    result: Any
    intended_model: str
    actual_model: str
    retry_count: int
    fallback_occurred: bool
    recovery_occurred: bool
    error_type: str | None


class AgentTimeoutError(Exception):
    """Raised when an agent exceeds the configured AGENT_TIMEOUT."""
    pass


class StartupTimeoutError(Exception):
    """Raised when a startup exceeds the TOTAL_STARTUP_TIMEOUT budget."""
    def __init__(self, elapsed: float, limit: float, message: str | None = None):
        self.elapsed = elapsed
        self.limit = limit
        self.message = message or (
            f"Startup exceeded time limit: {int(elapsed)}s elapsed (limit: {int(limit)}s). "
            f"All model retries failed."
        )
        super().__init__(self.message)


@dataclass
class FallbackState:
    """Tracks fallback model usage and recovery attempts."""
    active: bool = False
    primary_model: str | None = None
    fallback_count: int = 0
    last_failure_time: float = 0.0
    consecutive_successes: int = 0


# Thread-local storage: each worker thread gets its own FallbackState and startup timer.
_tls = threading.local()


def _fs() -> FallbackState:
    """Return this thread's FallbackState, creating one if needed."""
    if not hasattr(_tls, "fallback_state"):
        _tls.fallback_state = FallbackState()
    return _tls.fallback_state


def _get_startup_start_time() -> float | None:
    return getattr(_tls, "startup_start_time", None)


def _set_startup_start_time(t: float | None) -> None:
    _tls.startup_start_time = t


def reset_fallback_state() -> None:
    """Reset fallback state for the calling thread (call at start of new batch or startup)."""
    _tls.fallback_state = FallbackState()
    _tls.startup_start_time = None


def reset_startup_timer() -> None:
    """Reset the per-startup timer for the calling thread (call before each startup)."""
    _set_startup_start_time(None)


def should_attempt_recovery() -> bool:
    """Check if we should try switching back to primary model."""
    if not _fs().active:
        return False

    # Need enough consecutive successes
    if _fs().consecutive_successes < RECOVERY_CHECK_INTERVAL:
        return False

    # Need to wait for cooldown period
    elapsed = time.time() - _fs().last_failure_time
    return elapsed >= RECOVERY_COOLDOWN


def _execute_with_timeout(func: Callable[[], Any], timeout: int | None) -> Any:
    """Execute a function with a timeout limit using a background thread.

    Args:
        func: Function to execute
        timeout: Maximum seconds to allow (None to disable timeout)

    Returns:
        Function result

    Raises:
        AgentTimeoutError: If execution exceeds timeout limit
    """
    if timeout is None:
        return func()

    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func()
        except Exception as e:
            exception[0] = e

    thread = Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        # Thread is still running - it timed out
        raise AgentTimeoutError(
            f"Agent execution exceeded timeout limit of {timeout} seconds"
        )

    if exception[0] is not None:
        raise exception[0]

    return result[0]


def _classify_error(e: Exception) -> str:
    """Classify an exception into an error type for logging."""
    error_str = str(e).lower()
    if isinstance(e, AgentTimeoutError):
        return "agent_timeout"
    if "timeout" in error_str or "timed out" in error_str:
        return "timeout"
    if "connection" in error_str or "reset" in error_str:
        return "connection_reset"
    if any(code in error_str for code in ["502", "503", "504"]):
        return "server_error"
    return "other"


def _is_connection_error(e: Exception) -> bool:
    """Check if an exception is a retryable connection error."""
    error_str = str(e).lower()
    return any(
        err in error_str
        for err in [
            "connection", "reset", "errno 54", "errno 60",
            "apiconnectionerror", "readtimeout", "invalid response",
        ]
    )


def execute_with_retry(
    func: Callable[[], Any],
    model_name: str,
    agent_number: int,
    silent: bool = True,
    fallback_func: Callable[[], Any] | None = None,
) -> RetryResult:
    """
    Execute a function with retry logic and automatic fallback.

    Retry flow:
    1. Connection errors get exponential backoff retries (2, 4, 8, 16, 32s).
    2. If all retries exhausted OR agent times out (AGENT_TIMEOUT), switch to
       fallback model via ``fallback_func``.
    3. The total startup budget (TOTAL_STARTUP_TIMEOUT) is checked before every
       attempt; exceeding it raises StartupTimeoutError.

    Args:
        func: Function to execute (typically crew.kickoff for primary model)
        model_name: Primary model being used
        agent_number: Agent number (for logging and fallback model selection)
        silent: If True, suppress error messages during retries
        fallback_func: Function to execute with fallback model. If None, ``func``
            is reused (legacy behaviour — model doesn't actually change).

    Returns:
        RetryResult dict with result and execution metadata

    Raises:
        Last exception if all retries and fallback fail
        StartupTimeoutError: If total startup time exceeds TOTAL_STARTUP_TIMEOUT
    """
    # Record start time on first call for this startup (per-thread)
    if _get_startup_start_time() is None:
        _set_startup_start_time(time.time())

    # Get the appropriate fallback model for this agent
    fallback_model = get_fallback_model_for_agent(agent_number)

    # Track metadata for this execution
    retry_count = 0
    fallback_occurred = False
    recovery_occurred = False
    error_type = None

    # Determine which model to use
    if should_attempt_recovery():
        attempt_model = _fs().primary_model
        recovery_attempt = True
        if not silent:
            print(f"    ↻ Attempting recovery to primary model...")
    elif _fs().active:
        attempt_model = fallback_model
        recovery_attempt = False
    else:
        attempt_model = model_name
        recovery_attempt = False

    last_error = None

    # Check if we've already exceeded total startup timeout before even trying
    elapsed = time.time() - _get_startup_start_time()
    if elapsed >= TOTAL_STARTUP_TIMEOUT:
        raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)

    # --- Phase 1: Try with current model (primary or recovery) ---
    needs_fallback = False

    for attempt in range(RETRY_ATTEMPTS):
        try:
            # Wrap with AGENT_TIMEOUT to enforce max execution time
            result = _execute_with_timeout(func, AGENT_TIMEOUT)

            # Success! Update fallback state
            if recovery_attempt:
                if not silent:
                    print(f"    ✓ Recovered to primary model")
                _fs().active = False
                _fs().consecutive_successes = 0
                recovery_occurred = True
            elif _fs().active:
                _fs().consecutive_successes += 1

            return {
                "result": result,
                "intended_model": model_name,
                "actual_model": attempt_model,
                "retry_count": retry_count,
                "fallback_occurred": fallback_occurred,
                "recovery_occurred": recovery_occurred,
                "error_type": error_type,
            }

        except Exception as e:
            last_error = e

            # Capture error type for logging (first error wins)
            if not error_type:
                error_type = _classify_error(e)

            # Agent timeout → skip remaining retries, go straight to fallback
            if isinstance(e, AgentTimeoutError):
                if not silent:
                    print(f"    ⏰ Agent timed out after {AGENT_TIMEOUT}s — switching to fallback")
                needs_fallback = True
                break

            # Connection errors are retryable; anything else fails fast
            if not _is_connection_error(e):
                raise

            # Connection error — attempt retry with exponential backoff
            retry_count += 1

            # Check total startup timeout before retrying
            elapsed = time.time() - _get_startup_start_time()
            if elapsed >= TOTAL_STARTUP_TIMEOUT:
                raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)

            if attempt < RETRY_ATTEMPTS - 1:
                delay = RETRY_BASE_DELAY ** (attempt + 1)
                if not silent:
                    print(f"    ↻ Retrying... ({attempt + 1}/{RETRY_ATTEMPTS})")
                time.sleep(delay)
            else:
                # Exhausted retries on current model — need fallback
                needs_fallback = True

    # --- Phase 2: Fallback model ---
    if needs_fallback and fallback_model and not recovery_attempt and attempt_model != fallback_model:
        # Check total startup timeout before trying fallback
        elapsed = time.time() - _get_startup_start_time()
        if elapsed >= TOTAL_STARTUP_TIMEOUT:
            raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)

        if not silent:
            print(f"    ⚠ Switching to fallback model ({fallback_model})")

        # Activate fallback state
        if not _fs().active:
            _fs().active = True
            _fs().primary_model = model_name
            _fs().last_failure_time = time.time()

        _fs().fallback_count += 1
        _fs().consecutive_successes = 0
        fallback_occurred = True

        # Use fallback_func if provided (actually runs with the fallback model),
        # otherwise fall back to same func (legacy — model won't actually change)
        fb_func = fallback_func or func

        fallback_retry_count = 0
        for fallback_attempt in range(RETRY_ATTEMPTS):
            try:
                # Check total startup timeout before each attempt
                elapsed = time.time() - _get_startup_start_time()
                if elapsed >= TOTAL_STARTUP_TIMEOUT:
                    raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)

                result = _execute_with_timeout(fb_func, AGENT_TIMEOUT)

                # Success on fallback
                _fs().consecutive_successes += 1

                return {
                    "result": result,
                    "intended_model": model_name,
                    "actual_model": fallback_model,
                    "retry_count": retry_count + fallback_retry_count,
                    "fallback_occurred": fallback_occurred,
                    "recovery_occurred": recovery_occurred,
                    "error_type": error_type,
                }
            except Exception as fallback_error:
                fallback_retry_count += 1

                # Timeout or non-connection error on fallback — fail fast
                if not _is_connection_error(fallback_error):
                    raise

                # Check total startup timeout before retrying fallback
                elapsed = time.time() - _get_startup_start_time()
                if elapsed >= TOTAL_STARTUP_TIMEOUT:
                    raise StartupTimeoutError(elapsed, TOTAL_STARTUP_TIMEOUT)

                if fallback_attempt < RETRY_ATTEMPTS - 1:
                    delay = RETRY_BASE_DELAY ** (fallback_attempt + 1)
                    if not silent:
                        print(f"    ↻ Fallback retry... ({fallback_attempt + 1}/{RETRY_ATTEMPTS})")
                    time.sleep(delay)
                else:
                    if not silent:
                        print(f"    ✗ Fallback model also failed after {RETRY_ATTEMPTS} attempts")
                    raise fallback_error

    # Recovery attempt failed — stay on fallback for next call
    if recovery_attempt:
        if not silent:
            print(f"    ✗ Recovery failed, continuing with fallback")
        _fs().consecutive_successes = 0

    raise last_error


def get_fallback_stats() -> dict[str, Any]:
    """Get current fallback state statistics for the calling thread."""
    return {
        "fallback_active": _fs().active,
        "primary_model": _fs().primary_model,
        "fallback_count": _fs().fallback_count,
        "consecutive_successes": _fs().consecutive_successes,
        "seconds_since_failure": int(time.time() - _fs().last_failure_time) if _fs().last_failure_time > 0 else 0,
    }
