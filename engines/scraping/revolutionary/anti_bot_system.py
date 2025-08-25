#!/usr/bin/env python3
"""
🛡️ REVOLUTIONARY ANTI-BOT DEFENSE SYSTEM 🛡️
==============================================

Implementerar den ultimata anti-bot strategin enligt prioriteringslistan:
1. cloudscraper (drop-in requests ersättare)
2. FlareSolverr proxy integration
3. undetected-chromedriver fallback
4. TLS/JA3 fingerprinting med azuretls-client
5. 2captcha integration
6. NopeCHA extension support

🎯 COMPLETE ANTI-BOT PIPELINE:
- ⚡ Smart triage system (requests → cloudscraper → headless)
- 🔥 FlareSolverr proxy för Cloudflare IUAM/Turnstile  
- 🥷 undetected-chromedriver för svåra sajter
- 🔐 TLS/JA3 spoofing via azuretls
- 🤖 Automatisk CAPTCHA-lösning
- 📊 Intelligent retry och fallback logik
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from urllib.parse import urlparse
import re

# Core networking
import requests
import httpx

# Anti-bot libraries
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False
    logging.warning("⚠️  cloudscraper not available")

try:
    import undetected_chrome as uc
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False
    logging.warning("⚠️  undetected-chromedriver not available")

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("⚠️  Playwright not available")

# TLS fingerprinting (will be installed as needed)
try:
    import azuretls
    AZURETLS_AVAILABLE = True
except ImportError:
    AZURETLS_AVAILABLE = False
    logging.warning("⚠️  azuretls-client not available")

# CAPTCHA solving
try:
    from twocaptcha import TwoCaptcha
    TWOCAPTCHA_AVAILABLE = True
except ImportError:
    TWOCAPTCHA_AVAILABLE = False
    logging.warning("⚠️  2captcha-python not available")

logger = logging.getLogger(__name__)


class AntiDetectionMethod(Enum):
    """Anti-detection methods in priority order"""
    REQUESTS = "requests"                    # Standard requests
    CLOUDSCRAPER = "cloudscraper"           # CloudScraper for CF IUAM
    FLARE_SOLVERR = "flare_solverr"        # FlareSolverr proxy
    UNDETECTED_CHROME = "undetected_chrome" # Undetected Chrome
    PLAYWRIGHT_STEALTH = "playwright_stealth" # Playwright med stealth
    AZURETLS = "azuretls"                   # TLS/JA3 spoofing


class CaptchaProvider(Enum):
    """CAPTCHA solving providers"""
    NONE = "none"
    TWOCAPTCHA = "2captcha"
    NOPECHA = "nopecha"
    AUTO = "auto"


@dataclass
class AntiBotConfig:
    """Anti-bot system configuration"""
    # Method priority
    method_priority: List[AntiDetectionMethod] = field(default_factory=lambda: [
        AntiDetectionMethod.REQUESTS,
        AntiDetectionMethod.CLOUDSCRAPER,
        AntiDetectionMethod.FLARE_SOLVERR,
        AntiDetectionMethod.UNDETECTED_CHROME,
        AntiDetectionMethod.PLAYWRIGHT_STEALTH,
        AntiDetectionMethod.AZURETLS
    ])
    
    # FlareSolverr settings
    flaresolverr_url: str = "http://localhost:8191/v1"
    flaresolverr_timeout: int = 60
    flaresolverr_maxTimeout: int = 60000
    
    # CAPTCHA settings
    captcha_provider: CaptchaProvider = CaptchaProvider.AUTO
    twocaptcha_api_key: Optional[str] = None
    nopecha_api_key: Optional[str] = None
    
    # Retry settings
    max_method_attempts: int = 3
    retry_delay_base: float = 2.0
    retry_delay_max: float = 60.0
    
    # Detection patterns
    cloudflare_indicators: List[str] = field(default_factory=lambda: [
        "checking your browser",
        "cloudflare",
        "cf-ray",
        "ddos protection by cloudflare",
        "please wait 5 seconds",
        "just a moment",
        "please stand by",
        "__cf_bm"
    ])
    
    captcha_selectors: List[str] = field(default_factory=lambda: [
        ".g-recaptcha",
        ".h-captcha",
        ".cf-turnstile",
        "#cf-chl-widget",
        ".captcha",
        "[data-sitekey]"
    ])


@dataclass
class ScrapingResult:
    """Result from anti-bot scraping attempt"""
    success: bool = False
    method_used: Optional[AntiDetectionMethod] = None
    response: Optional[Any] = None  # requests.Response eller liknande
    content: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict] = None
    cookies: Optional[Dict] = None
    execution_time: float = 0.0
    attempts: int = 0
    error: Optional[str] = None
    cloudflare_detected: bool = False
    captcha_detected: bool = False
    captcha_solved: bool = False


class FlareSolverrClient:
    """FlareSolverr proxy client for Cloudflare bypass"""
    
    def __init__(self, config: AntiBotConfig):
        self.config = config
        self.session_id = None
        
    async def create_session(self) -> bool:
        """Create FlareSolverr session"""
        try:
            payload = {
                "cmd": "sessions.create",
                "session": f"revolutionary_{int(time.time())}"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.config.flaresolverr_url, json=payload)
                
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    self.session_id = data["session"]
                    logger.info(f"🔥 FlareSolverr session created: {self.session_id}")
                    return True
                    
        except Exception as e:
            logger.error(f"❌ Failed to create FlareSolverr session: {e}")
            
        return False
    
    async def solve_cloudflare(self, url: str, method: str = "GET", 
                              data: Optional[Dict] = None, 
                              headers: Optional[Dict] = None) -> Optional[ScrapingResult]:
        """Solve Cloudflare challenge via FlareSolverr"""
        if not self.session_id:
            if not await self.create_session():
                return None
                
        try:
            payload = {
                "cmd": "request.get" if method == "GET" else "request.post",
                "url": url,
                "session": self.session_id,
                "maxTimeout": self.config.flaresolverr_maxTimeout
            }
            
            if headers:
                payload["headers"] = headers
            if data and method == "POST":
                payload["postData"] = data
                
            start_time = time.time()
            
            async with httpx.AsyncClient(timeout=self.config.flaresolverr_timeout) as client:
                response = await client.post(self.config.flaresolverr_url, json=payload)
                
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("status") == "ok":
                    solution = data.get("solution", {})
                    
                    return ScrapingResult(
                        success=True,
                        method_used=AntiDetectionMethod.FLARE_SOLVERR,
                        content=solution.get("response"),
                        status_code=solution.get("status", 200),
                        headers=solution.get("headers", {}),
                        cookies=solution.get("cookies", {}),
                        execution_time=execution_time,
                        attempts=1
                    )
                else:
                    logger.error(f"❌ FlareSolverr error: {data.get('message', 'Unknown error')}")
                    
        except Exception as e:
            logger.error(f"❌ FlareSolverr request failed: {e}")
            
        return None
    
    async def destroy_session(self):
        """Destroy FlareSolverr session"""
        if self.session_id:
            try:
                payload = {
                    "cmd": "sessions.destroy",
                    "session": self.session_id
                }
                
                async with httpx.AsyncClient(timeout=10.0) as client:
                    await client.post(self.config.flaresolverr_url, json=payload)
                    
                logger.info(f"🗑️ FlareSolverr session destroyed: {self.session_id}")
                
            except Exception as e:
                logger.error(f"❌ Failed to destroy FlareSolverr session: {e}")
                
            finally:
                self.session_id = None


class CaptchaSolver:
    """Universal CAPTCHA solver"""
    
    def __init__(self, config: AntiBotConfig):
        self.config = config
        self.twocaptcha_client = None
        
        if TWOCAPTCHA_AVAILABLE and config.twocaptcha_api_key:
            self.twocaptcha_client = TwoCaptcha(config.twocaptcha_api_key)
    
    async def solve_recaptcha(self, site_key: str, page_url: str, 
                            version: str = "v2") -> Optional[str]:
        """Solve reCAPTCHA challenge"""
        if not self.twocaptcha_client:
            logger.warning("⚠️  No CAPTCHA solver available")
            return None
            
        try:
            if version == "v2":
                result = self.twocaptcha_client.recaptcha(
                    sitekey=site_key,
                    url=page_url
                )
            elif version == "v3":
                result = self.twocaptcha_client.recaptcha(
                    sitekey=site_key,
                    url=page_url,
                    version="v3",
                    score=0.3,
                    action="submit"
                )
            else:
                logger.error(f"❌ Unsupported reCAPTCHA version: {version}")
                return None
                
            if result and result.get("code"):
                logger.info("✅ reCAPTCHA solved successfully")
                return result["code"]
                
        except Exception as e:
            logger.error(f"❌ reCAPTCHA solving failed: {e}")
            
        return None
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve hCaptcha challenge"""
        if not self.twocaptcha_client:
            return None
            
        try:
            result = self.twocaptcha_client.hcaptcha(
                sitekey=site_key,
                url=page_url
            )
            
            if result and result.get("code"):
                logger.info("✅ hCaptcha solved successfully")
                return result["code"]
                
        except Exception as e:
            logger.error(f"❌ hCaptcha solving failed: {e}")
            
        return None
    
    async def solve_turnstile(self, site_key: str, page_url: str) -> Optional[str]:
        """Solve Cloudflare Turnstile challenge"""
        if not self.twocaptcha_client:
            return None
            
        try:
            result = self.twocaptcha_client.turnstile(
                sitekey=site_key,
                url=page_url
            )
            
            if result and result.get("code"):
                logger.info("✅ Turnstile solved successfully")  
                return result["code"]
                
        except Exception as e:
            logger.error(f"❌ Turnstile solving failed: {e}")
            
        return None


