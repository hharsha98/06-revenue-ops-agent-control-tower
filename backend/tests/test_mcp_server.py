from mcp_server.server import retrieve_docs


def test_mcp_retrieve_docs_uses_seed_knowledge_store():
    result = retrieve_docs("SSO security review")

    assert "security-sso.md" in result
    assert "SSO" in result

