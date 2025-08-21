"""
Login Handler - Automated authentication and session management.

Handles authentication flows for websites requiring login:
- Form-based authentication
- OAuth and social logins  
- CAPTCHA detection and handling
- Session persistence and validation
- Multi-factor authentication support
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page, Browser
from lxml import html

from ..utils.logger import get_logger
from ..observability.metrics import MetricsCollector
from ..anti_bot.browser_stealth.captcha_solver import CaptchaSolver
from ..anti_bot.header_generator import HeaderGenerator

logger = get_logger(__name__)


@dataclass
class LoginCredentials:
    """Authentication credentials."""
    username: str
    password: str
    additional_fields: Dict[str, str] = None
    
    def __post_init__(self):
        if self.additional_fields is None:
            self.additional_fields = {}


@dataclass
class LoginResult:
    """Result from login attempt."""
    success: bool
    session_data: Dict[str, Any]
    error_message: Optional[str] = None
    requires_captcha: bool = False
    requires_mfa: bool = False
    redirect_url: Optional[str] = None
    
    def __post_init__(self):
        if self.session_data is None:
            self.session_data = {}


class LoginHandler:
    """
    Advanced login automation system for web authentication.
    
    Supports multiple authentication methods including:
    - Form-based login
    - OAuth flows
    - Social media authentication
    - CAPTCHA solving
    - Multi-factor authentication
    - Session management and persistence
    """
    
    def __init__(
        self,
        captcha_solver: CaptchaSolver,
        header_generator: HeaderGenerator,
        metrics_collector: MetricsCollector,
        max_login_attempts: int = 3,
        session_timeout: float = 3600.0
    ):
        self.captcha_solver = captcha_solver
        self.header_generator = header_generator
        self.metrics = metrics_collector
        self.max_login_attempts = max_login_attempts
        self.session_timeout = session_timeout
        
        # Session storage
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def login(
        self,
        page: Page,
        login_url: str,
        credentials: LoginCredentials,
        domain: str
    ) -> LoginResult:
        """
        Perform automated login on a website.
        
        Args:
            page: Browser page for interaction
            login_url: URL of the login page
            credentials: Authentication credentials
            domain: Domain for session management
            
        Returns:
            LoginResult with success status and session data
        """
        start_time = time.time()
        attempt = 0
        
        while attempt < self.max_login_attempts:
            attempt += 1
            logger.info(f"Login attempt {attempt} for {domain}")
            
            try:
                # Navigate to login page
                await page.goto(login_url, wait_until='domcontentloaded')
                
                # Detect login form
                login_form = await self._detect_login_form(page)
                if not login_form:
                    return LoginResult(
                        success=False,
                        session_data={},
                        error_message="No login form detected"
                    )
                    
                # Handle CAPTCHA if present
                captcha_solved = await self._handle_captcha(page)
                if captcha_solved is False:  # Explicitly failed (None means no CAPTCHA)
                    return LoginResult(
                        success=False,
                        session_data={},
                        error_message="CAPTCHA solving failed",
                        requires_captcha=True
                    )
                    
                # Fill login form
                await self._fill_login_form(page, login_form, credentials)
                
                # Submit form and wait for response
                login_result = await self._submit_login_form(page, login_form)
                
                if login_result.success:
                    # Extract session data
                    session_data = await self._extract_session_data(page, domain)
                    login_result.session_data = session_data
                    
                    # Store session
                    self._store_session(domain, session_data)
                    
                    # Update metrics
                    self.metrics.timer(f"login_{domain}_time", time.time() - start_time)
                    self.metrics.counter(f"login_{domain}_success", 1)
                    
                    return login_result
                    
                # Check for specific error conditions
                if login_result.requires_mfa:
                    return login_result
                    
                # Log failed attempt
                logger.warning(f"Login attempt {attempt} failed: {login_result.error_message}")
                
                # Wait before retry
                if attempt < self.max_login_attempts:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    
            except Exception as e:
                logger.error(f"Login attempt {attempt} error: {e}")
                if attempt == self.max_login_attempts:
                    return LoginResult(
                        success=False,
                        session_data={},
                        error_message=f"Login failed after {self.max_login_attempts} attempts: {e}"
                    )
                    
        # Update failure metrics
        self.metrics.counter(f"login_{domain}_failure", 1)
        
        return LoginResult(
            success=False,
            session_data={},
            error_message=f"Login failed after {self.max_login_attempts} attempts"
        )


    async def _detect_login_form(self, page: Page) -> Optional[Dict[str, Any]]:
        """Detect and analyze login form on the page."""
        try:
            # Common login form selectors
            form_selectors = [
                'form[action*="login"]',
                'form[action*="signin"]',
                'form[action*="auth"]',
                'form:has(input[type="password"])',
                'form#login',
                'form.login',
                '#login-form',
                '.login-form'
            ]
            
            for selector in form_selectors:
                form_element = await page.query_selector(selector)
                if form_element:
                    # Analyze form structure
                    form_info = await self._analyze_form_structure(page, form_element)
                    if form_info:
                        return form_info
                        
            # Fallback: look for any form with password field
            password_input = await page.query_selector('input[type="password"]')
            if password_input:
                form_element = await password_input.query_selector('xpath=ancestor::form[1]')
                if form_element:
                    return await self._analyze_form_structure(page, form_element)
                    
            return None
            
        except Exception as e:
            logger.error(f"Error detecting login form: {e}")
            return None
            
    async def _analyze_form_structure(self, page: Page, form_element) -> Optional[Dict[str, Any]]:
        """Analyze the structure of a login form."""
        try:
            form_info = {
                'element': form_element,
                'action': await form_element.get_attribute('action') or '',
                'method': await form_element.get_attribute('method') or 'POST',
                'fields': {}
            }
            
            # Find username field
            username_selectors = [
                'input[name*="user"]',
                'input[name*="email"]',
                'input[name*="login"]',
                'input[id*="user"]',
                'input[id*="email"]',
                'input[id*="login"]',
                'input[type="email"]',
                'input[type="text"]:first-of-type'
            ]
            
            for selector in username_selectors:
                username_field = await form_element.query_selector(selector)
                if username_field:
                    form_info['fields']['username'] = {
                        'element': username_field,
                        'name': await username_field.get_attribute('name'),
                        'id': await username_field.get_attribute('id')
                    }
                    break
                    
            # Find password field
            password_field = await form_element.query_selector('input[type="password"]')
            if password_field:
                form_info['fields']['password'] = {
                    'element': password_field,
                    'name': await password_field.get_attribute('name'),
                    'id': await password_field.get_attribute('id')
                }
            else:
                return None  # No password field means not a login form
                
            # Find submit button
            submit_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Sign in")',
                'button:has-text("Log in")',
                '.login-button',
                '#login-button'
            ]
            
            for selector in submit_selectors:
                submit_button = await form_element.query_selector(selector)
                if submit_button:
                    form_info['fields']['submit'] = {
                        'element': submit_button,
                        'name': await submit_button.get_attribute('name'),
                        'id': await submit_button.get_attribute('id')
                    }
                    break
                    
            return form_info if form_info['fields'].get('username') and form_info['fields'].get('password') else None
            
        except Exception as e:
            logger.error(f"Error analyzing form structure: {e}")
            return None
            
    async def _handle_captcha(self, page: Page) -> Optional[bool]:
        """Handle CAPTCHA if present on the page."""
        try:
            # Common CAPTCHA selectors
            captcha_selectors = [
                '.captcha',
                '#captcha',
                '.recaptcha',
                '#recaptcha',
                '.hcaptcha',
                '#hcaptcha',
                'iframe[src*="recaptcha"]',
                'iframe[src*="hcaptcha"]'
            ]
            
            for selector in captcha_selectors:
                captcha_element = await page.query_selector(selector)
                if captcha_element:
                    logger.info("CAPTCHA detected, attempting to solve")
                    
                    # Take screenshot for CAPTCHA solving
                    screenshot = await page.screenshot()
                    
                    # Attempt to solve CAPTCHA
                    solution = await self.captcha_solver.solve_captcha(
                        screenshot, 
                        captcha_type='recaptcha'  # Default type
                    )
                    
                    if solution:
                        # Apply CAPTCHA solution
                        await self._apply_captcha_solution(page, captcha_element, solution)
                        return True
                    else:
                        return False
                        
            return None  # No CAPTCHA found
            
        except Exception as e:
            logger.error(f"Error handling CAPTCHA: {e}")
            return False
            
    async def _apply_captcha_solution(self, page: Page, captcha_element, solution: str):
        """Apply CAPTCHA solution to the form."""
        try:
            # Look for CAPTCHA input field
            captcha_input = await page.query_selector('input[name*="captcha"]')
            if captcha_input:
                await captcha_input.fill(solution)
            else:
                # Handle reCAPTCHA or other types
                logger.warning("Advanced CAPTCHA handling not implemented")
                
        except Exception as e:
            logger.error(f"Error applying CAPTCHA solution: {e}")
            
    async def _fill_login_form(
        self, 
        page: Page, 
        form_info: Dict[str, Any], 
        credentials: LoginCredentials
    ):
        """Fill login form with credentials."""
        try:
            # Fill username
            if 'username' in form_info['fields']:
                username_element = form_info['fields']['username']['element']
                await username_element.fill(credentials.username)
                
            # Fill password
            if 'password' in form_info['fields']:
                password_element = form_info['fields']['password']['element']
                await password_element.fill(credentials.password)
                
            # Fill additional fields
            for field_name, field_value in credentials.additional_fields.items():
                field_element = await page.query_selector(f'input[name="{field_name}"]')
                if field_element:
                    await field_element.fill(field_value)
                    
            # Random delay to mimic human behavior
            await asyncio.sleep(0.5 + (time.time() % 1000) / 1000.0)
            
        except Exception as e:
            logger.error(f"Error filling login form: {e}")
            
    async def _submit_login_form(self, page: Page, form_info: Dict[str, Any]) -> LoginResult:
        """Submit login form and analyze response."""
        try:
            current_url = page.url
            
            # Submit form
            if 'submit' in form_info['fields']:
                submit_button = form_info['fields']['submit']['element']
                await submit_button.click()
            else:
                # Fallback: press Enter on password field
                password_element = form_info['fields']['password']['element']
                await password_element.press('Enter')
                
            # Wait for navigation or response
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=10000)
            except:
                pass  # Page might not navigate
                
            # Check for success indicators
            success_indicators = [
                'dashboard', 'profile', 'account', 'welcome', 'logout', 'settings'
            ]
            
            page_content = await page.content()
            page_url = page.url
            
            # Check URL change (redirect to dashboard/home)
            if page_url != current_url and any(indicator in page_url.lower() for indicator in success_indicators):
                return LoginResult(
                    success=True,
                    session_data={},
                    redirect_url=page_url
                )
                
            # Check for logout button (indicates successful login)
            logout_selectors = [
                'a[href*="logout"]',
                'button:has-text("Logout")',
                'button:has-text("Sign out")',
                '.logout'
            ]
            
            for selector in logout_selectors:
                if await page.query_selector(selector):
                    return LoginResult(
                        success=True,
                        session_data={},
                        redirect_url=page_url
                    )
                    
            # Check for error messages
            error_selectors = [
                '.error',
                '.alert-danger',
                '.login-error',
                '#error',
                '[class*="error"]'
            ]
            
            error_message = None
            for selector in error_selectors:
                error_element = await page.query_selector(selector)
                if error_element:
                    error_text = await error_element.text_content()
                    if error_text and error_text.strip():
                        error_message = error_text.strip()
                        break
                        
            # Check for MFA requirement
            mfa_indicators = ['two-factor', '2fa', 'verification code', 'authenticator']
            if any(indicator in page_content.lower() for indicator in mfa_indicators):
                return LoginResult(
                    success=False,
                    session_data={},
                    requires_mfa=True,
                    error_message="Multi-factor authentication required"
                )
                
            return LoginResult(
                success=False,
                session_data={},
                error_message=error_message or "Login failed - unknown reason"
            )
            
        except Exception as e:
            logger.error(f"Error submitting login form: {e}")
            return LoginResult(
                success=False,
                session_data={},
                error_message=f"Form submission error: {e}"
            )
            
    async def _extract_session_data(self, page: Page, domain: str) -> Dict[str, Any]:
        """Extract session data after successful login."""
        try:
            # Get cookies
            cookies = await page.context.cookies()
            
            # Get local storage
            local_storage = await page.evaluate("""
                () => {
                    const storage = {};
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        storage[key] = localStorage.getItem(key);
                    }
                    return storage;
                }
            """)
            
            # Get session storage
            session_storage = await page.evaluate("""
                () => {
                    const storage = {};
                    for (let i = 0; i < sessionStorage.length; i++) {
                        const key = sessionStorage.key(i);
                        storage[key] = sessionStorage.getItem(key);
                    }
                    return storage;
                }
            """)
            
            return {
                'cookies': {cookie['name']: cookie['value'] for cookie in cookies},
                'local_storage': local_storage,
                'session_storage': session_storage,
                'current_url': page.url,
                'timestamp': time.time(),
                'domain': domain
            }
            
        except Exception as e:
            logger.error(f"Error extracting session data: {e}")
            return {}
            
    def _store_session(self, domain: str, session_data: Dict[str, Any]):
        """Store session data for reuse."""
        self._active_sessions[domain] = session_data
        
    def get_session(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get stored session data for domain."""
        session = self._active_sessions.get(domain)
        if session:
            # Check if session is still valid (not expired)
            if time.time() - session.get('timestamp', 0) < self.session_timeout:
                return session
            else:
                # Remove expired session
                del self._active_sessions[domain]
        return None
        
    def clear_session(self, domain: str):
        """Clear stored session for domain."""
        self._active_sessions.pop(domain, None)
        
    def clear_all_sessions(self):
        """Clear all stored sessions."""
        self._active_sessions.clear()
        
    async def validate_session(self, page: Page, domain: str) -> bool:
        """Validate if current session is still active."""
        try:
            session_data = self.get_session(domain)
            if not session_data:
                return False
                
            # Apply stored cookies
            cookies = session_data.get('cookies', {})
            if cookies:
                # Convert to playwright cookie format
                cookie_list = []
                for name, value in cookies.items():
                    cookie_list.append({
                        'name': name,
                        'value': value,
                        'domain': domain,
                        'path': '/'
                    })
                await page.context.add_cookies(cookie_list)
                
            # Navigate to a protected page to test session
            test_url = f"https://{domain}/dashboard"  # Common protected path
            try:
                await page.goto(test_url, timeout=10000)
                
                # Check if we're still logged in
                logout_selectors = [
                    'a[href*="logout"]',
                    'button:has-text("Logout")',
                    '.logout'
                ]
                
                for selector in logout_selectors:
                    if await page.query_selector(selector):
                        return True
                        
            except:
                pass
                
            return False
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return False
            
    def get_statistics(self) -> Dict[str, Any]:
        """Get login handler statistics."""
        active_sessions = len(self._active_sessions)
        valid_sessions = sum(
            1 for session in self._active_sessions.values()
            if time.time() - session.get('timestamp', 0) < self.session_timeout
        )
        
        return {
            'active_sessions': active_sessions,
            'valid_sessions': valid_sessions,
            'max_login_attempts': self.max_login_attempts,
            'session_timeout': self.session_timeout,
            'domains_with_sessions': list(self._active_sessions.keys())
        }


