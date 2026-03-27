"""Factory for creating CrewAI Agents from prompt.md files."""

from __future__ import annotations

from crewai import Agent, LLM

from .config import AGENTS_DIR, get_model_for_agent

# Agent metadata: number -> (role, goal)
_AGENT_META: dict[int, tuple[str, str]] = {
    1: ("Intake Parser", "Convert raw startup submissions into a clean, standardized startup brief"),
    2: ("Unified Venture Analyst", "Determine whether the startup is worth pursuing as a venture-scale company"),
    3: ("Market & Competition Analyst", "Assess market attractiveness and competitive landscape"),
    4: ("Product & Positioning Analyst", "Determine whether the startup has a real product opportunity"),
    5: ("Founder Fit Analyst", "Assess whether the founders are well positioned to build this company"),
    6: ("Recommendation / Pivot Agent", "Convert analysis into practical next steps and recommendations"),
    7: ("Ranking Committee Agent", "Rank startups relative to each other within a cohort"),
}


def _load_prompt(agent_number: int) -> str:
    path = AGENTS_DIR / f"Agent{agent_number}" / "prompt.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    return path.read_text(encoding="utf-8")


def create_agent(
    agent_number: int,
    llm: LLM | None = None,
    is_rerun: bool = False,
) -> Agent:
    """Create a CrewAI Agent from its prompt.md file.

    Args:
        agent_number: Which agent (1-7).
        llm: Explicit LLM override. If None, resolved from config
             using get_model_for_agent().
        is_rerun: If True (feedback-loop re-run), config may select
                  a different model via RERUN_MODEL.
    """
    role, goal = _AGENT_META[agent_number]
    backstory = _load_prompt(agent_number)
    if llm is None:
        model_name = get_model_for_agent(agent_number, is_rerun=is_rerun)
        llm = LLM(model=model_name)
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm,
        verbose=True,
    )
