import pytest
from datetime import datetime, timezone

from backend.services.parsers.base import (
    DocumentCategory,
    DocumentType,
    ParsedDocument,
    BaseParser,
    utc_now,
)


class TestDocumentCategory:
    """Tests for DocumentCategory enum."""
    
    def test_all_categories_exist(self):
        """Verify all expected categories exist."""
        assert DocumentCategory.GENERAL.value == "general"
        assert DocumentCategory.AI_CHAT_HISTORY.value == "ai_chat_history"
        assert DocumentCategory.KIRO_IDE_LOGS.value == "kiro_ide_logs"
        assert DocumentCategory.CAR_MAINTENANCE.value == "car_maintenance"
    
    def test_category_count(self):
        """Verify we have exactly 4 categories."""
        assert len(DocumentCategory) == 4


class TestDocumentType:
    """Tests for DocumentType enum."""
    
    def test_all_types_exist(self):
        """Verify all expected document types exist."""
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.DOCX.value == "docx"
        assert DocumentType.TXT.value == "txt"
        assert DocumentType.MD.value == "md"
        assert DocumentType.JSON.value == "json"
        assert DocumentType.UNKNOWN.value == "unknown"


class TestParsedDocument:
    """Tests for ParsedDocument dataclass."""
    
    def test_create_minimal_document(self):
        """Test creating a document with minimal fields."""
        doc = ParsedDocument(
            id="test123",
            filename="test.txt",
            filepath="/path/to/test.txt",
            category=DocumentCategory.GENERAL,
            doc_type=DocumentType.TXT,
            raw_text="Hello, World!"
        )
        
        assert doc.id == "test123"
        assert doc.filename == "test.txt"
        assert doc.category == DocumentCategory.GENERAL
        assert doc.doc_type == DocumentType.TXT
        assert doc.raw_text == "Hello, World!"
        assert doc.parse_success is True
        assert doc.error_message is None
    
    def test_word_count_calculated(self):
        """Test that word count is calculated automatically."""
        doc = ParsedDocument(
            id="test123",
            filename="test.txt",
            filepath="/path/to/test.txt",
            category=DocumentCategory.GENERAL,
            doc_type=DocumentType.TXT,
            raw_text="One two three four five"
        )
        
        assert doc.word_count == 5
    
    def test_timestamps_are_utc(self):
        """Test that timestamps are timezone-aware UTC."""
        doc = ParsedDocument(
            id="test123",
            filename="test.txt",
            filepath="/path/to/test.txt",
            category=DocumentCategory.GENERAL,
            doc_type=DocumentType.TXT,
            raw_text="Test"
        )
        
        assert doc.created_at.tzinfo == timezone.utc
        assert doc.parsed_at.tzinfo == timezone.utc
    
    def test_failed_parse(self):
        """Test creating a failed parse result."""
        doc = ParsedDocument(
            id="test123",
            filename="test.txt",
            filepath="/path/to/test.txt",
            category=DocumentCategory.GENERAL,
            doc_type=DocumentType.UNKNOWN,
            raw_text="",
            parse_success=False,
            error_message="Failed to read file"
        )
        
        assert doc.parse_success is False
        assert doc.error_message == "Failed to read file"


class TestUtcNow:
    """Tests for utc_now function."""
    
    def test_returns_datetime(self):
        """Test that utc_now returns a datetime."""
        result = utc_now()
        assert isinstance(result, datetime)
    
    def test_is_timezone_aware(self):
        """Test that the datetime is timezone-aware."""
        result = utc_now()
        assert result.tzinfo is not None
        assert result.tzinfo == timezone.utc