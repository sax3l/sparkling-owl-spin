import pytest
from fastapi.testclient import TestClient
from src.webapp.app import app

client = TestClient(app)

@pytest.mark.integration
def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}