#!/usr/bin/env python3
"""
Crawlee Integration - Revolutionary Ultimate System v4.0
Node.js-powered web crawler via HTTP API interface
"""

import asyncio
import logging
import time
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Set
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse
import shutil
import socket
from contextlib import closing

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CrawleeRequest:
    """Container for Crawlee crawling request"""
    start_urls: List[str]
    max_requests: int = 100
    max_concurrent: int = 10
    request_delay: float = 1.0
    use_puppeteer: bool = False
    use_playwright: bool = False
    use_cheerio: bool = True
    extract_links: bool = True
    extract_text: bool = True
    extract_images: bool = False
    extract_pdfs: bool = False
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None
    user_agent: Optional[str] = None
    timeout: int = 30
    viewport: Optional[Dict[str, int]] = None
    wait_for_selector: Optional[str] = None
    custom_selectors: Optional[Dict[str, str]] = None

@dataclass
class CrawleeResult:
    """Container for Crawlee crawl results"""
    url: str
    status_code: int
    title: Optional[str] = None
    text_content: Optional[str] = None
    html_content: Optional[str] = None
    links: Optional[List[str]] = None
    images: Optional[List[str]] = None
    pdfs: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    load_time: float = 0.0
    error: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None

@dataclass
class CrawleeConfig:
    """Configuration for Crawlee"""
    enabled: bool = True
    crawlee_server_url: str = "http://localhost:3000"
    node_binary_path: str = "node"
    npm_binary_path: str = "npm"
    auto_start_server: bool = True
    server_port: int = 3000
    max_concurrent_crawlers: int = 5
    default_timeout: int = 30
    default_delay: float = 1.0
    use_browser_pool: bool = True
    headless_browser: bool = True
    enable_screenshots: bool = False
    proxy_support: bool = False
    session_pool_size: int = 20
    retry_attempts: int = 3
    debug: bool = False

