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
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hall_of_fame (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id            TEXT NOT NULL,
    startup_name        TEXT NOT NULL,
    weighted_score      REAL NOT NULL,
    score_tier          TEXT NOT NULL,
    agent0_output_json  TEXT NOT NULL,
    agent2_output_json  TEXT NOT NULL,
    created_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_hall_of_fame_score ON hall_of_fame(weighted_score DESC);
CREATE INDEX IF NOT EXISTS idx_hall_of_fame_created ON hall_of_fame(created_at DESC);

CREATE TABLE IF NOT EXISTS retry_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id            TEXT NOT NULL,
    startup_name        TEXT NOT NULL,
    agent_number        INTEGER NOT NULL,
    intended_model      TEXT NOT NULL,
    actual_model        TEXT NOT NULL,
    retry_count         INTEGER NOT NULL DEFAULT 0,
    fallback_occurred   INTEGER NOT NULL DEFAULT 0,
    recovery_occurred   INTEGER NOT NULL DEFAULT 0,
    error_type          TEXT,
    created_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_retry_log_batch ON retry_log(batch_id);
CREATE INDEX IF NOT EXISTS idx_retry_log_startup ON retry_log(batch_id, startup_name);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DB_PATH
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")   # wait up to 5 s before SQLITE_BUSY
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
    db_path: Path | None = None,
) -> None:
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO agent_outputs "
        "(batch_id, startup_name, agent_number, output_json, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (batch_id, startup_name, agent_number, output_json, _now()),
    )
    conn.commit()
    conn.close()


def get_current_outputs(
    batch_id: str,
    startup_name: str,
    db_path: Path | None = None,
) -> dict[int, dict]:
    """Return {agent_number: parsed_json} for all stored outputs."""
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT agent_number, output_json FROM agent_outputs "
        "WHERE batch_id = ? AND startup_name = ? "
        "ORDER BY created_at DESC",
        (batch_id, startup_name),
    ).fetchall()
    conn.close()

    result: dict[int, dict] = {}
    for row in rows:
        agent_num = row["agent_number"]
        if agent_num in result:
            continue  # Already have this agent (latest wins)

        top_level_parsed = json.loads(row["output_json"])

        # Check if we have raw_output that needs inner parsing
        if "raw_output" in top_level_parsed:
            raw = top_level_parsed["raw_output"]
            if isinstance(raw, str):
                try:
                    result[agent_num] = json.loads(raw)
                    continue
                except json.JSONDecodeError:
                    continue

        result[agent_num] = top_level_parsed

    return result


def get_all_batch_outputs(batch_id: str, db_path: Path | None = None) -> list[dict]:
    """Return all outputs for every startup in a batch (for Agent 7)."""
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT startup_name, agent_number, output_json FROM agent_outputs "
        "WHERE batch_id = ? ORDER BY startup_name, agent_number, created_at DESC",
        (batch_id,),
    ).fetchall()
    conn.close()

    results: dict[str, dict[int, dict]] = {}
    for row in rows:
        name = row["startup_name"]
        agent_num = row["agent_number"]
        if name not in results:
            results[name] = {}
        if agent_num not in results[name]:  # latest wins (ORDER BY created_at DESC)
            results[name][agent_num] = json.loads(row["output_json"])
    return [{"startup_name": name, "outputs": outputs} for name, outputs in results.items()]



# ---------------------------------------------------------------------------
# Hall of Fame — Top-performing startup ideas
# ---------------------------------------------------------------------------

def insert_to_hall_of_fame(
    batch_id: str,
    startup_name: str,
    weighted_score: float,
    score_tier: str,
    agent0_output: dict,
    agent2_output: dict,
    db_path: Path | None = None,
) -> None:
    """Insert a high-scoring idea into the hall of fame.
    
    Maintains HALL_OF_FAME_SIZE by removing lowest-scoring entries when full.
    """
    from .config import HALL_OF_FAME_SIZE, HALL_OF_FAME_MIN_SCORE
    
    # Only insert if score meets minimum threshold
    if weighted_score < HALL_OF_FAME_MIN_SCORE:
        return
    
    conn = _connect(db_path)
    
    # Insert new entry
    conn.execute(
        "INSERT INTO hall_of_fame "
        "(batch_id, startup_name, weighted_score, score_tier, agent0_output_json, agent2_output_json, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            batch_id,
            startup_name,
            weighted_score,
            score_tier,
            json.dumps(agent0_output),
            json.dumps(agent2_output),
            _now(),
        ),
    )
    
    # Check if we exceed size limit
    count = conn.execute("SELECT COUNT(*) as cnt FROM hall_of_fame").fetchone()["cnt"]
    
    if count > HALL_OF_FAME_SIZE:
        # Remove lowest-scoring entries to maintain size limit
        conn.execute(
            "DELETE FROM hall_of_fame WHERE id IN ("
            "  SELECT id FROM hall_of_fame "
            "  ORDER BY weighted_score ASC, created_at ASC "
            "  LIMIT ?"
            ")",
            (count - HALL_OF_FAME_SIZE,),
        )
    
    conn.commit()
    conn.close()


