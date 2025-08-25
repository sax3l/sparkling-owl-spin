#!/usr/bin/env python3
"""
Engines Scraping Web Scraper - Consolidated web scraping functionality

This file consolidates multiple scraping classes:
- Originally from scrapers/website_scraper.py + scrapers/data_extractor.py  
- Unified scraping interface for all web scraping operations
- Support for multiple scraping backends (requests, selenium, playwright)
- Data extraction and transformation capabilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import re

from shared.models.base import BaseService, ServiceStatus
from shared.utils.helpers import get_logger, sanitize_url, validate_url


class ScrapingBackend(Enum):
    """Available scraping backends"""
    REQUESTS = "requests"
    SELENIUM = "selenium"  
    PLAYWRIGHT = "playwright"
    SCRAPY = "scrapy"


class ExtractionRule(Enum):
    """Data extraction rule types"""
    CSS_SELECTOR = "css"
    XPATH = "xpath"
    REGEX = "regex"
    JSON_PATH = "jsonpath"
    AI_EXTRACTION = "ai"


@dataclass
class ScrapingTask:
    """Scraping task configuration"""
    url: str
    backend: ScrapingBackend = ScrapingBackend.REQUESTS
    extraction_rules: Dict[str, Any] = None
    headers: Dict[str, str] = None
    cookies: Dict[str, str] = None
    timeout: int = 30
    retries: int = 3
    delay: float = 1.0
    javascript: bool = False
    stealth: bool = False
    proxy: Optional[str] = None


@dataclass 
class ScrapingResult:
    """Scraping operation result"""
    success: bool
    url: str
    status_code: Optional[int] = None
    content: Optional[str] = None
    extracted_data: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.extracted_data is None:
            self.extracted_data = {}
        if self.metadata is None:
            self.metadata = {}


class WebScraper(BaseService):
    """Unified web scraper with multiple backend support"""
    
    def __init__(self, default_backend: ScrapingBackend = ScrapingBackend.REQUESTS):
        super().__init__("web_scraper", "Web Scraping Engine")
        
        self.default_backend = default_backend
        self.logger = get_logger(__name__)
        self.session_cache = {}
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'backends_used': {}
        }
    
    async def start(self) -> None:
        """Start the web scraper service"""
        self.status = ServiceStatus.STARTING
        self.logger.info("Starting Web Scraper service...")
        
        try:
            # Initialize backends
            await self._initialize_backends()
            
            self.status = ServiceStatus.RUNNING
            self.logger.info("✅ Web Scraper service started")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to start Web Scraper: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the web scraper service"""
        self.status = ServiceStatus.STOPPING
        self.logger.info("Stopping Web Scraper service...")
        
        try:
            # Cleanup sessions and resources
            await self._cleanup_backends()
            
            self.status = ServiceStatus.STOPPED
            self.logger.info("✅ Web Scraper service stopped")
            
        except Exception as e:
            self.status = ServiceStatus.ERROR
            self.logger.error(f"❌ Failed to stop Web Scraper: {e}")
    
    async def _initialize_backends(self) -> None:
        """Initialize scraping backends"""
        
        # Initialize requests session
        try:
            import requests
            self.session_cache['requests'] = requests.Session()
            self.logger.info("✅ Requests backend initialized")
        except ImportError:
            self.logger.warning("⚠️ Requests library not available")
        
        # Initialize other backends as needed
        self.logger.info("Backend initialization completed")
    
    async def _cleanup_backends(self) -> None:
        """Cleanup scraping backends"""
        
        for backend_name, session in self.session_cache.items():
            try:
                if hasattr(session, 'close'):
                    session.close()
                self.logger.info(f"✅ Cleaned up {backend_name} backend")
            except Exception as e:
                self.logger.error(f"Error cleaning up {backend_name}: {e}")
        
        self.session_cache.clear()
    
    async def scrape(self, task: ScrapingTask) -> ScrapingResult:
        """Main scraping method"""
        
        if not validate_url(task.url):
            return ScrapingResult(
                success=False,
                url=task.url,
                error="Invalid URL format"
            )
        
        self.stats['total_requests'] += 1
        backend_name = task.backend.value
        self.stats['backends_used'][backend_name] = self.stats['backends_used'].get(backend_name, 0) + 1
        
        try:
            # Route to appropriate backend
            if task.backend == ScrapingBackend.REQUESTS:
                result = await self._scrape_with_requests(task)
            elif task.backend == ScrapingBackend.SELENIUM:
                result = await self._scrape_with_selenium(task)
            elif task.backend == ScrapingBackend.PLAYWRIGHT:
                result = await self._scrape_with_playwright(task)
            else:
                result = ScrapingResult(
                    success=False,
                    url=task.url,
                    error=f"Backend {task.backend.value} not implemented"
                )
            
            # Extract data if rules provided
            if result.success and task.extraction_rules:
                result.extracted_data = await self._extract_data(result.content, task.extraction_rules)
            
            if result.success:
                self.stats['successful_requests'] += 1
            else:
                self.stats['failed_requests'] += 1
            
            return result
            
        except Exception as e:
            self.stats['failed_requests'] += 1
            self.logger.error(f"Scraping error for {task.url}: {e}")
            
            return ScrapingResult(
                success=False,
                url=task.url,
                error=str(e)
            )
    
    async def _scrape_with_requests(self, task: ScrapingTask) -> ScrapingResult:
        """Scrape using requests library"""
        
        try:
            session = self.session_cache.get('requests')
            if not session:
                import requests
                session = requests.Session()
                self.session_cache['requests'] = session
            
            # Set headers
            headers = task.headers or {}
            headers.setdefault('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Make request
            response = session.get(
                task.url,
                headers=headers,
                cookies=task.cookies,
                timeout=task.timeout,
                proxies={'http': task.proxy, 'https': task.proxy} if task.proxy else None
            )
            
            return ScrapingResult(
                success=True,
                url=task.url,
                status_code=response.status_code,
                content=response.text,
                metadata={
                    'response_time': response.elapsed.total_seconds(),
                    'content_length': len(response.content),
                    'content_type': response.headers.get('content-type', ''),
                    'backend': 'requests'
                }
            )
            
        except Exception as e:
            return ScrapingResult(
                success=False,
                url=task.url,
                error=str(e)
            )
    
    async def _scrape_with_selenium(self, task: ScrapingTask) -> ScrapingResult:
        """Scrape using Selenium (placeholder - would need actual implementation)"""
        
        # This would be implemented with actual Selenium code
        return ScrapingResult(
            success=False,
            url=task.url,
            error="Selenium backend not fully implemented"
        )
    
    async def _scrape_with_playwright(self, task: ScrapingTask) -> ScrapingResult:
        """Scrape using Playwright (placeholder - would need actual implementation)"""
        
        # This would be implemented with actual Playwright code
        return ScrapingResult(
            success=False,
            url=task.url,
            error="Playwright backend not fully implemented"
        )
    
    async def _extract_data(self, content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from content using specified rules"""
        
        extracted = {}
        
        for field_name, rule_config in rules.items():
            try:
                if isinstance(rule_config, str):
                    # Simple CSS selector
                    rule_type = ExtractionRule.CSS_SELECTOR
                    rule_value = rule_config
                else:
                    rule_type = ExtractionRule(rule_config.get('type', 'css'))
                    rule_value = rule_config.get('value', '')
                
                if rule_type == ExtractionRule.CSS_SELECTOR:
                    extracted[field_name] = self._extract_with_css(content, rule_value)
                elif rule_type == ExtractionRule.XPATH:
                    extracted[field_name] = self._extract_with_xpath(content, rule_value)
                elif rule_type == ExtractionRule.REGEX:
                    extracted[field_name] = self._extract_with_regex(content, rule_value)
                elif rule_type == ExtractionRule.JSON_PATH:
                    extracted[field_name] = self._extract_with_jsonpath(content, rule_value)
                else:
                    extracted[field_name] = None
                    self.logger.warning(f"Unknown extraction rule type: {rule_type}")
                    
            except Exception as e:
                self.logger.error(f"Failed to extract {field_name}: {e}")
                extracted[field_name] = None
        
        return extracted
    
    def _extract_with_css(self, content: str, selector: str) -> Optional[str]:
        """Extract data using CSS selector"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            element = soup.select_one(selector)
            return element.get_text(strip=True) if element else None
        except ImportError:
            self.logger.warning("BeautifulSoup not available for CSS extraction")
            return None
        except Exception as e:
            self.logger.error(f"CSS extraction error: {e}")
            return None
    
    def _extract_with_xpath(self, content: str, xpath: str) -> Optional[str]:
        """Extract data using XPath"""
        try:
            from lxml import html
            tree = html.fromstring(content)
            elements = tree.xpath(xpath)
            return elements[0] if elements else None
        except ImportError:
            self.logger.warning("lxml not available for XPath extraction")
            return None
        except Exception as e:
            self.logger.error(f"XPath extraction error: {e}")
            return None
    
    def _extract_with_regex(self, content: str, pattern: str) -> Optional[str]:
        """Extract data using regex"""
        try:
            match = re.search(pattern, content)
            return match.group(1) if match and match.groups() else match.group(0) if match else None
        except Exception as e:
            self.logger.error(f"Regex extraction error: {e}")
            return None
    
    def _extract_with_jsonpath(self, content: str, path: str) -> Any:
        """Extract data using JSONPath"""
        try:
            import jsonpath_ng
            data = json.loads(content)
            jsonpath_expr = jsonpath_ng.parse(path)
            matches = jsonpath_expr.find(data)
            return matches[0].value if matches else None
        except ImportError:
            self.logger.warning("jsonpath-ng not available for JSONPath extraction")
            return None
        except Exception as e:
            self.logger.error(f"JSONPath extraction error: {e}")
            return None
    
    async def scrape_multiple(self, tasks: List[ScrapingTask]) -> List[ScrapingResult]:
        """Scrape multiple URLs concurrently"""
        
        results = []
        semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
        async def scrape_with_semaphore(task):
            async with semaphore:
                return await self.scrape(task)
        
        # Execute tasks concurrently
        tasks_coroutines = [scrape_with_semaphore(task) for task in tasks]
        results = await asyncio.gather(*tasks_coroutines, return_exceptions=True)
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = ScrapingResult(
                    success=False,
                    url=tasks[i].url,
                    error=str(result)
                )
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scraping statistics"""
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': (self.stats['successful_requests'] / self.stats['total_requests'] * 100) 
                           if self.stats['total_requests'] > 0 else 0,
            'backends_used': self.stats['backends_used'],
            'service_status': self.status.value
        }
    
    async def health_check(self):
        """Service health check"""
        from shared.models.base import ServiceHealthCheck
        
        # Simple health check - test scraping a reliable URL
        test_task = ScrapingTask(
            url="https://httpbin.org/get",
            timeout=10
        )
        
        try:
            result = await self.scrape(test_task)
            
            if result.success:
                status = "healthy"
                message = "Web scraper is operational"
            else:
                status = "degraded"
                message = f"Health check failed: {result.error}"
                
        except Exception as e:
            status = "unhealthy"
            message = f"Health check error: {str(e)}"
        
        return ServiceHealthCheck(
            service_id=self.service_id,
            status=status,
            message=message,
            timestamp=datetime.now(),
            details=self.get_statistics()
        )


# Convenience functions for backwards compatibility
async def scrape_url(url: str, backend: ScrapingBackend = ScrapingBackend.REQUESTS) -> ScrapingResult:
    """Convenience function to scrape a single URL"""
    scraper = WebScraper()
    await scraper.start()
    
    task = ScrapingTask(url=url, backend=backend)
    result = await scraper.scrape(task)
    
    await scraper.stop()
    return result


def extract_data_from_html(html_content: str, rules: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to extract data from HTML content"""
    scraper = WebScraper()
    return asyncio.run(scraper._extract_data(html_content, rules))
