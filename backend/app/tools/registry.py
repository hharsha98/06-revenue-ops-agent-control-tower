from typing import Literal

from pydantic import BaseModel


class ToolContract(BaseModel):
    name: str
    description: str
    mode: Literal["sandbox", "live"]
    requires_allowlist: bool


def build_tool_registry() -> dict[str, ToolContract]:
    contracts = [
        ToolContract(
            name="search_web",
            description="Research a company, product, or account from web sources.",
            mode="sandbox",
            requires_allowlist=False,
        ),
        ToolContract(
            name="retrieve_docs",
            description="Search company documents through pgvector-backed RAG.",
            mode="sandbox",
            requires_allowlist=False,
        ),
        ToolContract(
            name="read_gmail",
            description="Read customer emails from Gmail using configured OAuth credentials.",
            mode="sandbox",
            requires_allowlist=True,
        ),
        ToolContract(
            name="send_gmail",
            description="Send or draft customer emails through Gmail.",
            mode="sandbox",
            requires_allowlist=True,
        ),
        ToolContract(
            name="post_slack",
            description="Post internal updates and escalations to Slack.",
            mode="sandbox",
            requires_allowlist=True,
        ),
        ToolContract(
            name="create_github_issue",
            description="Create engineering handoff issues in GitHub.",
            mode="sandbox",
            requires_allowlist=True,
        ),
        ToolContract(
            name="triage_ticket",
            description="Classify support tickets by urgency, topic, sentiment, and owner.",
            mode="sandbox",
            requires_allowlist=False,
        ),
        ToolContract(
            name="score_lead",
            description="Score a lead using firmographic context and product fit.",
            mode="sandbox",
            requires_allowlist=False,
        ),
    ]
    return {contract.name: contract for contract in contracts}

