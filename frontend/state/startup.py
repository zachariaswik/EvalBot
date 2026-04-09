"""Startup state — loads all agent outputs for a single startup."""

from __future__ import annotations

import json
from pathlib import Path

import reflex as rx

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output" / "Batch"


def _db_path() -> Path | None:
    candidate = PROJECT_ROOT / "evalbot.db"
    return candidate if candidate.exists() else None


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


class StartupState(rx.State):
    current_batch_id: str = ""
    current_startup_name: str = ""
    verdict_color: str = "gray"
    active_tab: str = "market"

    # Agent outputs stored as dicts
    a1: dict = {}
    a2: dict = {}
    a3: dict = {}
    a4: dict = {}
    a5: dict = {}
    a6: dict = {}

    # Computed for radar chart
    radar_data: list[dict] = []

    # SWOT lists
    swot_strengths: list[str] = []
    swot_weaknesses: list[str] = []
    swot_opportunities: list[str] = []
    swot_threats: list[str] = []

    # Missing roles from a5
    missing_roles: list[str] = []

    # Action plan items
    thirty_day_plan: list[str] = []
    ninety_day_plan: list[str] = []
    pivots: list[str] = []

    is_loading: bool = True
    not_found: bool = False

    @rx.event
    async def load_startup(self):
        self.is_loading = True
        self.not_found = False
        yield

        params = self.router.page.params
        batch_id = params.get("batch_id", "")
        startup_name = params.get("startup_name", "")
        self.current_batch_id = batch_id
        self.current_startup_name = startup_name

        outputs = _get_startup_outputs(batch_id, startup_name)
        if not outputs:
            self.not_found = True
            self.is_loading = False
            return

        a1 = outputs.get(1, {}) or {}
        a2 = outputs.get(2, {}) or {}
        a3 = outputs.get(3, {}) or {}
        a4 = outputs.get(4, {}) or {}
        a5 = outputs.get(5, {}) or {}
        a6 = outputs.get(6, {}) or {}

        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.a5 = a5
        self.a6 = a6

        verdict = a2.get("verdict", "") or ""
        self.verdict_color = _get_verdict_color(verdict)

        # Build radar chart data
        self.radar_data = [
            {"subject": "Problem", "score": a2.get("score_problem_severity", 0) or 0},
            {"subject": "Market", "score": a2.get("score_market_size", 0) or 0},
            {"subject": "Diff.", "score": a2.get("score_differentiation", 0) or 0},
            {"subject": "Customer", "score": a2.get("score_customer_clarity", 0) or 0},
            {"subject": "Founder", "score": a2.get("score_founder_insight", 0) or 0},
            {"subject": "Biz Model", "score": a2.get("score_business_model", 0) or 0},
            {"subject": "Moat", "score": a2.get("score_moat_potential", 0) or 0},
            {"subject": "Venture", "score": a2.get("score_venture_potential", 0) or 0},
            {"subject": "Compete", "score": a2.get("score_competition_difficulty", 0) or 0},
            {"subject": "Execution", "score": a2.get("score_execution_feasibility", 0) or 0},
        ]

        # Extract SWOT
        swot = a2.get("swot", {}) or {}
        self.swot_strengths = swot.get("strengths", []) or []
        self.swot_weaknesses = swot.get("weaknesses", []) or []
        self.swot_opportunities = swot.get("opportunities", []) or []
        self.swot_threats = swot.get("threats", []) or []

        # Extract missing roles
        self.missing_roles = a5.get("missing_roles", []) or []

        # Extract action plans
        thirty = a6.get("thirty_day_plan", []) or []
        ninety = a6.get("ninety_day_plan", []) or []
        self.thirty_day_plan = [thirty] if isinstance(thirty, str) else list(thirty)
        self.ninety_day_plan = [ninety] if isinstance(ninety, str) else list(ninety)
        self.pivots = a6.get("pivots", []) or []

        self.is_loading = False

    @rx.event
    def set_tab(self, tab: str):
        self.active_tab = tab
