from fastmcp import FastMCP

mcp = FastMCP("revenueops-agent-tools")


@mcp.tool
def retrieve_docs(query: str) -> str:
    """Search company documents. Scaffold returns a deterministic placeholder."""
    return f"retrieved evidence for: {query}"


@mcp.tool
def triage_ticket(ticket: str) -> str:
    """Classify support ticket urgency. Scaffold returns a deterministic placeholder."""
    return f"triaged ticket: {ticket}"


if __name__ == "__main__":
    mcp.run()

