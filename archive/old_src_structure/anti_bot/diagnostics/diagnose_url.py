"""
URL Diagnostics - Comprehensive anti-bot detection and analysis tool.
Provides detailed analysis of websites' anti-bot measures, detection mechanisms,
and recommended strategies for ethical data extraction.
"""

import asyncio
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, urljoin

from utils.logger import get_logger
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


@dataclass
class BotDetectionSignal:
    """Individual bot detection signal found during analysis."""
    signal_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    evidence: str
    mitigation_hint: str
    confidence: float


@dataclass
class DiagnosticResult:
    """Complete diagnostic result for a URL."""
    url: str
    analyzed_at: datetime
    overall_risk_level: str
    bot_detection_signals: List[BotDetectionSignal]
    technical_analysis: Dict[str, Any]
    recommendations: List[str]
    success_probability: float
    estimated_complexity: str


class URLDiagnostic:
    """
    Advanced URL diagnostic system for anti-bot analysis.
    
    Features:
    - Comprehensive bot detection analysis
    - Technical capability assessment
    - Risk level evaluation
    - Mitigation strategy recommendations
    - Success probability estimation
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        
        # Detection patterns
        self.cloudflare_patterns = [
            r'cloudflare',
            r'cf-ray',
            r'__cfduid',
            r'_cfuvid',
            r'cf_clearance',
            r'checking your browser'
        ]
        
        self.captcha_patterns = [
            r'captcha',
            r'recaptcha',
            r'hcaptcha',
            r'prove you are human',
            r'verify you are human',
            r'robot check'
        ]
        
        self.js_challenge_patterns = [
            r'please enable javascript',
            r'javascript is required',
            r'js challenge',
            r'browser challenge',
            r'checking your browser'
        ]
        
        self.rate_limit_patterns = [
            r'rate limit',
            r'too many requests',
            r'429',
            r'slow down',
            r'request throttled'
        ]
        
        self.bot_detection_patterns = [
            r'bot detected',
            r'automated access',
            r'suspicious activity',
            r'access denied',
            r'blocked',
            r'forbidden'
        ]
        
    async def diagnose_url(
        self, 
        url: str, 
        user_agent: str = None,
        include_deep_analysis: bool = True
    ) -> DiagnosticResult:
        """
        Perform comprehensive diagnostic analysis of a URL.
        
        Args:
            url: Target URL to analyze
            user_agent: User agent to use for requests
            include_deep_analysis: Whether to perform deep technical analysis
            
        Returns:
            DiagnosticResult with complete analysis
        """
        logger.info(f"Starting diagnostic analysis for: {url}")
        start_time = time.time()
        
        try:
            # Initialize result
            signals = []
            technical_analysis = {}
            
            # Basic HTTP analysis
            http_signals, http_tech = await self._analyze_http_response(url, user_agent)
            signals.extend(http_signals)
            technical_analysis['http'] = http_tech
            
            # Headers analysis
            header_signals, header_tech = await self._analyze_response_headers(url, user_agent)
            signals.extend(header_signals)
            technical_analysis['headers'] = header_tech
            
            # Content analysis
            content_signals, content_tech = await self._analyze_page_content(url, user_agent)
            signals.extend(content_signals)
            technical_analysis['content'] = content_tech
            
            if include_deep_analysis:
                # JavaScript analysis
                js_signals, js_tech = await self._analyze_javascript_challenges(url)
                signals.extend(js_signals)
                technical_analysis['javascript'] = js_tech
                
                # Network behavior analysis
                network_signals, network_tech = await self._analyze_network_behavior(url)
                signals.extend(network_signals)
                technical_analysis['network'] = network_tech
                
            # Calculate overall risk and recommendations
            risk_level = self._calculate_risk_level(signals)
            recommendations = self._generate_recommendations(signals, technical_analysis)
            success_probability = self._estimate_success_probability(signals)
            complexity = self._estimate_complexity(signals, technical_analysis)
            
            result = DiagnosticResult(
                url=url,
                analyzed_at=datetime.now(),
                overall_risk_level=risk_level,
                bot_detection_signals=signals,
                technical_analysis=technical_analysis,
                recommendations=recommendations,
                success_probability=success_probability,
                estimated_complexity=complexity
            )
            
            # Update metrics
            analysis_time = time.time() - start_time
            self.metrics.timer("url_diagnostic_analysis_time", analysis_time)
            self.metrics.counter("url_diagnostic_completed", 1)
            self.metrics.counter(f"url_diagnostic_risk_{risk_level}", 1)
            
            logger.info(
                f"Diagnostic completed for {url}: "
                f"risk={risk_level}, signals={len(signals)}, "
                f"time={analysis_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error during diagnostic analysis of {url}: {e}")
            raise
            
    async def _analyze_http_response(
        self, 
        url: str, 
        user_agent: str = None
    ) -> Tuple[List[BotDetectionSignal], Dict[str, Any]]:
        """Analyze basic HTTP response characteristics."""
        signals = []
        tech_info = {}
        
        try:
            import httpx
            
            headers = {}
            if user_agent:
                headers['User-Agent'] = user_agent
            else:
                headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                tech_info = {
                    'status_code': response.status_code,
                    'final_url': str(response.url),
                    'redirects': len(response.history),
                    'response_time': response.elapsed.total_seconds(),
                    'content_length': len(response.content)
                }
                
                # Analyze status code
                if response.status_code == 403:
                    signals.append(BotDetectionSignal(
                        signal_type="http_status",
                        severity="high",
                        description="HTTP 403 Forbidden - Access denied",
                        evidence=f"Status code: {response.status_code}",
                        mitigation_hint="Try different user agent, headers, or proxy",
                        confidence=0.9
                    ))
                elif response.status_code == 429:
                    signals.append(BotDetectionSignal(
                        signal_type="rate_limit",
                        severity="medium",
                        description="HTTP 429 Too Many Requests - Rate limited",
                        evidence=f"Status code: {response.status_code}",
                        mitigation_hint="Implement request throttling and delays",
                        confidence=0.95
                    ))
                elif response.status_code == 503:
                    signals.append(BotDetectionSignal(
                        signal_type="service_unavailable",
                        severity="medium",
                        description="HTTP 503 Service Unavailable",
                        evidence=f"Status code: {response.status_code}",
                        mitigation_hint="May be temporary, try later or check for maintenance",
                        confidence=0.7
                    ))
                    
                # Analyze redirects
                if response.history:
                    redirect_chain = [str(r.url) for r in response.history]
                    tech_info['redirect_chain'] = redirect_chain
                    
                    # Check for suspicious redirects
                    if len(response.history) > 3:
                        signals.append(BotDetectionSignal(
                            signal_type="redirect_chain",
                            severity="low",
                            description="Multiple redirects detected",
                            evidence=f"Redirect chain: {' -> '.join(redirect_chain[:3])}...",
                            mitigation_hint="Monitor redirect behavior and ensure proper handling",
                            confidence=0.5
                        ))
                        
        except Exception as e:
            logger.error(f"Error analyzing HTTP response for {url}: {e}")
            signals.append(BotDetectionSignal(
                signal_type="connection_error",
                severity="high",
                description="Failed to establish HTTP connection",
                evidence=str(e),
                mitigation_hint="Check network connectivity and URL validity",
                confidence=0.8
            ))
            
        return signals, tech_info
        
    async def _analyze_response_headers(
        self, 
        url: str, 
        user_agent: str = None
    ) -> Tuple[List[BotDetectionSignal], Dict[str, Any]]:
        """Analyze HTTP response headers for bot detection signals."""
        signals = []
        tech_info = {}
        
        try:
            import httpx
            
            headers = {'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                
                response_headers = dict(response.headers)
                tech_info['headers'] = response_headers
                
                # Check for Cloudflare
                cf_headers = [
                    'cf-ray', 'cf-cache-status', 'cf-request-id', 
                    'server', 'cf-visitor', 'expect-ct'
                ]
                
                cf_detected = any(
                    header.lower() in [h.lower() for h in response_headers.keys()]
                    for header in cf_headers
                ) or any(
                    'cloudflare' in str(value).lower()
                    for value in response_headers.values()
                )
                
                if cf_detected:
                    signals.append(BotDetectionSignal(
                        signal_type="cloudflare",
                        severity="medium",
                        description="Cloudflare protection detected",
                        evidence="Cloudflare headers present",
                        mitigation_hint="Use stealth browser or specialized bypass techniques",
                        confidence=0.9
                    ))
                    
                # Check for rate limiting headers
                rate_limit_headers = [
                    'x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset',
                    'ratelimit-limit', 'ratelimit-remaining', 'retry-after'
                ]
                
                for header in rate_limit_headers:
                    if header.lower() in [h.lower() for h in response_headers.keys()]:
                        signals.append(BotDetectionSignal(
                            signal_type="rate_limit_header",
                            severity="low",
                            description="Rate limiting headers detected",
                            evidence=f"Header: {header}",
                            mitigation_hint="Respect rate limits and implement proper delays",
                            confidence=0.8
                        ))
                        break
                        
                # Check for security headers
                security_headers = [
                    'x-frame-options', 'x-content-type-options', 
                    'content-security-policy', 'strict-transport-security'
                ]
                
                security_count = sum(
                    1 for header in security_headers
                    if header.lower() in [h.lower() for h in response_headers.keys()]
                )
                
                tech_info['security_headers_count'] = security_count
                
                if security_count >= 3:
                    signals.append(BotDetectionSignal(
                        signal_type="security_headers",
                        severity="low",
                        description="Multiple security headers present",
                        evidence=f"{security_count} security headers detected",
                        mitigation_hint="Site has strong security posture, expect additional protections",
                        confidence=0.6
                    ))
                    
        except Exception as e:
            logger.error(f"Error analyzing headers for {url}: {e}")
            
        return signals, tech_info
        
    async def _analyze_page_content(
        self, 
        url: str, 
        user_agent: str = None
    ) -> Tuple[List[BotDetectionSignal], Dict[str, Any]]:
        """Analyze page content for bot detection patterns."""
        signals = []
        tech_info = {}
        
        try:
            import httpx
            
            headers = {'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url, headers=headers, follow_redirects=True)
                content = response.text.lower()
                
                tech_info = {
                    'content_length': len(content),
                    'has_javascript': '<script' in content,
                    'has_forms': '<form' in content,
                    'meta_tags_count': len(re.findall(r'<meta', content))
                }
                
                # Check for Cloudflare patterns
                cf_matches = []
                for pattern in self.cloudflare_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        cf_matches.append(pattern)
                        
                if cf_matches:
                    signals.append(BotDetectionSignal(
                        signal_type="cloudflare_content",
                        severity="high",
                        description="Cloudflare challenge page detected",
                        evidence=f"Patterns found: {', '.join(cf_matches)}",
                        mitigation_hint="Use browser automation with stealth capabilities",
                        confidence=0.95
                    ))
                    
                # Check for CAPTCHA
                captcha_matches = []
                for pattern in self.captcha_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        captcha_matches.append(pattern)
                        
                if captcha_matches:
                    signals.append(BotDetectionSignal(
                        signal_type="captcha",
                        severity="critical",
                        description="CAPTCHA challenge detected",
                        evidence=f"CAPTCHA patterns: {', '.join(captcha_matches)}",
                        mitigation_hint="Implement CAPTCHA solving or human verification workflow",
                        confidence=0.9
                    ))
                    
                # Check for JavaScript challenges
                js_matches = []
                for pattern in self.js_challenge_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        js_matches.append(pattern)
                        
                if js_matches:
                    signals.append(BotDetectionSignal(
                        signal_type="javascript_challenge",
                        severity="medium",
                        description="JavaScript challenge/requirement detected",
                        evidence=f"JS patterns: {', '.join(js_matches)}",
                        mitigation_hint="Use browser automation instead of HTTP requests",
                        confidence=0.8
                    ))
                    
                # Check for bot detection messages
                bot_matches = []
                for pattern in self.bot_detection_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        bot_matches.append(pattern)
                        
                if bot_matches:
                    signals.append(BotDetectionSignal(
                        signal_type="bot_detection_message",
                        severity="high",
                        description="Bot detection message found",
                        evidence=f"Detection patterns: {', '.join(bot_matches)}",
                        mitigation_hint="Improve stealth techniques and request patterns",
                        confidence=0.85
                    ))
                    
                # Analyze content complexity
                script_tags = len(re.findall(r'<script', content))
                if script_tags > 10:
                    tech_info['heavy_javascript'] = True
                    signals.append(BotDetectionSignal(
                        signal_type="heavy_javascript",
                        severity="low",
                        description="Heavy JavaScript usage detected",
                        evidence=f"{script_tags} script tags found",
                        mitigation_hint="Consider browser automation for dynamic content",
                        confidence=0.6
                    ))
                    
        except Exception as e:
            logger.error(f"Error analyzing content for {url}: {e}")
            
        return signals, tech_info
        
    async def _analyze_javascript_challenges(self, url: str) -> Tuple[List[BotDetectionSignal], Dict[str, Any]]:
        """Analyze JavaScript-based challenges and protections."""
        signals = []
        tech_info = {'js_analysis_attempted': True}
        
        # This would require browser automation to fully analyze
        # For now, we'll do basic pattern detection
        
        try:
            import httpx
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                content = response.text
                
                # Look for common JS protection patterns
                js_protection_patterns = [
                    r'setInterval\s*\(',
                    r'setTimeout\s*\(',
                    r'eval\s*\(',
                    r'document\.write',
                    r'window\.location',
                    r'navigator\.',
                    r'screen\.',
                    r'window\.innerWidth',
                    r'canvas\.getContext',
                    r'webgl'
                ]
                
                protection_count = 0
                found_patterns = []
                
                for pattern in js_protection_patterns:
                    matches = len(re.findall(pattern, content, re.IGNORECASE))
                    if matches > 0:
                        protection_count += matches
                        found_patterns.append(pattern)
                        
                tech_info['js_protection_patterns'] = found_patterns
                tech_info['js_protection_count'] = protection_count
                
                if protection_count > 5:
                    signals.append(BotDetectionSignal(
                        signal_type="js_fingerprinting",
                        severity="medium",
                        description="JavaScript fingerprinting detected",
                        evidence=f"{protection_count} JS protection patterns found",
                        mitigation_hint="Use stealth browser with fingerprint protection",
                        confidence=0.7
                    ))
                    
        except Exception as e:
            logger.error(f"Error analyzing JavaScript for {url}: {e}")
            tech_info['js_analysis_error'] = str(e)
            
        return signals, tech_info
        
    async def _analyze_network_behavior(self, url: str) -> Tuple[List[BotDetectionSignal], Dict[str, Any]]:
        """Analyze network behavior and timing patterns."""
        signals = []
        tech_info = {}
        
        try:
            import httpx
            
            # Perform multiple requests to analyze behavior
            request_times = []
            status_codes = []
            
            async with httpx.AsyncClient(timeout=30) as client:
                for i in range(3):
                    start_time = time.time()
                    try:
                        response = await client.get(url)
                        request_time = time.time() - start_time
                        request_times.append(request_time)
                        status_codes.append(response.status_code)
                        
                        # Small delay between requests
                        await asyncio.sleep(1)
                        
                    except Exception as e:
                        logger.debug(f"Request {i+1} failed: {e}")
                        
            tech_info = {
                'request_times': request_times,
                'status_codes': status_codes,
                'avg_response_time': sum(request_times) / len(request_times) if request_times else 0,
                'status_consistency': len(set(status_codes)) == 1 if status_codes else False
            }
            
            # Analyze response time patterns
            if request_times and max(request_times) - min(request_times) > 2.0:
                signals.append(BotDetectionSignal(
                    signal_type="variable_response_times",
                    severity="low",
                    description="Highly variable response times detected",
                    evidence=f"Response time range: {min(request_times):.2f}s - {max(request_times):.2f}s",
                    mitigation_hint="May indicate load balancing or dynamic processing",
                    confidence=0.5
                ))
                
            # Analyze status code consistency
            if len(set(status_codes)) > 1:
                signals.append(BotDetectionSignal(
                    signal_type="inconsistent_responses",
                    severity="medium",
                    description="Inconsistent HTTP status codes",
                    evidence=f"Status codes: {status_codes}",
                    mitigation_hint="May indicate request-based filtering or rate limiting",
                    confidence=0.6
                ))
                
        except Exception as e:
            logger.error(f"Error analyzing network behavior for {url}: {e}")
            tech_info['network_analysis_error'] = str(e)
            
        return signals, tech_info
        
    def _calculate_risk_level(self, signals: List[BotDetectionSignal]) -> str:
        """Calculate overall risk level based on detected signals."""
        if not signals:
            return "low"
            
        # Weight signals by severity
        severity_weights = {
            'low': 1,
            'medium': 3,
            'high': 6,
            'critical': 10
        }
        
        total_score = sum(
            severity_weights.get(signal.severity, 1) * signal.confidence
            for signal in signals
        )
        
        # Determine risk level based on score
        if total_score >= 15:
            return "critical"
        elif total_score >= 8:
            return "high"
        elif total_score >= 3:
            return "medium"
        else:
            return "low"
            
    def _generate_recommendations(
        self, 
        signals: List[BotDetectionSignal], 
        technical_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate specific recommendations based on analysis."""
        recommendations = []
        
        # General recommendations based on signals
        signal_types = {signal.signal_type for signal in signals}
        
        if 'cloudflare' in signal_types or 'cloudflare_content' in signal_types:
            recommendations.append("Use browser automation with Cloudflare bypass capabilities")
            recommendations.append("Implement stealth techniques to avoid detection")
            
        if 'captcha' in signal_types:
            recommendations.append("Implement CAPTCHA solving workflow")
            recommendations.append("Consider manual intervention for CAPTCHA challenges")
            
        if 'javascript_challenge' in signal_types or 'heavy_javascript' in signal_types:
            recommendations.append("Use headless browser instead of HTTP requests")
            recommendations.append("Ensure JavaScript execution capabilities")
            
        if 'rate_limit' in signal_types or 'rate_limit_header' in signal_types:
            recommendations.append("Implement request throttling and delays")
            recommendations.append("Use proxy rotation to distribute requests")
            
        if 'bot_detection_message' in signal_types:
            recommendations.append("Improve user agent and header randomization")
            recommendations.append("Implement more sophisticated stealth techniques")
            
        # Technical recommendations
        http_info = technical_analysis.get('http', {})
        if http_info.get('redirects', 0) > 2:
            recommendations.append("Monitor and handle redirect chains properly")
            
        content_info = technical_analysis.get('content', {})
        if content_info.get('heavy_javascript'):
            recommendations.append("Allow sufficient time for JavaScript execution")
            
        # Default recommendations if no specific issues found
        if not recommendations:
            recommendations.extend([
                "Use realistic request patterns and delays",
                "Implement proper error handling and retry logic",
                "Monitor for changes in website behavior"
            ])
            
        return recommendations
        
    def _estimate_success_probability(self, signals: List[BotDetectionSignal]) -> float:
        """Estimate probability of successful data extraction."""
        if not signals:
            return 0.9  # High probability if no issues detected
            
        # Start with base probability
        base_probability = 0.8
        
        # Reduce probability based on signals
        for signal in signals:
            severity_impact = {
                'low': 0.05,
                'medium': 0.15,
                'high': 0.25,
                'critical': 0.4
            }
            
            impact = severity_impact.get(signal.severity, 0.1)
            reduction = impact * signal.confidence
            base_probability -= reduction
            
        return max(0.0, min(1.0, base_probability))
        
    def _estimate_complexity(
        self, 
        signals: List[BotDetectionSignal], 
        technical_analysis: Dict[str, Any]
    ) -> str:
        """Estimate implementation complexity required."""
        if not signals:
            return "simple"
            
        complexity_factors = 0
        
        # Count critical factors
        critical_signals = [s for s in signals if s.severity == 'critical']
        high_signals = [s for s in signals if s.severity == 'high']
        
        complexity_factors += len(critical_signals) * 3
        complexity_factors += len(high_signals) * 2
        complexity_factors += len([s for s in signals if s.severity == 'medium'])
        
        # Technical complexity factors
        js_info = technical_analysis.get('javascript', {})
        if js_info.get('js_protection_count', 0) > 5:
            complexity_factors += 2
            
        content_info = technical_analysis.get('content', {})
        if content_info.get('heavy_javascript'):
            complexity_factors += 1
            
        # Determine complexity level
        if complexity_factors >= 8:
            return "expert"
        elif complexity_factors >= 5:
            return "advanced"
        elif complexity_factors >= 2:
            return "intermediate"
        else:
            return "simple"
            
    def export_report(self, result: DiagnosticResult, format: str = "json") -> str:
        """Export diagnostic report in specified format."""
        if format.lower() == "json":
            return json.dumps(asdict(result), indent=2, default=str)
        elif format.lower() == "text":
            return self._format_text_report(result)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    def _format_text_report(self, result: DiagnosticResult) -> str:
        """Format diagnostic result as human-readable text report."""
        report = []
        report.append(f"URL Diagnostic Report for: {result.url}")
        report.append(f"Analysis Date: {result.analyzed_at}")
        report.append(f"Overall Risk Level: {result.overall_risk_level.upper()}")
        report.append(f"Success Probability: {result.success_probability:.1%}")
        report.append(f"Estimated Complexity: {result.estimated_complexity}")
        report.append("")
        
        if result.bot_detection_signals:
            report.append("DETECTED SIGNALS:")
            for signal in result.bot_detection_signals:
                report.append(f"  • {signal.description} [{signal.severity.upper()}]")
                report.append(f"    Evidence: {signal.evidence}")
                report.append(f"    Mitigation: {signal.mitigation_hint}")
                report.append("")
                
        if result.recommendations:
            report.append("RECOMMENDATIONS:")
            for i, rec in enumerate(result.recommendations, 1):
                report.append(f"  {i}. {rec}")
            report.append("")
            
        return "\n".join(report)