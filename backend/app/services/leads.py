import json

from backend.app.core.paths import repo_root


def load_leads() -> list[dict]:
    directory = repo_root() / "sample-data" / "leads"
    if not directory.exists():
        return []
    leads: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        leads.append(json.loads(path.read_text(encoding="utf-8")))
    return leads


def load_tickets() -> list[dict]:
    directory = repo_root() / "sample-data" / "tickets"
    if not directory.exists():
        return []
    tickets: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["id"] = path.stem
        tickets.append(payload)
    return tickets


def match_lead(company: str) -> dict | None:
    needle = company.lower().strip()
    if not needle:
        return None
    for lead in load_leads():
        name = str(lead.get("company", "")).lower()
        if name and name == needle:
            return lead
    return None


def company_from_text(text: str) -> str:
    """Return a seeded company only when its full name appears in the text."""
    lowered = text.lower()
    matches = [
        str(lead.get("company", ""))
        for lead in load_leads()
        if str(lead.get("company", "")) and str(lead["company"]).lower() in lowered
    ]
    if not matches:
        return ""
    return max(matches, key=len)
