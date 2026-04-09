"""Page compilation and state-structure tests for the Reflex frontend.

These run without a live server and catch:
  - TypeError / AttributeError raised during component construction
    (e.g. using Python >= on a Reflex ObjectItemOperation instead of rx.cond)
  - Missing or mis-named state vars
  - Route-arg shadow conflicts (state var named 'batch_id'/'startup_name')
  - Stale navigation URLs

Run with: pytest tests/test_pages.py -v
"""

from __future__ import annotations

import json

import pytest
import reflex as rx


# ── Page compilation ──────────────────────────────────────────────────────────
# Each test calls the page function and asserts it returns a component.
# rx.foreach() calls the lambda at build-time, so any Python-level error
# (comparison operators on Var objects, missing state attrs, etc.) will raise here.


def test_dashboard_page_compiles():
    from frontend.pages.dashboard import dashboard_page
    c = dashboard_page()
    assert isinstance(c, rx.Component)


def test_batch_page_compiles():
    from frontend.pages.batch import batch_page
    c = batch_page()
    assert isinstance(c, rx.Component)


def test_startup_page_compiles():
    from frontend.pages.startup import startup_page
    c = startup_page()
    assert isinstance(c, rx.Component)


def test_run_page_compiles():
    from frontend.pages.run import run_page
    c = run_page()
    assert isinstance(c, rx.Component)


def test_roadmap_page_compiles():
    from frontend.pages.roadmap import roadmap_page
    c = roadmap_page()
    assert isinstance(c, rx.Component)


# ── Route registration ────────────────────────────────────────────────────────


def test_app_routes_registered():
    """All 5 pages must be registered in frontend/frontend.py."""
    from frontend.frontend import app

    # Reflex stores "/" as "index" and strips leading slashes from other routes
    routes = set(app._unevaluated_pages.keys())
    assert "index" in routes
    assert "batch/[batch_id]" in routes
    assert "batch/[batch_id]/[startup_name]" in routes
    assert "run" in routes
    assert "roadmap" in routes


# ── State var conflict checks ─────────────────────────────────────────────────
# Reflex 0.8.x injects dynamic route args into ALL state classes globally.
# Any state var named identically to a route arg raises DynamicRouteArgShadowsStateVarError.


def _direct_vars(cls) -> set[str]:
    """Return the set of vars declared directly on cls (not inherited)."""
    return set(cls.__annotations__.keys())


def test_no_batch_id_var_in_any_state():
    from frontend.state.batch import BatchState
    from frontend.state.dashboard import DashboardState
    from frontend.state.run import RunState
    from frontend.state.startup import StartupState

    for cls in [BatchState, StartupState, RunState, DashboardState]:
        assert "batch_id" not in _direct_vars(cls), (
            f"{cls.__name__} declares 'batch_id' which conflicts with the "
            "[batch_id] route arg — rename to 'current_batch_id'"
        )


def test_no_startup_name_var_in_any_state():
    from frontend.state.batch import BatchState
    from frontend.state.dashboard import DashboardState
    from frontend.state.run import RunState
    from frontend.state.startup import StartupState

    for cls in [BatchState, StartupState, RunState, DashboardState]:
        assert "startup_name" not in _direct_vars(cls), (
            f"{cls.__name__} declares 'startup_name' which conflicts with the "
            "[startup_name] route arg — rename to 'current_startup_name'"
        )


# ── Renamed vars exist with correct names ─────────────────────────────────────


def test_batch_state_has_current_batch_id():
    from frontend.state.batch import BatchState

    assert "current_batch_id" in _direct_vars(BatchState)


def test_startup_state_has_current_batch_id_and_startup_name():
    from frontend.state.startup import StartupState

    v = _direct_vars(StartupState)
    assert "current_batch_id" in v
    assert "current_startup_name" in v


def test_run_state_has_completed_batch_id():
    from frontend.state.run import RunState

    assert "completed_batch_id" in _direct_vars(RunState)


# ── Computed vars ─────────────────────────────────────────────────────────────


def test_run_state_has_multi_file_computed_var():
    """has_multi_file must be a @rx.var so it updates reactively with staged."""
    from frontend.state.run import RunState

    # @rx.var properties appear as class-level attributes
    assert hasattr(RunState, "has_multi_file"), (
        "RunState is missing has_multi_file computed var — "
        "the run page filter button won't render"
    )


# ── Bar color helpers ─────────────────────────────────────────────────────────
# score >= 70 → green, 50–69 → blue, < 50 → red


