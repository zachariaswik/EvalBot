"""Shared test configuration and fixtures.

Sets up module-level mocks for heavy dependencies (crewai, pdfplumber)
so tests run fast without API keys or installed LLM infrastructure.
These mocks must be installed before any src module is imported.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Mock crewai before any src import touches it
# ---------------------------------------------------------------------------

class _MockAgent:
    """Minimal stand-in for crewai.Agent."""
    def __init__(self, role="", goal="", backstory="", llm=None, verbose=False, **kwargs):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm = llm
        self.verbose = verbose


class _MockTask:
    """Minimal stand-in for crewai.Task."""
    def __init__(self, description="", expected_output="", agent=None,
                 output_pydantic=None, input_files=None, **kwargs):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.output_pydantic = output_pydantic
        self.input_files = input_files


class _MockLLM:
    """Minimal stand-in for crewai.LLM."""
    def __init__(self, model=None, timeout=None, **kwargs):
        self.model = model
        self.timeout = timeout


class _MockCrew:
    """Minimal stand-in for crewai.Crew."""
    def __init__(self, agents=None, tasks=None, verbose=False, **kwargs):
        self.agents = agents or []
        self.tasks = tasks or []
        self.verbose = verbose

    def kickoff(self):
        return MagicMock()


_crewai_mock = MagicMock()
_crewai_mock.Agent = _MockAgent
_crewai_mock.Task = _MockTask
_crewai_mock.LLM = _MockLLM
_crewai_mock.Crew = _MockCrew

sys.modules.setdefault("crewai", _crewai_mock)

# Mock pdfplumber (only used in main.py, not src/, but prevents import errors)
sys.modules.setdefault("pdfplumber", MagicMock())

# Mock docx (python-docx) with enough structure for docs.py tests
_docx_mock = MagicMock()
sys.modules.setdefault("docx", _docx_mock)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Initialised temporary SQLite database; deleted after the test."""
    from src.db import init_db
    db_path = tmp_path / "test.db"
    init_db(db_path)
    return db_path


@pytest.fixture
def tmp_agent_dir(tmp_path):
    """Temp directory containing minimal Agent{N}/prompt.md files (1-7)."""
    for i in range(1, 8):
        agent_dir = tmp_path / f"Agent{i}"
        agent_dir.mkdir()
        (agent_dir / "prompt.md").write_text(f"You are Agent {i}. Do your job.")
    return tmp_path
