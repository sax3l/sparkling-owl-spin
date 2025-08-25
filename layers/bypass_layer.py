"""
Bypass Layer - Sparkling-Owl-Spin Architecture
Layer 3: Resistance & Bypass Layer (FlareSolverr/proxy_pool/undetected-chromedriver)
Shield and lubricant. Overcomes obstacles.
"""

import asyncio
import logging
import random
import time
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import aiohttp
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class BypassMethod(Enum):
    """Available bypass methods"""
    FLARESOLVERR = "flaresolverr"
    PROXY_ROTATION = "proxy_rotation" 
    STEALTH_HEADERS = "stealth_headers"
    USER_AGENT_ROTATION = "user_agent_rotation"
    CAPTCHA_SOLVING = "captcha_solving"
    RATE_LIMITING = "rate_limiting"
    TLS_FINGERPRINT = "tls_fingerprint"

@dataclass
class ProxyInfo:
    """Proxy information structure"""
    host: str
    port: int
    protocol: str = "http"
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    speed: Optional[float] = None
    reliability: Optional[float] = None
    last_tested: Optional[float] = None
    
    @property
    def url(self) -> str:
        """Get proxy URL"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

class FlareSolverrClient:
    """Client for FlareSolverr bypass service"""
    
    def __init__(self, server_url: str = "http://localhost:8191"):
        self.server_url = server_url
        self.session_id = None
        
    async def create_session(self) -> bool:
        """Create a new FlareSolverr session"""
        try:
            payload = {
                "cmd": "sessions.create"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.server_url}/v1", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        self.session_id = result.get("session")
                        logger.info(f"FlareSolverr session created: {self.session_id}")
                        return True
                        
        except Exception as e:
            logger.error(f"Failed to create FlareSolverr session: {str(e)}")
            
        return False
        
    async def solve_challenge(self, url: str, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Solve CloudFlare challenge for given URL"""
        if not self.session_id:
            await self.create_session()
            
        try:
            payload = {
                "cmd": "request.get",
                "url": url,
                "session": self.session_id
            }
            
            if user_agent:
                payload["userAgent"] = user_agent
                
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.server_url}/v1", json=payload, timeout=60) as response:
                    if response.status == 200:
                        result = await response.json()
                        return {
                            "success": True,
                            "content": result.get("solution", {}).get("response", ""),
                            "cookies": result.get("solution", {}).get("cookies", []),
                            "user_agent": result.get("solution", {}).get("userAgent", "")
                        }
                        
        except Exception as e:
            logger.error(f"FlareSolverr challenge solving failed: {str(e)}")
            
        return {"success": False, "error": "Failed to solve challenge"}
        
    async def cleanup(self):
        """Cleanup FlareSolverr session"""
        if self.session_id:
            try:
                payload = {
                    "cmd": "sessions.destroy",
                    "session": self.session_id
                }
                
                async with aiohttp.ClientSession() as session:
                    await session.post(f"{self.server_url}/v1", json=payload)
                    
            except Exception as e:
                logger.error(f"Failed to cleanup FlareSolverr session: {str(e)}")

