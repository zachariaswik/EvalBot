"""Tests for src/agents.py — CrewAI agent factory."""

from __future__ import annotations

import pytest

# conftest.py has already installed the crewai mock into sys.modules
import src.config as cfg
from src.agents import _AGENT_META, _load_prompt, create_agent


# ---------------------------------------------------------------------------
# Agent metadata
# ---------------------------------------------------------------------------

class TestAgentMeta:
    def test_covers_all_standard_agents(self):
        assert set(_AGENT_META.keys()) == {1, 2, 3, 4, 5, 6, 7}

    def test_each_entry_is_role_goal_tuple(self):
        for agent_num, (role, goal) in _AGENT_META.items():
            assert isinstance(role, str) and role
            assert isinstance(goal, str) and goal

    def test_agent1_is_intake_parser(self):
        role, _ = _AGENT_META[1]
        assert "Intake" in role or "Parser" in role

    def test_agent7_is_ranking(self):
        role, _ = _AGENT_META[7]
        assert "Rank" in role


# ---------------------------------------------------------------------------
# _load_prompt
# ---------------------------------------------------------------------------

class TestLoadPrompt:
    def test_raises_for_missing_prompt_file(self, tmp_path, monkeypatch):
        # _load_prompt uses the module-level AGENTS_DIR imported into src.agents,
        # so we must patch it there, not on cfg.
        import src.agents as agents_module
        monkeypatch.setattr(agents_module, "AGENTS_DIR", tmp_path)
        # No Agent1/prompt.md exists yet
        with pytest.raises(FileNotFoundError):
            _load_prompt(1)

    def test_reads_correct_file(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        content = _load_prompt(3)
        assert "Agent 3" in content

    def test_all_agents_readable(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        for i in range(1, 8):
            content = _load_prompt(i)
            assert content  # non-empty


# ---------------------------------------------------------------------------
# create_agent
# ---------------------------------------------------------------------------

class TestCreateAgent:
    def test_invalid_agent_number_zero_raises(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        with pytest.raises(ValueError):
            create_agent(0)

    def test_invalid_agent_number_eight_raises(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        with pytest.raises(ValueError):
            create_agent(8)

    def test_negative_agent_number_raises(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        with pytest.raises(ValueError):
            create_agent(-1)

    def test_valid_agent_returns_agent_object(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        import crewai
        agent = create_agent(1)
        assert isinstance(agent, crewai.Agent)

    def test_agent_role_matches_metadata(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        agent = create_agent(1)
        assert agent.role == _AGENT_META[1][0]

    def test_agent_goal_matches_metadata(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        agent = create_agent(2)
        assert agent.goal == _AGENT_META[2][1]

    def test_agent_backstory_from_prompt_file(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        agent = create_agent(3)
        assert "Agent 3" in agent.backstory

    def test_all_valid_agents_creatable(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        for i in range(1, 8):
            agent = create_agent(i)
            assert agent is not None

    def test_explicit_llm_override(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        import crewai
        custom_llm = crewai.LLM(model="openai/custom-model")
        agent = create_agent(1, llm=custom_llm)
        assert agent.llm is custom_llm

    def test_is_rerun_flag_does_not_raise(self, tmp_agent_dir, monkeypatch):
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        agent = create_agent(1, is_rerun=True)
        assert agent is not None

    def test_non_ollama_model_not_passed_to_ensure_context(self, tmp_agent_dir, monkeypatch):
        """Non-Ollama models skip the ollama variant creation logic."""
        monkeypatch.setattr(cfg, "AGENTS_DIR", tmp_agent_dir)
        monkeypatch.setattr(cfg, "AGENT_MODELS", {1: "openai/gpt-4o"})
        # Should complete without calling subprocess
        agent = create_agent(1)
        assert agent is not None