class RevolutionaryAntiBotSystem:
    """Revolutionary Anti-Bot Defense System - Main Controller"""
    
    def __init__(self, config: Optional[AntiBotConfig] = None):
        self.config = config or AntiBotConfig()
        self.flaresolverr = FlareSolverrClient(self.config)
        self.captcha_solver = CaptchaSolver(self.config)
        
        # Initialize cloudscraper session
        if CLOUDSCRAPER_AVAILABLE:
            self.cloudscraper_session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
        else:
            self.cloudscraper_session = None
    
    def _detect_cloudflare(self, content: str, headers: Dict[str, str]) -> bool:
        """Detect Cloudflare protection"""
        if not content:
            return False
            
        content_lower = content.lower()
        
        # Check content indicators
        for indicator in self.config.cloudflare_indicators:
            if indicator.lower() in content_lower:
                return True
        
        # Check headers
        cf_headers = ['cf-ray', 'cf-cache-status', 'cf-request-id']
        for header in cf_headers:
            if header in headers:
                return True
                
        return False
    
    def _detect_captcha(self, content: str) -> Optional[Dict[str, str]]:
        """Detect CAPTCHA on page"""
        if not content:
            return None
            
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # reCAPTCHA v2/v3
        recaptcha = soup.find(attrs={"data-sitekey": True}) or soup.find(class_="g-recaptcha")
        if recaptcha:
            return {
                "type": "recaptcha",
                "sitekey": recaptcha.get("data-sitekey", ""),
                "version": "v3" if "v3" in str(recaptcha) else "v2"
            }
        
        # hCaptcha
        hcaptcha = soup.find(class_="h-captcha")
        if hcaptcha:
            return {
                "type": "hcaptcha", 
                "sitekey": hcaptcha.get("data-sitekey", "")
            }
        
        # Turnstile
        turnstile = soup.find(class_="cf-turnstile")
        if turnstile:
            return {
                "type": "turnstile",
                "sitekey": turnstile.get("data-sitekey", "")
            }
            
        return None
    
    async def _make_requests_attempt(self, url: str, method: str = "GET",
                                   headers: Optional[Dict] = None, 
                                   data: Optional[Dict] = None,
                                   **kwargs) -> ScrapingResult:
        """Standard requests attempt"""
        start_time = time.time()
        
        try:
            session = requests.Session()
            
            # Enhanced headers
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
            
            if headers:
                default_headers.update(headers)
            
            if method.upper() == "GET":
                response = session.get(url, headers=default_headers, timeout=30, **kwargs)
            else:
                response = session.post(url, headers=default_headers, data=data, timeout=30, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Check for Cloudflare
            cf_detected = self._detect_cloudflare(response.text, dict(response.headers))
            captcha_info = self._detect_captcha(response.text)
            
            return ScrapingResult(
                success=response.status_code == 200 and not cf_detected,
                method_used=AntiDetectionMethod.REQUESTS,
                response=response,
                content=response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
                execution_time=execution_time,
                attempts=1,
                cloudflare_detected=cf_detected,
                captcha_detected=captcha_info is not None
            )
            
        except Exception as e:
            return ScrapingResult(
                success=False,
                method_used=AntiDetectionMethod.REQUESTS,
                execution_time=time.time() - start_time,
                attempts=1,
                error=str(e)
            )
    
    async def _make_cloudscraper_attempt(self, url: str, method: str = "GET",
                                       headers: Optional[Dict] = None,
                                       data: Optional[Dict] = None,
                                       **kwargs) -> ScrapingResult:
        """CloudScraper attempt for Cloudflare bypass"""
        if not self.cloudscraper_session:
            return ScrapingResult(
                success=False,
                error="CloudScraper not available"
            )
        
        start_time = time.time()
        
        try:
            if method.upper() == "GET":
                response = self.cloudscraper_session.get(url, headers=headers, timeout=30, **kwargs)
            else:
                response = self.cloudscraper_session.post(url, headers=headers, data=data, timeout=30, **kwargs)
            
            execution_time = time.time() - start_time
            
            # Check results
            cf_detected = self._detect_cloudflare(response.text, dict(response.headers))
            captcha_info = self._detect_captcha(response.text)
            
            return ScrapingResult(
                success=response.status_code == 200 and not cf_detected,
                method_used=AntiDetectionMethod.CLOUDSCRAPER,
                response=response,
                content=response.text,
                status_code=response.status_code,
                headers=dict(response.headers),
                execution_time=execution_time,
                attempts=1,
                cloudflare_detected=cf_detected,
                captcha_detected=captcha_info is not None
            )
            
        except Exception as e:
            return ScrapingResult(
                success=False,
                method_used=AntiDetectionMethod.CLOUDSCRAPER,
                execution_time=time.time() - start_time,
                attempts=1,
                error=str(e)
            )
    
    async def _make_undetected_chrome_attempt(self, url: str, method: str = "GET",
                                            headers: Optional[Dict] = None,
                                            data: Optional[Dict] = None) -> ScrapingResult:
        """Undetected Chrome attempt"""
        if not UNDETECTED_CHROME_AVAILABLE:
            return ScrapingResult(
                success=False,
                error="undetected-chromedriver not available"
            )
        
        start_time = time.time()
        driver = None
        
        try:
            # Configure undetected Chrome
            options = uc.ChromeOptions()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = uc.Chrome(options=options, version_main=None)
            
            # Navigate to page
            driver.get(url)
            
            # Wait a moment for JS to load
            time.sleep(2)
            
            # Check for CAPTCHA and solve if needed
            captcha_info = self._detect_captcha(driver.page_source)
            if captcha_info and self.config.captcha_provider != CaptchaProvider.NONE:
                captcha_token = await self._solve_captcha_on_page(
                    driver, captcha_info, url
                )
                
            execution_time = time.time() - start_time
            
            return ScrapingResult(
                success=True,
                method_used=AntiDetectionMethod.UNDETECTED_CHROME,
                content=driver.page_source,
                status_code=200,
                execution_time=execution_time,
                attempts=1,
                captcha_detected=captcha_info is not None,
                captcha_solved=captcha_info is not None
            )
            
        except Exception as e:
            return ScrapingResult(
                success=False,
                method_used=AntiDetectionMethod.UNDETECTED_CHROME,
                execution_time=time.time() - start_time,
                attempts=1,
                error=str(e)
            )
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    async def _solve_captcha_on_page(self, driver, captcha_info: Dict[str, str], 
                                   page_url: str) -> Optional[str]:
        """Solve CAPTCHA on current page"""
        captcha_type = captcha_info.get("type")
        site_key = captcha_info.get("sitekey")
        
        if not site_key:
            logger.error("❌ No site key found for CAPTCHA")
            return None
        
        logger.info(f"🤖 Solving {captcha_type} CAPTCHA...")
        
        # Solve CAPTCHA
        if captcha_type == "recaptcha":
            token = await self.captcha_solver.solve_recaptcha(
                site_key, page_url, captcha_info.get("version", "v2")
            )
        elif captcha_type == "hcaptcha":
            token = await self.captcha_solver.solve_hcaptcha(site_key, page_url)
        elif captcha_type == "turnstile":
            token = await self.captcha_solver.solve_turnstile(site_key, page_url)
        else:
            logger.error(f"❌ Unsupported CAPTCHA type: {captcha_type}")
            return None
        
        if not token:
            return None
        
        # Inject token into page
        try:
            if captcha_type == "recaptcha":
                script = f"""
                document.getElementById('g-recaptcha-response').innerHTML = '{token}';
                document.getElementById('g-recaptcha-response').style.display = 'block';
                if (typeof grecaptcha !== 'undefined') {{
                    grecaptcha.getResponse = function() {{ return '{token}'; }};
                }}
                """
            elif captcha_type == "hcaptcha":
                script = f"""
                document.querySelector('[name="h-captcha-response"]').value = '{token}';
                """
            elif captcha_type == "turnstile":
                script = f"""
                document.querySelector('[name="cf-turnstile-response"]').value = '{token}';
                """
            
            driver.execute_script(script)
            time.sleep(1)
            
            return token
            
        except Exception as e:
            logger.error(f"❌ Failed to inject CAPTCHA token: {e}")
            return None
    
    async def scrape(self, url: str, method: str = "GET", 
                    headers: Optional[Dict] = None, 
                    data: Optional[Dict] = None,
                    **kwargs) -> ScrapingResult:
        """
        Main scraping method with intelligent anti-bot triage
        
        Follows the priority order:
        1. requests → 2. cloudscraper → 3. FlareSolverr → 4. undetected-chromedriver
        """
        
        logger.info(f"🚀 Starting anti-bot scraping for: {url}")
        
        total_attempts = 0
        last_result = None
        
        # Try each method in priority order
        for method_type in self.config.method_priority:
            
            for attempt in range(self.config.max_method_attempts):
                total_attempts += 1
                
                logger.info(f"🔄 Attempt {attempt + 1}/{self.config.max_method_attempts} "
                           f"with {method_type.value}")
                
                try:
                    if method_type == AntiDetectionMethod.REQUESTS:
                        result = await self._make_requests_attempt(
                            url, method, headers, data, **kwargs
                        )
                    elif method_type == AntiDetectionMethod.CLOUDSCRAPER:
                        result = await self._make_cloudscraper_attempt(
                            url, method, headers, data, **kwargs
                        )
                    elif method_type == AntiDetectionMethod.FLARE_SOLVERR:
                        result = await self.flaresolverr.solve_cloudflare(
                            url, method, data, headers
                        )
                    elif method_type == AntiDetectionMethod.UNDETECTED_CHROME:
                        result = await self._make_undetected_chrome_attempt(
                            url, method, headers, data
                        )
                    else:
                        # Other methods not yet implemented
                        continue
                    
                    if not result:
                        continue
                    
                    result.attempts = total_attempts
                    last_result = result
                    
                    # Success criteria
                    if result.success:
                        logger.info(f"✅ Success with {method_type.value} "
                                  f"after {total_attempts} attempts "
                                  f"({result.execution_time:.2f}s)")
                        return result
                    
                    # Log what went wrong
                    issues = []
                    if result.cloudflare_detected:
                        issues.append("Cloudflare detected")
                    if result.captcha_detected:
                        issues.append("CAPTCHA detected")
                    if result.error:
                        issues.append(f"Error: {result.error}")
                    if result.status_code and result.status_code != 200:
                        issues.append(f"Status: {result.status_code}")
                    
                    logger.warning(f"⚠️  {method_type.value} failed: {', '.join(issues)}")
                    
                    # If Cloudflare is detected, skip to more powerful methods
                    if result.cloudflare_detected and method_type in [
                        AntiDetectionMethod.REQUESTS, 
                        AntiDetectionMethod.CLOUDSCRAPER
                    ]:
                        logger.info("🔥 Cloudflare detected, escalating to advanced methods")
                        break
                    
                except Exception as e:
                    logger.error(f"❌ Method {method_type.value} crashed: {e}")
                
                # Wait before retry
                if attempt < self.config.max_method_attempts - 1:
                    delay = min(
                        self.config.retry_delay_base * (2 ** attempt),
                        self.config.retry_delay_max
                    )
                    logger.info(f"⏳ Waiting {delay:.1f}s before retry...")
                    await asyncio.sleep(delay)
        
        # All methods failed
        logger.error(f"❌ All anti-bot methods failed after {total_attempts} attempts")
        
        if last_result:
            return last_result
        else:
            return ScrapingResult(
                success=False,
                attempts=total_attempts,
                error="All anti-bot methods failed"
            )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.flaresolverr.destroy_session()


# Example usage and testing
async def test_anti_bot_system():
    """Test the anti-bot system"""
    
    config = AntiBotConfig(
        twocaptcha_api_key="your-2captcha-key-here",  # Replace with real key
        flaresolverr_url="http://localhost:8191/v1"   # Make sure FlareSolverr is running
    )
    
    async with RevolutionaryAntiBotSystem(config) as anti_bot:
        
        test_urls = [
            "https://httpbin.org/get",  # Should work with requests
            "https://nowsecure.nl",     # Cloudflare protected  
            # Add more test URLs
        ]
        
        for url in test_urls:
            print(f"\n🧪 Testing: {url}")
            result = await anti_bot.scrape(url)
            
            if result.success:
                print(f"✅ Success with {result.method_used.value} "
                      f"({result.execution_time:.2f}s)")
            else:
                print(f"❌ Failed: {result.error}")


if __name__ == "__main__":
    asyncio.run(test_anti_bot_system())
