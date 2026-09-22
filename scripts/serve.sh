#!/usr/bin/env bash
# One-process demo: API + built UI on 0.0.0.0:$PORT (default 8060).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install -r "$ROOT/backend/requirements.txt"
fi

if [[ ! -f "$ROOT/frontend/dist/index.html" ]]; then
  (cd "$ROOT/frontend" && npm ci && npm run build)
fi

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8060}"
echo "RevenueOps Control Tower on http://${HOST}:${PORT}"
exec "$ROOT/.venv/bin/python" -m backend.app
