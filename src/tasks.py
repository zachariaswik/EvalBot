"""Factory for creating CrewAI Tasks with structured Pydantic output."""

from __future__ import annotations

import json
import re
from pathlib import Path
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


def _json_only_instruction(agent_number: int) -> str:
    """Return a strict JSON-only output instruction tailored to the agent schema."""
    model = AGENT_OUTPUT_MODELS[agent_number]
    required_fields = [
        name for name, info in model.model_fields.items() if info.is_required()
    ]
    optional_fields = [
        name for name, info in model.model_fields.items() if not info.is_required()
    ]
    required = ", ".join(required_fields)
    optional = ", ".join(optional_fields)
    return (
        "\n\nOUTPUT FORMAT REQUIREMENT:\n"
        "Return ONLY one valid JSON object.\n"
        "Do NOT include markdown, headings, tables, code fences, or explanatory prose.\n"
        f"Required top-level keys: {required}.\n"
        f"Optional keys (include only when relevant): {optional}.\n"
        "Use exact enum values where applicable.\n"
    )


def _extract_pdf_paths(text: str) -> list[str]:
    """Extract PDF file paths from [PDF_FILE: ...] markers in text."""
    pattern = r'\[PDF_FILE:\s*([^\]]+)\]'
    matches = re.findall(pattern, text)
    return [m.strip() for m in matches]


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
    """Create a CrewAI Task for the given agent with structured Pydantic output.
    
    For Agent 1, if submission_text contains [PDF_FILE: ...] markers, extracts
    the PDF paths and passes them via the input_files parameter for direct reading.
    """
    description = _build_description(agent_number, submission_text, prior_context, feedback_reason)
    description += _json_only_instruction(agent_number)
    output_model = AGENT_OUTPUT_MODELS[agent_number]
    
    # Extract PDF file paths if present (Agent 1 can read PDFs directly)
    pdf_paths = _extract_pdf_paths(submission_text) if agent_number == 1 else []
    
    task_params = {
        "description": description,
        "expected_output": _EXPECTED_OUTPUT[agent_number],
        "agent": agent,
        "output_pydantic": output_model,
    }
    
    # Add input_files if we have PDFs
    if pdf_paths:
        task_params["input_files"] = pdf_paths
    
    return Task(**task_params)


def create_agent0_task(
    agent: Agent,
    constraints: dict[str, Any],
    screening_feedback: dict[str, Any] | None = None,
    prior_evaluation: dict[str, Any] | None = None,
    prior_score: dict[str, Any] | None = None,
    round_number: int = 1,
    attempt_number: int = 1,
    force_completely_new_idea: bool = False,
    hall_of_fame_examples: list[dict] | None = None,
    enable_dimension_reasoning: bool = True,
    enable_hall_of_fame: bool = True,
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
        hall_of_fame_examples: Top-scoring examples from Hall of Fame to guide generation.
        enable_dimension_reasoning: Enable self-evaluation on scoring dimensions.
        enable_hall_of_fame: Enable Hall of Fame examples in prompt.
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

    # Require a rich, consistently structured submission so Agent 1 can parse all fields.
    parts.append(
        "SUBMISSION_TEXT FORMAT REQUIREMENTS (MANDATORY):\n"
        "Your `submission_text` must be a complete startup brief with ALL sections below.\n"
        "Do not leave any section empty. Do not use placeholders like 'N/A', 'Unknown', or 'TBD'.\n"
        "Use these exact section headings in this order:\n"
        "1) Problem\n"
        "2) Solution\n"
        "3) Target Customer\n"
        "4) Buyer\n"
        "5) Market\n"
        "6) Business Model\n"
        "7) Competitors\n"
        "8) Traction\n"
        "9) Team\n"
        "10) Why Now\n"
        "11) Vision\n"
        "12) Unfair Advantage\n"
        "13) Risks\n\n"
        "Quality bar per section:\n"
        "- Provide concrete, startup-specific details (not generic statements).\n"
        "- Use at least 1-2 full sentences per section.\n"
        "- Ensure Buyer can differ from Target Customer when relevant.\n"
        "- Include at least one clear competitor/alternative in Competitors.\n"
        "- If traction is pre-launch, still provide a realistic traction plan or early evidence.\n"
    )

    # Hall of Fame Examples - Top-scoring ideas to guide generation
    if enable_hall_of_fame and hall_of_fame_examples:
        parts.append(
            "\n\n📚 HALL OF FAME EXAMPLES - Top-Scoring Startup Ideas:\n"
            "The following are examples of successful startup ideas that scored well.\n"
            "Use these as inspiration for what 'great' looks like.\n\n"
        )
        for i, example in enumerate(hall_of_fame_examples, 1):
            a0 = example.get("agent0_output", {})
            a2 = example.get("agent2_output", {})
            parts.append(f"--- Example {i} (Score: {example.get('weighted_score', 'N/A')}/80) ---")
            parts.append(f"Name: {a0.get('startup_name', 'Unknown')}")
            parts.append(f"One-line: {a0.get('one_line_description', 'N/A')}")
            parts.append(f"Problem: {a0.get('submission_text', '')[:200]}...")
            parts.append(f"Verdict: {a2.get('verdict', 'N/A')}")
            parts.append("")
        
        parts.append(
            "\n💡 Use these examples as inspiration for what makes a strong startup idea.\n"
            "Learn from their approach to problem, solution, market, and differentiation.\n"
        )

    # Explicit Dimension Reasoning - Force self-evaluation before submission
    # This helps catch oversights and improves idea quality
    if enable_dimension_reasoning:
        parts.append(
            "\n\nSELF-EVALUATION REQUIREMENT (DIMENSION REASONING):\n"
            "Before finalizing your submission, evaluate your idea on each dimension below.\n"
            "Provide a self-score (1-10) and brief reasoning for each. Be honest and critical.\n"
            "This self-evaluation helps you catch weaknesses before submission.\n\n"
            "Dimensions to evaluate:\n"
            "- problem_severity: How severe is the problem? Is it a real pain point?\n"
            "- market_size: How large is the target market? Is it venture-scale?\n"
            "- differentiation: How unique is the solution? What's the wedge?\n"
            "- customer_clarity: How clear is the target customer? Who pays?\n"
            "- founder_insight: How deep is the founder's understanding of the problem?\n"
            "- business_model: How will the startup make money? Is it sustainable?\n"
            "- moat_potential: What protects against competitors? Any unfair advantage?\n"
            "- venture_potential: Is this venture-scale? Could it become a billion-dollar company?\n\n"
            "Include your self-evaluation in the `dimension_reasoning` field of your output.\n"
        )

    description = "\n".join(parts) + _json_only_instruction(0)

    return Task(
        description=description,
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

    description = "\n".join(parts) + _json_only_instruction(7)

    return Task(
        description=description,
        expected_output=_EXPECTED_OUTPUT[7],
        agent=agent,
        output_pydantic=AGENT_OUTPUT_MODELS[7],
    )
