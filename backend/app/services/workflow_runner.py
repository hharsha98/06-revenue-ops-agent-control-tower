from typing import TypedDict

from langgraph.graph import END, StateGraph

from backend.app.agents.supervisor import build_startup_revenue_plan
from backend.app.models.workflow import (
    AgentEvent,
    ToolCall,
    WorkflowExecutionResult,
    WorkflowPlan,
    WorkflowRequest,
    WorkflowRun,
)
from backend.app.services.alerts import raise_live_alert
from backend.app.services.audit_log import audit_log
from backend.app.services.leads import company_from_text, match_lead
from backend.app.tools.executor import execute_tool

INJECTION_MARKERS = (
    "ignore previous",
    "ignore all instructions",
    "disregard the system",
    "exfiltrate",
    "reveal your prompt",
)


class WorkflowState(TypedDict):
    request: WorkflowRequest
    plan: WorkflowPlan | None
    events: list[AgentEvent]


workflow_runs: dict[str, WorkflowRun] = {}
workflow_events: dict[str, list[AgentEvent]] = {}


def _supervisor_node(state: WorkflowState) -> dict[str, object]:
    plan = build_startup_revenue_plan(state["request"])
    names = ", ".join(step.agent for step in plan.steps)
    event = AgentEvent(
        workflow_id=plan.workflow_id,
        sequence=1,
        agent="SupervisorAgent",
        event_type="workflow.planned",
        message=f"Planned {len(plan.steps)} specialist agent steps: {names}.",
        tools=[],
    )
    return {"plan": plan, "events": [event]}


def _snippet_from(events: list[AgentEvent]) -> str:
    for event in reversed(events):
        for call in reversed(event.tool_calls):
            snippet = call.details.get("snippet", "")
            if snippet:
                return snippet
    return ""


def _company(request: WorkflowRequest) -> str:
    if request.account:
        lead = match_lead(request.account)
        return str(lead["company"]) if lead else request.account
    return company_from_text(request.objective)


def _payload_for_tool(tool_name: str, request: WorkflowRequest, events: list[AgentEvent]) -> dict[str, str]:
    company = _company(request)
    if tool_name == "send_gmail":
        return {
            "to": "trial.customer@sandbox.example.com",
            "objective": request.objective,
            "body": request.objective,
            "evidence": _snippet_from(events),
        }
    if tool_name == "post_slack":
        return {"channel": "demo-alerts", "message": request.objective}
    if tool_name == "create_github_issue":
        return {
            "repo": "demo/revenueops-agent-control-tower",
            "title": "Agent-created customer escalation",
            "body": request.objective,
        }
    if tool_name == "retrieve_docs":
        return {"query": request.objective}
    if tool_name == "triage_ticket":
        return {"ticket": request.objective}
    if tool_name == "score_lead":
        return {"company": company}
    if tool_name == "search_web":
        return {"query": request.objective, "company": company}
    return {"target": request.objective, "company": company}


def _risk_message(request: WorkflowRequest, events: list[AgentEvent]) -> str:
    notes: list[str] = []
    objective = request.objective.lower()
    if any(marker in objective for marker in INJECTION_MARKERS):
        notes.append(
            "Prompt-injection markers detected. Any customer draft stays in the sandbox and is not delivered."
        )
    citations = [
        call.details.get("citations", "")
        for event in events
        for call in event.tool_calls
        if call.tool_name == "retrieve_docs" and call.details.get("citations")
    ]
    if citations:
        notes.append(f"Citations attached: {citations[-1]}.")
    elif any(event.agent == "KnowledgeAgent" for event in events):
        notes.append("Knowledge step ran without a citation hit.")
    if request.autonomy_mode == "sandbox":
        notes.append("Sandbox mode: external tools stay simulated.")
    elif request.autonomy_mode == "approval":
        notes.append("Approval mode: external tools wait for an operator.")
    else:
        notes.append("Real mode fails closed until live credentials exist.")
    return " ".join(notes)


def _event_message(agent: str, purpose: str, request: WorkflowRequest, events: list[AgentEvent], tool_calls: list[ToolCall]) -> str:
    if agent == "RiskGuardAgent":
        return _risk_message(request, events)
    if agent == "KnowledgeAgent" and tool_calls:
        snippet = tool_calls[0].details.get("snippet", "")
        if snippet:
            return f"Retrieved grounded evidence. {snippet}"
    if tool_calls:
        return tool_calls[0].summary
    return purpose


def _worker_node(state: WorkflowState) -> dict[str, object]:
    plan = state["plan"]
    if plan is None:
        raise ValueError("Workflow plan is missing before worker execution.")

    events = list(state["events"])
    for step in plan.steps:
        tool_calls = [
            execute_tool(
                tool_name=tool_name,
                autonomy_mode=state["request"].autonomy_mode,
                payload=_payload_for_tool(tool_name, state["request"], events),
            )
            for tool_name in step.tools
        ]
        events.append(
            AgentEvent(
                workflow_id=plan.workflow_id,
                sequence=len(events) + 1,
                agent=step.agent,
                event_type="agent.completed",
                message=_event_message(step.agent, step.purpose, state["request"], events, tool_calls),
                tools=step.tools,
                tool_calls=tool_calls,
            )
        )
    return {"events": events}


def build_agent_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("supervisor", _supervisor_node)
    graph.add_node("workers", _worker_node)
    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "workers")
    graph.add_edge("workers", END)
    return graph.compile()


def _record_side_effects(request: WorkflowRequest, run: WorkflowRun, events: list[AgentEvent]) -> None:
    audit_log.record(
        "workflow.completed" if run.status == "completed" else "workflow.blocked",
        f"{run.status}: {request.objective}",
        workflow_id=run.workflow_id,
    )
    for event in events:
        for call in event.tool_calls:
            audit_log.record(
                f"tool.{call.tool_name}",
                call.summary,
                workflow_id=run.workflow_id,
            )
            if call.tool_name == "triage_ticket" and call.details.get("urgency") == "high":
                account = _company(request) or "Unassigned"
                raise_live_alert(
                    alert_id=f"alert_live_{run.workflow_id}",
                    severity="high",
                    title=f"High-urgency triage for {account}",
                    detail=call.summary,
                    account=account,
                    owner_agent="TicketTriageAgent",
                )


def run_agent_workflow(request: WorkflowRequest) -> WorkflowExecutionResult:
    graph = build_agent_graph()
    final_state = graph.invoke({"request": request, "plan": None, "events": []})
    plan = final_state["plan"]
    if plan is None:
        raise ValueError("Workflow finished without a plan.")

    events = final_state["events"]
    blocked = any(not call.allowed for event in events for call in event.tool_calls)
    run = WorkflowRun(
        workflow_id=plan.workflow_id,
        status="blocked" if blocked else "completed",
        plan=plan,
        objective=request.objective,
        autonomy_mode=request.autonomy_mode,
    )
    workflow_runs[run.workflow_id] = run
    workflow_events[run.workflow_id] = events
    _record_side_effects(request, run, events)
    return WorkflowExecutionResult(run=run, events=events)


def get_workflow_run(workflow_id: str) -> WorkflowRun | None:
    return workflow_runs.get(workflow_id)


def get_workflow_events(workflow_id: str) -> list[AgentEvent]:
    return workflow_events.get(workflow_id, [])


def list_workflow_runs() -> list[WorkflowRun]:
    return list(reversed(workflow_runs.values()))
