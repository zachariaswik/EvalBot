from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = PROJECT_ROOT
COURSE_DOCS_DIR = PROJECT_ROOT / "CourseDocs"
DB_PATH = PROJECT_ROOT / "evalbot.db"

MAX_ITERATIONS = 18  # Safety limit: 3x the 6 agents in the loop

# ---------------------------------------------------------------------------
# LLM Configuration
# ---------------------------------------------------------------------------
# Supported model string formats (CrewAI uses litellm under the hood):
#   "gpt-4o"                        — OpenAI  (needs OPENAI_API_KEY)
#   "gemini/gemini-2.0-flash"       — Google   (needs GEMINI_API_KEY, free tier)
#   "ollama/qwen3:4b"               — Ollama   (local, free, needs ollama running)
#   "ollama/llama3.2"               — Ollama   (local, free)
#   "groq/llama-3.3-70b-versatile"  — Groq     (needs GROQ_API_KEY, free tier)
#   "anthropic/claude-sonnet-4-20250514"  — Anthropic (needs ANTHROPIC_API_KEY)
#
# Set GEMINI_API_KEY for free: https://aistudio.google.com/apikey
# ---------------------------------------------------------------------------

# Default model — used when no per-agent override is set
DEFAULT_MODEL = "ollama/qwen3:4b"

# Model used for re-runs (when a downstream agent triggers a re-run of an
# earlier agent). Set to None to reuse the same model the agent normally uses.
RERUN_MODEL: str | None = None

# Per-agent model overrides. Set to a model string to override DEFAULT_MODEL.
# None means "use DEFAULT_MODEL".
AGENT_MODELS: dict[int, str | None] = {
    1: None,   # Intake Parser
    2: None,   # Venture Analyst
    3: None,   # Market & Competition Analyst
    4: None,   # Product & Positioning Analyst
    5: None,   # Founder Fit Analyst
    6: None,   # Recommendation / Pivot Agent
    7: None,   # Ranking Committee Agent
}


def get_model_for_agent(agent_number: int, is_rerun: bool = False) -> str:
    """Resolve which LLM model string to use for a given agent.

    Priority order:
    1. RERUN_MODEL (if is_rerun=True and RERUN_MODEL is set)
    2. AGENT_MODELS[agent_number] (per-agent override)
    3. DEFAULT_MODEL (fallback)
    """
    if is_rerun and RERUN_MODEL:
        return RERUN_MODEL
    return AGENT_MODELS.get(agent_number) or DEFAULT_MODEL
