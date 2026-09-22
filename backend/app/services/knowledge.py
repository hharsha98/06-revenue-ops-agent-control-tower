import re
from collections import Counter

from backend.app.core.paths import repo_root
from backend.app.models.knowledge import (
    DocumentChunk,
    DocumentUploadRequest,
    KnowledgeSearchResult,
)
from backend.app.models.tower import DocumentRecord

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

        scored: list[tuple[KnowledgeSearchResult, int]] = []
        for chunk in self._chunks:
            chunk_counts = Counter(_tokens(chunk.content))
            overlap_score = sum(min(count, chunk_counts[token]) for token, count in query_counts.items())
            if overlap_score == 0:
                continue
            frequency = sum(chunk_counts[token] for token in query_counts)
            scored.append(
                (
                    KnowledgeSearchResult(
                        **chunk.model_dump(),
                        score=round(overlap_score / max(len(query_counts), 1), 3),
                    ),
                    frequency,
                )
            )

        scored.sort(key=lambda item: (item[0].score, item[1]), reverse=True)
        return [item[0] for item in scored[:limit]]

    def list_documents(self) -> list[DocumentRecord]:
        grouped: dict[str, list[DocumentChunk]] = {}
        for chunk in self._chunks:
            grouped.setdefault(chunk.source, []).append(chunk)
        records: list[DocumentRecord] = []
        for source, chunks in sorted(grouped.items()):
            preview = chunks[0].content[:220]
            records.append(DocumentRecord(source=source, chunks=len(chunks), preview=preview))
        return records

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)


knowledge_store = KnowledgeStore()
_SEEDED = False


def seed_knowledge_store() -> None:
    global _SEEDED
    if _SEEDED:
        return

    sample_dir = repo_root() / "sample-data" / "documents"
    paths = sorted(sample_dir.glob("*.md")) if sample_dir.exists() else []
    for path in paths:
        knowledge_store.ingest(
            DocumentUploadRequest(source=path.name, text=path.read_text(encoding="utf-8"))
        )
    _SEEDED = True


seed_knowledge_store()

