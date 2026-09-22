from fastapi import APIRouter, HTTPException

from backend.app.models.knowledge import (
    DocumentIngestResponse,
    DocumentUploadRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from backend.app.models.tower import Account, AgentCard, Alert, DocumentRecord, Overview, Scenario
from backend.app.models.workflow import AgentEvent, AuditEvent, ToolCall, ToolExecuteRequest, WorkflowRequest, WorkflowRun
from backend.app.services.alerts import acknowledge_alert, list_alerts
from backend.app.services.audit_log import audit_log
from backend.app.services.bootstrap import ensure_demo_ready
from backend.app.services.catalog import SCENARIOS
from backend.app.services.evals_runner import run_eval_suite
from backend.app.services.knowledge import knowledge_store
from backend.app.services.overview import build_overview, load_accounts
from backend.app.services.workflow_runner import (
    get_workflow_events,
    get_workflow_run,
    list_workflow_runs,
    run_agent_workflow,
)
from backend.app.tools.executor import execute_tool
from backend.app.tools.registry import build_tool_registry

router = APIRouter()


@router.get("/overview", response_model=Overview)
def get_overview() -> Overview:
    ensure_demo_ready()
    return build_overview()


@router.get("/agents", response_model=list[AgentCard])
def get_agents() -> list[AgentCard]:
    ensure_demo_ready()
    return build_overview().agents


@router.get("/scenarios", response_model=list[Scenario])
def get_scenarios() -> list[Scenario]:
    return list(SCENARIOS)


@router.get("/accounts", response_model=list[Account])
def get_accounts() -> list[Account]:
    return load_accounts()


@router.get("/alerts", response_model=list[Alert])
def get_alerts() -> list[Alert]:
    ensure_demo_ready()
    return list_alerts()


@router.post("/alerts/{alert_id}/acknowledge", response_model=Alert)
def acknowledge(alert_id: str) -> Alert:
    ensure_demo_ready()
    alert = acknowledge_alert(alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    audit_log.record("alert.acknowledged", f"Operator acknowledged {alert.title}.")
    return alert


@router.post("/workflows/run", response_model=WorkflowRun)
def run_workflow(request: WorkflowRequest) -> WorkflowRun:
    ensure_demo_ready()
    return run_agent_workflow(request).run


@router.get("/workflows", response_model=list[WorkflowRun])
def list_workflows() -> list[WorkflowRun]:
    ensure_demo_ready()
    return list_workflow_runs()


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


@router.get("/documents", response_model=list[DocumentRecord])
def list_documents() -> list[DocumentRecord]:
    ensure_demo_ready()
    return knowledge_store.list_documents()


@router.post("/documents/search", response_model=KnowledgeSearchResponse)
def search_documents(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    ensure_demo_ready()
    return KnowledgeSearchResponse(
        query=request.query,
        results=knowledge_store.search(request.query, request.limit),
    )


@router.post("/evals/run")
def run_evals() -> dict:
    ensure_demo_ready()
    report = run_eval_suite()
    audit_log.record("evals.completed", f"Eval suite {report['score']} {report['status']}.")
    return report


@router.get("/audit", response_model=list[AuditEvent])
def get_audit_events() -> list[AuditEvent]:
    ensure_demo_ready()
    return audit_log.list_events()


@router.get("/tools", response_model=dict)
def list_tools() -> dict:
    return build_tool_registry()


@router.post("/tools/execute", response_model=ToolCall)
def execute_registered_tool(request: ToolExecuteRequest) -> ToolCall:
    ensure_demo_ready()
    return execute_tool(
        tool_name=request.tool_name,
        autonomy_mode=request.autonomy_mode,
        payload=request.payload,
    )
