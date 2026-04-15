# EvalBot — AI-Powered Startup Evaluation Pipeline

EvalBot is a multi-agent AI system that evaluates early-stage startup submissions through a structured pipeline. Each agent specializes in one aspect of venture analysis (intake parsing, venture scoring, market analysis, product positioning, founder fit, and strategic recommendations), producing comprehensive evaluation reports with actionable insights.

## What It Does

EvalBot analyzes startup submissions and provides:

- **Structured scoring** across 10 venture-critical dimensions
- **Verdict classification** (Top VC Candidate, Promising, Small Business, Feature Not Company, etc.)
- **SWOT analysis** with market, product, and founder assessments
- **Strategic recommendations** including pivot options and 30/90-day action plans
- **Batch ranking** when evaluating multiple startups together
- **Professional reports** in JSON and Markdown formats
- **Web UI** for browsing results and running batches

## Architecture

### Multi-Agent Pipeline

EvalBot uses **7 specialized agents** that run sequentially:

1. **Intake Parser** (Agent 1) — Converts raw submissions into standardized JSON structure
2. **Venture Analyst** (Agent 2) — Core scoring: evaluates 10 dimensions (1-10 scale), produces verdict
3. **Market & Competition Analyst** (Agent 3) — Market dynamics, TAM/SAM/SOM, competitive landscape
4. **Product & Positioning Analyst** (Agent 4) — Feature vs company assessment, AI wrapper risk
5. **Founder Fit Analyst** (Agent 5) — Team assessment, execution confidence
6. **Recommendation Agent** (Agent 6) — Strategic synthesis with pivot options and action plans
7. **Ranking Committee** (Agent 7) — Comparative ranking across cohort (batch mode only)

### Key Features

- **PDF/DOCX Support**: Reads pitch decks, documents, and text submissions directly
- **Feedback Loop**: Agents can request re-runs from earlier agents when detecting gaps
- **Flexible LLM Backend**: Supports Anthropic, OpenAI, MiniMax, Gemini, Groq, and Ollama models
- **Automatic Retry & Fallback**: Handles API failures gracefully with configurable fallback models
- **Database Tracking**: SQLite database stores all outputs, iterations, and feedback events
- **Web UI**: Reflex-based dashboard for browsing batches, startup reports, and running new evaluations

## Web Interface

A full-featured web UI is available at **http://167.99.43.130** (internal access only).

### Pages

| Route | Description |
|---|---|
| `/` | Dashboard — all batches, stats, top startups |
| `/batch/[batch_id]` | Batch leaderboard — scores, verdict distribution, shortlist |
| `/batch/[batch_id]/[startup_name]` | Startup detail — radar chart, SWOT, analyst tabs, PDF feedback download |
| `/run` | Run Batch — upload submissions, monitor live progress |
| `/roadmap` | Feature roadmap |

### Running the Frontend Locally

```bash
source .venv313/bin/activate

# First time only — downloads Node/React dependencies
reflex init

# Start the dev server
reflex run
# → Open http://localhost:3000
```

For production (managed by systemd on the server):
```bash
reflex run --env prod --loglevel warning
```

## Quick Start

### Prerequisites

- **Python 3.13 or earlier** (CrewAI is incompatible with Python 3.14+)
- API key for at least one provider (Anthropic, OpenAI, or MiniMax recommended)
- **Node.js** (required by Reflex for the web UI — installed automatically by `reflex init`)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd EvalBot

# Create virtual environment (Python 3.13 or earlier)
python3.13 -m venv .venv313
source .venv313/bin/activate  # or .venv313\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Set up API keys
cp .env.example .env
# Edit .env and add your API key(s)

# Initialize Reflex (first time only)
reflex init
```

### Environment Variables

Create a `.env` file in the project root:

```bash
# At least one of these is required:
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
MINIMAX_API_KEY=your_key_here

# Optional providers:
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

## Usage

### Process a Single Startup

```bash
source .venv313/bin/activate

# From a text file
python main.py single path/to/submission.txt

# From a PDF pitch deck
python main.py single path/to/deck.pdf

# From a Word document
python main.py single path/to/pitch.docx
```

### Process a Batch of Startups

```bash
# Process all startups in a directory and rank them
python main.py batch path/to/startups_folder

# Long-running batches: pipe through tee to capture output
python main.py batch Startups/ 2>&1 | tee output.log
```

**Batch directory structure:**

```
Startups/
├── Company1/
│   ├── pitch.pdf
│   └── notes.md
├── Company2/
│   └── submission.txt
└── Company3/
    └── deck.docx
```

Supported file types: `.pdf`, `.docx`, `.txt`, `.md`

### Via the Web UI

1. Go to `/run`
2. Enter a startup name and upload its files
3. Repeat for each startup in the batch
4. Click **Run Batch** — progress streams live in the terminal monitor
5. When complete, click **View Results** to open the batch leaderboard
6. Open a startup page and click **Download PDF** to export the full EvalBot feedback report

## Output Structure

Results are saved to `output/Batch/batch_N/`:

