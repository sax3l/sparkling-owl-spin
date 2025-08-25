#!/usr/bin/env python3
"""
CloudScraper Integration - Revolutionary Ultimate System v4.0
CloudFlare bypass using JavaScript challenge solving
"""

import asyncio
import logging
import time
import json
import random
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse

try:
    import cloudscraper
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class CloudScraperConfig:
    """Configuration for CloudScraper"""
    enabled: bool = True
    browser: str = "chrome"  # chrome, firefox
    platform: str = "windows"  # windows, linux, darwin
    desktop: bool = True
    delay: float = 1.0  # Delay between requests
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 2.0
    allow_brotli: bool = True
    debug: bool = False
    interpreter: str = "nodejs"  # nodejs, js2py, native
    captcha_solver: Optional[str] = None  # 2captcha, anticaptcha, etc.
    doubledown: bool = True
    user_agent: Optional[str] = None
    headers: Dict[str, str] = None

@dataclass
class RequestSession:
    """CloudScraper session information"""
    session_id: str
    scraper: Any  # cloudscraper.CloudScraper instance
    created_at: float
    last_used: float
    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    current_user_agent: Optional[str] = None

class CloudScraperManager:
    """
    CloudScraper manager for CloudFlare bypass functionality.
    
    Features:
    - Automatic JavaScript challenge solving
    - Multiple browser emulation modes
    - Session management for cookie persistence
    - Retry logic with exponential backoff
    - Request rate limiting
    """
    
    def __init__(self, config: CloudScraperConfig):
        self.config = config
        self.sessions: Dict[str, RequestSession] = {}
        self.session_counter = 0
        self.last_request_time = 0
        
        if not CLOUDSCRAPER_AVAILABLE:
            raise ImportError("cloudscraper not available. Install with: pip install cloudscraper")
            
    def _create_scraper(self, 
                       browser: Optional[str] = None,
                       user_agent: Optional[str] = None) -> cloudscraper.CloudScraper:
        """Create a new CloudScraper instance"""
        
        browser = browser or self.config.browser
        
        # CloudScraper options
        scraper_options = {
            'browser': {
                'browser': browser,
                'platform': self.config.platform,
                'desktop': self.config.desktop
            },
            'debug': self.config.debug,
            'delay': self.config.delay,
            'doubledown': self.config.doubledown,
            'interpreter': self.config.interpreter
        }
        
        # Create scraper
        scraper = cloudscraper.create_scraper(**scraper_options)
        
        # Configure timeout
        scraper.timeout = self.config.timeout
        
        # Configure retries
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504, 403, 503],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        scraper.mount("http://", adapter)
        scraper.mount("https://", adapter)
        
        # Set headers
        headers = self.config.headers or {}
        if user_agent or self.config.user_agent:
            headers['User-Agent'] = user_agent or self.config.user_agent
            
        if self.config.allow_brotli:
            headers['Accept-Encoding'] = 'gzip, deflate, br'
        else:
            headers['Accept-Encoding'] = 'gzip, deflate'
            
        # Default headers
        default_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Merge headers
        for key, value in default_headers.items():
            if key not in headers:
                headers[key] = value
                
        scraper.headers.update(headers)
        
        return scraper
        
    async def create_session(self, browser: Optional[str] = None,
                           user_agent: Optional[str] = None) -> str:
        """Create a new scraping session"""
        
        try:
            self.session_counter += 1
            session_id = f"cs_session_{self.session_counter}_{int(time.time())}"
            
            logger.info(f"🌩️ Creating CloudScraper session: {session_id}")
            
            # Create scraper instance
            scraper = self._create_scraper(browser=browser, user_agent=user_agent)
            
            # Store session
            session = RequestSession(
                session_id=session_id,
                scraper=scraper,
                created_at=time.time(),
                last_used=time.time(),
                current_user_agent=scraper.headers.get('User-Agent')
            )
            
            self.sessions[session_id] = session
            
            logger.info(f"✅ CloudScraper session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create CloudScraper session: {str(e)}")
            raise
            
    async def get_page(self, session_id: str, url: str,
                      method: str = 'GET',
                      headers: Optional[Dict[str, str]] = None,
                      data: Optional[Union[Dict, str]] = None,
                      json_data: Optional[Dict] = None,
                      params: Optional[Dict[str, str]] = None,
                      follow_redirects: bool = True,
                      verify_ssl: bool = True) -> Dict[str, Any]:
        """Make a request using CloudScraper"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        scraper = session.scraper
        
        try:
            # Apply delay between requests
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            if time_since_last < self.config.delay:
                await asyncio.sleep(self.config.delay - time_since_last)
                
            logger.info(f"🌩️ CloudScraper {method} {url} (session: {session_id})")
            start_time = time.time()
            
            # Prepare request parameters
            request_kwargs = {
                'allow_redirects': follow_redirects,
                'verify': verify_ssl
            }
            
            # Add headers
            if headers:
                request_kwargs['headers'] = headers
                
            # Add parameters
            if params:
                request_kwargs['params'] = params
                
            # Add data
            if json_data:
                request_kwargs['json'] = json_data
            elif data:
                request_kwargs['data'] = data
                
            # Make request
            if method.upper() == 'GET':
                response = scraper.get(url, **request_kwargs)
            elif method.upper() == 'POST':
                response = scraper.post(url, **request_kwargs)
            elif method.upper() == 'PUT':
                response = scraper.put(url, **request_kwargs)
            elif method.upper() == 'DELETE':
                response = scraper.delete(url, **request_kwargs)
            elif method.upper() == 'HEAD':
                response = scraper.head(url, **request_kwargs)
            elif method.upper() == 'PATCH':
                response = scraper.patch(url, **request_kwargs)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            response_time = time.time() - start_time
            self.last_request_time = time.time()
            
            # Parse cookies
            cookies = {}
            for cookie in scraper.cookies:
                cookies[cookie.name] = cookie.value
                
            # Update session stats
            session.last_used = time.time()
            session.request_count += 1
            
            if response.status_code < 400:
                session.success_count += 1
            else:
                session.failure_count += 1
                
            logger.info(f"✅ CloudScraper response: {response.status_code} ({response_time:.2f}s)")
            
            return {
                'success': True,
                'url': str(response.url),
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'cookies': cookies,
                'html_content': response.text,
                'content': response.content,
                'response_time': response_time,
                'encoding': response.encoding,
                'reason': response.reason,
                'session_id': session_id
            }
            
        except cloudscraper.exceptions.CloudflareChallengeError as e:
            logger.error(f"❌ CloudFlare challenge failed: {str(e)}")
            session.failure_count += 1
            return {
                'success': False,
                'url': url,
                'error': f'CloudFlare challenge failed: {str(e)}',
                'error_type': 'cloudflare_challenge',
                'session_id': session_id
            }
            
        except cloudscraper.exceptions.CloudflareCode1020 as e:
            logger.error(f"❌ CloudFlare access denied (1020): {str(e)}")
            session.failure_count += 1
            return {
                'success': False,
                'url': url,
                'error': f'CloudFlare access denied: {str(e)}',
                'error_type': 'cloudflare_1020',
                'session_id': session_id
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {str(e)}")
            session.failure_count += 1
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'error_type': 'request_error',
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"❌ CloudScraper request failed: {str(e)}")
            session.failure_count += 1
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'error_type': 'general_error',
                'session_id': session_id
            }
            
    async def post_form(self, session_id: str, url: str,
                       form_data: Dict[str, Any],
                       files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Submit a form using CloudScraper"""
        
        try:
            kwargs = {'data': form_data}
            if files:
                kwargs['files'] = files
                
            return await self.get_page(session_id, url, method='POST', **kwargs)
            
        except Exception as e:
            logger.error(f"❌ Form submission failed: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'session_id': session_id
            }
            
    async def solve_captcha_challenge(self, session_id: str, url: str,
                                    captcha_params: Dict[str, Any]) -> Dict[str, Any]:
        """Solve CAPTCHA challenge (requires captcha solver service)"""
        
        if not self.config.captcha_solver:
            return {
                'success': False,
                'url': url,
                'error': 'No CAPTCHA solver configured',
                'session_id': session_id
            }
            
        # This would integrate with services like 2captcha, anticaptcha, etc.
        # For now, return placeholder
        logger.warning(f"⚠️ CAPTCHA challenge detected but solver not implemented")
        
        return {
            'success': False,
            'url': url,
            'error': 'CAPTCHA solver not implemented',
            'captcha_detected': True,
            'session_id': session_id
        }
        
    async def get_session_cookies(self, session_id: str) -> Dict[str, str]:
        """Get cookies from a session"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        scraper = session.scraper
        
        cookies = {}
        for cookie in scraper.cookies:
            cookies[cookie.name] = cookie.value
            
        return cookies
        
    async def set_session_cookies(self, session_id: str, 
                                cookies: Dict[str, str]) -> bool:
        """Set cookies for a session"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        scraper = session.scraper
        
        try:
            for name, value in cookies.items():
                scraper.cookies.set(name, value)
                
            session.last_used = time.time()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to set cookies: {str(e)}")
            return False
            
    async def update_session_headers(self, session_id: str,
                                   headers: Dict[str, str]) -> bool:
        """Update headers for a session"""
        
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
            
        session = self.sessions[session_id]
        scraper = session.scraper
        
        try:
            scraper.headers.update(headers)
            session.last_used = time.time()
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update headers: {str(e)}")
            return False
            
    async def destroy_session(self, session_id: str):
        """Destroy a scraping session"""
        
        if session_id not in self.sessions:
            logger.warning(f"⚠️ Session {session_id} not found for destruction")
            return
            
        try:
            logger.info(f"🗑️ Destroying CloudScraper session {session_id}")
            
            session = self.sessions[session_id]
            
            # Close the session
            session.scraper.close()
            
            # Remove from tracking
            del self.sessions[session_id]
            
        except Exception as e:
            logger.error(f"❌ Failed to destroy session: {str(e)}")
            
    async def cleanup_expired_sessions(self, max_age_minutes: int = 60):
        """Clean up expired sessions"""
        current_time = time.time()
        max_age_seconds = max_age_minutes * 60
        
        expired_sessions = []
        for session_id, session in self.sessions.items():
            if current_time - session.last_used > max_age_seconds:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            await self.destroy_session(session_id)
            
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired CloudScraper sessions")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get scraper statistics"""
        return {
            'active_sessions': len(self.sessions),
            'total_sessions_created': self.session_counter,
            'sessions': {
                session_id: {
                    'created_at': session.created_at,
                    'last_used': session.last_used,
                    'age_minutes': (time.time() - session.created_at) / 60,
                    'request_count': session.request_count,
                    'success_count': session.success_count,
                    'failure_count': session.failure_count,
                    'success_rate': session.success_count / max(session.request_count, 1),
                    'user_agent': session.current_user_agent
                }
                for session_id, session in self.sessions.items()
            }
        }
        
    async def cleanup(self):
        """Clean up all resources"""
        for session_id in list(self.sessions.keys()):
            await self.destroy_session(session_id)

