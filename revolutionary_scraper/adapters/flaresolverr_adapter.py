#!/usr/bin/env python3
"""
FlareSolverr Integration - Revolutionary Ultimate System v4.0
CloudFlare bypass using FlareSolverr service
"""

import aiohttp
import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class FlareSolverrConfig:
    """Configuration for FlareSolverr integration"""
    enabled: bool = True
    endpoint: str = "http://localhost:8191/v1"
    timeout: int = 60
    max_timeout: int = 600
    session_ttl: int = 600000  # 10 minutes in milliseconds
    debug: bool = False
    max_retries: int = 3
    proxy_support: bool = True

@dataclass
class FlareSolverrSession:
    """FlareSolverr session information"""
    session_id: str
    created_at: float
    last_used: float
    proxy: Optional[str] = None
    user_agent: Optional[str] = None

@dataclass
class FlareSolverrResult:
    """Result from FlareSolverr request"""
    success: bool
    url: str
    status: int = 0
    headers: Dict[str, str] = None
    cookies: List[Dict[str, Any]] = None
    html: str = ""
    message: str = ""
    startTimestamp: int = 0
    endTimestamp: int = 0
    version: str = ""
    solution: Dict[str, Any] = None
    session_id: Optional[str] = None

class FlareSolverrClient:
    """
    FlareSolverr client for CloudFlare bypass.
    
    Supports:
    - Session management for cookie persistence
    - Proxy support for IP rotation
    - Custom headers and user agents
    - Retry logic with exponential backoff
    """
    
    def __init__(self, config: FlareSolverrConfig):
        self.config = config
        self.sessions: Dict[str, FlareSolverrSession] = {}
        self.session_counter = 0
        
    async def create_session(self, proxy: Optional[str] = None, 
                           user_agent: Optional[str] = None) -> str:
        """Create a new FlareSolverr session"""
        try:
            self.session_counter += 1
            session_id = f"session_{self.session_counter}_{int(time.time())}"
            
            payload = {
                "cmd": "sessions.create",
                "session": session_id,
                "maxTimeout": self.config.max_timeout
            }
            
            if proxy:
                payload["proxy"] = {
                    "url": proxy
                }
                
            if user_agent:
                payload["userAgent"] = user_agent
                
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    self.config.endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status != 200:
                        raise Exception(f"Failed to create session: HTTP {response.status}")
                        
                    result = await response.json()
                    
                    if result.get("status") != "ok":
                        raise Exception(f"Session creation failed: {result.get('message', 'Unknown error')}")
                        
                    # Store session info
                    self.sessions[session_id] = FlareSolverrSession(
                        session_id=session_id,
                        created_at=time.time(),
                        last_used=time.time(),
                        proxy=proxy,
                        user_agent=user_agent
                    )
                    
                    logger.info(f"✅ Created FlareSolverr session: {session_id}")
                    return session_id
                    
        except Exception as e:
            logger.error(f"❌ Failed to create FlareSolverr session: {str(e)}")
            raise
            
    async def destroy_session(self, session_id: str):
        """Destroy a FlareSolverr session"""
        try:
            payload = {
                "cmd": "sessions.destroy",
                "session": session_id
            }
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.post(
                    self.config.endpoint,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    result = await response.json()
                    
                    # Remove from our tracking even if the request failed
                    if session_id in self.sessions:
                        del self.sessions[session_id]
                        
                    if result.get("status") == "ok":
                        logger.info(f"✅ Destroyed FlareSolverr session: {session_id}")
                    else:
                        logger.warning(f"⚠️ Session destroy warning: {result.get('message', 'Unknown')}")
                        
        except Exception as e:
            logger.error(f"❌ Failed to destroy session {session_id}: {str(e)}")
            # Still remove from tracking
            if session_id in self.sessions:
                del self.sessions[session_id]
                
    async def request(self, url: str, method: str = "GET", 
                     session_id: Optional[str] = None,
                     headers: Optional[Dict[str, str]] = None,
                     data: Optional[str] = None,
                     timeout: Optional[int] = None) -> FlareSolverrResult:
        """Make a request through FlareSolverr"""
        
        timeout = timeout or self.config.timeout
        
        for attempt in range(self.config.max_retries):
            try:
                payload = {
                    "cmd": "request.get" if method.upper() == "GET" else "request.post",
                    "url": url,
                    "maxTimeout": timeout * 1000  # Convert to milliseconds
                }
                
                if session_id:
                    payload["session"] = session_id
                    
                if headers:
                    payload["headers"] = headers
                    
                if data and method.upper() == "POST":
                    payload["postData"] = data
                    
                logger.info(f"🌐 FlareSolverr request: {method} {url} (attempt {attempt + 1})")
                
                start_time = time.time()
                
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=timeout + 10)
                ) as session:
                    async with session.post(
                        self.config.endpoint,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    ) as response:
                        
                        response_data = await response.json()
                        response_time = time.time() - start_time
                        
                        if response.status != 200:
                            raise Exception(f"HTTP {response.status}: {response_data.get('message', 'Unknown error')}")
                            
                        if response_data.get("status") != "ok":
                            error_msg = response_data.get("message", "Unknown error")
                            if "timeout" in error_msg.lower() and attempt < self.config.max_retries - 1:
                                logger.warning(f"⚠️ Timeout on attempt {attempt + 1}, retrying...")
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            raise Exception(f"FlareSolverr error: {error_msg}")
                            
                        solution = response_data.get("solution", {})
                        
                        # Update session last used time
                        if session_id and session_id in self.sessions:
                            self.sessions[session_id].last_used = time.time()
                            
                        result = FlareSolverrResult(
                            success=True,
                            url=solution.get("url", url),
                            status=solution.get("status", 200),
                            headers=solution.get("headers", {}),
                            cookies=solution.get("cookies", []),
                            html=solution.get("response", ""),
                            message=f"Success in {response_time:.2f}s",
                            startTimestamp=response_data.get("startTimestamp", 0),
                            endTimestamp=response_data.get("endTimestamp", 0),
                            version=response_data.get("version", ""),
                            solution=solution,
                            session_id=session_id
                        )
                        
                        logger.info(f"✅ FlareSolverr success: {url} ({response_time:.2f}s)")
                        return result
                        
            except Exception as e:
                logger.error(f"❌ FlareSolverr attempt {attempt + 1} failed: {str(e)}")
                
                if attempt == self.config.max_retries - 1:
                    # Last attempt failed
                    return FlareSolverrResult(
                        success=False,
                        url=url,
                        message=f"All {self.config.max_retries} attempts failed: {str(e)}"
                    )
                    
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
                
        # Should not reach here
        return FlareSolverrResult(
            success=False,
            url=url,
            message="Maximum retries exceeded"
        )
        
    async def get_cookies_as_dict(self, result: FlareSolverrResult) -> Dict[str, str]:
        """Convert FlareSolverr cookies to dict format"""
        cookies = {}
        
        if result.cookies:
            for cookie in result.cookies:
                name = cookie.get("name")
                value = cookie.get("value")
                if name and value:
                    cookies[name] = value
                    
        return cookies
        
    async def get_headers_for_requests(self, result: FlareSolverrResult) -> Dict[str, str]:
        """Get headers suitable for requests library"""
        headers = {}
        
        if result.headers:
            # Filter out headers that requests shouldn't set manually
            skip_headers = {
                'content-length', 'content-encoding', 'transfer-encoding',
                'connection', 'upgrade', 'proxy-authenticate', 'proxy-authorization'
            }
            
            for key, value in result.headers.items():
                if key.lower() not in skip_headers:
                    headers[key] = value
                    
        return headers
        
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session_info in self.sessions.items():
            # Check if session is expired (10 minutes of inactivity)
            if current_time - session_info.last_used > (self.config.session_ttl / 1000):
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            try:
                await self.destroy_session(session_id)
            except Exception as e:
                logger.error(f"❌ Failed to cleanup session {session_id}: {str(e)}")
                
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired FlareSolverr sessions")
            
    async def get_status(self) -> Dict[str, Any]:
        """Get FlareSolverr status"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.config.endpoint.rstrip('/v1')}/") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'available': True,
                            'version': data.get('version', 'unknown'),
                            'active_sessions': len(self.sessions),
                            'endpoint': self.config.endpoint
                        }
                    else:
                        return {
                            'available': False,
                            'error': f'HTTP {response.status}',
                            'endpoint': self.config.endpoint
                        }
                        
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'endpoint': self.config.endpoint
            }

class FlareSolverrAdapter:
    """High-level adapter for FlareSolverr integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = FlareSolverrConfig(**config)
        self.client = FlareSolverrClient(self.config)
        self._background_cleanup_task = None
        
    async def initialize(self):
        """Initialize the adapter"""
        # Check if FlareSolverr is available
        status = await self.client.get_status()
        
        if not status['available']:
            if self.config.enabled:
                logger.warning(f"⚠️ FlareSolverr not available: {status['error']}")
            return
            
        logger.info(f"✅ FlareSolverr available: {status['version']}")
        
        # Start background cleanup task
        self._background_cleanup_task = asyncio.create_task(self._cleanup_loop())
        
    async def bypass_cloudflare(self, url: str, 
                              proxy: Optional[str] = None,
                              headers: Optional[Dict[str, str]] = None,
                              persistent_session: bool = True) -> Dict[str, Any]:
        """
        Bypass CloudFlare protection for a URL.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'status_code': int,
            'html_content': str,
            'cookies': dict,
            'headers': dict,
            'session_id': str (if persistent_session=True)
        }
        """
        
        if not self.config.enabled:
            return {
                'success': False,
                'url': url,
                'error': 'FlareSolverr is disabled'
            }
            
        try:
            session_id = None
            
            if persistent_session:
                # Create a session for cookie persistence
                session_id = await self.client.create_session(proxy=proxy)
                
            # Make the request
            result = await self.client.request(
                url=url,
                session_id=session_id,
                headers=headers
            )
            
            if result.success:
                cookies_dict = await self.client.get_cookies_as_dict(result)
                headers_dict = await self.client.get_headers_for_requests(result)
                
                return {
                    'success': True,
                    'url': result.url,
                    'status_code': result.status,
                    'html_content': result.html,
                    'cookies': cookies_dict,
                    'headers': headers_dict,
                    'response_time': (result.endTimestamp - result.startTimestamp) / 1000.0,
                    'session_id': session_id,
                    'version': result.version
                }
            else:
                # Clean up session on failure
                if session_id:
                    await self.client.destroy_session(session_id)
                    
                return {
                    'success': False,
                    'url': url,
                    'error': result.message
                }
                
        except Exception as e:
            logger.error(f"❌ FlareSolverr bypass failed: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e)
            }
            
    async def reuse_session(self, session_id: str, url: str,
                          headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Reuse an existing session for another request"""
        
        if session_id not in self.client.sessions:
            return {
                'success': False,
                'url': url,
                'error': f'Session {session_id} not found'
            }
            
        result = await self.client.request(
            url=url,
            session_id=session_id,
            headers=headers
        )
        
        if result.success:
            cookies_dict = await self.client.get_cookies_as_dict(result)
            headers_dict = await self.client.get_headers_for_requests(result)
            
            return {
                'success': True,
                'url': result.url,
                'status_code': result.status,
                'html_content': result.html,
                'cookies': cookies_dict,
                'headers': headers_dict,
                'response_time': (result.endTimestamp - result.startTimestamp) / 1000.0,
                'session_id': session_id
            }
        else:
            return {
                'success': False,
                'url': url,
                'error': result.message
            }
            
    async def destroy_session(self, session_id: str):
        """Destroy a specific session"""
        await self.client.destroy_session(session_id)
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        status = await self.client.get_status()
        
        return {
            'enabled': self.config.enabled,
            'endpoint': self.config.endpoint,
            'available': status['available'],
            'active_sessions': len(self.client.sessions),
            'config': asdict(self.config)
        }
        
    async def _cleanup_loop(self):
        """Background task for session cleanup"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                await self.client.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Session cleanup failed: {str(e)}")
                
    async def cleanup(self):
        """Clean up all resources"""
        # Cancel background task
        if self._background_cleanup_task:
            self._background_cleanup_task.cancel()
            try:
                await self._background_cleanup_task
            except asyncio.CancelledError:
                pass
                
        # Destroy all active sessions
        for session_id in list(self.client.sessions.keys()):
            try:
                await self.client.destroy_session(session_id)
            except Exception as e:
                logger.error(f"❌ Failed to cleanup session {session_id}: {str(e)}")

# Factory function
def create_flaresolverr_adapter(config: Dict[str, Any]) -> FlareSolverrAdapter:
    """Create and configure FlareSolverr adapter"""
    return FlareSolverrAdapter(config)

# Example usage
async def main():
    """Example usage of FlareSolverr adapter"""
    config = {
        'enabled': True,
        'endpoint': 'http://localhost:8191/v1',
        'timeout': 60,
        'max_retries': 3,
        'debug': True
    }
    
    adapter = create_flaresolverr_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Test CloudFlare bypass
        result = await adapter.bypass_cloudflare(
            'https://example.com',
            persistent_session=True
        )
        
        if result['success']:
            print(f"✅ Success: {result['url']}")
            print(f"Status: {result['status_code']}")
            print(f"Content length: {len(result['html_content'])}")
            print(f"Cookies: {len(result['cookies'])}")
            
            # Reuse session for another request
            if result.get('session_id'):
                result2 = await adapter.reuse_session(
                    result['session_id'],
                    'https://example.com/about'
                )
                
                if result2['success']:
                    print(f"✅ Session reuse success: {result2['url']}")
        else:
            print(f"❌ Failed: {result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
