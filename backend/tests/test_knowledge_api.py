from fastapi.testclient import TestClient

from backend.app.main import create_app


def test_document_upload_and_search_api_returns_grounded_results():
    client = TestClient(create_app())

    upload_response = client.post(
        "/api/documents/upload",
        json={
            "source": "security-sso.md",
            "text": "SSO failures should collect request ID, IdP domain, and timestamp before escalation.",
        },
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["chunks_created"] == 1

    search_response = client.post(
        "/api/documents/search",
        json={"query": "SSO request ID escalation", "limit": 2},
    )

    assert search_response.status_code == 200
    body = search_response.json()
    assert body["query"] == "SSO request ID escalation"
    assert body["results"][0]["source"] == "security-sso.md"
    assert "request ID" in body["results"][0]["content"]

