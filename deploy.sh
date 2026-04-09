#!/usr/bin/env bash
# deploy.sh — pull latest code and restart nothing (CLI tool, not a daemon)
# Run this on the server:  bash /opt/evalbot/deploy.sh
set -euo pipefail

DEPLOY_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DEPLOY_DIR"

echo "=== EvalBot deploy: $(date) ==="

echo "--- Pulling latest code ---"
git pull

echo "--- Installing/updating dependencies ---"
.venv/bin/pip install --quiet -r requirements.txt

echo "--- Running tests ---"
.venv/bin/python -m pytest tests/ -q

echo "=== Deploy complete ==="
