"""
Unit tests för SOS Fetcher

Testar HTTP och Playwright fetching med error handling och proxy support.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch

from sos.core.fetcher import HttpFetcher, PlaywrightFetcher, FetchResponse


class TestHttpFetcher:
    """Test suite för HttpFetcher"""
    
    @pytest.mark.asyncio
    async def test_basic_get_request(self):
        """Test grundläggande GET request"""
        fetcher = HttpFetcher()
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body>Test</body></html>"
            mock_response.headers = {"content-type": "text/html"}
            mock_get.return_value = mock_response
            
            response = await fetcher.fetch("https://example.com")
            
            assert response.status_code == 200
            assert response.content == "<html><body>Test</body></html>"
            assert response.headers == {"content-type": "text/html"}
            assert response.url == "https://example.com"
            
    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test hantering av HTTP errors"""
        fetcher = HttpFetcher()
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = Exception("Connection timeout")
            
            response = await fetcher.fetch("https://example.com")
            
            assert response.status_code == 0
            assert "Connection timeout" in response.content
            assert response.error is not None
            
    @pytest.mark.asyncio
    async def test_custom_headers(self):
        """Test custom headers"""
        fetcher = HttpFetcher()
        custom_headers = {
            "User-Agent": "Custom Bot 1.0",
            "Accept": "application/json"
        }
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '{"status": "ok"}'
            mock_response.headers = {}
            mock_get.return_value = mock_response
            
            response = await fetcher.fetch("https://api.example.com", headers=custom_headers)
            
            # Verifiera att custom headers användes
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["headers"]["User-Agent"] == "Custom Bot 1.0"
            assert call_args[1]["headers"]["Accept"] == "application/json"
            
    @pytest.mark.asyncio
    async def test_proxy_support(self):
        """Test proxy support"""
        fetcher = HttpFetcher()
        proxy = "http://proxy.example.com:8080"
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "Success through proxy"
            mock_response.headers = {}
            mock_get.return_value = mock_response
            
            response = await fetcher.fetch("https://example.com", proxy=proxy)
            
            # Verifiera att proxy användes
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["proxies"] == proxy


class TestPlaywrightFetcher:
    """Test suite för PlaywrightFetcher"""
    
    @pytest.mark.asyncio
    async def test_basic_page_fetch(self):
        """Test grundläggande page fetching med Playwright"""
        fetcher = PlaywrightFetcher()
        
        # Mock Playwright components
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>Dynamic content</body></html>")
        mock_page.url = "https://example.com"
        
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()
        
        with patch('playwright.async_api.async_playwright') as mock_playwright:
            mock_p = AsyncMock()
            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock()
            
            response = await fetcher.fetch("https://example.com")
            
            assert response.status_code == 200
            assert response.content == "<html><body>Dynamic content</body></html>"
            assert response.url == "https://example.com"
            
    @pytest.mark.asyncio
    async def test_playwright_with_javascript_wait(self):
        """Test Playwright med JavaScript execution wait"""
        fetcher = PlaywrightFetcher(wait_for_js=True, js_wait_timeout=2000)
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html><body>JS loaded content</body></html>")
        mock_page.url = "https://spa.example.com"
        
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()
        
        with patch('playwright.async_api.async_playwright') as mock_playwright:
            mock_p = AsyncMock()
            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock()
            
            response = await fetcher.fetch("https://spa.example.com")
            
            # Verifiera att wait_for_load_state anropades
            mock_page.wait_for_load_state.assert_called_once_with("networkidle", timeout=2000)
            
    @pytest.mark.asyncio
    async def test_playwright_error_handling(self):
        """Test error handling i Playwright"""
        fetcher = PlaywrightFetcher()
        
        with patch('playwright.async_api.async_playwright') as mock_playwright:
            mock_playwright.side_effect = Exception("Browser launch failed")
            
            response = await fetcher.fetch("https://example.com")
            
            assert response.status_code == 0
            assert "Browser launch failed" in response.content
            assert response.error is not None
            
    @pytest.mark.asyncio
    async def test_playwright_stealth_mode(self):
        """Test Playwright stealth mode"""
        fetcher = PlaywrightFetcher(stealth_mode=True)
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock()
        mock_page.content = AsyncMock(return_value="<html>Stealth content</html>")
        mock_page.url = "https://protected.example.com"
        mock_page.add_init_script = AsyncMock()
        
        mock_context = AsyncMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock()
        
        mock_browser = AsyncMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()
        
        with patch('playwright.async_api.async_playwright') as mock_playwright:
            mock_p = AsyncMock()
            mock_p.chromium.launch = AsyncMock(return_value=mock_browser)
            mock_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_p)
            mock_playwright.return_value.__aexit__ = AsyncMock()
            
            response = await fetcher.fetch("https://protected.example.com")
            
            # Verifiera att stealth script lades till
            mock_page.add_init_script.assert_called()


