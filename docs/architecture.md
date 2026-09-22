# Architecture

## Goal

Build an enterprise-style control tower where one supervisor agent coordinates specialist
agents that use real business tools while preserving auditability, evals, and safe defaults.

## What runs in the native demo

- React operator console, served by FastAPI from `frontend/dist` on port 8060.
- FastAPI read model for KPIs, alerts, accounts, documents, workflows, audit, and evals.
- LangGraph graph with a supervisor node and a worker node. The worker executes the
  planned specialist steps in order and records tool calls.
- In-memory document store with keyword overlap and citations. Seeded from `sample-data/documents`.
- Sandbox adapters for Gmail, Slack, and GitHub. Real mode fails closed.
- Fixed eval dataset in `evals/dataset.jsonl`.

## Present in the repo, not on the demo path

- Postgres + pgvector schema and optional Compose services. The API does not embed or query them.
- Redis + Celery health task. Workflows run in-process.
- LiteLLM settings. The demo does not call a model.
- Langfuse, Prometheus, and Grafana are not wired.
- Kubernetes and Terraform files are skeletons. They are not applied.

## Runtime pieces the product is aimed at

- React dashboard: operator UI, workflow canvas, timeline, alerts, evals.
- FastAPI backend: workflow API, audit API, document ingestion API, eval API.
- LangGraph agent layer: supervisor routes to specialist agents.
- FastMCP server: retrieve and triage over the same in-memory store.
- Postgres + pgvector: intended store for business records and embeddings.
- Redis + Celery: intended background workers.
- LiteLLM: intended model gateway. Not used by the sandbox demo.

## Agent responsibilities

| Agent | Responsibility | Tools |
|---|---|---|
| SupervisorAgent | Plan, route, check completion, enforce mode | all |
| ResearchAgent | Research account/customer context | `search_web`, `score_lead` |
| KnowledgeAgent | Answer from docs with citations | `retrieve_docs` |
| TicketTriageAgent | Classify urgency, topic, owner | `triage_ticket`, `post_slack` |
| OutreachAgent | Draft/send customer messages | `read_gmail`, `send_gmail` |
| EngineeringHandoffAgent | Create engineering work items | `create_github_issue` |
| RiskGuardAgent | Check citations, unsafe instructions, allowlists | audit + policy |

## Safety model

- `sandbox`: tools simulate external actions.
- `approval`: external tools stop at a checkpoint and are not sent.
- `real`: allowlists are checked, then Gmail, Slack, and GitHub fail closed.
  This build does not ship live credentials, so a passing allowlist still sends nothing.

Default mode is `sandbox`.

## Build order

1. Scaffold and tests.
2. Real document ingestion and pgvector search.
3. LangGraph supervisor with mocked tools.
4. Gmail, Slack, GitHub sandbox adapters.
5. Evals and prompt-injection checks.
6. Real integration mode.
7. Kubernetes, Terraform, and observability hardening.

