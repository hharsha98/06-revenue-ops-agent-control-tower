import {
  Bot,
  BrainCircuit,
  CheckCircle2,
  Database,
  Github,
  Mail,
  MessageSquare,
  Send,
  ShieldCheck,
  Sparkles
} from "lucide-react";

const agents = [
  { name: "Research", eventAgent: "ResearchAgent", icon: Bot, status: "account context", signal: "lead fit 86%" },
  { name: "Knowledge", eventAgent: "KnowledgeAgent", icon: Database, status: "RAG citations", signal: "3 sources" },
  { name: "Ticket Triage", eventAgent: "TicketTriageAgent", icon: Bot, status: "urgency + owner", signal: "high priority" },
  { name: "Risk Guard", eventAgent: "RiskGuardAgent", icon: ShieldCheck, status: "policy gate", signal: "safe to draft" },
  { name: "Outreach", eventAgent: "OutreachAgent", icon: Send, status: "customer response", signal: "draft ready" }
];

const tools = [
  { name: "Gmail", icon: Mail, label: "read/send" },
  { name: "Slack", icon: MessageSquare, label: "handoff" },
  { name: "GitHub", icon: Github, label: "issues" },
  { name: "Eval", icon: CheckCircle2, label: "quality gate" }
];

type WorkflowCanvasEvent = {
  agent: string;
  tool_calls: Array<{
    tool_name: string;
    execution_mode: string;
    summary: string;
  }>;
};

type WorkflowCanvasProps = {
  workflowId?: string;
  events?: WorkflowCanvasEvent[];
  isRunning?: boolean;
};

export function WorkflowCanvas({ workflowId, events = [], isRunning = false }: WorkflowCanvasProps) {
  const completedAgents = new Set(events.map((event) => event.agent));
  const toolCalls = events.flatMap((event) => event.tool_calls);
  const latestToolCall = toolCalls.length > 0 ? toolCalls[toolCalls.length - 1] : undefined;
  const supervisorCompleted = completedAgents.has("SupervisorAgent");
  const completedStageCount = Math.min(
    ["SupervisorAgent", "KnowledgeAgent", "TicketTriageAgent", "RiskGuardAgent", "OutreachAgent"].filter(
      (agent) => completedAgents.has(agent)
    ).length,
    5
  );

  return (
    <section className="canvas" aria-label="Workflow canvas">
      <div className="canvas__header">
        <span>Workflow control plane</span>
        <strong>
          {isRunning ? "Workflow running" : workflowId ? `Canvas synced to ${workflowId}` : "Sandbox autonomy"}
        </strong>
      </div>
      <div className="canvas__body">
        <div className={`supervisor-card ${supervisorCompleted ? "supervisor-card--completed" : ""}`}>
          <div>
            <BrainCircuit size={22} />
            <span>SupervisorAgent</span>
          </div>
          <strong>
            {supervisorCompleted
              ? "Plan created, specialists delegated, risk gate queued."
              : "Plans, delegates, checks risk, then approves tool execution."}
          </strong>
        </div>

        <div className="flow-strip" aria-label="Workflow stages">
          {["intake", "plan", "delegate", "verify", "act"].map((stage, index) => (
            <span className={index < completedStageCount ? "flow-strip__step--completed" : ""} key={stage}>
              {stage}
            </span>
          ))}
        </div>

        <div className="agent-grid">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const isComplete = completedAgents.has(agent.eventAgent);
            return (
              <article className={`agent-card ${isComplete ? "agent-card--completed" : ""}`} key={agent.name}>
                <div className="agent-card__icon">
                  <Icon size={17} />
                </div>
                <div>
                  <strong>{agent.name}</strong>
                  <span>{isComplete ? "completed" : agent.status}</span>
                </div>
                <small>{isComplete ? "synced" : agent.signal}</small>
              </article>
            );
          })}
        </div>

        {latestToolCall && (
          <div className="canvas-proof">
            <span>Latest tool call</span>
            <strong>
              {latestToolCall.tool_name} · {latestToolCall.execution_mode}
            </strong>
            <small>{latestToolCall.summary}</small>
          </div>
        )}

        <div className="gate-row">
          <div className="gate-card">
            <ShieldCheck size={18} />
            <span>Allowlist + audit log</span>
          </div>
          <div className="gate-card">
            <Sparkles size={18} />
            <span>LLM eval gate</span>
          </div>
        </div>
      </div>
      <div className="tool-rail">
        {tools.map((tool) => {
          const Icon = tool.icon;
          return (
            <div className="tool-pill" key={tool.name}>
              <Icon size={16} />
              <span>{tool.name}</span>
              <small>{tool.label}</small>
            </div>
          );
        })}
      </div>
    </section>
  );
}
