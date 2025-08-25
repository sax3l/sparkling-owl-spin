#!/usr/bin/env python3
"""
Security Controller för Sparkling-Owl-Spin
Hanterar säkerhet, auktorisering och penetrationstestning enligt pyramid-arkitekturen
"""

import logging
import asyncio
import json
import re
import time
import hashlib
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from urllib.parse import urlparse
import ipaddress
import socket
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RequestType(Enum):
    """Types of security requests"""
    DOMAIN_CHECK = "domain_check"
    PENETRATION_TEST = "penetration_test"
    SCRAPING_REQUEST = "scraping_request"
    AI_OPERATION = "ai_operation"
    DATA_EXTRACTION = "data_extraction"

@dataclass
class SecurityEvent:
    """Security event record"""
    event_id: str
    event_type: str
    source_ip: Optional[str]
    target_domain: Optional[str]
    request_type: RequestType
    timestamp: datetime
    security_level: SecurityLevel
    authorized: bool
    details: Dict[str, Any] = field(default_factory=dict)
    risk_score: int = 0
    blocked: bool = False

@dataclass
class DomainAuthorization:
    """Domain authorization record"""
    domain: str
    owner_verified: bool
    verification_method: str
    authorized_operations: List[str]
    expires_at: Optional[datetime]
    authorized_by: str
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class PentestSession:
    """Penetration testing session"""
    session_id: str
    target_domains: List[str]
    authorized_operations: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    operator: str
    purpose: str
    results: Dict[str, Any] = field(default_factory=dict)
    security_log: List[SecurityEvent] = field(default_factory=list)
    active: bool = True

