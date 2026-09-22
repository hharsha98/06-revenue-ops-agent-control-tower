"""HTTP checks for the native control-tower process."""

from __future__ import annotations

import json
import os
import urllib.request

BASE_URL = os.environ["BASE_URL"].rstrip("/")
PORT = int(os.environ.get("PORT", "8060"))
FORBIDDEN = ("169.58.185.43", "agentfleet.")


def _request(path: str, payload: dict | None = None) -> dict | list:
    data = None if payload is None else json.dumps(payload).encode()
    request = urllib.request.Request(
        BASE_URL + path,
        data=data,
        headers={"content-type": "application/json", "accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read()
    text = body.decode()
    for marker in FORBIDDEN:
        if marker in text:
            raise SystemExit(f"{path} leaked forbidden marker {marker}")
    return json.loads(text)


def main() -> None:
    health = _request("/health")
    assert isinstance(health, dict)
    assert health["status"] == "ok"
    assert health["product"] == "revenueops-control-tower"
    assert health["host"] == "0.0.0.0"
    assert int(health["port"]) == PORT

    overview = _request("/api/overview")
    assert isinstance(overview, dict)
    assert overview["product"] == "revenueops-control-tower"
    assert overview["recommended_badge"] == "Early"
    assert len(overview["agents"]) >= 6
    assert len(overview["kpis"]) >= 4
    assert overview["knowledge"]["documents"] >= 4
    assert any(alert["id"] == "alert_sso_acme" for alert in overview["alerts"])
    assert any(document["source"] == "security-sso.md" for document in overview["documents"])
    assert any(item["objective"].startswith("Customer says SSO fails") for item in overview["recent_workflows"])

    search = _request("/api/documents/search", {"query": "SSO security review", "limit": 3})
    assert isinstance(search, dict)
    assert any(item["source"] == "security-sso.md" for item in search["results"])

    run = _request(
        "/api/workflows/run",
        {
            "objective": "Customer says SSO fails before security review. Answer from docs and escalate if needed.",
            "source": "gmail",
            "autonomy_mode": "sandbox",
        },
    )
    assert isinstance(run, dict)
    assert run["status"] == "completed"
    workflow_id = run["workflow_id"]

    events = _request(f"/api/workflows/{workflow_id}/events")
    assert isinstance(events, list)
    assert events[0]["agent"] == "SupervisorAgent"
    assert "KnowledgeAgent" in [event["agent"] for event in events]
    knowledge = next(event for event in events if event["agent"] == "KnowledgeAgent")
    assert "security-sso.md" in knowledge["tool_calls"][0]["details"]["citations"]
    assert any(
        "sandbox Gmail draft" in call["summary"]
        for event in events
        for call in event["tool_calls"]
    )

    audit = _request("/api/audit")
    assert isinstance(audit, list)
    assert any(item.get("workflow_id") == workflow_id for item in audit)

    report = _request("/api/evals/run", {})
    assert isinstance(report, dict)
    assert report["status"] == "passed"
    assert report["score"] == "3/3"

    blocked = _request(
        "/api/tools/execute",
        {
            "tool_name": "create_github_issue",
            "autonomy_mode": "real",
            "payload": {
                "repo": "external/private-prod-repo",
                "title": "do not send",
                "body": "sandbox safety check",
            },
        },
    )
    assert isinstance(blocked, dict)
    assert blocked["allowed"] is False
    assert blocked["execution_mode"] == "live_blocked"
    print("smoke checks passed")


if __name__ == "__main__":
    main()
