"""Tests for src/tasks.py — CrewAI task construction."""

from __future__ import annotations

import json

import pytest

# conftest.py has already installed the crewai mock into sys.modules
from src.tasks import (
    _build_description,
    _extract_pdf_paths,
    _json_only_instruction,
    _summarize_agent_output,
    create_ranking_task,
    create_task,
)
from src.models import AGENT_OUTPUT_MODELS


# ---------------------------------------------------------------------------
# _extract_pdf_paths
# ---------------------------------------------------------------------------

class TestExtractPdfPaths:
    def test_empty_string(self):
        assert _extract_pdf_paths("") == []

    def test_no_markers(self):
        assert _extract_pdf_paths("No PDFs here at all.") == []

    def test_single_marker(self):
        text = "Check this [PDF_FILE: /path/to/deck.pdf] out."
        result = _extract_pdf_paths(text)
        assert result == ["/path/to/deck.pdf"]

    def test_multiple_markers(self):
        text = "[PDF_FILE: /a/b.pdf] and [PDF_FILE: /c/d.pdf]"
        result = _extract_pdf_paths(text)
        assert result == ["/a/b.pdf", "/c/d.pdf"]

    def test_whitespace_trimmed(self):
        text = "[PDF_FILE:   /path/to/file.pdf   ]"
        result = _extract_pdf_paths(text)
        assert result == ["/path/to/file.pdf"]

    def test_path_with_spaces(self):
        text = "[PDF_FILE: /my docs/deck.pdf]"
        result = _extract_pdf_paths(text)
        assert result == ["/my docs/deck.pdf"]


# ---------------------------------------------------------------------------
# _json_only_instruction
# ---------------------------------------------------------------------------

class TestJsonOnlyInstruction:
    def test_contains_output_format_header(self):
        result = _json_only_instruction(1)
        assert "OUTPUT FORMAT REQUIREMENT" in result

    def test_no_markdown_instruction(self):
        result = _json_only_instruction(1)
        assert "markdown" in result.lower()

    def test_agent1_required_fields(self):
        result = _json_only_instruction(1)
        # Agent1Output has no required fields (all have defaults), but optional ones
        # should still be mentioned
        assert "Optional keys" in result

    def test_agent2_mentions_required_fields(self):
        result = _json_only_instruction(2)
        # Agent2Output has required fields with no defaults (checked via model_fields)
        # All fields happen to have defaults; instruction should mention them
        assert "Optional keys" in result

    def test_agent3_required_fields_present(self):
        from src.models import Agent3Output
        result = _json_only_instruction(3)
        # All Agent3Output fields are required (no defaults)
        assert "market_category" in result
        assert "Required top-level keys:" in result

    def test_all_agents_produce_non_empty_instruction(self):
        for agent_num in range(1, 8):
            instruction = _json_only_instruction(agent_num)
            assert len(instruction) > 50


# ---------------------------------------------------------------------------
# _build_description
# ---------------------------------------------------------------------------

class TestBuildDescription:
    def test_agent1_contains_submission(self):
        desc = _build_description(1, "My startup pitch", None)
        assert "My startup pitch" in desc

    def test_agent1_no_prior_context(self):
        desc = _build_description(1, "pitch text", None)
        # Agent 1 doesn't mention prior outputs
        assert "PRIOR AGENT OUTPUTS" not in desc

    def test_agent2_includes_prior_context(self):
        prior = {1: {"startup_name": "Acme", "problem": "Waste"}}
        desc = _build_description(2, "pitch", prior)
        assert "Acme" in desc
        assert "Agent 1" in desc

    def test_agent2_includes_submission(self):
        prior = {1: {"startup_name": "Acme"}}
        desc = _build_description(2, "original pitch text", prior)
        assert "original pitch text" in desc

    def test_no_rerun_label(self):
        desc = _build_description(1, "pitch", None)
        assert "RE-RUN" not in desc

    def test_no_feedback_loop_instruction(self):
        for agent_num in range(1, 8):
            prior = {i: {} for i in range(1, agent_num)}
            desc = _build_description(agent_num, "pitch", prior)
            assert "FEEDBACK LOOP INSTRUCTION" not in desc

    def test_prior_context_sorted_by_agent_number(self):
        prior = {3: {"c": 3}, 1: {"a": 1}, 2: {"b": 2}}
        desc = _build_description(4, "pitch", prior)
        # Agent 1 should appear before Agent 3
        assert desc.index("Agent 1") < desc.index("Agent 3")


