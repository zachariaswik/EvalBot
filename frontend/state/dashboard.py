"""Dashboard state — loads aggregate batch stats for the homepage."""

from __future__ import annotations

from pathlib import Path

import reflex as rx

# ---------------------------------------------------------------------------
# Helpers (duplicated from former app.py to keep src/ untouched)
# ---------------------------------------------------------------------------

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


def _load_batches_from_fs() -> list[dict]:
    if not OUTPUT_DIR.exists():
        return []
    batches = []
    for d in sorted(OUTPUT_DIR.iterdir(), reverse=True):
        if d.is_dir() and d.name.startswith("batch_"):
            startup_count = sum(1 for s in d.iterdir() if s.is_dir())
            batches.append(
                {
                    "batch_id": d.name,
                    "created_at": "",
                    "description": "",
                    "startup_count": startup_count,
                }
            )
    return batches


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
    import json

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


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


class DashboardState(rx.State):
    batches: list[dict] = []
    total_startups: int = 0
    total_batches: int = 0
    vc_percent: int = 0
    top_startups: list[dict] = []  # retained for compatibility
    latest_batch_id: str = ""
    latest_batch_created: str = ""
    avg_startups_per_batch: float = 0.0
    largest_batch_id: str = ""
    largest_batch_size: int = 0
    is_loading: bool = True

    @rx.event
    async def load_data(self):
        self.is_loading = True
        yield

        db = _db_path()
        if db:
            from src.db import list_batches

            batches = list_batches(db)
        else:
            batches = _load_batches_from_fs()

        self.batches = batches
        self.total_startups = sum(b.get("startup_count", 0) for b in batches)
        self.total_batches = len(batches)
        self.vc_percent = 0
        self.top_startups = []
        self.latest_batch_id = ""
        self.latest_batch_created = ""
        self.avg_startups_per_batch = (
            round(self.total_startups / self.total_batches, 1) if self.total_batches > 0 else 0.0
        )
        largest = max(batches, key=lambda b: b.get("startup_count", 0), default=None)
        if largest:
            self.largest_batch_id = largest.get("batch_id", "")
            self.largest_batch_size = int(largest.get("startup_count", 0) or 0)
        else:
            self.largest_batch_id = ""
            self.largest_batch_size = 0
        self.is_loading = False