class ProxyManager:
    """Advanced proxy management system"""
    
    def __init__(self):
        self.proxy_pool: List[ProxyInfo] = []
        self.working_proxies: List[ProxyInfo] = []
        self.blacklisted_proxies: List[str] = []
        self.current_proxy_index = 0
        
    async def initialize(self):
        """Initialize proxy manager"""
        logger.info("Initializing Proxy Manager")
        await self._load_proxy_sources()
        await self._test_proxies()
        
    async def _load_proxy_sources(self):
        """Load proxies from multiple sources"""
        # Free proxy sources
        await self._load_free_proxies()
        
        # Add high-quality proxies if configured
        await self._load_premium_proxies()
        
    async def _load_free_proxies(self):
        """Load free proxies from public sources"""
        sources = [
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
        ]
        
        for source in sources:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(source, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            proxies = self._parse_proxy_list(content)
                            self.proxy_pool.extend(proxies)
                            logger.info(f"Loaded {len(proxies)} proxies from {source}")
                            
            except Exception as e:
                logger.error(f"Failed to load proxies from {source}: {str(e)}")
                
    async def _load_premium_proxies(self):
        """Load premium proxies if configured"""
        # This would integrate with premium proxy services
        # Example: ProxyMesh, Bright Data, etc.
        pass
        
    def _parse_proxy_list(self, content: str) -> List[ProxyInfo]:
        """Parse proxy list content"""
        proxies = []
        
        for line in content.strip().split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                try:
                    parts = line.split(':')
                    if len(parts) >= 2:
                        host = parts[0].strip()
                        port = int(parts[1].strip())
                        proxies.append(ProxyInfo(host=host, port=port))
                        
                except ValueError:
                    continue
                    
        return proxies
        
    async def _test_proxies(self):
        """Test proxies for functionality"""
        logger.info(f"Testing {len(self.proxy_pool)} proxies")
        
        # Test in batches to avoid overwhelming
        batch_size = 20
        working_count = 0
        
        for i in range(0, len(self.proxy_pool), batch_size):
            batch = self.proxy_pool[i:i+batch_size]
            tasks = [self._test_proxy(proxy) for proxy in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for j, result in enumerate(results):
                if result is True:
                    batch[j].last_tested = time.time()
                    batch[j].reliability = 1.0
                    self.working_proxies.append(batch[j])
                    working_count += 1
                    
        logger.info(f"Found {working_count} working proxies")
        
    async def _test_proxy(self, proxy: ProxyInfo) -> bool:
        """Test individual proxy"""
        try:
            proxy_url = proxy.url
            
            async with aiohttp.ClientSession(
                connector=aiohttp.ProxyConnector.from_url(proxy_url),
                timeout=aiohttp.ClientTimeout(total=10)
            ) as session:
                async with session.get("http://httpbin.org/ip") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("origin") != ""
                        
        except Exception:
            pass
            
        return False
        
    def get_proxy(self) -> Optional[ProxyInfo]:
        """Get next working proxy"""
        if not self.working_proxies:
            return None
            
        proxy = self.working_proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.working_proxies)
        return proxy
        
    def blacklist_proxy(self, proxy: ProxyInfo):
        """Blacklist a non-working proxy"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        if proxy_key not in self.blacklisted_proxies:
            self.blacklisted_proxies.append(proxy_key)
            
        # Remove from working proxies
        self.working_proxies = [p for p in self.working_proxies if f"{p.host}:{p.port}" != proxy_key]

class StealthHeaderManager:
    """Manages stealth headers and fingerprints"""
    
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
        ]
        
        self.accept_languages = [
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "sv-SE,sv;q=0.9,en;q=0.8",
            "de-DE,de;q=0.9,en;q=0.8",
            "fr-FR,fr;q=0.9,en;q=0.8"
        ]
        
    def get_stealth_headers(self, url: str) -> Dict[str, str]:
        """Generate stealth headers for request"""
        parsed_url = urlparse(url)
        
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": random.choice(self.accept_languages),
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
        
        if parsed_url.hostname:
            headers["Host"] = parsed_url.hostname
            
        return headers

class CaptchaSolver:
    """CAPTCHA solving integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.services = {
            "2captcha": "https://2captcha.com",
            "anticaptcha": "https://api.anti-captcha.com",
            "deathbycaptcha": "http://api.dbcapi.me"
        }
        
    async def solve_captcha(self, captcha_type: str, captcha_data: Any) -> Dict[str, Any]:
        """Solve CAPTCHA using available services"""
        if not self.api_key:
            return {"success": False, "error": "No CAPTCHA API key configured"}
            
        try:
            if captcha_type == "recaptcha_v2":
                return await self._solve_recaptcha_v2(captcha_data)
            elif captcha_type == "recaptcha_v3":
                return await self._solve_recaptcha_v3(captcha_data)
            elif captcha_type == "hcaptcha":
                return await self._solve_hcaptcha(captcha_data)
            elif captcha_type == "cloudflare_turnstile":
                return await self._solve_turnstile(captcha_data)
                
        except Exception as e:
            logger.error(f"CAPTCHA solving failed: {str(e)}")
            
        return {"success": False, "error": "Unsupported CAPTCHA type or solving failed"}
        
    async def _solve_recaptcha_v2(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve reCAPTCHA v2"""
        # Implementation for reCAPTCHA v2 solving
        return {"success": False, "error": "Not implemented"}
        
    async def _solve_recaptcha_v3(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve reCAPTCHA v3"""
        # Implementation for reCAPTCHA v3 solving
        return {"success": False, "error": "Not implemented"}
        
    async def _solve_hcaptcha(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve hCaptcha"""
        # Implementation for hCaptcha solving
        return {"success": False, "error": "Not implemented"}
        
    async def _solve_turnstile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve Cloudflare Turnstile"""
        # Implementation for Turnstile solving
        return {"success": False, "error": "Not implemented"}

class BypassLayer:
    """
    Main bypass layer coordinator
    Manages all bypass methods and provides unified interface
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize components
        self.flaresolverr = None
        self.proxy_manager = None
        self.stealth_headers = StealthHeaderManager()
        self.captcha_solver = None
        
        # State tracking
        self.active_bypasses = {}
        self.bypass_stats = {
            "requests_processed": 0,
            "bypasses_successful": 0,
            "captchas_solved": 0,
            "proxies_rotated": 0
        }
        
    async def initialize(self):
        """Initialize bypass layer"""
        self.logger.info("🛡️ Initializing Bypass Layer")
        
        # Initialize FlareSolverr if enabled
        if self.config.enable_bypass:
            self.flaresolverr = FlareSolverrClient()
            
        # Initialize proxy manager if enabled
        if self.config.proxy_rotation:
            self.proxy_manager = ProxyManager()
            await self.proxy_manager.initialize()
            
        # Initialize CAPTCHA solver if enabled
        if self.config.enable_captcha_solving:
            # Get API key from config or environment
            api_key = getattr(self.config, 'captcha_api_key', None)
            self.captcha_solver = CaptchaSolver(api_key)
            
        self.logger.info("✅ Bypass Layer initialized successfully")
        
    async def process_request(self, url: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """
        Process request with appropriate bypass methods
        """
        self.bypass_stats["requests_processed"] += 1
        
        # Determine required bypass methods
        bypass_methods = await self._analyze_target(url)
        
        # Apply bypass methods
        request_config = await self._apply_bypasses(url, method, bypass_methods, **kwargs)
        
        return request_config
        
    async def _analyze_target(self, url: str) -> List[BypassMethod]:
        """Analyze target to determine required bypass methods"""
        bypass_methods = []
        
        # Always use stealth headers
        bypass_methods.append(BypassMethod.STEALTH_HEADERS)
        bypass_methods.append(BypassMethod.USER_AGENT_ROTATION)
        
        # Use proxy rotation if enabled
        if self.config.proxy_rotation and self.proxy_manager:
            bypass_methods.append(BypassMethod.PROXY_ROTATION)
            
        # Add rate limiting
        bypass_methods.append(BypassMethod.RATE_LIMITING)
        
        # Check if domain likely uses CloudFlare
        domain = urlparse(url).hostname
        if domain and await self._is_cloudflare_protected(domain):
            bypass_methods.append(BypassMethod.FLARESOLVERR)
            
        return bypass_methods
        
    async def _is_cloudflare_protected(self, domain: str) -> bool:
        """Check if domain is CloudFlare protected"""
        try:
            # Simple check - look for CloudFlare headers
            async with aiohttp.ClientSession() as session:
                async with session.head(f"http://{domain}", timeout=5) as response:
                    headers = response.headers
                    cf_indicators = [
                        "cf-ray", "cf-cache-status", "server"
                    ]
                    
                    for indicator in cf_indicators:
                        if indicator in headers:
                            if "cloudflare" in str(headers[indicator]).lower():
                                return True
                                
        except Exception:
            pass
            
        return False
        
    async def _apply_bypasses(self, url: str, method: str, bypass_methods: List[BypassMethod], **kwargs) -> Dict[str, Any]:
        """Apply selected bypass methods to request"""
        request_config = {
            "url": url,
            "method": method,
            "headers": {},
            "proxy": None,
            "timeout": 30,
            "allow_redirects": True
        }
        
        # Apply each bypass method
        for bypass_method in bypass_methods:
            try:
                if bypass_method == BypassMethod.STEALTH_HEADERS:
                    headers = self.stealth_headers.get_stealth_headers(url)
                    request_config["headers"].update(headers)
                    
                elif bypass_method == BypassMethod.PROXY_ROTATION:
                    if self.proxy_manager:
                        proxy = self.proxy_manager.get_proxy()
                        if proxy:
                            request_config["proxy"] = proxy.url
                            self.bypass_stats["proxies_rotated"] += 1
                            
                elif bypass_method == BypassMethod.RATE_LIMITING:
                    # Add random delay to avoid rate limiting
                    delay = random.uniform(1, 3)
                    await asyncio.sleep(delay)
                    
                elif bypass_method == BypassMethod.FLARESOLVERR:
                    if self.flaresolverr:
                        # Use FlareSolverr for CloudFlare bypass
                        result = await self.flaresolverr.solve_challenge(url)
                        if result.get("success"):
                            request_config["flaresolverr_result"] = result
                            self.bypass_stats["bypasses_successful"] += 1
                            
            except Exception as e:
                self.logger.error(f"Error applying bypass method {bypass_method}: {str(e)}")
                
        return request_config
        
    async def handle_captcha(self, captcha_type: str, captcha_data: Any) -> Dict[str, Any]:
        """Handle CAPTCHA challenges"""
        if not self.captcha_solver:
            return {"success": False, "error": "CAPTCHA solver not initialized"}
            
        result = await self.captcha_solver.solve_captcha(captcha_type, captcha_data)
        if result.get("success"):
            self.bypass_stats["captchas_solved"] += 1
            
        return result
        
    async def report_proxy_failure(self, proxy_url: str):
        """Report proxy failure for blacklisting"""
        if self.proxy_manager:
            # Find and blacklist the proxy
            for proxy in self.proxy_manager.working_proxies:
                if proxy.url == proxy_url:
                    self.proxy_manager.blacklist_proxy(proxy)
                    break
                    
    async def get_status(self) -> Dict[str, Any]:
        """Get bypass layer status"""
        status = {
            "healthy": True,
            "stats": self.bypass_stats.copy(),
            "components": {
                "flaresolverr": self.flaresolverr is not None,
                "proxy_manager": self.proxy_manager is not None,
                "captcha_solver": self.captcha_solver is not None
            }
        }
        
        if self.proxy_manager:
            status["proxy_stats"] = {
                "total_proxies": len(self.proxy_manager.proxy_pool),
                "working_proxies": len(self.proxy_manager.working_proxies),
                "blacklisted_proxies": len(self.proxy_manager.blacklisted_proxies)
            }
            
        return status
        
    async def cleanup(self):
        """Cleanup bypass layer resources"""
        self.logger.info("🧹 Cleaning up Bypass Layer")
        
        if self.flaresolverr:
            await self.flaresolverr.cleanup()
            
        # Clear proxy pools
        if self.proxy_manager:
            self.proxy_manager.proxy_pool.clear()
            self.proxy_manager.working_proxies.clear()
            
        self.logger.info("✅ Bypass Layer cleanup completed")
