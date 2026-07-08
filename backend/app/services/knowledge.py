import re
from collections import Counter
from pathlib import Path

from backend.app.models.knowledge import (
    DocumentChunk,
    DocumentUploadRequest,
    KnowledgeSearchResult,
)

TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> list[str]:
    return TOKEN_PATTERN.findall(text.lower())


def chunk_document(
    source: str,
    text: str,
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[DocumentChunk]:
    clean_text = " ".join(text.split())
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    chunks: list[DocumentChunk] = []
    start = 0
    index = 0
    while start < len(clean_text):
        end = min(start + chunk_size, len(clean_text))
        content = clean_text[start:end].strip()
        if content:
            chunks.append(
                DocumentChunk(
                    id=f"{source}:{index}",
                    source=source,
                    chunk_index=index,
                    content=content,
                )
            )
        if end == len(clean_text):
            break
        start = max(0, end - overlap)
        index += 1

    return chunks


class KnowledgeStore:
    def __init__(self) -> None:
        self._chunks: list[DocumentChunk] = []

    def clear(self) -> None:
        self._chunks.clear()

    def ingest(self, request: DocumentUploadRequest) -> list[DocumentChunk]:
        chunks = chunk_document(source=request.source, text=request.text)
        self._chunks = [chunk for chunk in self._chunks if chunk.source != request.source]
        self._chunks.extend(chunks)
        return chunks

    def search(self, query: str, limit: int = 5) -> list[KnowledgeSearchResult]:
        query_counts = Counter(_tokens(query))
        if not query_counts:
            return []

        scored: list[KnowledgeSearchResult] = []
        for chunk in self._chunks:
            chunk_counts = Counter(_tokens(chunk.content))
            overlap_score = sum(min(count, chunk_counts[token]) for token, count in query_counts.items())
            if overlap_score == 0:
                continue
            scored.append(
                KnowledgeSearchResult(
                    **chunk.model_dump(),
                    score=round(overlap_score / max(len(query_counts), 1), 3),
                )
            )

        return sorted(scored, key=lambda result: result.score, reverse=True)[:limit]


knowledge_store = KnowledgeStore()


def seed_knowledge_store() -> None:
    if knowledge_store.search("SSO", limit=1):
        return

    sample_path = Path(__file__).resolve().parents[3] / "sample-data" / "documents" / "security-sso.md"
    if sample_path.exists():
        knowledge_store.ingest(DocumentUploadRequest(source=sample_path.name, text=sample_path.read_text()))


seed_knowledge_store()

