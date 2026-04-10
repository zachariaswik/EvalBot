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
# --no-deps skips the dependency resolver.  requirements.txt is a complete
# pip freeze (all transitive deps pinned), so every package is already listed.
# This is necessary because crewai (click~=8.1.7) and reflex (click>=8.2)
# declare incompatible click bounds, but the pinned click==8.3.2 works fine
# at runtime — the resolver just can't figure that out.
.venv/bin/pip install --quiet --no-deps -r requirements.txt

echo "--- Running tests ---"
.venv/bin/python -m pytest tests/ -q

echo "--- Setting up nginx + Basic Auth (idempotent) ---"
apt-get install -y nginx apache2-utils 2>/dev/null || true
cp deploy/nginx-evalbot.conf /etc/nginx/sites-enabled/evalbot 2>/dev/null || true
rm -f /etc/nginx/sites-enabled/default 2>/dev/null || true
nginx -t 2>/dev/null && systemctl enable nginx 2>/dev/null && systemctl reload nginx 2>/dev/null || true
if [ ! -f /etc/nginx/.htpasswd ]; then
    echo "⚠  /etc/nginx/.htpasswd not found — Basic Auth will block all requests."
    echo "   Create it on the server with:  htpasswd -c /etc/nginx/.htpasswd alta"
fi

echo "--- Installing web service (idempotent) ---"
if [ ! -f /etc/systemd/system/evalbot-web.service ]; then
    cp deploy/evalbot-web.service /etc/systemd/system/ 2>/dev/null || true
    systemctl daemon-reload 2>/dev/null || true
    systemctl enable evalbot-web 2>/dev/null || true
fi

echo "--- Restarting web service ---"
systemctl restart evalbot-web 2>/dev/null || true

echo "=== Deploy complete ==="
