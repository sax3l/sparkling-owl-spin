#!/usr/bin/env python3
"""
Enhanced Cloudflare Bypass System för Sparkling-Owl-Spin
Integrerat system med FlareSolverr, CloudScraper, Undetected Chrome och mer
"""

import logging
import asyncio
import aiohttp
import json
import time
import random
import subprocess
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import re
from pathlib import Path
import hashlib
import tempfile

# Import alla tillgängliga bypass-bibliotek
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    UC_AVAILABLE = True
except ImportError:
    UC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from curl_cffi import requests as cf_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

logger = logging.getLogger(__name__)

class BypassMethod(Enum):
    """Enhanced Cloudflare bypass methods"""
    FLARESOLVERR = "flaresolverr"
    CLOUDSCRAPER_V3 = "cloudscraper_v3"
    UNDETECTED_CHROME = "undetected_chrome"
    CURL_CFFI = "curl_cffi"
    TLS_CLIENT = "tls_client"
    TURNSTILE_SOLVER = "turnstile_solver"
    HEADERS_ROTATION = "headers_rotation"
    SESSION_RECYCLING = "session_recycling"
    AUTO_ADAPTIVE = "auto_adaptive"

class ProtectionLevel(Enum):
    """Cloudflare protection levels"""
    LOW = "low"          # Basic protection
    MEDIUM = "medium"    # JavaScript challenge
    HIGH = "high"        # CAPTCHA required
    EXTREME = "extreme"  # Multiple challenges

@dataclass
class BypassConfig:
    """Enhanced configuration för bypass-försök"""
    method: BypassMethod
    timeout: int = 60
    max_retries: int = 5
    delay_between_retries: float = 3.0
    custom_headers: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    session_reuse: bool = True
    auto_retry: bool = True
    protection_level: Optional[ProtectionLevel] = None
    solve_captcha: bool = False
    captcha_api_key: Optional[str] = None

@dataclass
class BypassResult:
    """Enhanced result från bypass-försök"""
    success: bool
    method_used: BypassMethod
    protection_detected: Optional[ProtectionLevel] = None
    response_content: Optional[str] = None
    cookies: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    status_code: Optional[int] = None
    execution_time: Optional[float] = None
    attempts_made: int = 0
    challenges_solved: List[str] = None
    error_message: Optional[str] = None
    session_id: Optional[str] = None

