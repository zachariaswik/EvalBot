# Running EvalBot

EvalBot evaluates startup pitch submissions using a 7-agent AI pipeline. You can run it through the **web UI** (recommended) or directly from the **command line**.

---

## 1. Prerequisites

### Python environment

EvalBot requires Python 3.13. Activate the virtual environment before doing anything:

```bash
source .venv313/bin/activate
```

### API keys

Create a `.env` file in the project root (copy the block below and fill in your keys):

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
MINIMAX_API_KEY=...
GEMINI_API_KEY=...
GROQ_API_KEY=...
```

You only need keys for the models actually configured in `src/config.py`. At minimum, `OPENAI_API_KEY` is required (used by Agent 1 and as the global fallback model).

---

## 2. Web UI (recommended)

### Start the server

```bash
source .venv313/bin/activate
reflex run
```

Open **http://localhost:3000** in your browser. The first start takes ~30 seconds to compile the frontend.

### Upload startups

Go to **Run Batch** (`/run`) in the top navigation.

There are two upload modes:

| Button | What to pick | Result |
|--------|-------------|--------|
| **Single Startup** | A folder containing that startup's files (PDF, DOCX, TXT, MD) | Folder name becomes the startup name |
| **Batch Folder** | A parent folder whose subfolders are individual startups | Each subfolder becomes one startup |

Supported file types: `.pdf`, `.docx`, `.txt`, `.md`

After uploading, each startup appears in the **Staged** list. You can remove any you don't want to run, or use the **"Multi-file only"** filter to hide single-file submissions.

### Run the batch

Click **Run Batch** (top right). The pipeline monitor shows:

- A card per startup with 6 agent dots — grey (waiting) → blue spinner (active) → green check (done)
- The current agent role below each card
- Elapsed time per startup
- A completed list at the bottom (green = success, red ⏰ = timed out)
- A "Ranking cohort…" spinner while Agent 7 runs

### Monitor the log

At the bottom of the monitor panel, click **`>_ Raw Log ▼`** to expand the live log. The first two lines show:

```
Log: /path/to/EvalBot/output/run_20250411_143022.log
$ /path/to/.venv313/bin/python -u main.py batch Startups/ --only ...
```

You can also follow the log from a terminal while it runs:

```bash
tail -f $(ls -t output/run_*.log | head -1)
```

### View results

When the run finishes, click **View Results →** to go directly to the batch page, or navigate to **Dashboard** and select the batch from the list.

On the startup detail page (`/batch/<batch_id>/<startup_name>`), click **Download PDF** to export the full EvalBot feedback report for that startup.

---

## 3. Command line

### Single submission

```bash
source .venv313/bin/activate
python main.py single path/to/submission.pdf
```

Accepts `.pdf`, `.docx`, `.txt`, or `.md`. Output is saved to `output/batch_N/`.

### Batch from a directory

```bash
source .venv313/bin/activate
python main.py batch path/to/Startups/
```

The directory must contain subfolders — one per startup. All files inside each subfolder are concatenated and passed to the pipeline together.

```
Startups/
├── AlphaCo/
│   ├── pitch.pdf
│   └── financials.xlsx   ← ignored (unsupported extension)
├── BetaCo/
│   └── deck.pdf
└── GammaCo/
    ├── overview.md
    └── team.docx
```

**Run only specific startups from the folder:**

```bash
python main.py batch Startups/ --only AlphaCo GammaCo
```

**Limit concurrency** (default: all startups run in parallel):

```bash
python main.py batch Startups/ --workers 3
```

**Pipe output to a log file while watching live:**

```bash
python main.py batch Startups/ 2>&1 | tee output.log
```

---

## 4. Output

Results are saved to `output/Batch/batch_N/` after a batch run:

```
output/Batch/batch_5/
├── AlphaCo/
│   ├── AlphaCo.json        ← all agent outputs + token usage + metadata
│   └── AlphaCo.md          ← human-readable report
├── BetaCo/
│   ├── BetaCo.json
│   └── BetaCo.md
├── ranking.json            ← Agent 7 comparative ranking across the cohort
└── batch_summary.md        ← model usage, costs, retry stats
```

Run logs from the web UI are saved separately:

```
output/run_20250411_143022.log   ← full raw output including PROGRESS events
```

---

## 5. Agent pipeline

7 agents run per startup (agents 1–6 in parallel across startups, then agent 7 once for the whole batch):

| Agent | Role | Model |
|-------|------|-------|
| 1 | Intake Parser | GPT-4o |
| 2 | Venture Analyst | MiniMax-M2.7 |
| 3 | Market & Competition Analyst | MiniMax-M2.7 |
| 4 | Product & Positioning Analyst | MiniMax-M2.7 |
| 5 | Founder Fit Analyst | MiniMax-M2.7 |
| 6 | Recommendation Agent | MiniMax-M2.7 |
| 7 | Ranking Committee | GPT-4o |

Fallback model (used automatically on failure): **GPT-4o-mini**

Timeouts: 7 min per agent, 16 min total per startup.

To change models, edit `AGENT_MODELS` in `src/config.py`.

---

## 6. Reading the log

The log files are noisy — mostly agent output and per-second timing lines. Use these grep commands to pull out just the useful bits.

**Errors and failures only:**
```bash
grep -iE "error|exception|traceback|failed|✗|✘" $(ls -t output/run_*.log | head -1)
```

**Fallback and retry events:**
```bash
grep -E "fallback|retry|↻|⚠|⏰|timeout|timed out" $(ls -t output/run_*.log | head -1)
```

**Key pipeline events (start/done per agent and startup):**
```bash
grep -E "Processing:|completed in|STARTUP|BATCH|Ranking|Agent [0-9]+ \(" $(ls -t output/run_*.log | head -1)
```

**Everything troubleshooting-relevant in one pass:**
```bash
grep -iE "error|exception|traceback|failed|✗|fallback|retry|↻|⚠|⏰|timeout|processing:|completed in" \
  $(ls -t output/run_*.log | head -1)
```

**With line numbers** (useful for reading surrounding context):
```bash
grep -niE "error|exception|traceback|failed" $(ls -t output/run_*.log | head -1)
```

**Show 5 lines of context around each error:**
```bash
grep -iE -A5 "error|exception|traceback" $(ls -t output/run_*.log | head -1)
```

To point at a specific log file instead of the latest, replace the `$(ls -t ...)` substitution with the path shown at the top of the UI's Raw Log section.

---

## 7. Troubleshooting

**Run shows "interrupted" on page load**
A previous run was interrupted (server restarted mid-run). The state file `evalbot_run.json` is still marked as running. Start a new run — it will pick up cleanly.

**A startup shows ⏰ in the completed list**
That startup hit the 16-minute timeout. Its output is saved as a partial error result. Re-run just that startup:
```bash
python main.py batch Startups/ --only StartupName
```

**Fallback model is being used**
Normal behaviour. If the primary model (e.g. MiniMax) returns an unexpected response format, EvalBot automatically retries with GPT-4o-mini. Check `batch_summary.md` for a model usage breakdown.

**No startups found**
Make sure the folder passed to `batch` contains subfolders (one per startup), not files directly at the top level.

**API key missing**
You'll see an authentication error in the log. Add the relevant key to `.env` and restart.
