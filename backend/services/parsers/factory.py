from pathlib import Path
from typing import Optional

from .base import BaseParser, ParsedDocument, DocumentCategory
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .text_parser import TextParser
from .json_parser import JSONParser
from .invoice_parser import InvoiceParser


class ParserFactory:
    """Factory for selecting appropriate parser based on file type and category."""
    
    def __init__(self):
        self._parsers: dict[str, BaseParser] = {
            '.pdf': PDFParser(),
            '.docx': DOCXParser(),
            '.doc': DOCXParser(),
            '.txt': TextParser(),
            '.md': TextParser(),
            '.markdown': TextParser(),
            '.rst': TextParser(),
            '.log': TextParser(),
            '.json': JSONParser(),
            '.jsonl': JSONParser()
        }
        
        # Specialized parsers
        self._invoice_parser = InvoiceParser()
    
    def get_parser(
        self,
        filepath: Path,
        category_hint: Optional[DocumentCategory] = None
    ) -> Optional[BaseParser]:
        """Get appropriate parser for file."""
        suffix = filepath.suffix.lower()
        
        # Use specialized invoice parser for car maintenance PDFs
        if suffix == '.pdf' and category_hint == DocumentCategory.CAR_MAINTENANCE:
            return self._invoice_parser
        
        # Auto-detect invoice from filename
        if suffix == '.pdf':
            filename_lower = filepath.name.lower()
            if any(x in filename_lower for x in ['invoice', 'dealer', 'maintenance', 'receipt']):
                return self._invoice_parser
        
        return self._parsers.get(suffix)
    
    def parse(
        self,
        filepath: Path,
        category_hint: Optional[DocumentCategory] = None
    ) -> ParsedDocument:
        """Parse file using appropriate parser."""
        parser = self.get_parser(filepath, category_hint)
        
        if parser is None:
            from .base import DocumentType
            return ParsedDocument(
                id="unknown",
                filename=filepath.name,
                filepath=str(filepath),
                category=DocumentCategory.GENERAL,
                doc_type=DocumentType.UNKNOWN,
                raw_text="",
                parse_success=False,
                error_message=f"No parser available for extension: {filepath.suffix}"
            )
        
        return parser.parse(filepath)
    
    def supported_extensions(self) -> list[str]:
        """List all supported file extensions."""
        return list(self._parsers.keys())


# Singleton instance
parser_factory = ParserFactory()
