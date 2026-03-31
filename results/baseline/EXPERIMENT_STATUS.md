# Baseline Experiment - In Progress

## Status: RUNNING

**Started**: 2026-03-30 22:18:36  
**Configuration**: 2 rounds, baseline (N=1, no hall of fame, no dimension reasoning)  
**Log File**: `results/baseline/quick_test_2rounds.log`

## What's Happening

The system is currently running a 2-round baseline experiment to establish performance metrics before implementing optimizations.

### Execution Flow

Each round consists of:
1. **Inner Loop** (up to 5 attempts):
   - Agent 0: Generate startup idea
   - Agent 1: Parse submission into structured format
   - Agent 2: Score idea (0-80 scale)
   - If score < 50: provide feedback and retry
   - If score ≥ 50: proceed to full evaluation

2. **Full Evaluation** (for passing idea):
   - Agent 3: Market & Competition analysis
   - Agent 4: Product & Positioning analysis
   - Agent 5: Founder Fit analysis
   - Agent 6: Recommendations & pivot suggestions

3. **Next Round**:
   - Use Agent 6 recommendations to inform next idea generation
   - Repeat process

### Estimated Time

- **Per Round**: 5-10 minutes (depends on inner loop attempts and API speed)
- **Total for 2 Rounds**: 10-20 minutes
- **Full 10-Round Baseline**: 50-100 minutes

### What to Monitor

While running, the log shows:
- ⏱ Timer counting up for each agent call
- Startup names generated
- Scores achieved
- Inner loop retry attempts
- Round progression

## After Completion

Once the test completes, we'll:

1. **Extract Metrics**:
   ```bash
   python results/baseline/extract_metrics.py generated_1 results/baseline/baseline_2rounds_metrics.json
   ```

2. **Analyze Results**:
   - Average weighted score
   - Score distribution across dimensions
   - Inner loop success rate (first attempt pass %)
   - Execution time

3. **Compare to Future Tests**:
   - Best-of-N (N=3)
   - Hall of Fame enabled
   - All features combined

## Expected Baseline Performance

Based on system design:
- **Average Score**: 50-60 / 80 points
- **Score Tier**: Neutral to Positive
- **First Attempt Pass Rate**: 40-60%
- **Screening Attempts**: 1-3 per round

## Next Steps After Baseline

1. If scores are reasonable (50-60 range):
   - ✅ Proceed with Best-of-N implementation
   - Run comparison experiments

2. If scores are too low (< 50):
   - Investigate Agent 0 generation quality
   - Check Agent 2 scoring calibration
   - May need prompt adjustments

3. If scores are too high (> 70):
   - Good news! System already performing well
   - Optimizations may still provide incremental gains
   - Focus on consistency and reducing variance

## Progress Tracking

Check progress:
```bash
# View live log
tail -f results/baseline/quick_test_2rounds.log

# Check database
sqlite3 evalbot.db "SELECT COUNT(*) FROM agent_outputs WHERE batch_id='generated_1' AND agent_number=2;"
```

---

**Note**: The baseline is currently running in the background. Check back in ~15 minutes for results.
