# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

EvalBot is a multi-agent AI system that evaluates early-stage startup submissions. It runs 7 specialized CrewAI agents sequentially on each startup pitch, producing structured scores, verdicts, SWOT analyses, and strategic recommendations.

## Testing

All new code must be tested and all tests must pass before committing. Tests run without API keys — external dependencies (crewai, pdfplumber) are mocked in `tests/conftest.py`.

```bash
# Run the full test suite
source .venv313/bin/activate
pytest

# Run a single test file
pytest tests/test_db.py

# Run a single test by name
pytest tests/test_retry_utils.py::TestExecuteWithRetry::test_success_on_first_attempt -v
```

**When adding new features**: add tests alongside the code change. When a new `src/` module is created, create a corresponding `tests/test_<module>.py`. When adding new constants, functions, or edge-case handling, extend the relevant test file.

**Coverage by file:**

| Test file | Covers |
|-----------|--------|
| `tests/test_config.py` | Model resolution, fallback selection, constants |
| `tests/test_models.py` | All 7 Pydantic output schemas, enums, validation |
| `tests/test_db.py` | All SQLite operations incl. hall of fame and retry log |
| `tests/test_docs.py` | Document loading (text, PDF markers, DOCX, directories) |
| `tests/test_tasks.py` | Task description building, PDF extraction, task factory |
| `tests/test_agents.py` | Agent metadata, prompt loading, agent factory |
| `tests/test_retry_utils.py` | Retry logic, fallback, timeout, error classification |

## Running the Project

```bash
# Activate the Python 3.13 venv (required — CrewAI is incompatible with 3.14+)
source .venv313/bin/activate

# Process a single submission (text/PDF/DOCX)
python main.py single path/to/submission.txt

# Process a batch directory
python main.py batch path/to/Startups/

# Long-running commands: pipe through tee
python main.py batch path/to/Startups/ 2>&1 | tee output.log
```

Input batch structure:
```
Startups/
├── Company1/
│   ├── pitch.pdf
│   └── notes.md
├── Company2/
│   └── submission.txt
```

## Architecture

### Agent Pipeline (`src/pipeline.py`)

7 agents run sequentially per startup:

1. **Agent 1 – Intake Parser**: Extracts structured fields (problem, solution, team, market, etc.) from raw text/PDF/DOCX
2. **Agent 2 – Unified Venture Analyst**: Scores 10 dimensions (1–10), assigns verdict, produces SWOT
3. **Agent 3 – Market & Competition Analyst**: TAM/SAM/SOM, competitive landscape
4. **Agent 4 – Product & Positioning Analyst**: Feature-vs-company assessment, AI wrapper risk
5. **Agent 5 – Founder Fit Analyst**: Team assessment, execution confidence
6. **Agent 6 – Recommendation Agent**: Pivot options, 30/90-day action plans
7. **Agent 7 – Ranking Committee**: Comparative ranking across a batch (batch mode only)

Each agent's system prompt lives in `Agent{N}/prompt.md`.

**Feedback loop**: Agents 2–6 can request a re-run from an earlier agent if they detect insufficient data. The pipeline invalidates downstream outputs and re-executes from the requested agent. Maximum 18 iterations total.

### Key Source Files

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point; single/batch modes; file loading; results export |
| `src/pipeline.py` | Core orchestration; sequential agent execution; feedback loop logic |
| `src/config.py` | Per-agent model assignment, retry/fallback settings, timeouts |
| `src/models.py` | Pydantic output schemas for all 7 agents; `FeedbackMixin` for re-run requests |
| `src/agents.py` | CrewAI agent factory; loads prompts from `Agent{N}/prompt.md` |
| `src/tasks.py` | CrewAI task creation with structured outputs |
| `src/retry_utils.py` | Exponential backoff, fallback models, primary-model recovery logic |
| `src/db.py` | SQLite schema and all persistence operations |
| `src/docs.py` | Document loading — PDFs passed as file refs, DOCX text extracted |

### LLM Configuration (`src/config.py`)

Models are configured per-agent via `AGENT_MODELS`. The default fallback is `openai/gpt-4o-mini`. All providers are accessed through LiteLLM (prefix format: `openai/...`, `anthropic/...`, `minimax/...`, etc.).

Retry behavior: exponential backoff (2s base, 5 attempts), automatic fallback to `FALLBACK_MODEL` on repeated failures, with recovery back to primary after `RECOVERY_CHECK_INTERVAL` successes.

### Output Structure

```
output/Batch/batch_N/
├── StartupName/
│   ├── StartupName.json     # All agent outputs + metadata + token usage
│   └── StartupName.md       # Human-readable report
├── ranking.json             # Agent 7 output (batch only)
└── batch_summary.md         # Model usage, costs, retry stats
```

### Database (SQLite `evalbot.db`)

Tables: `batches`, `startups`, `agent_outputs` (with iteration tracking), `feedback_log`, `retry_log`, `hall_of_fame`.

## Environment

API keys go in `.env`:
```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
MINIMAX_API_KEY=...
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

The `.gitignore` excludes `.env`, `*.db`, `output/`, `Startups/`, and `*.log`.

## Deployment (DigitalOcean — 167.99.43.130)

**SSH alias** (configured in `~/.ssh/config` on local machine):
```bash
ssh evalbot          # connects as root@167.99.43.130 using ~/.ssh/digitalOcean1
```

**Server layout:**
- App: `/opt/evalbot/` (git clone of this repo)
- Venv: `/opt/evalbot/.venv/` (Python 3.12)
- API keys: `/opt/evalbot/.env` (never committed — fill in manually after clone)
- Inputs: `/opt/evalbot/Startups/` (upload batch dirs here)
- Outputs: `/opt/evalbot/output/`

**Deploy updates** (pull code + install deps + run tests):
```bash
ssh evalbot "bash /opt/evalbot/deploy.sh"
```

**Run a batch from the server:**
```bash
ssh evalbot
cd /opt/evalbot
source .venv/bin/activate
python main.py batch Startups/ 2>&1 | tee output.log
```

**Adding a cron job** (future — runs batch nightly at 2 AM):
```bash
# On the server:
crontab -e
# Add:  0 2 * * * cd /opt/evalbot && .venv/bin/python main.py batch Startups/ >> /var/log/evalbot.log 2>&1
```

**Note on `requirements.txt`**: generated from the local `.venv313` and committed to the repo. When adding new packages locally, regenerate with:
```bash
source .venv313/bin/activate && pip freeze > requirements.txt
```

## Python Version

Python 3.13 is required. `main.py` auto-relaunches with `.venv313/bin/python` if Python 3.14+ is detected.
