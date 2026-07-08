# Architecture

## Goal

Build an enterprise-style control tower where one supervisor agent coordinates specialist
agents that use real business tools while preserving auditability, evals, and safe defaults.

## Runtime pieces

- React dashboard: operator UI, workflow canvas, timeline, Kanban, evals, observability.
- FastAPI backend: workflow API, audit API, document ingestion API, eval trigger API.
- LangGraph agent layer: supervisor routes to specialist agents.
- FastMCP server: exposes tool contracts for agent-to-tool usage.
- Postgres + pgvector: business records and document embeddings.
- Redis + Celery: background ingestion, tool execution, evals, and long-running workflows.
- LiteLLM: one model gateway for Gemini, OpenAI, Anthropic, Mistral, or OpenAI-compatible models.
- Observability: Langfuse for LLM traces, OpenTelemetry/Prometheus/Grafana for service metrics.

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
- `approval`: tools draft actions but require human approval.
- `real`: tools may execute only when target allowlists match.

Default mode is `sandbox`.

## Build order

1. Scaffold and tests.
2. Real document ingestion and pgvector search.
3. LangGraph supervisor with mocked tools.
4. Gmail, Slack, GitHub sandbox adapters.
5. Evals and prompt-injection checks.
6. Real integration mode.
7. Kubernetes, Terraform, and observability hardening.

