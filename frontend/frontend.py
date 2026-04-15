"""AltaLab Reflex app — entry point.

Run locally:
    source .venv313/bin/activate
    reflex run

Production:
    reflex run --env prod --loglevel warning
"""

import re
from pathlib import Path

import reflex as rx
from reflex.utils import console as _rx_console
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Reflex warns every time a background task pushes a delta to a client that has
# navigated away. The message is identical each time (same session token), so we
# force deduplication: the user sees the warning once, then silence.
_orig_rx_warn = _rx_console.warn

def _deduping_warn(msg: str, *, dedupe: bool = False, **kwargs):
    if "disconnected client" in msg:
        dedupe = True
    _orig_rx_warn(msg, dedupe=dedupe, **kwargs)

_rx_console.warn = _deduping_warn

from frontend.pages.dashboard import dashboard_page
from frontend.pages.batch import batch_page
from frontend.pages.startup import startup_page
from frontend.pages.run import run_page
from frontend.pages.roadmap import roadmap_page
from frontend.pages.roadmap_detail import (
    analyst_profiles_page,
    deal_flow_page,
    portfolio_tracking_page,
    automated_reports_page,
    partner_api_page,
    cohort_analytics_page,
    founder_portal_page,
    platform_features_page,
    course_integration_page,
)
from frontend.pdf_report import generate_startup_feedback_pdf
from frontend.state.dashboard import DashboardState
from frontend.state.batch import BatchState
from frontend.state.startup import StartupState, _get_startup_outputs
from frontend.state.run import RunState

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_STARTUPS_DIR = PROJECT_ROOT / "Startups"
_ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md"}
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _save_folder_files(
    startup_name: str,
    files: list[tuple[str, bytes]],  # (filename, content)
    startups_dir: Path = _STARTUPS_DIR,
) -> tuple[list[str], str | None]:
    """Save validated files to Startups/{startup_name}/.
    Returns (saved_filenames, error_message_or_None).
    """
    name = startup_name.strip().replace("..", "").strip("/").strip("\\")
    if not name:
        return [], "No startup name provided."
    target = startups_dir / name
    target.mkdir(parents=True, exist_ok=True)
    saved: list[str] = []
    for filename, content in files:
        if Path(filename).suffix.lower() in _ALLOWED_EXTS:
            (target / Path(filename).name).write_bytes(content)
            saved.append(filename)
    if not saved:
        return [], "No supported files (.pdf .docx .txt .md) found in folder."
    return saved, None


def _safe_download_filename(startup_name: str) -> str:
    sanitized = _SAFE_FILENAME_RE.sub("_", startup_name.strip()).strip("._")
    if not sanitized:
        sanitized = "startup"
    return f"{sanitized}_evalbot_feedback.pdf"


def _build_startup_pdf_response(batch_id: str, startup_name: str) -> Response | JSONResponse:
    outputs = _get_startup_outputs(batch_id, startup_name)
    if not outputs:
        return JSONResponse({"ok": False, "error": "Startup outputs not found."}, status_code=404)

    pdf_bytes = generate_startup_feedback_pdf(batch_id, startup_name, outputs)
    filename = _safe_download_filename(startup_name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


app = rx.App(
    theme=rx.theme(
        appearance="light",
        accent_color="indigo",
        radius="medium",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap",
    ],
    style={
        "fontFamily": "'Plus Jakarta Sans', system-ui, sans-serif",
        "background": "#f4f6fb",
    },
)


async def _upload_startup_handler(request: Request) -> JSONResponse:
    form = await request.form()
    startup_name = str(form.get("startup_name", ""))
    files: list[tuple[str, bytes]] = []
    for key, value in form.multi_items():
        if key == "file" and hasattr(value, "filename"):
            files.append((value.filename or "", await value.read()))
    saved, err = _save_folder_files(startup_name, files)
    if err:
        return JSONResponse({"ok": False, "error": err})
    return JSONResponse({"ok": True, "startup": startup_name.strip(), "files": saved})


async def _download_startup_pdf_handler(request: Request) -> Response | JSONResponse:
    batch_id = str(request.query_params.get("batch_id", "")).strip()
    startup_name = str(request.query_params.get("startup_name", "")).strip()
    if not batch_id or not startup_name:
        return JSONResponse(
            {"ok": False, "error": "batch_id and startup_name are required."},
            status_code=400,
        )
    return _build_startup_pdf_response(batch_id, startup_name)


app._api.add_route("/upload-startup", _upload_startup_handler, methods=["POST"])
app._api.add_route("/download-startup-pdf", _download_startup_pdf_handler, methods=["GET"])

app.add_page(
    dashboard_page,
    route="/",
    on_load=DashboardState.load_data,
    title="AltaLab — Dashboard",
)

app.add_page(
    batch_page,
    route="/batch/[batch_id]",
    on_load=BatchState.load_batch,
    title="Batch — AltaLab",
)

app.add_page(
    startup_page,
    route="/batch/[batch_id]/[startup_name]",
    on_load=StartupState.load_startup,
    title="Startup — AltaLab",
)

app.add_page(
    run_page,
    route="/run",
    on_load=RunState.load_staged,
    title="Run Batch — AltaLab",
)

app.add_page(
    roadmap_page,
    route="/roadmap",
    title="Roadmap — AltaLab",
)

app.add_page(analyst_profiles_page, route="/roadmap/analyst-profiles", title="Analyst Profiles — AltaLab")
app.add_page(deal_flow_page, route="/roadmap/deal-flow-pipeline", title="Deal Flow Pipeline — AltaLab")
app.add_page(portfolio_tracking_page, route="/roadmap/portfolio-tracking", title="Portfolio Tracking — AltaLab")
app.add_page(automated_reports_page, route="/roadmap/automated-reports", title="Automated Reports — AltaLab")
app.add_page(partner_api_page, route="/roadmap/partner-api", title="Partner API — AltaLab")
app.add_page(cohort_analytics_page, route="/roadmap/cohort-analytics", title="Cohort Analytics — AltaLab")
app.add_page(founder_portal_page, route="/roadmap/founder-portal", title="Founder Portal — AltaLab")
app.add_page(platform_features_page, route="/roadmap/platform", title="Potential Platform Upgrades — AltaLab")
app.add_page(course_integration_page, route="/roadmap/course-integration", title="Course Integration — AltaLab")
