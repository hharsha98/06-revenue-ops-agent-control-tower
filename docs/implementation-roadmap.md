# Implementation Roadmap

## Status against this roadmap

| Phase | Label | Notes |
|---|---|---|
| 0 Scaffold | Live | API, UI, tests, Compose, CI |
| 1 Ingestion | Early | Upload, chunk, and search work in memory. pgvector is not the runtime |
| 2 Agent graph | Early | LangGraph supervisor plus one worker node. Not a separate node per agent |
| 3 Live tools | Early | Sandbox drafts and allowlists. No live OAuth |
| 4 Evals | Live | Fixed 3-case routing suite shown in the UI |
| 5 Enterprise deploy | Building | Compose optional. Kubernetes and Terraform are not applied |

## Phase 0: Scaffold

- Create backend, frontend, docs, sample data, Docker, Kubernetes, Terraform, and CI skeleton.
- Verify backend tests and frontend build/lint.

## Phase 1: Data and ingestion

- Add real file upload.
- Store documents in Postgres.
- Chunk and embed into pgvector.
- Add retrieval tests with deterministic fixtures.

## Phase 2: Agent graph

- Replace deterministic supervisor planner with LangGraph state graph.
- Add mocked tools first.
- Stream agent events to the frontend.

## Phase 3: Live tools

- Add Gmail, Slack, and GitHub adapters.
- Keep sandbox mode as default.
- Add allowlist enforcement tests for every external action.

## Phase 4: Evals

- Add fixed eval dataset.
- Measure citation coverage, tool success, triage accuracy, latency, and cost.
- Show eval results in frontend.

## Phase 5: Enterprise deployment

- Build Docker images.
- Run local stack with Docker Compose.
- Validate Kubernetes manifests.
- Add Terraform plan for AWS EKS, ECR, RDS, ElastiCache, and IAM.
- Add Prometheus/Grafana and OpenTelemetry wiring.

