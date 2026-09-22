import json
from threading import Lock

from backend.app.core.paths import repo_root
from backend.app.models.tower import Alert

_lock = Lock()
_alerts: list[Alert] | None = None


def _seed_alerts() -> list[Alert]:
    path = repo_root() / "sample-data" / "tower" / "alerts.json"
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [Alert.model_validate(item) for item in payload]


def _store() -> list[Alert]:
    global _alerts
    if _alerts is None:
        _alerts = _seed_alerts()
    return _alerts


def list_alerts() -> list[Alert]:
    return list(_store())


def acknowledge_alert(alert_id: str) -> Alert | None:
    with _lock:
        for index, alert in enumerate(_store()):
            if alert.id == alert_id:
                updated = alert.model_copy(update={"status": "acknowledged"})
                _store()[index] = updated
                return updated
    return None


def raise_live_alert(
    alert_id: str,
    severity: str,
    title: str,
    detail: str,
    account: str,
    owner_agent: str,
) -> Alert:
    with _lock:
        existing = next((alert for alert in _store() if alert.id == alert_id), None)
        if existing is not None:
            return existing
        alert = Alert.model_validate(
            {
                "id": alert_id,
                "severity": severity,
                "title": title,
                "detail": detail,
                "account": account,
                "owner_agent": owner_agent,
                "status": "open",
                "source": "live",
            }
        )
        _store().append(alert)
        return alert
