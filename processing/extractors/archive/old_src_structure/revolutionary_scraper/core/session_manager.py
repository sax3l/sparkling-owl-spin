"""
Revolutionary Session Manager
Advanced session and cookie management for unblockable scraping
Implements sophisticated session handling with persistence and rotation
"""

import asyncio
import json
import logging
import pickle
import time
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
from urllib.parse import urlparse
import hashlib
import random
import os

@dataclass
class SessionInfo:
    """Session information with metadata"""
    session_id: str
    cookies: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    user_agent: str = ""
    proxy_info: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_used: datetime = field(default_factory=datetime.now)
    request_count: int = 0
    success_count: int = 0
    domain: str = ""
    
    # Anti-detection features
    fingerprint_id: str = ""
    geo_location: str = ""
    timezone: str = ""
    language: str = "en-US"
    
    # Session persistence
    persistent: bool = True
    max_age: int = 3600  # 1 hour default
    max_requests: int = 1000
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        age_expired = (datetime.now() - self.created_at).total_seconds() > self.max_age
        request_limit_reached = self.request_count >= self.max_requests
        return age_expired or request_limit_reached
    
    @property
    def success_rate(self) -> float:
        """Calculate session success rate"""
        if self.request_count == 0:
            return 1.0
        return self.success_count / self.request_count

