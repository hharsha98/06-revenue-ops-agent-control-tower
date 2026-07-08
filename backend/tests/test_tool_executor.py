from backend.app.tools.executor import execute_tool


def test_sandbox_send_gmail_returns_simulated_tool_call():
    call = execute_tool(
        tool_name="send_gmail",
        autonomy_mode="sandbox",
        payload={
            "to": "trial.customer@sandbox.example.com",
            "subject": "SSO support follow-up",
            "body": "We collected the request ID and escalated the SSO issue.",
        },
    )

    assert call.tool_name == "send_gmail"
    assert call.allowed is True
    assert call.execution_mode == "simulated"
    assert call.target == "trial.customer@sandbox.example.com"
    assert "sandbox Gmail draft" in call.summary


def test_real_github_issue_is_blocked_when_repo_is_not_allowlisted():
    call = execute_tool(
        tool_name="create_github_issue",
        autonomy_mode="real",
        payload={
            "repo": "external/private-prod-repo",
            "title": "SSO docs stale",
            "body": "Customer hit missing SSO troubleshooting docs.",
        },
    )

    assert call.allowed is False
    assert call.execution_mode == "live_blocked"
    assert "not allowlisted" in call.summary

