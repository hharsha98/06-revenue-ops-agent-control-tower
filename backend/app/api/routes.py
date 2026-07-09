from fastapi import APIRouter, HTTPException

from backend.app.models.knowledge import (
    DocumentIngestResponse,
    DocumentUploadRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from backend.app.models.evals import EvaluationReport
from backend.app.models.workflow import AgentEvent, AuditEvent, ToolCall, ToolExecuteRequest, WorkflowRequest, WorkflowRun
from backend.app.services.evals import run_fixed_eval_suite
from backend.app.services.knowledge import knowledge_store
from backend.app.services.workflow_runner import (
    get_workflow_events,
    get_workflow_run,
    run_agent_workflow,
)
from backend.app.tools.executor import execute_tool
from backend.app.tools.registry import build_tool_registry

router = APIRouter()


@router.post("/workflows/run", response_model=WorkflowRun)
def run_workflow(request: WorkflowRequest) -> WorkflowRun:
    return run_agent_workflow(request).run


@router.get("/workflows/{workflow_id}", response_model=WorkflowRun)
def get_workflow(workflow_id: str) -> WorkflowRun:
    run = get_workflow_run(workflow_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return run


@router.get("/workflows/{workflow_id}/events", response_model=list[AgentEvent])
def list_workflow_events(workflow_id: str) -> list[AgentEvent]:
    events = get_workflow_events(workflow_id)
    if not events:
        raise HTTPException(status_code=404, detail="Workflow events not found")
    return events


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


@router.post("/evals/run", response_model=EvaluationReport)
def run_evals() -> EvaluationReport:
    return run_fixed_eval_suite()


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


@router.post("/tools/execute", response_model=ToolCall)
def execute_registered_tool(request: ToolExecuteRequest) -> ToolCall:
    return execute_tool(
        tool_name=request.tool_name,
        autonomy_mode=request.autonomy_mode,
        payload=request.payload,
    )
