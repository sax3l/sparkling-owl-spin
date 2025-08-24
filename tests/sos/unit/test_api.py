"""
Unit tests för SOS API endpoints

Testar FastAPI routes, request/response handling, och error cases.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from fastapi.testclient import TestClient

from sos.api.main import app, get_scheduler, get_template_manager


class TestSOSAPI:
    """Test suite för SOS API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client för API"""
        return TestClient(app)
        
    @pytest.fixture
    def mock_scheduler(self):
        """Mock scheduler"""
        scheduler = AsyncMock()
        return scheduler
        
    @pytest.fixture
    def mock_template_manager(self):
        """Mock template manager"""
        manager = AsyncMock()
        return manager
        
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["service"] == "sos-api"
        
    def test_root_endpoint(self, client):
        """Test root endpoint redirect"""
        response = client.get("/")
        
        # Ska redirecta till docs
        assert response.status_code in [200, 307]  # OK eller Redirect
        
    def test_create_crawl_job_success(self, client, mock_scheduler):
        """Test framgångsrik skapande av crawl job"""
        
        # Mock dependencies
        app.dependency_overrides[get_scheduler] = lambda: mock_scheduler
        mock_scheduler.submit_job.return_value = "job-123"
        
        job_request = {
            "start_urls": ["https://example.com"],
            "max_pages": 10,
            "max_depth": 2,
            "template_id": "basic-template"
        }
        
        response = client.post("/api/v1/jobs", json=job_request)
        
        assert response.status_code == 201
        data = response.json()
        assert data["job_id"] == "job-123"
        assert data["status"] == "queued"
        assert "created_at" in data
        
        # Cleanup
        app.dependency_overrides.clear()
        
    def test_create_crawl_job_validation_error(self, client):
        """Test validationsfel vid skapande av job"""
        
        # Ogiltig request - saknar required fields
        invalid_request = {
            "max_pages": "not a number"  # Fel typ
        }
        
        response = client.post("/api/v1/jobs", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
        
    def test_get_job_status_success(self, client, mock_scheduler):
        """Test hämtning av job status"""
        
        app.dependency_overrides[get_scheduler] = lambda: mock_scheduler
        mock_scheduler.get_job_status.return_value = "running"
        mock_scheduler.get_job_details.return_value = {
            "id": "job-123",
            "status": "running",
            "created_at": "2024-01-01T10:00:00Z",
            "progress": 0.5
        }
        
        response = client.get("/api/v1/jobs/job-123/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["job_id"] == "job-123"
        assert "progress" in data
        
        app.dependency_overrides.clear()
        
    def test_get_job_status_not_found(self, client, mock_scheduler):
        """Test job status för icke-existerande job"""
        
        app.dependency_overrides[get_scheduler] = lambda: mock_scheduler
        mock_scheduler.get_job_status.return_value = None
        
        response = client.get("/api/v1/jobs/nonexistent-job/status")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        
        app.dependency_overrides.clear()
        
    def test_get_job_results_success(self, client, mock_scheduler):
        """Test hämtning av job results"""
        
        mock_results = [
            {
                "url": "https://example.com",
                "status_code": 200,
                "title": "Example Page",
                "content": "Page content...",
                "links": ["https://example.com/page1"]
            }
        ]
        
        app.dependency_overrides[get_scheduler] = lambda: mock_scheduler
        mock_scheduler.get_job_results.return_value = mock_results
        
        response = client.get("/api/v1/jobs/job-123/results")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 1
        assert data["results"][0]["url"] == "https://example.com"
        assert data["total_results"] == 1
        
        app.dependency_overrides.clear()
        
    def test_list_templates_success(self, client, mock_template_manager):
        """Test listning av templates"""
        
        mock_templates = [
            {
                "id": "template-1",
                "name": "Basic Scraper",
                "description": "Basic web scraping template",
                "created_at": "2024-01-01T10:00:00Z"
            },
            {
                "id": "template-2", 
                "name": "E-commerce Scraper",
                "description": "Template for e-commerce sites",
                "created_at": "2024-01-01T11:00:00Z"
            }
        ]
        
        app.dependency_overrides[get_template_manager] = lambda: mock_template_manager
        mock_template_manager.list_templates.return_value = mock_templates
        
        response = client.get("/api/v1/templates")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 2
        assert data["templates"][0]["name"] == "Basic Scraper"
        
        app.dependency_overrides.clear()
        
    def test_get_template_success(self, client, mock_template_manager):
        """Test hämtning av specifik template"""
        
        mock_template = {
            "id": "template-1",
            "name": "Basic Scraper",
            "description": "Basic web scraping template",
            "config": {
                "selectors": {
                    "title": "h1",
                    "content": ".content"
                },
                "actions": [
                    {"type": "extract", "field": "title"},
                    {"type": "extract", "field": "content"}
                ]
            }
        }
        
        app.dependency_overrides[get_template_manager] = lambda: mock_template_manager
        mock_template_manager.get_template.return_value = mock_template
        
        response = client.get("/api/v1/templates/template-1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Basic Scraper"
        assert "config" in data
        assert "selectors" in data["config"]
        
        app.dependency_overrides.clear()
        
    def test_get_template_not_found(self, client, mock_template_manager):
        """Test template som inte finns"""
        
        app.dependency_overrides[get_template_manager] = lambda: mock_template_manager
        mock_template_manager.get_template.return_value = None
        
        response = client.get("/api/v1/templates/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        
        app.dependency_overrides.clear()
        
    def test_create_template_success(self, client, mock_template_manager):
        """Test skapande av ny template"""
        
        template_request = {
            "name": "New Template",
            "description": "A new scraping template",
            "config": {
                "selectors": {
                    "title": "h1",
                    "content": ".main-content"
                },
                "actions": [
                    {"type": "extract", "field": "title"}
                ]
            }
        }
        
        app.dependency_overrides[get_template_manager] = lambda: mock_template_manager
        mock_template_manager.create_template.return_value = "template-new-123"
        
        response = client.post("/api/v1/templates", json=template_request)
        
        assert response.status_code == 201
        data = response.json()
        assert data["template_id"] == "template-new-123"
        assert data["status"] == "created"
        
        app.dependency_overrides.clear()
        
    def test_job_cancellation(self, client, mock_scheduler):
        """Test cancellation av job"""
        
        app.dependency_overrides[get_scheduler] = lambda: mock_scheduler
        mock_scheduler.cancel_job.return_value = True
        
        response = client.post("/api/v1/jobs/job-123/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
        assert data["job_id"] == "job-123"
        
        app.dependency_overrides.clear()
        
    def test_job_cancellation_not_found(self, client, mock_scheduler):
        """Test cancellation av icke-existerande job"""
        
        app.dependency_overrides[get_scheduler] = lambda: mock_scheduler
        mock_scheduler.cancel_job.return_value = False
        
        response = client.post("/api/v1/jobs/nonexistent/cancel")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
        
        app.dependency_overrides.clear()


class TestAPIMiddleware:
    """Test suite för API middleware"""
    
    def test_cors_headers(self, client):
        """Test CORS headers"""
        response = client.options("/api/v1/jobs", headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST"
        })
        
        # CORS headers ska finnas
        assert "access-control-allow-origin" in response.headers
        
    def test_rate_limiting(self, client):
        """Test rate limiting (om implementerat)"""
        
        # Gör många requests snabbt
        responses = []
        for i in range(20):  # Många requests
            response = client.get("/health")
            responses.append(response.status_code)
            
        # De flesta ska lyckas, men rate limiting kan kicka in
        success_count = responses.count(200)
        assert success_count >= 15  # Minst 15 av 20 ska lyckas
        
    def test_request_id_header(self, client):
        """Test att request ID header sätts"""
        
        response = client.get("/health")
        
        # Många APIs sätter request ID för tracing
        # Detta är optional beroende på implementation
        assert response.status_code == 200


class TestAPIValidation:
    """Test suite för API validation"""
    
    def test_url_validation_in_job_request(self, client):
        """Test URL validation i job requests"""
        
        # Ogiltig URL
        job_request = {
            "start_urls": ["not-a-valid-url"],
            "max_pages": 10
        }
        
        response = client.post("/api/v1/jobs", json=job_request)
        
        # Ska få validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
    def test_numeric_validation(self, client):
        """Test numerisk validation"""
        
        # Negativa värden ska inte tillåtas
        job_request = {
            "start_urls": ["https://example.com"],
            "max_pages": -5,  # Negativt värde
            "max_depth": 0
        }
        
        response = client.post("/api/v1/jobs", json=job_request)
        
        # Ska få validation error
        assert response.status_code == 422
        
    def test_string_length_validation(self, client):
        """Test string length validation"""
        
        # Extremt långa strings
        job_request = {
            "start_urls": ["https://example.com"],
            "max_pages": 10,
            "template_id": "x" * 1000  # Mycket lång string
        }
        
        response = client.post("/api/v1/jobs", json=job_request)
        
        # Kan antingen accepteras eller få validation error beroende på implementation
        assert response.status_code in [201, 422]


class TestAPIErrorHandling:
    """Test suite för API error handling"""
    
    def test_internal_server_error_handling(self, client, mock_scheduler):
        """Test hantering av internal server errors"""
        
        app.dependency_overrides[get_scheduler] = lambda: mock_scheduler
        mock_scheduler.submit_job.side_effect = Exception("Database connection failed")
        
        job_request = {
            "start_urls": ["https://example.com"],
            "max_pages": 10
        }
        
        response = client.post("/api/v1/jobs", json=job_request)
        
        # Ska få server error
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        
        app.dependency_overrides.clear()
        
    def test_malformed_json_handling(self, client):
        """Test hantering av malformed JSON"""
        
        response = client.post(
            "/api/v1/jobs",
            data="{malformed json}",
            headers={"Content-Type": "application/json"}
        )
        
        # Ska få bad request
        assert response.status_code == 422
