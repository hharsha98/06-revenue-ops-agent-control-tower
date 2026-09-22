from backend.app.core.config import settings
from backend.app.models.tower import (
    Account,
    AgentCard,
    KnowledgeStats,
    Kpi,
    Overview,
    WorkflowSummary,
)
from backend.app.models.workflow import AgentEvent
from backend.app.services.alerts import list_alerts
from backend.app.services.audit_log import audit_log
from backend.app.services.catalog import AGENTS, READINESS, SCENARIOS
from backend.app.services.knowledge import knowledge_store
from backend.app.services.leads import load_leads
from backend.app.services.workflow_runner import get_workflow_events, list_workflow_runs

PRODUCT_ID = "revenueops-control-tower"
POSITIONING = (
    "RevenueOps Control Tower is its own portfolio demo. "
    "It does not serve Agent Fleet and this build has no public host."
)


def load_accounts() -> list[Account]:
    accounts: list[Account] = []
    for lead in load_leads():
        accounts.append(
            Account(
                company=str(lead.get("company", "Unknown")),
                segment=str(lead.get("segment", "")),
                team_size=int(lead.get("team_size") or 0),
                signal=str(lead.get("signal", "")),
                fit_score=int(lead.get("fit_score_hint") or 0),
                plan=str(lead.get("plan", "")),
            )
        )
    return accounts


def _agent_cards() -> list[AgentCard]:
    latest: dict[str, str] = {}
    for run in list_workflow_runs():
        for event in get_workflow_events(run.workflow_id):
            latest.setdefault(event.agent, event.message)
    cards: list[AgentCard] = []
    for agent in AGENTS:
        message = latest.get(agent.name, "")
        cards.append(
            AgentCard(
                name=agent.name,
                role=agent.role,
                tools=agent.tools,
                status="ran" if message else "ready",
                last_message=message or "Waiting for a workflow.",
            )
        )
    return cards


def _summaries() -> list[WorkflowSummary]:
    summaries: list[WorkflowSummary] = []
    for run in list_workflow_runs():
        summaries.append(
            WorkflowSummary(
                workflow_id=run.workflow_id,
                status=run.status,
                workflow_name=run.plan.workflow_name,
                objective=run.objective,
                autonomy_mode=run.autonomy_mode,
                agents=[step.agent for step in run.plan.steps],
            )
        )
    return summaries


def _latest_events() -> list[AgentEvent]:
    runs = list_workflow_runs()
    if not runs:
        return []
    return get_workflow_events(runs[0].workflow_id)


def _percent(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "n/a"
    return f"{round(100 * numerator / denominator)}%"


def _kpis() -> list[Kpi]:
    alerts = list_alerts()
    open_alerts = sum(1 for alert in alerts if alert.status == "open")
    runs = list_workflow_runs()
    calls = [
        call
        for run in runs
        for event in get_workflow_events(run.workflow_id)
        for call in event.tool_calls
    ]
    allowed = sum(1 for call in calls if call.allowed)
    knowledge_steps = 0
    cited = 0
    for run in runs:
        for event in get_workflow_events(run.workflow_id):
            if event.agent != "KnowledgeAgent":
                continue
            knowledge_steps += 1
            if any(call.tool_name == "retrieve_docs" and call.details.get("hits") not in {"", "0", None} for call in event.tool_calls):
                cited += 1
    documents = knowledge_store.list_documents()
    return [
        Kpi(
            id="open_alerts",
            label="open alerts",
            value=str(open_alerts),
            detail="Seeded queue plus live triage alerts in this process.",
        ),
        Kpi(
            id="evidence_chunks",
            label="evidence chunks",
            value=str(knowledge_store.chunk_count),
            detail=f"{len(documents)} company documents in the in-memory store.",
        ),
        Kpi(
            id="workflows",
            label="workflows",
            value=str(len(runs)),
            detail="Completed or blocked runs recorded in this process.",
        ),
        Kpi(
            id="tool_success",
            label="tool-call success",
            value=_percent(allowed, len(calls)),
            detail="Allowed tool calls divided by recorded calls. Sandbox drafts count as success.",
        ),
        Kpi(
            id="citation_coverage",
            label="citation coverage",
            value=_percent(cited, knowledge_steps),
            detail="Knowledge steps that returned at least one cited chunk.",
        ),
    ]


def build_overview() -> Overview:
    documents = knowledge_store.list_documents()
    return Overview(
        product=PRODUCT_ID,
        display_name=settings.app_name,
        autonomy_mode=settings.autonomy_mode,
        positioning=POSITIONING,
        recommended_badge=READINESS.recommended_badge,
        readiness=READINESS,
        kpis=_kpis(),
        agents=_agent_cards(),
        alerts=list_alerts(),
        accounts=load_accounts(),
        documents=documents,
        scenarios=SCENARIOS,
        recent_workflows=_summaries(),
        latest_events=_latest_events(),
        audit_events=audit_log.list_events()[:40],
        knowledge=KnowledgeStats(documents=len(documents), chunks=knowledge_store.chunk_count),
    )
