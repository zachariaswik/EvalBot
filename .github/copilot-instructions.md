# EvalBot — Multi-Agent Startup Evaluation Pipeline

EvalBot is a CrewAI-based system for evaluating early-stage startup submissions through a multi-agent pipeline. Each agent specializes in one aspect of venture analysis (intake parsing, venture scoring, market analysis, etc.) and produces structured JSON outputs that feed into downstream agents.

## Running the System

### Setup
```bash
# Use Python 3.13 or earlier (CrewAI stack incompatible with 3.14+)
python -m venv .venv313
source .venv313/bin/activate  # or .venv313\Scripts\activate on Windows
pip install -r requirements.txt  # if it exists, otherwise install crewai, litellm, pydantic, pdfplumber

# Set up API keys in .env
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
MINIMAX_API_KEY=your_key_here
```

### CLI Commands
```bash
# Process default CourseDocs submission
python main.py

# Process a single startup submission (text or PDF)
python main.py single <path/to/submission.txt>

# Process a batch of startups from a directory
python main.py batch <path/to/startups_folder>

# Generate synthetic startup ideas and evaluate them
python main.py generate --rounds 3 --screening-threshold 50 --max-attempts 5
```

## Architecture

### Multi-Agent Pipeline
The system uses **8 specialized agents** that run sequentially:

0. **Startup Idea Generator** (Agent 0) — Generate mode only
   - Creates synthetic startup submissions optimized for scoring well
   - Only runs in `generate` mode with screening loop

1. **Intake Parser** (Agent 1) — Low reasoning complexity
   - Converts raw submissions into standardized JSON structure
   - Extracts: problem, solution, market, team, competitors, traction, etc.
   - Flags missing/inconsistent information

2. **Venture Analyst** (Agent 2) — Very high reasoning complexity
   - Core scoring agent: evaluates 10 dimensions (1-10 scale each)
   - Produces verdict: Top VC Candidate, Promising (Needs Focus/Pivot), Good Small Business, Feature Not Company, AI Wrapper, Reject
   - Outputs SWOT analysis and weighted total score
   - In `generate` mode, runs in screening loop with Agent 0 & 1

3. **Market & Competition Analyst** (Agent 3) — Medium-high complexity
   - Market dynamics, TAM/SAM/SOM analysis
   - Competitive landscape assessment

4. **Product & Positioning Analyst** (Agent 4) — Medium complexity
   - Feature vs company distinction
   - AI wrapper risk assessment
   - Product positioning

5. **Founder Fit Analyst** (Agent 5) — Medium complexity
   - Team assessment
   - Execution confidence

6. **Recommendation / Pivot Agent** (Agent 6) — Very high complexity
   - Strategic synthesis of all prior analyses
   - Actionable recommendations and pivot options
   - Most important output for users

7. **Ranking Committee** (Agent 7) — Medium complexity
   - Only runs in batch mode
   - Comparative ranking across cohort
   - Input context grows with batch size

### Agent Structure
- Each agent lives in `Agent{N}/` directory with a `prompt.md` file
- Prompts are loaded at runtime by `src/agents.py`
- Agent metadata (role, goal) defined in `_AGENT_META` dict in `src/agents.py`
- Pydantic output models defined in `src/models.py` (one per agent)

### Feedback Loop / Re-run System
Agents 2-6 can request re-runs from earlier agents via `FeedbackMixin` fields:
- `rerun_from_agent`: int (which agent to re-run from)
- `rerun_reason`: str (explanation)

The pipeline enforces a `MAX_ITERATIONS` safety limit (default: 18 = 3x the 6-agent loop).

### Generate Mode — Screening Loop
When running `python main.py generate`, the system:
1. Agent 0 generates a startup idea optimized to score well
2. Agent 1 parses it
3. Agent 2 scores it
4. If score < threshold, regenerate with feedback (up to `--max-attempts` times per round)
5. Best attempt proceeds to full evaluation (Agents 3-6)
6. Repeat for `--rounds` number of startups
7. Agent 7 ranks the cohort

## Configuration

