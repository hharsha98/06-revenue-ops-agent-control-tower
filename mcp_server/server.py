from fastmcp import FastMCP

from backend.app.services.knowledge import knowledge_store

mcp = FastMCP("revenueops-agent-tools")


def retrieve_docs(query: str) -> str:
    results = knowledge_store.search(query, limit=3)
    if not results:
        return f"No company evidence found for: {query}"
    return "\n".join(f"[{result.source}#{result.chunk_index}] {result.content}" for result in results)


@mcp.tool
def retrieve_docs_tool(query: str) -> str:
    """Search company documents and return compact evidence for an agent."""
    return retrieve_docs(query)


@mcp.tool
def triage_ticket(ticket: str) -> str:
    """Classify support ticket urgency. Scaffold returns a deterministic placeholder."""
    return f"triaged ticket: {ticket}"


if __name__ == "__main__":
    mcp.run()
