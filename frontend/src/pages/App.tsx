import { useEffect, useState } from "react";
import { ArrowRight, ServerCog } from "lucide-react";
import { requestJson } from "../api";
import { AlertsPanel } from "../components/AlertsPanel";
import { EvalsPanel } from "../components/EvalsPanel";
import { EvidencePanel } from "../components/EvidencePanel";
import { Timeline } from "../components/Timeline";
import { WorkflowCanvas } from "../components/WorkflowCanvas";
import type {
  AgentEvent,
  AutonomyMode,
  Health,
  Overview,
  TowerView,
  WorkflowRun,
  WorkflowSource
} from "../types";

const VIEWS: Array<{ id: TowerView; label: string }> = [
  { id: "tower", label: "Tower" },
  { id: "run", label: "Workflow" },
  { id: "agents", label: "Agents" },
  { id: "evidence", label: "Evidence" },
  { id: "alerts", label: "Alerts" },
  { id: "audit", label: "Audit" },
  { id: "evals", label: "Evals" },
  { id: "readiness", label: "Readiness" }
];

const DEFAULT_OBJECTIVE =
  "Customer says SSO fails before security review. Answer from docs and escalate if needed.";

export function App() {
  const [view, setView] = useState<TowerView>("tower");
  const [health, setHealth] = useState<Health | null>(null);
  const [overview, setOverview] = useState<Overview | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [objective, setObjective] = useState(DEFAULT_OBJECTIVE);
  const [account, setAccount] = useState("Acme AI");
  const [source, setSource] = useState<WorkflowSource>("gmail");
  const [autonomy, setAutonomy] = useState<AutonomyMode>("sandbox");
  const [workflow, setWorkflow] = useState<WorkflowRun | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);

  async function loadTower() {
    try {
      const [healthBody, overviewBody] = await Promise.all([
        requestJson<Health>("/health"),
        requestJson<Overview>("/api/overview")
      ]);
      setHealth(healthBody);
      setOverview(overviewBody);
      setLoadError(null);
    } catch (caught) {
      setLoadError(caught instanceof Error ? caught.message : "Control tower API is unreachable.");
    }
  }

  useEffect(() => {
    void loadTower();
  }, []);

  async function runSandboxWorkflow() {
    setIsRunning(true);
    setRunError(null);
    setView("run");
    try {
      const run = await requestJson<WorkflowRun>("/api/workflows/run", {
        method: "POST",
        body: JSON.stringify({
          objective,
          source,
          autonomy_mode: autonomy,
          account
        })
      });
      const timeline = await requestJson<AgentEvent[]>(`/api/workflows/${run.workflow_id}/events`);
      setWorkflow(run);
      setEvents(timeline);
      await loadTower();
    } catch (caught) {
      setRunError(caught instanceof Error ? caught.message : "Workflow failed.");
    } finally {
      setIsRunning(false);
    }
  }

  async function acknowledge(alertId: string) {
    try {
      await requestJson(`/api/alerts/${alertId}/acknowledge`, { method: "POST" });
      await loadTower();
    } catch (caught) {
      setLoadError(caught instanceof Error ? caught.message : "Could not acknowledge the alert.");
    }
  }

  const visibleEvents = events.length > 0 ? events : (overview?.latest_events ?? []);
  const activeAgents = visibleEvents.map((event) => event.agent);
  const runLabel =
    autonomy === "sandbox" ? "Run sandbox workflow" : autonomy === "approval" ? "Run approval workflow" : "Run real-mode check";

  return (
    <div className="tower">
      <aside className="rail">
        <div className="brand">
          <ServerCog size={20} />
          <div>
            <strong>RevenueOps</strong>
            <small>Control Tower</small>
          </div>
        </div>
        <nav className="rail__nav" aria-label="Control tower sections">
          {VIEWS.map((item) => (
            <button
              key={item.id}
              type="button"
              className={view === item.id ? "nav-button nav-button--active" : "nav-button"}
              aria-current={view === item.id ? "page" : undefined}
              onClick={() => setView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        <p className="rail__badge">{overview?.recommended_badge ?? "…"} demo</p>
      </aside>

      <div className="workspace">
        <header className="masthead">
          <div>
            <p className="eyebrow">Founder and COO operator console</p>
            <h1>Revenue and support, under one governed tower.</h1>
            <p className="lede">
              Specialist agents research accounts, cite company docs, triage urgency, and prepare Gmail,
              Slack, and GitHub actions. Sandbox is the default. Nothing is sent.
            </p>
          </div>
          <div className="masthead__actions">
            <button type="button" className="primary" onClick={() => void runSandboxWorkflow()} disabled={isRunning}>
              {isRunning ? "Running workflow..." : runLabel} <ArrowRight size={16} />
            </button>
            <button type="button" className="secondary" onClick={() => setView("evals")}>
              View eval report
            </button>
            <div className="status-row" aria-live="polite">
              <span className={health?.status === "ok" ? "pill pill--ok" : "pill"}>
                {health ? `${health.product} · ${health.status}` : "API not checked"}
              </span>
              <span className="pill">{autonomy}</span>
              {workflow && (
                <span>
                  Workflow {workflow.workflow_id} {workflow.status}
                </span>
              )}
              {runError && <span className="run-status__error">{runError}</span>}
            </div>
          </div>
        </header>

        {loadError && (
          <p className="banner" role="alert">
            {loadError} Start the tower with <code>bash scripts/serve.sh</code> and open port 8060.
          </p>
        )}

        {overview && (
          <section className="kpi-grid" aria-label="Control tower KPIs">
            {overview.kpis.map((kpi) => (
              <article className="kpi" key={kpi.id}>
                <strong>{kpi.value}</strong>
                <span>{kpi.label}</span>
                <small>{kpi.detail}</small>
              </article>
            ))}
          </section>
        )}

        <main className="stage">
          {view === "tower" && (
            <div className="stage-grid">
              <section className="panel">
                <div className="panel__title">Open queue</div>
                <AlertsPanel
                  alerts={(overview?.alerts ?? []).filter((alert) => alert.status === "open").slice(0, 4)}
                  onAcknowledge={acknowledge}
                />
              </section>
              <section className="panel">
                <div className="panel__title">Latest workflow evidence</div>
                <Timeline events={visibleEvents} />
              </section>
              <section className="panel panel--wide">
                <div className="panel__title">Book of business</div>
                <div className="account-grid">
                  {(overview?.accounts ?? []).map((account) => (
                    <article className="account-card" key={account.company}>
                      <header>
                        <strong>{account.company}</strong>
                        <span>fit {account.fit_score}</span>
                      </header>
                      <p>{account.segment} · {account.team_size} people · {account.plan || "plan unset"}</p>
                      <small>{account.signal}</small>
                    </article>
                  ))}
                </div>
              </section>
            </div>
          )}

          {view === "run" && (
            <div className="stage-grid stage-grid--run">
              <section className="panel">
                <div className="panel__title">Demo scenarios</div>
                <div className="stack">
                  {(overview?.scenarios ?? []).map((scenario) => (
                    <button
                      key={scenario.id}
                      type="button"
                      className={objective === scenario.objective ? "scenario scenario--active" : "scenario"}
                      onClick={() => {
                        setObjective(scenario.objective);
                        setSource(scenario.source);
                        setAccount(scenario.account);
                      }}
                    >
                      <strong>{scenario.title}</strong>
                      <small>{scenario.account} · {scenario.source}</small>
                      <span>{scenario.summary}</span>
                    </button>
                  ))}
                </div>
                <label className="field" htmlFor="objective">
                  Objective
                  <textarea id="objective" value={objective} onChange={(event) => setObjective(event.target.value)} rows={4} />
                </label>
                <div className="field-row">
                  <label>
                    Source
                    <select value={source} onChange={(event) => setSource(event.target.value as WorkflowSource)}>
                      <option value="gmail">gmail</option>
                      <option value="manual">manual</option>
                      <option value="github">github</option>
                      <option value="slack">slack</option>
                    </select>
                  </label>
                  <label>
                    Autonomy
                    <select value={autonomy} onChange={(event) => setAutonomy(event.target.value as AutonomyMode)}>
                      <option value="sandbox">sandbox</option>
                      <option value="approval">approval</option>
                      <option value="real">real</option>
                    </select>
                  </label>
                </div>
              </section>
              <section className="panel">
                <div className="panel__title">Agent timeline</div>
                <Timeline events={visibleEvents} />
              </section>
              <div className="panel--wide">
                <WorkflowCanvas
                  autonomyMode={autonomy}
                  activeAgents={activeAgents}
                  workflowId={workflow?.workflow_id}
                />
              </div>
            </div>
          )}

          {view === "agents" && (
            <div className="agent-board">
              {(overview?.agents ?? []).map((agent) => (
                <article className="agent-board__card" key={agent.name}>
                  <header>
                    <strong>{agent.name}</strong>
                    <span>{agent.status}</span>
                  </header>
                  <p>{agent.role}</p>
                  <small>{agent.tools.length ? agent.tools.join(", ") : "No external tool"}</small>
                  <em>{agent.last_message}</em>
                </article>
              ))}
            </div>
          )}

          {view === "evidence" && <EvidencePanel documents={overview?.documents ?? []} />}
          {view === "alerts" && <AlertsPanel alerts={overview?.alerts ?? []} onAcknowledge={acknowledge} />}

          {view === "audit" && (
            <div className="panel">
              <div className="panel__title">Audit trail</div>
              <div className="audit-list">
                {(overview?.audit_events ?? []).map((event, index) => (
                  <article key={`${event.created_at ?? "audit"}-${index}`}>
                    <span>{event.event_type}</span>
                    <p>{event.message}</p>
                    <small>{event.workflow_id || "system"} · {event.created_at || "unspecified time"}</small>
                  </article>
                ))}
              </div>
            </div>
          )}

          {view === "evals" && <EvalsPanel />}

          {view === "readiness" && overview && (
            <section className="panel">
              <div className="panel__title">Studio readiness · {overview.readiness.recommended_badge}</div>
              <p className="lede lede--compact">{overview.readiness.summary}</p>
              <p className="positioning">{overview.positioning}</p>
              <div className="readiness-grid">
                <div>
                  <h2>Live</h2>
                  <ul>
                    {overview.readiness.live.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h2>Early</h2>
                  <ul>
                    {overview.readiness.early.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h2>Building</h2>
                  <ul>
                    {overview.readiness.building.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </section>
          )}
        </main>
        <footer className="footnote">
          Sandbox demo for this repository. External sends stay simulated. This host is not Agent Fleet.
        </footer>
      </div>
    </div>
  );
}
