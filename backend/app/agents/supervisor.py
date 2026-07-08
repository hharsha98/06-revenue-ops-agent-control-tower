from backend.app.models.workflow import AgentStep, WorkflowPlan, WorkflowRequest


def build_startup_revenue_plan(request: WorkflowRequest) -> WorkflowPlan:
    objective = request.objective.lower()
    steps: list[AgentStep] = []

    if any(keyword in objective for keyword in ["lead", "pricing", "account", "follow-up"]):
        steps.append(
            AgentStep(
                agent="ResearchAgent",
                purpose="Research account context and score startup fit.",
                tools=["search_web", "score_lead"],
            )
        )

    if any(keyword in objective for keyword in ["support", "question", "asked", "docs", "sso", "answer"]):
        steps.append(
            AgentStep(
                agent="KnowledgeAgent",
                purpose="Retrieve grounded product/support evidence with citations.",
                tools=["retrieve_docs"],
            )
        )

    if any(keyword in objective for keyword in ["ticket", "support", "issue", "failing", "fails", "bug", "escalate"]):
        steps.append(
            AgentStep(
                agent="TicketTriageAgent",
                purpose="Classify urgency, owner, customer impact, and escalation path.",
                tools=["triage_ticket"],
            )
        )

    if any(keyword in objective for keyword in ["issue", "bug", "stale", "github"]):
        steps.append(
            AgentStep(
                agent="EngineeringHandoffAgent",
                purpose="Create an engineering issue when product or docs work is needed.",
                tools=["create_github_issue"],
            )
        )

    steps.append(
        AgentStep(
            agent="RiskGuardAgent",
            purpose="Check citations, unsafe instructions, prompt injection, and autonomy rules.",
            tools=[],
        )
    )

    if request.source in {"gmail", "manual"}:
        steps.append(
            AgentStep(
                agent="OutreachAgent",
                purpose="Draft or send the customer-facing response according to autonomy mode.",
                tools=["send_gmail"],
            )
        )

    safety_notes: list[str] = []
    requires_approval = request.autonomy_mode in {"approval", "real"}
    if request.autonomy_mode == "real":
        safety_notes.append("real-account mode requires allowlisted recipients")

    return WorkflowPlan(
        workflow_name="customer-support-revenueops",
        steps=steps,
        requires_approval=requires_approval,
        safety_notes=safety_notes,
    )
