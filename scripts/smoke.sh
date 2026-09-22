#!/usr/bin/env bash
# Native smoke test. Does not use Docker.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

export HOST="0.0.0.0"
export PORT="${PORT:-8060}"
BASE_URL="${BASE_URL:-http://127.0.0.1:${PORT}}"

STARTED=0
if curl -sf "${BASE_URL}/health" >/dev/null 2>&1; then
  echo "Reusing ${BASE_URL}"
else
  HOST="$HOST" PORT="$PORT" "$PYTHON" -m backend.app > /tmp/revenueops-smoke.log 2>&1 &
  PID=$!
  STARTED=1
  trap 'kill "$PID" >/dev/null 2>&1 || true' EXIT
  ready=0
  for _ in $(seq 1 50); do
    if curl -sf "${BASE_URL}/health" >/dev/null 2>&1; then
      ready=1
      break
    fi
    if ! kill -0 "$PID" 2>/dev/null; then
      echo "Control tower exited before /health responded"
      cat /tmp/revenueops-smoke.log
      exit 1
    fi
    sleep 0.2
  done
  if [[ "$ready" -ne 1 ]]; then
    echo "Timed out waiting for ${BASE_URL}/health"
    cat /tmp/revenueops-smoke.log
    exit 1
  fi
fi

BASE_URL="$BASE_URL" PORT="$PORT" "$PYTHON" "$ROOT/scripts/smoke_checks.py"

if [[ -f "$ROOT/frontend/dist/index.html" ]]; then
  curl -sf "${BASE_URL}/" | grep -q "RevenueOps"
  echo "UI shell: PASS"
fi

echo "smoke: PASS"
if [[ "$STARTED" -eq 1 ]]; then
  kill "$PID" >/dev/null 2>&1 || true
  trap - EXIT
fi
