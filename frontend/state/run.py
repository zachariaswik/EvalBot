"""Run state — manages staged startups and batch execution with streaming progress."""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import uuid
from pathlib import Path

import reflex as rx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STARTUPS_DIR = PROJECT_ROOT / "Startups"
OUTPUT_DIR = PROJECT_ROOT / "output" / "Batch"
RUN_STATE_FILE = PROJECT_ROOT / "evalbot_run.json"
_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _python_binary() -> str:
    for p in [
        PROJECT_ROOT / ".venv313" / "bin" / "python",
        PROJECT_ROOT / ".venv" / "bin" / "python",
    ]:
        if p.exists():
            return str(p)
    import sys

    return sys.executable


def _latest_batch_id() -> str | None:
    if not OUTPUT_DIR.exists():
        return None
    candidates = [
        d.name
        for d in OUTPUT_DIR.iterdir()
        if d.is_dir()
        and d.name.startswith("batch_")
        and d.name.split("_")[1].isdigit()
    ]
    return max(candidates, key=lambda n: int(n.split("_")[1])) if candidates else None


def _read_run_state() -> dict | None:
    if not RUN_STATE_FILE.exists():
        return None
    try:
        return json.loads(RUN_STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return None


def _write_run_state(job_id: str, status: str, batch_id: str | None = None) -> None:
    RUN_STATE_FILE.write_text(
        json.dumps({"job_id": job_id, "status": status, "batch_id": batch_id}),
        encoding="utf-8",
    )


class RunState(rx.State):
    staged: list[dict] = []
    new_startup_name: str = ""
    status: str = "idle"  # idle | running | done | error | interrupted
    completed_batch_id: str = ""  # batch_id set after a run completes
    log_lines: list[str] = []
    show_log: bool = False
    run_error: str = ""
    filter_single: bool = False
    has_multi_file: bool = False  # True when at least one startup has >1 file
    upload_error: str = ""

    # Progress tracking
    progress_total: int = 0
    progress_completed: list[dict] = []
    progress_current_name: str = ""
    progress_current_agent: int = 0
    progress_current_role: str = ""
    progress_done_agents: list[int] = []
    progress_elapsed: int = 0

    @rx.event
    async def load_staged(self):
        staged: list[dict] = []
        if STARTUPS_DIR.exists():
            for d in sorted(STARTUPS_DIR.iterdir()):
                if d.is_dir():
                    files = [f.name for f in d.iterdir() if f.is_file()]
                    staged.append({"name": d.name, "files": files})
        self.staged = staged
        self.has_multi_file = any(len(s.get("files", [])) > 1 for s in staged)

        # Check for an in-progress run from state file
        state = _read_run_state()
        if state and state.get("status") == "running":
            self.status = "interrupted"
            self.run_error = (
                "A previous run was interrupted (server restarted). "
                "Start a new run when ready."
            )

    @rx.event
    async def upload_files(self, files: list[rx.UploadFile]):
        self.upload_error = ""
        name = self.new_startup_name.strip()
        if not name:
            self.upload_error = "Startup name is required."
            return
        if not files:
            self.upload_error = "Select at least one file."
            return

        ALLOWED = {".pdf", ".docx", ".txt", ".md"}
        target_dir = STARTUPS_DIR / name
        target_dir.mkdir(parents=True, exist_ok=True)

        saved: list[str] = []
        for upload in files:
            suffix = Path(upload.filename or "").suffix.lower()
            if suffix not in ALLOWED:
                self.upload_error = (
                    f"File type '{suffix}' not allowed. Use: {', '.join(ALLOWED)}"
                )
                return
            dest = target_dir / (upload.filename or "upload")
            dest.write_bytes(await upload.read())
            saved.append(upload.filename or "upload")

        # Update staged list
        idx = next((i for i, s in enumerate(self.staged) if s["name"] == name), -1)
        if idx >= 0:
            self.staged[idx] = {"name": name, "files": saved}
        else:
            self.staged = self.staged + [{"name": name, "files": saved}]

        self.new_startup_name = ""
        self.has_multi_file = any(len(s.get("files", [])) > 1 for s in self.staged)

    @rx.event
    def remove_startup(self, name: str):
        target = STARTUPS_DIR / name
        if target.exists() and target.is_dir():
            shutil.rmtree(target)
        self.staged = [s for s in self.staged if s["name"] != name]
        self.has_multi_file = any(len(s.get("files", [])) > 1 for s in self.staged)

    @rx.event
    def toggle_log(self):
        self.show_log = not self.show_log

    @rx.event
    def toggle_filter(self):
        self.filter_single = not self.filter_single

    @rx.event(background=True)
    async def start_run(self):
        async with self:
            if self.status == "running":
                return
            self.status = "running"
            self.log_lines = []
            self.completed_batch_id = ""
            self.run_error = ""
            self.progress_total = 0
            self.progress_completed = []
            self.progress_current_name = ""
            self.progress_current_agent = 0
            self.progress_current_role = ""
            self.progress_done_agents = []
            self.progress_elapsed = 0

        job_id = str(uuid.uuid4())
        _write_run_state(job_id, "running")

        try:
            python = _python_binary()

            # Get staged names for filter
            async with self:
                filter_single = self.filter_single
                staged = list(self.staged)

            startup_names = [
                s["name"]
                for s in staged
                if not filter_single or len(s.get("files", [])) > 1
            ]

            if not startup_names:
                async with self:
                    self.status = "error"
                    self.run_error = "No startups staged."
                return

            cmd = [python, "-u", "main.py", "batch", str(STARTUPS_DIR)]
            if startup_names:
                cmd += ["--only"] + startup_names

            async with self:
                self.log_lines = [f"$ {' '.join(cmd)}"]

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=str(PROJECT_ROOT),
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )

            # Track elapsed time
            start_time: float | None = None
            elapsed_task: asyncio.Task | None = None

            async def _tick_elapsed():
                nonlocal start_time
                while True:
                    await asyncio.sleep(1)
                    if start_time is None:
                        continue
                    # Skip update if client already disconnected (task cancelled)
                    try:
                        elapsed = int(asyncio.get_event_loop().time() - start_time)
                        async with self:
                            self.progress_elapsed = elapsed
                    except asyncio.CancelledError:
                        break

            elapsed_task = asyncio.create_task(_tick_elapsed())

            assert proc.stdout is not None
            async for raw_line in proc.stdout:
                line = _ANSI_RE.sub(
                    "", raw_line.decode("utf-8", errors="replace")
                ).rstrip()
                if not line:
                    continue

                if line.startswith("PROGRESS:"):
                    rest = line[len("PROGRESS:"):]
                    colon = rest.find(":")
                    if colon >= 0:
                        event_type = rest[:colon]
                        try:
                            data = json.loads(rest[colon + 1:])
                        except Exception:
                            data = {}
                        try:
                            await self._handle_progress(event_type, data, start_time)
                        except asyncio.CancelledError:
                            raise
                        except Exception:
                            pass
                        if event_type == "STARTUP_START":
                            start_time = asyncio.get_event_loop().time()
                else:
                    try:
                        async with self:
                            self.log_lines = self.log_lines + [line]
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        pass

            elapsed_task.cancel()
            await proc.wait()

            if proc.returncode == 0:
                run_batch_id = _latest_batch_id() or ""
                _write_run_state(job_id, "done", run_batch_id)
                async with self:
                    self.status = "done"
                    self.completed_batch_id = run_batch_id
                    self.staged = []
            else:
                _write_run_state(job_id, "error")
                async with self:
                    self.status = "error"
                    self.log_lines = self.log_lines + [
                        f"Process exited with code {proc.returncode}"
                    ]

        except asyncio.CancelledError:
            pass
        except Exception as exc:
            _write_run_state(job_id, "error")
            async with self:
                self.status = "error"
                self.log_lines = self.log_lines + [f"ERROR: {exc}"]

    async def _handle_progress(
        self,
        event_type: str,
        data: dict,
        start_time: float | None,
    ) -> None:
        """Update progress state based on PROGRESS events."""
        loop = asyncio.get_event_loop()

        if event_type == "BATCH_START":
            async with self:
                self.progress_total = data.get("total", 0)

        elif event_type == "STARTUP_START":
            async with self:
                self.progress_total = data.get("total", self.progress_total)
                self.progress_current_name = data.get("name", "")
                self.progress_current_agent = 0
                self.progress_current_role = ""
                self.progress_done_agents = []
                self.progress_elapsed = 0

        elif event_type == "AGENT_START":
            async with self:
                self.progress_current_agent = data.get("agent", 0)
                self.progress_current_role = data.get("role", "")

        elif event_type == "AGENT_DONE":
            async with self:
                agent = data.get("agent", 0)
                if agent not in self.progress_done_agents:
                    self.progress_done_agents = self.progress_done_agents + [agent]
                self.progress_current_agent = 0
                self.progress_current_role = ""

        elif event_type == "STARTUP_DONE":
            elapsed = 0
            if start_time is not None:
                elapsed = int(loop.time() - start_time)
            async with self:
                entry = {
                    "name": data.get("name", ""),
                    "elapsed_s": data.get("elapsed_s", elapsed),
                }
                self.progress_completed = self.progress_completed + [entry]
                self.progress_current_name = ""
                self.progress_current_agent = 0
                self.progress_current_role = ""
                self.progress_done_agents = []
                self.progress_elapsed = 0
