# EvalBot — AI-Powered Startup Evaluation Pipeline

EvalBot is a multi-agent AI system that evaluates early-stage startup submissions through a structured pipeline. Each agent specializes in one aspect of venture analysis (intake parsing, venture scoring, market analysis, product positioning, founder fit, and strategic recommendations), producing comprehensive evaluation reports with actionable insights.

## 🎯 What It Does

EvalBot analyzes startup submissions and provides:

- **Structured scoring** across 10 venture-critical dimensions
- **Verdict classification** (Top VC Candidate, Promising, Small Business, Feature Not Company, etc.)
- **SWOT analysis** with market, product, and founder assessments
- **Strategic recommendations** including pivot options and 30/90-day action plans
- **Batch ranking** when evaluating multiple startups together
- **Professional reports** in JSON and Markdown formats

## 🏗️ Architecture

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

## 🚀 Quick Start

### Prerequisites

- **Python 3.13 or earlier** (CrewAI is incompatible with Python 3.14+)
- API key for at least one provider (Anthropic, OpenAI, or MiniMax recommended)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd EvalBot

# Create virtual environment (Python 3.13 or earlier)
python3.13 -m venv .venv313
source .venv313/bin/activate  # or .venv313\Scripts\activate on Windows

# Install dependencies
pip install crewai litellm pydantic pdfplumber python-docx PyPDF2 python-dotenv

# Set up API keys
cp .env.example .env  # Create from template
# Edit .env and add your API key(s)
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

## 📖 Usage

### Process a Single Startup

```bash
# From a text file
python main.py single path/to/submission.txt

# From a PDF pitch deck
python main.py single path/to/deck.pdf

# From a Word document
python main.py single path/to/pitch.docx

# Default: Process the built-in CourseDocs example
python main.py
```

### Process a Batch of Startups

```bash
# Process all startups in a directory and rank them
python main.py batch path/to/startups_folder
```

**Batch directory structure** (two supported formats):

```
# Option 1: Subdirectories (recommended)
Startups/
├── Company1/
│   ├── pitch.pdf
│   └── financials.xlsx
├── Company2/
│   └── submission.md
└── Company3/
    └── deck.pdf

# Option 2: Legacy flat structure
Startups/
├── company1.md
├── company2.md
└── company3.md
```

Supported file types: `.md`, `.txt`, `.pdf`, `.docx`

## 📊 Output Structure

Results are exported to `output/<batch_id>/`:

```
output/
├── Batch/
│   └── batch_1/
│       ├── Startup1/
│       │   ├── Startup1.json          # Full pipeline results
│       │   └── Startup1.md            # Human-readable report
│       ├── Startup2/
│       │   ├── Startup2.json
│       │   └── Startup2.md
│       ├── ranking.json               # Agent 7 comparative ranking
│       └── batch_summary.md           # Model usage, costs, retry stats
└── single_run_1/
    └── MyStartup/
        ├── MyStartup.json
        └── MyStartup.md
```

### JSON Output Structure

Each startup's `.json` file contains:

```json
{
  "1": { /* Agent 1 output: structured intake data */ },
  "2": { /* Agent 2 output: scores, verdict, SWOT */ },
  "3": { /* Agent 3 output: market analysis */ },
  "4": { /* Agent 4 output: product positioning */ },
  "5": { /* Agent 5 output: founder fit */ },
  "6": { /* Agent 6 output: recommendations */ },
  "_tags": {
    "batch_id": "batch_1",
    "startup_name": "MyStartup",
    "total_iterations": 6,
    "processing_time_seconds": 142.5
  },
  "_usage": { /* Token usage and costs per agent */ }
}
```

## ⚙️ Configuration

### Model Assignment

Edit `src/config.py` to customize which LLM models are used:

