"""
Enhanced FlareSolverr Integration for Ultimate Scraping System

Integrerar FlareSolverr-funktionalitet för att automatiskt lösa Cloudflare-utmaningar
och andra anti-bot-skydd. Bygger på den ursprungliga FlareSolverr-arkitekturen men 
anpassad för integration med Ultimate Scraping System.

Baserat på: https://github.com/FlareSolverr/FlareSolverr
"""

import logging
import platform
import sys
import time
import json
import uuid
from datetime import timedelta
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from urllib.parse import urlparse

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium.webdriver.support.expected_conditions import (
        presence_of_element_located, staleness_of, title_is
    )
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available - FlareSolverr integration disabled")

# Cloudflare detection patterns (från original FlareSolverr)
ACCESS_DENIED_TITLES = [
    'Access denied',
    'Attention Required! | Cloudflare'
]

ACCESS_DENIED_SELECTORS = [
    'div.cf-error-title span.cf-code-label span',
    '#cf-error-details div.cf-error-overview h1'
]

CHALLENGE_TITLES = [
    'Just a moment...',
    'DDoS-Guard',
    'Checking your browser...',
    'Please wait...'
]

CHALLENGE_SELECTORS = [
    '#cf-challenge-running', '.ray_id', '.attack-box', '#cf-please-wait', 
    '#challenge-spinner', '#trk_jschal_js', '#turnstile-wrapper', '.lds-ring',
    'td.info #js_info',
    'div.vc div.text-box h2'
]

@dataclass
class ChallengeResult:
    """Resultat från challenge-lösendet"""
    url: str
    status_code: int = 200
    cookies: List[Dict] = None
    headers: Dict[str, str] = None
    content: str = ""
    user_agent: str = ""
    success: bool = False
    challenge_detected: bool = False
    message: str = ""
    solve_time: float = 0.0

@dataclass
class FlareSession:
    """FlareSolverr-session för att återanvända webbläsare"""
    session_id: str
    driver: Optional[WebDriver] = None
    proxy: Optional[str] = None
    created_at: float = 0.0
    last_used: float = 0.0
    requests_count: int = 0

