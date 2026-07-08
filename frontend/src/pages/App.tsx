import { useState } from "react";
import { Activity, ArrowRight, Database, Gauge, ServerCog, ShieldCheck } from "lucide-react";
import { WorkflowCanvas } from "../components/WorkflowCanvas";

const metrics = [
  ["tool-call success", "96%"],
  ["avg workflow latency", "18s"],
  ["citation coverage", "91%"],
  ["sandbox tool calls", "live"]
];

const evalCases = [
  ["citation accuracy", "pass", "Answers must quote retrieved company policy before drafting customer email."],
  ["ticket triage quality", "pass", "SSO outage mapped to high priority with SupportOps owner."],
  ["prompt-injection resistance", "pass", "External instructions cannot bypass allowlists or approval gates."]
];

const guardrailChecks = [
  ["sandbox default", "No real Gmail, Slack, or GitHub action runs without explicit config."],
  ["real sends require approval", "Customer-facing actions are drafted first unless allowlisted real mode is enabled."],
  ["audit trail", "Every agent step records owner, tool, execution mode, and summary."]
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

type WorkflowRun = {
  workflow_id: string;
  status: string;
};

type AgentEvent = {
  sequence: number;
  agent: string;
  message: string;
  tools: string[];
  tool_calls: Array<{
    tool_name: string;
    execution_mode: string;
    summary: string;
  }>;
};

export function App() {
  const [workflow, setWorkflow] = useState<WorkflowRun | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runSandboxWorkflow() {
    setIsRunning(true);
    setError(null);
    try {
      const runResponse = await fetch("/api/workflows/run", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          objective: "Customer says SSO fails before security review. Answer from docs and escalate if needed.",
          source: "gmail",
          autonomy_mode: "sandbox"
        })
      });
      if (!runResponse.ok) {
        throw new Error("Workflow API returned an error.");
      }
      const run = (await runResponse.json()) as WorkflowRun;
      const eventsResponse = await fetch(`/api/workflows/${run.workflow_id}/events`);
      if (!eventsResponse.ok) {
        throw new Error("Workflow events API returned an error.");
      }
      setWorkflow(run);
      setEvents((await eventsResponse.json()) as AgentEvent[]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Workflow failed.");
    } finally {
      setIsRunning(false);
    }
  }

  function showEvalPanel() {
    document.getElementById("eval-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

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
              <button type="button" onClick={runSandboxWorkflow} disabled={isRunning}>
                {isRunning ? "Running workflow..." : "Run sandbox workflow"} <ArrowRight size={16} />
              </button>
              <button type="button" className="secondary" onClick={showEvalPanel}>
                View eval report
              </button>
            </div>
            <div className="run-status" aria-live="polite">
              {workflow && <span>Workflow {workflow.workflow_id} {workflow.status}</span>}
              {error && <span className="run-status__error">{error}</span>}
            </div>
          </div>
          <WorkflowCanvas workflowId={workflow?.workflow_id} events={events} isRunning={isRunning} />
        </div>
      </section>

      <section className="dashboard">
        <div className="panel">
          <div className="panel__title">
            <Activity size={18} />
            Live agent timeline
          </div>
          {events.length === 0
            ? timelineEvents.map((event) => (
                <div className="timeline-row" key={event}>
                  <span />
                  {event}
                </div>
              ))
            : events.map((event) => (
                <div className="timeline-row timeline-row--rich" key={`${event.sequence}-${event.agent}`}>
                  <span />
                  <div>
                    <strong>{event.agent}</strong>
                    <small>{event.message}</small>
                    {event.tool_calls.map((call) => (
                      <em key={`${event.sequence}-${call.tool_name}`}>
                        {call.tool_name} · {call.execution_mode} · {call.summary}
                      </em>
                    ))}
                  </div>
                </div>
              ))}
        </div>

        <div className="panel panel--wide eval-report" id="eval-panel" aria-label="Agent evaluation report">
          <div className="panel__title panel__title--split">
            <div>
              <Gauge size={18} />
              Agent evaluation report
            </div>
            <span>fixed eval suite</span>
          </div>
          <div className="metric-grid">
            {metrics.map(([label, value]) => (
              <div className="metric" key={label}>
                <strong>{value}</strong>
                <span>{label}</span>
              </div>
            ))}
          </div>
          <div className="eval-grid">
            {evalCases.map(([name, result, detail]) => (
              <article className="eval-case" key={name}>
                <div>
                  <strong>{name}</strong>
                  <span>{result}</span>
                </div>
                <p>{detail}</p>
              </article>
            ))}
          </div>
          <div className="guardrail-list">
            {guardrailChecks.map(([label, detail]) => (
              <div className="guardrail-item" key={label}>
                <ShieldCheck size={17} />
                <div>
                  <strong>{label}</strong>
                  <span>{detail}</span>
                </div>
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
