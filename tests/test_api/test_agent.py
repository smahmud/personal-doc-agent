import pytest
from fastapi.testclient import TestClient


class TestAgentAPI:
    """Tests for agent API endpoints."""
    
    def test_query_agent(self, client: TestClient):
        """Test querying the agent."""
        response = client.post(
            "/api/v1/agent/query",
            json={
                "query": "What documents do I have?",
                "include_sources": True,
                "max_results": 5
            }
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "What documents do I have?"
        assert "answer" in data
        assert "sources" in data
        assert "reasoning_steps" in data
        assert "processing_time_ms" in data
    
    def test_query_agent_minimal(self, client: TestClient):
        """Test querying agent with minimal params."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "Hello"}
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
    
    def test_query_agent_empty_query(self, client: TestClient):
        """Test querying agent with empty query."""
        response = client.post(
            "/api/v1/agent/query",
            json={"query": ""}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_query_agent_stream_not_implemented(self, client: TestClient):
        """Test streaming endpoint returns not implemented."""
        response = client.post(
            "/api/v1/agent/query/stream",
            json={"query": "Test"}
        )
        
        assert response.status_code == 501


class TestAgentAPIValidation:
    """Tests for agent API input validation."""
    
    def test_max_results_validation(self, client: TestClient):
        """Test max_results bounds validation."""
        # Too high
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "test", "max_results": 100}
        )
        assert response.status_code == 422
        
        # Too low
        response = client.post(
            "/api/v1/agent/query",
            json={"query": "test", "max_results": 0}
        )
        assert response.status_code == 422
    
    def test_query_length_validation(self, client: TestClient):
        """Test query length validation."""
        # Too long
        long_query = "x" * 2001
        response = client.post(
            "/api/v1/agent/query",
            json={"query": long_query}
        )
        assert response.status_code == 422