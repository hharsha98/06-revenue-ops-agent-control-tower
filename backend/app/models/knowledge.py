from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    source: str = Field(min_length=1)
    text: str = Field(min_length=20)


class DocumentChunk(BaseModel):
    id: str
    source: str
    chunk_index: int
    content: str


class DocumentIngestResponse(BaseModel):
    source: str
    chunks_created: int


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    limit: int = Field(default=5, ge=1, le=10)


class KnowledgeSearchResult(DocumentChunk):
    score: float


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeSearchResult]

