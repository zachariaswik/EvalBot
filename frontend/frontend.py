"""EvalBot Reflex app — entry point.

Run locally:
    source .venv313/bin/activate
    reflex run

Production:
    reflex run --env prod --loglevel warning
"""

import reflex as rx

from frontend.pages.dashboard import dashboard_page
from frontend.pages.batch import batch_page
from frontend.pages.startup import startup_page
from frontend.pages.run import run_page
from frontend.pages.roadmap import roadmap_page
from frontend.state.dashboard import DashboardState
from frontend.state.batch import BatchState
from frontend.state.startup import StartupState
from frontend.state.run import RunState

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