class EnhancedCloudflareBypassAdapter:
    """Enhanced Cloudflare Bypass-adapter med alla integrerade tekniker"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.initialized = False
        self.session: Optional[aiohttp.ClientSession] = None
        
        # FlareSolverr configuration
        self.flaresolverr_url = "http://localhost:8191"
        self.flaresolverr_available = False
        
        # Session management för återanvändning
        self.active_sessions = {}
        self.session_stats = {}
        
        # User agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]
        
        # TLS fingerprints för rotation
        self.tls_fingerprints = [
            "chrome_120",
            "chrome_121", 
            "firefox_122",
            "safari_17"
        ]
        
        # Penetrationstestning disclaimer
        self.authorized_domains = set()
        
        # Statistik
        self.stats = {
            "total_attempts": 0,
            "successful_bypasses": 0,
            "failed_attempts": 0,
            "by_method": {},
            "by_protection_level": {},
            "avg_execution_time": 0.0,
            "session_reuse_rate": 0.0
        }
        
    async def initialize(self):
        """Initialize Enhanced Cloudflare Bypass adapter"""
        try:
            logger.info("🔥 Initializing Enhanced Cloudflare Bypass Adapter (Authorized Pentest Only)")
            
            # Skapa aiohttp session med enhanced konfiguration
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=10,
                ttl_dns_cache=300,
                use_dns_cache=True,
                keepalive_timeout=30,
                ssl=False  # Vi hanterar TLS manuellt
            )
            
            timeout = aiohttp.ClientTimeout(total=120, connect=30)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            
            # Kontrollera FlareSolverr
            await self._check_flaresolverr_availability()
            
            # Initiera statistik för alla metoder
            for method in BypassMethod:
                self.stats["by_method"][method.value] = {
                    "attempts": 0,
                    "successes": 0,
                    "failures": 0,
                    "avg_time": 0.0
                }
                
            for level in ProtectionLevel:
                self.stats["by_protection_level"][level.value] = {
                    "detected": 0,
                    "bypassed": 0
                }
                
            # Logga tillgängliga bibliotek
            available_libs = []
            if CLOUDSCRAPER_AVAILABLE:
                available_libs.append("CloudScraper v3.0+")
            if UC_AVAILABLE:
                available_libs.append("Undetected ChromeDriver")
            if CURL_CFFI_AVAILABLE:
                available_libs.append("curl_cffi")
            if self.flaresolverr_available:
                available_libs.append("FlareSolverr")
                
            logger.info(f"📋 Available bypass libraries: {', '.join(available_libs)}")
            
            self.initialized = True
            logger.info("✅ Enhanced Cloudflare Bypass Adapter initialized för penetrationstestning")
            logger.warning("⚠️ ENDAST FÖR PENETRATIONSTESTNING AV EGNA SERVRAR")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Cloudflare Bypass: {str(e)}")
            self.initialized = True  # Continue with limited functionality
            
    async def _check_flaresolverr_availability(self):
        """Kontrollera om FlareSolverr är tillgängligt"""
        try:
            async with self.session.get(f"{self.flaresolverr_url}/v1", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    self.flaresolverr_available = True
                    logger.info("✅ FlareSolverr is available")
                else:
                    logger.warning("⚠️ FlareSolverr responded with non-200 status")
        except Exception as e:
            logger.warning(f"⚠️ FlareSolverr not available: {str(e)}")
            
    def add_authorized_domain(self, domain: str):
        """Lägg till auktoriserad domän för penetrationstestning"""
        self.authorized_domains.add(domain.lower())
        logger.info(f"✅ Added authorized domain för Cloudflare bypass testing: {domain}")
        
    def _is_domain_authorized(self, url: str) -> bool:
        """Kontrollera om domän är auktoriserad för testning"""
        from urllib.parse import urlparse
        
        domain = urlparse(url).netloc.lower()
        
        if domain in self.authorized_domains:
            return True
            
        for auth_domain in self.authorized_domains:
            if domain.endswith(f".{auth_domain}"):
                return True
                
        return False
        
    async def bypass_cloudflare(self, url: str, config: Optional[BypassConfig] = None) -> BypassResult:
        """Enhanced Cloudflare bypass med automatisk metodval"""
        
        if not self.initialized:
            await self.initialize()
            
        # Säkerhetskontroll
        if not self._is_domain_authorized(url):
            error_msg = f"🚫 Domain not authorized för Cloudflare bypass testing: {url}"
            logger.error(error_msg)
            return BypassResult(
                success=False,
                method_used=BypassMethod.AUTO_ADAPTIVE,
                error_message=error_msg
            )
            
        if not config:
            config = BypassConfig(method=BypassMethod.AUTO_ADAPTIVE)
            
        self.stats["total_attempts"] += 1
        start_time = time.time()
        
        try:
            # Auto-adaptive method selection
            if config.method == BypassMethod.AUTO_ADAPTIVE:
                result = await self._auto_adaptive_bypass(url, config)
            else:
                result = await self._single_method_bypass(url, config)
                
            # Uppdatera statistik
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            method_stats = self.stats["by_method"][result.method_used.value]
            method_stats["attempts"] += 1
            
            if result.success:
                self.stats["successful_bypasses"] += 1
                method_stats["successes"] += 1
                
                if result.protection_detected:
                    self.stats["by_protection_level"][result.protection_detected.value]["bypassed"] += 1
                    
                logger.info(f"✅ Cloudflare bypass successful med {result.method_used.value} ({execution_time:.2f}s)")
            else:
                self.stats["failed_attempts"] += 1
                method_stats["failures"] += 1
                logger.warning(f"❌ Cloudflare bypass failed med {result.method_used.value}: {result.error_message}")
                
            # Uppdatera genomsnittlig execution time
            method_stats["avg_time"] = (
                (method_stats["avg_time"] * (method_stats["attempts"] - 1) + execution_time) 
                / method_stats["attempts"]
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Cloudflare bypass error: {str(e)}")
            return BypassResult(
                success=False,
                method_used=config.method,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )
            
    async def _auto_adaptive_bypass(self, url: str, config: BypassConfig) -> BypassResult:
        """Automatisk adaptiv bypass som väljer bästa metoden"""
        
        # Detektera protection level först
        protection_level = await self._detect_protection_level(url)
        
        # Välj metoder baserat på protection level
        if protection_level == ProtectionLevel.LOW:
            methods = [BypassMethod.CLOUDSCRAPER_V3, BypassMethod.CURL_CFFI, BypassMethod.HEADERS_ROTATION]
        elif protection_level == ProtectionLevel.MEDIUM:
            methods = [BypassMethod.UNDETECTED_CHROME, BypassMethod.FLARESOLVERR, BypassMethod.CLOUDSCRAPER_V3]
        elif protection_level == ProtectionLevel.HIGH:
            methods = [BypassMethod.FLARESOLVERR, BypassMethod.UNDETECTED_CHROME, BypassMethod.TURNSTILE_SOLVER]
        else:  # EXTREME
            methods = [BypassMethod.FLARESOLVERR, BypassMethod.TURNSTILE_SOLVER, BypassMethod.SESSION_RECYCLING]
            
        # Filtrera metoder baserat på tillgänglighet
        available_methods = []
        for method in methods:
            if self._is_method_available(method):
                available_methods.append(method)
                
        if not available_methods:
            available_methods = [BypassMethod.HEADERS_ROTATION]  # Fallback
            
        # Prova metoder i ordning
        for method in available_methods:
            try:
                method_config = BypassConfig(
                    method=method,
                    timeout=config.timeout,
                    max_retries=2,  # Färre retries per metod i auto mode
                    delay_between_retries=config.delay_between_retries,
                    custom_headers=config.custom_headers,
                    proxy=config.proxy,
                    user_agent=config.user_agent,
                    protection_level=protection_level
                )
                
                result = await self._single_method_bypass(url, method_config)
                
                if result.success:
                    result.protection_detected = protection_level
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Method {method.value} failed in auto-adaptive mode: {str(e)}")
                continue
                
        # Alla metoder misslyckades
        return BypassResult(
            success=False,
            method_used=BypassMethod.AUTO_ADAPTIVE,
            protection_detected=protection_level,
            error_message="All available methods failed in auto-adaptive mode"
        )
        
    async def _detect_protection_level(self, url: str) -> ProtectionLevel:
        """Detektera Cloudflare protection level"""
        try:
            # Gör en snabb initial request för att detektera protection
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                content = await response.text()
                
                # Analysera response för att identifiera protection level
                if "turnstile" in content.lower() or "captcha" in content.lower():
                    self.stats["by_protection_level"][ProtectionLevel.HIGH.value]["detected"] += 1
                    return ProtectionLevel.HIGH
                elif "challenge-form" in content or "cf-challenge" in content:
                    self.stats["by_protection_level"][ProtectionLevel.MEDIUM.value]["detected"] += 1
                    return ProtectionLevel.MEDIUM
                elif response.status == 403 or "cloudflare" in content.lower():
                    self.stats["by_protection_level"][ProtectionLevel.LOW.value]["detected"] += 1
                    return ProtectionLevel.LOW
                else:
                    return ProtectionLevel.LOW
                    
        except Exception:
            # Om vi inte kan detektera, anta medium level
            return ProtectionLevel.MEDIUM
            
    def _is_method_available(self, method: BypassMethod) -> bool:
        """Kontrollera om en bypass-metod är tillgänglig"""
        availability_map = {
            BypassMethod.FLARESOLVERR: self.flaresolverr_available,
            BypassMethod.CLOUDSCRAPER_V3: CLOUDSCRAPER_AVAILABLE,
            BypassMethod.UNDETECTED_CHROME: UC_AVAILABLE,
            BypassMethod.CURL_CFFI: CURL_CFFI_AVAILABLE,
            BypassMethod.HEADERS_ROTATION: True,  # Always available
            BypassMethod.SESSION_RECYCLING: True,  # Always available
            BypassMethod.TLS_CLIENT: CURL_CFFI_AVAILABLE,
            BypassMethod.TURNSTILE_SOLVER: self.flaresolverr_available,
            BypassMethod.AUTO_ADAPTIVE: True
        }
        
        return availability_map.get(method, False)
        
    async def _single_method_bypass(self, url: str, config: BypassConfig) -> BypassResult:
        """Utför bypass med en specifik metod"""
        
        method_map = {
            BypassMethod.FLARESOLVERR: self._bypass_flaresolverr,
            BypassMethod.CLOUDSCRAPER_V3: self._bypass_cloudscraper_v3,
            BypassMethod.UNDETECTED_CHROME: self._bypass_undetected_chrome,
            BypassMethod.CURL_CFFI: self._bypass_curl_cffi,
            BypassMethod.HEADERS_ROTATION: self._bypass_headers_rotation,
            BypassMethod.SESSION_RECYCLING: self._bypass_session_recycling,
            BypassMethod.TLS_CLIENT: self._bypass_tls_client,
            BypassMethod.TURNSTILE_SOLVER: self._bypass_turnstile_solver
        }
        
        bypass_func = method_map.get(config.method)
        if not bypass_func:
            return BypassResult(
                success=False,
                method_used=config.method,
                error_message=f"Method {config.method.value} not implemented"
            )
            
        return await bypass_func(url, config)
        
    async def _bypass_flaresolverr(self, url: str, config: BypassConfig) -> BypassResult:
        """Enhanced FlareSolverr bypass"""
        if not self.flaresolverr_available:
            return BypassResult(
                success=False,
                method_used=BypassMethod.FLARESOLVERR,
                error_message="FlareSolverr not available"
            )
            
        try:
            # Skapa session om session_reuse är enabled
            session_id = None
            if config.session_reuse:
                session_id = f"session_{hashlib.md5(url.encode()).hexdigest()[:8]}"
                
                # Skapa session i FlareSolverr
                create_payload = {
                    "cmd": "sessions.create",
                    "session": session_id
                }
                
                async with self.session.post(f"{self.flaresolverr_url}/v1", 
                                           json=create_payload) as response:
                    if response.status != 200:
                        logger.warning("⚠️ Failed to create FlareSolverr session")
                        session_id = None
                        
            # Request payload
            payload = {
                "cmd": "request.get",
                "url": url,
                "maxTimeout": config.timeout * 1000
            }
            
            if session_id:
                payload["session"] = session_id
                
            if config.proxy:
                payload["proxy"] = {
                    "url": config.proxy
                }
                
            # Utför bypass
            async with self.session.post(f"{self.flaresolverr_url}/v1", json=payload) as response:
                result = await response.json()
                
                if result.get("status") == "ok" and result.get("solution"):
                    solution = result["solution"]
                    return BypassResult(
                        success=True,
                        method_used=BypassMethod.FLARESOLVERR,
                        response_content=solution.get("response"),
                        cookies=solution.get("cookies", {}),
                        headers=solution.get("headers", {}),
                        status_code=solution.get("status"),
                        session_id=session_id
                    )
                else:
                    return BypassResult(
                        success=False,
                        method_used=BypassMethod.FLARESOLVERR,
                        error_message=result.get("message", "FlareSolverr failed")
                    )
                    
        except Exception as e:
            return BypassResult(
                success=False,
                method_used=BypassMethod.FLARESOLVERR,
                error_message=f"FlareSolverr error: {str(e)}"
            )
            
    async def _bypass_cloudscraper_v3(self, url: str, config: BypassConfig) -> BypassResult:
        """Enhanced CloudScraper v3 bypass med session recycling"""
        if not CLOUDSCRAPER_AVAILABLE:
            return BypassResult(
                success=False,
                method_used=BypassMethod.CLOUDSCRAPER_V3,
                error_message="CloudScraper not available"
            )
            
        try:
            # Återanvänd session om möjligt
            session_key = f"cloudscraper_{hashlib.md5(url.encode()).hexdigest()[:8]}"
            
            if config.session_reuse and session_key in self.active_sessions:
                scraper = self.active_sessions[session_key]
                logger.debug(f"♻️ Reusing CloudScraper session: {session_key}")
            else:
                # Skapa ny scraper med enhanced konfiguration
                scraper = cloudscraper.create_scraper(
                    browser={
                        'browser': 'chrome',
                        'platform': 'windows',
                        'mobile': False,
                        'desktop': True
                    },
                    delay=config.delay_between_retries,
                    debug=False
                )
                
                # Sätt custom headers
                if config.custom_headers:
                    scraper.headers.update(config.custom_headers)
                    
                # Sätt user agent
                if config.user_agent:
                    scraper.headers['User-Agent'] = config.user_agent
                else:
                    scraper.headers['User-Agent'] = random.choice(self.user_agents)
                    
                # Konfigurera proxy
                if config.proxy:
                    scraper.proxies = {
                        'http': config.proxy,
                        'https': config.proxy
                    }
                    
                # Spara session för återanvändning
                if config.session_reuse:
                    self.active_sessions[session_key] = scraper
                    
            # Utför request med retries
            for attempt in range(config.max_retries):
                try:
                    response = scraper.get(url, timeout=config.timeout)
                    
                    # Kontrollera om vi fortfarande möter Cloudflare-utmaning
                    if self._is_cloudflare_challenge(response.text):
                        if attempt < config.max_retries - 1:
                            logger.warning(f"⚠️ CloudScraper still getting challenge, attempt {attempt + 1}")
                            await asyncio.sleep(config.delay_between_retries * (attempt + 1))
                            continue
                        else:
                            return BypassResult(
                                success=False,
                                method_used=BypassMethod.CLOUDSCRAPER_V3,
                                error_message="CloudScraper failed to solve challenge after retries"
                            )
                            
                    return BypassResult(
                        success=True,
                        method_used=BypassMethod.CLOUDSCRAPER_V3,
                        response_content=response.text,
                        cookies=dict(response.cookies),
                        headers=dict(response.headers),
                        status_code=response.status_code,
                        attempts_made=attempt + 1,
                        session_id=session_key
                    )
                    
                except cloudscraper.exceptions.CloudflareException as e:
                    if attempt < config.max_retries - 1:
                        logger.warning(f"⚠️ CloudScraper Cloudflare exception, attempt {attempt + 1}: {str(e)}")
                        await asyncio.sleep(config.delay_between_retries * (attempt + 1))
                        
                        # Refresh session on Cloudflare exception
                        if session_key in self.active_sessions:
                            del self.active_sessions[session_key]
                            scraper = cloudscraper.create_scraper()
                            self.active_sessions[session_key] = scraper
                        continue
                    else:
                        return BypassResult(
                            success=False,
                            method_used=BypassMethod.CLOUDSCRAPER_V3,
                            error_message=f"CloudScraper Cloudflare exception: {str(e)}"
                        )
                        
                except Exception as e:
                    if attempt < config.max_retries - 1:
                        logger.warning(f"⚠️ CloudScraper error, attempt {attempt + 1}: {str(e)}")
                        await asyncio.sleep(config.delay_between_retries)
                        continue
                    else:
                        return BypassResult(
                            success=False,
                            method_used=BypassMethod.CLOUDSCRAPER_V3,
                            error_message=f"CloudScraper error: {str(e)}"
                        )
                        
            return BypassResult(
                success=False,
                method_used=BypassMethod.CLOUDSCRAPER_V3,
                error_message="CloudScraper failed after all retries"
            )
            
        except Exception as e:
            return BypassResult(
                success=False,
                method_used=BypassMethod.CLOUDSCRAPER_V3,
                error_message=f"CloudScraper setup error: {str(e)}"
            )
            
    async def _bypass_undetected_chrome(self, url: str, config: BypassConfig) -> BypassResult:
        """Enhanced Undetected Chrome bypass"""
        if not UC_AVAILABLE:
            return BypassResult(
                success=False,
                method_used=BypassMethod.UNDETECTED_CHROME,
                error_message="Undetected ChromeDriver not available"
            )
            
        driver = None
        try:
            # Konfigurera Chrome options
            options = uc.ChromeOptions()
            options.add_argument("--no-first-run")
            options.add_argument("--no-service-autorun")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            options.add_argument("--window-size=1920,1080")
            
            # Proxy configuration
            if config.proxy:
                options.add_argument(f"--proxy-server={config.proxy}")
                
            # User agent
            if config.user_agent:
                options.add_argument(f"--user-agent={config.user_agent}")
            else:
                options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
                
            # Skapa driver
            driver = uc.Chrome(options=options, version_main=None)
            
            # Remove webdriver property för stealth
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigera till URL
            driver.get(url)
            
            # Vänta på att Cloudflare challenge löses
            wait = WebDriverWait(driver, config.timeout)
            
            # Vänta tills vi inte längre ser Cloudflare challenge
            for attempt in range(config.max_retries):
                try:
                    # Kontrollera om vi fortfarande har Cloudflare challenge
                    page_source = driver.page_source
                    
                    if not self._is_cloudflare_challenge(page_source):
                        # Success! 
                        cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
                        
                        return BypassResult(
                            success=True,
                            method_used=BypassMethod.UNDETECTED_CHROME,
                            response_content=page_source,
                            cookies=cookies,
                            status_code=200,  # Assume success
                            attempts_made=attempt + 1
                        )
                        
                    # Vänta lite och försök igen
                    await asyncio.sleep(config.delay_between_retries)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Undetected Chrome wait error, attempt {attempt + 1}: {str(e)}")
                    if attempt < config.max_retries - 1:
                        await asyncio.sleep(config.delay_between_retries)
                        continue
                    else:
                        raise e
                        
            return BypassResult(
                success=False,
                method_used=BypassMethod.UNDETECTED_CHROME,
                error_message="Undetected Chrome failed to solve challenge within timeout"
            )
            
        except Exception as e:
            return BypassResult(
                success=False,
                method_used=BypassMethod.UNDETECTED_CHROME,
                error_message=f"Undetected Chrome error: {str(e)}"
            )
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                    
    async def _bypass_curl_cffi(self, url: str, config: BypassConfig) -> BypassResult:
        """curl_cffi bypass med TLS impersonation"""
        if not CURL_CFFI_AVAILABLE:
            return BypassResult(
                success=False,
                method_used=BypassMethod.CURL_CFFI,
                error_message="curl_cffi not available"
            )
            
        try:
            # Välj random TLS fingerprint
            impersonate = random.choice(['chrome110', 'chrome120', 'firefox110', 'safari15_5'])
            
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            if config.custom_headers:
                headers.update(config.custom_headers)
                
            if config.user_agent:
                headers['User-Agent'] = config.user_agent
                
            # Utför request
            response = cf_requests.get(
                url,
                headers=headers,
                timeout=config.timeout,
                proxies={'http': config.proxy, 'https': config.proxy} if config.proxy else None,
                impersonate=impersonate
            )
            
            # Kontrollera om vi möter Cloudflare challenge
            if self._is_cloudflare_challenge(response.text):
                return BypassResult(
                    success=False,
                    method_used=BypassMethod.CURL_CFFI,
                    error_message="curl_cffi encountered Cloudflare challenge"
                )
                
            return BypassResult(
                success=True,
                method_used=BypassMethod.CURL_CFFI,
                response_content=response.text,
                cookies=dict(response.cookies),
                headers=dict(response.headers),
                status_code=response.status_code
            )
            
        except Exception as e:
            return BypassResult(
                success=False,
                method_used=BypassMethod.CURL_CFFI,
                error_message=f"curl_cffi error: {str(e)}"
            )
            
    async def _bypass_headers_rotation(self, url: str, config: BypassConfig) -> BypassResult:
        """Headers rotation bypass"""
        
        # Rotera genom olika header kombinationer
        header_sets = [
            {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none'
            },
            {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        ]
        
        try:
            for attempt, headers in enumerate(header_sets):
                if config.custom_headers:
                    headers.update(config.custom_headers)
                    
                async with self.session.get(url, headers=headers) as response:
                    content = await response.text()
                    
                    if not self._is_cloudflare_challenge(content) and response.status == 200:
                        return BypassResult(
                            success=True,
                            method_used=BypassMethod.HEADERS_ROTATION,
                            response_content=content,
                            cookies=dict(response.cookies) if response.cookies else {},
                            headers=dict(response.headers),
                            status_code=response.status,
                            attempts_made=attempt + 1
                        )
                        
                await asyncio.sleep(config.delay_between_retries)
                
            return BypassResult(
                success=False,
                method_used=BypassMethod.HEADERS_ROTATION,
                error_message="Headers rotation failed to bypass Cloudflare"
            )
            
        except Exception as e:
            return BypassResult(
                success=False,
                method_used=BypassMethod.HEADERS_ROTATION,
                error_message=f"Headers rotation error: {str(e)}"
            )
            
    async def _bypass_session_recycling(self, url: str, config: BypassConfig) -> BypassResult:
        """Session recycling bypass"""
        # Implementation för session recycling
        return BypassResult(
            success=False,
            method_used=BypassMethod.SESSION_RECYCLING,
            error_message="Session recycling not yet implemented"
        )
        
    async def _bypass_tls_client(self, url: str, config: BypassConfig) -> BypassResult:
        """TLS Client bypass"""
        # Implementation för TLS client
        return BypassResult(
            success=False,
            method_used=BypassMethod.TLS_CLIENT,
            error_message="TLS Client not yet implemented"
        )
        
    async def _bypass_turnstile_solver(self, url: str, config: BypassConfig) -> BypassResult:
        """Turnstile solver bypass"""
        # Implementation för Turnstile solver
        return BypassResult(
            success=False,
            method_used=BypassMethod.TURNSTILE_SOLVER,
            error_message="Turnstile solver not yet implemented"
        )
        
    def _is_cloudflare_challenge(self, content: str) -> bool:
        """Detektera om response innehåller Cloudflare challenge"""
        challenge_indicators = [
            "cf-challenge",
            "cf-browser-verification",
            "challenge-form",
            "jschl-answer",
            "cf-captcha-container",
            "cloudflare-static",
            "cf-wrapper",
            "turnstile",
            "Please enable JavaScript and cookies",
            "DDoS protection by Cloudflare"
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in challenge_indicators)
        
    def get_cloudflare_statistics(self) -> Dict[str, Any]:
        """Hämta Cloudflare bypass-statistik"""
        return {
            "total_attempts": self.stats["total_attempts"],
            "successful_bypasses": self.stats["successful_bypasses"],
            "failed_attempts": self.stats["failed_attempts"],
            "success_rate": (
                self.stats["successful_bypasses"] / max(1, self.stats["total_attempts"])
            ) * 100,
            "by_method": self.stats["by_method"],
            "by_protection_level": self.stats["by_protection_level"],
            "avg_execution_time": self.stats["avg_execution_time"],
            "session_reuse_rate": self.stats["session_reuse_rate"],
            "authorized_domains": list(self.authorized_domains),
            "available_methods": [
                method.value for method in BypassMethod
                if self._is_method_available(method)
            ],
            "flaresolverr_available": self.flaresolverr_available,
            "active_sessions": len(self.active_sessions)
        }
        
    async def cleanup(self):
        """Cleanup Enhanced Cloudflare Bypass adapter"""
        logger.info("🧹 Cleaning up Enhanced Cloudflare Bypass Adapter")
        
        # Cleanup active sessions
        for session_key, session in list(self.active_sessions.items()):
            try:
                if hasattr(session, 'close'):
                    session.close()
            except:
                pass
                
        self.active_sessions.clear()
        
        if self.session:
            await self.session.close()
            
        self.authorized_domains.clear()
        self.stats.clear()
        self.initialized = False
        logger.info("✅ Enhanced Cloudflare Bypass Adapter cleanup completed")

# Alias för pyramid architecture compatibility
CloudflareBypass = EnhancedCloudflareBypassAdapter
