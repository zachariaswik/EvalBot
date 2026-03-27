"""Pydantic output models for all 7 agents."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Feedback mixin — agents 2-6 can request a re-run from an earlier agent
# ---------------------------------------------------------------------------

class FeedbackMixin(BaseModel):
    rerun_from_agent: Optional[int] = Field(
        default=None,
        description=(
            "If the analysis reveals that an earlier agent's output is insufficient "
            "or inconsistent, set this to the agent number (1-6) to re-run from. "
            "Leave null/None if no re-run is needed."
        ),
    )
    rerun_reason: Optional[str] = Field(
        default=None,
        description="Explanation of why a re-run from an earlier agent is needed.",
    )


# ---------------------------------------------------------------------------
# Agent 1 — Intake Parser
# ---------------------------------------------------------------------------

class Agent1Output(FeedbackMixin):
    startup_name: str = Field(description="Name of the startup")
    one_line_description: str = Field(description="One-line description of the startup")
    problem: str = Field(description="Problem the startup is solving")
    solution: str = Field(description="Proposed solution")
    target_customer: str = Field(description="Target customer / ICP")
    buyer: str = Field(description="Who pays — may differ from user")
    market: str = Field(description="Market description")
    business_model: str = Field(description="How the startup makes money")
    competitors: str = Field(description="Competitors and alternatives")
    traction: str = Field(description="Current traction and evidence")
    team: str = Field(description="Team description")
    why_now: str = Field(description="Why this is the right time")
    vision: str = Field(description="Long-term vision")
    unfair_advantage: str = Field(description="Claimed unfair advantage")
    risks: str = Field(description="Declared risks")
    missing_info: list[str] = Field(default_factory=list, description="Missing critical information")
    inconsistencies: list[str] = Field(default_factory=list, description="Inconsistencies or weak logic")
    clarity_score: int = Field(ge=1, le=10, description="Overall clarity of submission (1-10)")


# ---------------------------------------------------------------------------
# Agent 2 — Unified Venture Analyst
# ---------------------------------------------------------------------------

class Verdict(str, Enum):
    TOP_VC_CANDIDATE = "Top VC Candidate"
    PROMISING_NEEDS_FOCUS = "Promising, Needs Sharper Focus"
    PROMISING_NEEDS_PIVOT = "Promising, But Needs Pivot"
    GOOD_SMALL_BUSINESS = "Good Small Business, Not Venture-Scale"
    FEATURE_NOT_COMPANY = "Feature, Not a Company"
    AI_WRAPPER = "AI Wrapper With Weak Moat"
    REJECT = "Reject"


class SWOTModel(BaseModel):
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    threats: list[str] = Field(default_factory=list)


class Agent2Output(FeedbackMixin):
    summary: str
    problem_assessment: str
    market_assessment: str
    competition_assessment: str
    product_assessment: str
    business_model_assessment: str
    founder_insight_assessment: str
    moat_potential: str
    main_risks: str
    main_opportunities: str

    swot: SWOTModel

    score_problem_severity: int = Field(ge=1, le=10)
    score_market_size: int = Field(ge=1, le=10)
    score_differentiation: int = Field(ge=1, le=10)
    score_customer_clarity: int = Field(ge=1, le=10)
    score_founder_insight: int = Field(ge=1, le=10)
    score_business_model: int = Field(ge=1, le=10)
    score_moat_potential: int = Field(ge=1, le=10)
    score_venture_potential: int = Field(ge=1, le=10)
    score_competition_difficulty: int = Field(ge=1, le=10)
    score_execution_feasibility: int = Field(ge=1, le=10)
    total_score: int = Field(description="Sum of all 10 scores")

    verdict: Verdict
    explanation: str = Field(description="Why this verdict was chosen")


# ---------------------------------------------------------------------------
# Agent 3 — Market & Competition Analyst
# ---------------------------------------------------------------------------

class MarketSizeClass(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    NEW_CATEGORY = "new category"


class Agent3Output(FeedbackMixin):
    market_category: str
    size_class: MarketSizeClass
    trend: str = Field(description="Market growth and trends")
    direct_competitors: str = Field(description="Direct competitor types")
    indirect_competitors: str = Field(description="Indirect competitors and substitutes")
    big_tech_risk: str = Field(description="Incumbent / Big Tech / Platform risk")
    crowdedness: str = Field(description="Market crowdedness assessment")
    wedge: str = Field(description="Wedge opportunity for a new entrant")
    attractiveness_score: int = Field(ge=1, le=10, description="Market attractiveness (1-10)")
    competition_score: int = Field(ge=1, le=10, description="Competition difficulty (1-10)")
    conclusion: str = Field(description="Is this a good market for a new startup?")


# ---------------------------------------------------------------------------
# Agent 4 — Product & Positioning Analyst
# ---------------------------------------------------------------------------

class WrapperRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Agent4Output(FeedbackMixin):
    product_reality: str = Field(description="What the product really is")
    value_prop: str = Field(description="Value proposition")
    killer_feature: str = Field(description="Killer feature, if any")
    why_care: str = Field(description="Why customers would care")
    why_not_care: str = Field(description="Why customers might not care")
    feature_vs_company: str = Field(description="Feature vs Company assessment")
    wrapper_risk: WrapperRisk
    wedge: str = Field(description="Best wedge market")
    moat: str = Field(description="Moat hypothesis")
    positioning: str = Field(description="Recommended positioning")
    six_month_focus: str = Field(description="Focus recommendation for next 6 months")


# ---------------------------------------------------------------------------
# Agent 5 — Founder Fit Analyst
# ---------------------------------------------------------------------------

class Agent5Output(FeedbackMixin):
    founder_fit: str = Field(description="Founder-market fit assessment")
    domain: str = Field(description="Domain expertise assessment")
    technical: str = Field(description="Technical strength assessment")
    distribution: str = Field(description="Distribution / sales ability")
    strategy: str = Field(description="Strategic clarity")
    execution: str = Field(description="Execution confidence assessment")
    missing_roles: list[str] = Field(default_factory=list, description="Missing roles or capabilities")
    risks: list[str] = Field(default_factory=list, description="Team risks")
    fit_score: int = Field(ge=1, le=10, description="Founder fit score (1-10)")
    execution_score: int = Field(ge=1, le=10, description="Execution confidence score (1-10)")
    conclusion: str = Field(description="Can this team build a serious startup?")


# ---------------------------------------------------------------------------
# Agent 6 — Recommendation / Pivot Agent
# ---------------------------------------------------------------------------

class Recommendation(str, Enum):
    CONTINUE = "Continue"
    REFINE = "Refine"
    PIVOT = "Pivot"
    DROP = "Drop"


class Agent6Output(FeedbackMixin):
    recommendation: Recommendation
    customer_segment: str = Field(description="Best customer segment")
    wedge: str = Field(description="Best wedge strategy")
    remove: list[str] = Field(default_factory=list, description="What to remove")
    emphasize: list[str] = Field(default_factory=list, description="What to emphasize")
    pivots: list[str] = Field(default_factory=list, description="Suggested pivot directions (up to 3)")
    positioning_rewrite: str = Field(description="Suggested positioning rewrite")
    thirty_day_plan: str = Field(description="30-day action plan")
    ninety_day_plan: str = Field(description="90-day action plan")
    mistake_to_avoid: str = Field(description="Biggest strategic mistake to avoid")


# ---------------------------------------------------------------------------
# Agent 7 — Ranking Committee Agent (no FeedbackMixin)
# ---------------------------------------------------------------------------

class StartupLabel(str, Enum):
    VC_SCALE = "VC-Scale"
    NEEDS_PIVOT = "Needs Pivot"
    SMALL_BUSINESS = "Small Business"
    FEATURE = "Feature"
    WRAPPER = "Wrapper"
    REJECT = "Reject"


class RankedStartup(BaseModel):
    name: str
    label: StartupLabel
    rank: int
    score: float = Field(description="Composite score")
    summary: str = Field(description="One-line summary of the startup's evaluation")


class Agent7Output(BaseModel):
    ranked_startups: list[RankedStartup] = Field(description="All startups ranked")
    top_vc_candidates: list[str] = Field(default_factory=list)
    promising_need_focus: list[str] = Field(default_factory=list)
    promising_need_pivot: list[str] = Field(default_factory=list)
    good_small_businesses: list[str] = Field(default_factory=list)
    weak_ideas: list[str] = Field(default_factory=list)
    common_patterns: list[str] = Field(default_factory=list, description="Most common idea patterns")
    interesting_themes: list[str] = Field(default_factory=list, description="Most interesting themes")
    shortlist: list[str] = Field(default_factory=list, description="Recommended shortlist for interviews")


# ---------------------------------------------------------------------------
# Lookup table: agent number → output model
# ---------------------------------------------------------------------------

AGENT_OUTPUT_MODELS: dict[int, type[BaseModel]] = {
    1: Agent1Output,
    2: Agent2Output,
    3: Agent3Output,
    4: Agent4Output,
    5: Agent5Output,
    6: Agent6Output,
    7: Agent7Output,
}