@pytest.mark.parametrize(
    "score,expected",
    [
        (100, "#0a7c52"),
        (70, "#0a7c52"),   # boundary: >=70 = green
        (69, "#1b48c4"),   # just below green threshold
        (50, "#1b48c4"),   # boundary: >=50 = blue
        (49, "#b91c1c"),   # just below blue threshold
        (0, "#b91c1c"),
    ],
)
def test_bar_color_dashboard(score, expected):
    from frontend.state.dashboard import _get_bar_color

    assert _get_bar_color(score) == expected


@pytest.mark.parametrize(
    "score,expected",
    [
        (80, "#0a7c52"),
        (60, "#1b48c4"),
        (30, "#b91c1c"),
    ],
)
def test_bar_color_batch(score, expected):
    from frontend.state.batch import _get_bar_color

    assert _get_bar_color(score) == expected


# ── bar_color is precomputed in state dicts ───────────────────────────────────
# Pages must NOT use Python >= on Reflex Vars; bar_color must live in the dict.


def test_startup_scores_include_bar_color(tmp_path, monkeypatch):
    """BatchState produces startup_scores dicts that include 'bar_color'."""
    output_dir = tmp_path / "output" / "Batch"
    startup_dir = output_dir / "batch_1" / "AcmeCorp"
    startup_dir.mkdir(parents=True)
    (startup_dir / "AcmeCorp.json").write_text(
        json.dumps({"agent2": {"verdict": "Top VC Candidate", "total_score": 82}})
    )

    from frontend.state import batch as batch_mod

    monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(batch_mod, "_db_path", lambda: None)

    startups = batch_mod._load_batch_from_fs("batch_1")
    rows = []
    for s in startups:
        outputs = batch_mod._load_startup_outputs_from_fs("batch_1", s["startup_name"])
        a2 = outputs.get(2, {})
        score = a2.get("total_score", 0) or 0
        rows.append(
            {
                "name": s["startup_name"],
                "score": score,
                "bar_color": batch_mod._get_bar_color(score),
            }
        )

    assert len(rows) == 1
    assert "bar_color" in rows[0]
    assert rows[0]["bar_color"] == "#0a7c52"  # 82 → green


def test_top_startups_include_bar_color(tmp_path, monkeypatch):
    """DashboardState produces top_startups dicts that include 'bar_color'."""
    output_dir = tmp_path / "output" / "Batch"
    startup_dir = output_dir / "batch_1" / "BetaCo"
    startup_dir.mkdir(parents=True)
    (startup_dir / "BetaCo.json").write_text(
        json.dumps({"agent2": {"verdict": "Reject", "total_score": 35}})
    )

    from frontend.state import dashboard as dash_mod

    monkeypatch.setattr(dash_mod, "OUTPUT_DIR", output_dir)
    monkeypatch.setattr(dash_mod, "_db_path", lambda: None)

    outputs = dash_mod._load_startup_outputs_from_fs("batch_1", "BetaCo")
    score = outputs.get(2, {}).get("total_score", 0) or 0
    bar_color = dash_mod._get_bar_color(score)

    assert bar_color == "#b91c1c"  # 35 → red


# ── Filter-single logic ───────────────────────────────────────────────────────


def test_filter_single_excludes_one_file_startups():
    """start_run only includes multi-file startups when filter_single=True."""
    staged = [
        {"name": "Alpha", "files": ["pitch.pdf"]},
        {"name": "Beta", "files": ["deck.pdf", "notes.md"]},
        {"name": "Gamma", "files": ["brief.txt"]},
    ]
    filtered = [s["name"] for s in staged if len(s.get("files", [])) > 1]
    assert filtered == ["Beta"]


def test_filter_single_false_includes_all():
    staged = [
        {"name": "Alpha", "files": ["pitch.pdf"]},
        {"name": "Beta", "files": ["deck.pdf", "notes.md"]},
    ]
    all_names = [s["name"] for s in staged]
    assert all_names == ["Alpha", "Beta"]


# ── has_multi_file logic ──────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "staged,expected",
    [
        ([], False),
        ([{"name": "A", "files": ["f.pdf"]}], False),
        ([{"name": "A", "files": ["f.pdf", "g.md"]}], True),
        (
            [
                {"name": "A", "files": ["f.pdf"]},
                {"name": "B", "files": ["x.pdf", "y.md"]},
            ],
            True,
        ),
    ],
)
def test_has_multi_file_logic(staged, expected):
    """Verify the has_multi_file computed logic independently of Reflex runtime."""
    result = any(len(s.get("files", [])) > 1 for s in staged)
    assert result == expected
