"""Tests for the Reflex frontend state helper functions.

These tests verify the Python data-loading logic in the state modules
without requiring the Reflex runtime or a running server.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import reflex  # noqa: F401
    HAS_REFLEX = True
except ImportError:
    HAS_REFLEX = False

pytestmark = pytest.mark.skipif(not HAS_REFLEX, reason="reflex not installed")


# ---------------------------------------------------------------------------
# Helper: seed a test DB
# ---------------------------------------------------------------------------

def _seed_db(db_path: Path) -> None:
    from src.db import (
        create_batch,
        init_db,
        store_agent_output,
        update_startup_status,
        upsert_startup,
    )

    init_db(db_path)
    create_batch("batch_1", "Test batch", db_path)
    upsert_startup("batch_1", "TestCo", "some text", db_path)
    upsert_startup("batch_1", "AnotherCo", "some text", db_path)
    update_startup_status("batch_1", "TestCo", "completed", db_path)

    a2_output = {
        "verdict": "Top VC Candidate",
        "total_score": 78,
        "summary": "Very promising startup.",
        "score_problem_severity": 8,
        "score_market_size": 8,
        "score_differentiation": 8,
        "score_customer_clarity": 7,
        "score_founder_insight": 8,
        "score_business_model": 7,
        "score_moat_potential": 8,
        "score_venture_potential": 8,
        "score_competition_difficulty": 7,
        "score_execution_feasibility": 7,
        "swot": {
            "strengths": ["Strong team"],
            "weaknesses": ["Early stage"],
            "opportunities": ["Large market"],
            "threats": ["Competition"],
        },
        "explanation": "Great fundamentals.",
    }
    store_agent_output("batch_1", "TestCo", 2, json.dumps(a2_output), 1, db_path=db_path)

    a1_output = {
        "startup_name": "TestCo",
        "one_line_description": "AI for everything",
        "problem": "Big problem",
    }
    store_agent_output("batch_1", "TestCo", 1, json.dumps(a1_output), 1, db_path=db_path)


# ---------------------------------------------------------------------------
# _get_verdict_color
# ---------------------------------------------------------------------------

def test_verdict_color_vc():
    from frontend.state.dashboard import _get_verdict_color
    assert _get_verdict_color("Top VC Candidate") == "emerald"


def test_verdict_color_reject():
    from frontend.state.dashboard import _get_verdict_color
    assert _get_verdict_color("Reject") == "red"


def test_verdict_color_unknown():
    from frontend.state.dashboard import _get_verdict_color
    assert _get_verdict_color("Something Else") == "gray"


def test_verdict_color_promising():
    from frontend.state.dashboard import _get_verdict_color
    assert _get_verdict_color("Promising, Needs Sharper Focus") == "blue"


# ---------------------------------------------------------------------------
# _load_batches_from_fs
# ---------------------------------------------------------------------------

def test_load_batches_from_fs_empty(tmp_path, monkeypatch):
    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", tmp_path / "nonexistent")
    result = dash_mod._load_batches_from_fs()
    assert result == []


def test_load_batches_from_fs_with_data(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    (output_dir / "batch_1" / "TestCo").mkdir(parents=True)
    (output_dir / "batch_2" / "AnotherCo").mkdir(parents=True)
    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", output_dir)

    result = dash_mod._load_batches_from_fs()
    assert len(result) == 2
    batch_ids = [b["batch_id"] for b in result]
    assert "batch_1" in batch_ids
    assert "batch_2" in batch_ids


def test_load_batch_from_fs(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    (output_dir / "batch_1" / "TestCo").mkdir(parents=True)
    (output_dir / "batch_1" / "AnotherCo").mkdir(parents=True)
    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", output_dir)

    result = dash_mod._load_batch_from_fs("batch_1")
    names = [s["startup_name"] for s in result]
    assert "TestCo" in names
    assert "AnotherCo" in names


def test_load_batch_from_fs_missing(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    output_dir.mkdir(parents=True)
    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", output_dir)
    result = dash_mod._load_batch_from_fs("nonexistent_batch")
    assert result == []


# ---------------------------------------------------------------------------
# _load_startup_outputs_from_fs
# ---------------------------------------------------------------------------

def test_load_startup_outputs_from_fs(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    startup_dir = output_dir / "batch_1" / "TestCo"
    startup_dir.mkdir(parents=True)

    data = {
        "agent1": {"startup_name": "TestCo"},
        "agent2": {"verdict": "Top VC Candidate", "total_score": 75},
    }
    (startup_dir / "TestCo.json").write_text(json.dumps(data))

    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", output_dir)

    result = dash_mod._load_startup_outputs_from_fs("batch_1", "TestCo")
    assert 1 in result
    assert 2 in result
    assert result[2]["total_score"] == 75


def test_load_startup_outputs_missing(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    output_dir.mkdir(parents=True)
    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", output_dir)
    result = dash_mod._load_startup_outputs_from_fs("batch_1", "NoSuchCo")
    assert result == {}


# ---------------------------------------------------------------------------
# _get_startup_outputs (DB path)
# ---------------------------------------------------------------------------

def test_get_startup_outputs_from_db(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    _seed_db(db_path)

    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "_db_path", lambda: db_path)
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", tmp_path / "nonexistent")

    outputs = dash_mod._get_startup_outputs("batch_1", "TestCo")
    assert 2 in outputs
    assert outputs[2]["verdict"] == "Top VC Candidate"
    assert outputs[2]["total_score"] == 78


def test_get_startup_outputs_fallback_to_fs(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    startup_dir = output_dir / "batch_1" / "TestCo"
    startup_dir.mkdir(parents=True)

    data = {"agent2": {"verdict": "Reject", "total_score": 30}}
    (startup_dir / "TestCo.json").write_text(json.dumps(data))

    from frontend.state import dashboard as dash_mod
    monkeypatch.setattr(dash_mod, "_db_path", lambda: None)
    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", output_dir)

    outputs = dash_mod._get_startup_outputs("batch_1", "TestCo")
    assert 2 in outputs
    assert outputs[2]["verdict"] == "Reject"


# ---------------------------------------------------------------------------
# Batch state helpers
# ---------------------------------------------------------------------------

def test_batch_verdict_color():
    from frontend.state.batch import _get_verdict_color
    assert _get_verdict_color("Reject") == "red"
    assert _get_verdict_color("Top VC Candidate") == "emerald"


def test_batch_load_batch_from_fs(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    (output_dir / "batch_1" / "StartupA").mkdir(parents=True)
    (output_dir / "batch_1" / "StartupB").mkdir(parents=True)

    from frontend.state import batch as batch_mod
    monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)

    result = batch_mod._load_batch_from_fs("batch_1")
    assert len(result) == 2
    names = [s["startup_name"] for s in result]
    assert "StartupA" in names and "StartupB" in names


# ---------------------------------------------------------------------------
# Startup state helpers
# ---------------------------------------------------------------------------

def test_startup_verdict_color():
    from frontend.state.startup import _get_verdict_color
    assert _get_verdict_color("AI Wrapper With Weak Moat") == "amber"
    assert _get_verdict_color("Good Small Business, Not Venture-Scale") == "orange"


def test_startup_load_from_fs(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    startup_dir = output_dir / "batch_1" / "TestCo"
    startup_dir.mkdir(parents=True)

    data = {
        "agent1": {"startup_name": "TestCo", "one_line_description": "AI biz"},
        "agent2": {"verdict": "Promising, Needs Sharper Focus", "total_score": 60},
    }
    (startup_dir / "TestCo.json").write_text(json.dumps(data))

    from frontend.state import startup as startup_mod
    monkeypatch.setattr(startup_mod, "OUTPUT_DIR", output_dir)

    outputs = startup_mod._load_startup_outputs_from_fs("batch_1", "TestCo")
    assert 1 in outputs
    assert 2 in outputs
    assert outputs[2]["total_score"] == 60


# ---------------------------------------------------------------------------
# Run state helpers
# ---------------------------------------------------------------------------

def test_python_binary_returns_string():
    from frontend.state.run import _python_binary
    binary = _python_binary()
    assert isinstance(binary, str)
    assert len(binary) > 0


def test_latest_batch_id_no_output(tmp_path, monkeypatch):
    from frontend.state import run as run_mod
    monkeypatch.setattr(run_mod, "OUTPUT_DIR", tmp_path / "nonexistent")
    result = run_mod._latest_batch_id()
    assert result is None


def test_latest_batch_id_with_batches(tmp_path, monkeypatch):
    output_dir = tmp_path / "output" / "Batch"
    (output_dir / "batch_1").mkdir(parents=True)
    (output_dir / "batch_3").mkdir(parents=True)
    (output_dir / "batch_2").mkdir(parents=True)

    from frontend.state import run as run_mod
    monkeypatch.setattr(run_mod, "OUTPUT_DIR", output_dir)
    result = run_mod._latest_batch_id()
    assert result == "batch_3"


def test_run_state_file_round_trip(tmp_path, monkeypatch):
    state_file = tmp_path / "evalbot_run.json"
    from frontend.state import run as run_mod
    monkeypatch.setattr(run_mod, "RUN_STATE_FILE", state_file)

    run_mod._write_run_state("job-123", "running", None)
    state = run_mod._read_run_state()
    assert state is not None
    assert state["job_id"] == "job-123"
    assert state["status"] == "running"

    run_mod._write_run_state("job-123", "done", "batch_5")
    state = run_mod._read_run_state()
    assert state["status"] == "done"
    assert state["batch_id"] == "batch_5"


def test_read_run_state_missing(tmp_path, monkeypatch):
    from frontend.state import run as run_mod
    monkeypatch.setattr(run_mod, "RUN_STATE_FILE", tmp_path / "nonexistent.json")
    result = run_mod._read_run_state()
    assert result is None
