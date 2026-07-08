from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


AutonomyMode = Literal["sandbox", "approval", "real"]


class WorkflowRequest(BaseModel):
    objective: str = Field(min_length=5)
    source: Literal["gmail", "slack", "github", "manual"] = "manual"
    autonomy_mode: AutonomyMode = "sandbox"


class AgentStep(BaseModel):
    agent: str
    purpose: str
    tools: list[str] = Field(default_factory=list)


class WorkflowPlan(BaseModel):
    workflow_id: str = Field(default_factory=lambda: f"wf_{uuid4().hex[:12]}")
    workflow_name: str
    steps: list[AgentStep]
    requires_approval: bool
    safety_notes: list[str] = Field(default_factory=list)


class WorkflowRun(BaseModel):
    workflow_id: str
    status: Literal["planned", "running", "blocked", "completed"] = "planned"
    plan: WorkflowPlan


class ToolCall(BaseModel):
    tool_name: str
    target: str
    mode: AutonomyMode
    allowed: bool
    execution_mode: Literal["simulated", "approval_required", "live_blocked", "live"]
    summary: str


class ToolExecuteRequest(BaseModel):
    tool_name: str
    autonomy_mode: AutonomyMode = "sandbox"
    payload: dict[str, str] = Field(default_factory=dict)


class AgentEvent(BaseModel):
    workflow_id: str
    sequence: int
    agent: str
    event_type: Literal["workflow.planned", "agent.completed"]
    message: str
    tools: list[str] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)


class WorkflowExecutionResult(BaseModel):
    run: WorkflowRun
    events: list[AgentEvent]


class AuditEvent(BaseModel):
    event_type: str
    message: str
    workflow_id: str | None = None
