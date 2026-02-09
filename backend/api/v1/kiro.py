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
    summary="Upload Kiro IDE logs"
)
async def upload_kiro_logs(
    file: UploadFile = File(...)
):
    """
    Upload Kiro IDE log files (JSON format).
    
    Extracts: task IDs, credits used, time spent, status
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in [".json", ".jsonl"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kiro logs must be JSON or JSONL format"
        )
    
    content = await file.read()
    
    save_dir = settings.kiro_dir
    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / file.filename
    
    counter = 1
    while save_path.exists():
        stem = Path(file.filename).stem
        save_path = save_dir / f"{stem}_{counter}{file_ext}"
        counter += 1
    
    save_path.write_bytes(content)
    
    try:
        parsed = parser_factory.parse(
            save_path,
            category_hint=DocumentCategory.KIRO_IDE_LOGS
        )
        
        if not parsed.parse_success:
            return ParseResultResponse(
                success=False,
                filename=file.filename,
                category="kiro_ide_logs",
                doc_type=parsed.doc_type.value,
                error=parsed.error_message
            )
        
        # Extract summary stats
        metadata = parsed.metadata
        message = (
            f"Kiro logs uploaded. "
            f"Tasks: {metadata.get('task_count', 0)}, "
            f"Credits: {metadata.get('total_credits_used', 0)}, "
            f"Hours: {metadata.get('total_time_hours', 0)}"
        )
        
        return ParseResultResponse(
            success=True,
            document_id=parsed.id,
            filename=parsed.filename,
            category=parsed.category.value,
            doc_type=parsed.doc_type.value,
            word_count=parsed.word_count,
            chunk_count=len(parsed.chunks),
            message=message
        )
        
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse Kiro logs: {str(e)}"
        )


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List all Kiro log files"
)
async def list_kiro_logs(
    limit: int = 20,
    offset: int = 0
):
    """
    List all uploaded Kiro IDE log files.
    """
    return DocumentListResponse(
        success=True,
        documents=[],
        total=0,
        limit=limit,
        offset=offset
    )


@router.get(
    "/summary",
    summary="Get Kiro usage summary"
)
async def get_kiro_summary():
    """
    Get aggregated summary across all Kiro logs:
    - Total tasks
    - Total credits used
    - Total time spent
    - Status breakdown
    """
    # TODO: Aggregate across all Kiro logs
    
    return {
        "total_tasks": 0,
        "total_credits": 0,
        "total_hours": 0,
        "status_breakdown": {},
        "message": "Not implemented yet"
    }


@router.get(
    "/{document_id}/tasks",
    summary="Get tasks from a Kiro log"
)
async def get_kiro_tasks(
    document_id: str,
    status_filter: Optional[str] = None
):
    """
    Get all tasks from a specific Kiro log file.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Document not found: {document_id}"
    )