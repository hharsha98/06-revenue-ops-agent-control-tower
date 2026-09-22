import type { AgentEvent } from "../types";

export function Timeline({ events }: { events: AgentEvent[] }) {
  if (events.length === 0) {
    return <p className="empty">No workflow events yet. Run a scenario to record the agent trail.</p>;
  }

  return (
    <div className="timeline">
      {events.map((event) => (
        <article className="timeline-row timeline-row--rich" key={`${event.sequence}-${event.agent}`}>
          <span />
          <div>
            <strong>
              {event.sequence}. {event.agent}
            </strong>
            <small>{event.message}</small>
            {event.tool_calls.map((call) => (
              <em key={`${event.sequence}-${call.tool_name}`}>
                {call.tool_name} · {call.execution_mode} · {call.summary}
              </em>
            ))}
          </div>
        </article>
      ))}
    </div>
  );
}
