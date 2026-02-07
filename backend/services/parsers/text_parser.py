import re
from pathlib import Path
from typing import Any

from .base import (
    BaseParser,
    ParsedDocument,
    DocumentCategory,
    DocumentType
)


class TextParser(BaseParser):
    """Parser for plain text and markdown files."""
    
    supported_extensions = ['.txt', '.md', '.markdown', '.rst', '.log']
    
    def parse(self, filepath: Path) -> ParsedDocument:
        """Extract text from plain text files."""
        try:
            # Try multiple encodings
            raw_text = None
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    raw_text = filepath.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            
            if raw_text is None:
                raise ValueError("Unable to decode file with supported encodings")
            
            metadata = self.extract_metadata(filepath)
            metadata['encoding'] = encoding
            
            # Detect if markdown
            doc_type = DocumentType.MD if filepath.suffix.lower() in ['.md', '.markdown'] else DocumentType.TXT
            
            # Extract markdown-specific metadata
            if doc_type == DocumentType.MD:
                metadata.update(self._extract_markdown_metadata(raw_text))
            
            category = self.detect_category(filepath, raw_text)
            
            return ParsedDocument(
                id=self.generate_id(filepath),
                filename=filepath.name,
                filepath=str(filepath),
                category=category,
                doc_type=doc_type,
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
                doc_type=DocumentType.TXT,
                raw_text="",
                parse_success=False,
                error_message=str(e)
            )
    
    def extract_metadata(self, filepath: Path) -> dict[str, Any]:
        """Extract text file metadata."""
        stat = filepath.stat()
        
        return {
            'file_size_bytes': stat.st_size,
            'created_time': stat.st_ctime,
            'modified_time': stat.st_mtime,
            'extension': filepath.suffix.lower()
        }
    
    def _extract_markdown_metadata(self, text: str) -> dict[str, Any]:
        """Extract markdown-specific elements."""
        headings = re.findall(r'^#{1,6}\s+(.+)$', text, re.MULTILINE)
        code_blocks = re.findall(r'```(\w+)?', text)
        links = re.findall(r'$$([^$$]+)\]\(([^)]+)\)', text)
        
        return {
            'headings': headings[:20],  # Limit for metadata
            'heading_count': len(headings),
            'code_block_count': len(code_blocks),
            'code_languages': list(set(filter(None, code_blocks))),
            'link_count': len(links)
        }