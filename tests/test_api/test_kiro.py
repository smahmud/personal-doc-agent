import pytest
from fastapi.testclient import TestClient
from pathlib import Path


class TestKiroAPI:
    """Tests for Kiro IDE logs API endpoints."""
    
    def test_list_kiro_logs_empty(self, client: TestClient):
        """Test listing Kiro logs when none exist."""
        response = client.get("/api/v1/kiro/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["documents"] == []
    
    def test_get_kiro_summary(self, client: TestClient):
        """Test getting Kiro summary."""
        response = client.get("/api/v1/kiro/summary")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "total_tasks" in data
        assert "total_credits" in data
        assert "total_hours" in data
    
    def test_upload_kiro_logs(self, client: TestClient, sample_kiro_file: Path):
        """Test uploading Kiro logs."""
        with open(sample_kiro_file, "rb") as f:
            response = client.post(
                "/api/v1/kiro/upload",
                files={"file": ("kiro_logs.json", f, "application/json")}
            )
        
        assert response.status_code == 201
        
        data = response.json()
        assert data["success"] is True
        assert data["category"] == "kiro_ide_logs"
        assert "Tasks:" in data["message"]
    
    def test_upload_invalid_format(self, client: TestClient, sample_text_file: Path):
        """Test uploading non-JSON file to Kiro endpoint."""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/api/v1/kiro/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "JSON" in response.json()["detail"]