def get_top_ideas(
    limit: int = 5,
    min_score: float = 0,
    db_path: Path | None = None,
) -> list[dict]:
    """Retrieve top-scoring ideas from the hall of fame.
    
    Returns list of dicts with: id, batch_id, startup_name, weighted_score,
    score_tier, agent0_output, agent2_output, created_at
    """
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT id, batch_id, startup_name, weighted_score, score_tier, "
        "agent0_output_json, agent2_output_json, created_at "
        "FROM hall_of_fame "
        "WHERE weighted_score >= ? "
        "ORDER BY weighted_score DESC, created_at DESC "
        "LIMIT ?",
        (min_score, limit),
    ).fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row["id"],
            "batch_id": row["batch_id"],
            "startup_name": row["startup_name"],
            "weighted_score": row["weighted_score"],
            "score_tier": row["score_tier"],
            "agent0_output": json.loads(row["agent0_output_json"]),
            "agent2_output": json.loads(row["agent2_output_json"]),
            "created_at": row["created_at"],
        })
    
    return results


def get_relevant_examples(
    prior_scores: dict[str, float] | None = None,
    limit: int = 3,
    db_path: Path | None = None,
) -> list[dict]:
    """Get hall of fame examples most relevant to current weaknesses.
    
    If prior_scores provided, selects examples that scored high where
    the prior attempt scored low. Otherwise returns top N overall.
    
    Args:
        prior_scores: Dict of dimension -> score (e.g., {"problem_severity": 12})
        limit: Number of examples to return
        db_path: Database path override
    
    Returns:
        List of hall of fame entries, prioritized by relevance
    """
    all_ideas = get_top_ideas(limit=20, min_score=50, db_path=db_path)
    
    if not all_ideas:
        return []
    
    if not prior_scores:
        # No weaknesses identified, return top performers
        return all_ideas[:limit]
    
    # Identify weak dimensions (below 70% of max score)
    dimension_max_scores = {
        "problem_severity": 20,
        "market_size": 20,
        "differentiation": 15,
        "founder_insight": 15,
        "moat_potential": 10,
        "business_model": 10,
        "venture_potential": 10,
    }
    
    weak_dimensions = []
    for dim, score in prior_scores.items():
        max_score = dimension_max_scores.get(dim, 20)
        if score < (max_score * 0.7):  # Weak if below 70%
            weak_dimensions.append(dim)
    
    if not weak_dimensions:
        # No clear weaknesses, return top performers
        return all_ideas[:limit]
    
    # Score each example by how well it performs on weak dimensions
    scored_examples = []
    for idea in all_ideas:
        agent2 = idea["agent2_output"]
        dim_scores = agent2.get("dimension_scores", {})
        
        # Sum scores on weak dimensions
        relevance_score = 0
        for dim in weak_dimensions:
            dim_score = dim_scores.get(dim, 0)
            max_score = dimension_max_scores.get(dim, 20)
            # Normalize to 0-1 and add to relevance
            relevance_score += dim_score / max_score
        
        scored_examples.append((relevance_score, idea))
    
    # Sort by relevance (high relevance = strong where we're weak)
    scored_examples.sort(key=lambda x: x[0], reverse=True)
    
    # Return top N most relevant
    return [idea for _, idea in scored_examples[:limit]]


def clear_hall_of_fame(db_path: Path | None = None) -> int:
    """Clear all entries from hall of fame. Returns number of entries deleted."""
    conn = _connect(db_path)
    cursor = conn.execute("DELETE FROM hall_of_fame")
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count


