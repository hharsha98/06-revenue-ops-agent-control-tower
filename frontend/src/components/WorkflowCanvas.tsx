import {
  Bot,
  BrainCircuit,
  CheckCircle2,
  Database,
  Github,
  Mail,
  MessageSquare,
  ShieldCheck,
  Sparkles
} from "lucide-react";

const agents = [
  { name: "Research", icon: Bot, status: "account context", signal: "lead fit 86%" },
  { name: "Knowledge", icon: Database, status: "RAG citations", signal: "3 sources" },
  { name: "Ticket Triage", icon: Bot, status: "urgency + owner", signal: "high priority" },
  { name: "Risk Guard", icon: ShieldCheck, status: "policy gate", signal: "safe to draft" }
];

const tools = [
  { name: "Gmail", icon: Mail, label: "read/send" },
  { name: "Slack", icon: MessageSquare, label: "handoff" },
  { name: "GitHub", icon: Github, label: "issues" },
  { name: "Eval", icon: CheckCircle2, label: "quality gate" }
];

export function WorkflowCanvas() {
  return (
    <section className="canvas" aria-label="Workflow canvas">
      <div className="canvas__header">
        <span>Workflow control plane</span>
        <strong>Sandbox autonomy</strong>
      </div>
      <div className="canvas__body">
        <div className="supervisor-card">
          <div>
            <BrainCircuit size={22} />
            <span>SupervisorAgent</span>
          </div>
          <strong>Plans, delegates, checks risk, then approves tool execution.</strong>
        </div>

        <div className="flow-strip" aria-label="Workflow stages">
          {["intake", "plan", "delegate", "verify", "act"].map((stage) => (
            <span key={stage}>{stage}</span>
          ))}
        </div>

        <div className="agent-grid">
          {agents.map((agent) => {
            const Icon = agent.icon;
            return (
              <article className="agent-card" key={agent.name}>
                <div className="agent-card__icon">
                  <Icon size={17} />
                </div>
                <div>
                  <strong>{agent.name}</strong>
                  <span>{agent.status}</span>
                </div>
                <small>{agent.signal}</small>
              </article>
            );
          })}
        </div>

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
