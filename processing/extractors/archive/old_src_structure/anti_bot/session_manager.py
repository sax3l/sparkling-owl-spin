"""
Session management for anti-bot system.

Manages HTTP sessions, cookies, and session rotation strategies.
"""

import time
import uuid
import random
import logging
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

@dataclass
class SessionInfo:
    """Information about an HTTP session."""
    session_id: str
    domain: str
    created_at: datetime
    last_used: datetime
    request_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    cookies: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this session."""
        if self.request_count == 0:
            return 0.0
        return self.success_count / self.request_count

    @property
    def age_minutes(self) -> float:
        """Calculate age of session in minutes."""
        return (datetime.now() - self.created_at).total_seconds() / 60

class SessionManager:
    """Manages HTTP sessions with rotation and anti-detection features."""
    
    def __init__(self, max_requests_per_session: int = 100, 
                 max_session_age_minutes: int = 60,
                 session_pool_size: int = 10):
        self.max_requests_per_session = max_requests_per_session
        self.max_session_age_minutes = max_session_age_minutes
        self.session_pool_size = session_pool_size
        
        # Session storage
        self._sessions: Dict[str, requests.Session] = {}
        self._session_info: Dict[str, SessionInfo] = {}
        self._domain_sessions: Dict[str, List[str]] = {}
        
        # Configuration
        self._retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
    def create_session(self, domain: str, proxy: Optional[str] = None, 
                      user_agent: Optional[str] = None) -> str:
        """Create a new HTTP session for a domain."""
        session_id = f"{domain}_{uuid.uuid4().hex[:8]}"
        
        # Create requests session
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=self._retry_strategy))
        session.mount("https://", HTTPAdapter(max_retries=self._retry_strategy))
        
        # Configure proxy if provided
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        
        # Set user agent
        if user_agent:
            session.headers.update({"User-Agent": user_agent})
        
        # Store session
        self._sessions[session_id] = session
        self._session_info[session_id] = SessionInfo(
            session_id=session_id,
            domain=domain,
            created_at=datetime.now(),
            last_used=datetime.now(),
            proxy=proxy,
            user_agent=user_agent
        )
        
        # Add to domain mapping
        if domain not in self._domain_sessions:
            self._domain_sessions[domain] = []
        self._domain_sessions[domain].append(session_id)
        
        logger.info(f"Created new session {session_id} for domain {domain}")
        return session_id
    
    def get_session(self, domain: str, strategy: str = "round_robin") -> Optional[str]:
        """Get an active session for a domain."""
        self._cleanup_expired_sessions()
        
        domain_sessions = self._domain_sessions.get(domain, [])
        active_sessions = [
            sid for sid in domain_sessions 
            if sid in self._session_info and self._session_info[sid].is_active
        ]
        
        if not active_sessions:
            # Create new session if none available
            return self.create_session(domain)
        
        # Apply selection strategy
        if strategy == "round_robin":
            return self._round_robin_selection(active_sessions)
        elif strategy == "least_used":
            return self._least_used_selection(active_sessions)
        elif strategy == "random":
            return random.choice(active_sessions)
        else:
            return active_sessions[0]
    
    def use_session(self, session_id: str) -> Optional[requests.Session]:
        """Get session object for making requests."""
        if session_id not in self._sessions:
            logger.warning(f"Session {session_id} not found")
            return None
        
        session_info = self._session_info[session_id]
        session_info.last_used = datetime.now()
        session_info.request_count += 1
        
        # Check if session should be rotated
        if self._should_rotate_session(session_info):
            self._rotate_session(session_id)
            return None
        
        return self._sessions[session_id]
    
    def report_request_result(self, session_id: str, success: bool):
        """Report the result of a request made with this session."""
        if session_id in self._session_info:
            session_info = self._session_info[session_id]
            if success:
                session_info.success_count += 1
            else:
                session_info.failure_count += 1
    
    def invalidate_session(self, session_id: str, reason: str = "manual"):
        """Manually invalidate a session."""
        if session_id in self._session_info:
            self._session_info[session_id].is_active = False
            logger.info(f"Invalidated session {session_id}: {reason}")
    
    def get_session_stats(self, session_id: str) -> Optional[SessionInfo]:
        """Get statistics for a specific session."""
        return self._session_info.get(session_id)
    
    def get_domain_stats(self, domain: str) -> Dict[str, Any]:
        """Get statistics for all sessions of a domain."""
        domain_sessions = self._domain_sessions.get(domain, [])
        active_sessions = [
            self._session_info[sid] for sid in domain_sessions 
            if sid in self._session_info and self._session_info[sid].is_active
        ]
        
        if not active_sessions:
            return {"active_sessions": 0, "total_requests": 0, "avg_success_rate": 0.0}
        
        total_requests = sum(s.request_count for s in active_sessions)
        avg_success_rate = sum(s.success_rate for s in active_sessions) / len(active_sessions)
        
        return {
            "active_sessions": len(active_sessions),
            "total_requests": total_requests,
            "avg_success_rate": avg_success_rate,
            "oldest_session_age": max(s.age_minutes for s in active_sessions)
        }
    
    def _should_rotate_session(self, session_info: SessionInfo) -> bool:
        """Check if session should be rotated."""
        # Check request count limit
        if session_info.request_count >= self.max_requests_per_session:
            return True
        
        # Check age limit
        if session_info.age_minutes >= self.max_session_age_minutes:
            return True
        
        # Check failure rate
        if session_info.request_count > 10 and session_info.success_rate < 0.7:
            return True
        
        return False
    
    def _rotate_session(self, session_id: str):
        """Rotate a session by creating a new one."""
        if session_id not in self._session_info:
            return
        
        old_info = self._session_info[session_id]
        old_info.is_active = False
        
        # Create new session with similar properties
        self.create_session(
            domain=old_info.domain,
            proxy=old_info.proxy,
            user_agent=old_info.user_agent
        )
        
        logger.info(f"Rotated session {session_id} for domain {old_info.domain}")
    
    def _cleanup_expired_sessions(self):
        """Remove expired and inactive sessions."""
        expired_sessions = [
            sid for sid, info in self._session_info.items()
            if not info.is_active or info.age_minutes > self.max_session_age_minutes * 2
        ]
        
        for session_id in expired_sessions:
            self._remove_session(session_id)
    
    def _remove_session(self, session_id: str):
        """Remove session from all tracking."""
        if session_id in self._sessions:
            self._sessions[session_id].close()
            del self._sessions[session_id]
        
        if session_id in self._session_info:
            domain = self._session_info[session_id].domain
            del self._session_info[session_id]
            
            # Remove from domain mapping
            if domain in self._domain_sessions:
                self._domain_sessions[domain] = [
                    sid for sid in self._domain_sessions[domain] if sid != session_id
                ]
    
    def _round_robin_selection(self, session_ids: List[str]) -> str:
        """Select session using round-robin strategy."""
        # Simple round-robin based on least recently used
        return min(session_ids, key=lambda sid: self._session_info[sid].last_used)
    
    def _least_used_selection(self, session_ids: List[str]) -> str:
        """Select session with least request count."""
        return min(session_ids, key=lambda sid: self._session_info[sid].request_count)
    
    def cleanup_all_sessions(self):
        """Clean up all sessions (for shutdown)."""
        for session in self._sessions.values():
            session.close()
        
        self._sessions.clear()
        self._session_info.clear()
        self._domain_sessions.clear()
        
        logger.info("All sessions cleaned up")

# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

__all__ = ["SessionInfo", "SessionManager", "get_session_manager"]