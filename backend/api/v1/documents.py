from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from backend.config import settings
from backend.models import (
    DocumentListResponse,
    DocumentResponse,
    ParseResultResponse,
    SearchRequest,
    SearchResponse,
)
from backend.services.parsers import (
    parser_factory,
    DocumentCategory,
)

router = APIRouter()


@router.post(
    "/upload",
    response_model=ParseResultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a document"
)
async def upload_document(
    file: UploadFile = File(...),
    category: Optional[str] = Form(default=None),
    tags: Optional[str] = Form(default=None),  # Comma-separated
    description: Optional[str] = Form(default=None)
):
    """
    Upload a document for parsing and indexing.
    
    Supported formats: PDF, DOCX, TXT, MD, JSON
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Allowed: {settings.allowed_extensions}"
        )
    
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
        )
    
    # Determine category
    if category:
        try:
            doc_category = DocumentCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {category}"
            )
    else:
        doc_category = None
    
    # Save file
    save_dir = settings.get_category_dir(category or "general")
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file.filename
    
    # Handle duplicate filenames
    counter = 1
    while save_path.exists():
        stem = Path(file.filename).stem
        save_path = save_dir / f"{stem}_{counter}{file_ext}"
        counter += 1
    
    save_path.write_bytes(content)
    
    # Parse document
    try:
        parsed = parser_factory.parse(save_path, category_hint=doc_category)
        
        if not parsed.parse_success:
            return ParseResultResponse(
                success=False,
                filename=file.filename,
                category=category or "general",
                doc_type=parsed.doc_type.value,
                error=parsed.error_message
            )
        
        # TODO: Index in vector store (Phase 2)
        
        return ParseResultResponse(
            success=True,
            document_id=parsed.id,
            filename=parsed.filename,
            category=parsed.category.value,
            doc_type=parsed.doc_type.value,
            word_count=parsed.word_count,
            chunk_count=len(parsed.chunks),
            message="Document uploaded and parsed successfully"
        )
        
    except Exception as e:
        # Clean up saved file on error
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse document: {str(e)}"
        )


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List all documents"
)
async def list_documents(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    List all indexed documents with optional category filter.
    """
    # TODO: Implement with vector store metadata query
    
    # Placeholder response
    return DocumentListResponse(
        success=True,
        documents=[],
        total=0,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document by ID"
)
async def get_document(document_id: str):
    """
    Retrieve a specific document by ID.
    """
    # TODO: Implement with vector store lookup
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document not found: {document_id}"
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document"
)
async def delete_document(document_id: str):
    """
    Delete a document from the system.
    """
    # TODO: Implement deletion from vector store and filesystem
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document not found: {document_id}"
    )


@router.post(
    "/search",
    response_model=SearchResponse,
    summary="Search documents"
)
async def search_documents(request: SearchRequest):
    """
    Search documents using semantic similarity.
    """
    # TODO: Implement with vector store search
    
    return SearchResponse(
        success=True,
        query=request.query,
        results=[],
        total=0,
        limit=request.limit,
        offset=request.offset
    )