"""
Credential management for anti-bot system.

Manages login credentials, session handling, and authentication
for websites that require login to access content.
"""

import os
import json
import hashlib
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from cryptography.fernet import Fernet
import asyncio

from src.utils.logger import get_logger

logger = get_logger(__name__)

class AuthMethod(Enum):
    """Supported authentication methods"""
    FORM_LOGIN = "form_login"
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC_AUTH = "basic_auth"
    COOKIE_AUTH = "cookie_auth"
    TOKEN_AUTH = "token_auth"

class SessionStatus(Enum):
    """Session status states"""
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    PENDING = "pending"
    FAILED = "failed"

@dataclass
class Credential:
    """Credential information for a domain"""
    domain: str
    username: str
    password: str  # Will be encrypted
    auth_method: AuthMethod
    additional_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    use_count: int = 0
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'domain': self.domain,
            'username': self.username,
            'password': self.password,  # Already encrypted
            'auth_method': self.auth_method.value,
            'additional_data': self.additional_data,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'use_count': self.use_count,
            'is_active': self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Credential':
        """Create from dictionary"""
        return cls(
            domain=data['domain'],
            username=data['username'],
            password=data['password'],  # Already encrypted
            auth_method=AuthMethod(data['auth_method']),
            additional_data=data.get('additional_data', {}),
            created_at=datetime.fromisoformat(data['created_at']),
            last_used=datetime.fromisoformat(data['last_used']) if data.get('last_used') else None,
            use_count=data.get('use_count', 0),
            is_active=data.get('is_active', True)
        )

@dataclass
class Session:
    """Active session information"""
    domain: str
    credential_id: str
    session_id: str
    cookies: Dict[str, str] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    tokens: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.PENDING
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def age_minutes(self) -> float:
        """Get session age in minutes"""
        return (datetime.utcnow() - self.created_at).total_seconds() / 60
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()

