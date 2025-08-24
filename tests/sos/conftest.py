"""
SOS Test Suite - Sparkling Owl Spin Testing Framework

Komplett testsvit för den nya SOS-modulen med:
- Unit tests för alla komponenter
- Integration tests för API/DB/Crawler
- E2E tests för full workflow
- Performance/Load tests
- Security tests
"""

import pytest
import asyncio
from pathlib import Path

# SOS fixtures
@pytest.fixture
def sos_test_data_dir():
    """Testdata för SOS-modulen"""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def sample_template_yaml():
    """Exempel YAML template för tester"""
    return """
name: "Test Template"
start_urls:
  - "http://localhost:8000/test-page"
  
follow:
  - selector: "a.next-page"
    type: "pagination"
  - selector: ".item-link"
    type: "detail"
    
extract:
  - name: "title" 
    selector: "h1"
    type: "text"
  - name: "price"
    selector: ".price"
    type: "text"
    regex: "([0-9,]+)"
    
render:
  enabled: false
  
actions:
  scroll: false
  wait_ms: 1000
  
limits:
  max_pages: 10
  max_depth: 2
  
respect_robots: true
delay_ms: 1500
"""

@pytest.fixture
async def sos_test_db():
    """Test database för SOS med mock data"""
    from sos.db.session import engine
    from sos.db.models import Base
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def mock_proxy_pool():
    """Mock proxy pool för tester"""
    from sos.proxy.pool import ProxyPool
    
    class MockProxyPool(ProxyPool):
        def __init__(self):
            super().__init__(["http://proxy1:8080", "http://proxy2:8080"])
            
        def next(self):
            return "http://test-proxy:8080"
            
        def mark_bad(self, proxy, ban_seconds=120):
            pass
    
    return MockProxyPool()

@pytest.fixture
async def sos_api_client():
    """Test client för SOS API"""
    from fastapi.testclient import TestClient
    from sos.api.main import app
    
    return TestClient(app)
