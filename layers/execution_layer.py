"""
Execution Layer - Sparkling-Owl-Spin Architecture  
Layer 2: Execution & Acquisition Layer (Crawlee/Playwright/Scrapy)
The Body. Executes tasks.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import aiohttp
from urllib.parse import urljoin, urlparse
import random

logger = logging.getLogger(__name__)

class ExecutionEngine(Enum):
    """Available execution engines"""
    CRAWLEE = "crawlee"
    PLAYWRIGHT = "playwright"
    SCRAPY = "scrapy"
    REQUESTS = "requests"
    SELENIUM = "selenium"

class TaskType(Enum):
    """Types of execution tasks"""
    SCRAPE_PAGE = "scrape_page"
    CRAWL_SITE = "crawl_site"
    VULNERABILITY_TEST = "vulnerability_test"
    RECONNAISSANCE = "reconnaissance"
    OSINT_GATHERING = "osint_gathering"
    FORM_INTERACTION = "form_interaction"
    FILE_EXTRACTION = "file_extraction"

@dataclass
class ExecutionTask:
    """Task definition for execution"""
    task_id: str
    task_type: TaskType
    target: str
    parameters: Dict[str, Any]
    preferred_engine: Optional[ExecutionEngine] = None
    priority: int = 5  # 1-10 scale
    timeout: int = 60
    retries: int = 3
    stealth_level: int = 5

@dataclass
class ExecutionResult:
    """Result from task execution"""
    task_id: str
    success: bool
    data: Dict[str, Any]
    execution_time: float
    engine_used: ExecutionEngine
    errors: List[str]
    metadata: Dict[str, Any]

class CrawleeEngine:
    """Crawlee-based execution engine"""
    
    def __init__(self, bypass_layer):
        self.bypass_layer = bypass_layer
        self.logger = logging.getLogger(self.__class__.__name__)
        self.active_crawlers = {}
        
    async def initialize(self):
        """Initialize Crawlee engine"""
        self.logger.info("🕷️ Initializing Crawlee Engine")
        
        # Check if Node.js and Crawlee are available
        try:
            # This would normally start a Node.js server with Crawlee
            # For now, we'll simulate the functionality
            self.logger.info("✅ Crawlee Engine ready (simulated)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Crawlee: {str(e)}")
            return False
            
    async def execute_task(self, task: ExecutionTask) -> ExecutionResult:
        """Execute task using Crawlee"""
        start_time = time.time()
        
        try:
            if task.task_type == TaskType.SCRAPE_PAGE:
                result_data = await self._scrape_page(task)
            elif task.task_type == TaskType.CRAWL_SITE:
                result_data = await self._crawl_site(task)
            elif task.task_type == TaskType.RECONNAISSANCE:
                result_data = await self._perform_reconnaissance(task)
            else:
                raise ValueError(f"Unsupported task type: {task.task_type}")
                
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                task_id=task.task_id,
                success=True,
                data=result_data,
                execution_time=execution_time,
                engine_used=ExecutionEngine.CRAWLEE,
                errors=[],
                metadata={"stealth_level": task.stealth_level}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Crawlee execution failed for task {task.task_id}: {str(e)}")
            
            return ExecutionResult(
                task_id=task.task_id,
                success=False,
                data={},
                execution_time=execution_time,
                engine_used=ExecutionEngine.CRAWLEE,
                errors=[str(e)],
                metadata={}
            )
            
    async def _scrape_page(self, task: ExecutionTask) -> Dict[str, Any]:
        """Scrape a single page using Crawlee"""
        # Get bypass configuration
        request_config = await self.bypass_layer.process_request(task.target)
        
        # Simulate Crawlee page scraping
        result = {
            "url": task.target,
            "title": f"Title for {task.target}",
            "content": f"Scraped content from {task.target}",
            "links": [f"{task.target}/page1", f"{task.target}/page2"],
            "images": [f"{task.target}/image1.jpg"],
            "forms": [],
            "javascript_rendered": True,
            "load_time": random.uniform(1.0, 3.0),
            "status_code": 200
        }
        
        # Add bypass information
        if "flaresolverr_result" in request_config:
            result["cloudflare_bypassed"] = True
            
        return result
        
    async def _crawl_site(self, task: ExecutionTask) -> Dict[str, Any]:
        """Crawl entire site using Crawlee"""
        max_pages = task.parameters.get("max_pages", 100)
        depth = task.parameters.get("depth", 3)
        
        result = {
            "base_url": task.target,
            "pages_crawled": [],
            "total_pages": min(max_pages, random.randint(10, 50)),
            "depth_reached": depth,
            "discovered_assets": {
                "stylesheets": [],
                "scripts": [],
                "images": [],
                "documents": []
            },
            "sitemap_generated": True
        }
        
        # Simulate crawling multiple pages
        for i in range(result["total_pages"]):
            page_url = f"{task.target}/page_{i+1}"
            result["pages_crawled"].append({
                "url": page_url,
                "title": f"Page {i+1}",
                "status_code": 200,
                "content_length": random.randint(1000, 5000)
            })
            
        return result
        
    async def _perform_reconnaissance(self, task: ExecutionTask) -> Dict[str, Any]:
        """Perform reconnaissance using Crawlee"""
        target_domain = urlparse(task.target).hostname
        
        result = {
            "target": target_domain,
            "subdomains": [
                f"www.{target_domain}",
                f"api.{target_domain}",
                f"admin.{target_domain}",
                f"test.{target_domain}"
            ],
            "technologies": [
                {"name": "nginx", "version": "1.20.1"},
                {"name": "php", "version": "7.4.0"},
                {"name": "mysql", "version": "8.0.0"}
            ],
            "endpoints_discovered": [
                f"{task.target}/api/v1/",
                f"{task.target}/admin/",
                f"{task.target}/login",
                f"{task.target}/upload"
            ],
            "forms_found": [
                {"action": "/login", "method": "POST", "fields": ["username", "password"]},
                {"action": "/search", "method": "GET", "fields": ["q"]},
                {"action": "/contact", "method": "POST", "fields": ["name", "email", "message"]}
            ]
        }
        
        return result

class PlaywrightEngine:
    """Playwright-based execution engine"""
    
    def __init__(self, bypass_layer):
        self.bypass_layer = bypass_layer
        self.logger = logging.getLogger(self.__class__.__name__)
        self.browser = None
        self.contexts = {}
        
    async def initialize(self):
        """Initialize Playwright engine"""
        self.logger.info("🎭 Initializing Playwright Engine")
        
        try:
            # Import and initialize Playwright
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            self.logger.info("✅ Playwright Engine initialized")
            return True
            
        except ImportError:
            self.logger.warning("Playwright not available, using fallback")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Playwright: {str(e)}")
            return False
            
    async def execute_task(self, task: ExecutionTask) -> ExecutionResult:
        """Execute task using Playwright"""
        start_time = time.time()
        
        try:
            if task.task_type == TaskType.SCRAPE_PAGE:
                result_data = await self._scrape_page_with_browser(task)
            elif task.task_type == TaskType.FORM_INTERACTION:
                result_data = await self._interact_with_form(task)
            elif task.task_type == TaskType.VULNERABILITY_TEST:
                result_data = await self._test_vulnerability(task)
            else:
                raise ValueError(f"Unsupported task type for Playwright: {task.task_type}")
                
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                task_id=task.task_id,
                success=True,
                data=result_data,
                execution_time=execution_time,
                engine_used=ExecutionEngine.PLAYWRIGHT,
                errors=[],
                metadata={"browser_used": True}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Playwright execution failed for task {task.task_id}: {str(e)}")
            
            return ExecutionResult(
                task_id=task.task_id,
                success=False,
                data={},
                execution_time=execution_time,
                engine_used=ExecutionEngine.PLAYWRIGHT,
                errors=[str(e)],
                metadata={}
            )
            
    async def _scrape_page_with_browser(self, task: ExecutionTask) -> Dict[str, Any]:
        """Scrape page using real browser"""
        if not self.browser:
            raise RuntimeError("Playwright browser not initialized")
            
        # Create new context for isolation
        context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        try:
            page = await context.new_page()
            
            # Navigate to page
            await page.goto(task.target, wait_until="networkidle")
            
            # Extract comprehensive data
            result = {
                "url": task.target,
                "title": await page.title(),
                "content": await page.content(),
                "text_content": await page.inner_text("body"),
                "links": await page.evaluate("""
                    () => Array.from(document.querySelectorAll('a[href]')).map(a => a.href)
                """),
                "images": await page.evaluate("""
                    () => Array.from(document.querySelectorAll('img[src]')).map(img => img.src)
                """),
                "forms": await self._extract_forms(page),
                "cookies": await context.cookies(),
                "local_storage": await page.evaluate("() => JSON.stringify(localStorage)"),
                "console_logs": [],
                "network_requests": [],
                "performance": await page.evaluate("() => JSON.stringify(performance.timing)"),
                "screenshot": await page.screenshot(full_page=True) if task.parameters.get("take_screenshot") else None
            }
            
            return result
            
        finally:
            await context.close()
            
    async def _extract_forms(self, page) -> List[Dict[str, Any]]:
        """Extract all forms from page"""
        return await page.evaluate("""
            () => {
                const forms = Array.from(document.querySelectorAll('form'));
                return forms.map(form => ({
                    action: form.action,
                    method: form.method,
                    fields: Array.from(form.querySelectorAll('input, textarea, select')).map(field => ({
                        name: field.name,
                        type: field.type,
                        id: field.id,
                        required: field.required,
                        placeholder: field.placeholder
                    }))
                }));
            }
        """)
        
    async def _interact_with_form(self, task: ExecutionTask) -> Dict[str, Any]:
        """Interact with forms for testing"""
        if not self.browser:
            raise RuntimeError("Playwright browser not initialized")
            
        context = await self.browser.new_context()
        
        try:
            page = await context.new_page()
            await page.goto(task.target)
            
            form_selector = task.parameters.get("form_selector", "form")
            test_data = task.parameters.get("test_data", {})
            
            # Fill form fields
            for field_name, value in test_data.items():
                try:
                    await page.fill(f'input[name="{field_name}"]', str(value))
                except:
                    try:
                        await page.fill(f'#{field_name}', str(value))
                    except:
                        self.logger.warning(f"Could not fill field: {field_name}")
                        
            # Submit form and capture response
            await page.click('input[type="submit"], button[type="submit"]')
            await page.wait_for_load_state("networkidle")
            
            result = {
                "form_submitted": True,
                "response_url": page.url,
                "response_content": await page.content(),
                "status_indicators": await self._check_response_indicators(page),
                "error_messages": await self._extract_error_messages(page)
            }
            
            return result
            
        finally:
            await context.close()
            
    async def _test_vulnerability(self, task: ExecutionTask) -> Dict[str, Any]:
        """Test for vulnerabilities using browser"""
        vulnerability_type = task.parameters.get("vulnerability_type")
        payloads = task.parameters.get("payloads", [])
        
        results = {
            "vulnerability_type": vulnerability_type,
            "tested_payloads": len(payloads),
            "vulnerable": False,
            "evidence": [],
            "response_analysis": {}
        }
        
        for payload in payloads:
            try:
                test_result = await self._test_single_payload(task.target, payload, vulnerability_type)
                if test_result.get("vulnerable"):
                    results["vulnerable"] = True
                    results["evidence"].append(test_result)
                    
            except Exception as e:
                self.logger.error(f"Error testing payload {payload}: {str(e)}")
                
        return results
        
    async def _test_single_payload(self, url: str, payload: str, vuln_type: str) -> Dict[str, Any]:
        """Test single payload against target"""
        # This would implement specific vulnerability testing logic
        # For now, return a mock result
        return {
            "payload": payload,
            "vulnerable": False,
            "response_time": random.uniform(0.1, 2.0),
            "response_content": "Mock response content",
            "indicators": []
        }
        
    async def _check_response_indicators(self, page) -> List[str]:
        """Check for common response indicators"""
        indicators = []
        
        # Check for common success/error indicators
        success_selectors = ['.success', '.alert-success', '[class*="success"]']
        error_selectors = ['.error', '.alert-error', '.alert-danger', '[class*="error"]']
        
        for selector in success_selectors:
            try:
                if await page.query_selector(selector):
                    indicators.append("success_indicator_found")
                    break
            except:
                pass
                
        for selector in error_selectors:
            try:
                if await page.query_selector(selector):
                    indicators.append("error_indicator_found")
                    break
            except:
                pass
                
        return indicators
        
    async def _extract_error_messages(self, page) -> List[str]:
        """Extract error messages from page"""
        try:
            return await page.evaluate("""
                () => {
                    const errorElements = document.querySelectorAll('.error, .alert-error, .alert-danger, [class*="error"]');
                    return Array.from(errorElements).map(el => el.textContent.trim()).filter(text => text.length > 0);
                }
            """)
        except:
            return []
            
    async def cleanup(self):
        """Cleanup Playwright resources"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

