from backend.app.models.knowledge import DocumentUploadRequest
from backend.app.services.knowledge import KnowledgeStore, chunk_document


def test_chunk_document_preserves_source_and_splits_text_into_searchable_chunks():
    chunks = chunk_document(
        source="security-sso.md",
        text="SSO setup requires SAML metadata. " * 45,
        chunk_size=180,
        overlap=30,
    )

    assert len(chunks) > 1
    assert chunks[0].source == "security-sso.md"
    assert chunks[0].chunk_index == 0
    assert "SAML metadata" in chunks[0].content


def test_knowledge_store_retrieves_relevant_chunks_by_query_terms():
    store = KnowledgeStore()
    store.ingest(
        DocumentUploadRequest(
            source="security-sso.md",
            text="Enterprise SSO uses SAML metadata and role mapping. Billing docs mention invoices.",
        )
    )

    results = store.search("How do I fix SSO SAML setup?", limit=1)

    assert len(results) == 1
    assert results[0].source == "security-sso.md"
    assert results[0].score > 0
    assert "SAML" in results[0].content

