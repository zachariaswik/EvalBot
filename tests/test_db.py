"""Tests for src/db.py — SQLite persistence layer."""

from __future__ import annotations

import json
import sqlite3

import pytest

from src.db import (
    _connect,
    clear_hall_of_fame,
    create_batch,
    get_all_batch_outputs,
    get_current_outputs,
    get_hall_of_fame_stats,
    get_retry_stats,
    get_top_ideas,
    init_db,
    insert_to_hall_of_fame,
    log_retry_event,
    store_agent_output,
    update_startup_status,
    upsert_startup,
)


# ---------------------------------------------------------------------------
# Schema initialisation
# ---------------------------------------------------------------------------

class TestInitDb:
    def test_creates_all_tables(self, tmp_db):
        conn = sqlite3.connect(str(tmp_db))
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()
        tables = {row[0] for row in rows}
        assert {"batches", "startups", "agent_outputs",
                "hall_of_fame", "retry_log"}.issubset(tables)

    def test_idempotent(self, tmp_path):
        """Calling init_db twice on the same path does not raise."""
        db = tmp_path / "idempotent.db"
        init_db(db)
        init_db(db)  # should not raise

    def test_wal_mode_enabled(self, tmp_path):
        """_connect() sets WAL journal mode for concurrent write safety."""
        conn = _connect(tmp_path / "test_wal.db")
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode == "wal"


# ---------------------------------------------------------------------------
# Batches
# ---------------------------------------------------------------------------

