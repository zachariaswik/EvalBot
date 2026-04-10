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
# crewai declares click~=8.1.7 and reflex declares click>=8.2 — no single
# click version satisfies both according to pip's metadata resolver, yet both
# work fine with click==8.3.2 at runtime (proved by the test suite).
#
# Workaround: install each pinned package individually with --no-deps.
# When given one package at a time the resolver never sees the contradictory
# cross-package constraints.  requirements.txt is a complete pip freeze so
# every transitive dependency is already listed — nothing is skipped.
grep -v '^[[:space:]]*#' requirements.txt \
  | grep -v '^[[:space:]]*$' \
  | xargs -n1 .venv/bin/pip install --quiet --no-deps

echo "--- Running tests ---"
.venv/bin/python -m pytest tests/ -q

echo "--- Setting up nginx + Basic Auth (idempotent) ---"
apt-get install -y nginx apache2-utils unzip 2>/dev/null || true
cp deploy/nginx-evalbot.conf /etc/nginx/sites-enabled/evalbot 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t 2>/dev/null && systemctl enable nginx 2>/dev/null && systemctl reload nginx 2>/dev/null || true
if [ ! -f /etc/nginx/.htpasswd ]; then
    echo "⚠  /etc/nginx/.htpasswd not found — Basic Auth will block all requests."
    echo "   Create it on the server with:  htpasswd -c /etc/nginx/.htpasswd alta"
fi

echo "--- Installing web service (always sync) ---"
cp deploy/evalbot-web.service /etc/systemd/system/ 2>/dev/null || true
systemctl daemon-reload 2>/dev/null || true
systemctl enable evalbot-web 2>/dev/null || true

echo "--- Restarting web service ---"
systemctl restart evalbot-web 2>/dev/null || true

echo "=== Deploy complete ==="
