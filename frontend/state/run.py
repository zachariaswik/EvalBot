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

def _get_backend_base() -> str:
    """Return the Starlette backend base URL by reading Reflex's generated env.json.

    In development mode Reflex runs the Vite frontend (e.g. :3000) and the
    Starlette backend (e.g. :8001) on separate ports.  env.json is generated
    at startup with the real backend port, so it is the authoritative source.
    Falls back to "" when env.json is absent (production mode where a single
    server handles both frontend and backend — relative URLs work there).
    """
    env_file = PROJECT_ROOT / ".web" / "env.json"
    try:
        data = json.loads(env_file.read_text(encoding="utf-8"))
        upload_url = data.get("UPLOAD", "")
        if upload_url and "/_upload" in upload_url:
            return upload_url.split("/_upload")[0]  # e.g. "http://localhost:8001"
    except Exception:
        pass
    return ""


def _folder_picker_js(backend_base: str) -> str:
    """Build the JS that wires the hidden folder-input to POST to the upload endpoint.

    backend_base is embedded directly so the correct port is used in dev mode
    (Vite frontend ≠ Starlette backend port).  The JS also mirrors Reflex's own
    getBackendURL() logic: if the backend hostname is a loopback alias it is
    replaced with window.location.hostname so the URL works when the dev server
    is accessed from another machine or behind a proxy.
    """
    return f"""
(function () {{
    var inp = document.getElementById('evalbot-folder-input');
    if (!inp) return;
    inp.setAttribute('webkitdirectory', '');
    inp.setAttribute('multiple', '');
    inp.onchange = function () {{
        var files = Array.from(inp.files);
        if (!files.length) return;
        var folderName = files[0].webkitRelativePath.split('/')[0];
        var allowed = ['.pdf', '.docx', '.txt', '.md'];
        var valid = files.filter(function(f) {{
            return allowed.some(function(ext) {{ return f.name.toLowerCase().endsWith(ext); }});
        }});
        if (!valid.length) {{
            alert('No supported files (.pdf, .docx, .txt, .md) found in folder.');
            inp.value = '';
            return;
        }}
        var fd = new FormData();
        fd.append('startup_name', folderName);
        valid.forEach(function(f) {{ fd.append('file', f, f.name); }});

        // Resolve the upload URL.  backendBase is injected by Python; when it
        // contains a loopback hostname (localhost / 0.0.0.0) we substitute the
        // browser's own hostname so the URL is reachable from any client —
        // identical to what Reflex's getBackendURL() does.
        var backendBase = '{backend_base}';
        var uploadUrl = '/upload-startup';
        if (backendBase) {{
            try {{
                var u = new URL(backendBase);
                var loopbacks = ['localhost', '0.0.0.0', '::', '0:0:0:0:0:0:0:0'];
                if (loopbacks.indexOf(u.hostname) !== -1) {{
                    u.hostname = window.location.hostname;
                    if (window.location.protocol === 'https:') {{
                        u.protocol = 'https:';
                        u.port = '';
                    }}
                }}
                uploadUrl = u.origin + '/upload-startup';
            }} catch(e) {{}}
        }}

        fetch(uploadUrl, {{method: 'POST', body: fd}})
            .then(function(r) {{ return r.json(); }})
            .then(function(d) {{
                if (d.ok) {{ window.location.reload(); }}
                else {{ alert(d.error || 'Upload failed'); inp.value = ''; }}
            }})
            .catch(function(err) {{
                console.error('EvalBot upload error:', err);
                alert('Upload failed \u2014 server error');
                inp.value = '';
            }});
    }};
}})();
"""