class CloudScraperAdapter:
    """High-level adapter for CloudScraper integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = CloudScraperConfig(**config)
        self.manager = CloudScraperManager(self.config)
        self._cleanup_task = None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not CLOUDSCRAPER_AVAILABLE:
            if self.config.enabled:
                logger.error("❌ cloudscraper not available")
            return
            
        logger.info("✅ CloudScraper adapter initialized")
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def get_page_cloudflare(self, url: str,
                                method: str = 'GET',
                                headers: Optional[Dict[str, str]] = None,
                                data: Optional[Union[Dict, str]] = None,
                                json_data: Optional[Dict] = None,
                                params: Optional[Dict[str, str]] = None,
                                browser: Optional[str] = None,
                                user_agent: Optional[str] = None,
                                persistent_session: bool = False) -> Dict[str, Any]:
        """
        Get a page using CloudScraper bypass.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'status_code': int,
            'html_content': str,
            'headers': dict,
            'cookies': dict,
            'response_time': float,
            'session_id': str (if persistent_session=True)
        }
        """
        
        if not self.config.enabled:
            return {
                'success': False,
                'url': url,
                'error': 'CloudScraper is disabled'
            }
            
        try:
            # Create session
            session_id = await self.manager.create_session(
                browser=browser,
                user_agent=user_agent
            )
            
            # Make request
            result = await self.manager.get_page(
                session_id=session_id,
                url=url,
                method=method,
                headers=headers,
                data=data,
                json_data=json_data,
                params=params
            )
            
            if result['success']:
                response = {
                    'success': True,
                    'url': result['url'],
                    'status_code': result['status_code'],
                    'html_content': result['html_content'],
                    'headers': result['headers'],
                    'cookies': result['cookies'],
                    'response_time': result['response_time'],
                    'method': 'cloudscraper'
                }
                
                if persistent_session:
                    response['session_id'] = session_id
                else:
                    # Clean up session if not persistent
                    await self.manager.destroy_session(session_id)
                    
                return response
            else:
                # Clean up on failure
                await self.manager.destroy_session(session_id)
                return {
                    'success': False,
                    'url': url,
                    'error': result['error'],
                    'error_type': result.get('error_type'),
                    'method': 'cloudscraper'
                }
                
        except Exception as e:
            logger.error(f"❌ CloudScraper request failed: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'method': 'cloudscraper'
            }
            
    async def submit_form_cloudflare(self, url: str, form_data: Dict[str, Any],
                                   files: Optional[Dict[str, Any]] = None,
                                   headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Submit a form through CloudFlare protection"""
        
        try:
            session_id = await self.manager.create_session()
            
            # Submit form
            result = await self.manager.post_form(
                session_id=session_id,
                url=url,
                form_data=form_data,
                files=files
            )
            
            # Clean up
            await self.manager.destroy_session(session_id)
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
            
    async def get_with_session(self, session_id: str, url: str, 
                             **kwargs) -> Dict[str, Any]:
        """Make a request using an existing session"""
        return await self.manager.get_page(session_id, url, **kwargs)
        
    async def create_persistent_session(self, browser: Optional[str] = None,
                                      user_agent: Optional[str] = None) -> str:
        """Create a persistent session for multiple requests"""
        return await self.manager.create_session(browser=browser, user_agent=user_agent)
        
    async def destroy_session(self, session_id: str):
        """Destroy a persistent session"""
        await self.manager.destroy_session(session_id)
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            'enabled': self.config.enabled,
            'config': asdict(self.config),
            'manager_stats': self.manager.get_stats()
        }
        
    async def _cleanup_loop(self):
        """Background cleanup task"""
        while True:
            try:
                await asyncio.sleep(900)  # Check every 15 minutes
                await self.manager.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Cleanup task failed: {str(e)}")
                
    async def cleanup(self):
        """Clean up all resources"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
                
        await self.manager.cleanup()

# Factory function
def create_cloudscraper_adapter(config: Dict[str, Any]) -> CloudScraperAdapter:
    """Create and configure CloudScraper adapter"""
    return CloudScraperAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'browser': 'chrome',
        'debug': True,
        'delay': 1.0,
        'timeout': 30
    }
    
    adapter = create_cloudscraper_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Test CloudFlare bypass
        result = await adapter.get_page_cloudflare(
            'https://nowsecure.nl',  # CloudFlare protected site
            persistent_session=False
        )
        
        if result['success']:
            print(f"✅ Success: Status {result['status_code']}")
            print(f"Content length: {len(result['html_content'])}")
        else:
            print(f"❌ Failed: {result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