class TestCreateBatch:
    def test_inserts_batch(self, tmp_db):
        create_batch("batch_1", "my batch", tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        row = conn.execute(
            "SELECT batch_id, description FROM batches WHERE batch_id='batch_1'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "batch_1"
        assert row[1] == "my batch"

    def test_idempotent(self, tmp_db):
        """INSERT OR IGNORE means duplicate batch IDs do not raise."""
        create_batch("batch_1", "first", tmp_db)
        create_batch("batch_1", "second", tmp_db)  # should not raise
        conn = sqlite3.connect(str(tmp_db))
        count = conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
        conn.close()
        assert count == 1


# ---------------------------------------------------------------------------
# Startups
# ---------------------------------------------------------------------------

class TestUpsertStartup:
    def test_inserts_new_startup(self, tmp_db):
        create_batch("b1", "", tmp_db)
        upsert_startup("b1", "Acme", "raw text here", tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        row = conn.execute(
            "SELECT startup_name, raw_submission FROM startups WHERE startup_name='Acme'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "Acme"
        assert row[1] == "raw text here"

    def test_updates_existing_startup(self, tmp_db):
        create_batch("b1", "", tmp_db)
        upsert_startup("b1", "Acme", "old text", tmp_db)
        upsert_startup("b1", "Acme", "new text", tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        rows = conn.execute(
            "SELECT raw_submission FROM startups WHERE startup_name='Acme'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1, "No duplicate rows on update"
        assert rows[0][0] == "new text"

    def test_default_status_is_pending(self, tmp_db):
        create_batch("b1", "", tmp_db)
        upsert_startup("b1", "Acme", "text", tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        row = conn.execute(
            "SELECT pipeline_status FROM startups WHERE startup_name='Acme'"
        ).fetchone()
        conn.close()
        assert row[0] == "pending"


class TestUpdateStartupStatus:
    def test_updates_status(self, tmp_db):
        create_batch("b1", "", tmp_db)
        upsert_startup("b1", "Acme", "text", tmp_db)
        update_startup_status("b1", "Acme", "completed", tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        row = conn.execute(
            "SELECT pipeline_status FROM startups WHERE startup_name='Acme'"
        ).fetchone()
        conn.close()
        assert row[0] == "completed"

    def test_can_set_failed(self, tmp_db):
        create_batch("b1", "", tmp_db)
        upsert_startup("b1", "Acme", "text", tmp_db)
        update_startup_status("b1", "Acme", "failed", tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        row = conn.execute(
            "SELECT pipeline_status FROM startups WHERE startup_name='Acme'"
        ).fetchone()
        conn.close()
        assert row[0] == "failed"


# ---------------------------------------------------------------------------
# Agent outputs
# ---------------------------------------------------------------------------

class TestStoreAndRetrieveAgentOutput:
    def test_basic_store_and_retrieve(self, tmp_db):
        create_batch("b1", "", tmp_db)
        data = {"startup_name": "Acme", "problem": "Big pain"}
        store_agent_output("b1", "Acme", 1, json.dumps(data), db_path=tmp_db)
        outputs = get_current_outputs("b1", "Acme", tmp_db)
        assert 1 in outputs
        assert outputs[1]["problem"] == "Big pain"

    def test_latest_stored_output_is_returned(self, tmp_db):
        create_batch("b1", "", tmp_db)
        store_agent_output("b1", "S1", 1, json.dumps({"v": 1}), db_path=tmp_db)
        store_agent_output("b1", "S1", 1, json.dumps({"v": 2}), db_path=tmp_db)
        outputs = get_current_outputs("b1", "S1", tmp_db)
        assert outputs[1]["v"] == 2

    def test_multiple_agents(self, tmp_db):
        create_batch("b1", "", tmp_db)
        for agent in range(1, 4):
            store_agent_output("b1", "S1", agent, json.dumps({"agent": agent}), db_path=tmp_db)
        outputs = get_current_outputs("b1", "S1", tmp_db)
        assert set(outputs.keys()) == {1, 2, 3}

    def test_empty_startup_returns_empty_dict(self, tmp_db):
        create_batch("b1", "", tmp_db)
        outputs = get_current_outputs("b1", "NoSuchStartup", tmp_db)
        assert outputs == {}

    def test_recovers_verdict_from_malformed_raw_output(self, tmp_db):
        create_batch("b1", "", tmp_db)
        raw_output = (
            '\n\n{"summary":"Value with unescaped "quote",'
            '"total_score":63,"verdict":"Promising, Needs Sharper Focus"}'
        )
        malformed = json.dumps({"raw_output": raw_output})
        store_agent_output("b1", "S1", 2, malformed, db_path=tmp_db)
        outputs = get_current_outputs("b1", "S1", tmp_db)
        assert outputs[2]["verdict"] == "Promising, Needs Sharper Focus"
        assert outputs[2]["total_score"] == 63

    def test_keeps_raw_output_if_no_fields_recoverable(self, tmp_db):
        create_batch("b1", "", tmp_db)
        bad = '{"raw_output":"this is not json"}'
        store_agent_output("b1", "S1", 2, bad, db_path=tmp_db)
        outputs = get_current_outputs("b1", "S1", tmp_db)
        assert outputs[2] == {"raw_output": "this is not json"}


# ---------------------------------------------------------------------------
# Batch outputs
# ---------------------------------------------------------------------------

class TestGetAllBatchOutputs:
    def test_returns_all_startups(self, tmp_db):
        create_batch("b1", "", tmp_db)
        for name in ("Alpha", "Beta", "Gamma"):
            store_agent_output("b1", name, 1, json.dumps({"name": name}), db_path=tmp_db)
        results = get_all_batch_outputs("b1", tmp_db)
        names = {r["startup_name"] for r in results}
        assert names == {"Alpha", "Beta", "Gamma"}

    def test_returns_latest_output_per_agent(self, tmp_db):
        create_batch("b1", "", tmp_db)
        store_agent_output("b1", "S1", 1, json.dumps({"v": 1}), db_path=tmp_db)
        store_agent_output("b1", "S1", 1, json.dumps({"v": 2}), db_path=tmp_db)
        results = get_all_batch_outputs("b1", tmp_db)
        assert len(results) == 1
        assert results[0]["outputs"][1]["v"] == 2

    def test_empty_batch_returns_empty_list(self, tmp_db):
        create_batch("b1", "", tmp_db)
        results = get_all_batch_outputs("b1", tmp_db)
        assert results == []


# ---------------------------------------------------------------------------
# Retry log
# ---------------------------------------------------------------------------

class TestRetryLog:
    def test_log_retry_event_inserts_record(self, tmp_db):
        create_batch("b1", "", tmp_db)
        log_retry_event("b1", "S1", 2, "primary/model", "fallback/model",
                        3, True, False, "connection_reset", tmp_db)
        conn = sqlite3.connect(str(tmp_db))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM retry_log").fetchone()
        conn.close()
        assert row is not None
        assert row["agent_number"] == 2
        assert row["retry_count"] == 3
        assert row["fallback_occurred"] == 1
        assert row["recovery_occurred"] == 0
        assert row["error_type"] == "connection_reset"

    def test_get_retry_stats_empty_batch(self, tmp_db):
        create_batch("b1", "", tmp_db)
        stats = get_retry_stats("b1", tmp_db)
        assert stats["total_events"] == 0
        assert stats["fallback_count"] == 0

    def test_get_retry_stats_aggregation(self, tmp_db):
        create_batch("b1", "", tmp_db)
        log_retry_event("b1", "S1", 1, "p", "p", 0, False, False, None, tmp_db)
        log_retry_event("b1", "S1", 2, "p", "f", 3, True, False, "timeout", tmp_db)
        log_retry_event("b1", "S1", 3, "p", "f", 2, True, True, "timeout", tmp_db)
        stats = get_retry_stats("b1", tmp_db)
        assert stats["total_events"] == 3
        assert stats["fallback_count"] == 2
        assert stats["recovery_count"] == 1
        assert stats["total_retries"] == 5

    def test_get_retry_stats_error_types(self, tmp_db):
        create_batch("b1", "", tmp_db)
        log_retry_event("b1", "S1", 1, "p", "p", 1, False, False, "timeout", tmp_db)
        log_retry_event("b1", "S1", 2, "p", "p", 1, False, False, "timeout", tmp_db)
        log_retry_event("b1", "S1", 3, "p", "p", 1, False, False, "connection_reset", tmp_db)
        stats = get_retry_stats("b1", tmp_db)
        error_map = {e["error_type"]: e["count"] for e in stats["error_types"]}
        assert error_map.get("timeout") == 2
        assert error_map.get("connection_reset") == 1

    def test_get_retry_stats_per_agent(self, tmp_db):
        create_batch("b1", "", tmp_db)
        log_retry_event("b1", "S1", 2, "primary", "fallback", 3, True, False, None, tmp_db)
        stats = get_retry_stats("b1", tmp_db)
        agent_stats = stats["per_agent"]
        assert len(agent_stats) == 1
        assert agent_stats[0]["agent_number"] == 2
        assert agent_stats[0]["fallbacks"] == 1


# ---------------------------------------------------------------------------
# Hall of Fame
# ---------------------------------------------------------------------------

class TestHallOfFame:
    def _make_outputs(self):
        return (
            {"startup_name": "Test", "problem": "Pain"},
            {"verdict": "Top VC Candidate", "total_score": 85},
        )

    def test_insert_and_retrieve(self, tmp_db):
        agent0, agent2 = self._make_outputs()
        create_batch("b1", "", tmp_db)
        insert_to_hall_of_fame("b1", "Acme", 80.0, "Tier A", agent0, agent2, tmp_db)
        ideas = get_top_ideas(limit=5, db_path=tmp_db)
        assert len(ideas) == 1
        assert ideas[0]["startup_name"] == "Acme"
        assert ideas[0]["weighted_score"] == 80.0

    def test_min_score_threshold(self, tmp_db):
        agent0, agent2 = self._make_outputs()
        create_batch("b1", "", tmp_db)
        # Score below HALL_OF_FAME_MIN_SCORE should not be stored
        from src.config import HALL_OF_FAME_MIN_SCORE
        insert_to_hall_of_fame("b1", "LowScore", HALL_OF_FAME_MIN_SCORE - 1, "Tier C",
                               agent0, agent2, tmp_db)
        ideas = get_top_ideas(limit=10, db_path=tmp_db)
        names = [i["startup_name"] for i in ideas]
        assert "LowScore" not in names

    def test_returns_top_by_score(self, tmp_db):
        agent0, agent2 = self._make_outputs()
        create_batch("b1", "", tmp_db)
        for score in [70.0, 90.0, 80.0]:
            insert_to_hall_of_fame("b1", f"Co{score}", score, "Tier", agent0, agent2, tmp_db)
        ideas = get_top_ideas(limit=3, db_path=tmp_db)
        scores = [i["weighted_score"] for i in ideas]
        assert scores == sorted(scores, reverse=True)

    def test_clear_hall_of_fame(self, tmp_db):
        agent0, agent2 = self._make_outputs()
        create_batch("b1", "", tmp_db)
        insert_to_hall_of_fame("b1", "Acme", 80.0, "Tier A", agent0, agent2, tmp_db)
        cleared = clear_hall_of_fame(tmp_db)
        assert cleared == 1
        assert get_top_ideas(db_path=tmp_db) == []

    def test_stats_empty(self, tmp_db):
        stats = get_hall_of_fame_stats(tmp_db)
        assert stats["count"] == 0

    def test_stats_with_entries(self, tmp_db):
        agent0, agent2 = self._make_outputs()
        create_batch("b1", "", tmp_db)
        insert_to_hall_of_fame("b1", "A", 75.0, "T", agent0, agent2, tmp_db)
        insert_to_hall_of_fame("b1", "B", 85.0, "T", agent0, agent2, tmp_db)
        stats = get_hall_of_fame_stats(tmp_db)
        assert stats["count"] == 2
        assert stats["min_score"] == 75.0
        assert stats["max_score"] == 85.0

    def test_size_limit_enforced(self, tmp_db, monkeypatch):
        """When HOF exceeds HALL_OF_FAME_SIZE, lowest scores are evicted."""
        import src.config as cfg
        monkeypatch.setattr(cfg, "HALL_OF_FAME_SIZE", 2)
        monkeypatch.setattr(cfg, "HALL_OF_FAME_MIN_SCORE", 0)
        agent0, agent2 = self._make_outputs()
        create_batch("b1", "", tmp_db)
        for i, score in enumerate([65.0, 80.0, 90.0]):
            insert_to_hall_of_fame("b1", f"Co{i}", score, "T", agent0, agent2, tmp_db)
        ideas = get_top_ideas(limit=10, db_path=tmp_db)
        assert len(ideas) <= 2
        names_in = {i["startup_name"] for i in ideas}
        assert "Co0" not in names_in  # lowest score evicted


# ---------------------------------------------------------------------------
# Frontend query helpers
# ---------------------------------------------------------------------------

class TestListBatches:
    def test_returns_empty_when_no_batches(self, tmp_db):
        from src.db import list_batches
        result = list_batches(tmp_db)
        assert result == []

    def test_returns_batch_with_startup_count(self, tmp_db):
        from src.db import list_batches
        create_batch("b1", "Test batch", tmp_db)
        upsert_startup("b1", "Acme", "text", tmp_db)
        upsert_startup("b1", "Beta", "text", tmp_db)
        result = list_batches(tmp_db)
        assert len(result) == 1
        assert result[0]["batch_id"] == "b1"
        assert result[0]["startup_count"] == 2
        assert result[0]["description"] == "Test batch"

    def test_ordered_by_created_at_desc(self, tmp_db):
        from src.db import list_batches
        import time
        create_batch("b1", "", tmp_db)
        time.sleep(0.01)
        create_batch("b2", "", tmp_db)
        result = list_batches(tmp_db)
        assert result[0]["batch_id"] == "b2"
        assert result[1]["batch_id"] == "b1"

    def test_batch_with_no_startups_has_count_zero(self, tmp_db):
        from src.db import list_batches
        create_batch("empty_batch", "", tmp_db)
        result = list_batches(tmp_db)
        assert result[0]["startup_count"] == 0


class TestListStartups:
    def test_returns_empty_when_no_startups(self, tmp_db):
        from src.db import list_startups
        create_batch("b1", "", tmp_db)
        result = list_startups("b1", tmp_db)
        assert result == []

    def test_returns_startups_for_batch(self, tmp_db):
        from src.db import list_startups
        create_batch("b1", "", tmp_db)
        upsert_startup("b1", "Acme", "text", tmp_db)
        upsert_startup("b1", "Beta", "text", tmp_db)
        result = list_startups("b1", tmp_db)
        names = [r["startup_name"] for r in result]
        assert "Acme" in names
        assert "Beta" in names

    def test_returns_pipeline_status(self, tmp_db):
        from src.db import list_startups
        create_batch("b1", "", tmp_db)
        upsert_startup("b1", "Acme", "text", tmp_db)
        update_startup_status("b1", "Acme", "completed", tmp_db)
        result = list_startups("b1", tmp_db)
        assert result[0]["pipeline_status"] == "completed"

    def test_only_returns_startups_for_given_batch(self, tmp_db):
        from src.db import list_startups
        create_batch("b1", "", tmp_db)
        create_batch("b2", "", tmp_db)
        upsert_startup("b1", "Acme", "text", tmp_db)
        upsert_startup("b2", "Other", "text", tmp_db)
        result = list_startups("b1", tmp_db)
        names = [r["startup_name"] for r in result]
        assert "Acme" in names
        assert "Other" not in names
