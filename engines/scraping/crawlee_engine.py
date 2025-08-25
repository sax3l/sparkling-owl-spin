#!/usr/bin/env python3
"""
Enhanced Crawlee Engine för Sparkling-Owl-Spin
Anpassad från: crawlee
Extraherat från: vendors/crawlee
"""

import logging
import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import time
import random
from pathlib import Path

# Import från core pyramid architecture
from core.base_classes import BaseEngine
from engines.processing.scheduler import EnhancedBFSScheduler

logger = logging.getLogger(__name__)

class CrawleeMode(Enum):
    """Crawlee crawling modes"""
    HEADLESS_BROWSER = "headless_browser"
    HTTP_CLIENT = "http_client"
    HYBRID = "hybrid"

@dataclass
class CrawleeConfig:
    """Crawlee engine configuration"""
    mode: CrawleeMode = CrawleeMode.HTTP_CLIENT
    max_requests_per_minute: int = 60
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    user_agent: Optional[str] = None
    custom_headers: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None
    enable_cookies: bool = True
    enable_sessions: bool = True
    follow_redirects: bool = True
    max_redirect_count: int = 5
    auto_save_data: bool = True
    output_format: str = "json"  # json, csv, jsonl

@dataclass
class CrawlResult:
    """Crawlee crawl result"""
    url: str
    status_code: int
    content: str
    headers: Dict[str, str]
    cookies: Dict[str, str]
    response_time: float
    timestamp: datetime
    metadata: Dict[str, Any]
    error: Optional[str] = None