```python
# Default model for all agents
DEFAULT_MODEL = "anthropic/claude-haiku-4-5"

# Per-agent overrides (None = use DEFAULT_MODEL)
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

### Retry & Fallback Configuration

```python
# src/config.py
RETRY_ATTEMPTS = 3                    # Retries before fallback
RETRY_BASE_DELAY = 2                  # Exponential backoff: 2s, 4s, 8s
FALLBACK_MODEL = "anthropic/claude-haiku-4-5"  # Reliable fallback
RECOVERY_CHECK_INTERVAL = 3           # Successes before attempting recovery
RECOVERY_COOLDOWN = 60                # Seconds to wait before trying primary again
```

## 🔍 Advanced Features

### Feedback Loop System

Agents 2-6 can request re-runs from earlier agents when they detect insufficient information. The pipeline automatically:

1. Logs the feedback request to the database
2. Invalidates downstream outputs
3. Re-runs from the requested agent with feedback context
4. Enforces a maximum iteration limit (default: 18)

Track feedback events in the database:

```sql
sqlite3 evalbot.db "SELECT * FROM feedback_log WHERE batch_id='batch_1';"
```

### Quality Gates

The intake parser (Agent 1) flags missing critical fields:

```python
# src/config.py
CRITICAL_FIELDS = ["problem", "solution", "target_customer", "market", "business_model", "team"]
QUALITY_GATE_THRESHOLD = 3  # Warn if ≥3 critical fields missing
```

### Database Schema

EvalBot maintains a SQLite database (`evalbot.db`) with:

- `batches`: Batch metadata and descriptions
- `startups`: Startup entries and pipeline status
- `agent_outputs`: All agent outputs with iteration tracking
- `feedback_log`: Re-run requests and reasons
- `retry_events`: API retry and fallback events

## 💰 Cost Estimates

**Single startup evaluation** (Agents 1-6):
- **Premium** (Opus on 2&6, Sonnet on 3-5): ~$0.77
- **Balanced** (Sonnet on 2&6, MiniMax on 3-5): ~$0.13
- **Budget** (MiniMax across all): ~$0.03

**Batch of 10 startups + ranking**:
- **Premium**: ~$8.30
- **Balanced**: ~$1.40
- **Budget**: ~$0.35

See [`agent_models.md`](agent_models.md) for detailed cost breakdowns.

## 🛠️ Development

### Project Structure

```
EvalBot/
├── Agent1/           # Agent prompt files
│   └── prompt.md
├── Agent2/
│   └── prompt.md
├── ...
├── Agent7/
│   └── prompt.md
├── src/              # Core pipeline code
│   ├── agents.py     # Agent factory
│   ├── config.py     # Configuration
│   ├── db.py         # Database operations
│   ├── docs.py       # Document loading (PDF/DOCX)
│   ├── models.py     # Pydantic output models
│   ├── pipeline.py   # Pipeline orchestration
│   ├── retry_utils.py # Retry & fallback logic
│   └── tasks.py      # CrewAI task creation
├── main.py           # CLI entry point
├── evalbot.db        # SQLite database
└── output/           # Results directory
```

### Adding/Modifying Agents

1. Create/update `Agent{N}/prompt.md`
2. Define output model in `src/models.py` (`class Agent{N}Output`)
3. Add metadata to `_AGENT_META` in `src/agents.py`
4. Add expected output to `_EXPECTED_OUTPUT` in `src/tasks.py`
5. Update `AGENT_OUTPUT_MODELS` in `src/models.py`

### Testing

```bash
# Test agent creation
python -c "from src.agents import create_agent; print('✓' if create_agent(2) else '✗')"

# Test imports
python -c "from main import main; print('✓ Imports successful')"

# Validate syntax
python -m py_compile main.py src/*.py
```

## 📋 Troubleshooting

### Python 3.14+ Detected

EvalBot automatically re-launches with `.venv313/bin/python` if Python 3.14+ is detected. If this fails:

```bash
# Create a Python 3.13 environment manually
python3.13 -m venv .venv313
source .venv313/bin/activate
```

### API Connection Errors

The system automatically retries on connection errors and falls back to `FALLBACK_MODEL`. Monitor fallback stats in batch summary output.

To adjust retry behavior:

```python
# src/config.py
RETRY_ATTEMPTS = 5       # More patience
FALLBACK_MODEL = None    # Disable fallback (fail immediately)
```

### Missing Critical Fields

If startups have incomplete submissions, adjust the quality gate:

```python
# src/config.py
QUALITY_GATE_THRESHOLD = 5  # More lenient (warn only if ≥5 fields missing)
```

### Incomplete Batch Processing

Resume from failed startups:

```bash
# Find incomplete startups
sqlite3 evalbot.db "SELECT startup_name FROM startups WHERE batch_id='batch_1' AND pipeline_status != 'completed';"

# Process individually
python main.py single Startups/FailedStartupName/
```

## 📚 Documentation

- [`agent_models.md`](agent_models.md) — Detailed model recommendations and cost analysis
- [`RETRY_LOGGING.md`](RETRY_LOGGING.md) — Retry and fallback system details

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines here]

## 📧 Contact

[Add contact information here]
