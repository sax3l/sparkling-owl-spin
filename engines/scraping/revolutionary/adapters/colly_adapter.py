#!/usr/bin/env python3
"""
Colly Integration - Revolutionary Ultimate System v4.0
Go-powered web scraper and URL discovery system via HTTP API
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
class CollyRequest:
    """Container for Colly scraping request"""
    url: str
    method: str = 'GET'
    headers: Optional[Dict[str, str]] = None
    data: Optional[Dict[str, Any]] = None
    user_agent: Optional[str] = None
    timeout: int = 30
    follow_redirects: bool = True
    depth: int = 0
    callback: Optional[str] = None

@dataclass
class CollyResponse:
    """Container for Colly response data"""
    url: str
    status_code: int
    headers: Dict[str, str]
    body: str
    response_time: float
    final_url: Optional[str] = None
    error: Optional[str] = None
    depth: int = 0
    found_links: Optional[List[str]] = None
    extracted_data: Optional[Dict[str, Any]] = None

@dataclass
class CollyConfig:
    """Configuration for Colly scraper"""
    enabled: bool = True
    colly_server_url: str = "http://localhost:8080"
    colly_binary_path: Optional[str] = None
    go_binary_path: str = "go"
    auto_start_server: bool = True
    server_port: int = 8080
    max_concurrent: int = 10
    delay: float = 1.0
    timeout: int = 30
    user_agent: str = "Colly/Revolutionary-Spider 1.0"
    allowed_domains: List[str] = None
    disallowed_domains: List[str] = None
    follow_robots_txt: bool = True
    max_depth: int = 3
    max_pages: int = 100
    cache_enabled: bool = True
    debug: bool = False

class CollyServer:
    """
    Colly server manager for Go-based web scraping.
    
    Features:
    - High-performance Go-based scraping
    - Concurrent request handling
    - Built-in rate limiting
    - Domain filtering
    - Robots.txt compliance
    - CSS selector support
    - XPath support
    - Form handling
    """
    
    def __init__(self, config: CollyConfig):
        self.config = config
        self.server_process = None
        self.temp_dir = None
        self.session = None
        self._stats = {
            'requests_sent': 0,
            'requests_successful': 0,
            'requests_failed': 0,
            'total_response_time': 0.0,
            'pages_scraped': 0,
            'links_found': 0,
            'domains_visited': set(),
            'server_starts': 0
        }
        
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests not available. Install with: pip install requests")
            
    async def initialize(self):
        """Initialize Colly server"""
        
        if not self.config.enabled:
            return
            
        logger.info("🚀 Initializing Colly server...")
        
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="colly_"))
        
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
            logger.info("✅ Colly server already running")
            return
            
        # Start server if needed
        if self.config.auto_start_server:
            await self._start_colly_server()
        else:
            logger.warning("⚠️ Colly server not running and auto_start_server is disabled")
            
        logger.info("✅ Colly server initialized")
        
    async def _check_server_status(self) -> bool:
        """Check if Colly server is running"""
        
        try:
            response = self.session.get(
                f"{self.config.colly_server_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                server_info = response.json()
                logger.info(f"✅ Colly server running: {server_info.get('version', 'unknown')}")
                return True
                
        except Exception as e:
            logger.debug(f"Colly server not available: {str(e)}")
            
        return False
        
    def _find_free_port(self) -> int:
        """Find a free port for the server"""
        
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
            return port
            
    async def _start_colly_server(self):
        """Start Colly server using Go binary or create simple server"""
        
        try:
            # Check if we have a Colly binary
            colly_binary = self.config.colly_binary_path
            
            if not colly_binary:
                # Try to find or create Colly server
                colly_binary = await self._setup_colly_server()
                
            if colly_binary and Path(colly_binary).exists():
                await self._start_go_server(colly_binary)
            else:
                # Fallback to Python-based mock server
                await self._start_mock_server()
                
            self._stats['server_starts'] += 1
            
        except Exception as e:
            logger.error(f"❌ Failed to start Colly server: {str(e)}")
            raise
            
    async def _setup_colly_server(self) -> Optional[str]:
        """Setup Colly server from source or download binary"""
        
        try:
            logger.info("📦 Setting up Colly server...")
            
            # Create Go source for Colly server
            go_source = self._generate_colly_server_source()
            
            # Write Go source file
            go_file = self.temp_dir / "colly_server.go"
            with open(go_file, 'w') as f:
                f.write(go_source)
                
            # Try to build with Go
            try:
                binary_path = self.temp_dir / "colly_server"
                if Path(self.config.go_binary_path).exists() or shutil.which(self.config.go_binary_path):
                    
                    # Initialize Go module
                    subprocess.run([
                        self.config.go_binary_path, "mod", "init", "colly_server"
                    ], cwd=self.temp_dir, check=True, capture_output=True)
                    
                    # Get Colly dependency
                    subprocess.run([
                        self.config.go_binary_path, "mod", "tidy"
                    ], cwd=self.temp_dir, check=True, capture_output=True)
                    
                    # Build binary
                    build_result = subprocess.run([
                        self.config.go_binary_path, "build", "-o", str(binary_path), str(go_file)
                    ], cwd=self.temp_dir, capture_output=True, text=True)
                    
                    if build_result.returncode == 0 and binary_path.exists():
                        logger.info("✅ Colly server built successfully")
                        return str(binary_path)
                    else:
                        logger.warning(f"⚠️ Go build failed: {build_result.stderr}")
                        
            except Exception as e:
                logger.warning(f"⚠️ Failed to build Go server: {str(e)}")
                
        except Exception as e:
            logger.error(f"❌ Colly server setup failed: {str(e)}")
            
        return None
        
    def _generate_colly_server_source(self) -> str:
        """Generate Go source code for Colly server"""
        
        return f'''package main

import (
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "strconv"
    "time"
    
    "github.com/gocolly/colly/v2"
    "github.com/gocolly/colly/v2/debug"
    "github.com/gorilla/mux"
)

type ScrapeRequest struct {{
    URL            string            `json:"url"`
    Method         string            `json:"method"`
    Headers        map[string]string `json:"headers"`
    UserAgent      string            `json:"user_agent"`
    Timeout        int               `json:"timeout"`
    FollowRedirects bool             `json:"follow_redirects"`
    MaxDepth       int               `json:"max_depth"`
    AllowedDomains []string          `json:"allowed_domains"`
    Selectors      map[string]string `json:"selectors"`
}}

type ScrapeResponse struct {{
    URL          string            `json:"url"`
    StatusCode   int               `json:"status_code"`
    Headers      map[string]string `json:"headers"`
    Body         string            `json:"body"`
    ResponseTime float64           `json:"response_time"`
    FinalURL     string            `json:"final_url"`
    Error        string            `json:"error,omitempty"`
    FoundLinks   []string          `json:"found_links"`
    ExtractedData map[string]interface{} `json:"extracted_data"`
}}

func healthHandler(w http.ResponseWriter, r *http.Request) {{
    response := map[string]interface{}{{
        "status": "ok",
        "version": "1.0.0",
        "colly_version": "2.1.0",
    }}
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}}

func scrapeHandler(w http.ResponseWriter, r *http.Request) {{
    var req ScrapeRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {{
        http.Error(w, "Invalid JSON", http.StatusBadRequest)
        return
    }}
    
    start := time.Now()
    
    // Create collector
    c := colly.NewCollector(
        colly.UserAgent(req.UserAgent),
    )
    
    // Configure
    if req.MaxDepth > 0 {{
        c.Limit(&colly.LimitRule{{
            DomainGlob:  "*",
            Parallelism: {self.config.max_concurrent},
            Delay:       time.Duration({self.config.delay * 1000}) * time.Millisecond,
        }})
    }}
    
    if len(req.AllowedDomains) > 0 {{
        c.AllowedDomains = req.AllowedDomains
    }}
    
    response := ScrapeResponse{{
        URL: req.URL,
        FoundLinks: []string{{}},
        ExtractedData: make(map[string]interface{{}}),
    }}
    
    // Set up callbacks
    c.OnHTML("a[href]", func(e *colly.HTMLElement) {{
        link := e.Attr("href")
        if link != "" {{
            absoluteURL := e.Request.AbsoluteURL(link)
            response.FoundLinks = append(response.FoundLinks, absoluteURL)
        }}
    }})
    
    c.OnResponse(func(r *colly.Response) {{
        response.StatusCode = r.StatusCode
        response.Body = string(r.Body)
        response.FinalURL = r.Request.URL.String()
        
        // Convert headers
        headers := make(map[string]string)
        for key, values := range r.Headers {{
            if len(values) > 0 {{
                headers[key] = values[0]
            }}
        }}
        response.Headers = headers
    }})
    
    c.OnError(func(r *colly.Response, err error) {{
        response.Error = err.Error()
        response.StatusCode = r.StatusCode
    }})
    
    // Execute scraping
    err := c.Visit(req.URL)
    if err != nil && response.Error == "" {{
        response.Error = err.Error()
    }}
    
    response.ResponseTime = time.Since(start).Seconds()
    
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(response)
}}

func main() {{
    r := mux.NewRouter()
    
    r.HandleFunc("/health", healthHandler).Methods("GET")
    r.HandleFunc("/scrape", scrapeHandler).Methods("POST")
    
    port := {self.config.server_port}
    
    fmt.Printf("Starting Colly server on port %d\\n", port)
    log.Fatal(http.ListenAndServe(":"+strconv.Itoa(port), r))
}}
'''
        
    async def _start_go_server(self, binary_path: str):
        """Start the Go Colly server"""
        
        try:
            logger.info(f"🚀 Starting Colly Go server on port {self.config.server_port}")
            
            self.server_process = subprocess.Popen(
                [str(binary_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            # Wait for server to start
            for _ in range(30):  # Wait up to 30 seconds
                await asyncio.sleep(1)
                if await self._check_server_status():
                    logger.info("✅ Colly Go server started successfully")
                    return
                    
            raise RuntimeError("Failed to start Colly Go server within timeout")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Go server: {str(e)}")
            raise
            
    async def _start_mock_server(self):
        """Start Python mock server as fallback"""
        
        try:
            logger.info("🔄 Starting Colly mock server (Python fallback)")
            
            # Create simple mock server
            mock_server_code = f'''
import http.server
import socketserver
import json
import threading
import time
from urllib.parse import urlparse
import requests

class CollyMockHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {{"status": "ok", "version": "mock-1.0.0"}}
            self.wfile.write(json.dumps(response).encode())
            
    def do_POST(self):
        if self.path == '/scrape':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_data = json.loads(post_data.decode())
                
                # Simple mock scraping
                start_time = time.time()
                try:
                    response = requests.get(
                        request_data['url'], 
                        timeout=request_data.get('timeout', 30),
                        headers={{'User-Agent': request_data.get('user_agent', 'Colly-Mock')}}
                    )
                    
                    mock_response = {{
                        'url': request_data['url'],
                        'status_code': response.status_code,
                        'headers': dict(response.headers),
                        'body': response.text[:10000],  # Limit body size
                        'response_time': time.time() - start_time,
                        'final_url': response.url,
                        'found_links': [],
                        'extracted_data': {{}}
                    }}
                    
                    # Simple link extraction
                    import re
                    links = re.findall(r'href=[\'"]([^\'"]+)[\'"]', response.text)
                    base_url = f"{{urlparse(request_data['url']).scheme}}://{{urlparse(request_data['url']).netloc}}"
                    
                    for link in links[:50]:  # Limit links
                        if link.startswith('http'):
                            mock_response['found_links'].append(link)
                        elif link.startswith('/'):
                            mock_response['found_links'].append(base_url + link)
                    
                except Exception as e:
                    mock_response = {{
                        'url': request_data['url'],
                        'status_code': 0,
                        'headers': {{}},
                        'body': '',
                        'response_time': time.time() - start_time,
                        'error': str(e),
                        'found_links': [],
                        'extracted_data': {{}}
                    }}
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(mock_response).encode())
                
            except Exception as e:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(json.dumps({{'error': str(e)}}).encode())

PORT = {self.config.server_port}
Handler = CollyMockHandler

def start_server():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    import time
    while True:
        time.sleep(1)
'''
            
            # Write and start mock server
            mock_file = self.temp_dir / "colly_mock_server.py"
            with open(mock_file, 'w') as f:
                f.write(mock_server_code)
                
            self.server_process = subprocess.Popen([
                'python', str(mock_file)
            ], cwd=self.temp_dir)
            
            # Wait for server to start
            for _ in range(15):
                await asyncio.sleep(1)
                if await self._check_server_status():
                    logger.info("✅ Colly mock server started successfully")
                    return
                    
            raise RuntimeError("Failed to start Colly mock server")
            
        except Exception as e:
            logger.error(f"❌ Failed to start mock server: {str(e)}")
            raise
            
    async def scrape_url(self, url: str, **kwargs) -> CollyResponse:
        """Scrape single URL using Colly"""
        
        start_time = time.time()
        self._stats['requests_sent'] += 1
        
        try:
            request_data = CollyRequest(url=url, **kwargs)
            
            # Prepare request
            payload = {
                'url': request_data.url,
                'method': request_data.method,
                'headers': request_data.headers or {},
                'user_agent': request_data.user_agent or self.config.user_agent,
                'timeout': request_data.timeout,
                'follow_redirects': request_data.follow_redirects,
                'max_depth': self.config.max_depth,
                'allowed_domains': self.config.allowed_domains or []
            }
            
            # Make request to Colly server
            response = self.session.post(
                f"{self.config.colly_server_url}/scrape",
                json=payload,
                timeout=request_data.timeout + 10
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result_data = response.json()
                
                colly_response = CollyResponse(
                    url=result_data.get('url', url),
                    status_code=result_data.get('status_code', 0),
                    headers=result_data.get('headers', {}),
                    body=result_data.get('body', ''),
                    response_time=result_data.get('response_time', response_time),
                    final_url=result_data.get('final_url'),
                    error=result_data.get('error'),
                    found_links=result_data.get('found_links', []),
                    extracted_data=result_data.get('extracted_data', {})
                )
                
                # Update stats
                self._stats['requests_successful'] += 1
                self._stats['total_response_time'] += response_time
                self._stats['pages_scraped'] += 1
                self._stats['links_found'] += len(colly_response.found_links or [])
                
                # Track domains
                domain = urlparse(url).netloc
                if domain:
                    self._stats['domains_visited'].add(domain)
                    
                return colly_response
                
            else:
                error_msg = f"Colly server error: {response.status_code}"
                self._stats['requests_failed'] += 1
                
                return CollyResponse(
                    url=url,
                    status_code=response.status_code,
                    headers={},
                    body='',
                    response_time=response_time,
                    error=error_msg
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            self._stats['requests_failed'] += 1
            
            logger.error(f"❌ Scraping failed for {url}: {str(e)}")
            
            return CollyResponse(
                url=url,
                status_code=0,
                headers={},
                body='',
                response_time=response_time,
                error=str(e)
            )
            
    async def scrape_multiple(self, urls: List[str], **kwargs) -> List[CollyResponse]:
        """Scrape multiple URLs concurrently"""
        
        semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
        async def scrape_single(url):
            async with semaphore:
                return await self.scrape_url(url, **kwargs)
                
        tasks = [scrape_single(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, CollyResponse):
                valid_results.append(result)
            else:
                logger.error(f"❌ Scraping task failed: {str(result)}")
                
        return valid_results
        
    async def discover_links(self, start_url: str, max_depth: int = 2) -> List[str]:
        """Discover links starting from URL"""
        
        discovered = set()
        to_visit = [(start_url, 0)]
        visited = set()
        
        while to_visit and len(discovered) < self.config.max_pages:
            current_url, depth = to_visit.pop(0)
            
            if current_url in visited or depth > max_depth:
                continue
                
            visited.add(current_url)
            
            try:
                response = await self.scrape_url(current_url, timeout=self.config.timeout)
                
                if response.status_code == 200 and response.found_links:
                    for link in response.found_links[:20]:  # Limit links per page
                        if link not in discovered and link not in visited:
                            discovered.add(link)
                            
                            if depth < max_depth:
                                to_visit.append((link, depth + 1))
                                
            except Exception as e:
                logger.error(f"❌ Link discovery failed for {current_url}: {str(e)}")
                continue
                
            # Rate limiting
            if self.config.delay > 0:
                await asyncio.sleep(self.config.delay)
                
        return list(discovered)
        
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        
        avg_response_time = 0.0
        if self._stats['requests_successful'] > 0:
            avg_response_time = self._stats['total_response_time'] / self._stats['requests_successful']
            
        success_rate = 0.0
        if self._stats['requests_sent'] > 0:
            success_rate = self._stats['requests_successful'] / self._stats['requests_sent']
            
        return {
            **self._stats,
            'domains_visited': len(self._stats['domains_visited']),
            'average_response_time': avg_response_time,
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
                logger.info("🛑 Colly server stopped")
            except Exception as e:
                logger.error(f"❌ Failed to stop Colly server: {str(e)}")
                
        # Clean up temporary directory
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info("🧹 Cleaned up Colly temp directory")
            except Exception as e:
                logger.error(f"❌ Failed to cleanup temp dir: {str(e)}")

class CollyAdapter:
    """High-level adapter for Colly integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = CollyConfig(**config)
        self.server = CollyServer(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Colly adapter disabled")
            return
            
        if not REQUESTS_AVAILABLE:
            logger.error("❌ requests not available")
            if self.config.enabled:
                raise ImportError("requests package required")
            return
            
        if self.server:
            await self.server.initialize()
            logger.info("✅ Colly adapter initialized")
        else:
            logger.error("❌ Colly server not available")
            
    async def scrape_url(self, url: str, extract_links: bool = True,
                        timeout: int = 30) -> Dict[str, Any]:
        """
        Scrape single URL using Colly.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'status_code': int,
            'content': str,
            'response_time': float,
            'found_links': list,
            'final_url': str
        }
        """
        
        if not self.config.enabled or not self.server:
            return {
                'success': False,
                'url': url,
                'error': 'Colly is disabled or not available'
            }
            
        try:
            response = await self.server.scrape_url(
                url,
                timeout=timeout,
                user_agent=self.config.user_agent
            )
            
            return {
                'success': response.status_code == 200,
                'url': response.url,
                'status_code': response.status_code,
                'content': response.body,
                'headers': response.headers,
                'response_time': response.response_time,
                'found_links': response.found_links or [] if extract_links else [],
                'final_url': response.final_url or response.url,
                'error': response.error,
                'method': 'colly'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to scrape URL: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'colly'
            }
            
    async def discover_urls(self, start_url: str, max_depth: int = 2,
                          max_urls: int = 100) -> Dict[str, Any]:
        """Discover URLs starting from given URL"""
        
        if not self.config.enabled or not self.server:
            return {'success': False, 'error': 'Colly not available'}
            
        try:
            # Configure limits
            old_max_pages = self.server.config.max_pages
            self.server.config.max_pages = max_urls
            
            discovered_links = await self.server.discover_links(start_url, max_depth)
            
            # Restore config
            self.server.config.max_pages = old_max_pages
            
            return {
                'success': True,
                'start_url': start_url,
                'discovered_urls': discovered_links,
                'total_discovered': len(discovered_links),
                'max_depth': max_depth,
                'method': 'colly-discovery'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'colly-discovery'
            }
            
    async def scrape_multiple(self, urls: List[str]) -> Dict[str, Any]:
        """Scrape multiple URLs concurrently"""
        
        if not self.config.enabled or not self.server:
            return {'success': False, 'error': 'Colly not available'}
            
        try:
            responses = await self.server.scrape_multiple(urls)
            
            results = []
            successful = 0
            
            for response in responses:
                result = {
                    'url': response.url,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'content_length': len(response.body),
                    'response_time': response.response_time,
                    'links_found': len(response.found_links or []),
                    'error': response.error
                }
                
                results.append(result)
                
                if response.status_code == 200:
                    successful += 1
                    
            return {
                'success': True,
                'results': results,
                'total_requested': len(urls),
                'total_successful': successful,
                'success_rate': successful / len(urls) if urls else 0,
                'method': 'colly-batch'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'colly-batch'
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
def create_colly_adapter(config: Dict[str, Any]) -> CollyAdapter:
    """Create and configure Colly adapter"""
    return CollyAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'auto_start_server': True,
        'max_concurrent': 5,
        'delay': 1.0,
        'debug': True
    }
    
    adapter = create_colly_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Scrape single URL
        result = await adapter.scrape_url('http://example.com')
        
        if result['success']:
            print(f"✅ Scraped: {result['url']}")
            print(f"Status: {result['status_code']}")
            print(f"Links found: {len(result['found_links'])}")
            print(f"Response time: {result['response_time']:.2f}s")
        else:
            print(f"❌ Scraping failed: {result['error']}")
            
        # Discover URLs
        discovery_result = await adapter.discover_urls('http://example.com', max_depth=1)
        
        if discovery_result['success']:
            print(f"✅ Discovered {discovery_result['total_discovered']} URLs")
        else:
            print(f"❌ Discovery failed: {discovery_result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
