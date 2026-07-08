import { Activity, ArrowRight, Database, Gauge, ServerCog, ShieldCheck } from "lucide-react";
import { WorkflowCanvas } from "../components/WorkflowCanvas";

const metrics = [
  ["tool-call success", "96%"],
  ["avg workflow latency", "18s"],
  ["citation coverage", "91%"],
  ["sandbox tool calls", "live"]
];

const proofPoints = ["LangGraph", "FastAPI", "pgvector", "Celery", "EKS/Terraform"];

const tasks = [
  ["urgent", "SSO failure from enterprise trial", "TicketTriageAgent"],
  ["high", "Draft pricing follow-up for Acme AI", "OutreachAgent"],
  ["medium", "Create stale-doc issue for onboarding guide", "EngineeringHandoffAgent"]
];

const knowledgeItems = [
  ["seeded doc", "security-sso.md"],
  ["chunking", "700 chars + overlap"],
  ["retrieval", "keyword baseline"],
  ["agent tool", "MCP retrieve_docs"]
];

const toolItems = [
  ["Gmail", "sandbox draft"],
  ["Slack", "demo-alerts post"],
  ["GitHub", "allowlisted issue"],
  ["Safety", "real mode blocked"]
];

const timelineEvents = [
  "SupervisorAgent planned specialist steps",
  "KnowledgeAgent retrieved grounded evidence",
  "TicketTriageAgent classified urgency",
  "RiskGuardAgent checked safety policy",
  "OutreachAgent prepared Gmail action"
];

export function App() {
  return (
    <main>
      <section className="hero">
        <nav className="nav">
          <div className="brand">
            <ServerCog size={20} />
            RevenueOps Control Tower
          </div>
          <div className="nav__status">
            <span />
            enterprise scaffold
          </div>
        </nav>

        <div className="hero__grid">
          <div className="hero__copy">
            <p className="eyebrow">multi-agent AI platform for startup operators</p>
            <h1>Revenue and support ops, run by governed AI agents.</h1>
            <p className="lede">
              Research leads, answer customer questions from company knowledge, triage tickets, send
              Gmail updates, escalate to Slack, and create GitHub issues with audit trails, evals, and
              deployment proof.
            </p>
            <div className="proof-strip" aria-label="Technology proof points">
              {proofPoints.map((point) => (
                <span key={point}>{point}</span>
              ))}
            </div>
            <div className="actions">
              <button type="button">
                Run sandbox workflow <ArrowRight size={16} />
              </button>
              <button type="button" className="secondary">
                View eval report
              </button>
            </div>
          </div>
          <WorkflowCanvas />
        </div>
      </section>

      <section className="dashboard">
        <div className="panel">
          <div className="panel__title">
            <Activity size={18} />
            Live agent timeline
          </div>
          {timelineEvents.map((event) => (
            <div className="timeline-row" key={event}>
              <span />
              {event}
            </div>
          ))}
        </div>

        <div className="panel">
          <div className="panel__title">
            <Gauge size={18} />
            Evaluation gates
          </div>
          <div className="metric-grid">
            {metrics.map(([label, value]) => (
              <div className="metric" key={label}>
                <strong>{value}</strong>
                <span>{label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="panel panel--wide">
          <div className="panel__title">
            <Database size={18} />
            Knowledge base pipeline
          </div>
          <div className="knowledge-grid">
            {knowledgeItems.map(([label, value]) => (
              <div className="knowledge-item" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="panel panel--wide">
          <div className="panel__title">
            <ShieldCheck size={18} />
            Sandbox tool execution
          </div>
          <div className="knowledge-grid">
            {toolItems.map(([label, value]) => (
              <div className="knowledge-item" key={label}>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="panel panel--wide">
          <div className="panel__title">
            <ShieldCheck size={18} />
            Operator task board
          </div>
          <div className="kanban">
            {tasks.map(([priority, title, owner]) => (
              <article className="task-card" key={title}>
                <span>{priority}</span>
                <strong>{title}</strong>
                <small>{owner}</small>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
