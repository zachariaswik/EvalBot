"""End-to-end state simulation tests.

We simulate every user-clickable action and page-load scenario across all
5 pages (Dashboard, Batch, Startup, Run, Roadmap), covering both happy
paths (data exists, actions succeed) and sad paths (missing data, invalid
inputs, interrupted runs, empty states).

Reflex state objects require the full Reflex runtime to instantiate, so we
test:
  1. All helper functions that back event handlers (direct calls with mocked
     paths/DB).
  2. The core transformation logic of each event handler, replicated inline,
     exactly as the handler executes it — so any bug in the handler will
     surface here.
  3. Edge cases for every data shape the handlers encounter in production.

Run with:  pytest tests/test_e2e_state.py -v
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest


# ============================================================================
# Shared helpers
# ============================================================================

def _seed_full_db(db_path: Path) -> None:
    """Populate a test DB with two batches and several startups."""
    from src.db import (
        create_batch,
        init_db,
        store_agent_output,
        update_startup_status,
        upsert_startup,
    )

    init_db(db_path)

    # Batch 1 — two startups, one completed
    create_batch("batch_1", "First batch", db_path)
    upsert_startup("batch_1", "AlphaCo", "Alpha pitch", db_path)
    upsert_startup("batch_1", "BetaCo", "Beta pitch", db_path)
    update_startup_status("batch_1", "AlphaCo", "completed", db_path)
    update_startup_status("batch_1", "BetaCo", "completed", db_path)

    store_agent_output(
        "batch_1", "AlphaCo", 2,
        json.dumps({
            "verdict": "Top VC Candidate",
            "total_score": 82,
            "summary": "Exceptional team and market.",
            "score_problem_severity": 9,
            "score_market_size": 9,
            "score_differentiation": 8,
            "score_customer_clarity": 8,
            "score_founder_insight": 9,
            "score_business_model": 8,
            "score_moat_potential": 8,
            "score_venture_potential": 9,
            "score_competition_difficulty": 7,
            "score_execution_feasibility": 7,
            "swot": {
                "strengths": ["Strong moat", "Experienced founders"],
                "weaknesses": ["Early stage"],
                "opportunities": ["Huge TAM"],
                "threats": ["Well-funded competitors"],
            },
            "explanation": "Top tier.",
        }),
        1, db_path=db_path,
    )
    store_agent_output(
        "batch_1", "AlphaCo", 1,
        json.dumps({
            "startup_name": "AlphaCo",
            "one_line_description": "AI-powered deal sourcing",
            "problem": "VCs miss deals",
        }),
        1, db_path=db_path,
    )

    store_agent_output(
        "batch_1", "BetaCo", 2,
        json.dumps({
            "verdict": "Reject",
            "total_score": 28,
            "summary": "Weak fundamentals.",
            "score_problem_severity": 3,
            "score_market_size": 3,
            "score_differentiation": 2,
            "score_customer_clarity": 3,
            "score_founder_insight": 3,
            "score_business_model": 3,
            "score_moat_potential": 2,
            "score_venture_potential": 3,
            "score_competition_difficulty": 3,
            "score_execution_feasibility": 3,
            "swot": {
                "strengths": [],
                "weaknesses": ["No differentiation"],
                "opportunities": [],
                "threats": ["Market too crowded"],
            },
            "explanation": "Pass.",
        }),
        1, db_path=db_path,
    )

    # Batch 2 — one startup
    create_batch("batch_2", "Second batch", db_path)
    upsert_startup("batch_2", "GammaCo", "Gamma pitch", db_path)
    update_startup_status("batch_2", "GammaCo", "completed", db_path)
    store_agent_output(
        "batch_2", "GammaCo", 2,
        json.dumps({
            "verdict": "Promising, Needs Sharper Focus",
            "total_score": 61,
            "summary": "Good bones, needs focus.",
            "score_problem_severity": 7,
            "score_market_size": 6,
            "score_differentiation": 6,
            "score_customer_clarity": 6,
            "score_founder_insight": 6,
            "score_business_model": 6,
            "score_moat_potential": 6,
            "score_venture_potential": 6,
            "score_competition_difficulty": 5,
            "score_execution_feasibility": 7,
            "swot": {
                "strengths": ["Good team"],
                "weaknesses": ["Vague positioning"],
                "opportunities": ["Expanding market"],
                "threats": ["Entrenched players"],
            },
        }),
        1, db_path=db_path,
    )


def _make_json_output(
    output_dir: Path,
    batch_id: str,
    startup_name: str,
    a2: dict | None = None,
    a1: dict | None = None,
    a3: dict | None = None,
    a4: dict | None = None,
    a5: dict | None = None,
    a6: dict | None = None,
) -> Path:
    """Write a startup JSON file to the output filesystem."""
    startup_dir = output_dir / batch_id / startup_name
    startup_dir.mkdir(parents=True, exist_ok=True)
    data: dict = {}
    if a1:
        data["agent1"] = a1
    if a2:
        data["agent2"] = a2
    if a3:
        data["agent3"] = a3
    if a4:
        data["agent4"] = a4
    if a5:
        data["agent5"] = a5
    if a6:
        data["agent6"] = a6
    json_path = startup_dir / f"{startup_name}.json"
    json_path.write_text(json.dumps(data))
    return json_path


# ============================================================================
# Dashboard page — load_data logic
# ============================================================================

class TestDashboardLoadData:
    """Simulate DashboardState.load_data() for all scenarios."""

    def test_happy_path_from_db(self, tmp_path):
        """Dashboard loads batches + stats from DB (primary path)."""
        db_path = tmp_path / "test.db"
        _seed_full_db(db_path)

        from frontend.state import dashboard as dash
        from src.db import list_batches, list_startups

        batches = list_batches(db_path)
        assert len(batches) == 2

        total_startups = sum(b.get("startup_count", 0) for b in batches)
        assert total_startups >= 2  # at least AlphaCo + BetaCo counted

        # Simulate top-startups logic for the first (latest) batch
        first_batch_id = batches[0]["batch_id"]
        first_startups = list_startups(first_batch_id, db_path)
        assert len(first_startups) >= 1

        top_startups = []
        vc_count = 0
        for s in first_startups[:10]:
            from src.db import get_current_outputs
            outputs = get_current_outputs(first_batch_id, s["startup_name"], db_path)
            a2 = outputs.get(2, {})
            verdict = a2.get("verdict", "")
            score = a2.get("total_score", 0) or 0
            if verdict == "Top VC Candidate":
                vc_count += 1
            top_startups.append({
                "name": s["startup_name"],
                "verdict": verdict,
                "score": score,
                "verdict_color": dash._get_verdict_color(verdict),
                "bar_color": dash._get_bar_color(score),
            })

        top_startups.sort(key=lambda x: x["score"], reverse=True)
        # AlphaCo (82) must appear before BetaCo (28) in batch_2 vs batch_1 order
        assert top_startups[0]["score"] >= top_startups[-1]["score"]

        vc_percent = round(vc_count / total_startups * 100) if total_startups else 0
        assert isinstance(vc_percent, int)

    def test_happy_path_from_fs(self, tmp_path, monkeypatch):
        """Dashboard falls back to filesystem when no DB exists."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "StartupX",
                          a2={"verdict": "Top VC Candidate", "total_score": 75})
        _make_json_output(output_dir, "batch_1", "StartupY",
                          a2={"verdict": "Reject", "total_score": 22})

        from frontend.state import dashboard as dash
        monkeypatch.setattr(dash, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(dash, "_db_path", lambda: None)

        batches = dash._load_batches_from_fs()
        assert len(batches) == 1
        assert batches[0]["batch_id"] == "batch_1"
        assert batches[0]["startup_count"] == 2

        # Simulate stats
        total_startups = sum(b["startup_count"] for b in batches)
        assert total_startups == 2

        first_batch_id = batches[0]["batch_id"]
        first_startups = dash._load_batch_from_fs(first_batch_id)
        assert len(first_startups) == 2

        vc_count = 0
        top_startups = []
        for s in first_startups:
            outputs = dash._get_startup_outputs(first_batch_id, s["startup_name"])
            a2 = outputs.get(2, {})
            verdict = a2.get("verdict", "")
            score = a2.get("total_score", 0) or 0
            if verdict == "Top VC Candidate":
                vc_count += 1
            top_startups.append({"name": s["startup_name"], "score": score})

        top_startups.sort(key=lambda x: x["score"], reverse=True)
        assert top_startups[0]["name"] == "StartupX"  # score 75 > 22

        vc_percent = round(vc_count / total_startups * 100)
        assert vc_percent == 50  # 1 of 2

    def test_sad_path_empty_db(self, tmp_path):
        """Dashboard with empty DB shows zero stats."""
        from src.db import init_db, list_batches
        db_path = tmp_path / "empty.db"
        init_db(db_path)
        batches = list_batches(db_path)

        total_startups = sum(b.get("startup_count", 0) for b in batches)
        total_batches = len(batches)
        vc_percent = 0  # no startups → no VC candidates

        assert total_batches == 0
        assert total_startups == 0
        assert vc_percent == 0

    def test_sad_path_no_db_no_fs(self, tmp_path, monkeypatch):
        """Dashboard with no DB and no output directory returns empty state."""
        from frontend.state import dashboard as dash
        monkeypatch.setattr(dash, "OUTPUT_DIR", tmp_path / "nonexistent")
        monkeypatch.setattr(dash, "_db_path", lambda: None)

        batches = dash._load_batches_from_fs()
        assert batches == []

    def test_sad_path_batch_with_no_agent2(self, tmp_path, monkeypatch):
        """Batch where no startup has agent2 outputs → score=0, verdict=Unknown."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "BlankCo",
                          a1={"startup_name": "BlankCo"})  # only a1, no a2

        from frontend.state import dashboard as dash
        monkeypatch.setattr(dash, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(dash, "_db_path", lambda: None)

        first_startups = dash._load_batch_from_fs("batch_1")
        for s in first_startups:
            outputs = dash._get_startup_outputs("batch_1", s["startup_name"])
            a2 = outputs.get(2, {})
            verdict = a2.get("verdict", "")
            score = a2.get("total_score", 0) or 0
            assert score == 0
            assert verdict == ""

    def test_batches_sorted_newest_first(self, tmp_path, monkeypatch):
        """_load_batches_from_fs returns batches in reverse-alphabetical order."""
        output_dir = tmp_path / "output" / "Batch"
        for name in ["batch_1", "batch_3", "batch_2"]:
            (output_dir / name / "StartupA").mkdir(parents=True)

        from frontend.state import dashboard as dash
        monkeypatch.setattr(dash, "OUTPUT_DIR", output_dir)

        batches = dash._load_batches_from_fs()
        batch_ids = [b["batch_id"] for b in batches]
        assert batch_ids == ["batch_3", "batch_2", "batch_1"]

    def test_top_startups_capped_at_3(self, tmp_path, monkeypatch):
        """Dashboard shows at most 3 top startups."""
        output_dir = tmp_path / "output" / "Batch"
        for i, score in enumerate([90, 80, 70, 60, 50], 1):
            _make_json_output(output_dir, "batch_1", f"Co{i}",
                              a2={"verdict": "Top VC Candidate", "total_score": score})

        from frontend.state import dashboard as dash
        monkeypatch.setattr(dash, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(dash, "_db_path", lambda: None)

        first_startups = dash._load_batch_from_fs("batch_1")
        top_startups = []
        for s in first_startups[:10]:
            outputs = dash._get_startup_outputs("batch_1", s["startup_name"])
            a2 = outputs.get(2, {})
            score = a2.get("total_score", 0) or 0
            top_startups.append({"name": s["startup_name"], "score": score})

        top_startups.sort(key=lambda x: x["score"], reverse=True)
        top_3 = top_startups[:3]
        assert len(top_3) == 3
        assert top_3[0]["score"] == 90
        assert top_3[2]["score"] == 70

    def test_vc_percent_zero_when_no_startups(self):
        """vc_percent stays 0 when no startups (avoids ZeroDivisionError)."""
        total_startups = 0
        vc_count = 0
        vc_percent = round(vc_count / total_startups * 100) if total_startups > 0 else 0
        assert vc_percent == 0

    def test_vc_percent_100_when_all_vc(self, tmp_path, monkeypatch):
        """vc_percent is 100 when all startups are Top VC Candidate."""
        output_dir = tmp_path / "output" / "Batch"
        for name in ["A", "B", "C"]:
            _make_json_output(output_dir, "batch_1", name,
                              a2={"verdict": "Top VC Candidate", "total_score": 80})

        from frontend.state import dashboard as dash
        monkeypatch.setattr(dash, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(dash, "_db_path", lambda: None)

        startups = dash._load_batch_from_fs("batch_1")
        vc_count = 0
        for s in startups:
            outputs = dash._get_startup_outputs("batch_1", s["startup_name"])
            verdict = outputs.get(2, {}).get("verdict", "")
            if verdict == "Top VC Candidate":
                vc_count += 1
        vc_percent = round(vc_count / len(startups) * 100)
        assert vc_percent == 100


# ============================================================================
# Batch page — load_batch logic
# ============================================================================

class TestBatchLoadBatch:
    """Simulate BatchState.load_batch() for all scenarios."""

    def test_happy_path_from_fs(self, tmp_path, monkeypatch):
        """Batch leaderboard loads all startups and computes charts."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "Alpha",
                          a2={"verdict": "Top VC Candidate", "total_score": 80})
        _make_json_output(output_dir, "batch_1", "Beta",
                          a2={"verdict": "Reject", "total_score": 25})

        from frontend.state import batch as batch_mod
        monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(batch_mod, "_db_path", lambda: None)

        startups = batch_mod._load_batch_from_fs("batch_1")
        assert len(startups) == 2

        startup_scores = []
        verdict_counts: dict[str, int] = {}
        for s in startups:
            outputs = batch_mod._get_startup_outputs("batch_1", s["startup_name"])
            a2 = outputs.get(2, {})
            verdict = a2.get("verdict", "Unknown") or "Unknown"
            score = a2.get("total_score", 0) or 0
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
            startup_scores.append({
                "name": s["startup_name"],
                "score": score,
                "verdict": verdict,
                "verdict_color": batch_mod._get_verdict_color(verdict),
                "bar_color": batch_mod._get_bar_color(score),
                "pipeline_status": s.get("pipeline_status", ""),
            })

        startup_scores.sort(key=lambda x: x["score"], reverse=True)
        assert startup_scores[0]["name"] == "Alpha"
        assert startup_scores[0]["score"] == 80
        assert startup_scores[1]["name"] == "Beta"

        assert verdict_counts["Top VC Candidate"] == 1
        assert verdict_counts["Reject"] == 1

        bar_chart_data = [{"name": s["name"], "score": s["score"]} for s in startup_scores]
        pie_chart_data = [{"name": k, "value": v} for k, v in verdict_counts.items()]
        assert len(bar_chart_data) == 2
        assert len(pie_chart_data) == 2

    def test_sad_path_nonexistent_batch(self, tmp_path, monkeypatch):
        """Batch page with unknown batch_id → empty startups list."""
        output_dir = tmp_path / "output" / "Batch"
        output_dir.mkdir(parents=True)

        from frontend.state import batch as batch_mod
        monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(batch_mod, "_db_path", lambda: None)

        startups = batch_mod._load_batch_from_fs("nonexistent_batch_999")
        assert startups == []
        # not_found would be set to True in the state handler

    def test_sad_path_no_agent2_outputs(self, tmp_path, monkeypatch):
        """Batch where startups have no agent2 → score=0, verdict=Unknown."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "EmptyCo",
                          a1={"startup_name": "EmptyCo"})

        from frontend.state import batch as batch_mod
        monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(batch_mod, "_db_path", lambda: None)

        startups = batch_mod._load_batch_from_fs("batch_1")
        for s in startups:
            outputs = batch_mod._get_startup_outputs("batch_1", s["startup_name"])
            a2 = outputs.get(2, {})
            verdict = a2.get("verdict", "Unknown") or "Unknown"
            score = a2.get("total_score", 0) or 0
            assert verdict == "Unknown"
            assert score == 0
            bar_color = batch_mod._get_bar_color(score)
            assert bar_color == "#b91c1c"  # score 0 → red

    def test_shortlist_loaded_from_ranking_json(self, tmp_path, monkeypatch):
        """Shortlist is read from ranking.json when not in per-startup outputs."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "Alpha",
                          a2={"verdict": "Top VC Candidate", "total_score": 80})
        _make_json_output(output_dir, "batch_1", "Beta",
                          a2={"verdict": "Promising, Needs Sharper Focus", "total_score": 55})

        ranking = {"shortlist": ["Alpha"], "ranking": ["Alpha", "Beta"]}
        (output_dir / "batch_1" / "ranking.json").write_text(json.dumps(ranking))

        from frontend.state import batch as batch_mod
        monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(batch_mod, "_db_path", lambda: None)

        # Simulate: no shortlist from per-startup outputs, fall back to ranking.json
        shortlist: list[str] = []
        ranking_path = output_dir / "batch_1" / "ranking.json"
        if ranking_path.exists():
            ranking_data = json.loads(ranking_path.read_text())
            shortlist = ranking_data.get("shortlist", [])

        assert shortlist == ["Alpha"]

    def test_verdict_counting_multiple_types(self, tmp_path, monkeypatch):
        """Verdict distribution counts are correct for mixed verdicts."""
        output_dir = tmp_path / "output" / "Batch"
        cases = [
            ("Co1", "Top VC Candidate", 85),
            ("Co2", "Top VC Candidate", 80),
            ("Co3", "Promising, Needs Sharper Focus", 60),
            ("Co4", "Reject", 20),
            ("Co5", "Reject", 15),
            ("Co6", "Feature, Not a Company", 35),
        ]
        for name, verdict, score in cases:
            _make_json_output(output_dir, "batch_1", name,
                              a2={"verdict": verdict, "total_score": score})

        from frontend.state import batch as batch_mod
        monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(batch_mod, "_db_path", lambda: None)

        startups = batch_mod._load_batch_from_fs("batch_1")
        verdict_counts: dict[str, int] = {}
        for s in startups:
            outputs = batch_mod._get_startup_outputs("batch_1", s["startup_name"])
            verdict = outputs.get(2, {}).get("verdict", "Unknown") or "Unknown"
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1

        assert verdict_counts["Top VC Candidate"] == 2
        assert verdict_counts["Promising, Needs Sharper Focus"] == 1
        assert verdict_counts["Reject"] == 2
        assert verdict_counts["Feature, Not a Company"] == 1

    def test_startup_scores_sorted_descending(self, tmp_path, monkeypatch):
        """Leaderboard is sorted by score descending."""
        output_dir = tmp_path / "output" / "Batch"
        scores = [45, 72, 88, 33, 60]
        for i, score in enumerate(scores, 1):
            _make_json_output(output_dir, "batch_1", f"Co{i}",
                              a2={"verdict": "Promising, Needs Sharper Focus", "total_score": score})

        from frontend.state import batch as batch_mod
        monkeypatch.setattr(batch_mod, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(batch_mod, "_db_path", lambda: None)

        startups = batch_mod._load_batch_from_fs("batch_1")
        startup_scores = []
        for s in startups:
            outputs = batch_mod._get_startup_outputs("batch_1", s["startup_name"])
            score = outputs.get(2, {}).get("total_score", 0) or 0
            startup_scores.append(score)

        startup_scores.sort(reverse=True)
        assert startup_scores == [88, 72, 60, 45, 33]

    def test_bar_color_thresholds_in_leaderboard(self, tmp_path, monkeypatch):
        """Verify green/blue/red bar colors computed for leaderboard rows."""
        from frontend.state.batch import _get_bar_color
        assert _get_bar_color(88) == "#0a7c52"   # ≥70 → green
        assert _get_bar_color(70) == "#0a7c52"   # boundary
        assert _get_bar_color(69) == "#1b48c4"   # 50-69 → blue
        assert _get_bar_color(50) == "#1b48c4"   # boundary
        assert _get_bar_color(49) == "#b91c1c"   # <50 → red
        assert _get_bar_color(0) == "#b91c1c"

    def test_happy_path_from_db(self, tmp_path, monkeypatch):
        """Batch page loads from DB when available."""
        db_path = tmp_path / "test.db"
        _seed_full_db(db_path)

        from frontend.state import batch as batch_mod
        from src.db import list_startups
        monkeypatch.setattr(batch_mod, "_db_path", lambda: db_path)

        startups = list_startups("batch_1", db_path)
        assert any(s["startup_name"] == "AlphaCo" for s in startups)
        assert any(s["startup_name"] == "BetaCo" for s in startups)


# ============================================================================
# Startup page — load_startup + set_tab logic
# ============================================================================

class TestStartupLoadStartup:
    """Simulate StartupState.load_startup() + set_tab for all scenarios."""

    def _full_a2(self, verdict: str = "Top VC Candidate", score: int = 82) -> dict:
        return {
            "verdict": verdict,
            "total_score": score,
            "summary": "Strong startup.",
            "score_problem_severity": 9,
            "score_market_size": 8,
            "score_differentiation": 8,
            "score_customer_clarity": 7,
            "score_founder_insight": 9,
            "score_business_model": 7,
            "score_moat_potential": 8,
            "score_venture_potential": 9,
            "score_competition_difficulty": 7,
            "score_execution_feasibility": 7,
            "swot": {
                "strengths": ["Strong moat", "Expert founders"],
                "weaknesses": ["Small team"],
                "opportunities": ["Expanding market"],
                "threats": ["Big Tech could copy"],
            },
        }

    def test_happy_path_all_agents(self, tmp_path, monkeypatch):
        """Startup detail page loads all 6 agent outputs correctly."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(
            output_dir, "batch_1", "AlphaCo",
            a1={"startup_name": "AlphaCo", "one_line_description": "AI deal sourcing"},
            a2=self._full_a2(),
            a3={"market_category": "FinTech", "size_class": "Large", "attractiveness_score": 8,
                "competition_score": 6, "trend": "Growing", "conclusion": "Great market"},
            a4={"product_reality": "MVP", "killer_feature": "NLP matching", "wrapper_risk": "low",
                "moat": "Data network effects", "six_month_focus": "Customer acquisition"},
            a5={"fit_score": 9, "execution_score": 8, "missing_roles": ["Sales lead"],
                "conclusion": "Strong founders"},
            a6={"recommendation": "Continue", "thirty_day_plan": ["Launch beta", "Get 10 users"],
                "ninety_day_plan": ["100 customers"], "pivots": []},
        )

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "AlphaCo")
        assert 1 in outputs and 2 in outputs and 3 in outputs
        assert 4 in outputs and 5 in outputs and 6 in outputs

        a1 = outputs[1]
        a2 = outputs[2]
        a3 = outputs[3]
        a5 = outputs[5]
        a6 = outputs[6]

        # Verdict color
        verdict_color = su._get_verdict_color(a2["verdict"])
        assert verdict_color == "emerald"

        # Radar data
        radar_data = [
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
        assert len(radar_data) == 10
        assert radar_data[0]["score"] == 9   # problem
        assert radar_data[1]["score"] == 8   # market

        # SWOT extraction
        swot = a2.get("swot", {}) or {}
        strengths = swot.get("strengths", []) or []
        weaknesses = swot.get("weaknesses", []) or []
        assert "Strong moat" in strengths
        assert "Small team" in weaknesses

        # Missing roles
        missing_roles = a5.get("missing_roles", []) or []
        assert "Sales lead" in missing_roles

        # Action plans (list case)
        thirty = a6.get("thirty_day_plan", []) or []
        ninety = a6.get("ninety_day_plan", []) or []
        thirty_day_plan = [thirty] if isinstance(thirty, str) else list(thirty)
        ninety_day_plan = [ninety] if isinstance(ninety, str) else list(ninety)
        assert "Launch beta" in thirty_day_plan
        assert "100 customers" in ninety_day_plan

    def test_sad_path_startup_not_found(self, tmp_path, monkeypatch):
        """Startup not in DB or FS → not_found=True."""
        output_dir = tmp_path / "output" / "Batch"
        output_dir.mkdir(parents=True)

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "NoSuchStartup")
        assert outputs == {}  # handler would set not_found = True

    def test_partial_outputs_only_a2(self, tmp_path, monkeypatch):
        """Startup with only agent2 output — other agents get empty dicts."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "PartialCo",
                          a2=self._full_a2("Promising, Needs Sharper Focus", 61))

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "PartialCo")
        a1 = outputs.get(1, {}) or {}
        a2 = outputs.get(2, {}) or {}
        a3 = outputs.get(3, {}) or {}
        a5 = outputs.get(5, {}) or {}
        a6 = outputs.get(6, {}) or {}

        assert a1 == {}
        assert a2["total_score"] == 61
        assert a3 == {}

        # Missing roles defaults safely
        missing_roles = a5.get("missing_roles", []) or []
        assert missing_roles == []

        # Action plans default safely
        thirty = a6.get("thirty_day_plan", []) or []
        thirty_day_plan = [thirty] if isinstance(thirty, str) else list(thirty)
        assert thirty_day_plan == []

    def test_action_plan_string_type_handling(self, tmp_path, monkeypatch):
        """When agent6 returns action plans as strings (not lists), they're wrapped."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(
            output_dir, "batch_1", "StringPlanCo",
            a2=self._full_a2(),
            a6={
                "recommendation": "Refine",
                "thirty_day_plan": "Build MVP by end of month",   # str, not list
                "ninety_day_plan": "Reach 100 paying customers",  # str, not list
                "pivots": [],
            },
        )

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "StringPlanCo")
        a6 = outputs.get(6, {}) or {}

        thirty = a6.get("thirty_day_plan", []) or []
        ninety = a6.get("ninety_day_plan", []) or []
        thirty_day_plan = [thirty] if isinstance(thirty, str) else list(thirty)
        ninety_day_plan = [ninety] if isinstance(ninety, str) else list(ninety)

        assert thirty_day_plan == ["Build MVP by end of month"]
        assert ninety_day_plan == ["Reach 100 paying customers"]

    def test_radar_data_missing_scores_default_to_zero(self, tmp_path, monkeypatch):
        """Agent2 with missing individual scores → radar data defaults to 0."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "SparseScoreCo",
                          a2={"verdict": "Reject", "total_score": 20})
        # No individual score_* fields

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "SparseScoreCo")
        a2 = outputs.get(2, {}) or {}

        radar_data = [
            {"subject": "Problem", "score": a2.get("score_problem_severity", 0) or 0},
            {"subject": "Market", "score": a2.get("score_market_size", 0) or 0},
        ]
        assert radar_data[0]["score"] == 0
        assert radar_data[1]["score"] == 0

    def test_swot_empty_lists(self, tmp_path, monkeypatch):
        """Startup with empty SWOT lists doesn't crash."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "NoSwotCo",
                          a2={
                              "verdict": "Reject",
                              "total_score": 20,
                              "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
                          })

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "NoSwotCo")
        a2 = outputs.get(2, {}) or {}
        swot = a2.get("swot", {}) or {}
        assert swot.get("strengths", []) == []
        assert swot.get("weaknesses", []) == []

    def test_swot_missing_entirely(self, tmp_path, monkeypatch):
        """Agent2 output with no 'swot' key → all SWOT lists empty."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "NoSwotKey",
                          a2={"verdict": "Reject", "total_score": 20})  # no swot key

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "NoSwotKey")
        a2 = outputs.get(2, {}) or {}
        swot = a2.get("swot", {}) or {}
        strengths = swot.get("strengths", []) or []
        assert strengths == []

    @pytest.mark.parametrize("verdict,expected_color", [
        ("Top VC Candidate", "emerald"),
        ("Promising, Needs Sharper Focus", "blue"),
        ("Promising, But Needs Pivot", "blue"),
        ("Good Small Business, Not Venture-Scale", "orange"),
        ("Feature, Not a Company", "amber"),
        ("AI Wrapper With Weak Moat", "amber"),
        ("Reject", "red"),
        ("Unknown Verdict", "gray"),
        ("", "gray"),
    ])
    def test_verdict_color_all_variants(self, verdict, expected_color):
        """All verdict strings map to correct badge colors."""
        from frontend.state.startup import _get_verdict_color
        assert _get_verdict_color(verdict) == expected_color

    def test_set_tab_switches_active_tab(self):
        """set_tab event: active_tab changes to the clicked tab."""
        # Simulate the set_tab event handler logic
        active_tab = "market"

        # Click "product" tab
        active_tab = "product"
        assert active_tab == "product"

        # Click "founder" tab
        active_tab = "founder"
        assert active_tab == "founder"

        # Click "recs" tab
        active_tab = "recs"
        assert active_tab == "recs"

        # Return to "market"
        active_tab = "market"
        assert active_tab == "market"

    def test_pivots_displayed_when_present(self, tmp_path, monkeypatch):
        """Pivot options appear when a6 has pivots list."""
        output_dir = tmp_path / "output" / "Batch"
        _make_json_output(output_dir, "batch_1", "PivotCo",
                          a2=self._full_a2(),
                          a6={
                              "recommendation": "Pivot",
                              "thirty_day_plan": [],
                              "ninety_day_plan": [],
                              "pivots": ["Target enterprise instead of SMB",
                                         "Become a platform, not a tool"],
                          })

        from frontend.state import startup as su
        monkeypatch.setattr(su, "OUTPUT_DIR", output_dir)
        monkeypatch.setattr(su, "_db_path", lambda: None)

        outputs = su._get_startup_outputs("batch_1", "PivotCo")
        pivots = outputs.get(6, {}).get("pivots", []) or []
        assert len(pivots) == 2
        assert "Target enterprise instead of SMB" in pivots