```
output/
└── Batch/
    └── batch_1/
        ├── Startup1/
        │   ├── Startup1.json          # Full pipeline results (all agents)
        │   └── Startup1.md            # Human-readable report
        ├── Startup2/
        │   ├── Startup2.json
        │   └── Startup2.md
        ├── ranking.json               # Agent 7 comparative ranking + shortlist
        └── batch_summary.md           # Model usage, costs, retry stats
```

Each startup's `.json` file contains:

```json
{
  "agent1": { /* structured intake data */ },
  "agent2": { /* scores, verdict, SWOT */ },
  "agent3": { /* market analysis */ },
  "agent4": { /* product positioning */ },
  "agent5": { /* founder fit */ },
  "agent6": { /* recommendations */ },
  "_tags": {
    "batch_id": "batch_1",
    "startup_name": "MyStartup",
    "total_iterations": 6,
    "processing_time_seconds": 142.5
  },
  "_usage": { /* token usage and costs per agent */ }
}
```

## Configuration

### Model Assignment

Edit `src/config.py` to customize which LLM models are used:

```python
DEFAULT_MODEL = "anthropic/claude-haiku-4-5"

AGENT_MODELS: dict[int, str | None] = {
    1: "gpt-4.1-nano",                      # Cheap extraction
    2: "anthropic/claude-opus-4-6",         # Best reasoning
    3: "minimax/MiniMax-M2.7",              # Good value
    4: "minimax/MiniMax-M2.7",
    5: "minimax/MiniMax-M2.7",
    6: "anthropic/claude-opus-4-6",         # Best strategic synthesis
    7: "minimax/MiniMax-M2.7",
}
```

See [`agent_models.md`](agent_models.md) for detailed model recommendations and cost profiles.

### Supported Providers

| Provider   | Model Examples                           | Cost (per 1M tokens) |
|------------|------------------------------------------|----------------------|
| Anthropic  | `anthropic/claude-opus-4-6`              | $15 / $75 (in/out)   |
|            | `anthropic/claude-sonnet-4-6`            | $3 / $15             |
|            | `anthropic/claude-haiku-4-5`             | $1 / $5              |
| OpenAI     | `gpt-4.1`, `gpt-4o`, `o3-mini`           | $2-8 / $8-44         |
|            | `gpt-4.1-mini`, `gpt-4o-mini`            | $0.15-0.40 / $0.60-1.60 |
| MiniMax    | `minimax/MiniMax-M2.7`                   | $0.30 / $1.20        |
| Gemini     | `gemini/gemini-2.0-flash`                | Free tier available  |
| Groq       | `groq/llama-3.3-70b-versatile`           | Free tier available  |
| Ollama     | `ollama/qwen3:4b`, `ollama/llama3.2`     | Free (local)         |

### Retry & Fallback

```python
# src/config.py
RETRY_ATTEMPTS = 3
RETRY_BASE_DELAY = 2          # Exponential backoff: 2s, 4s, 8s
FALLBACK_MODEL = "anthropic/claude-haiku-4-5"
RECOVERY_CHECK_INTERVAL = 3   # Successes before attempting recovery to primary
RECOVERY_COOLDOWN = 60        # Seconds before retrying primary
```

## Cost Estimates

**Single startup evaluation** (Agents 1-6):

| Config | Cost |
|---|---|
| Premium (Opus on 2 & 6, Sonnet on 3-5) | ~$0.77 |
| Balanced (Sonnet on 2 & 6, MiniMax on 3-5) | ~$0.13 |
| Budget (MiniMax across all) | ~$0.03 |

**Batch of 10 startups + ranking**: 10× single cost + ~$0.05 for Agent 7.

See [`agent_models.md`](agent_models.md) for detailed cost breakdowns.

## Project Structure

