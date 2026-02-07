

from docx import Document
from pathlib import Path
from typing import Any

from .base import (
    BaseParser,
    ParsedDocument,
    DocumentCategory,
    DocumentType
)


class DOCXParser(BaseParser):
    """Parser for Microsoft Word documents."""
    
    supported_extensions = ['.docx', '.doc']
    
    def parse(self, filepath: Path) -> ParsedDocument:
        """Extract text and metadata from DOCX."""
        try:
            doc = Document(filepath)
            
            # Extract paragraphs
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            
            # Extract tables
            tables_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_text = [cell.text for cell in row.cells]
                    tables_text.append(" | ".join(row_text))
            
            # Combine all text
            raw_text = "\n\n".join(paragraphs)
            if tables_text:
                raw_text += "\n\n--- Tables ---\n" + "\n".join(tables_text)
            
            metadata = self.extract_metadata(filepath)
            metadata['paragraph_count'] = len(paragraphs)
            metadata['table_count'] = len(doc.tables)
            
            category = self.detect_category(filepath, raw_text)
            
            return ParsedDocument(
                id=self.generate_id(filepath),
                filename=filepath.name,
                filepath=str(filepath),
                category=category,
                doc_type=DocumentType.DOCX,
                raw_text=raw_text,
                chunks=self.chunk_text(raw_text),
                metadata=metadata,
                parse_success=True
            )
            
        except Exception as e:
            return ParsedDocument(
                id=self.generate_id(filepath),
                filename=filepath.name,
                filepath=str(filepath),
                category=DocumentCategory.GENERAL,
                doc_type=DocumentType.DOCX,
                raw_text="",
                parse_success=False,
                error_message=str(e)
            )
    
    def extract_metadata(self, filepath: Path) -> dict[str, Any]:
        """Extract DOCX-specific metadata."""
        try:
            doc = Document(filepath)
            props = doc.core_properties
            
            return {
                'title': props.title or '',
                'author': props.author or '',
                'subject': props.subject or '',
                'created': str(props.created) if props.created else '',
                'modified': str(props.modified) if props.modified else '',
                'last_modified_by': props.last_modified_by or '',
                'file_size_bytes': filepath.stat().st_size
            }
            
        except Exception:
            return {'file_size_bytes': filepath.stat().st_size}