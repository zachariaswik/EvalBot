"""SQLite persistence for EvalBot pipeline outputs."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import DB_PATH

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS batches (
    batch_id   TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS startups (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id        TEXT NOT NULL,
    startup_name    TEXT NOT NULL,
    raw_submission  TEXT,
    pipeline_status TEXT NOT NULL DEFAULT 'pending',
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
);

CREATE TABLE IF NOT EXISTS agent_outputs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id        TEXT NOT NULL,
    startup_name    TEXT NOT NULL,
    agent_number    INTEGER NOT NULL,
    output_json     TEXT NOT NULL,
    iteration       INTEGER NOT NULL DEFAULT 1,
    is_current      INTEGER NOT NULL DEFAULT 1,
    feedback_reason TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS feedback_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id        TEXT NOT NULL,
    startup_name    TEXT NOT NULL,
    from_agent      INTEGER NOT NULL,
    to_agent        INTEGER NOT NULL,
    reason          TEXT,
    iteration       INTEGER NOT NULL,
    created_at      TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------

def init_db(db_path: Path | None = None) -> None:
    conn = _connect(db_path)
    conn.executescript(_SCHEMA)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Batches & startups
# ---------------------------------------------------------------------------

def create_batch(batch_id: str, description: str = "", db_path: Path | None = None) -> None:
    conn = _connect(db_path)
    conn.execute(
        "INSERT OR IGNORE INTO batches (batch_id, created_at, description) VALUES (?, ?, ?)",
        (batch_id, _now(), description),
    )
    conn.commit()
    conn.close()


def upsert_startup(batch_id: str, startup_name: str, raw_submission: str, db_path: Path | None = None) -> None:
    conn = _connect(db_path)
    existing = conn.execute(
        "SELECT id FROM startups WHERE batch_id = ? AND startup_name = ?",
        (batch_id, startup_name),
    ).fetchone()
    if existing:
        conn.execute(
            "UPDATE startups SET raw_submission = ? WHERE id = ?",
            (raw_submission, existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO startups (batch_id, startup_name, raw_submission) VALUES (?, ?, ?)",
            (batch_id, startup_name, raw_submission),
        )
    conn.commit()
    conn.close()


def update_startup_status(batch_id: str, startup_name: str, status: str, db_path: Path | None = None) -> None:
    conn = _connect(db_path)
    conn.execute(
        "UPDATE startups SET pipeline_status = ? WHERE batch_id = ? AND startup_name = ?",
        (status, batch_id, startup_name),
    )
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Agent outputs
# ---------------------------------------------------------------------------

def store_agent_output(
    batch_id: str,
    startup_name: str,
    agent_number: int,
    output_json: str,
    iteration: int,
    feedback_reason: str | None = None,
    db_path: Path | None = None,
) -> None:
    conn = _connect(db_path)
    # Mark previous outputs for this agent as not current
    conn.execute(
        "UPDATE agent_outputs SET is_current = 0 "
        "WHERE batch_id = ? AND startup_name = ? AND agent_number = ?",
        (batch_id, startup_name, agent_number),
    )
    conn.execute(
        "INSERT INTO agent_outputs "
        "(batch_id, startup_name, agent_number, output_json, iteration, is_current, feedback_reason, created_at) "
        "VALUES (?, ?, ?, ?, ?, 1, ?, ?)",
        (batch_id, startup_name, agent_number, output_json, iteration, feedback_reason, _now()),
    )
    conn.commit()
    conn.close()


def invalidate_outputs_from(
    batch_id: str,
    startup_name: str,
    from_agent: int,
    db_path: Path | None = None,
) -> None:
    """Mark all outputs from `from_agent` onward as not current."""
    conn = _connect(db_path)
    conn.execute(
        "UPDATE agent_outputs SET is_current = 0 "
        "WHERE batch_id = ? AND startup_name = ? AND agent_number >= ?",
        (batch_id, startup_name, from_agent),
    )
    conn.commit()
    conn.close()


def get_current_outputs(
    batch_id: str,
    startup_name: str,
    db_path: Path | None = None,
) -> dict[int, dict]:
    """Return {agent_number: parsed_json} for all current outputs."""
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT agent_number, output_json FROM agent_outputs "
        "WHERE batch_id = ? AND startup_name = ? AND is_current = 1 "
        "ORDER BY agent_number",
        (batch_id, startup_name),
    ).fetchall()
    conn.close()
    return {row["agent_number"]: json.loads(row["output_json"]) for row in rows}


def get_all_batch_outputs(batch_id: str, db_path: Path | None = None) -> list[dict]:
    """Return all current outputs for every startup in a batch (for Agent 7)."""
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT startup_name, agent_number, output_json FROM agent_outputs "
        "WHERE batch_id = ? AND is_current = 1 ORDER BY startup_name, agent_number",
        (batch_id,),
    ).fetchall()
    conn.close()

    results: dict[str, dict[int, dict]] = {}
    for row in rows:
        name = row["startup_name"]
        results.setdefault(name, {})[row["agent_number"]] = json.loads(row["output_json"])
    return [{"startup_name": name, "outputs": outputs} for name, outputs in results.items()]


# ---------------------------------------------------------------------------
# Feedback log
# ---------------------------------------------------------------------------

def log_feedback(
    batch_id: str,
    startup_name: str,
    from_agent: int,
    to_agent: int,
    reason: str,
    iteration: int,
    db_path: Path | None = None,
) -> None:
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO feedback_log "
        "(batch_id, startup_name, from_agent, to_agent, reason, iteration, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (batch_id, startup_name, from_agent, to_agent, reason, iteration, _now()),
    )
    conn.commit()
    conn.close()
