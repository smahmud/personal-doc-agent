import fitz  # PyMuPDF
from pathlib import Path
from typing import Any

from .base import (
    BaseParser,
    ParsedDocument,
    DocumentCategory,
    DocumentType
)


class PDFParser(BaseParser):
    """Parser for PDF documents including invoices."""
    
    supported_extensions = ['.pdf']
    
    def parse(self, filepath: Path) -> ParsedDocument:
        """Extract text and metadata from PDF."""
        try:
            doc = fitz.open(filepath)
            
            # Extract text from all pages
            pages_text = []
            for page_num, page in enumerate(doc):
                text = page.get_text("text")
                pages_text.append(text)
            
            raw_text = "\n\n".join(pages_text)
            metadata = self.extract_metadata(filepath)
            metadata['page_texts'] = pages_text
            
            # Detect category
            category = self.detect_category(filepath, raw_text)
            
            # Create parsed document
            parsed = ParsedDocument(
                id=self.generate_id(filepath),
                filename=filepath.name,
                filepath=str(filepath),
                category=category,
                doc_type=DocumentType.PDF,
                raw_text=raw_text,
                chunks=self.chunk_text(raw_text),
                metadata=metadata,
                page_count=len(doc),
                parse_success=True
            )
            
            doc.close()
            return parsed
            
        except Exception as e:
            return ParsedDocument(
                id=self.generate_id(filepath),
                filename=filepath.name,
                filepath=str(filepath),
                category=DocumentCategory.GENERAL,
                doc_type=DocumentType.PDF,
                raw_text="",
                parse_success=False,
                error_message=str(e)
            )
    
    def extract_metadata(self, filepath: Path) -> dict[str, Any]:
        """Extract PDF-specific metadata."""
        try:
            doc = fitz.open(filepath)
            meta = doc.metadata
            
            metadata = {
                'title': meta.get('title', ''),
                'author': meta.get('author', ''),
                'subject': meta.get('subject', ''),
                'creator': meta.get('creator', ''),
                'producer': meta.get('producer', ''),
                'creation_date': meta.get('creationDate', ''),
                'modification_date': meta.get('modDate', ''),
                'file_size_bytes': filepath.stat().st_size
            }
            
            doc.close()
            return metadata
            
        except Exception:
            return {'file_size_bytes': filepath.stat().st_size}