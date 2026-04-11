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
