from backend.app.models.tower import AgentProfile, Readiness, Scenario

AGENTS: list[AgentProfile] = [
    AgentProfile(
        name="SupervisorAgent",
        role="Plans the workflow, routes specialists, and checks that the run finished.",
        tools=[],
    ),
    AgentProfile(
        name="ResearchAgent",
        role="Researches the account and scores startup fit from the seeded book of business.",
        tools=["search_web", "score_lead"],
    ),
    AgentProfile(
        name="KnowledgeAgent",
        role="Retrieves grounded product evidence and returns citations.",
        tools=["retrieve_docs"],
    ),
    AgentProfile(
        name="TicketTriageAgent",
        role="Classifies urgency, topic, and owner, then prepares a sandbox Slack alert.",
        tools=["triage_ticket", "post_slack"],
    ),
    AgentProfile(
        name="RiskGuardAgent",
        role="Checks citations, prompt-injection markers, and the autonomy policy.",
        tools=[],
    ),
    AgentProfile(
        name="OutreachAgent",
        role="Drafts the customer email. Sandbox mode never sends it.",
        tools=["send_gmail", "read_gmail"],
    ),
    AgentProfile(
        name="EngineeringHandoffAgent",
        role="Prepares a GitHub issue when product or docs work is required.",
        tools=["create_github_issue"],
    ),
]

SCENARIOS: list[Scenario] = [
    Scenario(
        id="pricing-follow-up",
        title="Pricing follow-up",
        account="Acme AI",
        source="manual",
        objective="Research Acme AI and draft a pricing follow-up.",
        summary="Research scores the account, then Outreach drafts a pricing note.",
    ),
    Scenario(
        id="stale-onboarding",
        title="Stale onboarding docs",
        account="Northline Health",
        source="github",
        objective="If onboarding docs are stale, create an engineering issue.",
        summary="Knowledge cites the onboarding guide and Engineering prepares a sandbox issue.",
    ),
    Scenario(
        id="sso-security-review",
        title="SSO failure before security review",
        account="Acme AI",
        source="gmail",
        objective="Customer says SSO fails before security review. Answer from docs and escalate if needed.",
        summary="The interview path: cite SSO docs, triage high, guard the draft, do not send.",
    ),
]

READINESS = Readiness(
    recommended_badge="Early",
    summary=(
        "The native operator demo is working: agents, KPIs, alerts, workflows, evidence, "
        "evals, and audit all run without Docker or paid services. Promote the studio card "
        "to Live only after this product has its own public host. Do not borrow another product's URL."
    ),
    live=[
        "Native control tower on one port (API + built UI)",
        "Seeded accounts, alerts, and company evidence",
        "Supervisor workflow with specialist agents and citations",
        "Sandbox Gmail, Slack, and GitHub drafts with allowlists",
        "Eval dataset, audit trail, and /health",
    ],
    early=[
        "External tools are simulated. Live mode fails closed without credentials",
        "Approval mode records a checkpoint and does not send",
        "MCP exposes retrieve and triage over the same in-memory store",
        "Docker Compose is optional and not required to demo",
    ],
    building=[
        "Postgres and pgvector are schema-only. Retrieval is in-memory keyword search",
        "Celery and Redis are not on the demo path",
        "No live Gmail, Slack, GitHub, or model calls",
        "Kubernetes and Terraform are not applied",
        "No public Contabo or sslip host is deployed for this repo",
    ],
)
