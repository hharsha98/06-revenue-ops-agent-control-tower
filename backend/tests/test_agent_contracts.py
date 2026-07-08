from backend.app.agents.supervisor import build_startup_revenue_plan
from backend.app.models.workflow import WorkflowRequest


def test_supervisor_plan_routes_support_email_to_knowledge_ticket_and_risk_agents():
    request = WorkflowRequest(
        objective="Customer asked why SSO is failing and wants an answer today.",
        source="gmail",
        autonomy_mode="sandbox",
    )

    plan = build_startup_revenue_plan(request)

    assert plan.workflow_name == "customer-support-revenueops"
    assert [step.agent for step in plan.steps] == [
        "KnowledgeAgent",
        "TicketTriageAgent",
        "RiskGuardAgent",
        "OutreachAgent",
    ]
    assert plan.requires_approval is False


def test_supervisor_plan_for_real_autonomy_requires_allowlisted_target():
    request = WorkflowRequest(
        objective="Send a pricing follow-up to a lead and create an issue if docs are stale.",
        source="gmail",
        autonomy_mode="real",
    )

    plan = build_startup_revenue_plan(request)

    assert plan.requires_approval is True
    assert "real-account mode requires allowlisted recipients" in plan.safety_notes

