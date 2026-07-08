from backend.app.core.config import settings
from backend.app.core.safety import assess_action_risk
from backend.app.models.workflow import ToolCall
from backend.app.services.knowledge import knowledge_store


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _email_allowlist() -> list[str]:
    return [
        f"*@{domain}" if "@" not in domain and "*" not in domain else domain
        for domain in _split_csv(settings.allowed_email_domains)
    ]


def _allowlist_for(tool_name: str) -> list[str]:
    if tool_name in {"send_gmail", "read_gmail"}:
        return _email_allowlist()
    if tool_name == "post_slack":
        return _split_csv(settings.allowed_slack_channels)
    if tool_name == "create_github_issue":
        return _split_csv(settings.allowed_github_repos)
    return ["*"]


def _target_for(tool_name: str, payload: dict) -> str:
    if tool_name in {"send_gmail", "read_gmail"}:
        return str(payload.get("to") or payload.get("from") or "trial.customer@sandbox.example.com")
    if tool_name == "post_slack":
        return str(payload.get("channel") or "demo-alerts")
    if tool_name == "create_github_issue":
        return str(payload.get("repo") or "demo/revenueops-agent-control-tower")
    if tool_name == "retrieve_docs":
        return str(payload.get("query") or "customer support question")
    if tool_name == "triage_ticket":
        return str(payload.get("ticket") or "support ticket")
    if tool_name == "score_lead":
        return str(payload.get("company") or "Acme AI")
    return str(payload.get("target") or tool_name)


def _sandbox_summary(tool_name: str, target: str, payload: dict) -> str:
    if tool_name == "send_gmail":
        return f"Created sandbox Gmail draft to {target}: {payload.get('subject', 'customer follow-up')}"
    if tool_name == "post_slack":
        return f"Prepared sandbox Slack post for #{target}."
    if tool_name == "create_github_issue":
        return f"Prepared sandbox GitHub issue in {target}: {payload.get('title', 'agent handoff')}"
    if tool_name == "retrieve_docs":
        results = knowledge_store.search(str(payload.get("query", target)), limit=1)
        if results:
            return f"Retrieved evidence from {results[0].source}."
        return "No matching company evidence found."
    if tool_name == "triage_ticket":
        return "Classified ticket as high priority with customer-impact escalation."
    if tool_name == "score_lead":
        return f"Scored {target} as strong startup fit."
    return f"Executed sandbox adapter for {tool_name}."


def execute_tool(tool_name: str, autonomy_mode: str, payload: dict | None = None) -> ToolCall:
    payload = payload or {}
    target = _target_for(tool_name, payload)
    decision = assess_action_risk(
        action=tool_name,
        target=target,
        autonomy_mode=autonomy_mode,
        allowlist=_allowlist_for(tool_name),
    )
    summary = _sandbox_summary(tool_name, target, payload) if decision.allowed else decision.reason

    return ToolCall(
        tool_name=tool_name,
        target=target,
        mode=autonomy_mode,
        allowed=decision.allowed,
        execution_mode=decision.execution_mode,
        summary=summary,
    )
