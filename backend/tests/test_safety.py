from backend.app.core.safety import assess_action_risk


def test_sandbox_mode_allows_simulated_external_actions():
    decision = assess_action_risk(
        action="send_gmail",
        target="demo.customer@example.com",
        autonomy_mode="sandbox",
        allowlist=[],
    )

    assert decision.allowed is True
    assert decision.execution_mode == "simulated"


def test_real_mode_blocks_non_allowlisted_targets():
    decision = assess_action_risk(
        action="send_gmail",
        target="customer@real-company.com",
        autonomy_mode="real",
        allowlist=["*@sandbox.example.com"],
    )

    assert decision.allowed is False
    assert "not allowlisted" in decision.reason