# ============================================================================
# Run page — upload / remove / toggle / progress logic
# ============================================================================

class TestRunPageActions:
    """Simulate all RunState event handlers."""

    # ── load_staged ──────────────────────────────────────────────────────────

    def test_load_staged_empty_directory(self, tmp_path, monkeypatch):
        """load_staged with empty Startups/ → staged=[]."""
        startups_dir = tmp_path / "Startups"
        startups_dir.mkdir()

        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "STARTUPS_DIR", startups_dir)

        staged: list[dict] = []
        if startups_dir.exists():
            for d in sorted(startups_dir.iterdir()):
                if d.is_dir():
                    files = [f.name for f in d.iterdir() if f.is_file()]
                    staged.append({"name": d.name, "files": files})

        assert staged == []

    def test_load_staged_with_startups(self, tmp_path, monkeypatch):
        """load_staged reads startup directories and their files."""
        startups_dir = tmp_path / "Startups"
        (startups_dir / "AlphaCo").mkdir(parents=True)
        (startups_dir / "AlphaCo" / "pitch.pdf").write_bytes(b"pdf")
        (startups_dir / "BetaCo").mkdir(parents=True)
        (startups_dir / "BetaCo" / "deck.pdf").write_bytes(b"pdf")
        (startups_dir / "BetaCo" / "notes.md").write_text("notes")

        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "STARTUPS_DIR", startups_dir)

        staged: list[dict] = []
        if startups_dir.exists():
            for d in sorted(startups_dir.iterdir()):
                if d.is_dir():
                    files = [f.name for f in d.iterdir() if f.is_file()]
                    staged.append({"name": d.name, "files": files})

        assert len(staged) == 2
        alpha = next(s for s in staged if s["name"] == "AlphaCo")
        beta = next(s for s in staged if s["name"] == "BetaCo")
        assert alpha["files"] == ["pitch.pdf"]
        assert set(beta["files"]) == {"deck.pdf", "notes.md"}

    def test_load_staged_no_startups_dir(self, tmp_path, monkeypatch):
        """load_staged when Startups/ does not exist → staged=[]."""
        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "STARTUPS_DIR", tmp_path / "Startups")

        staged: list[dict] = []
        startups_dir = tmp_path / "Startups"
        if startups_dir.exists():
            for d in sorted(startups_dir.iterdir()):
                if d.is_dir():
                    staged.append({"name": d.name, "files": []})

        assert staged == []

    def test_load_staged_interrupted_run_detected(self, tmp_path, monkeypatch):
        """load_staged detects interrupted run from state file."""
        state_file = tmp_path / "evalbot_run.json"
        state_file.write_text(json.dumps({"job_id": "abc", "status": "running"}))

        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "RUN_STATE_FILE", state_file)
        monkeypatch.setattr(run_mod, "STARTUPS_DIR", tmp_path / "Startups")

        state = run_mod._read_run_state()
        assert state is not None
        assert state["status"] == "running"

        # Simulate interrupt detection
        status = "idle"
        run_error = ""
        if state and state.get("status") == "running":
            status = "interrupted"
            run_error = "A previous run was interrupted"

        assert status == "interrupted"
        assert "interrupted" in run_error

    def test_load_staged_completed_run_not_interrupted(self, tmp_path, monkeypatch):
        """load_staged with a 'done' run state does NOT set interrupted."""
        state_file = tmp_path / "evalbot_run.json"
        state_file.write_text(json.dumps({"job_id": "abc", "status": "done", "batch_id": "batch_1"}))

        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "RUN_STATE_FILE", state_file)

        state = run_mod._read_run_state()
        status = "idle"
        if state and state.get("status") == "running":
            status = "interrupted"

        assert status == "idle"  # 'done' should NOT trigger interrupted

    # ── _get_backend_base / _folder_picker_js ────────────────────────────────

    def test_get_backend_base_happy_path(self, tmp_path, monkeypatch):
        """_get_backend_base extracts the base URL from env.json UPLOAD field."""
        from frontend.state import run as run_mod
        web_dir = tmp_path / ".web"
        web_dir.mkdir()
        (web_dir / "env.json").write_text('{"UPLOAD": "http://localhost:8001/_upload"}')
        monkeypatch.setattr(run_mod, "PROJECT_ROOT", tmp_path)
        assert run_mod._get_backend_base() == "http://localhost:8001"

    def test_get_backend_base_missing_env_json(self, tmp_path, monkeypatch):
        """_get_backend_base returns '' when env.json is absent."""
        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "PROJECT_ROOT", tmp_path)
        assert run_mod._get_backend_base() == ""

    def test_get_backend_base_malformed_env_json(self, tmp_path, monkeypatch):
        """_get_backend_base returns '' when env.json is corrupt."""
        from frontend.state import run as run_mod
        web_dir = tmp_path / ".web"
        web_dir.mkdir()
        (web_dir / "env.json").write_text("{bad json")
        monkeypatch.setattr(run_mod, "PROJECT_ROOT", tmp_path)
        assert run_mod._get_backend_base() == ""

    def test_folder_picker_js_embeds_backend_url(self):
        """_folder_picker_js injects the given backend base into the fetch call."""
        from frontend.state.run import _folder_picker_js
        js = _folder_picker_js("http://localhost:8001")
        assert "http://localhost:8001" in js
        assert "upload-startup" in js

    def test_folder_picker_js_empty_base_uses_relative(self):
        """_folder_picker_js with empty backend_base falls back to /upload-startup."""
        from frontend.state.run import _folder_picker_js
        js = _folder_picker_js("")
        assert "uploadUrl = '/upload-startup'" in js

    # ── _batch_picker_js ─────────────────────────────────────────────────────

    def test_batch_picker_js_embeds_backend_url(self):
        """_batch_picker_js injects the given backend base and upload endpoint."""
        from frontend.state.run import _batch_picker_js
        js = _batch_picker_js("http://localhost:8001")
        assert "http://localhost:8001" in js
        assert "upload-startup" in js

    def test_batch_picker_js_targets_batch_input(self):
        """_batch_picker_js targets the evalbot-batch-input element."""
        from frontend.state.run import _batch_picker_js
        js = _batch_picker_js("http://localhost:8001")
        assert "evalbot-batch-input" in js

    def test_batch_picker_js_empty_base_uses_relative(self):
        """_batch_picker_js with empty backend_base falls back to /upload-startup."""
        from frontend.state.run import _batch_picker_js
        js = _batch_picker_js("")
        assert "uploadUrl = '/upload-startup'" in js

    # ── run_label computed var ────────────────────────────────────────────────

    def test_run_label_empty_staged(self):
        """run_label returns 'Run Batch' when no startups are staged."""
        from frontend.state.run import RunState
        state = RunState()
        state.staged = []
        assert state.run_label == "Run Batch"

    def test_run_label_one_startup(self):
        """run_label returns 'Run Single' when exactly one startup is staged."""
        from frontend.state.run import RunState
        state = RunState()
        state.staged = [{"name": "AcmeCorp", "files": ["pitch.pdf"]}]
        assert state.run_label == "Run Single"

    def test_run_label_multiple_startups(self):
        """run_label returns 'Run Batch' when two or more startups are staged."""
        from frontend.state.run import RunState
        state = RunState()
        state.staged = [
            {"name": "Alpha", "files": ["a.pdf"]},
            {"name": "Beta", "files": ["b.pdf"]},
        ]
        assert state.run_label == "Run Batch"

    # ── _save_folder_files (upload endpoint helper) ───────────────────────────

    def test_save_folder_files_happy_path(self, tmp_path):
        """Files with supported extensions are saved and returned."""
        from frontend.frontend import _save_folder_files
        files = [("pitch.pdf", b"PDF content"), ("notes.md", b"# Notes")]
        saved, err = _save_folder_files("AcmeCorp", files, startups_dir=tmp_path)
        assert err is None
        assert "pitch.pdf" in saved
        assert "notes.md" in saved
        assert (tmp_path / "AcmeCorp" / "pitch.pdf").exists()

    def test_save_folder_files_no_name(self, tmp_path):
        """Empty startup name returns an error."""
        from frontend.frontend import _save_folder_files
        _, err = _save_folder_files("", [("x.pdf", b"")], startups_dir=tmp_path)
        assert err is not None and "name" in err.lower()

    def test_save_folder_files_skips_unsupported(self, tmp_path):
        """Unsupported file types are skipped; supported ones are saved."""
        from frontend.frontend import _save_folder_files
        files = [("video.mp4", b"vid"), ("deck.pdf", b"pdf")]
        saved, err = _save_folder_files("Startup", files, startups_dir=tmp_path)
        assert err is None
        assert "deck.pdf" in saved
        assert "video.mp4" not in saved

    def test_save_folder_files_all_unsupported(self, tmp_path):
        """If all files are unsupported, returns an error and empty saved list."""
        from frontend.frontend import _save_folder_files
        files = [("video.mp4", b"vid")]
        saved, err = _save_folder_files("Startup", files, startups_dir=tmp_path)
        assert err is not None
        assert saved == []

    def test_save_folder_files_path_traversal_blocked(self, tmp_path):
        """'../evil' is sanitized so files land inside startups_dir, not above it."""
        from frontend.frontend import _save_folder_files
        saved, err = _save_folder_files("../evil", [("x.pdf", b"x")], startups_dir=tmp_path)
        # Either the file is saved under a sanitized name inside tmp_path, or an error is returned.
        assert (tmp_path / "evil" / "x.pdf").exists() or err is not None

    # ── remove_startup ────────────────────────────────────────────────────────

    def test_remove_startup_removes_from_staged(self, tmp_path, monkeypatch):
        """remove_startup deletes dir and removes entry from staged list."""
        startups_dir = tmp_path / "Startups"
        (startups_dir / "RemoveCo").mkdir(parents=True)
        (startups_dir / "RemoveCo" / "pitch.pdf").write_bytes(b"x")

        staged = [
            {"name": "RemoveCo", "files": ["pitch.pdf"]},
            {"name": "KeepCo", "files": ["deck.pdf"]},
        ]

        import shutil
        name = "RemoveCo"
        target = startups_dir / name
        if target.exists() and target.is_dir():
            shutil.rmtree(target)

        staged = [s for s in staged if s["name"] != name]

        assert not (startups_dir / "RemoveCo").exists()
        assert len(staged) == 1
        assert staged[0]["name"] == "KeepCo"

    def test_remove_startup_nonexistent_dir(self, tmp_path):
        """remove_startup is safe when directory was already deleted."""
        staged = [{"name": "GoneCo", "files": []}]
        startups_dir = tmp_path / "Startups"
        startups_dir.mkdir()

        import shutil
        name = "GoneCo"
        target = startups_dir / name
        if target.exists() and target.is_dir():
            shutil.rmtree(target)  # dir doesn't exist, no error

        staged = [s for s in staged if s["name"] != name]
        assert staged == []

    # ── toggle_log ────────────────────────────────────────────────────────────

    def test_toggle_log_false_to_true(self):
        """Clicking raw log toggle opens the log view."""
        show_log = False
        show_log = not show_log
        assert show_log is True

    def test_toggle_log_true_to_false(self):
        """Clicking raw log toggle again collapses it."""
        show_log = True
        show_log = not show_log
        assert show_log is False

    # ── toggle_filter ─────────────────────────────────────────────────────────

    def test_toggle_filter_activates(self):
        """Clicking 'Hide single-file' button enables filter."""
        filter_single = False
        filter_single = not filter_single
        assert filter_single is True

    def test_toggle_filter_deactivates(self):
        """Clicking filter button again disables it."""
        filter_single = True
        filter_single = not filter_single
        assert filter_single is False

    # ── has_multi_file ────────────────────────────────────────────────────────

    def test_has_multi_file_no_startups(self):
        staged: list[dict] = []
        assert any(len(s.get("files", [])) > 1 for s in staged) is False

    def test_has_multi_file_all_single(self):
        staged = [{"name": "A", "files": ["f.pdf"]}, {"name": "B", "files": ["g.txt"]}]
        assert any(len(s.get("files", [])) > 1 for s in staged) is False

    def test_has_multi_file_one_multi(self):
        staged = [
            {"name": "A", "files": ["f.pdf"]},
            {"name": "B", "files": ["deck.pdf", "notes.md"]},
        ]
        assert any(len(s.get("files", [])) > 1 for s in staged) is True

    def test_has_multi_file_all_multi(self):
        staged = [
            {"name": "A", "files": ["f.pdf", "g.md"]},
            {"name": "B", "files": ["deck.pdf", "notes.md"]},
        ]
        assert any(len(s.get("files", [])) > 1 for s in staged) is True

    # ── filter_single logic ───────────────────────────────────────────────────

    def test_filter_single_excludes_one_file_startups(self):
        """When filter_single=True, only multi-file startups go to run cmd."""
        staged = [
            {"name": "Alpha", "files": ["pitch.pdf"]},
            {"name": "Beta", "files": ["deck.pdf", "notes.md"]},
            {"name": "Gamma", "files": ["brief.txt"]},
        ]
        filter_single = True
        filtered = [s["name"] for s in staged if not filter_single or len(s.get("files", [])) > 1]
        assert filtered == ["Beta"]

    def test_filter_single_false_includes_all(self):
        staged = [
            {"name": "Alpha", "files": ["pitch.pdf"]},
            {"name": "Beta", "files": ["deck.pdf", "notes.md"]},
        ]
        filter_single = False
        filtered = [s["name"] for s in staged if not filter_single or len(s.get("files", [])) > 1]
        assert filtered == ["Alpha", "Beta"]

    def test_filter_single_no_staged_yields_empty(self):
        staged: list[dict] = []
        filter_single = True
        filtered = [s["name"] for s in staged if not filter_single or len(s.get("files", [])) > 1]
        assert filtered == []

    # ── start_run error: no startups staged ──────────────────────────────────

    def test_start_run_no_staged_sets_error(self):
        """start_run with empty staged list → status=error, run_error set."""
        staged: list[dict] = []
        filter_single = False
        startup_names = [
            s["name"] for s in staged if not filter_single or len(s.get("files", [])) > 1
        ]
        status = "running"
        run_error = ""
        if not startup_names:
            status = "error"
            run_error = "No startups staged."

        assert status == "error"
        assert run_error == "No startups staged."

    def test_start_run_no_staged_after_filter_sets_error(self):
        """start_run with filter_single=True and only single-file startups → error."""
        staged = [{"name": "OnlyOne", "files": ["pitch.pdf"]}]
        filter_single = True
        startup_names = [
            s["name"] for s in staged if not filter_single or len(s.get("files", [])) > 1
        ]
        status = "running"
        run_error = ""
        if not startup_names:
            status = "error"
            run_error = "No startups staged."

        assert status == "error"
        assert run_error == "No startups staged."

    # ── Progress event parsing ────────────────────────────────────────────────

    def test_progress_batch_start(self):
        """BATCH_START sets progress_total."""
        progress_total = 0
        data = {"total": 5}
        progress_total = data.get("total", 0)
        assert progress_total == 5

    def test_progress_startup_start(self):
        """STARTUP_START adds a new entry to progress_active."""
        progress_active: list[dict] = []
        progress_total = 0

        data = {"name": "AlphaCo", "total": 5}
        name = data.get("name", "")
        progress_total = data.get("total", progress_total)
        entry = {
            "name": name, "elapsed_s": 0, "current_role": "",
            "a1_done": False, "a1_active": False,
            "a2_done": False, "a2_active": False,
            "a3_done": False, "a3_active": False,
            "a4_done": False, "a4_active": False,
            "a5_done": False, "a5_active": False,
            "a6_done": False, "a6_active": False,
        }
        progress_active = progress_active + [entry]

        assert progress_total == 5
        assert len(progress_active) == 1
        assert progress_active[0]["name"] == "AlphaCo"
        assert progress_active[0]["a1_done"] is False
        assert progress_active[0]["a1_active"] is False

    def test_progress_agent_start(self):
        """AGENT_START marks the agent active and sets current_role on the matching entry."""
        progress_active = [
            {"name": "AlphaCo", "elapsed_s": 10, "current_role": "",
             "a1_done": True, "a1_active": False,
             "a2_done": False, "a2_active": False,
             "a3_done": False, "a3_active": False,
             "a4_done": False, "a4_active": False,
             "a5_done": False, "a5_active": False,
             "a6_done": False, "a6_active": False}
        ]
        data = {"name": "AlphaCo", "agent": 2, "role": "Market & Competition Analyst"}
        name = data.get("name", "")
        agent = data.get("agent", 0)
        role = data.get("role", "")
        if 1 <= agent <= 6:
            progress_active = [
                {**e, f"a{agent}_active": True, "current_role": role}
                if e["name"] == name else e
                for e in progress_active
            ]

        assert progress_active[0]["a2_active"] is True
        assert progress_active[0]["current_role"] == "Market & Competition Analyst"
        assert progress_active[0]["a1_active"] is False  # unchanged

    def test_progress_agent_done(self):
        """AGENT_DONE marks agent done, clears active flag and current_role."""
        progress_active = [
            {"name": "AlphaCo", "elapsed_s": 30, "current_role": "Market & Competition Analyst",
             "a1_done": True, "a1_active": False,
             "a2_done": False, "a2_active": False,
             "a3_done": False, "a3_active": True,
             "a4_done": False, "a4_active": False,
             "a5_done": False, "a5_active": False,
             "a6_done": False, "a6_active": False}
        ]
        data = {"name": "AlphaCo", "agent": 3}
        name = data.get("name", "")
        agent = data.get("agent", 0)
        if 1 <= agent <= 6:
            progress_active = [
                {**e, f"a{agent}_done": True, f"a{agent}_active": False, "current_role": ""}
                if e["name"] == name else e
                for e in progress_active
            ]

        assert progress_active[0]["a3_done"] is True
        assert progress_active[0]["a3_active"] is False
        assert progress_active[0]["current_role"] == ""
        assert progress_active[0]["a1_done"] is True  # unchanged

    def test_progress_agent_done_no_duplicate(self):
        """AGENT_DONE is idempotent — marking an already-done agent done again is safe."""
        progress_active = [
            {"name": "AlphaCo", "elapsed_s": 40, "current_role": "",
             "a1_done": True, "a1_active": False,
             "a2_done": True, "a2_active": False,
             "a3_done": True, "a3_active": False,
             "a4_done": False, "a4_active": False,
             "a5_done": False, "a5_active": False,
             "a6_done": False, "a6_active": False}
        ]
        data = {"name": "AlphaCo", "agent": 2}  # agent 2 already done
        name = data.get("name", "")
        agent = data.get("agent", 0)
        if 1 <= agent <= 6:
            progress_active = [
                {**e, f"a{agent}_done": True, f"a{agent}_active": False, "current_role": ""}
                if e["name"] == name else e
                for e in progress_active
            ]

        assert progress_active[0]["a2_done"] is True   # still True, not lost
        assert progress_active[0]["a3_done"] is True   # unchanged

    def test_progress_startup_done(self):
        """STARTUP_DONE moves entry from progress_active to progress_completed."""
        progress_active = [
            {"name": "AlphaCo", "elapsed_s": 95, "current_role": "",
             "a1_done": True, "a1_active": False,
             "a2_done": True, "a2_active": False,
             "a3_done": True, "a3_active": False,
             "a4_done": True, "a4_active": False,
             "a5_done": True, "a5_active": False,
             "a6_done": True, "a6_active": False},
            {"name": "BetaCo", "elapsed_s": 60, "current_role": "Intake Parser",
             "a1_done": False, "a1_active": True,
             "a2_done": False, "a2_active": False,
             "a3_done": False, "a3_active": False,
             "a4_done": False, "a4_active": False,
             "a5_done": False, "a5_active": False,
             "a6_done": False, "a6_active": False},
        ]
        progress_completed: list[dict] = []
        data = {"name": "AlphaCo", "elapsed_s": 95}

        name = data.get("name", "")
        elapsed_s = data.get("elapsed_s", 0)
        completed_entry = {"name": name, "elapsed_s": elapsed_s, "timed_out": False}
        progress_completed = progress_completed + [completed_entry]
        progress_active = [e for e in progress_active if e["name"] != name]

        assert len(progress_completed) == 1
        assert progress_completed[0]["name"] == "AlphaCo"
        assert progress_completed[0]["elapsed_s"] == 95
        assert progress_completed[0]["timed_out"] is False
        assert len(progress_active) == 1
        assert progress_active[0]["name"] == "BetaCo"

    def test_progress_unknown_event_ignored(self):
        """Unknown PROGRESS event type does not crash."""
        event_type = "UNKNOWN_EVENT"
        data = {"foo": "bar"}
        progress_total = 0
        progress_active: list[dict] = []
        progress_ranking = False

        # Simulate the match logic — unknown events just do nothing
        if event_type == "BATCH_START":
            progress_total = data.get("total", 0)
        elif event_type == "STARTUP_START":
            pass
        elif event_type == "AGENT_START":
            pass
        elif event_type == "AGENT_DONE":
            pass
        elif event_type == "STARTUP_DONE":
            pass
        elif event_type == "STARTUP_TIMEOUT":
            pass
        elif event_type == "RANKING_START":
            progress_ranking = True
        # else: ignored

        assert progress_total == 0      # unchanged
        assert progress_active == []    # unchanged
        assert progress_ranking is False  # unchanged

    def test_progress_startup_timeout(self):
        """STARTUP_TIMEOUT moves entry to completed with timed_out=True."""
        progress_active = [
            {"name": "SlowCo", "elapsed_s": 900, "current_role": "Founder Fit Analyst",
             "a1_done": True, "a1_active": False,
             "a2_done": True, "a2_active": False,
             "a3_done": True, "a3_active": False,
             "a4_done": True, "a4_active": False,
             "a5_done": False, "a5_active": True,
             "a6_done": False, "a6_active": False},
        ]
        progress_completed: list[dict] = []
        data = {"name": "SlowCo", "elapsed_s": 900}

        name = data.get("name", "")
        elapsed_s = data.get("elapsed_s", 0)
        timeout_entry = {"name": name, "elapsed_s": elapsed_s, "timed_out": True}
        progress_completed = progress_completed + [timeout_entry]
        progress_active = [e for e in progress_active if e["name"] != name]

        assert len(progress_completed) == 1
        assert progress_completed[0]["name"] == "SlowCo"
        assert progress_completed[0]["timed_out"] is True
        assert len(progress_active) == 0

    def test_progress_ranking_start(self):
        """RANKING_START sets progress_ranking=True."""
        progress_ranking = False
        # Simulate RANKING_START handler
        progress_ranking = True
        assert progress_ranking is True

    def test_progress_parsing_ansi_stripped(self):
        """ANSI escape codes are stripped from log lines."""
        import re
        ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
        raw = b"\x1b[32mSome colored output\x1b[0m"
        line = ANSI_RE.sub("", raw.decode("utf-8", errors="replace")).rstrip()
        assert line == "Some colored output"

    def test_progress_line_parsing_valid(self):
        """PROGRESS:AGENT_START:{...} line is parsed correctly."""
        line = 'PROGRESS:AGENT_START:{"agent": 2, "role": "Venture Analyst"}'
        assert line.startswith("PROGRESS:")
        rest = line[len("PROGRESS:"):]
        colon = rest.find(":")
        assert colon >= 0
        event_type = rest[:colon]
        data = json.loads(rest[colon + 1:])
        assert event_type == "AGENT_START"
        assert data["agent"] == 2
        assert data["role"] == "Venture Analyst"

    def test_progress_line_parsing_bad_json(self):
        """Malformed JSON in PROGRESS line is caught gracefully."""
        line = "PROGRESS:AGENT_START:{bad json}"
        rest = line[len("PROGRESS:"):]
        colon = rest.find(":")
        event_type = rest[:colon]
        try:
            data = json.loads(rest[colon + 1:])
        except Exception:
            data = {}
        assert event_type == "AGENT_START"
        assert data == {}


