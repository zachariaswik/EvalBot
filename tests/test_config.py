"""Tests for src/config.py — model resolution and configuration constants."""

from __future__ import annotations

import pytest

import src.config as cfg
from src.config import (
    AGENT_FALLBACK_MODELS,
    AGENT_MODELS,
    DEFAULT_MODEL,
    FALLBACK_MODEL,
    HALL_OF_FAME_MIN_SCORE,
    HALL_OF_FAME_SIZE,
    QUALITY_GATE_THRESHOLD,
    RECOVERY_CHECK_INTERVAL,
    RECOVERY_COOLDOWN,
    RETRY_ATTEMPTS,
    RETRY_BASE_DELAY,
    get_fallback_model_for_agent,
    get_model_for_agent,
)


# ---------------------------------------------------------------------------
# get_model_for_agent
# ---------------------------------------------------------------------------

class TestGetModelForAgent:
    def test_returns_per_agent_override(self):
        """Each agent with an explicit override returns that model."""
        for agent_num, model in AGENT_MODELS.items():
            if model is not None:
                assert get_model_for_agent(agent_num) == model

    def test_returns_default_for_unknown_agent(self):
        """Unknown agent number falls back to DEFAULT_MODEL."""
        result = get_model_for_agent(99)
        assert result == DEFAULT_MODEL

    def test_all_standard_agents_return_strings(self):
        """All agents 1–7 return non-empty strings."""
        for i in range(1, 8):
            model = get_model_for_agent(i)
            assert isinstance(model, str) and model


# ---------------------------------------------------------------------------
# get_fallback_model_for_agent
# ---------------------------------------------------------------------------

class TestGetFallbackModelForAgent:
    def test_returns_per_agent_fallback_override(self):
        """Agents with per-agent fallback overrides return those models."""
        for agent_num, model in AGENT_FALLBACK_MODELS.items():
            assert get_fallback_model_for_agent(agent_num) == model

    def test_returns_global_fallback_for_unregistered_agent(self):
        """Agents not in AGENT_FALLBACK_MODELS use FALLBACK_MODEL."""
        unregistered = next(
            i for i in range(1, 8) if i not in AGENT_FALLBACK_MODELS
        )
        assert get_fallback_model_for_agent(unregistered) == FALLBACK_MODEL

    def test_returns_global_fallback_for_unknown_agent(self):
        assert get_fallback_model_for_agent(99) == FALLBACK_MODEL

    def test_all_agents_return_non_empty_string(self):
        for i in range(1, 8):
            result = get_fallback_model_for_agent(i)
            assert isinstance(result, str) and result


# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_retry_attempts_positive(self):
        assert RETRY_ATTEMPTS > 0

    def test_retry_base_delay_positive(self):
        assert RETRY_BASE_DELAY > 0

    def test_recovery_check_interval_positive(self):
        assert RECOVERY_CHECK_INTERVAL > 0

    def test_recovery_cooldown_positive(self):
        assert RECOVERY_COOLDOWN > 0

    def test_quality_gate_threshold_positive(self):
        assert QUALITY_GATE_THRESHOLD > 0

    def test_critical_fields_not_empty(self):
        from src.config import CRITICAL_FIELDS
        assert len(CRITICAL_FIELDS) >= 6
        assert "problem" in CRITICAL_FIELDS
        assert "solution" in CRITICAL_FIELDS

    def test_hall_of_fame_size_positive(self):
        assert HALL_OF_FAME_SIZE > 0

    def test_hall_of_fame_min_score_non_negative(self):
        assert HALL_OF_FAME_MIN_SCORE >= 0

    def test_default_model_is_string(self):
        assert isinstance(DEFAULT_MODEL, str) and DEFAULT_MODEL

    def test_fallback_model_is_string(self):
        assert isinstance(FALLBACK_MODEL, str) and FALLBACK_MODEL

    def test_agent_models_covers_all_standard_agents(self):
        """All agents 1-7 are represented in AGENT_MODELS."""
        assert set(AGENT_MODELS.keys()) == {1, 2, 3, 4, 5, 6, 7}