# Legacy function for backward compatibility
def perform_login(url: str, credentials: dict) -> dict:
    """
    Legacy function for backward compatibility.
    
    Args:
        url: Login URL
        credentials: Dictionary with username/password
        
    Returns:
        Dictionary with login result and session data
    """
    import asyncio
    from playwright.async_api import async_playwright
    
    async def _legacy_login():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                from ..anti_bot.browser_stealth.captcha_solver import CaptchaSolver
                from ..anti_bot.header_generator import HeaderGenerator
                from ..observability.metrics import MetricsCollector
                
                # Create simple instances for legacy support
                captcha_solver = CaptchaSolver({})
                header_generator = HeaderGenerator()
                metrics_collector = MetricsCollector()
                
                handler = LoginHandler(
                    captcha_solver=captcha_solver,
                    header_generator=header_generator,
                    metrics_collector=metrics_collector
                )
                
                creds = LoginCredentials(
                    username=credentials.get('username', ''),
                    password=credentials.get('password', ''),
                    additional_fields=credentials.get('additional_fields', {})
                )
                
                domain = url.split('/')[2]  # Extract domain from URL
                result = await handler.login(page, url, creds, domain)
                
                return {
                    'success': result.success,
                    'session_data': result.session_data,
                    'error_message': result.error_message,
                    'requires_captcha': result.requires_captcha,
                    'requires_mfa': result.requires_mfa
                }
                
            finally:
                await browser.close()
                
    return asyncio.run(_legacy_login())
    """
    Legacy function for backward compatibility.
    Performs a login and returns the session state (e.g., cookies).
    """
    logger.warning("Using legacy perform_login function - consider using LoginHandler class")
    try:
        return asyncio.run(_legacy_login())
    except Exception as e:
        logger.error(f"Legacy login failed: {e}")
        return {"success": False, "error": str(e)}