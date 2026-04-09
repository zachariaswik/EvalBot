"""EvalBot web frontend — FastAPI application."""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sse_starlette.sse import EventSourceResponse

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
STARTUPS_DIR = BASE_DIR.parent / "Startups"
PROJECT_ROOT = BASE_DIR.parent
_ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
jobs: dict[str, dict] = {}          # job_id → {status, lines, batch_id}
_run_lock: asyncio.Lock | None = None
RUN_STATE_FILE = PROJECT_ROOT / "evalbot_run.json"


def _write_run_state(job_id: str, status: str, batch_id: str | None = None) -> None:
    RUN_STATE_FILE.write_text(
        json.dumps({"job_id": job_id, "status": status, "batch_id": batch_id}),
        encoding="utf-8",
    )


def _read_run_state() -> dict | None:
    if not RUN_STATE_FILE.exists():
        return None
    try:
        return json.loads(RUN_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _get_run_lock() -> asyncio.Lock:
    global _run_lock
    if _run_lock is None:
        _run_lock = asyncio.Lock()
    return _run_lock


def _python_binary() -> str:
    for p in [PROJECT_ROOT / ".venv313" / "bin" / "python",
              PROJECT_ROOT / ".venv" / "bin" / "python"]:
        if p.exists():
            return str(p)
    import sys
    return sys.executable


def _latest_batch_id() -> str | None:
    if not OUTPUT_DIR.exists():
        return None
    candidates = [d.name for d in OUTPUT_DIR.iterdir()
                  if d.is_dir() and d.name.startswith("batch_")
                  and d.name.split("_")[1].isdigit()]
    return max(candidates, key=lambda n: int(n.split("_")[1])) if candidates else None

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


# ---------------------------------------------------------------------------
# Run Batch routes
# ---------------------------------------------------------------------------

@app.get("/run", response_class=HTMLResponse)
async def run_page(request: Request):
    """Staging page — list Startups/ dirs and show upload form."""
    staged: list[dict] = []
    if STARTUPS_DIR.exists():
        for d in sorted(STARTUPS_DIR.iterdir()):
            if d.is_dir():
                files = [f.name for f in d.iterdir() if f.is_file()]
                staged.append({"name": d.name, "files": files})

    # Check for an active or recently completed run to reconnect to
    active_job: dict | None = None
    state = _read_run_state()
    if state:
        job_id = state.get("job_id", "")
        if job_id in jobs:
            # Job is live in this server process — reconnect
            active_job = {"job_id": job_id, "status": state["status"], "stale": False}
        elif state.get("status") == "running":
            # State file says running but server lost track (e.g. restart)
            active_job = {"job_id": job_id, "status": "interrupted", "stale": True}

    return templates.TemplateResponse(request, "run.html", {"staged": staged, "active_job": active_job})


@app.post("/api/upload")
async def upload_startup(
    startup_name: str = Form(...),
    files: list[UploadFile] = File(...),
):
    """Save uploaded files to Startups/{name}/."""
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
    if not startup_name or not startup_name.strip():
        raise HTTPException(status_code=422, detail="startup_name is required")

    startup_name = startup_name.strip()
    target_dir = STARTUPS_DIR / startup_name
    target_dir.mkdir(parents=True, exist_ok=True)

    saved = []
    for upload in files:
        suffix = Path(upload.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{suffix}' not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}",
            )
        dest = target_dir / (upload.filename or "upload")
        dest.write_bytes(await upload.read())
        saved.append(upload.filename)

    return JSONResponse({"startup_name": startup_name, "files": saved})


@app.delete("/api/startup/{name}")
async def delete_startup(name: str):
    """Remove a staged startup dir."""
    target = STARTUPS_DIR / name
    if not target.exists() or not target.is_dir():
        raise HTTPException(status_code=404, detail=f"Startup '{name}' not found")
    shutil.rmtree(target)
    return JSONResponse({"deleted": name})


@app.post("/api/run")
async def start_run(request: Request):
    """Start subprocess batch run, return {job_id}."""
    lock = _get_run_lock()
    if lock.locked():
        raise HTTPException(status_code=409, detail="A batch run is already in progress")

    # Parse optional startup_names from request body
    try:
        body = await request.json()
        startup_names: list[str] = body.get("startup_names") or []
    except Exception:
        startup_names = []

    # Check that there's something to run
    if not STARTUPS_DIR.exists() or not any(
        d.is_dir() for d in STARTUPS_DIR.iterdir()
    ):
        raise HTTPException(status_code=400, detail="No startups staged in Startups/ directory")

    if startup_names:
        # Validate every requested name actually exists
        missing = [n for n in startup_names if not (STARTUPS_DIR / n).is_dir()]
        if missing:
            raise HTTPException(status_code=400, detail=f"Unknown startup(s): {missing}")

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "lines": [], "batch_id": None}
    _write_run_state(job_id, "running")

    async def _run():
        try:
            async with lock:
                python = _python_binary()
                cmd = [python, "-u", "main.py", "batch", str(STARTUPS_DIR)]
                if startup_names:
                    cmd += ["--only"] + startup_names
                jobs[job_id]["lines"].append(f"$ {' '.join(cmd)}")
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                    cwd=str(PROJECT_ROOT),
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                )
                assert proc.stdout is not None
                async for raw_line in proc.stdout:
                    line = _ANSI_RE.sub("", raw_line.decode("utf-8", errors="replace")).rstrip()
                    if line:
                        jobs[job_id]["lines"].append(line)
                await proc.wait()

                if proc.returncode == 0:
                    batch_id = _latest_batch_id()
                    jobs[job_id]["batch_id"] = batch_id
                    jobs[job_id]["status"] = "done"
                    jobs[job_id]["lines"].append(f"__DONE__:{batch_id or ''}")
                    _write_run_state(job_id, "done", batch_id)
                else:
                    jobs[job_id]["lines"].append(f"Process exited with code {proc.returncode}")
                    jobs[job_id]["status"] = "error"
                    jobs[job_id]["lines"].append("__ERROR__")
                    _write_run_state(job_id, "error")
        except Exception as exc:
            jobs[job_id]["lines"].append(f"ERROR: {exc}")
            jobs[job_id]["status"] = "error"
            jobs[job_id]["lines"].append("__ERROR__")
            _write_run_state(job_id, "error")

    asyncio.create_task(_run())
    return JSONResponse({"job_id": job_id})


@app.get("/api/run/{job_id}/status")
async def run_status(job_id: str):
    """Polling fallback — return {status, batch_id}."""
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")
    return JSONResponse({"status": job["status"], "batch_id": job.get("batch_id")})


@app.get("/api/run/{job_id}/stream")
async def run_stream(request: Request, job_id: str):
    """SSE log stream for a running job."""
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown job_id")

    async def _generator():
        yield {"data": "Stream connected — waiting for output..."}
        sent = 0
        while True:
            if await request.is_disconnected():
                break
            lines = job["lines"]
            while sent < len(lines):
                yield {"data": lines[sent]}
                sent += 1
            if job["status"] in ("done", "error"):
                break
            await asyncio.sleep(0.3)

    return EventSourceResponse(_generator())
