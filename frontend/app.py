"""EvalBot web frontend — FastAPI application."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.db import (
    get_all_batch_outputs,
    get_current_outputs,
    init_db,
    list_batches,
    list_startups,
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "Batch"

app = FastAPI(title="EvalBot", docs_url=None, redoc_url=None)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _db_path() -> Path | None:
    """Return path to evalbot.db if it exists, else None."""
    candidate = Path(__file__).resolve().parent.parent / "evalbot.db"
    return candidate if candidate.exists() else None


def _load_startup_outputs_from_fs(batch_id: str, startup_name: str) -> dict[int, dict]:
    """Fallback: load agent outputs from JSON file on disk."""
    json_path = OUTPUT_DIR / batch_id / startup_name / f"{startup_name}.json"
    if not json_path.exists():
        return {}
    data = json.loads(json_path.read_text())
    outputs: dict[int, dict] = {}
    for key, val in data.items():
        if key.startswith("agent") and key[5:].isdigit():
            outputs[int(key[5:])] = val
    return outputs


def _load_batch_from_fs(batch_id: str) -> list[dict]:
    """Fallback: list startup dirs from filesystem for a given batch."""
    batch_dir = OUTPUT_DIR / batch_id
    if not batch_dir.exists():
        return []
    return [
        {"startup_name": d.name, "pipeline_status": "completed"}
        for d in sorted(batch_dir.iterdir())
        if d.is_dir() and d.name != "__pycache__"
    ]


def _load_batches_from_fs() -> list[dict]:
    """Fallback: list batch dirs from filesystem."""
    if not OUTPUT_DIR.exists():
        return []
    batches = []
    for d in sorted(OUTPUT_DIR.iterdir(), reverse=True):
        if d.is_dir() and d.name.startswith("batch_"):
            startup_count = sum(1 for s in d.iterdir() if s.is_dir())
            batches.append({
                "batch_id": d.name,
                "created_at": "",
                "description": "",
                "startup_count": startup_count,
            })
    return batches


def _get_startup_outputs(batch_id: str, startup_name: str) -> dict[int, dict]:
    db = _db_path()
    if db:
        outputs = get_current_outputs(batch_id, startup_name, db)
        if outputs:
            return outputs
    return _load_startup_outputs_from_fs(batch_id, startup_name)


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


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    db = _db_path()
    if db:
        batches = list_batches(db)
    else:
        batches = _load_batches_from_fs()

    total_startups = sum(b.get("startup_count", 0) for b in batches)
    total_batches = len(batches)

    # Compute VC candidate % by scanning first batch for quick stats
    vc_count = 0
    latest_batch_data = None
    if batches:
        first_batch_id = batches[0]["batch_id"]
        if db:
            first_startups = list_startups(first_batch_id, db)
        else:
            first_startups = _load_batch_from_fs(first_batch_id)

        top_startups = []
        for s in first_startups[:10]:
            outputs = _get_startup_outputs(first_batch_id, s["startup_name"])
            a2 = outputs.get(2, {})
            verdict = a2.get("verdict", "")
            score = a2.get("total_score", 0)
            if verdict == "Top VC Candidate":
                vc_count += 1
            top_startups.append({
                "name": s["startup_name"],
                "verdict": verdict,
                "score": score,
                "verdict_color": _get_verdict_color(verdict),
            })
        top_startups.sort(key=lambda x: x["score"], reverse=True)
        latest_batch_data = {
            "batch_id": first_batch_id,
            "created_at": batches[0].get("created_at", ""),
            "top_startups": top_startups[:3],
        }

    vc_percent = round((vc_count / total_startups * 100) if total_startups > 0 else 0)

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "batches": batches,
            "stats": {
                "total_startups": total_startups,
                "total_batches": total_batches,
                "vc_percent": vc_percent,
            },
            "latest_batch": latest_batch_data,
        },
    )


@app.get("/batch/{batch_id}", response_class=HTMLResponse)
async def batch_detail(request: Request, batch_id: str):
    db = _db_path()
    if db:
        startups = list_startups(batch_id, db)
    else:
        startups = _load_batch_from_fs(batch_id)

    if not startups:
        raise HTTPException(status_code=404, detail=f"Batch '{batch_id}' not found")

    # Load per-startup scores and verdicts
    startup_scores: list[dict] = []
    verdict_counts: dict[str, int] = {}
    ranking: dict | None = None

    for s in startups:
        name = s["startup_name"]
        outputs = _get_startup_outputs(batch_id, name)
        a2 = outputs.get(2, {})
        verdict = a2.get("verdict", "Unknown")
        score = a2.get("total_score", 0)
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        startup_scores.append({
            "name": name,
            "score": score,
            "verdict": verdict,
            "verdict_color": _get_verdict_color(verdict),
        })
        # Agent 7 ranking is stored under a special "ranking" startup name or batch-level
        if 7 in outputs:
            ranking = outputs[7]

    startup_scores.sort(key=lambda x: x["score"], reverse=True)

    # Try to get Agent 7 ranking from a dedicated ranking entry
    if ranking is None:
        # Check if there's a ranking.json file
        ranking_path = OUTPUT_DIR / batch_id / "ranking.json"
        if ranking_path.exists():
            ranking = json.loads(ranking_path.read_text())

    # Get batch metadata
    created_at = ""
    if db:
        all_batches = list_batches(db)
        for b in all_batches:
            if b["batch_id"] == batch_id:
                created_at = b.get("created_at", "")
                break

    return templates.TemplateResponse(
        request,
        "batch.html",
        {
            "batch_id": batch_id,
            "created_at": created_at,
            "startups": startups,
            "startup_scores": startup_scores,
            "verdict_counts": verdict_counts,
            "ranking": ranking,
        },
    )


@app.get("/batch/{batch_id}/{startup_name}", response_class=HTMLResponse)
async def startup_detail(request: Request, batch_id: str, startup_name: str):
    outputs = _get_startup_outputs(batch_id, startup_name)
    if not outputs:
        raise HTTPException(
            status_code=404,
            detail=f"Startup '{startup_name}' in batch '{batch_id}' not found",
        )

    a2 = outputs.get(2, {})
    verdict = a2.get("verdict", "")

    return templates.TemplateResponse(
        request,
        "startup.html",
        {
            "batch_id": batch_id,
            "startup_name": startup_name,
            "verdict_color": _get_verdict_color(verdict),
            "a1": outputs.get(1),
            "a2": a2 or None,
            "a3": outputs.get(3),
            "a4": outputs.get(4),
            "a5": outputs.get(5),
            "a6": outputs.get(6),
        },
    )


@app.get("/roadmap", response_class=HTMLResponse)
async def roadmap(request: Request):
    return templates.TemplateResponse(request, "roadmap.html")
