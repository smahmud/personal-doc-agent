from typing import Optional
from pydantic import BaseModel, Field


class DocumentUploadRequest(BaseModel):
    """Request schema for document upload metadata."""
    
    category: Optional[str] = Field(
        default=None,
        description="Document category: general, ai_chat_history, kiro_ide_logs, car_maintenance"
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Optional tags for the document"
    )
    description: Optional[str] = Field(
        default=None,
        description="Optional description of the document"
    )


class AgentQueryRequest(BaseModel):
    """Request schema for agent queries."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's natural language query"
    )
    category: Optional[str] = Field(
        default=None,
        description="Limit search to specific category"
    )
    include_sources: bool = Field(
        default=True,
        description="Include source documents in response"
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of source documents to return"
    )


class SearchRequest(BaseModel):
    """Request schema for document search."""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query"
    )
    category: Optional[str] = Field(
        default=None,
        description="Filter by category"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum results to return"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Pagination offset"
    )