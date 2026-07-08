from backend.app.models.workflow import WorkflowRequest
from backend.app.services.workflow_runner import run_agent_workflow


def test_runner_executes_agent_plan_and_records_ordered_events():
    result = run_agent_workflow(
        WorkflowRequest(
            objective="Customer says SSO fails before security review. Answer from docs and escalate if needed.",
            source="gmail",
            autonomy_mode="sandbox",
        )
    )

    assert result.run.status == "completed"
    assert [event.agent for event in result.events] == [
        "SupervisorAgent",
        "KnowledgeAgent",
        "TicketTriageAgent",
        "RiskGuardAgent",
        "OutreachAgent",
    ]
    assert result.events[0].sequence == 1
    assert result.events[-1].event_type == "agent.completed"
    assert result.events[-1].tools == ["send_gmail"]
    assert result.events[-1].tool_calls[0].tool_name == "send_gmail"
    assert result.events[-1].tool_calls[0].execution_mode == "simulated"