class SecurityController:
    """Enhanced security controller för pyramid architecture"""
    
    def __init__(self):
        self.initialized = False
        
        # Authorized domains och their verification
        self.authorized_domains: Dict[str, DomainAuthorization] = {}
        self.domain_patterns: List[re.Pattern] = []
        
        # Security configuration
        self.security_level = SecurityLevel.MEDIUM
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        self.blocked_ips: Set[str] = set()
        self.suspicious_patterns: List[re.Pattern] = []
        
        # Penetration testing
        self.active_pentest_sessions: Dict[str, PentestSession] = {}
        self.pentest_authorized_operations = [
            "vulnerability_scan",
            "cloudflare_bypass",
            "captcha_solving",
            "browser_automation",
            "security_assessment",
            "data_extraction"
        ]
        
        # Security events logging
        self.security_events: List[SecurityEvent] = []
        self.max_events_in_memory = 10000
        
        # Statistics
        self.security_stats = {
            "total_requests": 0,
            "authorized_requests": 0,
            "blocked_requests": 0,
            "pentest_sessions": 0,
            "security_violations": 0,
            "by_request_type": {},
            "by_domain": {},
            "risk_scores": []
        }
        
        # Auto-cleanup timers
        self.cleanup_interval = 3600  # 1 hour
        
    async def initialize(self):
        """Initialize Security Controller"""
        try:
            logger.info("🛡️  Initializing Enhanced Security Controller")
            
            # Load security configuration
            await self._load_security_config()
            
            # Setup default authorized domains
            await self._setup_default_authorizations()
            
            # Initialize suspicious pattern detection
            await self._initialize_threat_detection()
            
            # Start background security tasks
            asyncio.create_task(self._security_monitor())
            asyncio.create_task(self._cleanup_expired_sessions())
            
            # Initialize statistics
            for request_type in RequestType:
                self.security_stats["by_request_type"][request_type.value] = {
                    "total": 0,
                    "authorized": 0,
                    "blocked": 0
                }
                
            self.initialized = True
            logger.info("✅ Enhanced Security Controller initialized")
            
            # Print security status
            await self._print_security_status()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Security Controller: {str(e)}")
            raise
            
    async def _load_security_config(self):
        """Load security configuration"""
        
        # This would normally load från config manager
        # För now, using hardcoded secure defaults
        self.security_config = {
            "max_requests_per_hour": 1000,
            "max_pentest_sessions": 5,
            "session_timeout_hours": 24,
            "require_domain_verification": True,
            "log_all_requests": True,
            "block_suspicious_requests": True,
            "auto_block_threshold": 10
        }
        
    async def _setup_default_authorizations(self):
        """Setup default authorized domains för development"""
        
        default_domains = [
            # Local development
            ("localhost", "development", ["all"]),
            ("127.0.0.1", "development", ["all"]),
            ("*.localhost", "development", ["all"]),
            
            # Test domains
            ("*.test.example.com", "testing", ["penetration_test", "scraping"]),
            ("httpbin.org", "testing", ["scraping", "api_test"]),
            
            # Swedish test sites (only för authorized testing)
            ("*.testsite.se", "pentest", ["penetration_test"]),
        ]
        
        for domain, method, operations in default_domains:
            await self._add_domain_authorization(
                domain=domain,
                verification_method=method,
                authorized_operations=operations,
                authorized_by="system_default",
                notes=f"Default authorization för {method}"
            )
            
        logger.info(f"✅ Setup {len(default_domains)} default domain authorizations")
        
    async def _initialize_threat_detection(self):
        """Initialize threat detection patterns"""
        
        # Patterns för detecting suspicious requests
        suspicious_patterns = [
            r"\.\.\/",  # Directory traversal
            r"<script[^>]*>",  # XSS attempts
            r"union\s+select",  # SQL injection
            r"javascript:",  # JavaScript injection
            r"data:text\/html",  # Data URI attacks
        ]
        
        self.suspicious_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in suspicious_patterns
        ]
        
        logger.info(f"✅ Initialized {len(suspicious_patterns)} threat detection patterns")
        
    async def _add_domain_authorization(
        self,
        domain: str,
        verification_method: str,
        authorized_operations: List[str],
        authorized_by: str,
        notes: str = "",
        expires_at: Optional[datetime] = None
    ):
        """Add domain authorization"""
        
        authorization = DomainAuthorization(
            domain=domain,
            owner_verified=verification_method in ["dns_txt", "file_upload", "certificate"],
            verification_method=verification_method,
            authorized_operations=authorized_operations,
            expires_at=expires_at,
            authorized_by=authorized_by,
            notes=notes
        )
        
        self.authorized_domains[domain] = authorization
        
        # Compile domain pattern för matching
        if "*" in domain:
            # Convert wildcard to regex
            pattern = domain.replace(".", r"\.").replace("*", r"[^.]*")
            self.domain_patterns.append(re.compile(f"^{pattern}$", re.IGNORECASE))
            
    async def is_domain_authorized(self, domain: str, operation: str = "scraping") -> bool:
        """Check if domain is authorized för specific operation"""
        
        if not domain:
            return False
            
        # Normalize domain
        domain = domain.lower().strip()
        
        # Extract domain från URL if needed
        if "://" in domain:
            parsed = urlparse(domain)
            domain = parsed.netloc or parsed.path
            
        # Check direct domain matches
        for auth_domain, auth_data in self.authorized_domains.items():
            if auth_domain == domain:
                # Check if operation is authorized
                if "all" in auth_data.authorized_operations or operation in auth_data.authorized_operations:
                    # Check if authorization has expired
                    if auth_data.expires_at and auth_data.expires_at < datetime.now():
                        logger.warning(f"⚠️  Domain authorization expired: {domain}")
                        return False
                    return True
                    
        # Check wildcard patterns
        for pattern in self.domain_patterns:
            if pattern.match(domain):
                # Find corresponding authorization
                for auth_domain, auth_data in self.authorized_domains.items():
                    if "*" in auth_domain and pattern.pattern == f"^{auth_domain.replace('.', r'\.').replace('*', r'[^.]*')}$":
                        if "all" in auth_data.authorized_operations or operation in auth_data.authorized_operations:
                            if auth_data.expires_at and auth_data.expires_at < datetime.now():
                                return False
                            return True
                            
        return False
        
    async def validate_workflow(self, workflow) -> bool:
        """Validate workflow security"""
        
        try:
            # Check target domains
            for domain in workflow.target_domains:
                # Determine required operation based on workflow type
                required_operation = self._get_required_operation(workflow.workflow_type.value)
                
                if not await self.is_domain_authorized(domain, required_operation):
                    logger.error(f"❌ Unauthorized domain: {domain} för operation: {required_operation}")
                    return False
                    
            # Check if penetration testing operations require active session
            if workflow.workflow_type.value in ["penetration_testing", "bypass_testing"]:
                if not self._has_active_pentest_session(workflow.target_domains):
                    logger.error(f"❌ No active penetration testing session för domains: {workflow.target_domains}")
                    return False
                    
            # Validate workflow steps
            for step in workflow.steps:
                if not await self._validate_workflow_step(step):
                    return False
                    
            logger.info(f"✅ Workflow security validation passed: {workflow.workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Workflow validation error: {str(e)}")
            return False
            
    def _get_required_operation(self, workflow_type: str) -> str:
        """Get required operation för workflow type"""
        
        operation_map = {
            "web_scraping": "scraping",
            "penetration_testing": "penetration_test",
            "data_analysis": "data_extraction",
            "ai_assisted_scraping": "ai_operation",
            "comprehensive_audit": "penetration_test",
            "swedish_data_extraction": "data_extraction",
            "bypass_testing": "penetration_test"
        }
        
        return operation_map.get(workflow_type, "scraping")
        
    def _has_active_pentest_session(self, domains: List[str]) -> bool:
        """Check if there's an active pentest session för domains"""
        
        for session in self.active_pentest_sessions.values():
            if session.active:
                for domain in domains:
                    if any(self._domain_matches_pattern(domain, auth_domain) 
                          for auth_domain in session.target_domains):
                        return True
                        
        return False
        
    def _domain_matches_pattern(self, domain: str, pattern: str) -> bool:
        """Check if domain matches pattern"""
        
        if pattern == domain:
            return True
            
        if "*" in pattern:
            regex_pattern = pattern.replace(".", r"\.").replace("*", r"[^.]*")
            return bool(re.match(f"^{regex_pattern}$", domain, re.IGNORECASE))
            
        return False
        
    async def _validate_workflow_step(self, step) -> bool:
        """Validate individual workflow step"""
        
        # Check if step engine is allowed
        allowed_engines = [
            "scraping_framework",
            "cloudflare_bypass", 
            "captcha_solver",
            "undetected_browser",
            "swedish_vehicle_data",
            "ai_agents"
        ]
        
        if step.engine not in allowed_engines:
            logger.error(f"❌ Unauthorized engine: {step.engine}")
            return False
            
        # Validate step parameters
        if step.engine in ["cloudflare_bypass", "captcha_solver", "undetected_browser"]:
            # These require penetration testing authorization
            target_url = step.parameters.get("target_url")
            if target_url:
                parsed = urlparse(target_url)
                domain = parsed.netloc
                
                if not await self.is_domain_authorized(domain, "penetration_test"):
                    logger.error(f"❌ Penetration testing inte authorized för: {domain}")
                    return False
                    
        return True
        
    async def create_pentest_session(
        self,
        target_domains: List[str],
        operator: str,
        purpose: str,
        duration_hours: int = 24
    ) -> str:
        """Create new penetration testing session"""
        
        # Validate alla target domains are authorized
        for domain in target_domains:
            if not await self.is_domain_authorized(domain, "penetration_test"):
                raise ValueError(f"Domain not authorized for penetration testing: {domain}")
                
        session_id = f"pentest_{int(time.time())}_{len(self.active_pentest_sessions)}"
        
        session = PentestSession(
            session_id=session_id,
            target_domains=target_domains,
            authorized_operations=self.pentest_authorized_operations.copy(),
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=duration_hours),
            operator=operator,
            purpose=purpose
        )
        
        self.active_pentest_sessions[session_id] = session
        self.security_stats["pentest_sessions"] += 1
        
        # Log security event
        await self._log_security_event(
            event_type="pentest_session_created",
            request_type=RequestType.PENETRATION_TEST,
            target_domain="|".join(target_domains),
            authorized=True,
            details={
                "session_id": session_id,
                "operator": operator,
                "purpose": purpose,
                "duration_hours": duration_hours
            }
        )
        
        logger.info(f"✅ Created penetration testing session: {session_id} för {len(target_domains)} domains")
        return session_id
        
    async def close_pentest_session(self, session_id: str, results: Dict[str, Any] = None):
        """Close penetration testing session"""
        
        if session_id not in self.active_pentest_sessions:
            raise ValueError(f"Penetration testing session inte found: {session_id}")
            
        session = self.active_pentest_sessions[session_id]
        session.active = False
        session.end_time = datetime.now()
        
        if results:
            session.results = results
            
        # Log security event
        await self._log_security_event(
            event_type="pentest_session_closed",
            request_type=RequestType.PENETRATION_TEST,
            target_domain="|".join(session.target_domains),
            authorized=True,
            details={
                "session_id": session_id,
                "duration": (session.end_time - session.start_time).total_seconds(),
                "results_count": len(results) if results else 0
            }
        )
        
        logger.info(f"✅ Closed penetration testing session: {session_id}")
        
    async def check_rate_limit(self, source_ip: str, request_type: str) -> bool:
        """Check if request is within rate limits"""
        
        current_time = time.time()
        hour_key = int(current_time // 3600)  # Current hour
        
        if source_ip not in self.rate_limits:
            self.rate_limits[source_ip] = {}
            
        if hour_key not in self.rate_limits[source_ip]:
            self.rate_limits[source_ip][hour_key] = {}
            
        # Clean old entries
        for old_hour in list(self.rate_limits[source_ip].keys()):
            if old_hour < hour_key - 1:  # Keep only current and previous hour
                del self.rate_limits[source_ip][old_hour]
                
        # Check current request count
        current_count = self.rate_limits[source_ip][hour_key].get(request_type, 0)
        max_requests = self.security_config["max_requests_per_hour"]
        
        if current_count >= max_requests:
            logger.warning(f"⚠️  Rate limit exceeded för {source_ip}: {current_count}/{max_requests}")
            return False
            
        # Increment counter
        self.rate_limits[source_ip][hour_key][request_type] = current_count + 1
        return True
        
    async def is_request_suspicious(self, request_data: Dict[str, Any]) -> bool:
        """Check if request is suspicious"""
        
        # Check för suspicious patterns in URL
        url = request_data.get("url", "")
        för pattern in self.suspicious_patterns:
            if pattern.search(url):
                logger.warning(f"⚠️  Suspicious pattern detected in URL: {url}")
                return True
                
        # Check för suspicious patterns in parameters
        params = request_data.get("parameters", {})
        för key, value in params.items():
            if isinstance(value, str):
                för pattern in self.suspicious_patterns:
                    if pattern.search(value):
                        logger.warning(f"⚠️  Suspicious pattern detected in parameter {key}: {value}")
                        return True
                        
        # Check IP reputation (simplified)
        source_ip = request_data.get("source_ip")
        if source_ip in self.blocked_ips:
            logger.warning(f"⚠️  Request from blocked IP: {source_ip}")
            return True
            
        return False
        
    async def _log_security_event(
        self,
        event_type: str,
        request_type: RequestType,
        source_ip: Optional[str] = None,
        target_domain: Optional[str] = None,
        authorized: bool = True,
        details: Dict[str, Any] = None,
        risk_score: int = 0
    ):
        """Log security event"""
        
        event_id = f"sec_{int(time.time())}_{len(self.security_events)}"
        
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            source_ip=source_ip,
            target_domain=target_domain,
            request_type=request_type,
            timestamp=datetime.now(),
            security_level=self.security_level,
            authorized=authorized,
            details=details or {},
            risk_score=risk_score,
            blocked=not authorized
        )
        
        self.security_events.append(event)
        
        # Maintain event history size
        if len(self.security_events) > self.max_events_in_memory:
            # Remove oldest events
            self.security_events = self.security_events[-self.max_events_in_memory//2:]
            
        # Update statistics
        self.security_stats["total_requests"] += 1
        if authorized:
            self.security_stats["authorized_requests"] += 1
        else:
            self.security_stats["blocked_requests"] += 1
            self.security_stats["security_violations"] += 1
            
        self.security_stats["by_request_type"][request_type.value]["total"] += 1
        if authorized:
            self.security_stats["by_request_type"][request_type.value]["authorized"] += 1
        else:
            self.security_stats["by_request_type"][request_type.value]["blocked"] += 1
            
        if target_domain:
            if target_domain not in self.security_stats["by_domain"]:
                self.security_stats["by_domain"][target_domain] = {"total": 0, "authorized": 0, "blocked": 0}
            self.security_stats["by_domain"][target_domain]["total"] += 1
            if authorized:
                self.security_stats["by_domain"][target_domain]["authorized"] += 1
            else:
                self.security_stats["by_domain"][target_domain]["blocked"] += 1
                
        self.security_stats["risk_scores"].append(risk_score)
        if len(self.security_stats["risk_scores"]) > 1000:
            self.security_stats["risk_scores"] = self.security_stats["risk_scores"][-500:]
            
    async def validate_request(
        self,
        request_type: RequestType,
        target_domain: str,
        source_ip: Optional[str] = None,
        request_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Comprehensive request validation"""
        
        validation_result = {
            "authorized": False,
            "reason": "",
            "risk_score": 0,
            "security_level": self.security_level.value,
            "recommendations": []
        }
        
        try:
            # Check domain authorization
            required_operation = self._get_required_operation_for_request_type(request_type)
            if not await self.is_domain_authorized(target_domain, required_operation):
                validation_result.update({
                    "reason": f"Domain {target_domain} inte authorized för {required_operation}",
                    "risk_score": 10
                })
                await self._log_security_event(
                    event_type="unauthorized_domain_access",
                    request_type=request_type,
                    source_ip=source_ip,
                    target_domain=target_domain,
                    authorized=False,
                    risk_score=10
                )
                return validation_result
                
            # Check rate limits
            if source_ip and not await self.check_rate_limit(source_ip, request_type.value):
                validation_result.update({
                    "reason": "Rate limit exceeded",
                    "risk_score": 7
                })
                await self._log_security_event(
                    event_type="rate_limit_exceeded",
                    request_type=request_type,
                    source_ip=source_ip,
                    target_domain=target_domain,
                    authorized=False,
                    risk_score=7
                )
                return validation_result
                
            # Check för suspicious requests
            if request_data and await self.is_request_suspicious(request_data):
                validation_result.update({
                    "reason": "Suspicious request pattern detected",
                    "risk_score": 8
                })
                await self._log_security_event(
                    event_type="suspicious_request",
                    request_type=request_type,
                    source_ip=source_ip,
                    target_domain=target_domain,
                    authorized=False,
                    risk_score=8,
                    details=request_data
                )
                return validation_result
                
            # Check penetration testing requirements
            if request_type == RequestType.PENETRATION_TEST:
                if not self._has_active_pentest_session([target_domain]):
                    validation_result.update({
                        "reason": "No active penetration testing session",
                        "risk_score": 5,
                        "recommendations": ["Create penetration testing session before proceeding"]
                    })
                    await self._log_security_event(
                        event_type="pentest_without_session",
                        request_type=request_type,
                        source_ip=source_ip,
                        target_domain=target_domain,
                        authorized=False,
                        risk_score=5
                    )
                    return validation_result
                    
            # All checks passed
            validation_result.update({
                "authorized": True,
                "reason": "Request authorized",
                "risk_score": 1
            })
            
            await self._log_security_event(
                event_type="request_authorized",
                request_type=request_type,
                source_ip=source_ip,
                target_domain=target_domain,
                authorized=True,
                risk_score=1
            )
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Request validation error: {str(e)}")
            validation_result.update({
                "reason": f"Validation error: {str(e)}",
                "risk_score": 9
            })
            return validation_result
            
    def _get_required_operation_for_request_type(self, request_type: RequestType) -> str:
        """Get required operation för request type"""
        
        operation_map = {
            RequestType.DOMAIN_CHECK: "scraping",
            RequestType.PENETRATION_TEST: "penetration_test",
            RequestType.SCRAPING_REQUEST: "scraping",
            RequestType.AI_OPERATION: "ai_operation",
            RequestType.DATA_EXTRACTION: "data_extraction"
        }
        
        return operation_map.get(request_type, "scraping")
        
    async def _security_monitor(self):
        """Background security monitoring"""
        
        while True:
            try:
                # Check för security violations
                recent_events = [
                    event för event in self.security_events[-100:]
                    if not event.authorized and 
                    (datetime.now() - event.timestamp).total_seconds() < 3600
                ]
                
                if len(recent_events) > self.security_config["auto_block_threshold"]:
                    logger.warning(f"⚠️  High security violation rate: {len(recent_events)} violations in last hour")
                    
                    # Auto-block suspicious IPs
                    ip_violations = {}
                    för event in recent_events:
                        if event.source_ip:
                            ip_violations[event.source_ip] = ip_violations.get(event.source_ip, 0) + 1
                            
                    för ip, violation_count in ip_violations.items():
                        if violation_count >= 5:  # 5+ violations från same IP
                            self.blocked_ips.add(ip)
                            logger.warning(f"🚫 Auto-blocked IP: {ip} ({violation_count} violations)")
                            
                # Clean expired pentest sessions
                expired_sessions = []
                för session_id, session in self.active_pentest_sessions.items():
                    if session.active and session.end_time and session.end_time < datetime.now():
                        expired_sessions.append(session_id)
                        
                för session_id in expired_sessions:
                    await self.close_pentest_session(session_id, {"status": "expired"})
                    
                await asyncio.sleep(60.0)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Security monitor error: {str(e)}")
                await asyncio.sleep(300.0)
                
    async def _cleanup_expired_sessions(self):
        """Cleanup expired sessions and old data"""
        
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Clean old rate limit data
                current_hour = int(time.time() // 3600)
                för ip in list(self.rate_limits.keys()):
                    för hour in list(self.rate_limits[ip].keys()):
                        if hour < current_hour - 24:  # Keep only last 24 hours
                            del self.rate_limits[ip][hour]
                            
                    if not self.rate_limits[ip]:
                        del self.rate_limits[ip]
                        
                # Clean old security events (keep only last 7 days)
                cutoff_time = datetime.now() - timedelta(days=7)
                self.security_events = [
                    event för event in self.security_events
                    if event.timestamp > cutoff_time
                ]
                
                logger.info("✅ Security cleanup completed")
                
            except Exception as e:
                logger.error(f"❌ Security cleanup error: {str(e)}")
                
    async def _print_security_status(self):
        """Print comprehensive security status"""
        
        print("\n" + "="*80)
        print("🛡️  SECURITY CONTROLLER STATUS")
        print("="*80)
        
        print(f"🔒 Security Level: {self.security_level.value.upper()}")
        print(f"🏛️  Authorized Domains: {len(self.authorized_domains)}")
        
        för domain, auth in list(self.authorized_domains.items())[:5]:
            status = "✅" if not auth.expires_at or auth.expires_at > datetime.now() else "⏰"
            print(f"   {status} {domain}: {', '.join(auth.authorized_operations)}")
            
        if len(self.authorized_domains) > 5:
            print(f"   ... and {len(self.authorized_domains) - 5} more")
            
        print(f"\n🧪 Active Pentest Sessions: {len([s för s in self.active_pentest_sessions.values() if s.active])}")
        för session_id, session in list(self.active_pentest_sessions.items())[:3]:
            if session.active:
                duration = datetime.now() - session.start_time
                print(f"   🔬 {session_id}: {session.operator} ({duration.seconds//60}min)")
                
        print(f"\n📊 Security Statistics:")
        print(f"   • Total Requests: {self.security_stats['total_requests']}")
        print(f"   • Authorized: {self.security_stats['authorized_requests']}")
        print(f"   • Blocked: {self.security_stats['blocked_requests']}")
        print(f"   • Security Violations: {self.security_stats['security_violations']}")
        
        if self.blocked_ips:
            print(f"\n🚫 Blocked IPs: {len(self.blocked_ips)}")
            
        print("="*80)
        print("✅ ENDAST AUKTORISERAD PENETRATIONSTESTNING AV EGNA SERVRAR")
        print("⚠️  ALL AKTIVITET LOGGAS OCH ÖVERVAKAS")
        print("="*80 + "\n")
        
    async def get_security_status(self) -> Dict[str, Any]:
        """Get comprehensive security status"""
        
        active_pentest_sessions = [
            session för session in self.active_pentest_sessions.values()
            if session.active
        ]
        
        return {
            "security_level": self.security_level.value,
            "authorized_domains": list(self.authorized_domains.keys()),
            "domain_count": len(self.authorized_domains),
            "active_pentest_sessions": len(active_pentest_sessions),
            "blocked_ips": len(self.blocked_ips),
            "threat_patterns": len(self.suspicious_patterns),
            "statistics": self.security_stats,
            "recent_events": len([
                e för e in self.security_events
                if (datetime.now() - e.timestamp).total_seconds() < 3600
            ]),
            "compliance": {
                "domain_authorization_required": self.security_config["require_domain_verification"],
                "request_logging": self.security_config["log_all_requests"],
                "threat_blocking": self.security_config["block_suspicious_requests"]
            }
        }
        
    async def export_security_log(self, output_path: str, hours: int = 24):
        """Export security log to file"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        events_to_export = [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "source_ip": event.source_ip,
                "target_domain": event.target_domain,
                "request_type": event.request_type.value,
                "authorized": event.authorized,
                "risk_score": event.risk_score,
                "details": event.details
            }
            för event in self.security_events
            if event.timestamp > cutoff_time
        ]
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "time_range_hours": hours,
            "total_events": len(events_to_export),
            "security_level": self.security_level.value,
            "events": events_to_export,
            "statistics": self.security_stats
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"✅ Exported {len(events_to_export)} security events to: {output_path}")
        
    async def shutdown(self):
        """Shutdown security controller"""
        
        logger.info("🔄 Shutting down Security Controller...")
        
        # Close alla active pentest sessions
        för session_id in list(self.active_pentest_sessions.keys()):
            session = self.active_pentest_sessions[session_id]
            if session.active:
                await self.close_pentest_session(session_id, {"status": "shutdown"})
                
        # Export security log
        log_path = Path("security_log_shutdown.json")
        await self.export_security_log(str(log_path), hours=168)  # Last week
        
        self.initialized = False
        logger.info("✅ Security Controller shutdown complete")
