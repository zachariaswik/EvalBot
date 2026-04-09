"""Batch state — loads startup scores, verdicts, and ranking for a batch."""

from __future__ import annotations

import json
from pathlib import Path

import reflex as rx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "Batch"


def _db_path() -> Path | None:
    candidate = PROJECT_ROOT / "evalbot.db"
    return candidate if candidate.exists() else None


def _get_bar_color(score: int) -> str:
    if score >= 70:
        return "#0a7c52"
    if score >= 50:
        return "#1b48c4"
    return "#b91c1c"


def _get_verdict_color(verdict: str) -> str:
    mapping = {
        "Top VC Candidate": "emerald",
        "Promising, Needs Sharper Focus": "blue",
        "Promising, But Needs Pivot": "blue",
        "Good Small Business, Not Venture-Scale": "orange",
        "Feature, Not a Company": "amber",
        "AI Wrapper With Weak Moat": "amber",
        "Reject": "red",
    }
    return mapping.get(verdict, "gray")


def _load_batch_from_fs(batch_id: str) -> list[dict]:
    batch_dir = OUTPUT_DIR / batch_id
    if not batch_dir.exists():
        return []
    return [
        {"startup_name": d.name, "pipeline_status": "completed"}
        for d in sorted(batch_dir.iterdir())
        if d.is_dir() and d.name != "__pycache__"
    ]


def _load_startup_outputs_from_fs(batch_id: str, startup_name: str) -> dict[int, dict]:
    json_path = OUTPUT_DIR / batch_id / startup_name / f"{startup_name}.json"
    if not json_path.exists():
        return {}
    data = json.loads(json_path.read_text())
    outputs: dict[int, dict] = {}
    for key, val in data.items():
        if key.startswith("agent") and key[5:].isdigit():
            outputs[int(key[5:])] = val
    return outputs


def _get_startup_outputs(batch_id: str, startup_name: str) -> dict[int, dict]:
    db = _db_path()
    if db:
        from src.db import get_current_outputs

        outputs = get_current_outputs(batch_id, startup_name, db)
        if outputs:
            return outputs
    return _load_startup_outputs_from_fs(batch_id, startup_name)


class BatchState(rx.State):
    current_batch_id: str = ""
    created_at: str = ""
    startup_count: int = 0
    startup_scores: list[dict] = []
    verdict_counts: dict[str, int] = {}
    shortlist: list[str] = []
    bar_chart_data: list[dict] = []
    pie_chart_data: list[dict] = []
    is_loading: bool = True
    not_found: bool = False

    @rx.event
    async def load_batch(self):
        self.is_loading = True
        self.not_found = False
        yield

        batch_id = self.router.page.params.get("batch_id", "")
        self.current_batch_id = batch_id

        db = _db_path()
        if db:
            from src.db import list_startups

            startups = list_startups(batch_id, db)
        else:
            startups = _load_batch_from_fs(batch_id)

        if not startups:
            self.not_found = True
            self.is_loading = False
            return

        self.startup_count = len(startups)

        startup_scores: list[dict] = []
        verdict_counts: dict[str, int] = {}
        shortlist: list[str] = []

        for s in startups:
            name = s["startup_name"]
            outputs = _get_startup_outputs(batch_id, name)
            a2 = outputs.get(2, {})
            verdict = a2.get("verdict", "Unknown") or "Unknown"
            score = a2.get("total_score", 0) or 0
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
            startup_scores.append(
                {
                    "name": name,
                    "score": score,
                    "verdict": verdict,
                    "verdict_color": _get_verdict_color(verdict),
                    "bar_color": _get_bar_color(score),
                    "pipeline_status": s.get("pipeline_status", ""),
                }
            )
            # Check agent 7 ranking
            if 7 in outputs and outputs[7].get("shortlist"):
                shortlist = outputs[7]["shortlist"]

        startup_scores.sort(key=lambda x: x["score"], reverse=True)

        # If no shortlist from per-startup outputs, check ranking.json
        if not shortlist:
            ranking_path = OUTPUT_DIR / batch_id / "ranking.json"
            if ranking_path.exists():
                try:
                    ranking_data = json.loads(ranking_path.read_text())
                    shortlist = ranking_data.get("shortlist", [])
                except Exception:
                    pass

        # Get batch created_at
        created_at = ""
        if db:
            from src.db import list_batches

            all_batches = list_batches(db)
            for b in all_batches:
                if b["batch_id"] == batch_id:
                    created_at = b.get("created_at", "")
                    break

        self.created_at = created_at
        self.startup_scores = startup_scores
        self.verdict_counts = verdict_counts
        self.shortlist = shortlist

        # Build chart data
        self.bar_chart_data = [
            {"name": s["name"], "score": s["score"]} for s in startup_scores
        ]
        self.pie_chart_data = [
            {"name": k, "value": v} for k, v in verdict_counts.items()
        ]

        self.is_loading = False