class CredentialManager:
    """
    Manages credentials and sessions for authenticated scraping.
    
    Features:
    - Encrypted credential storage
    - Session management and reuse
    - Multiple authentication methods
    - Automatic session validation
    - Load balancing across credentials
    """
    
    def __init__(self, 
                 credentials_file: str = "data/credentials.json",
                 encryption_key: Optional[str] = None,
                 session_timeout: int = 3600,
                 max_concurrent_sessions: int = 5):
        self.credentials_file = credentials_file
        self.session_timeout = session_timeout
        self.max_concurrent_sessions = max_concurrent_sessions
        
        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate or load encryption key
            key_file = "data/.encryption_key"
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    self.cipher = Fernet(f.read())
            else:
                key = Fernet.generate_key()
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(key)
                self.cipher = Fernet(key)
        
        self.credentials: Dict[str, Credential] = {}
        self.sessions: Dict[str, Session] = {}
        self.domain_sessions: Dict[str, List[str]] = {}
        
        self._load_credentials()
    
    def add_credential(self,
                      domain: str,
                      username: str,
                      password: str,
                      auth_method: AuthMethod,
                      additional_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a new credential.
        
        Args:
            domain: Domain for the credential
            username: Username
            password: Password (will be encrypted)
            auth_method: Authentication method
            additional_data: Additional auth data (API keys, etc.)
            
        Returns:
            Credential ID
        """
        # Encrypt password
        encrypted_password = self.cipher.encrypt(password.encode()).decode()
        
        # Generate credential ID
        credential_id = hashlib.md5(f"{domain}:{username}".encode()).hexdigest()
        
        credential = Credential(
            domain=domain,
            username=username,
            password=encrypted_password,
            auth_method=auth_method,
            additional_data=additional_data or {}
        )
        
        self.credentials[credential_id] = credential
        self._save_credentials()
        
        logger.info(f"Added credential for {domain}:{username} (method: {auth_method.value})")
        return credential_id
    
    def get_credential(self, credential_id: str) -> Optional[Credential]:
        """Get credential by ID"""
        return self.credentials.get(credential_id)
    
    def get_credentials_for_domain(self, domain: str) -> List[Credential]:
        """Get all active credentials for a domain"""
        return [
            cred for cred in self.credentials.values()
            if cred.domain == domain and cred.is_active
        ]
    
    def get_decrypted_password(self, credential_id: str) -> Optional[str]:
        """Get decrypted password for a credential"""
        credential = self.credentials.get(credential_id)
        if not credential:
            return None
        
        try:
            return self.cipher.decrypt(credential.password.encode()).decode()
        except Exception as e:
            logger.error(f"Failed to decrypt password for {credential_id}: {e}")
            return None
    
    async def authenticate(self, 
                          domain: str,
                          credential_id: Optional[str] = None,
                          **auth_kwargs) -> Optional[Session]:
        """
        Authenticate and create a session.
        
        Args:
            domain: Target domain
            credential_id: Specific credential to use (optional)
            **auth_kwargs: Additional authentication parameters
            
        Returns:
            Active session or None if authentication failed
        """
        # Get credential
        if credential_id:
            credential = self.get_credential(credential_id)
            if not credential or not credential.is_active:
                logger.error(f"Invalid or inactive credential: {credential_id}")
                return None
        else:
            # Find best available credential for domain
            credentials = self.get_credentials_for_domain(domain)
            if not credentials:
                logger.error(f"No credentials available for domain: {domain}")
                return None
            
            # Use least recently used credential
            credential = min(credentials, key=lambda c: c.last_used or datetime.min)
            credential_id = next(k for k, v in self.credentials.items() if v == credential)
        
        # Check if we already have an active session
        existing_session = self._get_active_session(domain, credential_id)
        if existing_session:
            logger.info(f"Reusing existing session for {domain}:{credential.username}")
            existing_session.update_activity()
            return existing_session
        
        # Check concurrent session limit
        if len(self._get_domain_sessions(domain)) >= self.max_concurrent_sessions:
            logger.warning(f"Max concurrent sessions reached for {domain}")
            # Clean up old sessions
            self._cleanup_expired_sessions(domain)
        
        # Perform authentication
        session = await self._perform_authentication(credential, credential_id, **auth_kwargs)
        
        if session:
            # Update credential usage
            credential.last_used = datetime.utcnow()
            credential.use_count += 1
            self._save_credentials()
            
            # Store session
            self.sessions[session.session_id] = session
            if domain not in self.domain_sessions:
                self.domain_sessions[domain] = []
            self.domain_sessions[domain].append(session.session_id)
            
            logger.info(f"Authentication successful for {domain}:{credential.username}")
        
        return session
    
    async def _perform_authentication(self, 
                                    credential: Credential,
                                    credential_id: str,
                                    **auth_kwargs) -> Optional[Session]:
        """Perform the actual authentication based on method"""
        password = self.get_decrypted_password(credential_id)
        if not password:
            return None
        
        session_id = f"{credential.domain}_{credential.username}_{int(time.time())}"
        session = Session(
            domain=credential.domain,
            credential_id=credential_id,
            session_id=session_id,
            expires_at=datetime.utcnow() + timedelta(seconds=self.session_timeout)
        )
        
        try:
            if credential.auth_method == AuthMethod.FORM_LOGIN:
                success = await self._form_login(credential, password, session, **auth_kwargs)
            elif credential.auth_method == AuthMethod.OAUTH2:
                success = await self._oauth2_login(credential, session, **auth_kwargs)
            elif credential.auth_method == AuthMethod.API_KEY:
                success = await self._api_key_auth(credential, session, **auth_kwargs)
            elif credential.auth_method == AuthMethod.BASIC_AUTH:
                success = await self._basic_auth(credential, password, session, **auth_kwargs)
            elif credential.auth_method == AuthMethod.COOKIE_AUTH:
                success = await self._cookie_auth(credential, session, **auth_kwargs)
            elif credential.auth_method == AuthMethod.TOKEN_AUTH:
                success = await self._token_auth(credential, session, **auth_kwargs)
            else:
                logger.error(f"Unsupported auth method: {credential.auth_method}")
                return None
            
            if success:
                session.status = SessionStatus.ACTIVE
                return session
            else:
                session.status = SessionStatus.FAILED
                return None
                
        except Exception as e:
            logger.error(f"Authentication failed for {credential.domain}:{credential.username}: {e}")
            session.status = SessionStatus.FAILED
            return None
    
    async def _form_login(self, 
                         credential: Credential, 
                         password: str, 
                         session: Session,
                         **kwargs) -> bool:
        """Perform form-based login"""
        # This would typically use a browser automation tool
        # For now, return a mock implementation
        
        login_url = kwargs.get('login_url', f"https://{credential.domain}/login")
        username_field = kwargs.get('username_field', 'username')
        password_field = kwargs.get('password_field', 'password')
        submit_selector = kwargs.get('submit_selector', 'input[type="submit"]')
        
        # Mock successful login - in real implementation would use Selenium/Playwright
        session.cookies = {
            'session_id': f"sess_{int(time.time())}",
            'auth_token': f"token_{credential.username}"
        }
        
        logger.info(f"Form login completed for {credential.domain}:{credential.username}")
        return True
    
    async def _oauth2_login(self, credential: Credential, session: Session, **kwargs) -> bool:
        """Perform OAuth2 authentication"""
        client_id = credential.additional_data.get('client_id')
        client_secret = credential.additional_data.get('client_secret')
        
        if not client_id or not client_secret:
            logger.error("OAuth2 credentials missing client_id or client_secret")
            return False
        
        # Mock OAuth2 flow - in real implementation would handle full OAuth2
        session.tokens = {
            'access_token': f"oauth2_token_{int(time.time())}",
            'refresh_token': f"refresh_token_{int(time.time())}",
            'token_type': 'Bearer'
        }
        
        logger.info(f"OAuth2 login completed for {credential.domain}")
        return True
    
    async def _api_key_auth(self, credential: Credential, session: Session, **kwargs) -> bool:
        """Perform API key authentication"""
        api_key = credential.additional_data.get('api_key')
        if not api_key:
            logger.error("API key missing from credential")
            return False
        
        header_name = credential.additional_data.get('header_name', 'X-API-Key')
        session.headers[header_name] = api_key
        
        logger.info(f"API key auth configured for {credential.domain}")
        return True
    
    async def _basic_auth(self, 
                         credential: Credential, 
                         password: str, 
                         session: Session,
                         **kwargs) -> bool:
        """Perform HTTP Basic authentication"""
        import base64
        
        auth_string = f"{credential.username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        session.headers['Authorization'] = f"Basic {encoded_auth}"
        
        logger.info(f"Basic auth configured for {credential.domain}:{credential.username}")
        return True
    
    async def _cookie_auth(self, credential: Credential, session: Session, **kwargs) -> bool:
        """Perform cookie-based authentication"""
        cookies = credential.additional_data.get('cookies', {})
        if not cookies:
            logger.error("No cookies provided for cookie auth")
            return False
        
        session.cookies.update(cookies)
        
        logger.info(f"Cookie auth configured for {credential.domain}")
        return True
    
    async def _token_auth(self, credential: Credential, session: Session, **kwargs) -> bool:
        """Perform token-based authentication"""
        token = credential.additional_data.get('token')
        if not token:
            logger.error("No token provided for token auth")
            return False
        
        token_type = credential.additional_data.get('token_type', 'Bearer')
        session.headers['Authorization'] = f"{token_type} {token}"
        
        logger.info(f"Token auth configured for {credential.domain}")
        return True
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session and session.is_expired:
            self._invalidate_session(session_id)
            return None
        return session
    
    def get_session_for_domain(self, domain: str, credential_id: Optional[str] = None) -> Optional[Session]:
        """Get an active session for a domain"""
        return self._get_active_session(domain, credential_id)
    
    def _get_active_session(self, domain: str, credential_id: Optional[str] = None) -> Optional[Session]:
        """Get active session for domain/credential"""
        domain_sessions = self._get_domain_sessions(domain)
        
        for session_id in domain_sessions:
            session = self.sessions.get(session_id)
            if not session or session.is_expired:
                continue
            
            if credential_id and session.credential_id != credential_id:
                continue
            
            if session.status == SessionStatus.ACTIVE:
                return session
        
        return None
    
    def _get_domain_sessions(self, domain: str) -> List[str]:
        """Get all session IDs for a domain"""
        return self.domain_sessions.get(domain, [])
    
    def _invalidate_session(self, session_id: str):
        """Invalidate a session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.status = SessionStatus.INVALID
            
            # Remove from domain sessions
            domain_sessions = self.domain_sessions.get(session.domain, [])
            if session_id in domain_sessions:
                domain_sessions.remove(session_id)
            
            del self.sessions[session_id]
            logger.info(f"Invalidated session: {session_id}")
    
    def _cleanup_expired_sessions(self, domain: Optional[str] = None):
        """Clean up expired sessions"""
        domains_to_check = [domain] if domain else list(self.domain_sessions.keys())
        
        for domain in domains_to_check:
            session_ids = self.domain_sessions.get(domain, []).copy()
            for session_id in session_ids:
                session = self.sessions.get(session_id)
                if not session or session.is_expired or session.status != SessionStatus.ACTIVE:
                    self._invalidate_session(session_id)
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if a session is still active"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        # Could add additional validation logic here
        # e.g., make a test request to verify session is still valid
        
        return session.status == SessionStatus.ACTIVE
    
    def _load_credentials(self):
        """Load credentials from file"""
        if not os.path.exists(self.credentials_file):
            return
        
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
            
            for cred_id, cred_data in data.items():
                self.credentials[cred_id] = Credential.from_dict(cred_data)
            
            logger.info(f"Loaded {len(self.credentials)} credentials")
            
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
    
    def _save_credentials(self):
        """Save credentials to file"""
        try:
            os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
            
            data = {
                cred_id: cred.to_dict()
                for cred_id, cred in self.credentials.items()
            }
            
            with open(self.credentials_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    def remove_credential(self, credential_id: str) -> bool:
        """Remove a credential"""
        if credential_id not in self.credentials:
            return False
        
        credential = self.credentials[credential_id]
        
        # Invalidate related sessions
        for session_id in list(self.sessions.keys()):
            session = self.sessions[session_id]
            if session.credential_id == credential_id:
                self._invalidate_session(session_id)
        
        del self.credentials[credential_id]
        self._save_credentials()
        
        logger.info(f"Removed credential for {credential.domain}:{credential.username}")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get credential manager statistics"""
        active_credentials = sum(1 for cred in self.credentials.values() if cred.is_active)
        active_sessions = sum(1 for session in self.sessions.values() if session.status == SessionStatus.ACTIVE)
        
        domain_stats = {}
        for domain in set(cred.domain for cred in self.credentials.values()):
            domain_creds = len([cred for cred in self.credentials.values() if cred.domain == domain])
            domain_sessions = len(self._get_domain_sessions(domain))
            domain_stats[domain] = {
                'credentials': domain_creds,
                'active_sessions': domain_sessions
            }
        
        return {
            'total_credentials': len(self.credentials),
            'active_credentials': active_credentials,
            'total_sessions': len(self.sessions),
            'active_sessions': active_sessions,
            'domains': len(domain_stats),
            'domain_stats': domain_stats
        }