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
    summary="Upload car maintenance invoice"
)
async def upload_invoice(
    file: UploadFile = File(...)
):
    """
    Upload a car maintenance invoice (PDF format).
    
    Extracts: line items, totals, categories, vehicle info
    """
    file_ext = Path(file.filename).suffix.lower()
    if file_ext != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoices must be PDF format"
        )
    
    content = await file.read()
    
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum: {settings.max_upload_size_mb}MB"
        )
    
    save_dir = settings.invoices_dir
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
            category_hint=DocumentCategory.CAR_MAINTENANCE
        )
        
        if not parsed.parse_success:
            return ParseResultResponse(
                success=False,
                filename=file.filename,
                category="car_maintenance",
                doc_type=parsed.doc_type.value,
                error=parsed.error_message
            )
        
        metadata = parsed.metadata
        total = metadata.get("total", "N/A")
        message = f"Invoice uploaded. Total: ${total}"
        
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
            detail=f"Failed to parse invoice: {str(e)}"
        )


@router.get(
    "/",
    response_model=DocumentListResponse,
    summary="List all invoices"
)
async def list_invoices(
    limit: int = 20,
    offset: int = 0
):
    """
    List all uploaded car maintenance invoices.
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
    summary="Get spending summary"
)
async def get_spending_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get aggregated spending summary across all invoices:
    - Total spending
    - Category breakdown (motor, brakes, tires, etc.)
    - Timeline analysis
    """
    # TODO: Aggregate across all invoices
    
    return {
        "total_spending": 0,
        "category_breakdown": {},
        "invoice_count": 0,
        "message": "Not implemented yet"
    }


@router.get(
    "/{document_id}",
    summary="Get invoice details"
)
async def get_invoice_details(document_id: str):
    """
    Get detailed breakdown of a specific invoice.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Invoice not found: {document_id}"
    )


@router.get(
    "/{document_id}/line-items",
    summary="Get invoice line items"
)
async def get_invoice_line_items(document_id: str):
    """
    Get all line items from a specific invoice.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Invoice not found: {document_id}"
    )