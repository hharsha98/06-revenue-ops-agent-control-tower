import type { Alert } from "../types";

export function AlertsPanel({
  alerts,
  onAcknowledge
}: {
  alerts: Alert[];
  onAcknowledge: (alertId: string) => Promise<void>;
}) {
  if (alerts.length === 0) {
    return <p className="empty">No alerts are loaded. Start the API to seed the operator queue.</p>;
  }

  return (
    <div className="stack">
      {alerts.map((alert) => (
        <article className={`alert-card severity-${alert.severity}`} key={alert.id}>
          <header>
            <span>{alert.severity}</span>
            <span>{alert.status}</span>
            <span>{alert.source}</span>
          </header>
          <strong>{alert.title}</strong>
          <p>{alert.detail}</p>
          <footer>
            <span>{alert.account}</span>
            <span>{alert.owner_agent}</span>
            {alert.status === "open" && (
              <button type="button" className="secondary" onClick={() => void onAcknowledge(alert.id)}>
                Acknowledge
              </button>
            )}
          </footer>
        </article>
      ))}
    </div>
  );
}
