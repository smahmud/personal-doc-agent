import pytest
from pathlib import Path

from backend.services.parsers.text_parser import TextParser
from backend.services.parsers.base import DocumentCategory, DocumentType


class TestTextParser:
    """Tests for TextParser."""
    
    @pytest.fixture
    def parser(self):
        """Create a TextParser instance."""
        return TextParser()
    
    def test_supported_extensions(self, parser):
        """Test supported file extensions."""
        assert '.txt' in parser.supported_extensions
        assert '.md' in parser.supported_extensions
        assert '.markdown' in parser.supported_extensions
        assert '.log' in parser.supported_extensions
    
    def test_parse_text_file(self, parser, sample_text_file):
        """Test parsing a simple text file."""
        result = parser.parse(sample_text_file)
        
        assert result.parse_success is True
        assert result.filename == "sample.txt"
        assert result.doc_type == DocumentType.TXT
        assert "sample text file" in result.raw_text
        assert result.word_count > 0
    
    def test_parse_markdown_file(self, parser, sample_markdown_file):
        """Test parsing a markdown file."""
        result = parser.parse(sample_markdown_file)
        
        assert result.parse_success is True
        assert result.filename == "sample.md"
        assert result.doc_type == DocumentType.MD
        assert "# Sample Markdown" in result.raw_text
        
        # Check markdown-specific metadata
        assert 'heading_count' in result.metadata
        assert 'code_block_count' in result.metadata
        assert result.metadata['heading_count'] > 0
    
    def test_parse_nonexistent_file(self, parser, temp_dir):
        """Test parsing a file that doesn't exist."""
        fake_path = temp_dir / "nonexistent.txt"
        result = parser.parse(fake_path)
        
        assert result.parse_success is False
        assert result.error_message is not None
    
    def test_chunks_created(self, parser, sample_text_file):
        """Test that text is chunked."""
        result = parser.parse(sample_text_file)
        
        assert result.parse_success is True
        assert len(result.chunks) > 0


class TestTextParserChunking:
    """Tests for text chunking functionality."""
    
    def test_chunk_small_text(self):
        """Test chunking text smaller than chunk size."""
        parser = TextParser(chunk_size=1000, chunk_overlap=200)
        
        small_text = "This is a small text."
        chunks = parser.chunk_text(small_text)
        
        assert len(chunks) == 1
        assert chunks[0] == small_text
    
    def test_chunk_large_text(self):
        """Test chunking text larger than chunk size."""
        parser = TextParser(chunk_size=100, chunk_overlap=20)
        
        # Create text larger than chunk size
        large_text = "This is a sentence. " * 20  # ~400 characters
        chunks = parser.chunk_text(large_text)
        
        assert len(chunks) > 1
    
    def test_chunk_overlap(self):
        """Test that chunks have overlap."""
        parser = TextParser(chunk_size=100, chunk_overlap=20)
        
        large_text = "Word " * 100  # 500 characters
        chunks = parser.chunk_text(large_text)
        
        # Check that chunks exist and overlap would cause more chunks
        assert len(chunks) >= 2
    
    def test_empty_text(self):
        """Test chunking empty text."""
        parser = TextParser()
        
        chunks = parser.chunk_text("")
        
        assert chunks == []