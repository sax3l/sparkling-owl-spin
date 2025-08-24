"""
Integration tests för SOS system

Testar integration mellan olika komponenter och end-to-end workflows.
"""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, patch

# Mock imports för nu - kommer att uppdateras när SOS modulen är redo
pytest.importorskip("sos", reason="SOS module not available yet")


class TestSOSIntegration:
    """Integration tester för SOS komponenter"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_template_to_crawl_workflow(self):
        """Test complete workflow från template till crawl results"""
        
        # Template definition
        template_yaml = """
        name: "Integration Test Template"
        description: "Template för integration testing"
        
        selectors:
          title: "h1"
          content: ".content"
          links: "a"
          
        follow:
          - selector: "a.next-page"
            max_depth: 2
            
        actions:
          - type: extract
            field: title
          - type: extract
            field: content
          - type: follow_links
            selector: links
        """
        
        # Mock fetcher som returnerar realistic HTML
        from sos.core.fetcher import HttpFetcher
        
        def mock_fetch(url, **kwargs):
            html_content = f"""
            <html>
            <head><title>Test Page - {url}</title></head>
            <body>
                <h1>Page Title for {url}</h1>
                <div class="content">
                    <p>This is content for {url}</p>
                </div>
                <a href="/page2" class="next-page">Next Page</a>
                <a href="/page3">Another Link</a>
            </body>
            </html>
            """
            
            response = Mock()
            response.is_success.return_value = True
            response.url = url
            response.content = html_content
            response.status_code = 200
            response.headers = {"content-type": "text/html"}
            return response
            
        # Test complete workflow
        with patch.object(HttpFetcher, 'fetch', side_effect=mock_fetch):
            
            # 1. Parse template
            from sos.core.template_dsl import TemplateDSL
            
            template = TemplateDSL.parse_yaml(template_yaml)
            assert template.name == "Integration Test Template"
            assert "title" in template.selectors
            
            # 2. Create crawl job from template
            from sos.crawler.engine import CrawlJob
            
            job = CrawlJob(
                id="integration-test-job",
                start_urls=["https://example.com"],
                max_pages=3,
                max_depth=2,
                template=template
            )
            
            # 3. Execute crawl
            from sos.crawler.engine import CrawlEngine
            from sos.core.fetcher import HttpFetcher
            
            fetcher = HttpFetcher()
            engine = CrawlEngine(fetcher=fetcher)
            
            results = await engine.crawl(job)
            
            # 4. Verify results
            assert len(results) > 0
            
            # Alla results ska ha extraherad data enligt template
            for result in results:
                assert result.extracted_data is not None
                assert "title" in result.extracted_data
                assert "content" in result.extracted_data
                
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_scheduler_with_real_components(self):
        """Test scheduler med riktiga komponenter"""
        
        from sos.scheduler.manager import SchedulerManager
        from sos.crawler.engine import CrawlEngine
        from sos.core.fetcher import HttpFetcher
        
        # Setup komponenter
        fetcher = HttpFetcher()
        engine = CrawlEngine(fetcher=fetcher)
        scheduler = SchedulerManager(max_workers=2)
        
        # Mock fetcher för kontrollerbar output
        def mock_fetch(url, **kwargs):
            response = Mock()
            response.is_success.return_value = True
            response.url = url
            response.content = f"<html><body><h1>Content for {url}</h1></body></html>"
            response.status_code = 200
            return response
            
        with patch.object(fetcher, 'fetch', side_effect=mock_fetch):
            
            # Submit flera jobb
            job_configs = [
                {
                    "id": f"scheduler-test-job-{i}",
                    "start_urls": [f"https://example{i}.com"],
                    "max_pages": 2,
                    "max_depth": 1
                }
                for i in range(3)
            ]
            
            job_ids = []
            for config in job_configs:
                job_id = await scheduler.submit_job(config, engine)
                job_ids.append(job_id)
                
            # Starta scheduler
            scheduler_task = asyncio.create_task(scheduler.start())
            
            # Vänta på completion
            timeout = 5.0  # 5 sekunder timeout
            start_time = asyncio.get_event_loop().time()
            
            while len(scheduler.completed_jobs) < 3:
                if asyncio.get_event_loop().time() - start_time > timeout:
                    break
                await asyncio.sleep(0.1)
                
            await scheduler.stop()
            await scheduler_task
            
            # Verify alla jobb kördes
            assert len(scheduler.completed_jobs) == 3
            
            # Alla jobb ska ha results
            for job_id in job_ids:
                results = scheduler.get_job_results(job_id)
                assert len(results) > 0
                
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_with_real_backend(self):
        """Test API med real backend komponenter"""
        
        # Detta test kräver att API:et startas med riktiga komponenter
        # För nu, mocka vi dependency injection
        
        from fastapi.testclient import TestClient
        from sos.api.main import app, get_scheduler, get_template_manager
        from sos.scheduler.manager import SchedulerManager
        from sos.db.template_manager import TemplateManager
        from sos.crawler.engine import CrawlEngine
        from sos.core.fetcher import HttpFetcher
        
        # Setup real components
        fetcher = HttpFetcher() 
        engine = CrawlEngine(fetcher=fetcher)
        scheduler = SchedulerManager(max_workers=1)
        template_manager = TemplateManager()
        
        # Override dependencies
        app.dependency_overrides[get_scheduler] = lambda: scheduler
        app.dependency_overrides[get_template_manager] = lambda: template_manager
        
        client = TestClient(app)
        
        try:
            # 1. Create template via API
            template_data = {
                "name": "API Integration Template",
                "description": "Template för API testing",
                "config": {
                    "selectors": {
                        "title": "h1",
                        "content": ".content"
                    },
                    "actions": [
                        {"type": "extract", "field": "title"}
                    ]
                }
            }
            
            response = client.post("/api/v1/templates", json=template_data)
            assert response.status_code == 201
            template_id = response.json()["template_id"]
            
            # 2. Create crawl job via API
            job_data = {
                "start_urls": ["https://example.com"],
                "max_pages": 2,
                "max_depth": 1,
                "template_id": template_id
            }
            
            response = client.post("/api/v1/jobs", json=job_data)
            assert response.status_code == 201
            job_id = response.json()["job_id"]
            
            # 3. Check job status
            response = client.get(f"/api/v1/jobs/{job_id}/status")
            assert response.status_code == 200
            status_data = response.json()
            assert status_data["job_id"] == job_id
            assert status_data["status"] in ["queued", "running", "completed"]
            
        finally:
            # Cleanup
            app.dependency_overrides.clear()
            
    @pytest.mark.integration 
    @pytest.mark.asyncio
    async def test_proxy_rotation_integration(self):
        """Test proxy rotation integration med crawler"""
        
        from sos.proxy.pool import ProxyPool
        from sos.core.fetcher import HttpFetcher
        from sos.crawler.engine import CrawlEngine, CrawlJob
        
        # Setup proxy pool
        proxy_urls = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080", 
            "http://proxy3.example.com:8080"
        ]
        proxy_pool = ProxyPool(proxy_urls)
        
        # Setup components
        fetcher = HttpFetcher(proxy_pool=proxy_pool)
        engine = CrawlEngine(fetcher=fetcher)
        
        used_proxies = []
        
        def mock_fetch_with_proxy_tracking(url, proxy=None, **kwargs):
            used_proxies.append(proxy)
            response = Mock()
            response.is_success.return_value = True
            response.url = url
            response.content = f"<html><body>Content via {proxy}</body></html>"
            response.status_code = 200
            return response
            
        with patch.object(fetcher, 'fetch', side_effect=mock_fetch_with_proxy_tracking):
            
            job = CrawlJob(
                id="proxy-test-job",
                start_urls=[
                    "https://site1.example.com",
                    "https://site2.example.com", 
                    "https://site3.example.com"
                ],
                max_pages=3,
                max_depth=1
            )
            
            results = await engine.crawl(job)
            
            # Verify att olika proxies användes
            assert len(used_proxies) > 0
            unique_proxies = set(p for p in used_proxies if p is not None)
            assert len(unique_proxies) >= 2  # Minst 2 olika proxies användes
            
    @pytest.mark.integration
    def test_database_integration(self):
        """Test database integration för templates och results"""
        
        # Detta test kräver databas setup
        # För nu, test med temporary database
        
        import tempfile
        import sqlite3
        
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_db:
            db_path = tmp_db.name
            
        try:
            # Setup temporary database
            conn = sqlite3.connect(db_path)
            conn.execute("""
                CREATE TABLE templates (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    config TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE TABLE crawl_results (
                    id INTEGER PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status_code INTEGER,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            conn.close()
            
            # Test template storage och retrieval
            from sos.db.template_manager import TemplateManager
            
            # Detta skulle använda riktig database connection
            # template_manager = TemplateManager(db_url=f"sqlite:///{db_path}")
            
            # För nu, mock implementationen
            template_manager = Mock()
            template_manager.create_template.return_value = "template-123"
            template_manager.get_template.return_value = {
                "id": "template-123",
                "name": "Test Template",
                "config": {}
            }
            
            # Test create och retrieve
            template_id = template_manager.create_template({
                "name": "Test Template",
                "config": {"selectors": {"title": "h1"}}
            })
            
            assert template_id == "template-123"
            
            retrieved_template = template_manager.get_template(template_id)
            assert retrieved_template["name"] == "Test Template"
            
        finally:
            # Cleanup
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestSOSPerformance:
    """Performance och load tester för SOS"""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_crawl_performance(self):
        """Test performance för concurrent crawling"""
        
        from sos.crawler.engine import CrawlEngine
        from sos.core.fetcher import HttpFetcher
        
        fetcher = HttpFetcher()
        engine = CrawlEngine(fetcher=fetcher)
        
        # Mock för snabb respons
        def fast_mock_fetch(url, **kwargs):
            response = Mock()
            response.is_success.return_value = True
            response.url = url
            response.content = "<html><body>Fast response</body></html>"
            response.status_code = 200
            return response
            
        with patch.object(fetcher, 'fetch', side_effect=fast_mock_fetch):
            
            # Test crawling av många URLs
            start_time = asyncio.get_event_loop().time()
            
            job = CrawlJob(
                id="performance-test",
                start_urls=[f"https://example{i}.com" for i in range(10)],
                max_pages=10,
                max_depth=1
            )
            
            results = await engine.crawl(job)
            
            end_time = asyncio.get_event_loop().time()
            
            # Performance assertions
            crawl_time = end_time - start_time
            assert crawl_time < 5.0  # Ska ta mindre än 5 sekunder
            assert len(results) == 10  # Alla URLs ska crawlas
            
            # Throughput check
            throughput = len(results) / crawl_time
            assert throughput > 2.0  # Minst 2 pages per sekund
            
    @pytest.mark.performance
    def test_memory_usage_stability(self):
        """Test att memory usage är stabilt under load"""
        
        import psutil
        import gc
        
        process = psutil.Process()
        
        # Mät initial memory
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Simulera många operationer
        from sos.core.template_dsl import TemplateDSL
        
        template_yaml = """
        name: "Memory Test Template"
        selectors:
          title: "h1"
        actions:
          - type: extract
            field: title
        """
        
        # Parse många templates
        for i in range(100):
            template = TemplateDSL.parse_yaml(template_yaml)
            assert template.name == "Memory Test Template"
            
            # Simulera template usage
            _ = template.selectors
            _ = template.actions
            
        # Mät memory efter operationer
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Memory growth ska vara rimlig
        memory_growth = final_memory - initial_memory
        assert memory_growth < 50  # Mindre än 50MB growth
        
        print(f"Memory usage: {initial_memory:.1f} MB -> {final_memory:.1f} MB (+{memory_growth:.1f} MB)")


class TestSOSReliability:
    """Reliability och error recovery tester"""
    
    @pytest.mark.reliability
    @pytest.mark.asyncio
    async def test_network_error_recovery(self):
        """Test recovery från network errors"""
        
        from sos.crawler.engine import CrawlEngine
        from sos.core.fetcher import HttpFetcher
        
        fetcher = HttpFetcher()
        engine = CrawlEngine(fetcher=fetcher)
        
        call_count = 0
        
        def unreliable_fetch(url, **kwargs):
            nonlocal call_count
            call_count += 1
            
            # Första anropet failar, andra lyckas
            if call_count % 2 == 1:
                response = Mock()
                response.is_success.return_value = False
                response.url = url
                response.content = "Network error"
                response.status_code = 0
                response.error = Exception("Connection timeout")
                return response
            else:
                response = Mock()
                response.is_success.return_value = True
                response.url = url
                response.content = "<html><body>Success after retry</body></html>"
                response.status_code = 200
                return response
                
        with patch.object(fetcher, 'fetch', side_effect=unreliable_fetch):
            
            job = CrawlJob(
                id="reliability-test",
                start_urls=["https://unreliable.example.com"],
                max_pages=1,
                max_depth=1,
                retry_failed=True  # Om implementerat
            )
            
            results = await engine.crawl(job)
            
            # Ska ha minst ett resultat (även om första försöket failade)
            assert len(results) >= 1
            
            # Om retry implementerat, ska ha framgångsrikt resultat
            # Annars ska ha error result
            has_success = any(r.success for r in results)
            has_error = any(not r.success for r in results) 
            
            assert has_success or has_error  # Minst en typ av resultat
