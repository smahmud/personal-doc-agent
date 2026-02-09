import pytest
import json
from pathlib import Path

from backend.services.parsers.json_parser import JSONParser
from backend.services.parsers.base import DocumentCategory, DocumentType


class TestJSONParser:
    """Tests for JSONParser."""
    
    @pytest.fixture
    def parser(self):
        """Create a JSONParser instance."""
        return JSONParser()
    
    def test_supported_extensions(self, parser):
        """Test supported file extensions."""
        assert '.json' in parser.supported_extensions
        assert '.jsonl' in parser.supported_extensions
    
    def test_parse_simple_json(self, parser, sample_json_file):
        """Test parsing a simple JSON file."""
        result = parser.parse(sample_json_file)
        
        assert result.parse_success is True
        assert result.doc_type == DocumentType.JSON
        assert result.word_count > 0
    
    def test_parse_chat_history(self, parser, sample_chat_file):
        """Test parsing AI chat history."""
        result = parser.parse(sample_chat_file)
        
        assert result.parse_success is True
        assert result.category == DocumentCategory.AI_CHAT_HISTORY
        
        # Check chat-specific metadata
        assert 'message_count' in result.metadata
        assert 'platform' in result.metadata
        assert result.metadata['message_count'] == 4
    
    def test_parse_kiro_logs(self, parser, sample_kiro_file):
        """Test parsing Kiro IDE logs."""
        result = parser.parse(sample_kiro_file)
        
        assert result.parse_success is True
        assert result.category == DocumentCategory.KIRO_IDE_LOGS
        
        # Check Kiro-specific metadata
        assert 'task_count' in result.metadata
        assert 'total_credits_used' in result.metadata
        assert result.metadata['task_count'] == 3
        assert result.metadata['total_credits_used'] == 30  # 10 + 5 + 15
    
    def test_command_extraction(self, parser, sample_chat_file):
        """Test that CLI commands are extracted from chat."""
        result = parser.parse(sample_chat_file)
        
        assert 'extracted_commands' in result.metadata
        commands = result.metadata['extracted_commands']
        
        # Should find git commands
        git_commands = [c for c in commands if c['type'] == 'git']
        assert len(git_commands) > 0
    
    def test_parse_invalid_json(self, parser, temp_dir):
        """Test parsing invalid JSON."""
        invalid_file = temp_dir / "invalid.json"
        invalid_file.write_text("{ this is not valid json }")
        
        result = parser.parse(invalid_file)
        
        assert result.parse_success is False
        assert result.error_message is not None


class TestJSONParserCommandExtraction:
    """Tests for command extraction functionality."""
    
    def test_extract_git_commands(self):
        """Test extracting git commands."""
        parser = JSONParser()
        
        text = """
        Use git init to start a new repo.
        Then run git add . to stage files.
        Finally git commit -m 'message' to commit.
        """
        
        commands = parser._extract_commands(text)
        git_commands = [c for c in commands if c['type'] == 'git']
        
        assert len(git_commands) >= 3
    
    def test_extract_docker_commands(self):
        """Test extracting docker commands."""
        parser = JSONParser()
        
        text = """
        Run docker build -t myapp .
        Then docker run -p 8080:80 myapp
        Use docker-compose up -d for multiple services.
        """
        
        commands = parser._extract_commands(text)
        docker_commands = [c for c in commands if c['type'] == 'docker']
        
        assert len(docker_commands) >= 2
    
    def test_extract_multiple_command_types(self):
        """Test extracting multiple command types."""
        parser = JSONParser()
        
        text = """
        First git clone the repo.
        Then pip install -r requirements.txt
        Finally docker build and docker run.
        """
        
        commands = parser._extract_commands(text)
        
        types = set(c['type'] for c in commands)
        assert 'git' in types
        assert 'pip' in types
        assert 'docker' in types