```
EvalBot/
├── agents/
│   ├── Agent1/prompt.md  # Intake Parser system prompt
│   ├── Agent2/prompt.md  # Venture Analyst system prompt
│   ├── Agent3/prompt.md  # Market & Competition Analyst
│   ├── Agent4/prompt.md  # Product & Positioning Analyst
│   ├── Agent5/prompt.md  # Founder Fit Analyst
│   ├── Agent6/prompt.md  # Recommendation Agent
│   └── Agent7/prompt.md  # Ranking Committee Agent
├── src/
│   ├── agents.py         # CrewAI agent factory
│   ├── config.py         # Model assignment, retry settings, constants
│   ├── db.py             # SQLite schema and all persistence operations
│   ├── docs.py           # Document loading (PDF/DOCX/text)
│   ├── models.py         # Pydantic output schemas for all 7 agents
│   ├── pipeline.py       # Sequential agent orchestration + feedback loop
│   ├── retry_utils.py    # Exponential backoff, fallback, recovery logic
│   └── tasks.py          # CrewAI task creation with structured outputs
├── frontend/
│   ├── frontend.py       # Reflex app entry point + page registration
│   ├── state/
│   │   ├── dashboard.py  # DashboardState — batch list, stats, top startups
│   │   ├── batch.py      # BatchState — leaderboard, charts, shortlist
│   │   ├── startup.py    # StartupState — agent outputs, radar, SWOT, tabs
│   │   └── run.py        # RunState — upload, subprocess, live progress stream
│   ├── pages/
│   │   ├── dashboard.py  # / route
│   │   ├── batch.py      # /batch/[batch_id] route
│   │   ├── startup.py    # /batch/[batch_id]/[startup_name] route
│   │   ├── run.py        # /run route
│   │   └── roadmap.py    # /roadmap route
│   └── components/
│       ├── navbar.py     # Top nav + page layout wrapper
│       ├── badges.py     # Verdict badge, score bar, status pill
│       └── charts.py     # Radar, bar, and pie chart wrappers (rx.recharts)
├── tests/
│   ├── conftest.py       # crewai/pdfplumber mocks
│   ├── test_agents.py
│   ├── test_config.py
│   ├── test_db.py
│   ├── test_docs.py
│   ├── test_frontend.py  # State helper unit tests
│   ├── test_models.py
│   ├── test_pages.py     # Page compilation + state structure tests
│   ├── test_retry_utils.py
│   └── test_tasks.py
├── deploy/
│   ├── evalbot-web.service  # systemd service file for production
│   └── nginx-evalbot.conf   # nginx reverse-proxy config
├── main.py               # CLI entry point (single / batch modes)
├── deploy.sh             # Server deployment script
├── rxconfig.py           # Reflex configuration
├── evalbot.db            # SQLite database (gitignored)
├── evalbot_run.json      # Run state persistence (survives server restarts)
├── requirements.txt      # Pinned dependencies
└── output/               # Generated results (gitignored)
```

## Development

### Running Tests

```bash
source .venv313/bin/activate
pytest                    # 253 tests, ~2s, no API keys needed
pytest tests/test_db.py   # single file
pytest -v -k "batch"      # filter by name
```

Tests cover: agent creation, config resolution, all 7 Pydantic schemas, SQLite operations, document loading, task building, retry logic, frontend state helpers, and page compilation.

### Adding/Modifying Agents

1. Create/update `agents/Agent{N}/prompt.md`
2. Define output model in `src/models.py` (`class Agent{N}Output`)
3. Add metadata to `_AGENT_META` in `src/agents.py`
4. Add expected output to `_EXPECTED_OUTPUT` in `src/tasks.py`
5. Update `AGENT_OUTPUT_MODELS` in `src/models.py`

### Updating Dependencies

```bash
source .venv313/bin/activate
pip install <new-package>
pip freeze > requirements.txt
```

## Deployment (DigitalOcean — 167.99.43.130)

```bash
# SSH alias (configured in ~/.ssh/config)
ssh evalbot   # connects as root@167.99.43.130

# Pull updates, install deps, run tests
ssh evalbot "bash /opt/evalbot/deploy.sh"

# Service management
ssh evalbot "systemctl status evalbot-web"
ssh evalbot "systemctl restart evalbot-web"
```

The web service runs as `evalbot-web` (systemd), started with:
```
reflex run --env prod --loglevel warning
```

**Note:** Reflex requires Node.js on the server. `deploy.sh` handles installation on first run.

## Advanced Features

### Feedback Loop System

Agents 2-6 can request re-runs from earlier agents when detecting insufficient information:

1. Logs the feedback request to the database
2. Invalidates downstream outputs
3. Re-runs from the requested agent with feedback context
4. Enforces a maximum iteration limit (default: 18)

```sql
-- Track feedback events
sqlite3 evalbot.db "SELECT * FROM feedback_log WHERE batch_id='batch_1';"
```

### Run State Persistence

`evalbot_run.json` persists the current run's status so the UI can detect interrupted runs after a server restart and prompt the user to start a new batch.

### Database Schema

Tables: `batches`, `startups`, `agent_outputs` (with iteration tracking), `feedback_log`, `retry_log`, `hall_of_fame`.

## Troubleshooting

### Python 3.14+ Detected

EvalBot automatically re-launches with `.venv313/bin/python` if Python 3.14+ is detected. Create the environment manually if needed:

```bash
python3.13 -m venv .venv313
source .venv313/bin/activate
pip install -r requirements.txt
```

### API Errors

The system retries automatically and falls back to `FALLBACK_MODEL`. Check retry stats in `batch_summary.md` or:

```bash
sqlite3 evalbot.db "SELECT * FROM retry_log ORDER BY timestamp DESC LIMIT 20;"
```

### Incomplete Batch

Resume from failed startups:

```bash
sqlite3 evalbot.db "SELECT startup_name FROM startups WHERE batch_id='batch_1' AND pipeline_status != 'completed';"
python main.py single Startups/FailedStartupName/
```

### Reflex / Frontend Issues

```bash
# Re-initialize if .web/ is corrupted
rm -rf .web/
reflex init
reflex run
```

## Documentation

- [`agent_models.md`](agent_models.md) — Model recommendations and cost analysis
- [`RETRY_LOGGING.md`](RETRY_LOGGING.md) — Retry and fallback system details
