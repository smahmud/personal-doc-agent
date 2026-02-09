from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    version: str
    timestamp: datetime
    services: dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now())


class DocumentMetadata(BaseModel):
    """Document metadata schema."""
    
    id: str
    filename: str
    category: str
    doc_type: str
    word_count: Optional[int] = None
    page_count: Optional[int] = None
    created_at: datetime
    parsed_at: datetime
    tags: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    """Single document response."""
    
    success: bool = True
    document: DocumentMetadata
    message: Optional[str] = None


class DocumentListResponse(BaseModel):
    """Multiple documents response."""
    
    success: bool = True
    documents: list[DocumentMetadata]
    total: int
    limit: int
    offset: int


class ParseResultResponse(BaseModel):
    """Document parsing result."""
    
    success: bool
    document_id: Optional[str] = None
    filename: str
    category: str
    doc_type: str
    word_count: Optional[int] = None
    chunk_count: int = 0
    message: Optional[str] = None
    error: Optional[str] = None


class SourceDocument(BaseModel):
    """Source document reference in agent response."""
    
    document_id: str
    filename: str
    category: str
    relevance_score: float
    snippet: str


class AgentResponse(BaseModel):
    """Agent query response."""
    
    success: bool = True
    query: str
    answer: str
    sources: list[SourceDocument] = Field(default_factory=list)
    reasoning_steps: list[str] = Field(default_factory=list)
    processing_time_ms: int


class SearchResult(BaseModel):
    """Single search result."""
    
    document_id: str
    filename: str
    category: str
    score: float
    snippet: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    """Search results response."""
    
    success: bool = True
    query: str
    results: list[SearchResult]
    total: int
    limit: int
    offset: int