# ---------------------------------------------------------------------------
# create_task
# ---------------------------------------------------------------------------

class TestCreateTask:
    def _make_agent(self):
        from conftest import _MockAgent
        return _MockAgent(role="Test", goal="Test")

    def test_returns_task_object(self):
        from tests.conftest import _MockAgent, _MockTask
        import crewai
        agent = crewai.Agent(role="Test", goal="Test", backstory="")
        task = create_task(1, agent, "startup pitch text")
        assert isinstance(task, crewai.Task)

    def test_task_has_description(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        task = create_task(1, agent, "my pitch")
        assert "my pitch" in task.description

    def test_task_output_pydantic_set(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        task = create_task(2, agent, "my pitch", prior_context={1: {"problem": "pain"}})
        assert task.output_pydantic is AGENT_OUTPUT_MODELS[2]

    def test_task_with_pdf_sets_input_files(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        submission = "[PDF_FILE: /tmp/deck.pdf]"
        task = create_task(1, agent, submission)
        assert task.input_files is not None
        assert len(task.input_files) == 1

    def test_task_without_pdf_no_input_files(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        task = create_task(1, agent, "plain text submission with no pdfs")
        assert not task.input_files  # None or empty

    def test_agent7_task_has_correct_output_model(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        # Agent 7 uses create_ranking_task, but create_task(7) should also work
        task = create_task(7, agent, "data", prior_context={1: {}})
        assert task.output_pydantic is AGENT_OUTPUT_MODELS[7]


# ---------------------------------------------------------------------------
# create_ranking_task
# ---------------------------------------------------------------------------

class TestCreateRankingTask:
    def test_returns_task_object(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        batch_data = [
            {"startup_name": "Alpha", "outputs": {1: {"problem": "pain"}, 2: {"verdict": "good"}}},
            {"startup_name": "Beta", "outputs": {1: {"problem": "less pain"}}},
        ]
        task = create_ranking_task(agent, batch_data)
        assert isinstance(task, crewai.Task)

    def test_description_contains_startup_names(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        batch_data = [
            {"startup_name": "AlphaVenture", "outputs": {1: {"x": 1}}},
        ]
        task = create_ranking_task(agent, batch_data)
        assert "AlphaVenture" in task.description

    def test_output_pydantic_is_agent7(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        task = create_ranking_task(agent, [])
        assert task.output_pydantic is AGENT_OUTPUT_MODELS[7]

    def test_ranking_task_uses_compact_summaries(self):
        import crewai
        agent = crewai.Agent(role="R", goal="G", backstory="")
        long_text = "x" * 1000
        batch_data = [
            {
                "startup_name": "CompactCo",
                "outputs": {
                    2: {
                        "verdict": "Top VC Candidate",
                        "total_score": 91,
                        "summary": long_text,
                        "main_risks": long_text,
                    }
                },
            }
        ]
        task = create_ranking_task(agent, batch_data)
        assert "--- Compact Evaluation Summary ---" in task.description
        assert long_text not in task.description
        assert "..." in task.description


class TestSummarizeAgentOutput:
    def test_agent2_summary_keeps_core_fields(self):
        out = {
            "verdict": "Top VC Candidate",
            "total_score": 88,
            "summary": "Strong founder-market fit and fast growth.",
            "main_risks": ["Crowded market", "Regulatory uncertainty"],
        }
        summary = _summarize_agent_output(2, out)
        assert summary["verdict"] == "Top VC Candidate"
        assert summary["total_score"] == 88
        assert "Strong founder-market fit" in summary["summary"]
