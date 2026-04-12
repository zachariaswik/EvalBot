"""EvalBot Reflex app — entry point.

Run locally:
    source .venv313/bin/activate
    reflex run

Production:
    reflex run --env prod --loglevel warning
"""

from pathlib import Path

import reflex as rx
from reflex.utils import console as _rx_console
from starlette.requests import Request
from starlette.responses import JSONResponse

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
from frontend.state.dashboard import DashboardState
from frontend.state.batch import BatchState
from frontend.state.startup import StartupState
from frontend.state.run import RunState

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_STARTUPS_DIR = PROJECT_ROOT / "Startups"
_ALLOWED_EXTS = {".pdf", ".docx", ".txt", ".md"}


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


app._api.add_route("/upload-startup", _upload_startup_handler, methods=["POST"])

app.add_page(
    dashboard_page,
    route="/",
    on_load=DashboardState.load_data,
    title="EvalBot — Dashboard",
)

app.add_page(
    batch_page,
    route="/batch/[batch_id]",
    on_load=BatchState.load_batch,
    title="Batch — EvalBot",
)

app.add_page(
    startup_page,
    route="/batch/[batch_id]/[startup_name]",
    on_load=StartupState.load_startup,
    title="Startup — EvalBot",
)

app.add_page(
    run_page,
    route="/run",
    on_load=RunState.load_staged,
    title="Run Batch — EvalBot",
)

app.add_page(
    roadmap_page,
    route="/roadmap",
    title="Roadmap — EvalBot",
)

app.add_page(analyst_profiles_page, route="/roadmap/analyst-profiles", title="Analyst Profiles — EvalBot")
app.add_page(deal_flow_page, route="/roadmap/deal-flow-pipeline", title="Deal Flow Pipeline — EvalBot")
app.add_page(portfolio_tracking_page, route="/roadmap/portfolio-tracking", title="Portfolio Tracking — EvalBot")
app.add_page(automated_reports_page, route="/roadmap/automated-reports", title="Automated Reports — EvalBot")
app.add_page(partner_api_page, route="/roadmap/partner-api", title="Partner API — EvalBot")
app.add_page(cohort_analytics_page, route="/roadmap/cohort-analytics", title="Cohort Analytics — EvalBot")
app.add_page(founder_portal_page, route="/roadmap/founder-portal", title="Founder Portal — EvalBot")
app.add_page(platform_features_page, route="/roadmap/platform", title="Potential Platform Upgrades — EvalBot")
app.add_page(course_integration_page, route="/roadmap/course-integration", title="Course Integration — EvalBot")
