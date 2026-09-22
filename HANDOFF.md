# HANDOFF — RevenueOps Agent Control Tower

Suggested studio badge: **Early**.

The native operator demo is working and can be promoted to **Live** after this repo
has its own public host. Do not mark it Live by pointing at Agent Fleet, AgentOps
Studio, Agent OS, or the RAG lab.

| Layer | Label | What that means |
|---|---|---|
| Operator demo | Live | Agents, KPIs, alerts, workflows, citations, audit, and evals run with `bash scripts/serve.sh` |
| Sandbox Gmail / Slack / GitHub | Early | Drafts and allowlists work. Nothing is sent |
| Approval mode | Early | Local tools still run. External sends stop and the workflow is `blocked` |
| Real mode | Early | Allowlists are checked, then external tools fail closed. No credentials ship in this repo |
| Retrieval | Early | In-memory keyword search with citations. Not pgvector |
| MCP | Early | `retrieve_docs` and `triage_ticket` over the same store |
| Postgres, Redis, Celery, LiteLLM | Building | Present as optional Compose or settings. Not on the demo path |
| Kubernetes and Terraform | Building | Skeletons. Not applied |
| Public Contabo / sslip host | Building | Runbook only, in `docs/contabo-sslip.md`. No URL is claimed |

## Demo

```bash
cp .env.example .env
bash scripts/serve.sh
```

Open `http://127.0.0.1:8060`.

1. The tower loads seeded accounts, alerts, agents, and three replayed workflows.
2. Click **Run sandbox workflow**. The default case is Acme AI's SSO failure before a security review.
3. The timeline cites `security-sso.md`, classifies the ticket as high, prepares a sandbox Slack post, and drafts a Gmail message that is not sent.
4. Open **Evidence** and search `SSO security review`.
5. Open **Evals** and run the suite. Expect `3/3 passed`.
6. Open **Readiness** for the Live / Early / Building split.

Ports: API + UI `8060`, Vite dev `3066`. Do not bind Fleet `8000`/`3002`, RAG `8402`, Agent OS `8090`, or AgentOps `8010`/`3010`.

`/health` returns `product=revenueops-control-tower`, `host=0.0.0.0`, and `port`.

## Verification on this cloud VM (no Docker)

| Check | Result |
|---|---|
| `pytest backend/tests` | 24 passed |
| `ruff check backend mcp_server evals` | pass |
| `npm run test`, `npm run lint`, `npm run build` | pass |
| `bash scripts/smoke.sh` | pass, including the built UI shell |
| Browser, desktop | Tower KPIs and queue render from the API. Sandbox run `wf_680194309edd` completed with a `security-sso.md` citation, high triage, sandbox Slack, and a sandbox Gmail draft |
| Browser, evidence search | `SSO security review` returns `security-sso.md` at score 1 |
| Browser, evals | `3/3 passed` |
| Browser, 390px width | Nav, run button, KPIs, and queue remain reachable |

Screenshots: `docs/screenshots/tower.png`, `docs/screenshots/workflow.png`, `docs/screenshots/evidence.png`, `docs/screenshots/tower-mobile.png`.

## What a stranger should not be told

- This is not Agent Fleet and it does not use that product's host.
- Keyword search is not pgvector.
- Sandbox drafts are not sent mail, Slack messages, or GitHub issues.
- Compose, Kubernetes, and Terraform are not required and were not applied here.
