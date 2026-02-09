from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.config import settings
from backend.models import (
    DocumentListResponse,
    ParseResultResponse,
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
    summary="Upload AI chat history"
)
async def upload_chat_history(
    file: UploadFile = File(...),
    platform: Optional[str] = None  # claude, copilot, gemini, perplexity
):
    """
    Upload an AI chat history export (JSON format).
    
    Supported platforms: Claude, Copilot, Gemini, Perplexity, ChatGPT
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".json", ".jsonl"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat history must be JSON or JSONL format"
        )
    
    content = await file.read()
    
    # Save file
    save_dir = settings.chats_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file.filename
    
    counter = 1
    while save_path.exists():
        stem = Path(file.filename).stem
        save_path = save_dir / f"{stem}_{counter}{file_ext}"
        counter += 1
    
    save_path.write_bytes(content)
    
    # Parse with AI chat category hint
    try:
        parsed = parser_factory.parse(
            save_path,
            category_hint=DocumentCategory.AI_CHAT_HISTORY
        )
        
        if not parsed.parse_success:
            return ParseResultResponse(
                success=False,
                filename=file.filename,
                category="ai_chat_history",
                doc_type=parsed.doc_type.value,
                error=parsed.error_message
            )
        
        return ParseResultResponse(
            success=True,
            document_id=parsed.id,
            filename=parsed.filename,
            category=parsed.category.value,
            doc_type=parsed.doc_type.value,
            word_count=parsed.word_count,
            chunk_count=len(parsed.chunks),
            message=f"Chat history uploaded. Platform: {parsed.metadata.get('platform', 'unknown')}"
        )
        
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse chat history: {str(e)}"
        )


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List all chat histories"
)
async def list_chat_histories(
    platform: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """
    List all uploaded chat histories with optional platform filter.
    """
    # TODO: Implement with vector store
    
    return DocumentListResponse(
        success=True,
        documents=[],
        total=0,
        limit=limit,
        offset=offset
    )


@router.get(
    "/{document_id}/commands",
    summary="Extract commands from chat history"
)
async def get_extracted_commands(document_id: str):
    """
    Get all extracted CLI commands from a chat history.
    
    Returns categorized commands: git, docker, aws, kubectl, npm, pip, powershell
    """
    # TODO: Implement command extraction lookup
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document not found: {document_id}"
    )


@router.get(
    "/{document_id}/analysis",
    summary="Get chat analysis"
)
async def get_chat_analysis(document_id: str):
    """
    Get analysis of a chat history including:
    - Sentiment/frustration detection
    - Code issue patterns
    - Topic breakdown
    """
    # TODO: Implement analysis
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document not found: {document_id}"
    )