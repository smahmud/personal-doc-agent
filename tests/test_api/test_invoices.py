import pytest
from fastapi.testclient import TestClient
from pathlib import Path


class TestInvoicesAPI:
    """Tests for car maintenance invoices API endpoints."""
    
    def test_list_invoices_empty(self, client: TestClient):
        """Test listing invoices when none exist."""
        response = client.get("/api/v1/invoices/")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["documents"] == []
    
    def test_get_spending_summary(self, client: TestClient):
        """Test getting spending summary."""
        response = client.get("/api/v1/invoices/summary")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "total_spending" in data
        assert "category_breakdown" in data
        assert "invoice_count" in data
    
    def test_upload_non_pdf(self, client: TestClient, sample_text_file: Path):
        """Test uploading non-PDF file to invoices endpoint."""
        with open(sample_text_file, "rb") as f:
            response = client.post(
                "/api/v1/invoices/upload",
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]
    
    def test_get_invoice_not_found(self, client: TestClient):
        """Test getting non-existent invoice."""
        response = client.get("/api/v1/invoices/nonexistent123")
        
        assert response.status_code == 404
    
    def test_get_line_items_not_found(self, client: TestClient):
        """Test getting line items for non-existent invoice."""
        response = client.get("/api/v1/invoices/nonexistent123/line-items")
        
        assert response.status_code == 404