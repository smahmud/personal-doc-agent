import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import Settings, get_settings

def get_test_settings() -> Settings:
    """Get settings configured for testing."""
    return Settings(
        debug=True,
        data_dir=Path(tempfile.mkdtemp()),
        documents_dir=Path(tempfile.mkdtemp()),
        chats_dir=Path(tempfile.mkdtemp()),
        kiro_dir=Path(tempfile.mkdtemp()),
        invoices_dir=Path(tempfile.mkdtemp()),
        vectordb_dir=Path(tempfile.mkdtemp()),
    )


@pytest.fixture
def test_settings() -> Settings:
    """Fixture for test settings."""
    return get_test_settings()
  
@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    app.dependency_overrides[get_settings] = get_test_settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    
@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
        
@pytest.fixture
def sample_text_file(temp_dir: Path) -> Path:
    """Create a sample text file."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("This is a sample text file.\nIt has multiple lines.\nUsed for testing.")
    return file_path
  
  
@pytest.fixture
def sample_markdown_file(temp_dir: Path) -> Path:
    """Create a sample markdown file."""
    file_path = temp_dir / "sample.md"
    content = """# Sample Markdown    

                 ## Introduction 

                  This is a **sample** markdown file.

                  ### Code Example

                  ```python
                  def hello():
                     print("Hello, World!")
                  ```
                  ### Links

                  Example Link
                  [https://example.com/](https://example.com/)
                  """
    file_path.write_text(content)
    return file_path

@pytest.fixture
def sample_json_file(temp_dir: Path) -> Path:
    """Create a sample JSON file."""
    import json
    
    file_path = temp_dir / "sample.json"
    data = {
        "name": "Test Document",
        "items": [1, 2, 3],
        "nested": {"key": "value"}
    }
    file_path.write_text(json.dumps(data, indent=2))
    return file_path
  
@pytest.fixture
def sample_chat_file(temp_dir: Path) -> Path:
    """Create a sample AI chat history file."""
    import json
    
    file_path = temp_dir / "claude_chat.json"
    data = [
        {
            "role": "user",
            "content": "How do I use git?",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "Here are git commands:\n\ngit init\ngit add .\ngit commit -m 'Initial commit'",
            "timestamp": "2024-01-15T10:00:05Z"
        },
        {
            "role": "user",
            "content": "How do I push to remote?",
            "timestamp": "2024-01-15T10:01:00Z"
        },
        {
            "role": "assistant",
            "content": "Use this command:\n\ngit push origin main",
            "timestamp": "2024-01-15T10:01:05Z"
        }
    ]
    file_path.write_text(json.dumps(data, indent=2))
    return file_path
  
@pytest.fixture
def sample_kiro_file(temp_dir: Path) -> Path:
    """Create a sample Kiro IDE log file."""
    import json
    
    file_path = temp_dir / "kiro_logs.json"
    data = [
        {
            "task_id": "TASK-001",
            "status": "completed",
            "credits": 10,
            "duration": 3600,
            "description": "Implement user authentication",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "task_id": "TASK-002",
            "status": "in_progress",
            "credits": 5,
            "duration": 1800,
            "description": "Fix bug in payment module",
            "timestamp": "2024-01-15T11:00:00Z"
        },
        {
            "task_id": "TASK-003",
            "status": "completed",
            "credits": 15,
            "duration": 7200,
            "description": "Add API documentation",
            "timestamp": "2024-01-15T12:00:00Z"
        }
    ]
    file_path.write_text(json.dumps(data, indent=2))
    return file_path
  