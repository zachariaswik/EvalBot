"""Batch state — loads startup scores, verdicts, and ranking for a batch."""

from __future__ import annotations

import json
from pathlib import Path

import reflex as rx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "Batch"

VERDICT_HEX: dict[str, str] = {
    "Top VC Candidate": "#0a7c52",
    "Promising, Needs Sharper Focus": "#1b48c4",
    "Promising, But Needs Pivot": "#3b6fd4",
    "Good Small Business, Not Venture-Scale": "#a85800",
    "Feature, Not a Company": "#92400e",
    "AI Wrapper With Weak Moat": "#92400e",
    "Reject": "#b91c1c",
}

_POSITIVE_VERDICTS = {"Top VC Candidate", "Promising, Needs Sharper Focus", "Promising, But Needs Pivot"}
_NEGATIVE_VERDICTS = {"Reject", "Feature, Not a Company", "AI Wrapper With Weak Moat"}


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
    score_histogram: list[dict] = []
    score_zones: list[dict] = []
    pie_chart_data: list[dict] = []
    verdict_distribution: list[dict] = []
    batch_sentiment: str = ""
    batch_sentiment_hex: str = "#7188a4"
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

        # Build score distribution histogram — trimmed to actual data range
        bucket_counts = [0] * 10
        for s in startup_scores:
            bucket_counts[min(int(s["score"]) // 10, 9)] += 1

        non_zero = [i for i, c in enumerate(bucket_counts) if c > 0]
        lo, hi = (non_zero[0], non_zero[-1]) if non_zero else (0, 9)
        trimmed = list(range(lo, hi + 1))
        max_count = max(bucket_counts[i] for i in trimmed) or 1

        self.score_histogram = [
            {
                "label": str(i * 10),
                "count": bucket_counts[i],
                "has_count": bucket_counts[i] > 0,
                "height_px": round(bucket_counts[i] / max_count * 100),
                "fill": "#0a7c52" if i >= 7 else ("#1b48c4" if i >= 5 else "#b91c1c"),
            }
            for i in trimmed
        ]

        # Zone descriptors — only zones present in the trimmed range
        red = sum(1 for i in trimmed if i < 5)
        blue = sum(1 for i in trimmed if 5 <= i < 7)
        green = sum(1 for i in trimmed if i >= 7)
        zones = []
        if red:
            zones.append({"flex": red, "label": "Reject zone", "hex": "#b91c1c", "bg": "rgba(185,28,28,0.05)"})
        if blue:
            zones.append({"flex": blue, "label": "Promising", "hex": "#1b48c4", "bg": "rgba(27,72,196,0.05)"})
        if green:
            zones.append({"flex": green, "label": "VC Candidate", "hex": "#0a7c52", "bg": "rgba(10,124,82,0.05)"})
        self.score_zones = zones
        self.pie_chart_data = [
            {"name": k, "value": v} for k, v in verdict_counts.items()
        ]

        # Build verdict distribution (sorted by count desc, precomputed for UI)
        n_total = len(startups)
        sorted_v = sorted(verdict_counts.items(), key=lambda x: x[1], reverse=True)
        dist = []
        for vname, vcount in sorted_v:
            hex_col = VERDICT_HEX.get(vname, "#7188a4")
            pct = round(vcount / n_total * 100) if n_total > 0 else 0
            dist.append({
                "name": vname,
                "count": vcount,
                "pct_str": f"{pct}%",
                "fill_width": f"{pct}%",
                "hex": hex_col,
            })
        self.verdict_distribution = dist

        # Compute batch sentiment
        positive = sum(v for k, v in verdict_counts.items() if k in _POSITIVE_VERDICTS)
        negative = sum(v for k, v in verdict_counts.items() if k in _NEGATIVE_VERDICTS)
        if n_total > 0 and positive >= n_total * 0.5:
            self.batch_sentiment = "Strong batch"
            self.batch_sentiment_hex = "#0a7c52"
        elif n_total > 0 and negative >= n_total * 0.5:
            self.batch_sentiment = "Challenging batch"
            self.batch_sentiment_hex = "#b91c1c"
        else:
            self.batch_sentiment = "Mixed signals"
            self.batch_sentiment_hex = "#a85800"

        self.is_loading = False
