"""Tests for frontend/app.py — FastAPI web interface."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def app_with_db(tmp_path, monkeypatch):
    """FastAPI TestClient backed by a seeded temp database."""
    from src.db import (
        create_batch,
        init_db,
        store_agent_output,
        update_startup_status,
        upsert_startup,
    )

    db_path = tmp_path / "test.db"
    init_db(db_path)

    # Seed batch and startups
    create_batch("batch_1", "Test batch", db_path)
    upsert_startup("batch_1", "TestCo", "some text", db_path)
    upsert_startup("batch_1", "AnotherCo", "some text", db_path)
    update_startup_status("batch_1", "TestCo", "completed", db_path)

    # Seed agent 2 output for TestCo
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

    # Seed agent 1 output for TestCo
    a1_output = {
        "startup_name": "TestCo",
        "one_line_description": "AI for everything",
        "problem": "Big problem",
        "solution": "AI solution",
        "target_customer": "Enterprises",
        "buyer": "CTO",
        "market": "B2B SaaS",
        "business_model": "Subscription",
        "competitors": "None known",
        "traction": "10 pilots",
        "team": "3 founders",
        "why_now": "AI wave",
        "vision": "Global scale",
        "unfair_advantage": "Domain expertise",
        "risks": "Market adoption",
        "missing_info": [],
        "inconsistencies": [],
        "clarity_score": 8,
    }
    store_agent_output("batch_1", "TestCo", 1, json.dumps(a1_output), 1, db_path=db_path)

    # Patch the app to use our temp db
    import frontend.app as app_module
    monkeypatch.setattr(app_module, "_db_path", lambda: db_path)

    from frontend.app import app
    return TestClient(app)


# ---------------------------------------------------------------------------
# Dashboard tests
# ---------------------------------------------------------------------------

class TestDashboard:
    def test_dashboard_loads(self, app_with_db):
        response = app_with_db.get("/")
        assert response.status_code == 200
        assert "EvalBot" in response.text

    def test_dashboard_shows_batch_list(self, app_with_db):
        response = app_with_db.get("/")
        assert response.status_code == 200
        assert "batch_1" in response.text


# ---------------------------------------------------------------------------
# Batch page tests
# ---------------------------------------------------------------------------

class TestBatchPage:
    def test_batch_page_loads(self, app_with_db):
        response = app_with_db.get("/batch/batch_1")
        assert response.status_code == 200

    def test_batch_page_shows_startups(self, app_with_db):
        response = app_with_db.get("/batch/batch_1")
        assert "TestCo" in response.text

    def test_404_on_missing_batch(self, app_with_db):
        response = app_with_db.get("/batch/nonexistent_batch_999")
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Startup detail tests
# ---------------------------------------------------------------------------

class TestStartupPage:
    def test_startup_page_loads(self, app_with_db):
        response = app_with_db.get("/batch/batch_1/TestCo")
        assert response.status_code == 200

    def test_startup_page_shows_name(self, app_with_db):
        response = app_with_db.get("/batch/batch_1/TestCo")
        assert "TestCo" in response.text

    def test_startup_page_shows_scores(self, app_with_db):
        response = app_with_db.get("/batch/batch_1/TestCo")
        # Radar chart data or score values should be in the page
        assert "78" in response.text  # total_score


# ---------------------------------------------------------------------------
# Roadmap tests
# ---------------------------------------------------------------------------

class TestRoadmapPage:
    def test_roadmap_loads(self, app_with_db):
        response = app_with_db.get("/roadmap")
        assert response.status_code == 200

    def test_roadmap_contains_coming_soon(self, app_with_db):
        response = app_with_db.get("/roadmap")
        assert "Coming" in response.text
