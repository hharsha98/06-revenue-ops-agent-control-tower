from backend.app.core.config import settings
from backend.app.core.safety import RiskDecision, assess_action_risk
from backend.app.models.workflow import ToolCall
from backend.app.services.knowledge import knowledge_store
from backend.app.services.leads import company_from_text, match_lead
from backend.app.services.triage import classify_ticket
from backend.app.tools.registry import build_tool_registry

EXTERNAL_SIDE_EFFECTS = {"send_gmail", "read_gmail", "post_slack", "create_github_issue"}
LOCAL_TOOLS = {"retrieve_docs", "triage_ticket", "score_lead", "search_web"}
INJECTION_MARKERS = (
    "ignore previous",
    "ignore all instructions",
    "disregard the system",
    "exfiltrate",
    "reveal your prompt",
)


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
    if tool_name in {"score_lead", "search_web"}:
        return str(payload.get("company") or payload.get("query") or "Acme AI")
    return str(payload.get("target") or tool_name)


def _clip(text: str, limit: int = 220) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    cut = clean[: limit - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(".,;:") + "…"


def _draft_email(objective: str, snippet: str) -> tuple[str, str]:
    lowered = objective.lower()
    if "pricing" in lowered:
        subject = "Pricing follow-up for your trial"
    elif "onboarding" in lowered or "stale" in lowered:
        subject = "Onboarding documentation follow-up"
    elif "sso" in lowered or "security review" in lowered:
        subject = "SSO support before your security review"
    else:
        subject = "Follow-up from RevenueOps"
    sentences = ["Thanks for the note. We reviewed the account against company knowledge."]
    if snippet:
        sentences.append(f"From our docs: {snippet}")
    else:
        sentences.append("No matching doc was found, so this draft stays conservative.")
    sentences.append("Prepared in sandbox mode. Nothing was sent.")
    return subject, " ".join(sentences)


def _local_result(tool_name: str, target: str, payload: dict) -> tuple[str, dict[str, str]]:
    if tool_name == "send_gmail":
        subject, body = _draft_email(str(payload.get("objective") or payload.get("body") or target), str(payload.get("evidence") or ""))
        subject = str(payload.get("subject") or subject)
        return (
            f"Created sandbox Gmail draft to {target}: {subject}",
            {"to": target, "subject": subject, "body": body, "sent": "false"},
        )
    if tool_name == "read_gmail":
        return (
            f"Read sandbox inbox for {target}. No live mailbox is connected.",
            {"from": target, "live": "false"},
        )
    if tool_name == "post_slack":
        message = _clip(str(payload.get("message") or "Sandbox escalation"))
        return (
            f"Prepared sandbox Slack post for #{target}.",
            {"channel": target, "message": message, "sent": "false"},
        )
    if tool_name == "create_github_issue":
        title = str(payload.get("title") or "Agent-created customer escalation")
        return (
            f"Prepared sandbox GitHub issue in {target}: {title}",
            {"repo": target, "title": title, "sent": "false"},
        )
    if tool_name == "retrieve_docs":
        query = str(payload.get("query") or target)
        found = knowledge_store.search(query, limit=5)
        if not found:
            return ("No matching company evidence found.", {"hits": "0", "citations": "", "snippet": "", "score": "0"})
        top_score = found[0].score
        results = [item for item in found if item.score >= max(0.45, top_score * 0.8)][:3]
        if not results:
            results = found[:1]
        citations = ", ".join(f"{item.source}#{item.chunk_index}" for item in results)
        snippet = _clip(results[0].content, 180)
        return (
            f"Retrieved evidence from {results[0].source}.",
            {
                "hits": str(len(results)),
                "citations": citations,
                "snippet": snippet,
                "score": str(results[0].score),
            },
        )
    if tool_name == "triage_ticket":
        classification = classify_ticket(str(payload.get("ticket") or target))
        summary = (
            f"Classified ticket as {classification['urgency']} urgency · "
            f"topic {classification['topic']} · owner {classification['owner']}."
        )
        return summary, classification
    if tool_name == "score_lead":
        company = str(payload.get("company") or company_from_text(target))
        lead = match_lead(company)
        if lead is None:
            return (f"No seeded account matched {company}.", {"company": company, "score": "0"})
        score = str(lead.get("fit_score_hint", 0))
        return (
            f"Scored {lead['company']} as {score} startup fit ({lead.get('segment', 'unknown segment')}).",
            {
                "company": str(lead["company"]),
                "score": score,
                "segment": str(lead.get("segment", "")),
                "signal": _clip(str(lead.get("signal", "")), 160),
                "team_size": str(lead.get("team_size", "")),
            },
        )
    if tool_name == "search_web":
        company = str(payload.get("company") or company_from_text(str(payload.get("query") or target)))
        lead = match_lead(company)
        if lead is None:
            return (f"Sandbox research found no seeded account for {company}.", {"company": company, "live_web": "false"})
        return (
            f"Sandbox research note for {lead['company']}: {lead.get('signal', 'no public signal stored')}",
            {
                "company": str(lead["company"]),
                "signal": _clip(str(lead.get("signal", "")), 180),
                "live_web": "false",
            },
        )
    return (f"Executed sandbox adapter for {tool_name}.", {})


def _fail_closed(tool_name: str) -> RiskDecision:
    return RiskDecision(
        allowed=False,
        execution_mode="live_blocked",
        reason=(
            f"Live credentials are not configured for {tool_name}. "
            "The action was not sent."
        ),
    )


def _unknown_tool(tool_name: str, autonomy_mode: str) -> ToolCall:
    if autonomy_mode == "approval":
        execution_mode = "approval_required"
    elif autonomy_mode == "real":
        execution_mode = "live_blocked"
    else:
        execution_mode = "simulated"
    mode = autonomy_mode if autonomy_mode in {"sandbox", "approval", "real"} else "sandbox"
    return ToolCall(
        tool_name=tool_name,
        target=tool_name,
        mode=mode,  # type: ignore[arg-type]
        allowed=False,
        execution_mode=execution_mode,  # type: ignore[arg-type]
        summary=f"Unknown tool {tool_name}.",
        details={"blocked": "true"},
    )


def execute_tool(tool_name: str, autonomy_mode: str, payload: dict | None = None) -> ToolCall:
    payload = payload or {}
    if tool_name not in build_tool_registry():
        return _unknown_tool(tool_name, autonomy_mode)

    target = _target_for(tool_name, payload)
    decision = assess_action_risk(
        action=tool_name,
        target=target,
        autonomy_mode=autonomy_mode,
        allowlist=_allowlist_for(tool_name),
    )
    if autonomy_mode == "approval" and tool_name in LOCAL_TOOLS:
        decision = RiskDecision(
            allowed=True,
            execution_mode="simulated",
            reason="Local tools still run while approval mode holds external sends.",
        )
    if decision.allowed and decision.execution_mode == "live" and tool_name in EXTERNAL_SIDE_EFFECTS:
        decision = _fail_closed(tool_name)
    if decision.allowed and decision.execution_mode == "live" and tool_name in LOCAL_TOOLS:
        decision = RiskDecision(
            allowed=True,
            execution_mode="simulated",
            reason="This tool reads the local demo store and does not make an outbound call.",
        )

    if decision.allowed:
        summary, details = _local_result(tool_name, target, payload)
    else:
        summary, details = decision.reason, {"blocked": "true"}

    inspected = " ".join(
        str(payload.get(key, "")) for key in ("objective", "body", "ticket", "query", "message")
    )
    if any(marker in inspected.lower() for marker in INJECTION_MARKERS) or any(
        marker in target.lower() for marker in INJECTION_MARKERS
    ):
        details["injection"] = "true"

    return ToolCall(
        tool_name=tool_name,
        target=target,
        mode=autonomy_mode,  # type: ignore[arg-type]
        allowed=decision.allowed,
        execution_mode=decision.execution_mode,
        summary=summary,
        details=details,
    )