class TestFetchResponse:
    """Test suite för FetchResponse"""
    
    def test_fetch_response_creation(self):
        """Test skapande av FetchResponse"""
        response = FetchResponse(
            url="https://example.com",
            status_code=200,
            content="<html>Test</html>",
            headers={"content-type": "text/html"}
        )
        
        assert response.url == "https://example.com"
        assert response.status_code == 200
        assert response.content == "<html>Test</html>"
        assert response.headers["content-type"] == "text/html"
        assert response.error is None
        
    def test_fetch_response_with_error(self):
        """Test FetchResponse med error"""
        error = Exception("Network error")
        response = FetchResponse(
            url="https://example.com",
            status_code=0,
            content="",
            error=error
        )
        
        assert response.error == error
        assert response.status_code == 0
        assert not response.is_success()
        
    def test_is_success_method(self):
        """Test is_success method"""
        # Framgångsrik respons
        success_response = FetchResponse("https://example.com", 200, "OK")
        assert success_response.is_success()
        
        # Client error
        client_error = FetchResponse("https://example.com", 404, "Not Found")
        assert not client_error.is_success()
        
        # Server error
        server_error = FetchResponse("https://example.com", 500, "Internal Error")
        assert not server_error.is_success()
        
        # Network error
        network_error = FetchResponse("https://example.com", 0, "", error=Exception())
        assert not network_error.is_success()


class TestFetcherIntegration:
    """Integration tester för fetchers"""
    
    @pytest.mark.asyncio
    async def test_fetcher_factory(self):
        """Test factory pattern för fetcher creation"""
        
        def create_fetcher(fetcher_type: str, **kwargs):
            if fetcher_type == "http":
                return HttpFetcher(**kwargs)
            elif fetcher_type == "playwright":
                return PlaywrightFetcher(**kwargs)
            else:
                raise ValueError(f"Unknown fetcher type: {fetcher_type}")
        
        # HTTP fetcher
        http_fetcher = create_fetcher("http")
        assert isinstance(http_fetcher, HttpFetcher)
        
        # Playwright fetcher
        playwright_fetcher = create_fetcher("playwright", stealth_mode=True)
        assert isinstance(playwright_fetcher, PlaywrightFetcher)
        assert playwright_fetcher.stealth_mode is True
        
        # Unknown type
        with pytest.raises(ValueError):
            create_fetcher("unknown")
            
    @pytest.mark.asyncio
    async def test_response_comparison(self):
        """Test jämförelse mellan HTTP och Playwright responses"""
        
        # Samma content från båda fetchers
        test_content = "<html><body>Same content</body></html>"
        
        http_response = FetchResponse("https://example.com", 200, test_content)
        playwright_response = FetchResponse("https://example.com", 200, test_content)
        
        assert http_response.content == playwright_response.content
        assert http_response.status_code == playwright_response.status_code
        assert http_response.url == playwright_response.url
