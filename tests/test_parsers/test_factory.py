import pytest
from pathlib import Path

from backend.services.parsers.factory import ParserFactory, parser_factory
from backend.services.parsers.base import DocumentCategory, DocumentType
from backend.services.parsers.text_parser import TextParser
from backend.services.parsers.json_parser import JSONParser
from backend.services.parsers.pdf_parser import PDFParser


class TestParserFactory:
    """Tests for ParserFactory."""
    
    @pytest.fixture
    def factory(self):
        """Create a ParserFactory instance."""
        return ParserFactory()
    
    def test_singleton_exists(self):
        """Test that parser_factory singleton exists."""
        assert parser_factory is not None
        assert isinstance(parser_factory, ParserFactory)
    
    def test_get_parser_for_txt(self, factory):
        """Test getting parser for .txt files."""
        parser = factory.get_parser(Path("test.txt"))
        
        assert parser is not None
        assert isinstance(parser, TextParser)
    
    def test_get_parser_for_md(self, factory):
        """Test getting parser for .md files."""
        parser = factory.get_parser(Path("test.md"))
        
        assert parser is not None
        assert isinstance(parser, TextParser)
    
    def test_get_parser_for_json(self, factory):
        """Test getting parser for .json files."""
        parser = factory.get_parser(Path("test.json"))
        
        assert parser is not None
        assert isinstance(parser, JSONParser)
    
    def test_get_parser_for_pdf(self, factory):
        """Test getting parser for .pdf files."""
        parser = factory.get_parser(Path("test.pdf"))
        
        assert parser is not None
        assert isinstance(parser, PDFParser)
    
    def test_get_parser_for_unknown(self, factory):
        """Test getting parser for unknown extension."""
        parser = factory.get_parser(Path("test.xyz"))
        
        assert parser is None
    
    def test_supported_extensions(self, factory):
        """Test listing supported extensions."""
        extensions = factory.supported_extensions()
        
        assert '.txt' in extensions
        assert '.md' in extensions
        assert '.json' in extensions
        assert '.pdf' in extensions
        assert '.docx' in extensions
    
    def test_parse_text_file(self, factory, sample_text_file):
        """Test parsing a text file through factory."""
        result = factory.parse(sample_text_file)
        
        assert result.parse_success is True
        assert result.doc_type == DocumentType.TXT
    
    def test_parse_with_category_hint(self, factory, sample_chat_file):
        """Test parsing with category hint."""
        result = factory.parse(
            sample_chat_file,
            category_hint=DocumentCategory.AI_CHAT_HISTORY
        )
        
        assert result.parse_success is True
        assert result.category == DocumentCategory.AI_CHAT_HISTORY
    
    def test_parse_unsupported_extension(self, factory, temp_dir):
        """Test parsing unsupported file extension."""
        unsupported_file = temp_dir / "test.xyz"
        unsupported_file.write_text("content")
        
        result = factory.parse(unsupported_file)
        
        assert result.parse_success is False
        assert result.doc_type == DocumentType.UNKNOWN
        assert "No parser available" in result.error_message