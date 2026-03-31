"""Pydantic output models for all 7 agents."""

from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Feedback mixin — agents 2-6 can request a re-run from an earlier agent
# ---------------------------------------------------------------------------

class Agent0Output(BaseModel):
    startup_name: str = Field(description="Name of the startup")
    one_line_description: str = Field(description="One-line description of the startup")
    submission_text: str = Field(description="Full generated startup submission")
    strategy_notes: str = Field(default="", description="Internal reasoning on why this should score well")
    
    # Explicit Dimension Reasoning - Self-evaluation before submission
    # Helps catch oversights and improves idea quality
    dimension_reasoning: dict[str, dict[str, float | str]] = Field(
        default_factory=dict,
        description=(
            "Self-evaluation on each scoring dimension. "
            "Keys are dimension names, values are dicts with 'self_score' (1-10) and 'reasoning' (str)."
        )
    )


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
    startup_name: str = Field(default="Unknown Startup", description="Name of the startup")
    one_line_description: str = Field(default="Not provided", description="One-line description of the startup")
    problem: str = Field(default="Not provided", description="Problem the startup is solving")
    solution: str = Field(default="Not provided", description="Proposed solution")
    target_customer: str = Field(default="Not provided", description="Target customer / ICP")
    buyer: str = Field(default="Not provided", description="Who pays — may differ from user")
    market: str = Field(default="Not provided", description="Market description")
    business_model: str = Field(default="Not provided", description="How the startup makes money")
    competitors: str = Field(default="Not provided", description="Competitors and alternatives")
    traction: str = Field(default="Not provided", description="Current traction and evidence")
    team: str = Field(default="Not provided", description="Team description")
    why_now: str = Field(default="Not provided", description="Why this is the right time")
    vision: str = Field(default="Not provided", description="Long-term vision")
    unfair_advantage: str = Field(default="Not provided", description="Claimed unfair advantage")
    risks: str = Field(default="Not provided", description="Declared risks")
    missing_info: list[str] | str = Field(default_factory=list, description="Missing critical information")
    inconsistencies: list[str] | str = Field(default_factory=list, description="Inconsistencies or weak logic")
    clarity_score: int = Field(default=5, ge=1, le=10, description="Overall clarity of submission (1-10)")


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
    summary: str = Field(default="Not provided")
    problem_assessment: str = Field(default="Not provided")
    market_assessment: str = Field(default="Not provided")
    competition_assessment: str = Field(default="Not provided")
    product_assessment: str = Field(default="Not provided")
    business_model_assessment: str = Field(default="Not provided")
    founder_insight_assessment: str = Field(default="Not provided")
    moat_potential: str = Field(default="Not provided")
    main_risks: str | list[str] = Field(default="Not provided")
    main_opportunities: str | list[str] = Field(default="Not provided")

    swot: SWOTModel = Field(default_factory=SWOTModel)

    score_problem_severity: int = Field(default=5, ge=1, le=10)
    score_market_size: int = Field(default=5, ge=1, le=10)
    score_differentiation: int = Field(default=5, ge=1, le=10)
    score_customer_clarity: int = Field(default=5, ge=1, le=10)
    score_founder_insight: int = Field(default=5, ge=1, le=10)
    score_business_model: int = Field(default=5, ge=1, le=10)
    score_moat_potential: int = Field(default=5, ge=1, le=10)
    score_venture_potential: int = Field(default=5, ge=1, le=10)
    score_competition_difficulty: int = Field(default=5, ge=1, le=10)
    score_execution_feasibility: int = Field(default=5, ge=1, le=10)
    total_score: int = Field(default=50, description="Sum of all 10 scores")

    verdict: Verdict = Field(default=Verdict.PROMISING_NEEDS_FOCUS)
    explanation: str = Field(default="Schema fallback used due unparseable output", description="Why this verdict was chosen")


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
    direct_competitors: str | list[str] = Field(description="Direct competitor types")
    indirect_competitors: str | list[str] = Field(description="Indirect competitors and substitutes")
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
    founder_fit: str | dict[str, Any] = Field(description="Founder-market fit assessment")
    domain: str | dict[str, Any] = Field(description="Domain expertise assessment")
    technical: str | dict[str, Any] = Field(description="Technical strength assessment")
    distribution: str | dict[str, Any] = Field(description="Distribution / sales ability")
    strategy: str | dict[str, Any] = Field(description="Strategic clarity")
    ambition: str | dict[str, Any] = Field(description="Ambition level assessment")
    execution: str | dict[str, Any] = Field(description="Execution confidence assessment")
    missing_roles: list[str] = Field(default_factory=list, description="Missing roles or capabilities")
    risks: list[str | dict[str, Any]] = Field(default_factory=list, description="Team risks")
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
    recommendation: Recommendation = Field(default=Recommendation.REFINE)
    customer_segment: str = Field(default="Not provided", description="Best customer segment")
    wedge: str = Field(default="Not provided", description="Best wedge strategy")
    remove: list[str] = Field(default_factory=list, description="What to remove")
    emphasize: list[str] = Field(default_factory=list, description="What to emphasize")
    pivots: list[str] = Field(default_factory=list, description="Suggested pivot directions (up to 3)")
    positioning_rewrite: str = Field(default="Not provided", description="Suggested positioning rewrite")
    thirty_day_plan: str | list[str] = Field(default="Not provided", description="30-day action plan")
    ninety_day_plan: str | list[str] = Field(default="Not provided", description="90-day action plan")
    mistake_to_avoid: str | list[str] = Field(default="Not provided", description="Biggest strategic mistake to avoid")


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
    0: Agent0Output,
    1: Agent1Output,
    2: Agent2Output,
    3: Agent3Output,
    4: Agent4Output,
    5: Agent5Output,
    6: Agent6Output,
    7: Agent7Output,
}
