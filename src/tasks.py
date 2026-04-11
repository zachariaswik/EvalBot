"""Factory for creating CrewAI Tasks with structured Pydantic output."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from crewai import Agent, Task

from .models import AGENT_OUTPUT_MODELS

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


_RANKING_FIELD_CHAR_LIMIT = 220
_RANKING_LIST_LIMIT = 3


def _truncate_text(value: Any, max_chars: int = _RANKING_FIELD_CHAR_LIMIT) -> str:
    """Convert a value to compact text and cap length for ranking prompts."""
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    elif isinstance(value, list):
        text = "; ".join(_truncate_text(v, max_chars // 2) for v in value[:_RANKING_LIST_LIMIT])
    elif isinstance(value, dict):
        text = json.dumps(value, ensure_ascii=True, separators=(",", ":"), default=str)
    else:
        text = str(value)
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3] + "..."


def _summarize_agent_output(agent_number: int, output: Any) -> dict[str, Any]:
    """Build a compact, ranking-focused summary of one agent output."""
    if not isinstance(output, dict):
        return {"summary": _truncate_text(output)}

    if agent_number == 1:
        return {
            "one_line_description": _truncate_text(output.get("one_line_description")),
            "problem": _truncate_text(output.get("problem")),
            "solution": _truncate_text(output.get("solution")),
            "target_customer": _truncate_text(output.get("target_customer")),
            "business_model": _truncate_text(output.get("business_model")),
            "traction": _truncate_text(output.get("traction")),
            "team": _truncate_text(output.get("team")),
            "clarity_score": output.get("clarity_score"),
            "missing_info": _truncate_text(output.get("missing_info")),
            "inconsistencies": _truncate_text(output.get("inconsistencies")),
        }
    if agent_number == 2:
        return {
            "verdict": _truncate_text(output.get("verdict")),
            "total_score": output.get("total_score"),
            "summary": _truncate_text(output.get("summary")),
            "main_risks": _truncate_text(output.get("main_risks")),
            "main_opportunities": _truncate_text(output.get("main_opportunities")),
            "explanation": _truncate_text(output.get("explanation")),
        }
    if agent_number == 3:
        return {
            "market_category": _truncate_text(output.get("market_category")),
            "size_class": _truncate_text(output.get("size_class")),
            "attractiveness_score": output.get("attractiveness_score"),
            "competition_score": output.get("competition_score"),
            "trend": _truncate_text(output.get("trend")),
            "wedge": _truncate_text(output.get("wedge")),
            "conclusion": _truncate_text(output.get("conclusion")),
        }
    if agent_number == 4:
        return {
            "feature_vs_company": _truncate_text(output.get("feature_vs_company")),
            "wrapper_risk": _truncate_text(output.get("wrapper_risk")),
            "value_prop": _truncate_text(output.get("value_prop")),
            "wedge": _truncate_text(output.get("wedge")),
            "moat": _truncate_text(output.get("moat")),
            "positioning": _truncate_text(output.get("positioning")),
            "six_month_focus": _truncate_text(output.get("six_month_focus")),
        }
    if agent_number == 5:
        return {
            "fit_score": output.get("fit_score"),
            "execution_score": output.get("execution_score"),
            "founder_fit": _truncate_text(output.get("founder_fit")),
            "domain": _truncate_text(output.get("domain")),
            "risks": _truncate_text(output.get("risks")),
            "missing_roles": _truncate_text(output.get("missing_roles")),
            "conclusion": _truncate_text(output.get("conclusion")),
        }
    if agent_number == 6:
        return {
            "recommendation": _truncate_text(output.get("recommendation")),
            "customer_segment": _truncate_text(output.get("customer_segment")),
            "wedge": _truncate_text(output.get("wedge")),
            "emphasize": _truncate_text(output.get("emphasize")),
            "remove": _truncate_text(output.get("remove")),
            "pivots": _truncate_text(output.get("pivots")),
            "positioning_rewrite": _truncate_text(output.get("positioning_rewrite")),
            "mistake_to_avoid": _truncate_text(output.get("mistake_to_avoid")),
        }

    compact_items = list(output.items())[:8]
    return {k: _truncate_text(v) for k, v in compact_items}


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
) -> str:
    """Build the task description for a given agent."""
    parts: list[str] = []

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

    return "\n".join(parts)


def create_task(
    agent_number: int,
    agent: Agent,
    submission_text: str,
    prior_context: dict[int, Any] | None = None,
) -> Task:
    """Create a CrewAI Task for the given agent with structured Pydantic output.

    For Agent 1, if submission_text contains [PDF_FILE: ...] markers, extracts
    the PDF paths and passes them via the input_files parameter for direct reading.
    """
    description = _build_description(agent_number, submission_text, prior_context)
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
    # CrewAI expects input_files as dict[str, Any], not list
    if pdf_paths:
        task_params["input_files"] = {
            f"document_{i}": path for i, path in enumerate(pdf_paths)
        }
    
    return Task(**task_params)


def create_ranking_task(
    agent: Agent,
    batch_data: list[dict],
) -> Task:
    """Create the Agent 7 ranking task from accumulated batch data."""
    parts = [
        "Rank the following startups relative to each other.\n",
        "Use the compact per-agent summaries below (not full raw outputs) to compare each startup consistently.\n",
    ]
    for entry in batch_data:
        name = entry["startup_name"]
        outputs = entry["outputs"]
        compact_outputs = {
            num: _summarize_agent_output(num, outputs[num]) for num in sorted(outputs.keys())
        }
        parts.append(f"\n{'='*60}\nSTARTUP: {name}\n{'='*60}\n")
        parts.append(
            f"\n--- Compact Evaluation Summary ---\n{json.dumps(compact_outputs, indent=2, default=str)}\n"
        )

    description = "\n".join(parts) + _json_only_instruction(7)

    return Task(
        description=description,
        expected_output=_EXPECTED_OUTPUT[7],
        agent=agent,
        output_pydantic=AGENT_OUTPUT_MODELS[7],
    )