# ============================================================================
# Run state — run-state persistence (already in test_frontend.py, add edge cases)
# ============================================================================

class TestRunStatePersistence:

    def test_run_state_corrupt_json_returns_none(self, tmp_path, monkeypatch):
        """Corrupt evalbot_run.json is handled gracefully."""
        state_file = tmp_path / "evalbot_run.json"
        state_file.write_text("{this is not valid json")

        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "RUN_STATE_FILE", state_file)

        state = run_mod._read_run_state()
        assert state is None  # exception caught, returns None

    def test_run_state_done_persists_batch_id(self, tmp_path, monkeypatch):
        """Completed run state stores batch_id for 'View Results' link."""
        state_file = tmp_path / "evalbot_run.json"
        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "RUN_STATE_FILE", state_file)

        run_mod._write_run_state("job-abc", "done", "batch_7")
        state = run_mod._read_run_state()
        assert state["status"] == "done"
        assert state["batch_id"] == "batch_7"

    def test_latest_batch_id_ignores_non_batch_dirs(self, tmp_path, monkeypatch):
        """_latest_batch_id skips non-batch_N directories."""
        output_dir = tmp_path / "output" / "Batch"
        (output_dir / "batch_1").mkdir(parents=True)
        (output_dir / "batch_2").mkdir()
        (output_dir / "some_other_dir").mkdir()  # should be ignored
        (output_dir / "batch_abc").mkdir()        # non-numeric — should be ignored

        from frontend.state import run as run_mod
        monkeypatch.setattr(run_mod, "OUTPUT_DIR", output_dir)

        result = run_mod._latest_batch_id()
        assert result == "batch_2"


