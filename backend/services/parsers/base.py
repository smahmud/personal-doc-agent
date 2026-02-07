from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class DocumentCategory(Enum):
    """Four core document categories for PDA V1."""
    GENERAL = "general"
    AI_CHAT_HISTORY = "ai_chat_history"
    KIRO_IDE_LOGS = "kiro_ide_logs"
    CAR_MAINTENANCE = "car_maintenance"

class DocumentType(Enum):
    """Supported file types."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    JSON = "json"
    UNKNOWN = "unknown"
    
def utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)    

@dataclass
class ParsedDocument:
    """Standardized output from all parsers."""
    
    # Identity
    id: str
    filename: str
    filepath: str
    
    # Classification
    category: DocumentCategory
    doc_type: DocumentType
    
    # Content
    raw_text: str
    chunks: list[str] = field(default_factory=list)
    
    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    
    # Timestamps
    created_at: datetime = field(default_factory=utc_now)
    parsed_at: datetime = field(default_factory=utc_now)
    
    # Processing flags
    parse_success: bool = True
    error_message: Optional[str] = None

    def __post_init__(self):
        """Calculate word count after initialization."""
        if self.raw_text and not self.word_count:
            self.word_count = len(self.raw_text.split())


class BaseParser(ABC):
    """Abstract base class for all document parsers."""
    
    supported_extensions: list[str] = []
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @abstractmethod
    def parse(self, filepath: Path) -> ParsedDocument:
        """Parse document and return standardized output."""
        pass
    
    @abstractmethod
    def extract_metadata(self, filepath: Path) -> dict[str, Any]:
        """Extract document-specific metadata."""
        pass
    
    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping chunks for vector storage."""
        if not text:
            return []
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < text_length:
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > self.chunk_size // 2:
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - self.chunk_overlap
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def generate_id(self, filepath: Path) -> str:
        """Generate unique document ID."""
        import hashlib
        content = f"{filepath.name}_{filepath.stat().st_mtime}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def detect_category(self, filepath: Path, content: str = "") -> DocumentCategory:
        """Auto-detect document category based on path and content."""
        path_lower = str(filepath).lower()
        
        if any(x in path_lower for x in ['invoice', 'dealer', 'maintenance', 'car', 'vehicle']):
            return DocumentCategory.CAR_MAINTENANCE
        
        if any(x in path_lower for x in ['kiro', 'ide', 'vscode']):
            return DocumentCategory.KIRO_IDE_LOGS
        
        if any(x in path_lower for x in ['chat', 'claude', 'copilot', 'gemini', 'perplexity']):
            return DocumentCategory.AI_CHAT_HISTORY
        
        return DocumentCategory.GENERAL