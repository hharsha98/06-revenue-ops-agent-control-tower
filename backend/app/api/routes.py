from fastapi import APIRouter

from backend.app.agents.supervisor import build_startup_revenue_plan
from backend.app.models.knowledge import (
    DocumentIngestResponse,
    DocumentUploadRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from backend.app.models.workflow import AuditEvent, WorkflowRequest, WorkflowRun
from backend.app.services.knowledge import knowledge_store
from backend.app.tools.registry import build_tool_registry

router = APIRouter()


@router.post("/workflows/run", response_model=WorkflowRun)
def run_workflow(request: WorkflowRequest) -> WorkflowRun:
    plan = build_startup_revenue_plan(request)
    return WorkflowRun(workflow_id=plan.workflow_id, plan=plan)


@router.get("/workflows/{workflow_id}", response_model=dict)
def get_workflow(workflow_id: str) -> dict[str, str]:
    return {"workflow_id": workflow_id, "status": "planned"}


@router.get("/workflows/{workflow_id}/events", response_model=list[AuditEvent])
def get_workflow_events(workflow_id: str) -> list[AuditEvent]:
    return [
        AuditEvent(
            workflow_id=workflow_id,
            event_type="workflow.planned",
            message="Supervisor created an auditable agent plan.",
        )
    ]


@router.post("/documents/upload", response_model=DocumentIngestResponse)
def upload_document(request: DocumentUploadRequest) -> DocumentIngestResponse:
    chunks = knowledge_store.ingest(request)
    return DocumentIngestResponse(source=request.source, chunks_created=len(chunks))


@router.post("/documents/search", response_model=KnowledgeSearchResponse)
def search_documents(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    return KnowledgeSearchResponse(
        query=request.query,
        results=knowledge_store.search(request.query, request.limit),
    )


@router.post("/evals/run", response_model=dict)
def run_evals() -> dict[str, str]:
    return {"status": "stubbed", "next": "run fixed eval dataset through mocked tools"}


@router.get("/audit", response_model=list[AuditEvent])
def get_audit_events() -> list[AuditEvent]:
    return [
        AuditEvent(
            event_type="system.ready",
            message="Audit trail endpoint is wired for Project 06 scaffold.",
        )
    ]


@router.get("/tools", response_model=dict)
def list_tools() -> dict:
    return build_tool_registry()