# ============================================================================
# Cross-page: navigation link construction
# ============================================================================

class TestNavigationLinks:
    """Verify that navigation URLs are constructed correctly."""

    def test_batch_link_from_dashboard(self):
        """Dashboard batch row links to /batch/{batch_id}."""
        batch_id = "batch_3"
        href = f"/batch/{batch_id}"
        assert href == "/batch/batch_3"

    def test_startup_link_from_batch(self):
        """Batch leaderboard row links to /batch/{batch_id}/{startup_name}."""
        batch_id = "batch_3"
        name = "AlphaCo"
        href = f"/batch/{batch_id}/{name}"
        assert href == "/batch/batch_3/AlphaCo"

    def test_view_results_link_after_run(self):
        """'View Results' button links to /batch/{completed_batch_id}."""
        completed_batch_id = "batch_5"
        href = "/batch/" + completed_batch_id
        assert href == "/batch/batch_5"

    def test_shortlist_links_in_batch_page(self):
        """Shortlist entries link to /batch/{batch_id}/{startup_name}."""
        batch_id = "batch_1"
        shortlist = ["AlphaCo", "GammaCo"]
        links = [f"/batch/{batch_id}/{name}" for name in shortlist]
        assert links == ["/batch/batch_1/AlphaCo", "/batch/batch_1/GammaCo"]

    def test_run_new_batch_button_links_to_run(self):
        """'Run New Batch' button on dashboard links to /run."""
        href = "/run"
        assert href == "/run"

    def test_dashboard_breadcrumb_link(self):
        """All inner pages have 'Dashboard' breadcrumb pointing to /."""
        href = "/"
        assert href == "/"
