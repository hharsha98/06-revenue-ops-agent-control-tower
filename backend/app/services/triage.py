def classify_ticket(ticket: str) -> dict[str, str]:
    text = ticket.lower()
    if any(word in text for word in ("security review", "failing", "fails", "outage", "down", "tomorrow")):
        urgency = "high"
    elif any(word in text for word in ("pricing", "follow-up", "follow up", "trial", "stale")):
        urgency = "medium"
    else:
        urgency = "low"

    if any(word in text for word in ("sso", "saml", "identity provider", "idp")):
        topic = "sso"
        owner = "EngineeringHandoffAgent"
    elif any(word in text for word in ("pricing", "invoice", "billing")):
        topic = "billing"
        owner = "OutreachAgent"
    elif any(word in text for word in ("onboarding", "stale", "docs")):
        topic = "documentation"
        owner = "EngineeringHandoffAgent"
    else:
        topic = "general"
        owner = "TicketTriageAgent"

    if any(word in text for word in ("failing", "fails", "urgent", "blocked", "tomorrow")):
        sentiment = "frustrated"
    else:
        sentiment = "neutral"

    return {
        "urgency": urgency,
        "topic": topic,
        "owner": owner,
        "sentiment": sentiment,
    }
