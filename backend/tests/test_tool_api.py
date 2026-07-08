from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_tool_execute_api_runs_sandbox_adapter():
    client = TestClient(create_app())

    response = client.post(
        "/api/tools/execute",
        json={
            "tool_name": "post_slack",
            "autonomy_mode": "sandbox",
            "payload": {"channel": "demo-alerts", "message": "SSO issue escalated."},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["tool_name"] == "post_slack"
    assert body["execution_mode"] == "simulated"
    assert body["allowed"] is True

