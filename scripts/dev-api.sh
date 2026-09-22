#!/usr/bin/env bash
# API only, for use with the Vite dev server on port 3066.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -x "$ROOT/.venv/bin/python" ]]; then
  python3 -m venv "$ROOT/.venv"
  "$ROOT/.venv/bin/pip" install -r "$ROOT/backend/requirements.txt"
fi

export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8060}"
exec "$ROOT/.venv/bin/python" -m uvicorn backend.app.main:app --host "$HOST" --port "$PORT" --reload
