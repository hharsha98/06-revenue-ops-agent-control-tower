import { Bot, BrainCircuit, CheckCircle2, Github, Mail, MessageSquare, ShieldCheck } from "lucide-react";

const agents = [
  { name: "Supervisor", icon: BrainCircuit, status: "routing", x: 46, y: 12 },
  { name: "Research", icon: Bot, status: "account context", x: 8, y: 40 },
  { name: "Knowledge", icon: Bot, status: "RAG citations", x: 32, y: 52 },
  { name: "Ticket Triage", icon: Bot, status: "urgency + owner", x: 58, y: 52 },
  { name: "Risk Guard", icon: ShieldCheck, status: "policy gate", x: 82, y: 40 }
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
        <span>Live workflow canvas</span>
        <strong>Sandbox autonomy active</strong>
      </div>
      <div className="canvas__stage">
        <svg className="canvas__lines" viewBox="0 0 100 72" role="img" aria-label="Agent routing paths">
          <path d="M50 22 C32 28 22 33 16 42" />
          <path d="M50 22 C42 34 39 42 38 54" />
          <path d="M50 22 C58 34 64 42 66 54" />
          <path d="M50 22 C70 28 80 33 88 42" />
        </svg>
        {agents.map((agent) => {
          const Icon = agent.icon;
          return (
            <div className="agent-node" key={agent.name} style={{ left: `${agent.x}%`, top: `${agent.y}%` }}>
              <Icon size={18} />
              <strong>{agent.name}</strong>
              <span>{agent.status}</span>
            </div>
          );
        })}
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

