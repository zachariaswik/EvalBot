from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = PROJECT_ROOT
COURSE_DOCS_DIR = PROJECT_ROOT / "CourseDocs"
DB_PATH = PROJECT_ROOT / "evalbot.db"

MAX_ITERATIONS = 18  # Safety limit: 3x the 6 agents in the loop

# ---------------------------------------------------------------------------
# Intake Quality Gate
# ---------------------------------------------------------------------------
CRITICAL_FIELDS = ["problem", "solution", "target_customer", "market", "business_model", "team"]
QUALITY_GATE_THRESHOLD = 3  # Warn if >= this many critical fields are missing

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
DEFAULT_MODEL = "openai/gpt-4o-mini"

# Context window size for Ollama models (default 4096 is too small for our prompts).
# Only applies to ollama/ models. Set to 0 to use the model's default.
OLLAMA_NUM_CTX = 16384

# Timeout in seconds for LLM requests. Set to None to disable (calls run to completion).
# Connection errors fail fast naturally (seconds), so a short timeout isn't needed to
# detect hangs. Exponential backoff handles retries. Use AGENT_TIMEOUT as a safety net
# for runaway agents, or TOTAL_STARTUP_TIMEOUT as a per-startup budget.
LLM_TIMEOUT = None  # No timeout - slow-but-working calls complete naturally

# Hard timeout in seconds for each agent's total execution. Set to None to disable.
# If an agent exceeds this limit, the pipeline falls back to gpt-4o-mini or gpt-4o.
AGENT_TIMEOUT = 420  # 7 minutes

# Total wall-clock time budget for processing one startup across all agents.
# After this limit, the startup is marked as failed and stored for re-running.
TOTAL_STARTUP_TIMEOUT = 960  # 16 minutes

# Model used for re-runs (when a downstream agent triggers a re-run of an
# earlier agent). Set to None to reuse the same model the agent normally uses.
RERUN_MODEL: str | None = None

# Per-agent model overrides. Set to a model string to override DEFAULT_MODEL.
# None means "use DEFAULT_MODEL".
AGENT_MODELS: dict[int, str | None] = {
    1: "openai/gpt-4o",                           # Intake Parser (PDF + visual context)
    2: "minimax/MiniMax-M2.7",                    # Venture Analyst
    3: "minimax/MiniMax-M2.7",                    # Market & Competition Analyst
    4: "minimax/MiniMax-M2.7",                    # Product & Positioning Analyst
    5: "minimax/MiniMax-M2.7",                    # Founder Fit Analyst
    6: "minimax/MiniMax-M2.7",                    # Recommendation / Pivot Agent
    7: "minimax/MiniMax-M2.7",                    # Ranking Committee Agent
}

# ---------------------------------------------------------------------------
# Retry & Fallback Configuration
# ---------------------------------------------------------------------------
# Automatic retry and fallback when primary model fails (e.g., connection errors)

# Number of retry attempts before falling back to secondary model
RETRY_ATTEMPTS = 5  # 5 retries with exponential backoff

# Delay between retries (seconds). Uses exponential backoff: 2, 4, 8, 16, 32, ...
RETRY_BASE_DELAY = 2

# Fallback model to use when primary model fails after retries
# Can be a single model string or a dict mapping agent_number → fallback model
# Set to None to disable fallback (will raise error instead)
FALLBACK_MODEL = "openai/gpt-4o-mini"  # Global default (fast, reliable)

# Per-agent fallback overrides. Agents not listed use FALLBACK_MODEL above.
# Agents 2 and 6 need higher reasoning quality when MiniMax fails.
AGENT_FALLBACK_MODELS: dict[int, str] = {
    2: "openai/gpt-4o",   # Venture Analyst - critical scoring decisions
    6: "openai/gpt-4o",   # Recommendations - strategic synthesis
}

# After this many successful fallback executions, try switching back to primary
RECOVERY_CHECK_INTERVAL = 3

# Cooldown period (seconds) before attempting to switch back to primary model
RECOVERY_COOLDOWN = 60

# ---------------------------------------------------------------------------
# Hall of Fame Configuration (legacy feature)
# ---------------------------------------------------------------------------
# Maximum number of entries to keep in the hall of fame
HALL_OF_FAME_SIZE = 50

# Minimum weighted score required to enter the hall of fame (0-100 scale)
HALL_OF_FAME_MIN_SCORE = 60


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


def get_fallback_model_for_agent(agent_number: int) -> str:
    """Resolve which fallback model to use for a given agent.

    Priority order:
    1. AGENT_FALLBACK_MODELS[agent_number] (per-agent fallback override)
    2. FALLBACK_MODEL (global fallback)
    """
    return AGENT_FALLBACK_MODELS.get(agent_number) or FALLBACK_MODEL
