#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

"$ROOT/.venv/bin/python" -m pytest backend/tests -q
"$ROOT/.venv/bin/ruff" check backend mcp_server evals
(cd "$ROOT/frontend" && npm run test && npm run lint && npm run build)
bash "$ROOT/scripts/smoke.sh"
