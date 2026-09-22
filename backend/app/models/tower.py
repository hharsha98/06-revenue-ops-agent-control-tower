from typing import Literal

from pydantic import BaseModel, Field

from backend.app.models.workflow import AgentEvent, AuditEvent


class AgentProfile(BaseModel):
    name: str
    role: str
    tools: list[str] = Field(default_factory=list)


class AgentCard(AgentProfile):
    status: Literal["ready", "ran"] = "ready"
    last_message: str = "Waiting for a workflow."


class Scenario(BaseModel):
    id: str
    title: str
    account: str
    source: Literal["gmail", "slack", "github", "manual"]
    objective: str
    summary: str


class Alert(BaseModel):
    id: str
    severity: Literal["critical", "high", "medium", "low"]
    title: str
    detail: str
    account: str
    owner_agent: str
    status: Literal["open", "acknowledged", "resolved"] = "open"
    source: Literal["seed", "live"] = "seed"


class Account(BaseModel):
    company: str
    segment: str
    team_size: int
    signal: str
    fit_score: int
    plan: str = ""


class DocumentRecord(BaseModel):
    source: str
    chunks: int
    preview: str


class Kpi(BaseModel):
    id: str
    label: str
    value: str
    detail: str


class WorkflowSummary(BaseModel):
    workflow_id: str
    status: str
    workflow_name: str
    objective: str
    autonomy_mode: str
    agents: list[str]


class Readiness(BaseModel):
    recommended_badge: Literal["Live", "Early", "Building"]
    summary: str
    live: list[str]
    early: list[str]
    building: list[str]


class KnowledgeStats(BaseModel):
    documents: int
    chunks: int


class Overview(BaseModel):
    product: str
    display_name: str
    autonomy_mode: str
    positioning: str
    recommended_badge: Literal["Live", "Early", "Building"]
    readiness: Readiness
    kpis: list[Kpi]
    agents: list[AgentCard]
    alerts: list[Alert]
    accounts: list[Account]
    documents: list[DocumentRecord]
    scenarios: list[Scenario]
    recent_workflows: list[WorkflowSummary]
    latest_events: list[AgentEvent]
    audit_events: list[AuditEvent]
    knowledge: KnowledgeStats
