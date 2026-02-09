import pytest
from fastapi.testclient import TestClient
from pathlib import Path


class TestChatAPI:
    """Tests for AI chat history API endpoints."""
    
    def test_list_chat_histories_empty(self, client: TestClient):
        """Test listing chat histories when none exist."""
        response = client.get("/api/v1/chat/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["documents"] == []
    
    def test_upload_chat_history(self, client: TestClient, sample_chat_file: Path):
        """Test uploading chat history."""
        with open(sample_chat_file, "rb") as f:
            response = client.post(
                "/api/v1/chat/upload",
                files={"file": ("claude_chat.json", f, "application/json")}
            )
        
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
        assert data["category"] == "ai_chat_history"
    
    def test_upload_invalid_format(self, client: TestClient, sample_text_file: Path):
        """Test uploading non-JSON file to chat endpoint."""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/api/v1/chat/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "JSON" in response.json()["detail"]
    
    def test_get_commands_not_found(self, client: TestClient):
        """Test getting commands for non-existent document."""
        response = client.get("/api/v1/chat/nonexistent123/commands")
        
        assert response.status_code == 404
    
    def test_get_analysis_not_found(self, client: TestClient):
        """Test getting analysis for non-existent document."""
        response = client.get("/api/v1/chat/nonexistent123/analysis")
        
        assert response.status_code == 404