class EnhancedCrawleeEngine(BaseEngine):
    """Enhanced Crawlee Engine med full funktionalitet"""
    
    def __init__(self, config: CrawleeConfig):
        super().__init__()
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.scheduler = EnhancedBFSScheduler()
        
        # Request queue and processing
        self.request_queue: List[str] = []
        self.processed_urls: set = set()
        self.failed_urls: set = set()
        self.results: List[CrawlResult] = []
        
        # Rate limiting
        self.request_times: List[float] = []
        self.concurrent_requests = 0
        
        # Request handlers
        self.request_handlers: Dict[str, Callable] = {}
        self.error_handlers: Dict[str, Callable] = {}
        
        # Data extraction patterns
        self.extraction_rules: Dict[str, Any] = {}
        
        # Statistics
        self.stats = {
            "requests_made": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "data_items_extracted": 0,
            "avg_response_time": 0.0,
            "total_processing_time": 0.0,
            "start_time": None,
            "end_time": None
        }
        
    async def initialize(self):
        """Initialize Crawlee engine"""
        try:
            logger.info("🕷️ Initializing Enhanced Crawlee Engine")
            
            # Create aiohttp session
            connector = aiohttp.TCPConnector(
                limit=self.config.max_concurrent_requests * 2,
                limit_per_host=self.config.max_concurrent_requests,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30
            )
            
            timeout = aiohttp.ClientTimeout(total=self.config.request_timeout)
            
            headers = {}
            if self.config.user_agent:
                headers["User-Agent"] = self.config.user_agent
            else:
                headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
                
            if self.config.custom_headers:
                headers.update(self.config.custom_headers)
                
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers,
                cookie_jar=aiohttp.CookieJar() if self.config.enable_cookies else None
            )
            
            # Initialize scheduler
            await self.scheduler.initialize()
            
            # Set default request handler
            self.request_handlers["default"] = self._default_request_handler
            self.error_handlers["default"] = self._default_error_handler
            
            self.initialized = True
            self.stats["start_time"] = datetime.now()
            
            logger.info("✅ Enhanced Crawlee Engine initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Crawlee Engine: {str(e)}")
            raise
            
    async def add_requests(self, urls: Union[str, List[str]], 
                         handler_name: str = "default") -> None:
        """Add URLs to crawling queue"""
        
        if isinstance(urls, str):
            urls = [urls]
            
        for url in urls:
            if url not in self.processed_urls and url not in self.failed_urls:
                await self.scheduler.add_url(url, priority=1.0, metadata={"handler": handler_name})
                logger.debug(f"📝 Added URL to queue: {url}")
                
    async def crawl(self, start_urls: Union[str, List[str]], 
                   handler_name: str = "default") -> List[CrawlResult]:
        """Start crawling process"""
        
        if not self.initialized:
            await self.initialize()
            
        logger.info(f"🚀 Starting Crawlee crawl with {len(start_urls) if isinstance(start_urls, list) else 1} URLs")
        
        # Add start URLs
        await self.add_requests(start_urls, handler_name)
        
        # Process queue
        while not await self.scheduler.is_empty():
            # Rate limiting
            await self._enforce_rate_limit()
            
            # Get next URL batch
            batch_size = min(
                self.config.max_concurrent_requests - self.concurrent_requests,
                10  # Max batch size
            )
            
            if batch_size <= 0:
                await asyncio.sleep(0.1)
                continue
                
            tasks = []
            for _ in range(batch_size):
                if await self.scheduler.is_empty():
                    break
                    
                task_data = await self.scheduler.get_next_task()
                if task_data:
                    url = task_data["url"]
                    metadata = task_data["metadata"]
                    handler_name = metadata.get("handler", "default")
                    
                    task = asyncio.create_task(
                        self._process_request(url, handler_name, metadata)
                    )
                    tasks.append(task)
                    self.concurrent_requests += 1
                    
            # Wait for batch completion
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        self.stats["end_time"] = datetime.now()
        self.stats["total_processing_time"] = (
            self.stats["end_time"] - self.stats["start_time"]
        ).total_seconds()
        
        logger.info(f"✅ Crawlee crawl completed: {len(self.results)} results")
        
        # Auto-save if enabled
        if self.config.auto_save_data:
            await self._save_results()
            
        return self.results
        
    async def _process_request(self, url: str, handler_name: str, metadata: Dict[str, Any]) -> None:
        """Process single request"""
        
        start_time = time.time()
        
        try:
            # Get request handler
            handler = self.request_handlers.get(handler_name, self.request_handlers["default"])
            
            # Make request
            result = await handler(url, metadata)
            
            if result:
                # Calculate response time
                result.response_time = time.time() - start_time
                result.timestamp = datetime.now()
                
                self.results.append(result)
                self.processed_urls.add(url)
                self.stats["successful_requests"] += 1
                self.stats["data_items_extracted"] += len(result.metadata.get("extracted_data", []))
                
                # Update average response time
                self.stats["avg_response_time"] = (
                    (self.stats["avg_response_time"] * (self.stats["successful_requests"] - 1) + result.response_time) 
                    / self.stats["successful_requests"]
                )
                
                await self.scheduler.mark_completed(url)
                logger.debug(f"✅ Processed: {url} ({result.response_time:.2f}s)")
            else:
                await self._handle_request_failure(url, "Handler returned None")
                
        except Exception as e:
            await self._handle_request_failure(url, str(e))
            
        finally:
            self.concurrent_requests -= 1
            self.stats["requests_made"] += 1
            
    async def _handle_request_failure(self, url: str, error: str) -> None:
        """Handle request failure"""
        
        logger.warning(f"❌ Request failed: {url} - {error}")
        
        # Try error handler
        error_handler = self.error_handlers.get("default")
        if error_handler:
            try:
                await error_handler(url, error)
            except Exception as e:
                logger.error(f"❌ Error handler failed: {str(e)}")
                
        self.failed_urls.add(url)
        await self.scheduler.mark_failed(url, error)
        self.stats["failed_requests"] += 1
        
    async def _default_request_handler(self, url: str, metadata: Dict[str, Any]) -> Optional[CrawlResult]:
        """Default request handler"""
        
        try:
            async with self.session.get(url) as response:
                content = await response.text()
                
                # Extract data using rules
                extracted_data = await self._extract_data(content, url)
                
                result = CrawlResult(
                    url=url,
                    status_code=response.status,
                    content=content,
                    headers=dict(response.headers),
                    cookies=dict(response.cookies) if response.cookies else {},
                    response_time=0.0,  # Will be set by caller
                    timestamp=datetime.now(),
                    metadata={
                        "extracted_data": extracted_data,
                        "content_length": len(content),
                        "content_type": response.headers.get("Content-Type", "")
                    }
                )
                
                return result
                
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
            
    async def _default_error_handler(self, url: str, error: str) -> None:
        """Default error handler"""
        logger.warning(f"⚠️ Default error handler: {url} - {error}")
        
    async def _extract_data(self, content: str, url: str) -> List[Dict[str, Any]]:
        """Extract data from content using configured rules"""
        
        extracted = []
        
        # Apply extraction rules
        for rule_name, rule_config in self.extraction_rules.items():
            try:
                if rule_config["type"] == "regex":
                    import re
                    pattern = rule_config["pattern"]
                    matches = re.findall(pattern, content)
                    for match in matches:
                        extracted.append({
                            "rule": rule_name,
                            "data": match,
                            "url": url
                        })
                        
                elif rule_config["type"] == "css":
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content, 'html.parser')
                    elements = soup.select(rule_config["selector"])
                    for element in elements:
                        extracted.append({
                            "rule": rule_name,
                            "data": element.get_text().strip(),
                            "url": url
                        })
                        
            except Exception as e:
                logger.warning(f"⚠️ Data extraction failed for rule {rule_name}: {str(e)}")
                
        return extracted
        
    async def _enforce_rate_limit(self) -> None:
        """Enforce rate limiting"""
        
        current_time = time.time()
        
        # Remove old request times (older than 1 minute)
        self.request_times = [
            req_time for req_time in self.request_times 
            if current_time - req_time < 60
        ]
        
        # Check if we're within rate limit
        if len(self.request_times) >= self.config.max_requests_per_minute:
            # Calculate sleep time
            oldest_request = min(self.request_times)
            sleep_time = 60 - (current_time - oldest_request)
            
            if sleep_time > 0:
                logger.debug(f"⏱️ Rate limiting: sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                
        # Record this request time
        self.request_times.append(current_time)
        
    async def _save_results(self) -> None:
        """Save crawl results to file"""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if self.config.output_format == "json":
                filename = f"crawlee_results_{timestamp}.json"
                data = [
                    {
                        "url": result.url,
                        "status_code": result.status_code,
                        "content": result.content,
                        "headers": result.headers,
                        "cookies": result.cookies,
                        "response_time": result.response_time,
                        "timestamp": result.timestamp.isoformat(),
                        "metadata": result.metadata
                    }
                    for result in self.results
                ]
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif self.config.output_format == "jsonl":
                filename = f"crawlee_results_{timestamp}.jsonl"
                with open(filename, 'w', encoding='utf-8') as f:
                    for result in self.results:
                        data = {
                            "url": result.url,
                            "status_code": result.status_code,
                            "content": result.content,
                            "headers": result.headers,
                            "cookies": result.cookies,
                            "response_time": result.response_time,
                            "timestamp": result.timestamp.isoformat(),
                            "metadata": result.metadata
                        }
                        f.write(json.dumps(data, ensure_ascii=False) + "\n")
                        
            elif self.config.output_format == "csv":
                import csv
                filename = f"crawlee_results_{timestamp}.csv"
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "url", "status_code", "response_time", "timestamp",
                        "content_length", "content_type"
                    ])
                    
                    for result in self.results:
                        writer.writerow([
                            result.url,
                            result.status_code,
                            result.response_time,
                            result.timestamp.isoformat(),
                            result.metadata.get("content_length", 0),
                            result.metadata.get("content_type", "")
                        ])
                        
            logger.info(f"💾 Crawlee results saved: {filename}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save results: {str(e)}")
            
    def add_request_handler(self, name: str, handler: Callable) -> None:
        """Add custom request handler"""
        self.request_handlers[name] = handler
        logger.info(f"📝 Added request handler: {name}")
        
    def add_error_handler(self, name: str, handler: Callable) -> None:
        """Add custom error handler"""
        self.error_handlers[name] = handler
        logger.info(f"📝 Added error handler: {name}")
        
    def add_extraction_rule(self, name: str, rule_type: str, pattern_or_selector: str) -> None:
        """Add data extraction rule"""
        self.extraction_rules[name] = {
            "type": rule_type,
            "pattern" if rule_type == "regex" else "selector": pattern_or_selector
        }
        logger.info(f"📝 Added extraction rule: {name} ({rule_type})")
        
    def get_crawl_statistics(self) -> Dict[str, Any]:
        """Get crawling statistics"""
        return {
            "requests_made": self.stats["requests_made"],
            "successful_requests": self.stats["successful_requests"],
            "failed_requests": self.stats["failed_requests"],
            "success_rate": (
                self.stats["successful_requests"] / max(1, self.stats["requests_made"])
            ) * 100,
            "data_items_extracted": self.stats["data_items_extracted"],
            "avg_response_time": self.stats["avg_response_time"],
            "total_processing_time": self.stats["total_processing_time"],
            "urls_processed": len(self.processed_urls),
            "urls_failed": len(self.failed_urls),
            "results_count": len(self.results)
        }
        
    async def cleanup(self):
        """Cleanup Crawlee engine"""
        logger.info("🧹 Cleaning up Enhanced Crawlee Engine")
        
        if self.session:
            await self.session.close()
            
        await self.scheduler.cleanup()
        
        self.results.clear()
        self.processed_urls.clear()
        self.failed_urls.clear()
        self.request_times.clear()
        
        logger.info("✅ Enhanced Crawlee Engine cleanup completed")

# Alias för pyramid architecture compatibility
CrawleeEngine = EnhancedCrawleeEngine
