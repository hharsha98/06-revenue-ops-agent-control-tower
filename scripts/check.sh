#!/usr/bin/env bash
set -euo pipefail

.venv/bin/python -m pytest backend/tests -q
.venv/bin/ruff check backend
(cd frontend && npm run lint && npm run build)

