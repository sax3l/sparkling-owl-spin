#!/usr/bin/env python3
"""
Crawlee Engine Adapter för Sparkling-Owl-Spin  
Integration av Crawlee JavaScript crawling engine
"""

import logging
import asyncio
import subprocess
import json
import tempfile
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass 
class CrawleeCrawler:
    """Crawlee crawler definition"""
    name: str
    start_urls: List[str]
    crawler_type: str  # "playwright", "puppeteer", "cheerio", "jsdom"
    options: Dict[str, Any]
    
@dataclass
class CrawleeJob:
    """Crawlee crawling job"""
    job_id: str
    crawler_name: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    items_crawled: int = 0
    errors: List[str] = None
    process_id: Optional[int] = None
    
@dataclass
class CrawledData:
    """Crawled data från Crawlee"""
    url: str
    title: str
    text_content: str
    html_content: str
    links: List[str]
    images: List[str]
    metadata: Dict[str, Any]
    screenshot: Optional[str] = None
    timestamp: datetime = None

class CrawleeEngineAdapter:
    """Crawlee Engine integration för JavaScript-powered crawling"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.crawlers = {}
        self.active_jobs = {}
        self.initialized = False
        self.node_available = False
        self.crawlee_installed = False
        self.data_callbacks = []
        
    async def initialize(self):
        """Initiera Crawlee Engine"""
        try:
            logger.info("🎭 Initializing Crawlee Engine Adapter")
            
            # Check if Node.js is available
            await self._check_node_availability()
            
            # Check if Crawlee is installed
            await self._check_crawlee_installation()
            
            # Setup default crawlers
            await self._setup_default_crawlers()
            
            self.initialized = True
            logger.info("✅ Crawlee Engine Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Crawlee Engine: {str(e)}")
            raise
            
    async def _check_node_availability(self):
        """Check if Node.js is available"""
        try:
            result = await asyncio.create_subprocess_exec(
                'node', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                node_version = stdout.decode().strip()
                logger.info(f"✅ Node.js available: {node_version}")
                self.node_available = True
            else:
                logger.warning("⚠️ Node.js not found")
                self.node_available = False
                
        except Exception as e:
            logger.warning(f"⚠️ Error checking Node.js: {str(e)}")
            self.node_available = False
            
    async def _check_crawlee_installation(self):
        """Check if Crawlee is installed"""
        if not self.node_available:
            self.crawlee_installed = False
            return
            
        try:
            # Mock check - in real implementation, check npm list crawlee
            logger.info("📦 Crawlee availability check (mock - assuming installed)")
            self.crawlee_installed = True
            
        except Exception as e:
            logger.warning(f"⚠️ Error checking Crawlee installation: {str(e)}")
            self.crawlee_installed = False
            
    async def _setup_default_crawlers(self):
        """Setup default Crawlee crawlers"""
        
        # Playwright crawler (full browser)
        playwright_crawler = CrawleeCrawler(
            name="playwright_crawler",
            start_urls=[],
            crawler_type="playwright",
            options={
                "headless": True,
                "max_requests_per_crawl": 100,
                "request_handler_timeout": 30000,
                "navigation_timeout": 30000,
                "browser_pool_options": {
                    "max_open_pages_per_browser": 5
                },
                "pre_navigation_hooks": [],
                "post_navigation_hooks": []
            }
        )
        self.crawlers["playwright_crawler"] = playwright_crawler
        
        # Puppeteer crawler
        puppeteer_crawler = CrawleeCrawler(
            name="puppeteer_crawler",
            start_urls=[],
            crawler_type="puppeteer",
            options={
                "headless": True,
                "max_requests_per_crawl": 200,
                "request_handler_timeout": 20000,
                "launch_options": {
                    "args": ["--no-sandbox", "--disable-setuid-sandbox"]
                }
            }
        )
        self.crawlers["puppeteer_crawler"] = puppeteer_crawler
        
        # Cheerio crawler (server-side DOM)
        cheerio_crawler = CrawleeCrawler(
            name="cheerio_crawler",
            start_urls=[],
            crawler_type="cheerio",
            options={
                "max_requests_per_crawl": 500,
                "request_handler_timeout": 10000,
                "max_request_retries": 3,
                "request_options": {
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (compatible; Crawlee Cheerio Crawler)"
                    }
                }
            }
        )
        self.crawlers["cheerio_crawler"] = cheerio_crawler
        
        # JSDOM crawler  
        jsdom_crawler = CrawleeCrawler(
            name="jsdom_crawler",
            start_urls=[],
            crawler_type="jsdom",
            options={
                "max_requests_per_crawl": 300,
                "request_handler_timeout": 15000,
                "run_scripts": False,
                "resource_loader": "usable"
            }
        )
        self.crawlers["jsdom_crawler"] = jsdom_crawler
        
        logger.info(f"🎭 Setup {len(self.crawlers)} default Crawlee crawlers")
        
    async def create_crawler(self, crawler_config: Dict[str, Any]) -> str:
        """Create new Crawlee crawler"""
        crawler_name = crawler_config.get("name", f"crawler_{len(self.crawlers)}")
        
        crawler = CrawleeCrawler(
            name=crawler_name,
            start_urls=crawler_config.get("start_urls", []),
            crawler_type=crawler_config.get("crawler_type", "cheerio"),
            options=crawler_config.get("options", {})
        )
        
        self.crawlers[crawler_name] = crawler
        logger.info(f"🎭 Created Crawlee crawler: {crawler_name}")
        
        return crawler_name
        
    async def start_crawl(self, crawler_name: str, start_urls: List[str] = None,
                         options: Dict[str, Any] = None) -> str:
        """Start Crawlee crawling job"""
        if crawler_name not in self.crawlers:
            raise ValueError(f"Unknown crawler: {crawler_name}")
            
        job_id = f"crawlee_job_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_jobs)}"
        crawler = self.crawlers[crawler_name]
        
        # Override URLs if provided
        if start_urls:
            crawler.start_urls = start_urls
            
        # Override options if provided  
        if options:
            crawler.options.update(options)
            
        job = CrawleeJob(
            job_id=job_id,
            crawler_name=crawler_name,
            status="running",
            start_time=datetime.now(),
            errors=[]
        )
        
        self.active_jobs[job_id] = job
        
        # Start crawling
        if self.crawlee_installed and self.node_available:
            await self._run_crawlee_real(job_id)
        else:
            # Use mock implementation
            asyncio.create_task(self._run_crawlee_mock(job_id))
            
        logger.info(f"🚀 Started Crawlee job {job_id} with crawler {crawler_name}")
        return job_id
        
    async def _run_crawlee_real(self, job_id: str):
        """Run real Crawlee crawler"""
        job = self.active_jobs[job_id]
        crawler = self.crawlers[job.crawler_name]
        
        try:
            # Create Crawlee script
            script_content = await self._generate_crawlee_script(crawler)
            
            # Write script to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(script_content)
                script_path = f.name
                
            # Run Crawlee script
            process = await asyncio.create_subprocess_exec(
                'node', script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            job.process_id = process.pid
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                # Parse results
                try:
                    results = json.loads(stdout.decode())
                    await self._process_crawlee_results(job_id, results)
                    job.status = "completed"
                except json.JSONDecodeError as e:
                    job.errors.append(f"Failed to parse results: {str(e)}")
                    job.status = "failed"
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                job.errors.append(f"Crawlee script failed: {error_msg}")
                job.status = "failed"
                
            # Cleanup
            os.unlink(script_path)
            
        except Exception as e:
            job.status = "failed"
            job.errors.append(f"Crawler error: {str(e)}")
            logger.error(f"❌ Crawlee job {job_id} failed: {str(e)}")
            
        finally:
            job.end_time = datetime.now()
            
    async def _run_crawlee_mock(self, job_id: str):
        """Mock Crawlee crawler execution"""
        job = self.active_jobs[job_id]
        crawler = self.crawlers[job.crawler_name]
        
        try:
            # Simulate crawling with different delays based on crawler type
            delay_map = {
                "playwright": 2.0,  # Browser crawlers are slower
                "puppeteer": 1.8,
                "cheerio": 0.5,     # Server-side DOM is faster
                "jsdom": 0.8
            }
            
            delay = delay_map.get(crawler.crawler_type, 1.0)
            total_items = len(crawler.start_urls) * 3  # Mock: 3 items per URL
            
            for i in range(total_items):
                await asyncio.sleep(delay)
                
                # Create mock crawled data
                data = CrawledData(
                    url=f"https://example.com/page_{i}",
                    title=f"Mock Page Title {i}",
                    text_content=f"Mock text content for page {i} crawled with {crawler.crawler_type}",
                    html_content=f"<html><body><h1>Mock Page {i}</h1><p>Content here</p></body></html>",
                    links=[f"https://example.com/link_{i}_{j}" for j in range(3)],
                    images=[f"https://example.com/image_{i}_{j}.jpg" for j in range(2)],
                    metadata={
                        "crawler_type": crawler.crawler_type,
                        "job_id": job_id,
                        "item_index": i,
                        "has_javascript": crawler.crawler_type in ["playwright", "puppeteer"],
                        "load_time": delay * 1000  # Mock load time in ms
                    },
                    screenshot=f"screenshot_{i}.png" if crawler.crawler_type in ["playwright", "puppeteer"] else None,
                    timestamp=datetime.now()
                )
                
                # Call data callbacks
                for callback in self.data_callbacks:
                    try:
                        await callback(data)
                    except Exception as e:
                        job.errors.append(f"Callback error: {str(e)}")
                        
                job.items_crawled += 1
                
                # Check if job was cancelled
                if job.status == "cancelled":
                    break
                    
            job.status = "completed"
            job.end_time = datetime.now()
            
        except Exception as e:
            job.status = "failed"
            job.end_time = datetime.now()
            job.errors.append(f"Mock crawler error: {str(e)}")
            
        logger.info(f"✅ Crawlee job {job_id} completed with {job.items_crawled} items")
        
    async def _generate_crawlee_script(self, crawler: CrawleeCrawler) -> str:
        """Generate Crawlee JavaScript script"""
        crawler_class_map = {
            "playwright": "PlaywrightCrawler",
            "puppeteer": "PuppeteerCrawler", 
            "cheerio": "CheerioCrawler",
            "jsdom": "JsdomCrawler"
        }
        
        crawler_class = crawler_class_map.get(crawler.crawler_type, "CheerioCrawler")
        
        script = f"""
