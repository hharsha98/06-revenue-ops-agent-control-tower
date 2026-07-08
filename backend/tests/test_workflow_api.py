from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_workflow_run_api_persists_retrievable_events():
    client = TestClient(create_app())

    run_response = client.post(
        "/api/workflows/run",
        json={
            "objective": "Customer says SSO fails before security review. Answer from docs and escalate if needed.",
            "source": "gmail",
            "autonomy_mode": "sandbox",
        },
    )

    assert run_response.status_code == 200
    workflow = run_response.json()
    assert workflow["status"] == "completed"

    events_response = client.get(f"/api/workflows/{workflow['workflow_id']}/events")

    assert events_response.status_code == 200
    events = events_response.json()
    assert events[0]["agent"] == "SupervisorAgent"
    assert events[-1]["agent"] == "OutreachAgent"
    assert events[-1]["tools"] == ["send_gmail"]

