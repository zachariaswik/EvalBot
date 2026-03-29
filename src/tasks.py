"""Factory for creating CrewAI Tasks with structured Pydantic output."""

from __future__ import annotations

import json
from typing import Any

from crewai import Agent, Task

from .models import AGENT_OUTPUT_MODELS, Agent0Output

# ---------------------------------------------------------------------------
# Expected-output descriptions for each agent
# ---------------------------------------------------------------------------

_EXPECTED_OUTPUT: dict[int, str] = {
    1: "A structured startup brief in JSON matching the Agent1Output schema.",
    2: "A venture analysis with scores, SWOT, and verdict in JSON matching the Agent2Output schema.",
    3: "A market and competition analysis in JSON matching the Agent3Output schema.",
    4: "A product and positioning analysis in JSON matching the Agent4Output schema.",
    5: "A founder fit analysis in JSON matching the Agent5Output schema.",
    6: "A recommendation with action plans in JSON matching the Agent6Output schema.",
    7: "A cohort ranking in JSON matching the Agent7Output schema.",
}

_FEEDBACK_INSTRUCTION = (
    "\n\n---\n"
    "FEEDBACK LOOP INSTRUCTION:\n"
    "If you believe an earlier agent's output is missing critical information, "
    "contains errors, or is insufficient for your analysis, you may request a "
    "re-run by setting `rerun_from_agent` to the agent number (1-{max_agent}) "
    "and `rerun_reason` to a brief explanation. Only do this if the issue is "
    "significant enough to affect your analysis quality. Otherwise leave these "
    "fields as null."
)


def _build_description(
    agent_number: int,
    submission_text: str,
    prior_context: dict[int, Any] | None,
    feedback_reason: str | None,
) -> str:
    """Build the task description for a given agent."""
    parts: list[str] = []

    if feedback_reason:
        parts.append(
            f"NOTE: This is a RE-RUN triggered by a downstream agent.\n"
            f"Reason for re-run: {feedback_reason}\n"
            f"Please address this feedback in your analysis.\n"
        )

    if agent_number == 1:
        parts.append("Analyze the following startup submission and produce a structured startup brief.\n")
        parts.append(f"STARTUP SUBMISSION:\n\n{submission_text}")
    else:
        parts.append("Analyze the following startup based on the accumulated analysis so far.\n")
        parts.append(f"ORIGINAL SUBMISSION:\n\n{submission_text}\n")
        if prior_context:
            parts.append("PRIOR AGENT OUTPUTS:\n")
            for num in sorted(prior_context.keys()):
                data = prior_context[num]
                if isinstance(data, dict):
                    formatted = json.dumps(data, indent=2, default=str)
                else:
                    formatted = str(data)
                parts.append(f"\n--- Agent {num} Output ---\n{formatted}\n")

    # Add feedback instruction for agents 2-6
    if 2 <= agent_number <= 6:
        parts.append(_FEEDBACK_INSTRUCTION.format(max_agent=agent_number - 1))

    return "\n".join(parts)


def create_task(
    agent_number: int,
    agent: Agent,
    submission_text: str,
    prior_context: dict[int, Any] | None = None,
    feedback_reason: str | None = None,
) -> Task:
    """Create a CrewAI Task for the given agent with structured Pydantic output."""
    description = _build_description(agent_number, submission_text, prior_context, feedback_reason)
    output_model = AGENT_OUTPUT_MODELS[agent_number]

    return Task(
        description=description,
        expected_output=_EXPECTED_OUTPUT[agent_number],
        agent=agent,
        output_pydantic=output_model,
    )


