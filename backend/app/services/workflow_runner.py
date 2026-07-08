from typing import TypedDict

from langgraph.graph import END, StateGraph

from backend.app.agents.supervisor import build_startup_revenue_plan
from backend.app.models.workflow import (
    AgentEvent,
    WorkflowExecutionResult,
    WorkflowPlan,
    WorkflowRequest,
    WorkflowRun,
)
from backend.app.tools.executor import execute_tool


class WorkflowState(TypedDict):
    request: WorkflowRequest
    plan: WorkflowPlan | None
    events: list[AgentEvent]


workflow_runs: dict[str, WorkflowRun] = {}
workflow_events: dict[str, list[AgentEvent]] = {}


def _supervisor_node(state: WorkflowState) -> dict[str, object]:
    plan = build_startup_revenue_plan(state["request"])
    event = AgentEvent(
        workflow_id=plan.workflow_id,
        sequence=1,
        agent="SupervisorAgent",
        event_type="workflow.planned",
        message=f"Planned {len(plan.steps)} specialist agent steps.",
        tools=[],
    )
    return {"plan": plan, "events": [event]}


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
                payload=_payload_for_tool(tool_name, state["request"]),
            )
            for tool_name in step.tools
        ]
        events.append(
            AgentEvent(
                workflow_id=plan.workflow_id,
                sequence=len(events) + 1,
                agent=step.agent,
                event_type="agent.completed",
                message=step.purpose,
                tools=step.tools,
                tool_calls=tool_calls,
            )
        )
    return {"events": events}


def _payload_for_tool(tool_name: str, request: WorkflowRequest) -> dict[str, str]:
    if tool_name == "send_gmail":
        return {
            "to": "trial.customer@sandbox.example.com",
            "subject": "Support follow-up from RevenueOps agent",
            "body": request.objective,
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
        return {"company": "Acme AI"}
    return {"target": request.objective}


def build_agent_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("supervisor", _supervisor_node)
    graph.add_node("workers", _worker_node)
    graph.set_entry_point("supervisor")
    graph.add_edge("supervisor", "workers")
    graph.add_edge("workers", END)
    return graph.compile()


def run_agent_workflow(request: WorkflowRequest) -> WorkflowExecutionResult:
    graph = build_agent_graph()
    final_state = graph.invoke({"request": request, "plan": None, "events": []})
    plan = final_state["plan"]
    if plan is None:
        raise ValueError("Workflow finished without a plan.")

    run = WorkflowRun(workflow_id=plan.workflow_id, status="completed", plan=plan)
    events = final_state["events"]
    workflow_runs[run.workflow_id] = run
    workflow_events[run.workflow_id] = events
    return WorkflowExecutionResult(run=run, events=events)


def get_workflow_run(workflow_id: str) -> WorkflowRun | None:
    return workflow_runs.get(workflow_id)


def get_workflow_events(workflow_id: str) -> list[AgentEvent]:
    return workflow_events.get(workflow_id, [])