def get_hall_of_fame_stats(db_path: Path | None = None) -> dict:
    """Get statistics about the hall of fame."""
    conn = _connect(db_path)
    
    stats = conn.execute(
        "SELECT "
        "  COUNT(*) as count, "
        "  AVG(weighted_score) as avg_score, "
        "  MIN(weighted_score) as min_score, "
        "  MAX(weighted_score) as max_score "
        "FROM hall_of_fame"
    ).fetchone()
    
    conn.close()
    
    return {
        "count": stats["count"],
        "avg_score": stats["avg_score"] if stats["avg_score"] else 0,
        "min_score": stats["min_score"] if stats["min_score"] else 0,
        "max_score": stats["max_score"] if stats["max_score"] else 0,
    }


# ---------------------------------------------------------------------------
# Retry & Fallback Logging
# ---------------------------------------------------------------------------

def log_retry_event(
    batch_id: str,
    startup_name: str,
    agent_number: int,
    intended_model: str,
    actual_model: str,
    retry_count: int,
    fallback_occurred: bool,
    recovery_occurred: bool,
    error_type: str | None = None,
    db_path: Path | None = None,
) -> None:
    """Log a retry/fallback event for an agent execution."""
    conn = _connect(db_path)
    conn.execute(
        "INSERT INTO retry_log "
        "(batch_id, startup_name, agent_number, intended_model, actual_model, "
        "retry_count, fallback_occurred, recovery_occurred, error_type, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            batch_id,
            startup_name,
            agent_number,
            intended_model,
            actual_model,
            retry_count,
            1 if fallback_occurred else 0,
            1 if recovery_occurred else 0,
            error_type,
            _now(),
        ),
    )
    conn.commit()
    conn.close()


def get_retry_stats(batch_id: str, db_path: Path | None = None) -> dict:
    """Get retry/fallback statistics for a batch."""
    conn = _connect(db_path)
    
    # Overall stats
    overall = conn.execute(
        "SELECT "
        "  COUNT(*) as total_events, "
        "  SUM(fallback_occurred) as fallback_count, "
        "  SUM(recovery_occurred) as recovery_count, "
        "  SUM(retry_count) as total_retries, "
        "  AVG(retry_count) as avg_retries "
        "FROM retry_log "
        "WHERE batch_id = ?",
        (batch_id,),
    ).fetchone()
    
    # Per-agent breakdown
    per_agent = conn.execute(
        "SELECT "
        "  agent_number, "
        "  COUNT(*) as events, "
        "  SUM(fallback_occurred) as fallbacks, "
        "  SUM(recovery_occurred) as recoveries, "
        "  SUM(retry_count) as total_retries, "
        "  intended_model, "
        "  actual_model "
        "FROM retry_log "
        "WHERE batch_id = ? "
        "GROUP BY agent_number, intended_model, actual_model "
        "ORDER BY agent_number",
        (batch_id,),
    ).fetchall()
    
    # Error type breakdown
    error_types = conn.execute(
        "SELECT error_type, COUNT(*) as count "
        "FROM retry_log "
        "WHERE batch_id = ? AND error_type IS NOT NULL "
        "GROUP BY error_type "
        "ORDER BY count DESC",
        (batch_id,),
    ).fetchall()
    
    conn.close()
    
    return {
        "total_events": overall["total_events"],
        "fallback_count": overall["fallback_count"] or 0,
        "recovery_count": overall["recovery_count"] or 0,
        "total_retries": overall["total_retries"] or 0,
        "avg_retries": overall["avg_retries"] or 0.0,
        "per_agent": [
            {
                "agent_number": row["agent_number"],
                "events": row["events"],
                "fallbacks": row["fallbacks"] or 0,
                "recoveries": row["recoveries"] or 0,
                "total_retries": row["total_retries"] or 0,
                "intended_model": row["intended_model"],
                "actual_model": row["actual_model"],
            }
            for row in per_agent
        ],
        "error_types": [
            {"error_type": row["error_type"], "count": row["count"]}
            for row in error_types
        ],
    }


# ---------------------------------------------------------------------------
# Frontend query helpers
# ---------------------------------------------------------------------------

def list_batches(db_path: Path | None = None) -> list[dict]:
    """Return all batches ordered by created_at desc, with startup count."""
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT b.batch_id, b.created_at, b.description, COUNT(s.id) as startup_count "
        "FROM batches b LEFT JOIN startups s ON b.batch_id = s.batch_id "
        "GROUP BY b.batch_id "
        "ORDER BY b.created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def list_startups(batch_id: str, db_path: Path | None = None) -> list[dict]:
    """Return all startups in a batch with their pipeline_status."""
    conn = _connect(db_path)
    rows = conn.execute(
        "SELECT startup_name, pipeline_status FROM startups "
        "WHERE batch_id = ? ORDER BY startup_name",
        (batch_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]