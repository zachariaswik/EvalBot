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
