"""Factory for creating CrewAI Agents from prompt.md files."""

from __future__ import annotations

from crewai import Agent, LLM

from .config import AGENTS_DIR, LLM_TIMEOUT, OLLAMA_NUM_CTX, get_model_for_agent

# Agent metadata: number -> (role, goal)
_AGENT_META: dict[int, tuple[str, str]] = {
    0: ("Startup Idea Generator", "Generate a startup idea optimized to score well in venture evaluation"),
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


def _ensure_ollama_context(model_name: str) -> str:
    """For Ollama models, create a variant with a larger context window.

    Ollama defaults to 4096 tokens which is too small for our prompts.
    We create a model alias (e.g. qwen3:4b -> qwen3:4b-32k) with the
    desired num_ctx baked into its Modelfile.

    Returns the model name to use (may be the variant name).
    """
    if not model_name.startswith("ollama/") or not OLLAMA_NUM_CTX:
        return model_name

    import subprocess

    base_model = model_name.removeprefix("ollama/")
    variant = f"{base_model}-{OLLAMA_NUM_CTX // 1024}k"

    # Check if variant already exists
    result = subprocess.run(
        ["ollama", "show", variant],
        capture_output=True, text=True,
    )
    if result.returncode == 0:
        return f"ollama/{variant}"

    # Create variant with larger context via temp Modelfile
    import tempfile
    modelfile_content = f"FROM {base_model}\nPARAMETER num_ctx {OLLAMA_NUM_CTX}\n"
    print(f"  Creating Ollama variant '{variant}' with num_ctx={OLLAMA_NUM_CTX}...")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".Modelfile", delete=False) as f:
        f.write(modelfile_content)
        tmppath = f.name
    try:
        result = subprocess.run(
            ["ollama", "create", variant, "-f", tmppath],
            capture_output=True, text=True,
        )
    finally:
        import os
        os.unlink(tmppath)
    if result.returncode != 0:
        print(f"  WARNING: Could not create Ollama variant: {result.stderr}")
        return model_name  # Fall back to original

    print(f"  Created '{variant}' successfully.")
    return f"ollama/{variant}"


# Cache resolved model names so we only create variants once
_resolved_models: dict[str, str] = {}


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
        # Ensure Ollama models have sufficient context window
        if model_name not in _resolved_models:
            _resolved_models[model_name] = _ensure_ollama_context(model_name)
        resolved = _resolved_models[model_name]
        llm = LLM(model=resolved, timeout=LLM_TIMEOUT)
    return Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        llm=llm,
        verbose=True,
    )
