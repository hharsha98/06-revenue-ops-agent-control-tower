import { useState } from "react";
import { requestJson } from "../api";
import type { EvalReport } from "../types";

export function EvalsPanel() {
  const [report, setReport] = useState<EvalReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  async function runEvals() {
    setRunning(true);
    setError(null);
    try {
      setReport(await requestJson<EvalReport>("/api/evals/run", { method: "POST" }));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Eval run failed.");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="panel" id="eval-panel">
      <div className="panel__title">Evaluation gates</div>
      <p className="lede lede--compact">
        The fixed dataset checks that the supervisor routes each objective to the expected agents.
        Evidence hits are reported beside the gate. This suite does not call a paid model.
      </p>
      <button type="button" className="primary" onClick={() => void runEvals()} disabled={running}>
        {running ? "Running evals..." : "Run eval suite"}
      </button>
      {error && <p className="run-status__error">{error}</p>}
      {report && (
        <div className="stack">
          <p className="score">
            {report.score} {report.status}
          </p>
          {report.cases.map((item) => (
            <article className="eval-case" key={item.id}>
              <header>
                <strong>{item.id}</strong>
                <span>{item.ok ? "pass" : "fail"}</span>
              </header>
              <p>Agents: {item.actual_agents.join(", ")}</p>
              {item.missing_agents.length > 0 && <p>Missing: {item.missing_agents.join(", ")}</p>}
              <ul>
                {item.evidence.map((hit) => (
                  <li key={hit.term}>
                    {hit.term}: {hit.found ? hit.source : "not in the seeded corpus"}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
