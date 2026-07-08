from backend.app.tools.registry import build_tool_registry


def test_tool_registry_contains_live_tool_contracts_with_sandbox_defaults():
    registry = build_tool_registry()

    assert sorted(registry.keys()) == [
        "create_github_issue",
        "post_slack",
        "read_gmail",
        "retrieve_docs",
        "score_lead",
        "search_web",
        "send_gmail",
        "triage_ticket",
    ]
    assert registry["send_gmail"].mode == "sandbox"
    assert registry["create_github_issue"].requires_allowlist is True

