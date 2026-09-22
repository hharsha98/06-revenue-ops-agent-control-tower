from datetime import UTC, datetime

from backend.app.models.workflow import AuditEvent


class AuditLog:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, event_type: str, message: str, workflow_id: str | None = None) -> AuditEvent:
        event = AuditEvent(
            event_type=event_type,
            message=message,
            workflow_id=workflow_id,
            created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        self._events.append(event)
        return event

    def list_events(self) -> list[AuditEvent]:
        return list(reversed(self._events))


audit_log = AuditLog()
