# API Retry & Fallback Logging

## Overview

The system now tracks all retry and fallback events in the database and includes this information in batch/generation summary reports.

## Database Schema

### `retry_log` Table
Stores every retry/fallback event that occurs during agent execution:

```sql
CREATE TABLE retry_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id            TEXT NOT NULL,
    startup_name        TEXT NOT NULL,
    agent_number        INTEGER NOT NULL,
    intended_model      TEXT NOT NULL,      -- Originally configured model
    actual_model        TEXT NOT NULL,       -- Model actually used (may differ if fallback)
    retry_count         INTEGER NOT NULL,    -- Number of retries before success/fallback
    fallback_occurred   INTEGER NOT NULL,    -- 1 if switched to fallback model, 0 otherwise
    recovery_occurred   INTEGER NOT NULL,    -- 1 if recovered from fallback to primary, 0 otherwise
    error_type          TEXT,                -- timeout | connection_reset | server_error | other
    created_at          TEXT NOT NULL
);
```

## Output Files

### Individual Startup JSON (`output/<batch_id>/<startup_name>.json`)

The `_usage` section now includes retry information:

```json
{
  "1": {
    "model": "minimax/MiniMax-M2.7",
    "intended_model": "minimax/MiniMax-M2.7",
    "prompt_tokens": 6119,
    "completion_tokens": 1696,
    "total_tokens": 7815,
    "fallback_occurred": false,
    "retry_count": 0
  },
  "3": {
    "model": "anthropic/claude-haiku-4-5",
    "intended_model": "minimax/MiniMax-M2.7",
    "prompt_tokens": 9050,
    "completion_tokens": 1301,
    "total_tokens": 10351,
    "fallback_occurred": true,
    "retry_count": 3
  }
}
```

**Key fields:**
- `model`: Actual model used (fallback if occurred)
- `intended_model`: Originally configured model
- `fallback_occurred`: Whether fallback happened
- `retry_count`: Number of retries before success

### Batch Summary (`batch_summary.md` / `generation_summary.md`)

New section added at the top showing retry statistics:

```markdown
## API Retry & Fallback Summary

**Total Retry Events**: 15
**Fallback Events**: 3
**Recovery Events**: 1
**Total Retries**: 42
**Average Retries per Event**: 2.8

### Per-Agent Breakdown

| Agent | Events | Fallbacks | Recoveries | Total Retries | Intended → Actual Model |
|-------|--------|-----------|------------|---------------|-------------------------|
| 2     | 5      | 1         | 0          | 12            | minimax/MiniMax-M2.7 → anthropic/claude-haiku-4-5 |
| 3     | 10     | 2         | 1          | 30            | minimax/MiniMax-M2.7 → anthropic/claude-haiku-4-5 |

### Error Types

- **connection_reset**: 8 occurrences
- **timeout**: 5 occurrences
- **server_error**: 2 occurrences
```

**Models Used** table now includes fallback indicators:

```markdown
## Models Used

| Agent | Role                           | Model                              | Notes |
|-------|--------------------------------|------------------------------------|-------|
| 1     | Intake Parser                  | anthropic/claude-sonnet-4-6        |       |
| 2     | Venture Analyst                | minimax/MiniMax-M2.7               | ⚠️ Fallback used 2x |
| 3     | Market & Competition Analyst   | minimax/MiniMax-M2.7               | ⚠️ Fallback used 5x |
```

## Querying Retry Data

### SQL Queries

```sql
-- Get all retry events for a batch
SELECT * FROM retry_log WHERE batch_id = 'batch_1' ORDER BY created_at;

-- Find startups with most fallbacks
SELECT 
    startup_name, 
    COUNT(*) as fallback_count
FROM retry_log
WHERE batch_id = 'batch_1' AND fallback_occurred = 1
GROUP BY startup_name
ORDER BY fallback_count DESC;

-- Error type distribution
SELECT 
    error_type, 
    COUNT(*) as count,
    AVG(retry_count) as avg_retries
FROM retry_log
WHERE batch_id = 'batch_1'
GROUP BY error_type
ORDER BY count DESC;

-- Agent reliability (which agents fail most)
SELECT 
    agent_number,
    COUNT(*) as total_events,
    SUM(fallback_occurred) as fallbacks,
    AVG(retry_count) as avg_retries
FROM retry_log
WHERE batch_id = 'batch_1'
GROUP BY agent_number
ORDER BY fallbacks DESC;
```

### Python API

```python
from src.db import get_retry_stats

# Get comprehensive stats for a batch
stats = get_retry_stats("batch_1")

print(f"Total events: {stats['total_events']}")
print(f"Fallback count: {stats['fallback_count']}")
print(f"Recovery count: {stats['recovery_count']}")

# Per-agent breakdown
for agent_stat in stats['per_agent']:
    print(f"Agent {agent_stat['agent_number']}: "
          f"{agent_stat['fallbacks']} fallbacks, "
          f"{agent_stat['total_retries']} retries")

# Error types
for error_stat in stats['error_types']:
    print(f"{error_stat['error_type']}: {error_stat['count']} times")
```

## Use Cases

### Cost Analysis
Compare intended vs actual model usage to understand cost impact of fallbacks:
- If Agent 3 intended to use `minimax/MiniMax-M2.7` (cheap) but used `anthropic/claude-haiku-4-5` (more expensive) 10 times, calculate the cost difference.

### Reliability Monitoring
Identify which agents/models are most unstable:
- High fallback rates indicate provider issues
- High retry counts with no fallback indicate intermittent failures that self-resolve

### Provider Selection
Use historical data to inform model configuration:
- If MiniMax has 30% fallback rate during certain hours, schedule batch processing accordingly
- If Anthropic has 0% fallback rate, consider using it as primary despite higher cost

### Optimization
- If fallback model performs well, consider making it primary
- If certain agents never fail, allocate more budget to agents that struggle

## Implementation Notes

- Retry events are logged **only** when retries or fallback occur (not every successful execution)
- Logging happens synchronously in `pipeline.py` after `execute_with_retry()` completes
- The `RetryResult` dict returned by `execute_with_retry()` contains all metadata
- Summary generation in `main.py` queries the database via `get_retry_stats()`

## Testing

Run the test suite to verify logging works:

```bash
python3 << 'ENDTEST'
from src.db import init_db, log_retry_event, get_retry_stats
from pathlib import Path
import tempfile

with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
    test_db = Path(tmp.name)

init_db(test_db)
log_retry_event(
    batch_id="test",
    startup_name="Test",
    agent_number=3,
    intended_model="minimax/MiniMax-M2.7",
    actual_model="anthropic/claude-haiku-4-5",
    retry_count=3,
    fallback_occurred=True,
    recovery_occurred=False,
    error_type="connection_reset",
    db_path=test_db,
)

stats = get_retry_stats("test", db_path=test_db)
assert stats['total_events'] == 1
assert stats['fallback_count'] == 1
print("✅ All tests passed!")

test_db.unlink()
ENDTEST
```
