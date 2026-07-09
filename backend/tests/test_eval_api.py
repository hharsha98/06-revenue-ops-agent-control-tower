from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_eval_run_api_returns_structured_quality_report():
    client = TestClient(create_app())

    response = client.post("/api/evals/run")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["summary"]["cases_passed"] == 4
    assert body["summary"]["cases_failed"] == 0
    assert body["summary"]["citation_coverage"] == 0.91
    assert body["cases"][0]["name"] == "citation accuracy"
    assert body["cases"][0]["result"] == "pass"
    assert body["cases"][-1]["name"] == "unsafe autonomous action"
