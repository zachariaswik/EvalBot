"""Tests for src/models.py — Pydantic output schemas for all 7 agents."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.models import (
    AGENT_OUTPUT_MODELS,
    Agent1Output,
    Agent2Output,
    Agent3Output,
    Agent4Output,
    Agent5Output,
    Agent6Output,
    Agent7Output,
    CategorizedStartup,
    MarketSizeClass,
    RankedStartup,
    Recommendation,
    StartupLabel,
    SWOTModel,
    Verdict,
    WrapperRisk,
)


# ---------------------------------------------------------------------------
# Agent 1 — Intake Parser
# ---------------------------------------------------------------------------

class TestAgent1Output:
    def test_all_defaults(self):
        out = Agent1Output()
        assert out.startup_name == "Unknown Startup"
        assert out.problem == "Not provided"
        assert out.solution == "Not provided"
        assert out.clarity_score == 5
        assert out.missing_info == []
        assert out.inconsistencies == []

    def test_clarity_score_valid_bounds(self):
        out = Agent1Output(clarity_score=1)
        assert out.clarity_score == 1
        out = Agent1Output(clarity_score=10)
        assert out.clarity_score == 10

    def test_clarity_score_too_high_raises(self):
        with pytest.raises(ValidationError):
            Agent1Output(clarity_score=11)

    def test_clarity_score_too_low_raises(self):
        with pytest.raises(ValidationError):
            Agent1Output(clarity_score=0)

    def test_missing_info_accepts_list(self):
        out = Agent1Output(missing_info=["team", "market"])
        assert out.missing_info == ["team", "market"]

    def test_full_construction(self):
        out = Agent1Output(
            startup_name="Acme",
            problem="Users waste time",
            solution="Automate it",
            target_customer="SMBs",
            buyer="CTO",
            market="B2B SaaS",
            business_model="Subscription",
            clarity_score=8,
        )
        assert out.startup_name == "Acme"
        assert out.clarity_score == 8


# ---------------------------------------------------------------------------
# Agent 2 — Unified Venture Analyst
# ---------------------------------------------------------------------------

class TestAgent2Output:
    def test_all_defaults(self):
        out = Agent2Output()
        assert out.verdict == Verdict.PROMISING_NEEDS_FOCUS
        assert out.total_score == 50
        assert isinstance(out.swot, SWOTModel)

    def test_score_field_bounds(self):
        for field in [
            "score_problem_severity", "score_market_size", "score_differentiation",
            "score_customer_clarity", "score_founder_insight", "score_business_model",
            "score_moat_potential", "score_venture_potential",
            "score_competition_difficulty", "score_execution_feasibility",
        ]:
            with pytest.raises(ValidationError):
                Agent2Output(**{field: 0})
            with pytest.raises(ValidationError):
                Agent2Output(**{field: 11})

    def test_verdict_enum_values(self):
        assert Verdict.TOP_VC_CANDIDATE == "Top VC Candidate"
        assert Verdict.REJECT == "Reject"
        assert Verdict.AI_WRAPPER == "AI Wrapper With Weak Moat"
        assert Verdict.FEATURE_NOT_COMPANY == "Feature, Not a Company"

    def test_all_verdicts_constructable(self):
        for v in Verdict:
            out = Agent2Output(verdict=v)
            assert out.verdict == v


class TestSWOTModel:
    def test_defaults_empty_lists(self):
        swot = SWOTModel()
        assert swot.strengths == []
        assert swot.weaknesses == []
        assert swot.opportunities == []
        assert swot.threats == []

    def test_accepts_lists(self):
        swot = SWOTModel(strengths=["strong team"], threats=["incumbents"])
        assert len(swot.strengths) == 1
        assert len(swot.threats) == 1


# ---------------------------------------------------------------------------
# Agent 3 — Market & Competition Analyst
# ---------------------------------------------------------------------------

_AGENT3_MINIMAL = dict(
    market_category="B2B SaaS",
    size_class=MarketSizeClass.LARGE,
    trend="Growing fast",
    direct_competitors="Salesforce",
    indirect_competitors="Excel",
    big_tech_risk="Medium",
    crowdedness="High",
    wedge="SMB segment",
    attractiveness_score=7,
    competition_score=5,
    conclusion="Good market",
)


class TestAgent3Output:
    def test_valid_construction(self):
        out = Agent3Output(**_AGENT3_MINIMAL)
        assert out.market_category == "B2B SaaS"
        assert out.size_class == MarketSizeClass.LARGE
        assert out.attractiveness_score == 7

    def test_market_size_class_all_values(self):
        for size in MarketSizeClass:
            out = Agent3Output(**{**_AGENT3_MINIMAL, "size_class": size})
            assert out.size_class == size

    def test_attractiveness_score_bounds(self):
        with pytest.raises(ValidationError):
            Agent3Output(**{**_AGENT3_MINIMAL, "attractiveness_score": 0})
        with pytest.raises(ValidationError):
            Agent3Output(**{**_AGENT3_MINIMAL, "attractiveness_score": 11})

    def test_competition_score_bounds(self):
        with pytest.raises(ValidationError):
            Agent3Output(**{**_AGENT3_MINIMAL, "competition_score": 11})


# ---------------------------------------------------------------------------
# Agent 4 — Product & Positioning Analyst
# ---------------------------------------------------------------------------

_AGENT4_MINIMAL = dict(
    product_reality="A SaaS dashboard",
    value_prop="Saves time",
    killer_feature="Auto-sync",
    why_care="Reduces manual work",
    why_not_care="Incumbents exist",
    feature_vs_company="Potential company",
    wrapper_risk=WrapperRisk.LOW,
    wedge="SMB accounting",
    moat="Data network effects",
    positioning="SMB finance tool",
    six_month_focus="Close 10 customers",
)


class TestAgent4Output:
    def test_valid_construction(self):
        out = Agent4Output(**_AGENT4_MINIMAL)
        assert out.wrapper_risk == WrapperRisk.LOW
        assert out.product_reality == "A SaaS dashboard"

    def test_wrapper_risk_all_values(self):
        for risk in WrapperRisk:
            out = Agent4Output(**{**_AGENT4_MINIMAL, "wrapper_risk": risk})
            assert out.wrapper_risk == risk


# ---------------------------------------------------------------------------
# Agent 5 — Founder Fit Analyst
# ---------------------------------------------------------------------------

_AGENT5_MINIMAL = dict(
    founder_fit="Strong domain fit",
    domain="10 years in fintech",
    technical="Strong engineer",
    distribution="Former sales",
    strategy="Clear vision",
    ambition="Venture-scale",
    execution="High confidence",
    fit_score=8,
    execution_score=7,
    conclusion="Excellent team",
)


class TestAgent5Output:
    def test_valid_construction(self):
        out = Agent5Output(**_AGENT5_MINIMAL)
        assert out.fit_score == 8
        assert out.execution_score == 7
        assert out.missing_roles == []

    def test_fit_score_bounds(self):
        with pytest.raises(ValidationError):
            Agent5Output(**{**_AGENT5_MINIMAL, "fit_score": 0})
        with pytest.raises(ValidationError):
            Agent5Output(**{**_AGENT5_MINIMAL, "fit_score": 11})

    def test_execution_score_bounds(self):
        with pytest.raises(ValidationError):
            Agent5Output(**{**_AGENT5_MINIMAL, "execution_score": 11})


# ---------------------------------------------------------------------------
# Agent 6 — Recommendation / Pivot Agent
# ---------------------------------------------------------------------------

class TestAgent6Output:
    def test_all_defaults(self):
        out = Agent6Output()
        assert out.recommendation == Recommendation.REFINE
        assert out.customer_segment == "Not provided"
        assert out.remove == []
        assert out.pivots == []

    def test_recommendation_enum_values(self):
        assert Recommendation.CONTINUE == "Continue"
        assert Recommendation.PIVOT == "Pivot"
        assert Recommendation.DROP == "Drop"
        assert Recommendation.REFINE == "Refine"

    def test_all_recommendations_constructable(self):
        for r in Recommendation:
            out = Agent6Output(recommendation=r)
            assert out.recommendation == r


# ---------------------------------------------------------------------------
# Agent 7 — Ranking Committee Agent
# ---------------------------------------------------------------------------

class TestAgent7Output:
    def test_minimal_construction(self):
        out = Agent7Output(ranked_startups=[])
        assert out.ranked_startups == []
        assert out.top_vc_candidates == []
        assert out.shortlist == []
        assert out.common_patterns == []

    def test_ranked_startup_model(self):
        rs = RankedStartup(
            name="TestCo",
            label=StartupLabel.VC_SCALE,
            rank=1,
            score=87.5,
            summary="Top contender",
        )
        assert rs.name == "TestCo"
        assert rs.rank == 1

    def test_categorized_startup_model(self):
        cs = CategorizedStartup(name="TestCo", rationale="Strong team")
        assert cs.name == "TestCo"
        assert cs.rationale == "Strong team"

    def test_start_label_all_values(self):
        labels = {sl.value for sl in StartupLabel}
        assert "VC-Scale" in labels
        assert "Reject" in labels

    def test_full_construction_with_startups(self):
        ranked = [
            RankedStartup(name="A", label=StartupLabel.VC_SCALE, rank=1, score=90, summary="Best"),
            RankedStartup(name="B", label=StartupLabel.REJECT, rank=2, score=30, summary="Weak"),
        ]
        out = Agent7Output(
            ranked_startups=ranked,
            shortlist=["A"],
            common_patterns=["AI wrappers"],
        )
        assert len(out.ranked_startups) == 2
        assert out.shortlist == ["A"]


# ---------------------------------------------------------------------------
# AGENT_OUTPUT_MODELS lookup
# ---------------------------------------------------------------------------

class TestAgentOutputModels:
    def test_covers_all_agents(self):
        assert set(AGENT_OUTPUT_MODELS.keys()) == {1, 2, 3, 4, 5, 6, 7}

    def test_correct_types(self):
        assert AGENT_OUTPUT_MODELS[1] is Agent1Output
        assert AGENT_OUTPUT_MODELS[2] is Agent2Output
        assert AGENT_OUTPUT_MODELS[3] is Agent3Output
        assert AGENT_OUTPUT_MODELS[4] is Agent4Output
        assert AGENT_OUTPUT_MODELS[5] is Agent5Output
        assert AGENT_OUTPUT_MODELS[6] is Agent6Output
        assert AGENT_OUTPUT_MODELS[7] is Agent7Output

    def test_all_are_pydantic_models(self):
        from pydantic import BaseModel
        for model_cls in AGENT_OUTPUT_MODELS.values():
            assert issubclass(model_cls, BaseModel)
