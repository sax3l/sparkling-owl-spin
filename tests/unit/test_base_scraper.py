"""
Tests for base scraper functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.scraper.base_scraper import BaseScraper


class TestBaseScraper:
    """Test cases for BaseScraper class."""
    
    def test_base_scraper_initialization(self):
        """Test that BaseScraper initializes correctly."""
        scraper = BaseScraper()
        assert scraper is not None
    
    def test_scrape_method_not_implemented(self):
        """Test that scrape method raises NotImplementedError."""
        scraper = BaseScraper()
        with pytest.raises(NotImplementedError):
            scraper.scrape("https://example.com")
    
    def test_validate_url(self):
        """Test URL validation functionality."""
        scraper = BaseScraper()
        
        # Valid URLs
        assert scraper.validate_url("https://example.com") is True
        assert scraper.validate_url("http://test.org") is True
        assert scraper.validate_url("https://subdomain.example.com/path") is True
        
        # Invalid URLs
        assert scraper.validate_url("not-a-url") is False
        assert scraper.validate_url("") is False
        assert scraper.validate_url(None) is False
    
    def test_set_headers(self):
        """Test setting custom headers."""
        scraper = BaseScraper()
        
        custom_headers = {
            "User-Agent": "Custom Bot 1.0",
            "Accept": "text/html,application/xhtml+xml"
        }
        
        scraper.set_headers(custom_headers)
        assert scraper.headers == custom_headers
    
    def test_set_proxies(self):
        """Test setting proxy configuration."""
        scraper = BaseScraper()
        
        proxy_config = {
            "http": "http://proxy.example.com:8080",
            "https": "https://proxy.example.com:8080"
        }
        
        scraper.set_proxies(proxy_config)
        assert scraper.proxies == proxy_config
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        scraper = BaseScraper(rate_limit=2.0)  # 2 seconds between requests
        assert scraper.rate_limit == 2.0
    
    def test_timeout_configuration(self):
        """Test timeout configuration."""
        scraper = BaseScraper(timeout=30)
        assert scraper.timeout == 30
    
    def test_retry_configuration(self):
        """Test retry configuration."""
        scraper = BaseScraper(max_retries=5)
        assert scraper.max_retries == 5
    
    def test_user_agent_randomization(self):
        """Test user agent randomization."""
        scraper = BaseScraper(randomize_user_agent=True)
        
        # Should have different user agents on multiple calls
        ua1 = scraper.get_random_user_agent()
        ua2 = scraper.get_random_user_agent()
        
        assert ua1 is not None
        assert ua2 is not None
        # Note: They might be the same due to randomness, but both should be valid
    
    def test_error_handling(self):
        """Test error handling mechanisms."""
        scraper = BaseScraper()
        
        # Test handling of network errors
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            result = scraper.safe_request("https://example.com")
            assert result is None or "error" in result
    
    def test_response_validation(self):
        """Test response validation."""
        scraper = BaseScraper()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body>Test</body></html>"
        mock_response.text = "<html><body>Test</body></html>"
        
        assert scraper.validate_response(mock_response) is True
        
        # Mock failed response
        mock_response.status_code = 404
        assert scraper.validate_response(mock_response) is False
    
    def test_content_type_detection(self):
        """Test content type detection."""
        scraper = BaseScraper()
        
        # Mock response with HTML content
        mock_response = Mock()
        mock_response.headers = {"Content-Type": "text/html; charset=utf-8"}
        
        content_type = scraper.get_content_type(mock_response)
        assert content_type == "text/html"
