# Baseline Testing Plan

## Purpose
Establish performance baseline for the EvalBot generator before implementing Quick Wins optimizations.

## Test Configuration

**System State**: All Quick Wins features DISABLED
- `--best-of-n 1` (single idea per attempt, no sampling)
- `--no-hall-of-fame` (no example library)
- `--no-dimension-reasoning` (no self-evaluation)

**Founder Constraints**: (Standardized across all experiments)
- Team size: 1
- Experience: "Founder starting from scratch without any previous experience"
- Network: None
- Availability: 100%
- Locale: Unspecified, global
- Capital: Very low
- Traction: Zero (no customers, revenue, or prototype)
- Languages: English
- Industry: Unspecified

**Test Parameters**:
- Rounds: 10 (outer loop iterations)
- Inner loop max attempts: 5 (default)
- Screening threshold: 50/80

## Execution

### Quick Test (1-2 rounds)
For rapid validation:
```bash
cd /Users/erikwik/AltaIR/EvalBot
python main.py generate --rounds 2 --best-of-n 1 --no-hall-of-fame --no-dimension-reasoning
```

### Full Baseline (10 rounds)
For comprehensive baseline:
```bash
cd /Users/erikwik/AltaIR/EvalBot
./results/baseline/run_baseline.sh
```

**Estimated time**: 30-60 minutes (depends on API speed and model)
**Estimated cost**: ~$2-5 (depends on model pricing)

## Metrics to Collect

### Primary Metrics
1. **Weighted Total Score** (0-80 scale)
   - Per round
   - Average across all rounds
   - Standard deviation
   - Min/max scores

2. **Score Distribution**
   - Count by tier (Reject, Weak, Neutral, Positive, Strong Positive)
   - Histogram of scores

3. **Scoring Dimensions** (individual component scores)
   - Problem Severity (0-20)
   - Market Size (0-20)
   - Differentiation (0-15)
   - Founder Insight (0-15)
   - Moat Potential (0-10)
   - Business Model (0-10)
   - Venture Potential (0-10)

### Secondary Metrics
4. **Execution Metrics**
   - Total execution time
   - Time per round
   - API calls made
   - Token usage
   - Cost (if trackable)

5. **Inner Loop Performance**
   - Number of screening attempts per round
   - Screening pass rate (% that pass threshold on first attempt)

## Data Collection

### Manual Extraction
After run completes, extract from:
1. Console output / execution.log
2. `output/generated_*/` directories (JSON outputs)
3. SQLite database `evalbot.db`

### Data to Record
Create `results/baseline/metrics.json`:
```json
{
  "experiment": "baseline",
  "timestamp": "2026-03-30T20:00:00Z",
  "configuration": {
    "best_of_n": 1,
    "hall_of_fame": false,
    "dimension_reasoning": false,
    "rounds": 10
  },
  "scores": {
    "weighted_total": [55, 62, 48, ...],
    "average": 57.3,
    "std_dev": 8.2,
    "min": 48,
    "max": 68
  },
  "dimensions": {
    "problem_severity": {"avg": 15.2, "std": 2.1},
    "market_size": {"avg": 14.8, "std": 2.5},
    ...
  },
  "execution": {
    "total_time_seconds": 2400,
    "time_per_round_seconds": 240,
    "total_api_calls": 150
  },
  "screening": {
    "attempts_per_round": [2, 1, 3, ...],
    "first_attempt_pass_rate": 0.4
  }
}
```

## Success Criteria

Baseline is complete when:
- ✅ 10 rounds executed successfully
- ✅ All scores recorded
- ✅ Execution metrics documented
- ✅ Results saved to `results/baseline/`
- ✅ Baseline can be compared to future experiments

## Notes

### Why 10 Rounds?
- Enough data for statistical validity
- Captures variation in generation quality
- Reasonable time/cost for experimentation
- Standard in ML experimentation

### Reproducibility
Use same constraints across all experiments:
- Baseline (this test)
- Best-of-N only
- Hall of Fame only
- All features combined

This allows fair comparison of feature impact.

### Cost Considerations
If API costs are a concern:
- Reduce rounds to 5 (minimum for statistical validity)
- Use cheaper models (e.g., Haiku instead of Sonnet)
- Test with --rounds 2 first to verify everything works

## Next Steps After Baseline

1. Implement Best-of-N sampling
2. Run Best-of-N experiment (10 rounds, N=3)
3. Compare scores to baseline
4. Repeat for other features
5. Final comparison: all features vs baseline