const {{ {crawler_class} }} = require('crawlee');

const crawler = new {crawler_class}({{
    ...{json.dumps(crawler.options, indent=4)},
    requestHandler: async ({{ request, page, $ }}) => {{
        const title = await page.title() || $('title').text() || '';
        const text = await page.textContent('body') || $('body').text() || '';
        const html = await page.content() || $.html() || '';
        
        const links = [];
        const images = [];
        
        if (page) {{
            // For browser crawlers
            const linkElements = await page.$$eval('a[href]', els => els.map(el => el.href));
            const imageElements = await page.$$eval('img[src]', els => els.map(el => el.src));
            links.push(...linkElements);
            images.push(...imageElements);
        }} else if ($) {{
            // For server-side crawlers
            $('a[href]').each((i, el) => links.push($(el).attr('href')));
            $('img[src]').each((i, el) => images.push($(el).attr('src')));
        }}
        
        const result = {{
            url: request.url,
            title,
            text_content: text,
            html_content: html,
            links,
            images,
            metadata: {{
                timestamp: new Date().toISOString(),
                crawler_type: '{crawler.crawler_type}'
            }}
        }};
        
        console.log(JSON.stringify(result));
    }}
}});

(async () => {{
    await crawler.run({json.dumps(crawler.start_urls)});
}})();
"""
        return script
        
    async def _process_crawlee_results(self, job_id: str, results: Dict[str, Any]):
        """Process results från real Crawlee execution"""
        job = self.active_jobs[job_id]
        
        # Process each crawled item
        for item_data in results.get("items", []):
            data = CrawledData(
                url=item_data.get("url", ""),
                title=item_data.get("title", ""),
                text_content=item_data.get("text_content", ""),
                html_content=item_data.get("html_content", ""),
                links=item_data.get("links", []),
                images=item_data.get("images", []),
                metadata=item_data.get("metadata", {}),
                timestamp=datetime.fromisoformat(item_data.get("timestamp", datetime.now().isoformat()))
            )
            
            # Call callbacks
            for callback in self.data_callbacks:
                try:
                    await callback(data)
                except Exception as e:
                    job.errors.append(f"Callback error: {str(e)}")
                    
            job.items_crawled += 1
            
    async def stop_crawl(self, job_id: str):
        """Stop Crawlee crawling job"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        job.status = "cancelled"
        job.end_time = datetime.now()
        
        # Try to kill process if running
        if job.process_id:
            try:
                os.kill(job.process_id, 15)  # SIGTERM
                await asyncio.sleep(5)
                os.kill(job.process_id, 9)   # SIGKILL
            except ProcessLookupError:
                pass  # Process already terminated
            except Exception as e:
                logger.error(f"Error terminating process {job.process_id}: {str(e)}")
                
        logger.info(f"🛑 Stopped Crawlee job {job_id}")
        
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get Crawlee job status"""
        if job_id not in self.active_jobs:
            raise ValueError(f"Unknown job: {job_id}")
            
        job = self.active_jobs[job_id]
        
        return {
            "job_id": job.job_id,
            "crawler_name": job.crawler_name,
            "crawler_type": self.crawlers[job.crawler_name].crawler_type,
            "status": job.status,
            "items_crawled": job.items_crawled,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "errors": job.errors,
            "duration": (job.end_time - job.start_time).total_seconds() if job.end_time else None,
            "process_id": job.process_id
        }
        
    def add_data_callback(self, callback: Callable):
        """Add callback för crawled data"""
        self.data_callbacks.append(callback)
        logger.info(f"➕ Added Crawlee data callback: {callback.__name__}")
        
    def get_available_crawlers(self) -> List[Dict[str, Any]]:
        """Get available Crawlee crawlers"""
        return [
            {
                "name": crawler.name,
                "crawler_type": crawler.crawler_type,
                "start_urls_count": len(crawler.start_urls),
                "options": crawler.options
            }
            for crawler in self.crawlers.values()
        ]
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get Crawlee system information"""
        return {
            "node_available": self.node_available,
            "crawlee_installed": self.crawlee_installed,
            "total_crawlers": len(self.crawlers),
            "active_jobs": len([job for job in self.active_jobs.values() if job.status == "running"]),
            "supported_types": ["playwright", "puppeteer", "cheerio", "jsdom"]
        }
        
    async def cleanup(self):
        """Cleanup Crawlee Engine"""
        logger.info("🧹 Cleaning up Crawlee Engine")
        
        # Stop active jobs
        for job_id in list(self.active_jobs.keys()):
            try:
                await self.stop_crawl(job_id)
            except Exception as e:
                logger.error(f"Error stopping job {job_id}: {str(e)}")
                
        self.active_jobs.clear()
        self.crawlers.clear()
        self.data_callbacks.clear()
        self.initialized = False
        
        logger.info("✅ Crawlee Engine cleanup completed")
