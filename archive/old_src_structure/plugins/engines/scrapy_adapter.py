#!/usr/bin/env python3
"""
Scrapy Engine Adapter för Sparkling-Owl-Spin
Integration av Scrapy crawling engine
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import tempfile
import os

logger = logging.getLogger(__name__)

@dataclass
class ScrapySpider:
    """Scrapy spider definition"""
    name: str
    start_urls: List[str]
    allowed_domains: List[str]
    custom_settings: Dict[str, Any]
    spider_class: str = "CrawlSpider"
    
@dataclass
class ScrapingJob:
    """Scrapy scraping job"""
    job_id: str
    spider_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    items_scraped: int = 0
    errors: List[str] = None
    
@dataclass
class ScrapedItem:
    """Scraped item från Scrapy"""
    url: str
    title: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    spider_name: str

class ScrapyEngineAdapter:
    """Scrapy Engine integration för web crawling"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.spiders = {}
        self.active_jobs = {}
        self.settings = {}
        self.initialized = False
        self.item_callbacks = []
        
    async def initialize(self):
        """Initiera Scrapy Engine"""
        try:
            logger.info("🕷️ Initializing Scrapy Engine Adapter")
            
            # Try to import Scrapy
            try:
                # import scrapy  # Uncomment when available
                # from scrapy.crawler import CrawlerProcess, CrawlerRunner
                # from scrapy.settings import Settings
                logger.info("✅ Scrapy dependencies available (mock)")
            except ImportError:
                logger.warning("⚠️ Scrapy not installed - using mock implementation")
                
            await self._setup_default_settings()
            await self._setup_default_spiders()
            
            self.initialized = True
            logger.info("✅ Scrapy Engine Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Scrapy Engine: {str(e)}")
            raise
            
    async def _setup_default_settings(self):
        """Setup default Scrapy settings"""
        self.settings = {
            # Basic settings
            'BOT_NAME': 'sparkling-owl-spin',
            'ROBOTSTXT_OBEY': True,
            'USER_AGENT': 'sparkling-owl-spin (+http://www.yourdomain.com)',
            
            # Download settings
            'DOWNLOAD_DELAY': 1,
            'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
            'CONCURRENT_REQUESTS': 16,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
            
            # AutoThrottle
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 1,
            'AUTOTHROTTLE_MAX_DELAY': 60,
            'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
            'AUTOTHROTTLE_DEBUG': False,
            
            # Caching
            'HTTPCACHE_ENABLED': True,
            'HTTPCACHE_EXPIRATION_SECS': 3600,
            'HTTPCACHE_DIR': 'httpcache',
            
            # Pipeline settings
            'ITEM_PIPELINES': {
                'scrapy.pipelines.files.FilesPipeline': 300,
                'scrapy.pipelines.images.ImagesPipeline': 300,
            },
            
            # Extensions
            'EXTENSIONS': {
                'scrapy.extensions.telnet.TelnetConsole': None,
            },
            
            # Logging
            'LOG_LEVEL': 'INFO',
            'LOG_ENABLED': True,
            
            # Request settings
            'RETRY_ENABLED': True,
            'RETRY_TIMES': 2,
            'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429]
        }
        
        logger.info("⚙️ Setup default Scrapy settings")
        
    async def _setup_default_spiders(self):
        """Setup default spiders"""
        
        # Generic web spider
        generic_spider = ScrapySpider(
            name="generic_spider",
            start_urls=[],
            allowed_domains=[],
            custom_settings={
                'DOWNLOAD_DELAY': 2,
                'CONCURRENT_REQUESTS': 8
            },
            spider_class="CrawlSpider"
        )
        self.spiders["generic_spider"] = generic_spider
        
        # E-commerce spider
        ecommerce_spider = ScrapySpider(
            name="ecommerce_spider",
            start_urls=[],
            allowed_domains=[],
            custom_settings={
                'DOWNLOAD_DELAY': 3,
                'CONCURRENT_REQUESTS': 4,
                'ROBOTSTXT_OBEY': True,
                'USER_AGENT': 'Mozilla/5.0 (compatible; E-commerce crawler)'
            },
            spider_class="CrawlSpider"
        )
        self.spiders["ecommerce_spider"] = ecommerce_spider
        
        # News spider
        news_spider = ScrapySpider(
            name="news_spider", 
            start_urls=[],
            allowed_domains=[],
            custom_settings={
                'DOWNLOAD_DELAY': 1,
                'CONCURRENT_REQUESTS': 12,
                'AUTOTHROTTLE_TARGET_CONCURRENCY': 2.0
            },
            spider_class="CrawlSpider"
        )
        self.spiders["news_spider"] = news_spider
        
        # Social media spider (more careful)
        social_spider = ScrapySpider(
            name="social_spider",
            start_urls=[],
            allowed_domains=[],
            custom_settings={
                'DOWNLOAD_DELAY': 5,
                'CONCURRENT_REQUESTS': 2,
                'RANDOMIZE_DOWNLOAD_DELAY': 1.0,
                'COOKIES_ENABLED': True,
                'SESSION_PERSISTENCE': True
            },
            spider_class="CrawlSpider"
        )
        self.spiders["social_spider"] = social_spider
        
        logger.info(f"🕷️ Setup {len(self.spiders)} default spiders")
        
    async def create_spider(self, spider_config: Dict[str, Any]) -> str:
        """Create new spider från config"""
        spider_name = spider_config.get("name", f"spider_{len(self.spiders)}")
        
        spider = ScrapySpider(
            name=spider_name,
            start_urls=spider_config.get("start_urls", []),
            allowed_domains=spider_config.get("allowed_domains", []),
            custom_settings=spider_config.get("custom_settings", {}),
            spider_class=spider_config.get("spider_class", "CrawlSpider")
        )
        
        self.spiders[spider_name] = spider
        logger.info(f"🕷️ Created spider: {spider_name}")
        
        return spider_name
        
    async def start_crawl(self, spider_name: str, start_urls: List[str] = None, 
                         custom_settings: Dict[str, Any] = None) -> str:
        """Starta crawling job"""
        if spider_name not in self.spiders:
            raise ValueError(f"Unknown spider: {spider_name}")
            
        job_id = f"job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_jobs)}"
        spider = self.spiders[spider_name]
        
        # Override URLs if provided
        if start_urls:
            spider.start_urls = start_urls
            
        # Override settings if provided
        if custom_settings:
            spider.custom_settings.update(custom_settings)
            
        job = ScrapingJob(
            job_id=job_id,
            spider_name=spider_name,
            status="running",
            start_time=datetime.now(),
            errors=[]
        )
        
        self.active_jobs[job_id] = job
        
        # Start crawling (mock implementation)
        asyncio.create_task(self._run_spider_mock(job_id))
        
        logger.info(f"🚀 Started crawl job {job_id} with spider {spider_name}")
        return job_id
        
    async def _run_spider_mock(self, job_id: str):
        """Mock spider execution"""
        job = self.active_jobs[job_id]
        spider = self.spiders[job.spider_name]
        
        try:
            # Simulate crawling
            total_items = len(spider.start_urls) * 5  # Mock: 5 items per URL
            
            for i in range(total_items):
                await asyncio.sleep(0.1)  # Simulate crawling delay
                
                # Create mock item
                item = ScrapedItem(
                    url=f"https://example.com/page_{i}",
                    title=f"Mock Title {i}",
                    content=f"Mock content for item {i}",
                    metadata={
                        "item_index": i,
                        "spider": job.spider_name,
                        "job_id": job_id
                    },
                    timestamp=datetime.now(),
                    spider_name=job.spider_name
                )
                
                # Call item callbacks
                for callback in self.item_callbacks:
                    try:
                        await callback(item)
                    except Exception as e:
                        job.errors.append(f"Callback error: {str(e)}")
                        
                job.items_scraped += 1
                
                # Check if job was cancelled
                if job.status == "cancelled":
                    break
                    
            # Complete job
            job.status = "completed"
            job.end_time = datetime.now()
            
        except Exception as e:
            job.status = "failed"
            job.end_time = datetime.now()
            job.errors.append(f"Spider error: {str(e)}")
            logger.error(f"❌ Spider {job.spider_name} failed: {str(e)}")
            
        logger.info(f"✅ Crawl job {job_id} completed with {job.items_scraped} items")
        
    async def stop_crawl(self, job_id: str):
        """Stoppa crawling job"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        job.status = "cancelled"
        job.end_time = datetime.now()
        
        logger.info(f"🛑 Stopped crawl job {job_id}")
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Hämta job status"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "spider_name": job.spider_name,
            "status": job.status,
            "items_scraped": job.items_scraped,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "errors": job.errors,
            "duration": (job.end_time - job.start_time).total_seconds() if job.end_time else None
        }
        
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Hämta all job status"""
        return [self.get_job_status(job_id) for job_id in self.active_jobs.keys()]
        
    def get_spider_info(self, spider_name: str) -> Dict[str, Any]:
        """Hämta spider information"""
        if spider_name not in self.spiders:
            raise ValueError(f"Unknown spider: {spider_name}")
            
        spider = self.spiders[spider_name]
        
        return {
            "name": spider.name,
            "spider_class": spider.spider_class,
            "start_urls": spider.start_urls,
            "allowed_domains": spider.allowed_domains,
            "custom_settings": spider.custom_settings
        }
        
    def get_all_spiders(self) -> List[Dict[str, Any]]:
        """Hämta alla spiders"""
        return [self.get_spider_info(name) for name in self.spiders.keys()]
        
    def add_item_callback(self, callback: Callable):
        """Add callback för scraped items"""
        self.item_callbacks.append(callback)
        logger.info(f"➕ Added item callback: {callback.__name__}")
        
    def remove_item_callback(self, callback: Callable):
        """Remove item callback"""
        if callback in self.item_callbacks:
            self.item_callbacks.remove(callback)
            logger.info(f"➖ Removed item callback: {callback.__name__}")
            
    async def export_items(self, job_id: str, format: str = "json") -> str:
        """Export scraped items"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        
        # Mock export
        export_data = {
            "job_info": self.get_job_status(job_id),
            "spider_info": self.get_spider_info(job.spider_name),
            "items": [
                {
                    "url": f"https://example.com/page_{i}",
                    "title": f"Mock Title {i}",
                    "content": f"Mock content for item {i}",
                    "timestamp": datetime.now().isoformat()
                }
                for i in range(job.items_scraped)
            ]
        }
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False) as f:
            if format.lower() == "json":
                json.dump(export_data, f, indent=2, default=str)
            elif format.lower() == "csv":
                # Mock CSV export
                f.write("url,title,content,timestamp\n")
                for item in export_data["items"]:
                    f.write(f'"{item["url"]}","{item["title"]}","{item["content"]}","{item["timestamp"]}"\n')
            else:
                json.dump(export_data, f, indent=2, default=str)
                
            export_file = f.name
            
        logger.info(f"📄 Exported {job.items_scraped} items to {export_file}")
        return export_file
        
    def get_scrapy_settings(self) -> Dict[str, Any]:
        """Hämta current Scrapy settings"""
        return self.settings.copy()
        
    def update_settings(self, new_settings: Dict[str, Any]):
        """Update Scrapy settings"""
        self.settings.update(new_settings)
        logger.info(f"⚙️ Updated {len(new_settings)} Scrapy settings")
        
    async def cleanup(self):
        """Cleanup Scrapy Engine"""
        logger.info("🧹 Cleaning up Scrapy Engine")
        
        # Cancel active jobs
        for job_id in list(self.active_jobs.keys()):
            try:
                await self.stop_crawl(job_id)
            except Exception as e:
                logger.error(f"Error stopping job {job_id}: {str(e)}")
                
        self.active_jobs.clear()
        self.spiders.clear()
        self.item_callbacks.clear()
        self.settings.clear()
        self.initialized = False
        
        logger.info("✅ Scrapy Engine cleanup completed")