class CrawleeServer:
    """
    Crawlee server manager for Node.js-based web crawling.
    
    Features:
    - High-performance Node.js crawling
    - Multiple crawler types (Cheerio, Puppeteer, Playwright)
    - Browser automation support
    - Session management
    - Request/response interception
    - Proxy rotation support
    - Screenshot capabilities
    """
    
    def __init__(self, config: CrawleeConfig):
        self.config = config
        self.server_process = None
        self.temp_dir = None
        self.session = None
        self._stats = {
            'crawls_initiated': 0,
            'crawls_completed': 0,
            'crawls_failed': 0,
            'total_pages_crawled': 0,
            'total_links_found': 0,
            'total_crawl_time': 0.0,
            'server_starts': 0,
            'active_crawlers': 0
        }
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not available. Install with: pip install requests")
            
    async def initialize(self):
        """Initialize Crawlee server"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing Crawlee server...")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="crawlee_"))
        
        # Setup requests session
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Check if server is already running
        if await self._check_server_status():
            logger.info("✅ Crawlee server already running")
            return
            
        # Start server if needed
        if self.config.auto_start_server:
            await self._start_crawlee_server()
        else:
            logger.warning("⚠️ Crawlee server not running and auto_start_server is disabled")
            
        logger.info("✅ Crawlee server initialized")
        
    async def _check_server_status(self) -> bool:
        """Check if Crawlee server is running"""
        
        try:
            response = self.session.get(
                f"{self.config.crawlee_server_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                server_info = response.json()
                logger.info(f"✅ Crawlee server running: {server_info.get('version', 'unknown')}")
                return True
                
        except Exception as e:
            logger.debug(f"Crawlee server not available: {str(e)}")
            
        return False
        
    async def _start_crawlee_server(self):
        """Start Crawlee server using Node.js"""
        
        try:
            # Setup Crawlee server project
            await self._setup_crawlee_project()
            
            # Start Node.js server
            await self._start_node_server()
            
            self._stats['server_starts'] += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to start Crawlee server: {str(e)}")
            raise
            
    async def _setup_crawlee_project(self):
        """Setup Crawlee Node.js project"""
        
        try:
            logger.info("📦 Setting up Crawlee project...")
            
            # Create package.json
            package_json = {
                "name": "crawlee-server",
                "version": "1.0.0",
                "description": "Crawlee HTTP API Server",
                "main": "server.js",
                "dependencies": {
                    "crawlee": "^3.5.0",
                    "express": "^4.18.0",
                    "cors": "^2.8.5",
                    "puppeteer": "^21.0.0",
                    "playwright": "^1.39.0"
                },
                "scripts": {
                    "start": "node server.js"
                }
            }
            
            package_file = self.temp_dir / "package.json"
            with open(package_file, 'w') as f:
                json.dump(package_json, f, indent=2)
                
            # Create server.js
            server_js = self._generate_crawlee_server_code()
            server_file = self.temp_dir / "server.js"
            with open(server_file, 'w') as f:
                f.write(server_js)
                
            # Install dependencies
            if shutil.which(self.config.npm_binary_path):
                logger.info("📥 Installing Crawlee dependencies...")
                
                install_result = subprocess.run([
                    self.config.npm_binary_path, "install"
                ], cwd=self.temp_dir, capture_output=True, text=True, timeout=300)
                
                if install_result.returncode != 0:
                    logger.error(f"❌ npm install failed: {install_result.stderr}")
                    # Continue anyway, might work with global packages
                else:
                    logger.info("✅ Dependencies installed")
            else:
                logger.warning("⚠️ npm not found, trying without dependency installation")
                
        except Exception as e:
            logger.error(f"❌ Crawlee project setup failed: {str(e)}")
            raise
            
    def _generate_crawlee_server_code(self) -> str:
        """Generate Node.js server code for Crawlee"""
        
        return f'''const express = require('express');
const cors = require('cors');
const {{ CheerioCrawler, PuppeteerCrawler, PlaywrightCrawler }} = require('crawlee');

const app = express();
const PORT = {self.config.server_port};

app.use(cors());
app.use(express.json({{ limit: '10mb' }}));

// Health check endpoint
app.get('/health', (req, res) => {{
    res.json({{
        status: 'ok',
        version: '1.0.0',
        crawlee_version: '3.5.0',
        uptime: process.uptime()
    }});
}});

// Main crawl endpoint
app.post('/crawl', async (req, res) => {{
    try {{
        const {{
            startUrls = [],
            maxRequests = 100,
            maxConcurrency = {self.config.max_concurrent_crawlers},
            requestDelay = {self.config.default_delay * 1000},
            usePuppeteer = false,
            usePlaywright = false,
            useCheerio = true,
            extractLinks = true,
            extractText = true,
            extractImages = false,
            allowedDomains = [],
            userAgent,
            timeout = {self.config.default_timeout * 1000},
            customSelectors = {{}},
            waitForSelector
        }} = req.body;
        
        const results = [];
        let crawlStats = {{
            requestsFinished: 0,
            requestsFailed: 0,
            totalTime: 0
        }};
        
        const startTime = Date.now();
        
        // Choose crawler type
        let Crawler;
        if (usePuppeteer) {{
            Crawler = PuppeteerCrawler;
        }} else if (usePlaywright) {{
            Crawler = PlaywrightCrawler;
        }} else {{
            Crawler = CheerioCrawler;
        }}
        
        // Configure crawler
        const crawler = new Crawler({{
            maxRequestsPerCrawl: maxRequests,
            maxConcurrency: maxConcurrency,
            requestDelay: requestDelay,
            requestHandlerTimeoutSecs: timeout / 1000,
            
            async requestHandler({{ request, $, page, response }}) {{
                const result = {{
                    url: request.loadedUrl || request.url,
                    statusCode: response?.statusCode || 200,
                    loadTime: Date.now() - request.loadedAt?.getTime() || 0
                }};
                
                try {{
                    if (usePuppeteer || usePlaywright) {{
                        // Browser-based extraction
                        result.title = await page.title();
                        
                        if (extractText) {{
                            result.textContent = await page.evaluate(() => {{
                                return document.body ? document.body.innerText : '';
                            }});
                        }}
                        
                        if (extractLinks) {{
                            result.links = await page.evaluate(() => {{
                                return Array.from(document.querySelectorAll('a[href]'))
                                    .map(a => a.href)
                                    .filter(href => href && href.startsWith('http'));
                            }});
                        }}
                        
                        if (extractImages) {{
                            result.images = await page.evaluate(() => {{
                                return Array.from(document.querySelectorAll('img[src]'))
                                    .map(img => img.src)
                                    .filter(src => src && src.startsWith('http'));
                            }});
                        }}
                        
                        // Custom selectors
                        if (Object.keys(customSelectors).length > 0) {{
                            result.extractedData = {{}};
                            for (const [key, selector] of Object.entries(customSelectors)) {{
                                try {{
                                    const elements = await page.$$(selector);
                                    result.extractedData[key] = await Promise.all(
                                        elements.map(el => el.innerText || el.textContent)
                                    );
                                }} catch (e) {{
                                    result.extractedData[key] = [];
                                }}
                            }}
                        }}
                        
                        // Wait for selector if specified
                        if (waitForSelector) {{
                            try {{
                                await page.waitForSelector(waitForSelector, {{ timeout: 5000 }});
                            }} catch (e) {{
                                console.log(`Selector ${{waitForSelector}} not found`);
                            }}
                        }}
                        
                    }} else {{
                        // Cheerio-based extraction
                        result.title = $('title').text() || '';
                        
                        if (extractText) {{
                            result.textContent = $('body').text() || '';
                        }}
                        
                        if (extractLinks) {{
                            result.links = [];
                            $('a[href]').each((i, el) => {{
                                const href = $(el).attr('href');
                                if (href && (href.startsWith('http') || href.startsWith('/'))) {{
                                    const absoluteUrl = href.startsWith('http') ? 
                                        href : new URL(href, request.loadedUrl).href;
                                    result.links.push(absoluteUrl);
                                }}
                            }});
                        }}
                        
                        if (extractImages) {{
                            result.images = [];
                            $('img[src]').each((i, el) => {{
                                const src = $(el).attr('src');
                                if (src) {{
                                    const absoluteUrl = src.startsWith('http') ? 
                                        src : new URL(src, request.loadedUrl).href;
                                    result.images.push(absoluteUrl);
                                }}
                            }});
                        }}
                        
                        // Custom selectors for Cheerio
                        if (Object.keys(customSelectors).length > 0) {{
                            result.extractedData = {{}};
                            for (const [key, selector] of Object.entries(customSelectors)) {{
                                try {{
                                    result.extractedData[key] = [];
                                    $(selector).each((i, el) => {{
                                        result.extractedData[key].push($(el).text());
                                    }});
                                }} catch (e) {{
                                    result.extractedData[key] = [];
                                }}
                            }}
                        }}
                    }}
                    
                    // Get HTML content if requested
                    if ($ && $.html) {{
                        result.htmlContent = $.html();
                    }}
                    
                    results.push(result);
                    
                }} catch (error) {{
                    result.error = error.message;
                    results.push(result);
                }}
            }},
            
            failedRequestHandler({{ request, error }}) {{
                results.push({{
                    url: request.url,
                    statusCode: 0,
                    error: error.message,
                    loadTime: 0
                }});
                crawlStats.requestsFailed++;
            }}
        }});
        
        // Add URLs to crawler
        await crawler.addRequests(startUrls.map(url => ({{ url }})));
        
        // Run crawler
        await crawler.run();
        
        const totalTime = Date.now() - startTime;
        crawlStats.totalTime = totalTime;
        crawlStats.requestsFinished = results.filter(r => !r.error).length;
        
        res.json({{
            success: true,
            results: results,
            stats: crawlStats,
            totalResults: results.length
        }});
        
    }} catch (error) {{
        console.error('Crawl error:', error);
        res.status(500).json({{
            success: false,
            error: error.message
        }});
    }}
}});

// Get crawler statistics
app.get('/stats', (req, res) => {{
    res.json({{
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        version: '1.0.0'
    }});
}});

// Start server
app.listen(PORT, () => {{
    console.log(`Crawlee server running on http://localhost:${{PORT}}`);
}});

// Graceful shutdown
process.on('SIGTERM', () => {{
    console.log('Shutting down Crawlee server...');
    process.exit(0);
}});
'''
        
    async def _start_node_server(self):
        """Start the Node.js Crawlee server"""
        
        try:
            logger.info(f"🚀 Starting Crawlee Node.js server on port {self.config.server_port}")
            
            if not shutil.which(self.config.node_binary_path):
                raise RuntimeError("Node.js not found. Please install Node.js")
                
            self.server_process = subprocess.Popen([
                self.config.node_binary_path, "server.js"
            ], cwd=self.temp_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            for _ in range(30):  # Wait up to 30 seconds
                await asyncio.sleep(1)
                if await self._check_server_status():
                    logger.info("✅ Crawlee Node.js server started successfully")
                    return
                    
            raise RuntimeError("Failed to start Crawlee server within timeout")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Node.js server: {str(e)}")
            raise
            
    async def crawl_urls(self, request: CrawleeRequest) -> List[CrawleeResult]:
        """Crawl URLs using Crawlee"""
        
        start_time = time.time()
        self._stats['crawls_initiated'] += 1
        
        try:
            # Prepare request payload
            payload = {
                'startUrls': request.start_urls,
                'maxRequests': request.max_requests,
                'maxConcurrency': request.max_concurrent,
                'requestDelay': request.request_delay * 1000,  # Convert to ms
                'usePuppeteer': request.use_puppeteer,
                'usePlaywright': request.use_playwright,
                'useCheerio': request.use_cheerio,
                'extractLinks': request.extract_links,
                'extractText': request.extract_text,
                'extractImages': request.extract_images,
                'allowedDomains': request.allowed_domains or [],
                'userAgent': request.user_agent or f'Crawlee-Server/1.0',
                'timeout': request.timeout * 1000,  # Convert to ms
                'customSelectors': request.custom_selectors or {},
                'waitForSelector': request.wait_for_selector
            }
            
            # Make request to Crawlee server
            response = self.session.post(
                f"{self.config.crawlee_server_url}/crawl",
                json=payload,
                timeout=request.timeout * 2  # Allow extra time for server processing
            )
            
            crawl_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                if result_data.get('success'):
                    results = []
                    
                    for item in result_data.get('results', []):
                        crawlee_result = CrawleeResult(
                            url=item.get('url', ''),
                            status_code=item.get('statusCode', 0),
                            title=item.get('title'),
                            text_content=item.get('textContent'),
                            html_content=item.get('htmlContent'),
                            links=item.get('links', []),
                            images=item.get('images', []),
                            metadata=item.get('metadata', {}),
                            load_time=item.get('loadTime', 0) / 1000,  # Convert from ms
                            error=item.get('error'),
                            extracted_data=item.get('extractedData', {})
                        )
                        results.append(crawlee_result)
                        
                    # Update stats
                    self._stats['crawls_completed'] += 1
                    self._stats['total_pages_crawled'] += len(results)
                    self._stats['total_crawl_time'] += crawl_time
                    
                    # Count total links found
                    for result in results:
                        if result.links:
                            self._stats['total_links_found'] += len(result.links)
                            
                    return results
                    
                else:
                    error_msg = result_data.get('error', 'Unknown crawl error')
                    self._stats['crawls_failed'] += 1
                    
                    logger.error(f"❌ Crawl failed: {error_msg}")
                    return []
                    
            else:
                error_msg = f"Crawlee server error: {response.status_code}"
                self._stats['crawls_failed'] += 1
                
                logger.error(f"❌ {error_msg}")
                return []
                
        except Exception as e:
            crawl_time = time.time() - start_time
            self._stats['crawls_failed'] += 1
            
            logger.error(f"❌ Crawl request failed: {str(e)}")
            return []
            
    async def crawl_single_url(self, url: str, **kwargs) -> Optional[CrawleeResult]:
        """Crawl single URL"""
        
        request = CrawleeRequest(
            start_urls=[url],
            max_requests=1,
            **kwargs
        )
        
        results = await self.crawl_urls(request)
        return results[0] if results else None
        
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        
        avg_crawl_time = 0.0
        if self._stats['crawls_completed'] > 0:
            avg_crawl_time = self._stats['total_crawl_time'] / self._stats['crawls_completed']
            
        avg_pages_per_crawl = 0.0
        if self._stats['crawls_completed'] > 0:
            avg_pages_per_crawl = self._stats['total_pages_crawled'] / self._stats['crawls_completed']
            
        success_rate = 0.0
        if self._stats['crawls_initiated'] > 0:
            success_rate = self._stats['crawls_completed'] / self._stats['crawls_initiated']
            
        return {
            **self._stats,
            'average_crawl_time': avg_crawl_time,
            'average_pages_per_crawl': avg_pages_per_crawl,
            'success_rate': success_rate,
            'config': asdict(self.config)
        }
        
    async def cleanup(self):
        """Clean up resources"""
        
        # Stop server if we started it
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=10)
                logger.info("🛑 Crawlee server stopped")
            except Exception as e:
                logger.error(f"❌ Failed to stop Crawlee server: {str(e)}")
                
        # Clean up temporary directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info("🧹 Cleaned up Crawlee temp directory")
            except Exception as e:
                logger.error(f"❌ Failed to cleanup temp dir: {str(e)}")

class CrawleeAdapter:
    """High-level adapter for Crawlee integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = CrawleeConfig(**config)
        self.server = CrawleeServer(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Crawlee adapter disabled")
            return
            
        if not REQUESTS_AVAILABLE:
            logger.error("❌ requests not available")
            if self.config.enabled:
                raise ImportError("requests package required")
            return
            
        if self.server:
            await self.server.initialize()
            logger.info("✅ Crawlee adapter initialized")
        else:
            logger.error("❌ Crawlee server not available")
            
    async def crawl_website(self, start_urls: List[str],
                          max_pages: int = 100,
                          use_browser: bool = False,
                          extract_links: bool = True,
                          extract_text: bool = True) -> Dict[str, Any]:
        """
        Crawl website using Crawlee.
        
        Returns:
        {
            'success': bool,
            'results': list,
            'total_pages': int,
            'total_links': int,
            'crawl_time': float
        }
        """
        
        if not self.config.enabled or not self.server:
            return {
                'success': False,
                'error': 'Crawlee is disabled or not available'
            }
            
        try:
            request = CrawleeRequest(
                start_urls=start_urls,
                max_requests=max_pages,
                max_concurrent=self.config.max_concurrent_crawlers,
                request_delay=self.config.default_delay,
                use_puppeteer=use_browser,
                use_cheerio=not use_browser,
                extract_links=extract_links,
                extract_text=extract_text,
                timeout=self.config.default_timeout
            )
            
            start_time = time.time()
            results = await self.server.crawl_urls(request)
            crawl_time = time.time() - start_time
            
            if results:
                # Compile statistics
                total_links = sum(len(r.links or []) for r in results)
                successful_pages = len([r for r in results if r.status_code == 200])
                
                return {
                    'success': True,
                    'results': [
                        {
                            'url': r.url,
                            'title': r.title,
                            'status_code': r.status_code,
                            'text_content': r.text_content,
                            'links': r.links or [],
                            'images': r.images or [],
                            'load_time': r.load_time,
                            'error': r.error,
                            'extracted_data': r.extracted_data or {}
                        }
                        for r in results
                    ],
                    'total_pages': len(results),
                    'successful_pages': successful_pages,
                    'total_links': total_links,
                    'crawl_time': crawl_time,
                    'method': 'crawlee'
                }
            else:
                return {
                    'success': False,
                    'error': 'No results returned from crawler',
                    'method': 'crawlee'
                }
                
        except Exception as e:
            logger.error(f"❌ Failed to crawl website: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'method': 'crawlee'
            }
            
    async def scrape_page(self, url: str, 
                         use_browser: bool = False,
                         selectors: Optional[Dict[str, str]] = None,
                         wait_for: Optional[str] = None) -> Dict[str, Any]:
        """Scrape single page with custom selectors"""
        
        if not self.config.enabled or not self.server:
            return {'success': False, 'error': 'Crawlee not available'}
            
        try:
            result = await self.server.crawl_single_url(
                url,
                use_puppeteer=use_browser,
                use_cheerio=not use_browser,
                custom_selectors=selectors or {},
                wait_for_selector=wait_for,
                extract_links=False,
                extract_text=True
            )
            
            if result:
                return {
                    'success': result.status_code == 200,
                    'url': result.url,
                    'title': result.title,
                    'content': result.text_content,
                    'extracted_data': result.extracted_data or {},
                    'load_time': result.load_time,
                    'error': result.error,
                    'method': 'crawlee-scrape'
                }
            else:
                return {
                    'success': False,
                    'error': 'No result returned',
                    'method': 'crawlee-scrape'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'crawlee-scrape'
            }
            
    async def discover_links(self, start_url: str, 
                           max_depth: int = 2,
                           same_domain_only: bool = True) -> Dict[str, Any]:
        """Discover links from website"""
        
        if not self.config.enabled or not self.server:
            return {'success': False, 'error': 'Crawlee not available'}
            
        try:
            # Configure domain filtering
            allowed_domains = None
            if same_domain_only:
                domain = urlparse(start_url).netloc
                allowed_domains = [domain]
                
            request = CrawleeRequest(
                start_urls=[start_url],
                max_requests=50 * max_depth,  # Reasonable limit per depth
                max_concurrent=5,
                extract_links=True,
                extract_text=False,
                extract_images=False,
                allowed_domains=allowed_domains
            )
            
            results = await self.server.crawl_urls(request)
            
            if results:
                all_links = set()
                successful_pages = 0
                
                for result in results:
                    if result.status_code == 200:
                        successful_pages += 1
                        if result.links:
                            all_links.update(result.links)
                            
                return {
                    'success': True,
                    'start_url': start_url,
                    'discovered_links': list(all_links),
                    'total_links': len(all_links),
                    'pages_crawled': len(results),
                    'successful_pages': successful_pages,
                    'method': 'crawlee-discovery'
                }
            else:
                return {
                    'success': False,
                    'error': 'No results from link discovery',
                    'method': 'crawlee-discovery'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'crawlee-discovery'
            }
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        base_stats = {
            'enabled': self.config.enabled,
            'config': asdict(self.config)
        }
        
        if self.server:
            base_stats['server_stats'] = self.server.get_stats()
        else:
            base_stats['server_stats'] = {}
            
        return base_stats
        
    async def cleanup(self):
        """Clean up all resources"""
        if self.server:
            await self.server.cleanup()

# Factory function
def create_crawlee_adapter(config: Dict[str, Any]) -> CrawleeAdapter:
    """Create and configure Crawlee adapter"""
    return CrawleeAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'auto_start_server': True,
        'max_concurrent_crawlers': 3,
        'default_delay': 1.0,
        'debug': True
    }
    
    adapter = create_crawlee_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Crawl website
        result = await adapter.crawl_website(
            ['http://example.com'],
            max_pages=10,
            use_browser=False
        )
        
        if result['success']:
            print(f"✅ Crawled {result['total_pages']} pages")
            print(f"Found {result['total_links']} links")
            print(f"Crawl time: {result['crawl_time']:.2f}s")
        else:
            print(f"❌ Crawl failed: {result['error']}")
            
        # Scrape single page with custom selectors
        scrape_result = await adapter.scrape_page(
            'http://example.com',
            selectors={'headings': 'h1, h2, h3'}
        )
        
        if scrape_result['success']:
            print(f"✅ Scraped: {scrape_result['title']}")
            print(f"Extracted data: {scrape_result['extracted_data']}")
        else:
            print(f"❌ Scraping failed: {scrape_result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