def _batch_picker_js(backend_base: str) -> str:
    """Build the JS that wires the hidden batch-input to POST multiple startups.

    Groups files by the second path segment (parts[1]) — each subfolder becomes
    one startup.  Files directly inside the picked folder (parts.length < 3) are
    ignored.  Each group is POSTed sequentially to /upload-startup; on success
    the page reloads.
    """
    return f"""
(function () {{
    var inp = document.getElementById('evalbot-batch-input');
    if (!inp) return;
    inp.setAttribute('webkitdirectory', '');
    inp.setAttribute('multiple', '');
    inp.onchange = function () {{
        var files = Array.from(inp.files);
        if (!files.length) return;
        var allowed = ['.pdf', '.docx', '.txt', '.md'];

        // Group files by second path segment (subfolder name)
        var groups = {{}};
        files.forEach(function(f) {{
            var parts = f.webkitRelativePath.split('/');
            if (parts.length < 3) return;  // skip top-level files
            var startupName = parts[1];
            var ext = f.name.toLowerCase();
            if (!allowed.some(function(e) {{ return ext.endsWith(e); }})) return;
            if (!groups[startupName]) groups[startupName] = [];
            groups[startupName].push(f);
        }});

        var names = Object.keys(groups);
        if (!names.length) {{
            alert('No startup subfolders found with supported files (.pdf, .docx, .txt, .md).\\nMake sure you pick the parent folder that contains startup folders.');
            inp.value = '';
            return;
        }}

        // Resolve the upload URL (same logic as _folder_picker_js)
        var backendBase = '{backend_base}';
        var uploadUrl = '/upload-startup';
        if (backendBase) {{
            try {{
                var u = new URL(backendBase);
                var loopbacks = ['localhost', '0.0.0.0', '::', '0:0:0:0:0:0:0:0'];
                if (loopbacks.indexOf(u.hostname) !== -1) {{
                    u.hostname = window.location.hostname;
                    if (window.location.protocol === 'https:') {{
                        u.protocol = 'https:';
                        u.port = '';
                    }}
                }}
                uploadUrl = u.origin + '/upload-startup';
            }} catch(e) {{}}
        }}

        // POST each group sequentially
        function postNext(idx) {{
            if (idx >= names.length) {{
                window.location.reload();
                return;
            }}
            var name = names[idx];
            var fd = new FormData();
            fd.append('startup_name', name);
            groups[name].forEach(function(f) {{ fd.append('file', f, f.name); }});
            fetch(uploadUrl, {{method: 'POST', body: fd}})
                .then(function(r) {{ return r.json(); }})
                .then(function(d) {{
                    if (d.ok) {{ postNext(idx + 1); }}
                    else {{ alert((d.error || 'Upload failed') + ' (' + name + ')'); inp.value = ''; }}
                }})
                .catch(function(err) {{
                    console.error('EvalBot batch upload error:', err);
                    alert('Upload failed \u2014 server error (' + name + ')');
                    inp.value = '';
                }});
        }}
        postNext(0);
    }};
}})();
"""


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
    status: str = "idle"  # idle | running | done | error | interrupted
    completed_batch_id: str = ""  # batch_id set after a run completes
    log_lines: list[str] = []
    show_log: bool = False
    run_error: str = ""
    filter_single: bool = False

    @rx.var
    def run_label(self) -> str:
        if len(self.staged) == 1:
            return "Run Single"
        return "Run Batch"

    @rx.var
    def has_multi_file(self) -> bool:
        return any(len(s.get("files", [])) > 1 for s in self.staged)

    @rx.var
    def staged_visible(self) -> list[dict]:
        """Staged list after applying the single-file filter."""
        if not self.filter_single:
            return self.staged
        return [s for s in self.staged if len(s.get("files", [])) > 1]

    # Progress tracking
    progress_total: int = 0
    progress_completed: list[dict] = []  # [{name, elapsed_s, timed_out}]
    # Parallel active startups — one entry per concurrently-running startup.
    # Each entry: {name, elapsed_s, current_role,
    #              a1_done, a1_active, ..., a6_done, a6_active}
    progress_active: list[dict] = []
    progress_ranking: bool = False  # True while Agent 7 ranking is running

    @rx.event
    async def load_staged(self):
        staged: list[dict] = []
        if STARTUPS_DIR.exists():
            for d in sorted(STARTUPS_DIR.iterdir()):
                if d.is_dir():
                    files = [f.name for f in d.iterdir() if f.is_file()]
                    staged.append({"name": d.name, "files": files})
        self.staged = staged

        # Check for an in-progress run from state file
        state = _read_run_state()
        if state and state.get("status") == "running":
            self.status = "interrupted"
            self.run_error = (
                "A previous run was interrupted (server restarted). "
                "Start a new run when ready."
            )
        yield rx.call_script(_folder_picker_js(_get_backend_base()))
        yield rx.call_script(_batch_picker_js(_get_backend_base()))

    @rx.event
    def remove_startup(self, name: str):
        target = STARTUPS_DIR / name
        if target.exists() and target.is_dir():
            shutil.rmtree(target)
        self.staged = [s for s in self.staged if s["name"] != name]

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
            self.progress_active = []
            self.progress_ranking = False

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

            # Per-startup start times (name → loop.time() when STARTUP_START received)
            startup_start_times: dict[str, float] = {}
            elapsed_task: asyncio.Task | None = None

            async def _tick_elapsed():
                """Update elapsed_s for every active startup once per second."""
                while True:
                    await asyncio.sleep(1)
                    try:
                        loop = asyncio.get_event_loop()
                        async with self:
                            if not self.progress_active:
                                continue
                            updated = []
                            for e in self.progress_active:
                                t0 = startup_start_times.get(e["name"])
                                new_elapsed = int(loop.time() - t0) if t0 else e["elapsed_s"]
                                updated.append({**e, "elapsed_s": new_elapsed})
                            self.progress_active = updated
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
                            await self._handle_progress(event_type, data, startup_start_times)
                        except asyncio.CancelledError:
                            raise
                        except Exception:
                            pass
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
        startup_start_times: dict,
    ) -> None:
        """Update progress state based on PROGRESS events (parallel-aware)."""
        loop = asyncio.get_event_loop()

        def _make_entry(name: str) -> dict:
            return {
                "name": name, "elapsed_s": 0, "current_role": "",
                "a1_done": False, "a1_active": False,
                "a2_done": False, "a2_active": False,
                "a3_done": False, "a3_active": False,
                "a4_done": False, "a4_active": False,
                "a5_done": False, "a5_active": False,
                "a6_done": False, "a6_active": False,
            }

        if event_type == "BATCH_START":
            async with self:
                self.progress_total = data.get("total", 0)

        elif event_type == "STARTUP_START":
            name = data.get("name", "")
            startup_start_times[name] = loop.time()
            async with self:
                self.progress_total = data.get("total", self.progress_total)
                # Add a new active entry for this startup
                self.progress_active = self.progress_active + [_make_entry(name)]

        elif event_type == "AGENT_START":
            name = data.get("name", "")
            agent = data.get("agent", 0)
            role = data.get("role", "")
            if 1 <= agent <= 6:
                async with self:
                    # Fallback: if pipeline didn't send name, update first active entry
                    if not name and len(self.progress_active) == 1:
                        name = self.progress_active[0]["name"]
                    self.progress_active = [
                        {**e, f"a{agent}_active": True, "current_role": role}
                        if e["name"] == name else e
                        for e in self.progress_active
                    ]

        elif event_type == "AGENT_DONE":
            name = data.get("name", "")
            agent = data.get("agent", 0)
            if 1 <= agent <= 6:
                async with self:
                    if not name and len(self.progress_active) == 1:
                        name = self.progress_active[0]["name"]
                    self.progress_active = [
                        {**e, f"a{agent}_done": True, f"a{agent}_active": False, "current_role": ""}
                        if e["name"] == name else e
                        for e in self.progress_active
                    ]

        elif event_type == "STARTUP_DONE":
            name = data.get("name", "")
            elapsed_s = data.get("elapsed_s", 0)
            if not elapsed_s:
                t0 = startup_start_times.get(name)
                elapsed_s = int(loop.time() - t0) if t0 else 0
            startup_start_times.pop(name, None)
            async with self:
                entry = {"name": name, "elapsed_s": elapsed_s, "timed_out": False}
                self.progress_completed = self.progress_completed + [entry]
                self.progress_active = [e for e in self.progress_active if e["name"] != name]

        elif event_type == "STARTUP_TIMEOUT":
            name = data.get("name", "")
            elapsed_s = data.get("elapsed_s", 0)
            startup_start_times.pop(name, None)
            async with self:
                entry = {"name": name, "elapsed_s": elapsed_s, "timed_out": True}
                self.progress_completed = self.progress_completed + [entry]
                self.progress_active = [e for e in self.progress_active if e["name"] != name]

        elif event_type == "RANKING_START":
            async with self:
                self.progress_ranking = True
