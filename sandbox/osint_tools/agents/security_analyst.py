"""
Security Analyst Agent for Sparkling Owl Spin
Advanced security analysis and bypass capabilities
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
import hashlib
import re

from core.base_classes import BaseAgent, Priority
from core.registry import get_registry
from engines.bypass.cloudflare_bypass import CloudflareBypass
from engines.bypass.captcha_solver import CaptchaSolver
from engines.pentesting.vulnerability_scanner import VulnerabilityScanner

logger = logging.getLogger(__name__)

class SecurityAnalyst(BaseAgent):
    """
    Specialized agent for security analysis and bypass operations
    Omdöpt från security_agent.py enligt pyramidarkitekturen
    """
    
    def __init__(self, agent_id: str = "security_analyst"):
        capabilities = [
            "security_analysis",
            "vulnerability_scanning", 
            "bypass_detection",
            "captcha_solving",
            "firewall_analysis",
            "bot_detection_evasion",
            "threat_assessment"
        ]
        
        super().__init__(
            agent_id=agent_id,
            name="Security Analyst",
            capabilities=capabilities
        )
        
        # Security tools
        self.bypass_engines: Dict[str, Any] = {}
        self.vulnerability_scanners: Dict[str, Any] = {}
        self.captcha_solvers: Dict[str, Any] = {}
        
        # Security configuration
        self.security_level = "high"  # low, medium, high, paranoid
        self.threat_threshold = 0.7
        self.automatic_bypass = True
        self.logging_enabled = True
        
        # Detection patterns
        self.protection_patterns = {
            'cloudflare': [
                re.compile(r'cloudflare', re.IGNORECASE),
                re.compile(r'cf-ray', re.IGNORECASE),
                re.compile(r'__cfduid', re.IGNORECASE)
            ],
            'incapsula': [
                re.compile(r'incapsula', re.IGNORECASE),
                re.compile(r'incap_ses', re.IGNORECASE)
            ],
            'akamai': [
                re.compile(r'akamai', re.IGNORECASE),
                re.compile(r'_abck', re.IGNORECASE)
            ],
            'datadome': [
                re.compile(r'datadome', re.IGNORECASE),
                re.compile(r'dd_cookie', re.IGNORECASE)
            ],
            'recaptcha': [
                re.compile(r'recaptcha', re.IGNORECASE),
                re.compile(r'g-recaptcha', re.IGNORECASE)
            ],
            'hcaptcha': [
                re.compile(r'hcaptcha', re.IGNORECASE),
                re.compile(r'h-captcha', re.IGNORECASE)
            ]
        }
        
        # Threat intelligence
        self.known_threats: Dict[str, Any] = {}
        self.security_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = 3600  # 1 hour
        
    async def start(self) -> bool:
        """Start the security analyst"""
        success = await super().start()
        if success:
            await self._initialize_security_tools()
        return success
        
    async def _initialize_security_tools(self):
        """Initialize security and bypass tools"""
        try:
            registry = await get_registry()
            
            # Initialize Cloudflare bypass
            cf_bypass = CloudflareBypass("cloudflare_bypass", "Cloudflare Bypass Engine")
            await registry.register_service(cf_bypass)
            await cf_bypass.start()
            self.bypass_engines['cloudflare'] = cf_bypass
            
            # Initialize captcha solver
            captcha_solver = CaptchaSolver("captcha_solver", "Captcha Solving Engine")
            await registry.register_service(captcha_solver)
            await captcha_solver.start()
            self.captcha_solvers['default'] = captcha_solver
            
            # Initialize vulnerability scanner
            vuln_scanner = VulnerabilityScanner("vuln_scanner", "Vulnerability Scanner")
            await registry.register_service(vuln_scanner)
            await vuln_scanner.start()
            self.vulnerability_scanners['default'] = vuln_scanner
            
            self.logger.info(f"Initialized security tools: {len(self.bypass_engines)} bypass engines, "
                           f"{len(self.captcha_solvers)} captcha solvers, "
                           f"{len(self.vulnerability_scanners)} scanners")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize security tools: {e}")
            
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a security analysis task"""
        task_start = datetime.utcnow()
        task_id = task.get('id', 'unknown')
        
        try:
            # Validate task
            if not await self._validate_security_task(task):
                return {
                    'status': 'failed',
                    'error': 'Invalid security task format',
                    'task_id': task_id
                }
                
            self.current_task = task
            
            # Determine task type and execute
            task_type = task.get('type', '')
            data = task.get('data', {})
            
            if task_type == 'security_analysis':
                result = await self._perform_security_analysis(data)
            elif task_type == 'bypass_protection':
                result = await self._bypass_protection(data)
            elif task_type == 'vulnerability_scan':
                result = await self._perform_vulnerability_scan(data)
            elif task_type == 'captcha_solve':
                result = await self._solve_captcha(data)
            elif task_type == 'threat_assessment':
                result = await self._assess_threat(data)
            else:
                raise ValueError(f"Unknown security task type: {task_type}")
                
            # Update performance metrics
            execution_time = (datetime.utcnow() - task_start).total_seconds()
            self.performance_metrics['tasks_completed'] += 1
            current_avg = self.performance_metrics['average_execution_time']
            total_tasks = self.performance_metrics['tasks_completed']
            self.performance_metrics['average_execution_time'] = (
                (current_avg * (total_tasks - 1)) + execution_time
            ) / total_tasks
            
            return {
                'status': 'completed',
                'result': result,
                'task_id': task_id,
                'execution_time': execution_time,
                'security_level': self.security_level
            }
            
        except Exception as e:
            self.logger.error(f"Security task execution failed: {e}")
            self.performance_metrics['tasks_failed'] += 1
            return {
                'status': 'failed',
                'error': str(e),
                'task_id': task_id
            }
        finally:
            self.current_task = None
            
    async def _perform_security_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive security analysis"""
        
        url = data.get('url')
        response_data = data.get('response_data', {})
        headers = data.get('headers', {})
        content = data.get('content', '')
        
        # Check cache first
        cache_key = self._generate_cache_key(url, 'security_analysis')
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
            
        analysis_result = {
            'url': url,
            'timestamp': datetime.utcnow().isoformat(),
            'protections_detected': [],
            'security_headers': self._analyze_security_headers(headers),
            'content_security': self._analyze_content_security(content),
            'threat_level': 'low',
            'recommendations': []
        }
        
        # Detect protections
        protections = await self._detect_protections(content, headers, response_data)
        analysis_result['protections_detected'] = protections
        
        # Calculate threat level
        threat_score = self._calculate_threat_score(protections, headers, content)
        if threat_score > 0.8:
            analysis_result['threat_level'] = 'critical'
        elif threat_score > 0.6:
            analysis_result['threat_level'] = 'high'
        elif threat_score > 0.4:
            analysis_result['threat_level'] = 'medium'
        else:
            analysis_result['threat_level'] = 'low'
            
        # Generate recommendations
        analysis_result['recommendations'] = self._generate_security_recommendations(
            protections, headers, threat_score
        )
        
        # Cache result
        self._store_in_cache(cache_key, analysis_result)
        
        return analysis_result
        
    async def _detect_protections(self, content: str, headers: Dict[str, str], 
                                response_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect various protection mechanisms"""
        
        protections = []
        
        # Check headers for protection signatures
        header_str = ' '.join([f"{k}: {v}" for k, v in headers.items()])
        
        for protection_name, patterns in self.protection_patterns.items():
            for pattern in patterns:
                if pattern.search(header_str) or pattern.search(content):
                    protections.append({
                        'type': protection_name,
                        'detection_method': 'pattern_match',
                        'confidence': 0.8,
                        'details': f'Detected via {pattern.pattern}'
                    })
                    break
                    
        # Specific detection logic
        
        # Cloudflare detection
        if any(header.lower().startswith('cf-') for header in headers.keys()):
            protections.append({
                'type': 'cloudflare',
                'detection_method': 'header_analysis',
                'confidence': 0.95,
                'details': 'Cloudflare headers detected'
            })
            
        # Rate limiting detection
        if any(code in [429, 503] for code in [response_data.get('status_code')]):
            protections.append({
                'type': 'rate_limiting',
                'detection_method': 'status_code',
                'confidence': 0.9,
                'details': f'Rate limiting status code: {response_data.get("status_code")}'
            })
            
        # Bot detection patterns
        bot_indicators = [
            'please enable javascript',
            'checking your browser',
            'verify you are human',
            'automated requests',
            'suspicious activity'
        ]
        
        content_lower = content.lower()
        for indicator in bot_indicators:
            if indicator in content_lower:
                protections.append({
                    'type': 'bot_detection',
                    'detection_method': 'content_analysis',
                    'confidence': 0.7,
                    'details': f'Bot detection phrase: {indicator}'
                })
                break
                
        return protections
        
    def _analyze_security_headers(self, headers: Dict[str, str]) -> Dict[str, Any]:
        """Analyze security-related headers"""
        
        security_headers = {
            'content_security_policy': headers.get('content-security-policy'),
            'strict_transport_security': headers.get('strict-transport-security'),
            'x_frame_options': headers.get('x-frame-options'),
            'x_content_type_options': headers.get('x-content-type-options'),
            'x_xss_protection': headers.get('x-xss-protection'),
            'referrer_policy': headers.get('referrer-policy')
        }
        
        # Security score
        security_score = 0
        max_score = len(security_headers)
        
        for header, value in security_headers.items():
            if value:
                security_score += 1
                
        return {
            'headers_present': security_headers,
            'security_score': security_score / max_score,
            'missing_headers': [k for k, v in security_headers.items() if not v]
        }
        
    def _analyze_content_security(self, content: str) -> Dict[str, Any]:
        """Analyze content for security indicators"""
        
        # Look for common security patterns
        patterns = {
            'inline_scripts': re.findall(r'<script[^>]*>.*?</script>', content, re.DOTALL),
            'external_scripts': re.findall(r'<script[^>]*src=[\'"](.*?)[\'"]', content),
            'forms': re.findall(r'<form[^>]*>', content),
            'iframes': re.findall(r'<iframe[^>]*>', content)
        }
        
        return {
            'inline_scripts_count': len(patterns['inline_scripts']),
            'external_scripts_count': len(patterns['external_scripts']),
            'forms_count': len(patterns['forms']),
            'iframes_count': len(patterns['iframes']),
            'external_domains': list(set(self._extract_domains_from_scripts(patterns['external_scripts'])))
        }
        
    def _extract_domains_from_scripts(self, script_urls: List[str]) -> List[str]:
        """Extract domains from script URLs"""
        domains = []
        for url in script_urls:
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                if domain:
                    domains.append(domain)
            except:
                continue
        return domains
        
    def _calculate_threat_score(self, protections: List[Dict[str, Any]], 
                               headers: Dict[str, str], content: str) -> float:
        """Calculate overall threat score"""
        
        score = 0.0
        
        # Protection mechanisms increase threat score
        for protection in protections:
            confidence = protection.get('confidence', 0.5)
            if protection['type'] in ['cloudflare', 'incapsula', 'akamai']:
                score += 0.3 * confidence
            elif protection['type'] in ['recaptcha', 'hcaptcha']:
                score += 0.2 * confidence
            elif protection['type'] == 'bot_detection':
                score += 0.4 * confidence
            elif protection['type'] == 'rate_limiting':
                score += 0.3 * confidence
                
        # Missing security headers reduce threat score (paradox - easier to exploit)
        security_headers_count = len([h for h in ['content-security-policy', 
                                                 'strict-transport-security',
                                                 'x-frame-options'] 
                                     if h in headers])
        if security_headers_count < 3:
            score -= 0.1 * (3 - security_headers_count)
            
        return max(0.0, min(1.0, score))
        
    def _generate_security_recommendations(self, protections: List[Dict[str, Any]], 
                                         headers: Dict[str, str], 
                                         threat_score: float) -> List[str]:
        """Generate security recommendations"""
        
        recommendations = []
        
        # Protection-specific recommendations
        protection_types = [p['type'] for p in protections]
        
        if 'cloudflare' in protection_types:
            recommendations.append("Consider using Cloudflare bypass techniques")
            recommendations.append("Implement request header randomization")
            
        if any(captcha in protection_types for captcha in ['recaptcha', 'hcaptcha']):
            recommendations.append("Implement captcha solving capability")
            recommendations.append("Consider using slower request rates")
            
        if 'bot_detection' in protection_types:
            recommendations.append("Implement browser fingerprint randomization")
            recommendations.append("Use residential proxy rotation")
            
        if 'rate_limiting' in protection_types:
            recommendations.append("Implement exponential backoff")
            recommendations.append("Distribute requests across multiple IP addresses")
            
        # General recommendations based on threat score
        if threat_score > 0.7:
            recommendations.append("Use advanced stealth techniques")
            recommendations.append("Consider manual inspection required")
        elif threat_score > 0.5:
            recommendations.append("Implement medium-level evasion techniques")
        else:
            recommendations.append("Standard scraping techniques should work")
            
        return recommendations
        
    async def _bypass_protection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to bypass detected protections"""
        
        url = data.get('url')
        protection_type = data.get('protection_type')
        
        if protection_type == 'cloudflare' and 'cloudflare' in self.bypass_engines:
            engine = self.bypass_engines['cloudflare']
            return await engine.process(url, data)
        else:
            return {
                'success': False,
                'error': f'No bypass engine available for {protection_type}'
            }
            
    async def _solve_captcha(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve captcha challenges"""
        
        captcha_type = data.get('captcha_type', 'recaptcha')
        
        if 'default' in self.captcha_solvers:
            engine = self.captcha_solvers['default']
            return await engine.process(captcha_type, data)
        else:
            return {
                'success': False,
                'error': 'No captcha solver available'
            }
            
    async def _perform_vulnerability_scan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform vulnerability scanning"""
        
        if 'default' in self.vulnerability_scanners:
            scanner = self.vulnerability_scanners['default']
            return await scanner.process(data.get('url'), data)
        else:
            return {
                'success': False,
                'error': 'No vulnerability scanner available'
            }
            
    async def _assess_threat(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess threat level for a target"""
        
        url = data.get('url')
        
        # Perform quick security analysis
        analysis = await self._perform_security_analysis(data)
        
        threat_level = analysis.get('threat_level', 'unknown')
        protections = analysis.get('protections_detected', [])
        
        return {
            'url': url,
            'threat_level': threat_level,
            'protection_count': len(protections),
            'requires_advanced_techniques': threat_level in ['high', 'critical'],
            'recommended_approach': self._recommend_approach(threat_level, protections)
        }
        
    def _recommend_approach(self, threat_level: str, protections: List[Dict[str, Any]]) -> str:
        """Recommend scraping approach based on threat assessment"""
        
        if threat_level == 'critical':
            return "manual_analysis_required"
        elif threat_level == 'high':
            return "advanced_bypass_techniques"
        elif threat_level == 'medium':
            return "standard_evasion_techniques"
        else:
            return "basic_scraping_sufficient"
            
    def _generate_cache_key(self, url: str, operation: str) -> str:
        """Generate cache key for security analysis"""
        return hashlib.md5(f"{url}:{operation}".encode()).hexdigest()
        
    def _get_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """Get result from security cache"""
        if key in self.security_cache:
            cache_entry = self.security_cache[key]
            if datetime.utcnow().timestamp() - cache_entry['timestamp'] < self.cache_ttl:
                return cache_entry['data']
            else:
                del self.security_cache[key]
        return None
        
    def _store_in_cache(self, key: str, data: Dict[str, Any]):
        """Store result in security cache"""
        self.security_cache[key] = {
            'data': data,
            'timestamp': datetime.utcnow().timestamp()
        }
        
    async def _validate_security_task(self, task: Dict[str, Any]) -> bool:
        """Validate security task format"""
        return (
            'type' in task and
            'data' in task and
            isinstance(task['data'], dict)
        )
