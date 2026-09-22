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
  { id: "ResearchAgent", name: "Research", icon: Bot, status: "account context" },
  { id: "KnowledgeAgent", name: "Knowledge", icon: Database, status: "citations" },
  { id: "TicketTriageAgent", name: "Ticket Triage", icon: Bot, status: "urgency + Slack" },
  { id: "RiskGuardAgent", name: "Risk Guard", icon: ShieldCheck, status: "policy gate" },
  { id: "OutreachAgent", name: "Outreach", icon: Mail, status: "draft only" },
  { id: "EngineeringHandoffAgent", name: "Handoff", icon: Github, status: "sandbox issue" }
];

const tools = [
  { name: "Gmail", icon: Mail, label: "draft" },
  { name: "Slack", icon: MessageSquare, label: "sandbox" },
  { name: "GitHub", icon: Github, label: "sandbox" },
  { name: "Eval", icon: CheckCircle2, label: "dataset" }
];

type WorkflowCanvasProps = {
  autonomyMode: string;
  activeAgents: string[];
  workflowId?: string | null;
};

export function WorkflowCanvas({ autonomyMode, activeAgents, workflowId }: WorkflowCanvasProps) {
  return (
    <section className="canvas" aria-label="Workflow canvas">
      <div className="canvas__header">
        <span>{workflowId ? workflowId : "Workflow control plane"}</span>
        <strong>{autonomyMode} autonomy</strong>
      </div>
      <div className="canvas__body">
        <div className="supervisor-card">
          <div>
            <BrainCircuit size={22} />
            <span>SupervisorAgent</span>
          </div>
          <strong>Plans, delegates, checks risk, then records every tool call.</strong>
        </div>
        <div className="flow-strip" aria-label="Workflow stages">
          {["intake", "plan", "delegate", "verify", "act"].map((stage) => (
            <span key={stage}>{stage}</span>
          ))}
        </div>
        <div className="agent-grid">
          {agents.map((agent) => {
            const Icon = agent.icon;
            const active = activeAgents.includes(agent.id);
            return (
              <article className={active ? "agent-card agent-card--active" : "agent-card"} key={agent.id}>
                <div className="agent-card__icon">
                  <Icon size={17} />
                </div>
                <div>
                  <strong>{agent.name}</strong>
                  <span>{agent.status}</span>
                </div>
                <small>{active ? "ran" : "ready"}</small>
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
            <span>Citation check</span>
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
