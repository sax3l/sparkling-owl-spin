"""
HTTP-based scraper implementation using httpx.

Fast, async HTTP scraper for simple HTML content extraction.
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .base_scraper import BaseScraper, ScrapingResult, ScrapingConfig

logger = logging.getLogger(__name__)

class HttpScraper(BaseScraper):
    """HTTP-based scraper using httpx for fast async requests."""
    
    def __init__(self, config: Optional[ScrapingConfig] = None):
        super().__init__(config)
        self._client: Optional[httpx.AsyncClient] = None
        
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create httpx client."""
        if self._client is None:
            timeout = httpx.Timeout(
                connect=10.0,
                read=self.config.timeout_seconds,
                write=10.0,
                pool=10.0
            )
            
            limits = httpx.Limits(
                max_connections=50,
                max_keepalive_connections=20
            )
            
            self._client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                verify=self.config.verify_ssl,
                follow_redirects=self.config.follow_redirects,
                max_redirects=self.config.max_redirects
            )
            
        return self._client
    
    async def scrape_url(self, url: str, **kwargs) -> ScrapingResult:
        """Scrape a single URL using HTTP requests."""
        if not self.validate_url(url):
            return ScrapingResult(
                url=url,
                data={},
                success=False,
                error_message="Invalid URL format"
            )
        
        start_time = time.time()
        
        try:
            await self._apply_delay()
            
            # Prepare headers
            headers = self._prepare_headers(kwargs.get('headers'))
            
            # Get client and make request
            client = await self._get_client()
            
            # Configure proxy if specified
            proxies = None
            if self.config.proxy:
                proxies = {"http://": self.config.proxy, "https://": self.config.proxy}
            
            response = await client.get(
                url,
                headers=headers,
                cookies=self.config.cookies,
                proxies=proxies,
                params=kwargs.get('params')
            )
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Check response status
            if response.status_code != 200:
                return ScrapingResult(
                    url=url,
                    data={},
                    success=False,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    error_message=self._handle_response_error(response, url)
                )
            
            # Extract data from response
            data = await self.extract_data(response.text, url, **kwargs)
            
            return ScrapingResult(
                url=url,
                data=data,
                success=True,
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                metadata={
                    "content_length": len(response.text),
                    "content_type": response.headers.get("content-type"),
                    "encoding": response.encoding,
                    "final_url": str(response.url)
                }
            )
            
        except httpx.TimeoutException:
            return ScrapingResult(
                url=url,
                data={},
                success=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                error_message="Request timeout"
            )
        except httpx.RequestError as e:
            return ScrapingResult(
                url=url,
                data={},
                success=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"Request error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return ScrapingResult(
                url=url,
                data={},
                success=False,
                response_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"Unexpected error: {str(e)}"
            )
    
    async def extract_data(self, content: str, url: str, **kwargs) -> Dict[str, Any]:
        """Extract structured data from HTML content using BeautifulSoup."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Get selectors from kwargs or use defaults
            selectors = kwargs.get('selectors', {})
            if not selectors:
                # Default extraction strategy
                return self._extract_default_data(soup, url)
            
            # Extract data using provided selectors
            extracted_data = {}
            for field_name, selector in selectors.items():
                try:
                    elements = soup.select(selector)
                    if elements:
                        if len(elements) == 1:
                            extracted_data[field_name] = self._clean_text(elements[0].get_text())
                        else:
                            extracted_data[field_name] = [
                                self._clean_text(elem.get_text()) for elem in elements
                            ]
                    else:
                        extracted_data[field_name] = None
                except Exception as e:
                    logger.warning(f"Error extracting {field_name} with selector {selector}: {e}")
                    extracted_data[field_name] = None
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error parsing HTML content from {url}: {e}")
            return {"error": f"HTML parsing failed: {str(e)}"}
    
    def _extract_default_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract default data when no selectors provided."""
        data = {
            "title": None,
            "description": None,
            "headings": [],
            "links": [],
            "images": [],
            "text_content": None
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            data["title"] = self._clean_text(title_tag.get_text())
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data["description"] = meta_desc.get('content', '').strip()
        
        # Extract headings
        for level in ['h1', 'h2', 'h3']:
            headings = soup.find_all(level)
            data["headings"].extend([
                {"level": level, "text": self._clean_text(h.get_text())}
                for h in headings
            ])
        
        # Extract links
        links = soup.find_all('a', href=True)
        for link in links[:20]:  # Limit to first 20 links
            href = link['href']
            full_url = urljoin(url, href)
            link_text = self._clean_text(link.get_text())
            if link_text and href:
                data["links"].append({
                    "url": full_url,
                    "text": link_text,
                    "relative_url": href
                })
        
        # Extract images
        images = soup.find_all('img', src=True)
        for img in images[:10]:  # Limit to first 10 images
            src = img['src']
            full_url = urljoin(url, src)
            alt_text = img.get('alt', '').strip()
            data["images"].append({
                "url": full_url,
                "alt": alt_text,
                "relative_url": src
            })
        
        # Extract main text content
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text_content = soup.get_text()
        data["text_content"] = self._clean_text(text_content)[:1000]  # Limit length
        
        return data
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = ' '.join(text.split())
        return cleaned.strip()
    
    async def scrape_with_pagination(self, base_url: str, max_pages: int = 10, **kwargs) -> List[ScrapingResult]:
        """Scrape multiple pages with pagination support."""
        results = []
        current_page = 1
        
        while current_page <= max_pages:
            # Construct URL for current page
            if 'page_param' in kwargs:
                page_param = kwargs['page_param']
                url = f"{base_url}?{page_param}={current_page}"
            else:
                url = f"{base_url}?page={current_page}"
            
            self.logger.info(f"Scraping page {current_page}: {url}")
            
            result = await self.scrape_url(url, **kwargs)
            results.append(result)
            
            if not result.success:
                self.logger.warning(f"Failed to scrape page {current_page}, stopping pagination")
                break
            
            # Check if we should continue (look for next page indicators)
            if not self._has_next_page(result.data):
                self.logger.info(f"No more pages found after page {current_page}")
                break
            
            current_page += 1
        
        return results
    
    def _has_next_page(self, data: Dict[str, Any]) -> bool:
        """Check if there's a next page based on scraped data."""
        # Look for common pagination indicators
        links = data.get('links', [])
        for link in links:
            link_text = link.get('text', '').lower()
            if any(indicator in link_text for indicator in ['next', 'nästa', '>']):
                return True
        
        return False
    
    async def cleanup(self):
        """Clean up HTTP client resources."""
        if self._client:
            await self._client.aclose()
            self._client = None
        await super().cleanup()

__all__ = ["HttpScraper"]