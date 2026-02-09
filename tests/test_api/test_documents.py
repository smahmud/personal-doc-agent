import pytest
from fastapi.testclient import TestClient
from pathlib import Path


class TestDocumentsAPI:
    """Tests for documents API endpoints."""
    
    def test_list_documents_empty(self, client: TestClient):
        """Test listing documents when none exist."""
        response = client.get("/api/v1/documents/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["documents"] == []
        assert data["total"] == 0
    
    def test_list_documents_with_pagination(self, client: TestClient):
        """Test listing documents with pagination params."""
        response = client.get("/api/v1/documents/?limit=10&offset=0")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0
    
    def test_get_document_not_found(self, client: TestClient):
        """Test getting a document that doesn't exist."""
        response = client.get("/api/v1/documents/nonexistent123")
        
        assert response.status_code == 404
    
    def test_delete_document_not_found(self, client: TestClient):
        """Test deleting a document that doesn't exist."""
        response = client.delete("/api/v1/documents/nonexistent123")
        
        assert response.status_code == 404
    
    def test_search_documents_empty(self, client: TestClient):
        """Test searching when no documents exist."""
        response = client.post(
            "/api/v1/documents/search",
            json={"query": "test query", "limit": 10}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "test query"
        assert data["results"] == []
    
    def test_upload_unsupported_file_type(self, client: TestClient, temp_dir: Path):
        """Test uploading an unsupported file type."""
        # Create a file with unsupported extension
        test_file = temp_dir / "test.xyz"
        test_file.write_text("test content")
        
        with open(test_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("test.xyz", f, "application/octet-stream")}
            )
        
        assert response.status_code == 400
        assert "Unsupported file type" in response.json()["detail"]
    
    def test_upload_text_file(self, client: TestClient, sample_text_file: Path):
        """Test uploading a text file."""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("sample.txt", f, "text/plain")}
            )

        assert response.status_code == 201

        data = response.json()
        assert data["success"] is True
        assert data["filename"].startswith("sample")  # May be sample.txt or sample_1.txt
        assert data["filename"].endswith(".txt")
        assert data["doc_type"] == "txt"
        assert data["chunk_count"] > 0

class TestDocumentsAPIValidation:
    """Tests for documents API input validation."""
    
    def test_search_missing_query(self, client: TestClient):
        """Test search with missing query field."""
        response = client.post(
            "/api/v1/documents/search",
            json={"limit": 10}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_search_empty_query(self, client: TestClient):
        """Test search with empty query."""
        response = client.post(
            "/api/v1/documents/search",
            json={"query": "", "limit": 10}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_category(self, client: TestClient, sample_text_file: Path):
        """Test upload with invalid category."""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/api/v1/documents/upload",
                files={"file": ("sample.txt", f, "text/plain")},
                data={"category": "invalid_category"}
            )
        
        assert response.status_code == 400
        assert "Invalid category" in response.json()["detail"]