class SessionManager:
    """
    Revolutionary session manager with advanced persistence and rotation
    Implements intelligent session handling for maximum stealth
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Session pools
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.session_pool: Dict[str, aiohttp.ClientSession] = {}
        self.domain_sessions: Dict[str, List[str]] = {}
        
        # Configuration
        self.max_sessions_per_domain = config.get('max_sessions_per_domain', 5)
        self.session_rotation_interval = config.get('session_rotation_interval', 300)  # 5 minutes
        self.session_persistence_path = config.get('session_persistence_path', 'sessions')
        self.auto_save_interval = config.get('auto_save_interval', 60)  # 1 minute
        
        # Session policies
        self.session_timeout = config.get('session_timeout', 3600)  # 1 hour
        self.max_requests_per_session = config.get('max_requests_per_session', 1000)
        self.enable_session_rotation = config.get('enable_session_rotation', True)
        self.enable_cookie_persistence = config.get('enable_cookie_persistence', True)
        
        # Anti-detection features
        self.geo_consistency = config.get('geo_consistency', True)
        self.header_consistency = config.get('header_consistency', True)
        self.rate_limiting = config.get('rate_limiting', True)
        
        # Rate limiting
        self.request_delays: Dict[str, float] = {}
        self.last_request_times: Dict[str, datetime] = {}
        
        # Statistics
        self.session_stats = {
            'total_sessions_created': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'sessions_expired': 0,
            'cookies_persisted': 0
        }
        
        # Initialize storage
        self._init_storage()
        
        # Background tasks
        self._cleanup_task = None
        self._save_task = None
        
    def _init_storage(self):
        """Initialize session storage"""
        self.storage_path = Path(self.session_persistence_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.cookies_path = self.storage_path / 'cookies'
        self.cookies_path.mkdir(exist_ok=True)
        
        self.sessions_path = self.storage_path / 'sessions'
        self.sessions_path.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize session manager"""
        self.logger.info("Initializing revolutionary session manager...")
        
        # Load persisted sessions
        await self._load_persisted_sessions()
        
        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
        self._save_task = asyncio.create_task(self._auto_save_sessions())
        
        self.logger.info(f"Session manager initialized with {len(self.active_sessions)} sessions")
    
    async def get_session(self, domain: str = None, session_id: str = None, 
                         proxy_info: Dict = None) -> aiohttp.ClientSession:
        """
        Get or create optimized session for domain
        """
        if session_id:
            # Try to get specific session
            if session_id in self.active_sessions and session_id in self.session_pool:
                session_info = self.active_sessions[session_id]
                if not session_info.is_expired:
                    session_info.last_used = datetime.now()
                    return self.session_pool[session_id]
        
        # Get optimal session for domain
        optimal_session_id = await self._get_optimal_session_for_domain(domain, proxy_info)
        
        if optimal_session_id:
            return self.session_pool[optimal_session_id]
        
        # Create new session
        return await self._create_new_session(domain, proxy_info)
    
    async def _get_optimal_session_for_domain(self, domain: str, 
                                            proxy_info: Dict = None) -> Optional[str]:
        """
        Get optimal existing session for domain
        """
        if not domain:
            return None
            
        domain_session_ids = self.domain_sessions.get(domain, [])
        if not domain_session_ids:
            return None
        
        # Filter valid sessions
        valid_sessions = []
        for session_id in domain_session_ids:
            if session_id in self.active_sessions:
                session_info = self.active_sessions[session_id]
                if not session_info.is_expired:
                    valid_sessions.append((session_id, session_info))
        
        if not valid_sessions:
            return None
        
        # Select session based on strategy
        return self._select_optimal_session(valid_sessions, proxy_info)
    
    def _select_optimal_session(self, sessions: List[tuple], 
                              proxy_info: Dict = None) -> str:
        """
        Select optimal session from candidates
        """
        # Sort by success rate and recency
        sessions.sort(key=lambda x: (x[1].success_rate, -x[1].request_count), reverse=True)
        
        # Apply randomization for stealth
        if len(sessions) > 1 and random.random() < 0.3:  # 30% chance of non-optimal selection
            return random.choice(sessions[:min(3, len(sessions))])[0]
        
        return sessions[0][0]
    
    async def _create_new_session(self, domain: str = None, 
                                 proxy_info: Dict = None) -> aiohttp.ClientSession:
        """
        Create new session with advanced configuration
        """
        session_id = self._generate_session_id(domain)
        
        # Session configuration
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        # Configure proxy
        proxy_config = None
        if proxy_info:
            if proxy_info.get('auth_user') and proxy_info.get('auth_pass'):
                proxy_url = f"http://{proxy_info['auth_user']}:{proxy_info['auth_pass']}@{proxy_info['url']}"
            else:
                proxy_url = f"http://{proxy_info['url']}"
            proxy_config = proxy_url
        
        # Connector configuration
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True,
            enable_cleanup_closed=True
        )
        
        # Create session
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            trust_env=True
        )
        
        # Configure session with realistic headers
        headers = self._generate_session_headers(domain, proxy_info)
        session.headers.update(headers)
        
        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            headers=dict(headers),
            domain=domain or 'unknown',
            proxy_info=proxy_info,
            max_age=self.session_timeout,
            max_requests=self.max_requests_per_session
        )
        
        # Set proxy if configured
        if proxy_config:
            session._connector._proxy = proxy_config
        
        # Store session
        self.active_sessions[session_id] = session_info
        self.session_pool[session_id] = session
        
        # Update domain mapping
        if domain:
            if domain not in self.domain_sessions:
                self.domain_sessions[domain] = []
            self.domain_sessions[domain].append(session_id)
            
            # Limit sessions per domain
            if len(self.domain_sessions[domain]) > self.max_sessions_per_domain:
                old_session_id = self.domain_sessions[domain].pop(0)
                await self._cleanup_session(old_session_id)
        
        # Load persisted cookies for domain
        await self._load_domain_cookies(session_id, domain)
        
        self.session_stats['total_sessions_created'] += 1
        
        self.logger.debug(f"Created new session {session_id} for domain {domain}")
        return session
    
    def _generate_session_id(self, domain: str = None) -> str:
        """Generate unique session ID"""
        base_data = f"{domain}_{time.time()}_{random.random()}"
        return hashlib.md5(base_data.encode()).hexdigest()[:16]
    
    def _generate_session_headers(self, domain: str = None, 
                                 proxy_info: Dict = None) -> Dict[str, str]:
        """
        Generate realistic session headers
        """
        # Base headers
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self._generate_user_agent()
        }
        
        # Add geo-consistent headers if proxy info available
        if proxy_info and self.geo_consistency:
            country = proxy_info.get('country', 'US')
            if country == 'SE':
                headers['Accept-Language'] = 'sv-SE,sv;q=0.9,en-US;q=0.8,en;q=0.7'
            elif country == 'DE':
                headers['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.6'
            elif country == 'FR':
                headers['Accept-Language'] = 'fr-FR,fr;q=0.9,en;q=0.6'
        
        return headers
    
    def _generate_user_agent(self) -> str:
        """Generate realistic User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
        ]
        return random.choice(user_agents)
    
    async def update_session_cookies(self, session_id: str, cookies: Dict[str, Any]):
        """
        Update session cookies
        """
        if session_id in self.active_sessions:
            session_info = self.active_sessions[session_id]
            session_info.cookies.update(cookies)
            
            # Persist cookies if enabled
            if self.enable_cookie_persistence:
                await self._save_session_cookies(session_id)
                self.session_stats['cookies_persisted'] += 1
    
    async def report_request_result(self, session_id: str, success: bool):
        """
        Report request result for session analytics
        """
        if session_id in self.active_sessions:
            session_info = self.active_sessions[session_id]
            session_info.request_count += 1
            session_info.last_used = datetime.now()
            
            if success:
                session_info.success_count += 1
                self.session_stats['successful_requests'] += 1
            
            self.session_stats['total_requests'] += 1
            
            # Apply rate limiting
            if self.rate_limiting:
                await self._apply_rate_limiting(session_id)
    
    async def _apply_rate_limiting(self, session_id: str):
        """
        Apply intelligent rate limiting
        """
        if session_id not in self.last_request_times:
            self.last_request_times[session_id] = datetime.now()
            return
        
        # Calculate delay based on session history
        session_info = self.active_sessions.get(session_id)
        if not session_info:
            return
        
        # Base delay with randomization
        base_delay = random.uniform(0.5, 2.0)
        
        # Adjust based on success rate
        if session_info.success_rate < 0.8:
            base_delay *= 2  # Slower if many failures
        
        # Apply delay
        last_request = self.last_request_times[session_id]
        time_since_last = (datetime.now() - last_request).total_seconds()
        
        if time_since_last < base_delay:
            await asyncio.sleep(base_delay - time_since_last)
        
        self.last_request_times[session_id] = datetime.now()
    
    async def _load_domain_cookies(self, session_id: str, domain: str):
        """
        Load persisted cookies for domain
        """
        if not domain or not self.enable_cookie_persistence:
            return
        
        cookie_file = self.cookies_path / f"{domain}.pkl"
        if cookie_file.exists():
            try:
                with open(cookie_file, 'rb') as f:
                    cookies = pickle.load(f)
                
                session_info = self.active_sessions[session_id]
                session_info.cookies.update(cookies)
                
                # Apply cookies to session
                if session_id in self.session_pool:
                    session = self.session_pool[session_id]
                    for name, value in cookies.items():
                        if isinstance(value, dict):
                            session.cookie_jar.update_cookies({name: value.get('value', '')})
                        else:
                            session.cookie_jar.update_cookies({name: value})
                
                self.logger.debug(f"Loaded {len(cookies)} cookies for domain {domain}")
                
            except Exception as e:
                self.logger.warning(f"Failed to load cookies for {domain}: {e}")
    
    async def _save_session_cookies(self, session_id: str):
        """
        Save session cookies to disk
        """
        if session_id not in self.active_sessions:
            return
        
        session_info = self.active_sessions[session_id]
        if not session_info.cookies or not session_info.domain:
            return
        
        cookie_file = self.cookies_path / f"{session_info.domain}.pkl"
        try:
            with open(cookie_file, 'wb') as f:
                pickle.dump(session_info.cookies, f)
        except Exception as e:
            self.logger.warning(f"Failed to save cookies for {session_info.domain}: {e}")
    
    async def _load_persisted_sessions(self):
        """
        Load persisted sessions from disk
        """
        session_files = list(self.sessions_path.glob('*.json'))
        loaded_count = 0
        
        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Recreate session info
                session_info = SessionInfo(
                    session_id=session_data['session_id'],
                    cookies=session_data.get('cookies', {}),
                    headers=session_data.get('headers', {}),
                    domain=session_data.get('domain', 'unknown'),
                    created_at=datetime.fromisoformat(session_data['created_at']),
                    last_used=datetime.fromisoformat(session_data['last_used']),
                    request_count=session_data.get('request_count', 0),
                    success_count=session_data.get('success_count', 0)
                )
                
                # Only load if not expired
                if not session_info.is_expired:
                    # Recreate HTTP session
                    session = await self._recreate_http_session(session_info)
                    
                    self.active_sessions[session_info.session_id] = session_info
                    self.session_pool[session_info.session_id] = session
                    
                    # Update domain mapping
                    if session_info.domain not in self.domain_sessions:
                        self.domain_sessions[session_info.domain] = []
                    self.domain_sessions[session_info.domain].append(session_info.session_id)
                    
                    loaded_count += 1
                
            except Exception as e:
                self.logger.warning(f"Failed to load session from {session_file}: {e}")
        
        self.logger.info(f"Loaded {loaded_count} persisted sessions")
    
    async def _recreate_http_session(self, session_info: SessionInfo) -> aiohttp.ClientSession:
        """
        Recreate HTTP session from session info
        """
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
        
        session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=session_info.headers
        )
        
        # Restore cookies
        for name, value in session_info.cookies.items():
            if isinstance(value, dict):
                session.cookie_jar.update_cookies({name: value.get('value', '')})
            else:
                session.cookie_jar.update_cookies({name: value})
        
        return session
    
    async def _cleanup_expired_sessions(self):
        """
        Background task to cleanup expired sessions
        """
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                expired_session_ids = []
                for session_id, session_info in self.active_sessions.items():
                    if session_info.is_expired:
                        expired_session_ids.append(session_id)
                
                for session_id in expired_session_ids:
                    await self._cleanup_session(session_id)
                    self.session_stats['sessions_expired'] += 1
                
                if expired_session_ids:
                    self.logger.info(f"Cleaned up {len(expired_session_ids)} expired sessions")
                    
            except Exception as e:
                self.logger.error(f"Error in session cleanup: {e}")
    
    async def _cleanup_session(self, session_id: str):
        """
        Clean up specific session
        """
        # Save session data before cleanup
        if session_id in self.active_sessions:
            await self._save_session_data(session_id)
        
        # Close HTTP session
        if session_id in self.session_pool:
            session = self.session_pool[session_id]
            await session.close()
            del self.session_pool[session_id]
        
        # Remove from active sessions
        if session_id in self.active_sessions:
            session_info = self.active_sessions[session_id]
            
            # Remove from domain mapping
            if session_info.domain in self.domain_sessions:
                try:
                    self.domain_sessions[session_info.domain].remove(session_id)
                except ValueError:
                    pass
            
            del self.active_sessions[session_id]
    
    async def _save_session_data(self, session_id: str):
        """
        Save session data to disk
        """
        if session_id not in self.active_sessions:
            return
        
        session_info = self.active_sessions[session_id]
        
        session_data = {
            'session_id': session_info.session_id,
            'cookies': session_info.cookies,
            'headers': session_info.headers,
            'domain': session_info.domain,
            'created_at': session_info.created_at.isoformat(),
            'last_used': session_info.last_used.isoformat(),
            'request_count': session_info.request_count,
            'success_count': session_info.success_count
        }
        
        session_file = self.sessions_path / f"{session_id}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Failed to save session {session_id}: {e}")
    
    async def _auto_save_sessions(self):
        """
        Background task to auto-save sessions
        """
        while True:
            try:
                await asyncio.sleep(self.auto_save_interval)
                
                for session_id in list(self.active_sessions.keys()):
                    await self._save_session_data(session_id)
                    
            except Exception as e:
                self.logger.error(f"Error in auto-save: {e}")
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive session statistics
        """
        active_sessions_count = len(self.active_sessions)
        total_requests = self.session_stats['total_requests']
        successful_requests = self.session_stats['successful_requests']
        
        # Domain statistics
        domain_stats = {}
        for domain, session_ids in self.domain_sessions.items():
            valid_sessions = [sid for sid in session_ids if sid in self.active_sessions]
            domain_stats[domain] = {
                'active_sessions': len(valid_sessions),
                'total_requests': sum(self.active_sessions[sid].request_count for sid in valid_sessions),
                'success_rate': sum(self.active_sessions[sid].success_rate for sid in valid_sessions) / max(1, len(valid_sessions))
            }
        
        return {
            'active_sessions': active_sessions_count,
            'total_sessions_created': self.session_stats['total_sessions_created'],
            'sessions_expired': self.session_stats['sessions_expired'],
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'overall_success_rate': successful_requests / max(1, total_requests),
            'cookies_persisted': self.session_stats['cookies_persisted'],
            'domain_stats': domain_stats,
            'average_requests_per_session': total_requests / max(1, active_sessions_count)
        }
    
    async def close(self):
        """
        Clean up session manager
        """
        # Cancel background tasks
        if self._cleanup_task:
            self._cleanup_task.cancel()
        if self._save_task:
            self._save_task.cancel()
        
        # Close all sessions
        for session_id in list(self.session_pool.keys()):
            await self._cleanup_session(session_id)
        
        self.logger.info("Session manager shutdown complete")
