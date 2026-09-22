# 06 · RevenueOps Agent Control Tower

Operator console for a startup founder or COO. One supervisor agent routes specialist
agents across a seeded book of business: research, cited knowledge, ticket triage,
sandbox Gmail / Slack / GitHub drafts, a risk check, an audit trail, and a fixed eval set.

This repository is **not** Agent Fleet, AgentOps Studio, Agent OS, or the RAG lab.
It does not publish those hosts, and it does not borrow their ports.

| | This repo | Leave these alone |
|---|---|---|
| What it is | Revenue ops control tower demo | Other portfolio products |
| Native ports | API + UI **8060**, Vite dev **3066** | Fleet 8000 / 3002, RAG 8402, Agent OS 8090, AgentOps 8010 / 3010 |
| Public URL | None in this build | Do not point this product at another product's host |

Suggested [Agentic Systems Studio](https://agentic-systems-studio.com/) badge: **Early**.
The operator demo itself runs. A public host for this repo is still Building.
See [HANDOFF.md](HANDOFF.md).

## Demo (native, no Docker)

Requirements: Python 3.12 with `python3-venv`, Node.js 22, npm.

```bash
cp .env.example .env
bash scripts/serve.sh
```

Open `http://127.0.0.1:8060`.

1. The tower is already populated: accounts, alerts, agents, and three replayed workflows.
2. Click **Run sandbox workflow**. The default objective is the Acme AI SSO security review.
3. Open **Workflow**, **Evidence**, **Alerts**, **Audit**, and **Evals**.
4. On **Evals**, click **Run eval suite**. The fixed set should report `3/3`.
5. On **Evidence**, search `SSO security review` and read the citation from `security-sso.md`.

`scripts/serve.sh` binds `0.0.0.0` and `PORT` (default `8060`), serves `/health`, and
serves the built UI from the same process.

### Two terminals, if you are changing the UI

```bash
bash scripts/dev-api.sh          # http://127.0.0.1:8060
cd frontend && npm install && npm run dev   # http://127.0.0.1:3066
```

Vite proxies `/api` and `/health` to port 8060.

### Smoke

```bash
bash scripts/smoke.sh
```

Smoke starts the API if it is not already up, checks health, the tower payload,
a cited SSO workflow, the audit trail, the eval suite, and a blocked real-mode
GitHub call. It does not use Docker. `bash scripts/check.sh` runs unit tests,
lint, the frontend build, and smoke.

## What the demo actually does

- Loads six company documents, three accounts, and the operator alert queue.
- Replays three scenarios through a LangGraph supervisor → worker graph.
- Knowledge search is in-memory keyword overlap with citations. It is not pgvector.
- Gmail, Slack, and GitHub run as sandbox drafts. Real mode fails closed because
  this build has no live credentials.
- Evals check supervisor routing against `evals/dataset.jsonl`.

## Optional Docker

Compose is optional. The hiring-manager path above does not need it.

```bash
docker compose up --build
```

API: `http://127.0.0.1:8060`. UI container: `http://127.0.0.1:3066` (nginx proxies `/api`).
Postgres and Redis start with Compose and are **not** used by the native demo.

## Contabo / sslip

See [docs/contabo-sslip.md](docs/contabo-sslip.md). Use port **8060** on this product's
own host. Do not reuse another product's public URL.

## Safety

Autonomy defaults to `sandbox`. Allowlists still apply in `real` mode, and external
side effects stay blocked until credentials exist — which they do not in this demo.

## Layout

- `backend/app` — FastAPI, LangGraph workflow, tools, tower read model
- `frontend` — React operator console
- `sample-data` — accounts, tickets, alerts, and company documents
- `evals` — fixed routing dataset
- `mcp_server` — retrieve and triage tools over the same store
- `infra` — Kubernetes and Terraform skeletons (not applied)

## Architecture

See [docs/architecture.md](docs/architecture.md) and [docs/demo-script.md](docs/demo-script.md).
