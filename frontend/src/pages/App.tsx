import { Activity, ArrowRight, Gauge, ServerCog, ShieldCheck } from "lucide-react";
import { WorkflowCanvas } from "../components/WorkflowCanvas";

const metrics = [
  ["tool-call success", "96%"],
  ["avg workflow latency", "18s"],
  ["citation coverage", "91%"],
  ["unsafe actions blocked", "12"]
];

const tasks = [
  ["urgent", "SSO failure from enterprise trial", "TicketTriageAgent"],
  ["high", "Draft pricing follow-up for Acme AI", "OutreachAgent"],
  ["medium", "Create stale-doc issue for onboarding guide", "EngineeringHandoffAgent"]
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
            <h1>One supervisor agent coordinates sales, support, and engineering handoffs.</h1>
            <p className="lede">
              Research leads, answer customer questions from company knowledge, triage tickets, send
              Gmail updates, escalate to Slack, and create GitHub issues with audit trails, evals, and
              deployment proof.
            </p>
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
          {["Supervisor planned 4 steps", "KnowledgeAgent retrieved 3 citations", "RiskGuard blocked real send", "Slack escalation drafted"].map(
            (event) => (
              <div className="timeline-row" key={event}>
                <span />
                {event}
              </div>
            )
          )}
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