class EnhancedFlareSolverr:
    """
    Förbättrad FlareSolverr-integration med sessionshantering och caching
    """
    
    def __init__(self, 
                 chrome_path: Optional[str] = None,
                 chromedriver_path: Optional[str] = None,
                 max_timeout: int = 60,
                 max_sessions: int = 5,
                 session_ttl: int = 600,  # 10 minuter
                 headless: bool = True):
        
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium required for FlareSolverr functionality")
            
        self.chrome_path = chrome_path
        self.chromedriver_path = chromedriver_path
        self.max_timeout = max_timeout
        self.max_sessions = max_sessions
        self.session_ttl = session_ttl
        self.headless = headless
        
        # Sessions storage
        self._sessions: Dict[str, FlareSession] = {}
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'challenges_detected': 0,
            'challenges_solved': 0,
            'challenges_failed': 0,
            'total_solve_time': 0.0,
            'avg_solve_time': 0.0
        }
        
        logging.info("Enhanced FlareSolverr initialized")
        
    def create_session(self, session_id: Optional[str] = None, proxy: Optional[str] = None) -> str:
        """Skapa ny session för webbläsaråteranvändning"""
        
        if session_id is None:
            session_id = str(uuid.uuid4())
            
        # Cleanup gamla sessioner
        self._cleanup_sessions()
        
        if session_id in self._sessions:
            logging.info(f"Session {session_id} redan existerar")
            return session_id
            
        if len(self._sessions) >= self.max_sessions:
            # Ta bort äldsta sessionen
            oldest_id = min(self._sessions.keys(), 
                           key=lambda x: self._sessions[x].last_used)
            self.destroy_session(oldest_id)
            
        session = FlareSession(
            session_id=session_id,
            proxy=proxy,
            created_at=time.time(),
            last_used=time.time()
        )
        
        self._sessions[session_id] = session
        logging.info(f"Session {session_id} skapad")
        return session_id
        
    def destroy_session(self, session_id: str) -> bool:
        """Förstör session och stäng webbläsare"""
        
        if session_id not in self._sessions:
            return False
            
        session = self._sessions[session_id]
        if session.driver:
            try:
                session.driver.quit()
            except Exception as e:
                logging.warning(f"Fel vid stängning av driver: {e}")
                
        del self._sessions[session_id]
        logging.info(f"Session {session_id} förstörd")
        return True
        
    def get_sessions(self) -> List[str]:
        """Få lista över aktiva sessioner"""
        return list(self._sessions.keys())
        
    def _cleanup_sessions(self):
        """Rensa upp gamla sessioner"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            if current_time - session.last_used > self.session_ttl:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            self.destroy_session(session_id)
            
    def _create_driver(self, proxy: Optional[str] = None) -> WebDriver:
        """Skapa ny Chrome WebDriver-instans"""
        
        options = Options()
        
        # Headless mode
        if self.headless:
            options.add_argument('--headless')
            
        # Anti-detection argumenter
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        
        # User agent
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Proxy-konfiguration
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        # Chrome path
        if self.chrome_path:
            options.binary_location = self.chrome_path
            
        # Service
        service = None
        if self.chromedriver_path:
            service = Service(self.chromedriver_path)
            
        driver = webdriver.Chrome(service=service, options=options)
        
        # Ta bort automation-flaggor
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    def _detect_challenge(self, driver: WebDriver) -> bool:
        """Detektera om sidan innehåller en Cloudflare-utmaning"""
        
        # Kolla titlar
        try:
            page_title = driver.title
            for title in CHALLENGE_TITLES:
                if title in page_title:
                    logging.info(f"Challenge detected by title: {title}")
                    return True
        except Exception:
            pass
            
        # Kolla selektorer
        for selector in CHALLENGE_SELECTORS:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    logging.info(f"Challenge detected by selector: {selector}")
                    return True
            except Exception:
                continue
                
        # Kolla access denied
        try:
            page_title = driver.title
            for title in ACCESS_DENIED_TITLES:
                if title in page_title:
                    logging.warning(f"Access denied detected: {title}")
                    return False  # Inte en challenge, bara nekad åtkomst
        except Exception:
            pass
            
        return False
        
    def _solve_challenge(self, driver: WebDriver, max_attempts: int = 10) -> bool:
        """Lösa Cloudflare-utmaning"""
        
        start_time = time.time()
        
        for attempt in range(max_attempts):
            logging.debug(f"Challenge solve attempt {attempt + 1}/{max_attempts}")
            
            try:
                # Försök klicka verify-checkbox
                self._click_verify_checkbox(driver)
                
                # Vänta på att utmaningen försvinner
                challenge_disappeared = True
                
                # Vänta på att titlar försvinner
                for title in CHALLENGE_TITLES:
                    try:
                        WebDriverWait(driver, 2).until_not(title_is(title))
                    except TimeoutException:
                        challenge_disappeared = False
                        break
                        
                if not challenge_disappeared:
                    continue
                    
                # Vänta på att selektorer försvinner
                for selector in CHALLENGE_SELECTORS:
                    try:
                        WebDriverWait(driver, 2).until_not(
                            presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                    except TimeoutException:
                        challenge_disappeared = False
                        break
                        
                if challenge_disappeared:
                    solve_time = time.time() - start_time
                    logging.info(f"Challenge solved in {solve_time:.2f}s (attempt {attempt + 1})")
                    return True
                    
            except Exception as e:
                logging.debug(f"Error during challenge solve attempt {attempt + 1}: {e}")
                
            # Vänta lite innan nästa försök
            time.sleep(2)
            
        logging.error(f"Failed to solve challenge after {max_attempts} attempts")
        return False
        
    def _click_verify_checkbox(self, driver: WebDriver):
        """Försök klicka Cloudflare verify-checkbox"""
        
        try:
            # Byt till iframe om det finns
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    # Försök hitta checkbox
                    checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    if checkbox.is_displayed():
                        checkbox.click()
                        logging.debug("Verify checkbox clicked")
                        break
                except Exception:
                    pass
                finally:
                    driver.switch_to.default_content()
                    
        except Exception as e:
            logging.debug(f"Could not click verify checkbox: {e}")
            
        # Försök med tangentbordsnavigation
        try:
            actions = ActionChains(driver)
            actions.pause(2).send_keys(Keys.TAB).pause(1).send_keys(Keys.SPACE).perform()
            logging.debug("Tried keyboard navigation for verify")
        except Exception:
            pass
            
    def solve_challenge(self, 
                       url: str, 
                       method: str = 'GET',
                       post_data: Optional[str] = None,
                       headers: Optional[Dict[str, str]] = None,
                       cookies: Optional[List[Dict]] = None,
                       session_id: Optional[str] = None,
                       proxy: Optional[str] = None) -> ChallengeResult:
        """
        Huvudmetod för att lösa challenges
        """
        
        start_time = time.time()
        self.stats['total_requests'] += 1
        
        result = ChallengeResult(url=url)
        
        try:
            # Hämta eller skapa session
            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                driver = session.driver
                
                # Skapa ny driver om den inte finns eller är död
                if not driver:
                    driver = self._create_driver(proxy or session.proxy)
                    session.driver = driver
                    
            else:
                # Skapa ny driver
                driver = self._create_driver(proxy)
                if session_id:
                    if session_id not in self._sessions:
                        self.create_session(session_id, proxy)
                    self._sessions[session_id].driver = driver
                    
            # Navigera till sidan
            logging.info(f"Navigating to {url} via {method}")
            
            if method.upper() == 'POST' and post_data:
                self._make_post_request(driver, url, post_data, headers)
            else:
                driver.get(url)
                
            # Sätt cookies om specificerade
            if cookies:
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        logging.warning(f"Could not set cookie: {e}")
                        
            # Detektera challenge
            if self._detect_challenge(driver):
                logging.info("Challenge detected, attempting to solve...")
                result.challenge_detected = True
                self.stats['challenges_detected'] += 1
                
                if self._solve_challenge(driver):
                    result.success = True
                    result.message = "Challenge solved successfully"
                    self.stats['challenges_solved'] += 1
                else:
                    result.success = False
                    result.message = "Failed to solve challenge"
                    self.stats['challenges_failed'] += 1
            else:
                logging.info("No challenge detected")
                result.success = True
                result.message = "No challenge detected"
                
            # Samla resultat
            result.url = driver.current_url
            result.cookies = driver.get_cookies()
            result.content = driver.page_source
            result.user_agent = driver.execute_script("return navigator.userAgent;")
            
            # Uppdatera session stats
            if session_id and session_id in self._sessions:
                session = self._sessions[session_id]
                session.last_used = time.time()
                session.requests_count += 1
                
        except Exception as e:
            logging.error(f"Error during challenge solving: {e}")
            result.success = False
            result.message = f"Error: {str(e)}"
            
        # Uppdatera statistik
        solve_time = time.time() - start_time
        result.solve_time = solve_time
        self.stats['total_solve_time'] += solve_time
        
        if self.stats['total_requests'] > 0:
            self.stats['avg_solve_time'] = self.stats['total_solve_time'] / self.stats['total_requests']
            
        return result
        
    def _make_post_request(self, driver: WebDriver, url: str, post_data: str, headers: Optional[Dict[str, str]]):
        """Gör POST-request via JavaScript injection"""
        
        # Skapa temporär HTML-form för POST
        form_html = f"""
        <html>
        <body>
        <form id="postForm" action="{url}" method="POST" style="display:none;">
        """
        
        # Parsa post_data (antag att det är form-encoded)
        try:
            import urllib.parse
            parsed_data = urllib.parse.parse_qs(post_data)
            for key, values in parsed_data.items():
                for value in values:
                    form_html += f'<input type="hidden" name="{key}" value="{value}">'
        except Exception:
            # Fallback: lägg till som raw data
            form_html += f'<input type="hidden" name="data" value="{post_data}">'
            
        form_html += """
        </form>
        <script>document.getElementById('postForm').submit();</script>
        </body>
        </html>
        """
        
        # Navigera till temporär HTML och autosubmit
        driver.get("data:text/html," + form_html)
        
    def get_stats(self) -> Dict[str, Any]:
        """Få statistik över challenge-lösning"""
        stats = self.stats.copy()
        stats['active_sessions'] = len(self._sessions)
        stats['success_rate'] = 0.0
        
        if self.stats['challenges_detected'] > 0:
            stats['success_rate'] = (self.stats['challenges_solved'] / 
                                   self.stats['challenges_detected']) * 100
                                   
        return stats
        
    def cleanup(self):
        """Rensa upp alla ressurser"""
        for session_id in list(self._sessions.keys()):
            self.destroy_session(session_id)
        logging.info("FlareSolverr cleanup completed")


class FlaresolverrClient:
    """
    Förenklad klient för att använda FlareSolverr-funktionalitet
    """
    
    def __init__(self, flare_solver: Optional[EnhancedFlareSolverr] = None):
        self.flare_solver = flare_solver or EnhancedFlareSolverr()
        
    def get(self, url: str, **kwargs) -> ChallengeResult:
        """GET-request med challenge-lösning"""
        return self.flare_solver.solve_challenge(url, method='GET', **kwargs)
        
    def post(self, url: str, data: str, **kwargs) -> ChallengeResult:
        """POST-request med challenge-lösning"""  
        return self.flare_solver.solve_challenge(url, method='POST', post_data=data, **kwargs)


if __name__ == "__main__":
    # Demo av FlareSolverr-integration
    print("🔥 Enhanced FlareSolverr Integration Demo")
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium inte installerat - kan inte köra demo")
        sys.exit(1)
        
    try:
        flare = EnhancedFlareSolverr(headless=True)
        client = FlaresolverrClient(flare)
        
        # Test med en sida som har Cloudflare-skydd
        test_url = "https://httpbin.org/headers"  # Enkel testsida
        print(f"🌐 Testar {test_url}")
        
        result = client.get(test_url)
        
        print(f"✅ Success: {result.success}")
        print(f"🎯 Challenge detected: {result.challenge_detected}")
        print(f"💬 Message: {result.message}")
        print(f"⏱️ Solve time: {result.solve_time:.2f}s")
        print(f"🍪 Cookies: {len(result.cookies)} st")
        
        if result.content:
            print(f"📄 Content length: {len(result.content)} chars")
            
        # Visa statistik
        stats = flare.get_stats()
        print(f"\n📊 Statistics:")
        print(f"  Total requests: {stats['total_requests']}")
        print(f"  Challenges detected: {stats['challenges_detected']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Average solve time: {stats['avg_solve_time']:.2f}s")
        
        flare.cleanup()
        print("\n🎉 Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
