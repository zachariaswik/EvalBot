#!/bin/bash
# Baseline Experiment - No Optimizations
# This script runs the generator with all Quick Wins features disabled
# to establish a performance baseline for comparison.

set -e

echo "=================================================="
echo "EvalBot Baseline Experiment"
echo "Features: All optimizations DISABLED"
echo "  - Best-of-N: 1 (disabled)"
echo "  - Hall of Fame: Disabled"
echo "  - Dimension Reasoning: Disabled"
echo "=================================================="
echo ""

# Configuration
ROUNDS=10
EXPERIMENT_NAME="baseline_$(date +%Y%m%d_%H%M%S)"
OUTPUT_DIR="results/baseline/${EXPERIMENT_NAME}"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

echo "Running ${ROUNDS} rounds..."
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Run with all features disabled
python main.py generate \
  --rounds ${ROUNDS} \
  --name "${EXPERIMENT_NAME}" \
  --best-of-n 1 \
  --no-hall-of-fame \
  --no-dimension-reasoning \
  --team-size 1 \
  --experience "Founder starting from scratch without any previous experience" \
  --capital "Very low" \
  --traction "Zero — no customers, no revenue, no prototype" \
  2>&1 | tee "${OUTPUT_DIR}/execution.log"

echo ""
echo "=================================================="
echo "Baseline experiment complete!"
echo "Results saved to: ${OUTPUT_DIR}"
echo ""
echo "Next steps:"
echo "  1. Review execution.log for scores and timing"
echo "  2. Extract score data from output/ directory"
echo "  3. Run comparison experiments with features enabled"
echo "=================================================="
