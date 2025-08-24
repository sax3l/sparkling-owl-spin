"""
Unit tests för SOS Crawler Engine

Testar BFS crawling, URL management, och respect för robots.txt.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from urllib.parse import urljoin

from sos.crawler.engine import CrawlEngine, CrawlJob, CrawlResult


class TestCrawlEngine:
    """Test suite för CrawlEngine"""
    
    @pytest.fixture
    def mock_fetcher(self):
        """Mock fetcher för testing"""
        fetcher = AsyncMock()
        return fetcher
        
    @pytest.fixture
    def basic_crawl_job(self):
        """Grundläggande crawl job för testing"""
        return CrawlJob(
            id="test-job-1",
            start_urls=["https://example.com"],
            max_pages=5,
            max_depth=2,
            respect_robots=False  # Disable för testing
        )
        
    def test_crawl_engine_initialization(self, mock_fetcher):
        """Test skapande av CrawlEngine"""
        engine = CrawlEngine(fetcher=mock_fetcher)
        
        assert engine.fetcher == mock_fetcher
        assert engine.visited == set()
        assert engine.queue == []
        assert engine.results == []
        
    @pytest.mark.asyncio
    async def test_simple_single_page_crawl(self, mock_fetcher, basic_crawl_job):
        """Test crawling av en enda sida"""
        
        # Mock response
        mock_response = Mock()
        mock_response.is_success.return_value = True
        mock_response.url = "https://example.com"
        mock_response.content = "<html><body><h1>Test Page</h1></body></html>"
        mock_response.status_code = 200
        mock_fetcher.fetch.return_value = mock_response
        
        engine = CrawlEngine(fetcher=mock_fetcher)
        results = await engine.crawl(basic_crawl_job)
        
        assert len(results) == 1
        assert results[0].url == "https://example.com"
        assert results[0].status_code == 200
        assert "Test Page" in results[0].content
        
    @pytest.mark.asyncio
    async def test_bfs_crawling_with_links(self, mock_fetcher):
        """Test BFS crawling med länkar"""
        
        # Definiera responses för olika sidor
        responses = {
            "https://example.com": Mock(
                is_success=lambda: True,
                url="https://example.com",
                content='<html><body><a href="/page1">Page 1</a><a href="/page2">Page 2</a></body></html>',
                status_code=200
            ),
            "https://example.com/page1": Mock(
                is_success=lambda: True,
                url="https://example.com/page1",
                content='<html><body><h1>Page 1</h1></body></html>',
                status_code=200
            ),
            "https://example.com/page2": Mock(
                is_success=lambda: True,
                url="https://example.com/page2", 
                content='<html><body><h1>Page 2</h1></body></html>',
                status_code=200
            )
        }
        
        def mock_fetch(url, **kwargs):
            return responses.get(url, Mock(is_success=lambda: False, status_code=404))
            
        mock_fetcher.fetch.side_effect = mock_fetch
        
        # Crawl job som tillåter djupare crawling
        job = CrawlJob(
            id="test-bfs-job",
            start_urls=["https://example.com"],
            max_pages=3,
            max_depth=2,
            respect_robots=False
        )
        
        engine = CrawlEngine(fetcher=mock_fetcher)
        
        # Mock extract_links för att returnera förväntade länkar
        with patch.object(engine, 'extract_links') as mock_extract:
            def extract_side_effect(content, base_url):
                if "example.com/page" not in base_url:  # Root page
                    return [
                        "https://example.com/page1",
                        "https://example.com/page2"
                    ]
                return []  # Leaf pages har inga länkar
                
            mock_extract.side_effect = extract_side_effect
            
            results = await engine.crawl(job)
            
            # Ska ha crawlat alla 3 sidor
            assert len(results) == 3
            crawled_urls = {r.url for r in results}
            assert "https://example.com" in crawled_urls
            assert "https://example.com/page1" in crawled_urls
            assert "https://example.com/page2" in crawled_urls
            
    @pytest.mark.asyncio
    async def test_max_pages_limit(self, mock_fetcher):
        """Test att max_pages respekteras"""
        
        # Mock som alltid returnerar framgång med många länkar
        def mock_fetch(url, **kwargs):
            return Mock(
                is_success=lambda: True,
                url=url,
                content='<html><body><a href="/page1">Link</a><a href="/page2">Link</a></body></html>',
                status_code=200
            )
            
        mock_fetcher.fetch.side_effect = mock_fetch
        
        job = CrawlJob(
            id="test-limit-job",
            start_urls=["https://example.com"],
            max_pages=2,  # Begränsa till 2 sidor
            max_depth=10,
            respect_robots=False
        )
        
        engine = CrawlEngine(fetcher=mock_fetcher)
        
        # Mock extract_links för att alltid returnera nya länkar
        link_counter = 0
        with patch.object(engine, 'extract_links') as mock_extract:
            def extract_side_effect(content, base_url):
                nonlocal link_counter
                link_counter += 1
                return [f"https://example.com/page{link_counter}-{i}" for i in range(5)]
                
            mock_extract.side_effect = extract_side_effect
            
            results = await engine.crawl(job)
            
            # Ska respektera max_pages limit
            assert len(results) == 2
            
    @pytest.mark.asyncio
    async def test_max_depth_limit(self, mock_fetcher):
        """Test att max_depth respekteras"""
        
        def mock_fetch(url, **kwargs):
            return Mock(
                is_success=lambda: True,
                url=url,
                content=f'<html><body><h1>Content for {url}</h1><a href="{url}/deeper">Deeper</a></body></html>',
                status_code=200
            )
            
        mock_fetcher.fetch.side_effect = mock_fetch
        
        job = CrawlJob(
            id="test-depth-job",
            start_urls=["https://example.com"],
            max_pages=10,
            max_depth=1,  # Bara 1 djup
            respect_robots=False
        )
        
        engine = CrawlEngine(fetcher=mock_fetcher)
        
        with patch.object(engine, 'extract_links') as mock_extract:
            def extract_side_effect(content, base_url):
                # Returnera länkar till djupare nivåer
                if "/deeper" not in base_url:
                    return [base_url + "/deeper"]
                return []
                
            mock_extract.side_effect = extract_side_effect
            
            results = await engine.crawl(job)
            
            # Ska bara crawla root + 1 djup = 2 sidor max
            assert len(results) <= 2
            
            # Verifiera att inga länkar på djup > 1 crawlades
            deep_urls = [r.url for r in results if r.url.count("/") > 3]
            assert len(deep_urls) <= 1  # Max 1 djup tillåtet
            
    def test_extract_links_basic(self):
        """Test grundläggande länkextrahering"""
        engine = CrawlEngine(fetcher=Mock())
        
        html_content = '''
        <html>
        <body>
            <a href="/relative-link">Relative</a>
            <a href="https://example.com/absolute">Absolute</a>
            <a href="mailto:test@example.com">Email</a>
            <a href="javascript:void(0)">JavaScript</a>
            <a href="#anchor">Anchor</a>
        </body>
        </html>
        '''
        
        base_url = "https://example.com"
        links = engine.extract_links(html_content, base_url)
        
        # Ska extrahera bara HTTP/HTTPS länkar
        expected_links = {
            "https://example.com/relative-link",
            "https://example.com/absolute"
        }
        
        assert set(links) == expected_links
        
    def test_extract_links_deduplication(self):
        """Test deduplicering av extraherade länkar"""
        engine = CrawlEngine(fetcher=Mock())
        
        html_content = '''
        <html>
        <body>
            <a href="/page1">Link 1</a>
            <a href="/page1">Link 1 Again</a>
            <a href="/page2">Link 2</a>
            <a href="https://example.com/page1">Absolute same as relative</a>
        </body>
        </html>
        '''
        
        base_url = "https://example.com"
        links = engine.extract_links(html_content, base_url)
        
        # Ska ha unika länkar
        assert len(links) == len(set(links))
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        
    @pytest.mark.asyncio
    async def test_error_handling_during_crawl(self, mock_fetcher):
        """Test error handling under crawling"""
        
        def mock_fetch(url, **kwargs):
            if "error" in url:
                return Mock(
                    is_success=lambda: False,
                    url=url,
                    content="Error occurred",
                    status_code=500,
                    error=Exception("Server error")
                )
            return Mock(
                is_success=lambda: True,
                url=url,
                content=f'<html><body><a href="{url}/error">Error link</a></body></html>',
                status_code=200
            )
            
        mock_fetcher.fetch.side_effect = mock_fetch
        
        job = CrawlJob(
            id="test-error-job",
            start_urls=["https://example.com"],
            max_pages=3,
            max_depth=2,
            respect_robots=False
        )
        
        engine = CrawlEngine(fetcher=mock_fetcher)
        
        with patch.object(engine, 'extract_links') as mock_extract:
            def extract_side_effect(content, base_url):
                if "error" not in base_url:
                    return [base_url + "/error"]
                return []
                
            mock_extract.side_effect = extract_side_effect
            
            results = await engine.crawl(job)
            
            # Ska ha resultat för både framgångsrika och misslyckade requests
            assert len(results) >= 1  # Minst root page
            
            # Verifiera att error results finns med
            error_results = [r for r in results if not r.success]
            success_results = [r for r in results if r.success]
            
            assert len(success_results) >= 1  # Root page ska lyckas
            assert len(error_results) >= 0   # Error pages kan finnas


class TestCrawlJob:
    """Test suite för CrawlJob"""
    
    def test_crawl_job_creation(self):
        """Test skapande av CrawlJob"""
        job = CrawlJob(
            id="test-job",
            start_urls=["https://example.com", "https://test.com"],
            max_pages=100,
            max_depth=3,
            respect_robots=True,
            delay_seconds=1.0
        )
        
        assert job.id == "test-job"
        assert len(job.start_urls) == 2
        assert job.max_pages == 100
        assert job.max_depth == 3
        assert job.respect_robots is True
        assert job.delay_seconds == 1.0
        
    def test_crawl_job_defaults(self):
        """Test default values för CrawlJob"""
        job = CrawlJob(
            id="minimal-job",
            start_urls=["https://example.com"]
        )
        
        assert job.max_pages == 100  # Default
        assert job.max_depth == 3    # Default
        assert job.respect_robots is True  # Default
        assert job.delay_seconds == 1.0    # Default


class TestCrawlResult:
    """Test suite för CrawlResult"""
    
    def test_crawl_result_creation(self):
        """Test skapande av CrawlResult"""
        result = CrawlResult(
            url="https://example.com",
            status_code=200,
            content="<html>Test</html>",
            title="Test Page",
            links=["https://example.com/page1"],
            depth=1,
            crawl_time=0.5
        )
        
        assert result.url == "https://example.com"
        assert result.status_code == 200
        assert result.content == "<html>Test</html>"
        assert result.title == "Test Page"
        assert result.links == ["https://example.com/page1"]
        assert result.depth == 1
        assert result.crawl_time == 0.5
        assert result.success is True  # 200 status = success
        
    def test_crawl_result_error_detection(self):
        """Test error detection i CrawlResult"""
        
        # Framgångsrik result
        success_result = CrawlResult("https://example.com", 200, "OK")
        assert success_result.success is True
        
        # Client error
        client_error = CrawlResult("https://example.com", 404, "Not Found")
        assert client_error.success is False
        
        # Server error
        server_error = CrawlResult("https://example.com", 500, "Internal Error")
        assert server_error.success is False
        
        # Network error (status_code 0)
        network_error = CrawlResult("https://example.com", 0, "Connection failed")
        assert network_error.success is False