class RequestsEngine:
    """Requests-based execution engine for simple tasks"""
    
    def __init__(self, bypass_layer):
        self.bypass_layer = bypass_layer
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = None
        
    async def initialize(self):
        """Initialize Requests engine"""
        self.logger.info("📡 Initializing Requests Engine")
        self.session = aiohttp.ClientSession()
        self.logger.info("✅ Requests Engine initialized")
        return True
        
    async def execute_task(self, task: ExecutionTask) -> ExecutionResult:
        """Execute task using HTTP requests"""
        start_time = time.time()
        
        try:
            if task.task_type == TaskType.SCRAPE_PAGE:
                result_data = await self._scrape_page_http(task)
            elif task.task_type == TaskType.RECONNAISSANCE:
                result_data = await self._http_reconnaissance(task)
            else:
                raise ValueError(f"Unsupported task type for Requests engine: {task.task_type}")
                
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                task_id=task.task_id,
                success=True,
                data=result_data,
                execution_time=execution_time,
                engine_used=ExecutionEngine.REQUESTS,
                errors=[],
                metadata={"method": "http_only"}
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Requests execution failed for task {task.task_id}: {str(e)}")
            
            return ExecutionResult(
                task_id=task.task_id,
                success=False,
                data={},
                execution_time=execution_time,
                engine_used=ExecutionEngine.REQUESTS,
                errors=[str(e)],
                metadata={}
            )
            
    async def _scrape_page_http(self, task: ExecutionTask) -> Dict[str, Any]:
        """Scrape page using HTTP requests only"""
        # Get bypass configuration
        request_config = await self.bypass_layer.process_request(task.target)
        
        # Make HTTP request with bypass configuration
        async with self.session.get(
            task.target,
            headers=request_config.get("headers", {}),
            proxy=request_config.get("proxy"),
            timeout=request_config.get("timeout", 30)
        ) as response:
            content = await response.text()
            
            result = {
                "url": task.target,
                "status_code": response.status,
                "headers": dict(response.headers),
                "content": content,
                "content_length": len(content),
                "response_time": time.time(),
                "cookies": [{"name": cookie.key, "value": cookie.value} for cookie in response.cookies]
            }
            
            # Basic HTML parsing without browser
            if "html" in response.content_type:
                result.update(await self._parse_html_basic(content))
                
            return result
            
    async def _parse_html_basic(self, html_content: str) -> Dict[str, Any]:
        """Basic HTML parsing without full browser"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            return {
                "title": soup.title.string if soup.title else "",
                "links": [a.get('href') for a in soup.find_all('a', href=True)],
                "images": [img.get('src') for img in soup.find_all('img', src=True)],
                "forms": [{"action": form.get('action'), "method": form.get('method', 'GET')} 
                         for form in soup.find_all('form')],
                "text_content": soup.get_text()[:1000]  # First 1000 chars
            }
        except ImportError:
            self.logger.warning("BeautifulSoup not available for HTML parsing")
            return {"parsing": "basic_regex_only"}
            
    async def _http_reconnaissance(self, task: ExecutionTask) -> Dict[str, Any]:
        """Perform HTTP-based reconnaissance"""
        target_domain = urlparse(task.target).hostname
        
        result = {
            "target": target_domain,
            "http_methods_allowed": [],
            "server_headers": {},
            "security_headers": {},
            "cookies": [],
            "redirects": [],
            "response_analysis": {}
        }
        
        # Test different HTTP methods
        methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
        for method in methods:
            try:
                async with self.session.request(method, task.target, timeout=10) as response:
                    if response.status < 405:  # Method allowed
                        result["http_methods_allowed"].append(method)
                        
            except Exception:
                pass
                
        # Analyze server headers
        try:
            async with self.session.get(task.target, timeout=10) as response:
                result["server_headers"] = dict(response.headers)
                
                # Check for security headers
                security_headers = [
                    "content-security-policy", "x-frame-options", "x-content-type-options",
                    "strict-transport-security", "x-xss-protection"
                ]
                
                for header in security_headers:
                    if header in response.headers:
                        result["security_headers"][header] = response.headers[header]
                        
        except Exception as e:
            self.logger.error(f"Error in HTTP reconnaissance: {str(e)}")
            
        return result
        
    async def cleanup(self):
        """Cleanup Requests engine"""
        if self.session:
            await self.session.close()

class ExecutionLayer:
    """
    Main execution layer coordinator
    Routes tasks to appropriate execution engines
    """
    
    def __init__(self, config, bypass_layer):
        self.config = config
        self.bypass_layer = bypass_layer
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize execution engines
        self.engines = {}
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}
        
        # Execution statistics
        self.stats = {
            "tasks_executed": 0,
            "tasks_successful": 0,
            "tasks_failed": 0,
            "total_execution_time": 0.0,
            "engine_usage": {}
        }
        
    async def initialize(self):
        """Initialize execution layer and all engines"""
        self.logger.info("⚡ Initializing Execution Layer")
        
        # Initialize available engines
        await self._initialize_engines()
        
        # Start task processor
        asyncio.create_task(self._process_task_queue())
        
        self.logger.info("✅ Execution Layer initialized successfully")
        
    async def _initialize_engines(self):
        """Initialize all available execution engines"""
        # Initialize Crawlee engine
        crawlee_engine = CrawleeEngine(self.bypass_layer)
        if await crawlee_engine.initialize():
            self.engines[ExecutionEngine.CRAWLEE] = crawlee_engine
            
        # Initialize Playwright engine
        playwright_engine = PlaywrightEngine(self.bypass_layer)
        if await playwright_engine.initialize():
            self.engines[ExecutionEngine.PLAYWRIGHT] = playwright_engine
            
        # Initialize Requests engine (always available)
        requests_engine = RequestsEngine(self.bypass_layer)
        if await requests_engine.initialize():
            self.engines[ExecutionEngine.REQUESTS] = requests_engine
            
        self.logger.info(f"Initialized {len(self.engines)} execution engines")
        
    async def execute_task(self, task: ExecutionTask) -> ExecutionResult:
        """Execute a task using the most appropriate engine"""
        # Select best engine for task
        engine = self._select_engine(task)
        
        if not engine:
            return ExecutionResult(
                task_id=task.task_id,
                success=False,
                data={},
                execution_time=0.0,
                engine_used=ExecutionEngine.REQUESTS,
                errors=["No suitable engine available"],
                metadata={}
            )
            
        # Execute task with retry logic
        for attempt in range(task.retries + 1):
            try:
                result = await engine.execute_task(task)
                
                # Update statistics
                self.stats["tasks_executed"] += 1
                if result.success:
                    self.stats["tasks_successful"] += 1
                else:
                    self.stats["tasks_failed"] += 1
                    
                self.stats["total_execution_time"] += result.execution_time
                
                engine_name = result.engine_used.value
                self.stats["engine_usage"][engine_name] = self.stats["engine_usage"].get(engine_name, 0) + 1
                
                if result.success or attempt == task.retries:
                    return result
                    
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
                
            except Exception as e:
                self.logger.error(f"Task execution error (attempt {attempt + 1}): {str(e)}")
                
        # All retries exhausted
        return ExecutionResult(
            task_id=task.task_id,
            success=False,
            data={},
            execution_time=0.0,
            engine_used=ExecutionEngine.REQUESTS,
            errors=["All retry attempts exhausted"],
            metadata={"attempts": task.retries + 1}
        )
        
    def _select_engine(self, task: ExecutionTask) -> Optional[object]:
        """Select the best engine for a given task"""
        # If preferred engine is specified and available
        if task.preferred_engine and task.preferred_engine in self.engines:
            return self.engines[task.preferred_engine]
            
        # Task-specific engine selection logic
        if task.task_type == TaskType.VULNERABILITY_TEST:
            # Prefer Playwright for vulnerability testing
            if ExecutionEngine.PLAYWRIGHT in self.engines:
                return self.engines[ExecutionEngine.PLAYWRIGHT]
                
        elif task.task_type == TaskType.CRAWL_SITE:
            # Prefer Crawlee for site crawling
            if ExecutionEngine.CRAWLEE in self.engines:
                return self.engines[ExecutionEngine.CRAWLEE]
                
        elif task.task_type == TaskType.FORM_INTERACTION:
            # Prefer Playwright for form interaction
            if ExecutionEngine.PLAYWRIGHT in self.engines:
                return self.engines[ExecutionEngine.PLAYWRIGHT]
                
        elif task.task_type == TaskType.RECONNAISSANCE:
            # Prefer Crawlee for reconnaissance
            if ExecutionEngine.CRAWLEE in self.engines:
                return self.engines[ExecutionEngine.CRAWLEE]
            elif ExecutionEngine.REQUESTS in self.engines:
                return self.engines[ExecutionEngine.REQUESTS]
                
        # Default fallback
        if ExecutionEngine.REQUESTS in self.engines:
            return self.engines[ExecutionEngine.REQUESTS]
            
        return None
        
    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step from an orchestrated plan"""
        task = ExecutionTask(
            task_id=step.get("id", "step_" + str(int(time.time()))),
            task_type=TaskType(step.get("type", "scrape_page")),
            target=step.get("target", ""),
            parameters=step.get("parameters", {}),
            preferred_engine=ExecutionEngine(step.get("engine")) if step.get("engine") else None,
            stealth_level=step.get("stealth_level", 5)
        )
        
        result = await self.execute_task(task)
        
        return {
            "success": result.success,
            "data": result.data,
            "execution_time": result.execution_time,
            "errors": result.errors,
            "metadata": result.metadata
        }
        
    async def gather_intelligence(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Gather intelligence based on operation specification"""
        operation_type = operation.get("type", "general")
        target = operation.get("target", "")
        
        task = ExecutionTask(
            task_id=f"intel_{operation_type}_{int(time.time())}",
            task_type=TaskType.OSINT_GATHERING,
            target=target,
            parameters=operation.get("parameters", {}),
            stealth_level=operation.get("stealth_level", 7)
        )
        
        result = await self.execute_task(task)
        return result.data if result.success else {}
        
    async def perform_reconnaissance(self, target: str) -> Dict[str, Any]:
        """Perform comprehensive reconnaissance"""
        task = ExecutionTask(
            task_id=f"recon_{int(time.time())}",
            task_type=TaskType.RECONNAISSANCE,
            target=target,
            parameters={"comprehensive": True},
            stealth_level=8
        )
        
        result = await self.execute_task(task)
        return result.data if result.success else {}
        
    async def execute_vulnerability_test(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Execute vulnerability test"""
        task = ExecutionTask(
            task_id=f"vuln_test_{int(time.time())}",
            task_type=TaskType.VULNERABILITY_TEST,
            target=test.get("target", ""),
            parameters=test,
            preferred_engine=ExecutionEngine.PLAYWRIGHT,
            stealth_level=9
        )
        
        result = await self.execute_task(task)
        return result.data if result.success else {}
        
    async def _process_task_queue(self):
        """Process queued tasks in background"""
        while True:
            try:
                task = await self.task_queue.get()
                result = await self.execute_task(task)
                self.active_tasks[task.task_id] = result
                self.task_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error processing queued task: {str(e)}")
                
    async def get_status(self) -> Dict[str, Any]:
        """Get execution layer status"""
        return {
            "healthy": len(self.engines) > 0,
            "available_engines": list(self.engines.keys()),
            "queued_tasks": self.task_queue.qsize(),
            "active_tasks": len(self.active_tasks),
            "statistics": self.stats.copy()
        }
        
    async def cleanup(self):
        """Cleanup execution layer resources"""
        self.logger.info("🧹 Cleaning up Execution Layer")
        
        # Cleanup all engines
        for engine in self.engines.values():
            if hasattr(engine, 'cleanup'):
                await engine.cleanup()
                
        # Clear task queue
        while not self.task_queue.empty():
            try:
                self.task_queue.get_nowait()
                self.task_queue.task_done()
            except asyncio.QueueEmpty:
                break
                
        self.active_tasks.clear()
        self.logger.info("✅ Execution Layer cleanup completed")