### LLM Model Assignment (`src/config.py`)
- CrewAI uses **litellm** under the hood — any litellm-compatible model string works
- `DEFAULT_MODEL`: Fallback model (currently `anthropic/claude-haiku-4-5`)
- `AGENT_MODELS`: Dict mapping agent number → model string override
- `RERUN_MODEL`: Model used for feedback-triggered re-runs (None = reuse agent's normal model)
- `get_model_for_agent(agent_number, is_rerun)`: Resolves model priority

See `agent_models.md` for detailed model recommendations by provider and cost profiles.

**Supported providers** (set API key in `.env`):
- OpenAI: `gpt-4o`, `gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `o3-mini`
- Anthropic: `anthropic/claude-opus-4-6`, `anthropic/claude-sonnet-4-6`, `anthropic/claude-haiku-4-5`
- MiniMax: `minimax/MiniMax-M2.7` (ultra-cheap, good reasoning)
- Gemini: `gemini/gemini-2.0-flash` (free tier available)
- Groq: `groq/llama-3.3-70b-versatile` (free tier)
- Ollama: `ollama/qwen3:4b`, `ollama/llama3.2` (local, free)

**Ollama context window**: `OLLAMA_NUM_CTX` (default: 16384) — models need larger context than 4096 default

### Structured Output Handling
- Most providers use CrewAI's `output_pydantic` for structured JSON
- MiniMax doesn't support structured output → falls back to JSON extraction from text
- Fallback parser (`_extract_json_segment`) handles models that return raw text

### Quality Gates
- `CRITICAL_FIELDS`: List of required intake fields (problem, solution, target_customer, market, business_model, team)
- `QUALITY_GATE_THRESHOLD`: Warn if ≥ this many critical fields are missing (default: 3)

## Database Schema (`evalbot.db`)

### Tables
- `batches`: batch_id (PK), created_at, description
- `startups`: id (PK), batch_id, startup_name, raw_submission, pipeline_status
- `agent_outputs`: id (PK), batch_id, startup_name, agent_number, output_json, iteration, is_current, feedback_reason, created_at
- `feedback_log`: tracks re-run requests between agents

### Key Functions (`src/db.py`)
- `init_db()`: Initialize schema
- `create_batch(batch_id, description)`: Register new batch
- `upsert_startup(batch_id, startup_name, submission)`: Add/update startup
- `store_agent_output(batch_id, startup_name, agent_number, output, iteration, feedback_reason)`: Save agent results
- `invalidate_outputs_from(batch_id, startup_name, from_agent)`: Mark outputs as stale when re-running
- `get_all_batch_outputs(batch_id)`: Retrieve all current outputs for a batch

## Output Structure

Results are exported to `output/<batch_id>/` as JSON files:
- `<startup_name>.json`: Full pipeline results for one startup
- `batch_summary.json`: Aggregated results for the batch (if batch mode)
- `ranking.json`: Agent 7 ranking output (batch mode only)

Each startup's JSON contains:
- Keys `1`, `2`, `3`, ..., `6`: Agent outputs (structured JSON matching Pydantic models)
- `_tags`: Metadata (batch_id, startup_name, processing time, etc.)

## Key Conventions

### Pydantic Models (`src/models.py`)
- One model class per agent: `Agent1Output`, `Agent2Output`, etc.
- All models inherit from `BaseModel`
- Agents 1-6 inherit from `FeedbackMixin` for re-run support
- Agent 2 verdict is an enum (`Verdict`) with exact string matches required
- SWOT is a nested `SWOTModel` with list fields

### Task Creation (`src/tasks.py`)
- `create_task(agent, agent_number, ...)`: Builds CrewAI Task with context
- `create_ranking_task(agent, cohort_data)`: Special task for Agent 7
- `_json_only_instruction(agent_number)`: Appends strict JSON formatting rules
- `_FEEDBACK_INSTRUCTION`: Added to agents 2-6 prompts to enable re-runs

### Pipeline Orchestration (`src/pipeline.py`)
- `run_single(startup_name, submission_text, batch_id)`: One startup through agents 1-6
- `run_batch(batch_id, submissions)`: Multiple startups + Agent 7 ranking
- `_run_single_agent(agent_number, ...)`: Execute one agent with context
- `_compute_weighted_score(a2_output)`: Calculate weighted total from Agent 2 scores
- `_check_reject_signals(a2_output)`: Identify auto-reject conditions

### Generate Mode Specifics (`main.py`)
- `run_generate(config)`: Orchestrates generate mode workflow
- Inner loop: Agent 0 → 1 → 2 with screening threshold
- Outer loop: Repeat for N rounds
- Best attempt (highest score) proceeds to full evaluation per round
- Final Agent 7 ranking across all generated startups

## Common Patterns

### Adding/Modifying an Agent
1. Create/update `Agent{N}/prompt.md`
2. Define output model in `src/models.py` (`class Agent{N}Output`)
3. Add metadata to `_AGENT_META` in `src/agents.py`
4. Add expected output description to `_EXPECTED_OUTPUT` in `src/tasks.py`
5. Update `AGENT_OUTPUT_MODELS` dict in `src/models.py`
6. If agent needs structured output, add to `AGENT_OUTPUT_MODELS` mapping

### Changing Model Assignments
Edit `src/config.py`:
- `AGENT_MODELS` dict: Set per-agent overrides
- Use `None` to fall back to `DEFAULT_MODEL`
- Refer to `agent_models.md` for cost/quality tradeoffs

### Debugging Agent Outputs
- Check `output/<batch_id>/<startup_name>.json` for raw agent outputs
- Use `evalbot.db` to query historical runs and feedback loops
- Look for `_parse_failed` flag in output dict (indicates JSON extraction fallback)
- Review `output.log` if logging is enabled

### Python 3.14+ Compatibility
The script automatically detects Python 3.14+ and attempts to re-launch with `.venv313/bin/python` if it exists. CrewAI's dependency stack is incompatible with Python 3.14+.

## Debugging the Feedback Loop

The feedback loop allows agents 2-6 to request re-runs from earlier agents when they detect insufficient/inconsistent information. Understanding how to debug this is critical for diagnosing pipeline issues.

### How the Feedback Loop Works

1. **Detection**: Agents 2-6 can set `rerun_from_agent` (int) and `rerun_reason` (str) in their output
2. **Validation**: Pipeline checks if `1 <= rerun_from_agent < current_agent_number`
3. **Logging**: Records to `feedback_log` table with batch_id, startup_name, from_agent, to_agent, reason, iteration
4. **Invalidation**: Marks all agent outputs from `rerun_from_agent` onward as `is_current = 0`
5. **State Reset**: Clears in-memory outputs and jumps back to target agent
6. **Re-execution**: Re-runs from target agent with feedback context
7. **Safety**: `MAX_ITERATIONS` (default: 18) prevents infinite loops

### Querying Feedback History

```sql
-- View all feedback events for a batch
SELECT 
    startup_name, 
    from_agent, 
    to_agent, 
    reason, 
    iteration, 
    created_at
FROM feedback_log
WHERE batch_id = 'batch_1'
ORDER BY created_at;

-- Find startups with multiple feedback loops
SELECT 
    startup_name, 
    COUNT(*) as loop_count
FROM feedback_log
WHERE batch_id = 'batch_1'
GROUP BY startup_name
HAVING loop_count > 1;

-- Trace a specific startup's feedback chain
SELECT 
    iteration,
    from_agent || ' → ' || to_agent as flow,
    reason
FROM feedback_log
WHERE batch_id = 'batch_1' 
  AND startup_name = 'MyStartup'
ORDER BY iteration;
```

### Viewing Agent Output History

```sql
-- See all versions of an agent's output (including invalidated ones)
SELECT 
    agent_number,
    iteration,
    is_current,
    feedback_reason,
    created_at,
    substr(output_json, 1, 100) as output_preview
FROM agent_outputs
WHERE batch_id = 'batch_1' 
  AND startup_name = 'MyStartup'
ORDER BY agent_number, iteration;

-- Compare before/after a feedback loop
-- First run (iteration 1)
SELECT output_json 
FROM agent_outputs
WHERE batch_id = 'batch_1'
  AND startup_name = 'MyStartup'
  AND agent_number = 2
  AND iteration = 1;

-- After re-run (iteration 2+)
SELECT output_json 
FROM agent_outputs
WHERE batch_id = 'batch_1'
  AND startup_name = 'MyStartup'
  AND agent_number = 2
  AND iteration > 1
  AND is_current = 1;
```

### Common Feedback Loop Issues

**Infinite Loop (hits MAX_ITERATIONS)**:
- **Symptom**: Pipeline stops with "Max iterations reached"
- **Cause**: Agent keeps requesting re-runs for same issue
- **Diagnosis**:
  ```sql
  -- Check iteration count and feedback patterns
  SELECT startup_name, MAX(iteration) as max_iter
  FROM agent_outputs
  WHERE batch_id = 'batch_1'
  GROUP BY startup_name
  HAVING max_iter > 10;
  
  -- Look at repeated feedback reasons
  SELECT reason, COUNT(*) as occurrences
  FROM feedback_log
  WHERE batch_id = 'batch_1' AND startup_name = 'MyStartup'
  GROUP BY reason;
  ```
- **Fix**: Adjust agent prompt to be more tolerant, or increase `MAX_ITERATIONS` if legitimate complexity

**Agent Never Requests Feedback When It Should**:
- **Symptom**: Agent produces low-quality output but doesn't trigger re-run
- **Cause**: Prompt doesn't emphasize when to use feedback, or `rerun_from_agent` gets dropped during parsing
- **Diagnosis**: Check raw agent output for `rerun_from_agent` field
  ```python
  # In main.py or a debug script
  import json
  with open('output/batch_1/MyStartup.json') as f:
      data = json.load(f)
      agent_out = data.get('3', {})  # Agent 3 output
      print(f"rerun_from_agent: {agent_out.get('rerun_from_agent')}")
      print(f"rerun_reason: {agent_out.get('rerun_reason')}")
  ```
- **Fix**: Update agent prompt with clearer feedback instructions, or check if model supports structured output correctly

**Feedback Loop Targets Wrong Agent**:
- **Symptom**: Agent 5 requests re-run from Agent 3, but should request from Agent 1
- **Cause**: Agent doesn't understand upstream dependencies
- **Diagnosis**: Review `feedback_log` for illogical jumps
  ```sql
  SELECT from_agent, to_agent, reason
  FROM feedback_log
  WHERE batch_id = 'batch_1'
  ORDER BY created_at;
  ```
- **Fix**: Update agent prompts to clarify which earlier agents provide which information

**Feedback Reason Missing or Vague**:
- **Symptom**: `rerun_reason` is null or "insufficient information"
- **Cause**: Agent prompt doesn't require specificity
- **Diagnosis**: 
  ```sql
  SELECT from_agent, to_agent, reason
  FROM feedback_log
  WHERE reason IS NULL OR LENGTH(reason) < 20;
  ```
- **Fix**: Add to agent prompt: "When requesting re-run, provide specific missing fields or issues"

### Console Output Indicators

Watch for these patterns in pipeline execution logs:

```
✓ Normal progression:
  [Progress 2/6] Agent 2/6 | Iteration 1
  Agent 2 completed successfully.
  [Progress 3/6] Agent 3/6 | Iteration 2
  Agent 3 completed successfully.

⚠ Feedback loop triggered:
  [Progress 4/6] Agent 4/6 | Iteration 4
  
  FEEDBACK LOOP: Agent 4 requests re-run from Agent 1
  Reason: Missing critical field: target_customer ICP details
  
  [Progress 1/6] Agent 1/6 | Iteration 5 (RE-RUN)
  Feedback context: Missing critical field: target_customer ICP details

⛔ Iteration limit hit:
  ⚠ WARNING: Max iterations reached (18). Ending pipeline.
  Total iterations: 18 | Pipeline incomplete
```

### Debugging Workflow

1. **Check if feedback loop occurred**: Look for "FEEDBACK LOOP:" in console output
2. **Query feedback_log**: Understand which agents triggered re-runs and why
3. **Compare agent_outputs**: View iterations before/after to see what changed
4. **Check is_current flag**: Verify stale outputs were properly invalidated
5. **Review iteration count**: Ensure it's reasonable (typically 6-12 for single startup)
6. **Examine rerun_reason**: Assess if feedback requests are legitimate or overly sensitive

### Testing Feedback Loop Behavior

To verify feedback loop works correctly:

```bash
# Run with a deliberately incomplete submission
echo "We're building an app." > test_minimal.txt
python main.py single test_minimal.txt

# Check if Agent 2 or 3 requested more info from Agent 1
sqlite3 evalbot.db "SELECT * FROM feedback_log ORDER BY created_at DESC LIMIT 5;"
```

## Testing

No formal test suite currently exists. Manual testing via CLI commands is the primary validation method.

## Related Documentation

- `agent_models.md`: Detailed model recommendations, cost estimates, provider profiles
- `Altalab_results_prompt.md`: Original architecture design and agent role definitions
- `deploymentPlan/staged_migration_blueprint.md`: Deployment/migration notes