def create_agent0_task(
    agent: Agent,
    constraints: dict[str, Any],
    screening_feedback: dict[str, Any] | None = None,
    prior_evaluation: dict[str, Any] | None = None,
    prior_score: dict[str, Any] | None = None,
    round_number: int = 1,
    attempt_number: int = 1,
    force_completely_new_idea: bool = False,
) -> Task:
    """Create a task for Agent 0 — Startup Idea Generator.

    Args:
        agent: The CrewAI Agent instance for Agent 0.
        constraints: Founder constraints (team_size, experience, etc.).
        screening_feedback: Agent 2 output from a failed inner-loop attempt.
        prior_evaluation: Agent 6 output from the previous outer-loop round.
        prior_score: Agent 2 output from the previous outer-loop round.
        round_number: Current outer-loop round (1-based).
        attempt_number: Current inner-loop attempt (1-based).
        force_completely_new_idea: If true, require a fresh idea trajectory.
    """
    parts: list[str] = []

    parts.append(
        f"Generate a startup idea (Round {round_number}, Attempt {attempt_number}).\n"
    )

    # Founder constraints
    parts.append("FOUNDER CONSTRAINTS:\n")
    for key, value in constraints.items():
        label = key.replace("_", " ").title()
        parts.append(f"- {label}: {value}")
    parts.append("")

    # Inner loop feedback (screening rejection)
    if screening_feedback and attempt_number > 1:
        parts.append("SCREENING FEEDBACK — your previous idea scored below threshold:\n")
        parts.append(f"- Weighted Score: {screening_feedback.get('weighted_total_score', 'N/A')}/80")
        parts.append(f"- Score Tier: {screening_feedback.get('score_tier', 'N/A')}")
        parts.append(f"- Verdict: {screening_feedback.get('verdict', 'N/A')}")
        parts.append(f"- Explanation: {screening_feedback.get('explanation', 'N/A')}")

        # Include individual dimension scores for targeted improvement
        score_fields = [
            ("score_problem_severity", "Problem Severity"),
            ("score_market_size", "Market Size"),
            ("score_differentiation", "Differentiation"),
            ("score_customer_clarity", "Customer Clarity"),
            ("score_founder_insight", "Founder Insight"),
            ("score_business_model", "Business Model"),
            ("score_moat_potential", "Moat Potential"),
            ("score_venture_potential", "Venture Potential"),
            ("score_competition_difficulty", "Competition Difficulty"),
            ("score_execution_feasibility", "Execution Feasibility"),
        ]
        parts.append("\nDimension Scores:")
        for field, label in score_fields:
            parts.append(f"  - {label}: {screening_feedback.get(field, 'N/A')}/10")
        parts.append("\nGenerate a DIFFERENT idea that addresses the weaknesses above.\n")

    # Outer loop feedback (prior round evaluation)
    if round_number > 1 and (prior_evaluation or force_completely_new_idea):
        if force_completely_new_idea:
            parts.append(
                "STRATEGIC RESTART MODE: The previous rounds were not strongly positive.\n"
                "Generate a COMPLETELY NEW idea direction. Do NOT do a light refinement, "
                "small pivot, or iteration of the prior concept.\n"
                "Use prior feedback only as anti-pattern guidance (what to avoid repeating).\n"
            )
        parts.append("PRIOR ROUND EVALUATION (from full pipeline):\n")
        if prior_score:
            parts.append(f"Previous Weighted Score: {prior_score.get('weighted_total_score', 'N/A')}/80")
            parts.append(f"Previous Verdict: {prior_score.get('verdict', 'N/A')}\n")
        if prior_evaluation:
            parts.append(f"Recommendation: {prior_evaluation.get('recommendation', 'N/A')}")
            parts.append(f"Best Customer Segment: {prior_evaluation.get('customer_segment', 'N/A')}")
            parts.append(f"Best Wedge Strategy: {prior_evaluation.get('wedge', 'N/A')}")

            remove = prior_evaluation.get("remove", [])
            if remove:
                parts.append(f"Stop Doing: {', '.join(str(r) for r in remove)}")

            emphasize = prior_evaluation.get("emphasize", [])
            if emphasize:
                parts.append(f"Start Emphasizing: {', '.join(str(e) for e in emphasize)}")

            pivots = prior_evaluation.get("pivots", [])
            if pivots:
                parts.append("Suggested Pivots:")
                for i, p in enumerate(pivots, 1):
                    parts.append(f"  {i}. {p}")

            mistake = prior_evaluation.get("mistake_to_avoid")
            if mistake:
                parts.append(f"Mistake to Avoid: {mistake}")

        if force_completely_new_idea:
            parts.append("\nUse this context to avoid past mistakes while proposing a DISTINCT new concept.\n")
        else:
            parts.append("\nUse this feedback to generate a FUNDAMENTALLY IMPROVED idea.\n")

    return Task(
        description="\n".join(parts),
        expected_output="A startup idea with name, description, full submission text, and strategy notes in JSON matching the Agent0Output schema.",
        agent=agent,
        output_pydantic=Agent0Output,
    )


def create_ranking_task(
    agent: Agent,
    batch_data: list[dict],
) -> Task:
    """Create the Agent 7 ranking task from accumulated batch data."""
    parts = ["Rank the following startups relative to each other.\n"]
    for entry in batch_data:
        name = entry["startup_name"]
        outputs = entry["outputs"]
        parts.append(f"\n{'='*60}\nSTARTUP: {name}\n{'='*60}\n")
        for num in sorted(outputs.keys()):
            parts.append(f"\n--- Agent {num} Output ---\n{json.dumps(outputs[num], indent=2, default=str)}\n")

    return Task(
        description="\n".join(parts),
        expected_output=_EXPECTED_OUTPUT[7],
        agent=agent,
        output_pydantic=AGENT_OUTPUT_MODELS[7],
    )
