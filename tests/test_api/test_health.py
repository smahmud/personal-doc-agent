import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client: TestClient):
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
        assert "services" in data
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API info."""
        response = client.get("/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Personal Documentation Agent"
        assert "version" in data
        assert data["docs"] == "/docs"
        assert data["health"] == "/health"
        assert data["api"] == "/api/v1"


class TestDocsEndpoint:
    """Tests for documentation endpoints."""
    
    def test_swagger_docs_available(self, client: TestClient):
        """Test Swagger UI is available."""
        response = client.get("/docs")
        
        assert response.status_code == 200
    
    def test_redoc_available(self, client: TestClient):
        """Test ReDoc is available."""
        response = client.get("/redoc")
        
        assert response.status_code == 200