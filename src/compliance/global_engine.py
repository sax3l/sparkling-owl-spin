"""
Global Compliance Engine

Världens mest avancerade compliance-system för etisk webscraping som automatiskt
hanterar juridisk efterlevnad, robots.txt, GDPR/CCPA, och regionala regler.
"""

import asyncio
import json
import logging
import re
import time
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from urllib.parse import urlparse, urljoin, robotparser
from urllib.robotparser import RobotFileParser
import requests
import aiohttp
from datetime import datetime, timedelta

# Internal imports
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ComplianceLevel(Enum):
    """Levels of compliance enforcement"""
    PERMISSIVE = "permissive"        # Minimal compliance
    STANDARD = "standard"            # Standard web ethics
    STRICT = "strict"                # Strict legal compliance
    ULTRA_STRICT = "ultra_strict"    # Maximum legal safety


class LegalJurisdiction(Enum):
    """Legal jurisdictions with specific requirements"""
    GDPR_EU = "gdpr_eu"              # European Union
    CCPA_CALIFORNIA = "ccpa_ca"      # California, USA
    PIPEDA_CANADA = "pipeda_ca"      # Canada
    DPA_UK = "dpa_uk"                # United Kingdom
    LGPD_BRAZIL = "lgpd_br"          # Brazil
    PDPA_SINGAPORE = "pdpa_sg"       # Singapore
    GLOBAL = "global"                # Global best practices


class DataCategory(Enum):
    """Categories of data for compliance"""
    PUBLIC = "public"                # Publicly available data
    PERSONAL = "personal"            # Personal identifiable information
    SENSITIVE = "sensitive"          # Sensitive personal data
    FINANCIAL = "financial"          # Financial information
    HEALTH = "health"                # Health information
    BIOMETRIC = "biometric"          # Biometric data
    LOCATION = "location"            # Location data
    BEHAVIORAL = "behavioral"        # Behavioral data


class ComplianceAction(Enum):
    """Actions to take for compliance"""
    ALLOW = "allow"
    BLOCK = "block"
    WARN = "warn" 
    DELAY = "delay"
    ANONYMIZE = "anonymize"
    ENCRYPT = "encrypt"
    DELETE = "delete"


@dataclass
class RobotsRule:
    """Robots.txt rule"""
    user_agent: str
    allow: List[str]
    disallow: List[str]
    crawl_delay: Optional[float]
    request_rate: Optional[Tuple[int, int]]  # (requests, seconds)


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    rule_id: str
    name: str
    description: str
    jurisdiction: LegalJurisdiction
    data_categories: List[DataCategory]
    url_patterns: List[str]
    action: ComplianceAction
    parameters: Dict[str, Any] = None
    priority: int = 100
    active: bool = True


@dataclass
class SiteCompliance:
    """Compliance status for a specific site"""
    domain: str
    robots_allowed: bool
    robots_crawl_delay: Optional[float]
    robots_request_rate: Optional[Tuple[int, int]]
    privacy_policy_url: Optional[str]
    terms_of_service_url: Optional[str]
    gdpr_compliant: bool
    ccpa_compliant: bool
    data_categories_allowed: Set[DataCategory]
    compliance_rules: List[ComplianceRule]
    last_checked: datetime
    compliance_score: float


@dataclass
class ComplianceViolation:
    """Compliance violation record"""
    violation_id: str
    timestamp: datetime
    url: str
    rule_violated: ComplianceRule
    severity: str  # "low", "medium", "high", "critical"
    description: str
    recommended_action: str
    data_affected: Dict[str, Any] = None


class RobotsParser:
    """Advanced robots.txt parser with caching"""
    
    def __init__(self):
        self.robots_cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def can_fetch(self, url: str, user_agent: str = "*") -> Tuple[bool, Optional[float], Optional[Tuple[int, int]]]:
        """Check if URL can be fetched according to robots.txt"""
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_url = urljoin(base_url, '/robots.txt')
            
            # Check cache
            if robots_url in self.robots_cache:
                cached_data = self.robots_cache[robots_url]
                if time.time() - cached_data['timestamp'] < self.cache_ttl:
                    rules = cached_data['rules']
                    return self._check_rules(url, rules, user_agent)
            
            # Fetch robots.txt
            rules = await self._fetch_robots(robots_url)
            
            # Cache results
            self.robots_cache[robots_url] = {
                'rules': rules,
                'timestamp': time.time()
            }
            
            return self._check_rules(url, rules, user_agent)
            
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True, None, None  # Allow by default if robots.txt unavailable
    
    async def _fetch_robots(self, robots_url: str) -> RobotsRule:
        """Fetch and parse robots.txt"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=10) as response:
                    if response.status != 200:
                        return RobotsRule("*", [], [], None, None)  # Empty rules
                    
                    content = await response.text()
                    return self._parse_robots_content(content)
                    
        except Exception as e:
            logger.warning(f"Failed to fetch robots.txt from {robots_url}: {e}")
            return RobotsRule("*", [], [], None, None)
    
    def _parse_robots_content(self, content: str) -> RobotsRule:
        """Parse robots.txt content"""
        lines = content.strip().split('\n')
        
        current_user_agent = "*"
        allow_rules = []
        disallow_rules = []
        crawl_delay = None
        request_rate = None
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == 'user-agent':
                    current_user_agent = value
                elif key == 'allow':
                    allow_rules.append(value)
                elif key == 'disallow':
                    disallow_rules.append(value)
                elif key == 'crawl-delay':
                    try:
                        crawl_delay = float(value)
                    except ValueError:
                        pass
                elif key == 'request-rate':
                    try:
                        # Format: "1/5s" means 1 request per 5 seconds
                        match = re.match(r'(\d+)/(\d+)s?', value)
                        if match:
                            requests_count = int(match.group(1))
                            seconds = int(match.group(2))
                            request_rate = (requests_count, seconds)
                    except:
                        pass
        
        return RobotsRule(
            user_agent=current_user_agent,
            allow=allow_rules,
            disallow=disallow_rules,
            crawl_delay=crawl_delay,
            request_rate=request_rate
        )
    
    def _check_rules(self, 
                    url: str, 
                    rules: RobotsRule, 
                    user_agent: str) -> Tuple[bool, Optional[float], Optional[Tuple[int, int]]]:
        """Check if URL is allowed according to robots rules"""
        parsed_url = urlparse(url)
        path = parsed_url.path or '/'
        
        # Check if user agent matches
        if rules.user_agent != "*" and user_agent not in rules.user_agent:
            return True, None, None  # Rules don't apply to this user agent
        
        # Check disallow rules first (more restrictive)
        for disallow_pattern in rules.disallow:
            if self._pattern_matches(path, disallow_pattern):
                # Check if there's a more specific allow rule
                for allow_pattern in rules.allow:
                    if self._pattern_matches(path, allow_pattern):
                        return True, rules.crawl_delay, rules.request_rate
                return False, rules.crawl_delay, rules.request_rate
        
        # Check allow rules
        for allow_pattern in rules.allow:
            if self._pattern_matches(path, allow_pattern):
                return True, rules.crawl_delay, rules.request_rate
        
        # Default behavior: if no specific rules, allow
        return True, rules.crawl_delay, rules.request_rate
    
    def _pattern_matches(self, path: str, pattern: str) -> bool:
        """Check if path matches robots.txt pattern"""
        if not pattern:
            return False
            
        # Convert robots.txt pattern to regex
        # * matches zero or more characters
        # $ at end matches end of path
        regex_pattern = pattern.replace('*', '.*')
        if pattern.endswith('$'):
            regex_pattern = regex_pattern[:-1] + '$'
        else:
            regex_pattern = '^' + regex_pattern
        
        try:
            return bool(re.match(regex_pattern, path))
        except:
            return False


class PrivacyPolicyAnalyzer:
    """Analyze privacy policies for compliance indicators"""
    
    def __init__(self):
        self.gdpr_indicators = [
            "gdpr", "general data protection regulation", "data protection",
            "right to erasure", "data portability", "consent", "lawful basis",
            "data controller", "data processor", "privacy by design"
        ]
        
        self.ccpa_indicators = [
            "ccpa", "california consumer privacy act", "do not sell",
            "personal information", "consumer rights", "opt-out",
            "california residents", "privacy rights"
        ]
        
        self.data_collection_indicators = [
            "collect", "gather", "obtain", "receive", "acquire",
            "personal data", "personal information", "pii",
            "cookies", "tracking", "analytics", "behavioral"
        ]
    
    async def analyze_privacy_policy(self, url: str) -> Dict[str, Any]:
        """Analyze privacy policy at URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as response:
                    if response.status != 200:
                        return {"error": "Privacy policy not accessible"}
                    
                    content = await response.text()
                    return self._analyze_content(content)
                    
        except Exception as e:
            logger.warning(f"Failed to analyze privacy policy {url}: {e}")
            return {"error": str(e)}
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze privacy policy content"""
        content_lower = content.lower()
        
        # Check for GDPR compliance indicators
        gdpr_score = sum(1 for indicator in self.gdpr_indicators 
                        if indicator in content_lower)
        gdpr_compliant = gdpr_score >= 3
        
        # Check for CCPA compliance indicators  
        ccpa_score = sum(1 for indicator in self.ccpa_indicators
                        if indicator in content_lower)
        ccpa_compliant = ccpa_score >= 2
        
        # Check data collection practices
        data_collection_score = sum(1 for indicator in self.data_collection_indicators
                                  if indicator in content_lower)
        
        # Detect data categories mentioned
        data_categories = set()
        if any(term in content_lower for term in ["email", "address", "phone", "name"]):
            data_categories.add(DataCategory.PERSONAL)
        if any(term in content_lower for term in ["health", "medical", "disease"]):
            data_categories.add(DataCategory.HEALTH)
        if any(term in content_lower for term in ["financial", "credit card", "payment"]):
            data_categories.add(DataCategory.FINANCIAL)
        if any(term in content_lower for term in ["location", "gps", "geolocation"]):
            data_categories.add(DataCategory.LOCATION)
        if any(term in content_lower for term in ["behavior", "tracking", "analytics"]):
            data_categories.add(DataCategory.BEHAVIORAL)
        
        return {
            "gdpr_compliant": gdpr_compliant,
            "gdpr_score": gdpr_score,
            "ccpa_compliant": ccpa_compliant,
            "ccpa_score": ccpa_score,
            "data_collection_score": data_collection_score,
            "data_categories": list(data_categories),
            "content_length": len(content)
        }


class ComplianceRuleEngine:
    """Engine for managing and enforcing compliance rules"""
    
    def __init__(self):
        self.rules = {}
        self.violations = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default compliance rules"""
        
        # GDPR Rules
        gdpr_rules = [
            ComplianceRule(
                rule_id="gdpr_personal_data",
                name="GDPR Personal Data Protection",
                description="Block collection of personal data without explicit consent in EU",
                jurisdiction=LegalJurisdiction.GDPR_EU,
                data_categories=[DataCategory.PERSONAL, DataCategory.SENSITIVE],
                url_patterns=["*"],
                action=ComplianceAction.WARN,
                parameters={"consent_required": True},
                priority=90
            ),
            ComplianceRule(
                rule_id="gdpr_sensitive_data",
                name="GDPR Sensitive Data Ban",
                description="Block collection of sensitive personal data",
                jurisdiction=LegalJurisdiction.GDPR_EU,
                data_categories=[DataCategory.HEALTH, DataCategory.BIOMETRIC],
                url_patterns=["*"],
                action=ComplianceAction.BLOCK,
                priority=95
            )
        ]
        
        # CCPA Rules
        ccpa_rules = [
            ComplianceRule(
                rule_id="ccpa_opt_out",
                name="CCPA Opt-out Requirement",
                description="Respect Do Not Sell preferences for California residents",
                jurisdiction=LegalJurisdiction.CCPA_CALIFORNIA,
                data_categories=[DataCategory.PERSONAL, DataCategory.BEHAVIORAL],
                url_patterns=["*"],
                action=ComplianceAction.WARN,
                parameters={"opt_out_required": True},
                priority=85
            )
        ]
        
        # General ethical rules
        general_rules = [
            ComplianceRule(
                rule_id="rate_limit_respect",
                name="Respect Rate Limits",
                description="Honor crawl delays and rate limits specified in robots.txt",
                jurisdiction=LegalJurisdiction.GLOBAL,
                data_categories=[],
                url_patterns=["*"],
                action=ComplianceAction.DELAY,
                parameters={"respect_robots": True},
                priority=70
            ),
            ComplianceRule(
                rule_id="no_disruption",
                name="No Service Disruption",
                description="Avoid overwhelming servers with requests",
                jurisdiction=LegalJurisdiction.GLOBAL,
                data_categories=[],
                url_patterns=["*"],
                action=ComplianceAction.DELAY,
                parameters={"max_requests_per_second": 2},
                priority=60
            )
        ]
        
        # Add all rules
        all_rules = gdpr_rules + ccpa_rules + general_rules
        for rule in all_rules:
            self.rules[rule.rule_id] = rule
    
    def add_custom_rule(self, rule: ComplianceRule):
        """Add a custom compliance rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added compliance rule: {rule.name}")
    
    def evaluate_compliance(self, 
                          url: str,
                          data_categories: List[DataCategory],
                          jurisdiction: LegalJurisdiction = LegalJurisdiction.GLOBAL,
                          site_compliance: SiteCompliance = None) -> List[Tuple[ComplianceRule, ComplianceAction]]:
        """Evaluate compliance for a URL and data collection"""
        
        applicable_rules = []
        
        for rule in self.rules.values():
            if not rule.active:
                continue
                
            # Check jurisdiction
            if rule.jurisdiction != LegalJurisdiction.GLOBAL and rule.jurisdiction != jurisdiction:
                continue
            
            # Check data categories
            if rule.data_categories and not any(cat in data_categories for cat in rule.data_categories):
                continue
            
            # Check URL patterns
            if not self._url_matches_patterns(url, rule.url_patterns):
                continue
            
            applicable_rules.append((rule, rule.action))
        
        # Sort by priority (higher = more important)
        applicable_rules.sort(key=lambda x: x[0].priority, reverse=True)
        
        return applicable_rules
    
    def _url_matches_patterns(self, url: str, patterns: List[str]) -> bool:
        """Check if URL matches any of the patterns"""
        for pattern in patterns:
            if pattern == "*":
                return True
            
            # Convert glob pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("?", ".")
            if re.search(regex_pattern, url, re.IGNORECASE):
                return True
        
        return False
    
    def record_violation(self, 
                        url: str,
                        rule: ComplianceRule,
                        severity: str,
                        description: str,
                        data_affected: Dict[str, Any] = None):
        """Record a compliance violation"""
        violation = ComplianceViolation(
            violation_id=str(time.time()),
            timestamp=datetime.now(),
            url=url,
            rule_violated=rule,
            severity=severity,
            description=description,
            recommended_action=f"Apply {rule.action.value} action",
            data_affected=data_affected
        )
        
        self.violations.append(violation)
        logger.warning(f"Compliance violation recorded: {description}")
    
    def get_violations(self, 
                      hours: int = 24,
                      severity: str = None) -> List[ComplianceViolation]:
        """Get compliance violations within time window"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_violations = [
            v for v in self.violations 
            if v.timestamp >= cutoff_time
        ]
        
        if severity:
            filtered_violations = [
                v for v in filtered_violations
                if v.severity == severity
            ]
        
        return filtered_violations


class GlobalComplianceEngine:
    """
    Main compliance engine that coordinates all compliance checking
    """
    
    def __init__(self, compliance_level: ComplianceLevel = ComplianceLevel.STANDARD):
        self.compliance_level = compliance_level
        self.robots_parser = RobotsParser()
        self.privacy_analyzer = PrivacyPolicyAnalyzer()
        self.rule_engine = ComplianceRuleEngine()
        
        # Site compliance cache
        self.site_compliance_cache = {}
        self.cache_ttl = 3600 * 24  # 24 hours
        
        logger.info(f"Global Compliance Engine initialized: {compliance_level.value}")
    
    async def check_url_compliance(self,
                                 url: str,
                                 data_categories: List[DataCategory] = None,
                                 jurisdiction: LegalJurisdiction = LegalJurisdiction.GLOBAL,
                                 user_agent: str = "WebScraper-Bot/1.0") -> Dict[str, Any]:
        """
        Comprehensive compliance check for a URL
        """
        if data_categories is None:
            data_categories = [DataCategory.PUBLIC]
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # Get or create site compliance
            site_compliance = await self.get_site_compliance(domain)
            
            # Check robots.txt
            robots_allowed, crawl_delay, request_rate = await self.robots_parser.can_fetch(url, user_agent)
            
            # Evaluate compliance rules
            rule_evaluations = self.rule_engine.evaluate_compliance(
                url, data_categories, jurisdiction, site_compliance
            )
            
            # Determine final action
            final_action, blocking_rules = self._determine_final_action(rule_evaluations)
            
            # Calculate compliance score
            compliance_score = self._calculate_compliance_score(
                robots_allowed, site_compliance, rule_evaluations
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                site_compliance, rule_evaluations, robots_allowed
            )
            
            return {
                "url": url,
                "domain": domain,
                "compliance_allowed": final_action != ComplianceAction.BLOCK,
                "final_action": final_action.value,
                "robots_allowed": robots_allowed,
                "crawl_delay": crawl_delay,
                "request_rate": request_rate,
                "compliance_score": compliance_score,
                "applicable_rules": [rule.name for rule, action in rule_evaluations],
                "blocking_rules": [rule.name for rule in blocking_rules],
                "site_compliance": asdict(site_compliance),
                "recommendations": recommendations,
                "jurisdiction": jurisdiction.value,
                "data_categories": [cat.value for cat in data_categories]
            }
            
        except Exception as e:
            logger.error(f"Compliance check failed for {url}: {e}")
            return {
                "url": url,
                "compliance_allowed": False,
                "final_action": ComplianceAction.BLOCK.value,
                "error": str(e)
            }
    
    async def get_site_compliance(self, domain: str) -> SiteCompliance:
        """Get comprehensive compliance status for a site"""
        
        # Check cache
        if domain in self.site_compliance_cache:
            cached_data = self.site_compliance_cache[domain]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['compliance']
        
        # Analyze site compliance
        site_compliance = await self._analyze_site_compliance(domain)
        
        # Cache result
        self.site_compliance_cache[domain] = {
            'compliance': site_compliance,
            'timestamp': time.time()
        }
        
        return site_compliance
    
    async def _analyze_site_compliance(self, domain: str) -> SiteCompliance:
        """Analyze compliance status for a domain"""
        base_url = f"https://{domain}"
        
        # Check robots.txt
        robots_allowed, crawl_delay, request_rate = await self.robots_parser.can_fetch(base_url)
        
        # Look for common policy URLs
        privacy_policy_url = await self._find_privacy_policy(domain)
        terms_url = await self._find_terms_of_service(domain)
        
        # Analyze privacy policy if found
        gdpr_compliant = False
        ccpa_compliant = False
        data_categories_allowed = {DataCategory.PUBLIC}
        
        if privacy_policy_url:
            policy_analysis = await self.privacy_analyzer.analyze_privacy_policy(privacy_policy_url)
            if "error" not in policy_analysis:
                gdpr_compliant = policy_analysis.get("gdpr_compliant", False)
                ccpa_compliant = policy_analysis.get("ccpa_compliant", False)
                
                # Add allowed data categories based on policy
                for cat_name in policy_analysis.get("data_categories", []):
                    try:
                        data_categories_allowed.add(DataCategory(cat_name))
                    except ValueError:
                        pass
        
        # Get applicable compliance rules
        applicable_rules = [
            rule for rule in self.rule_engine.rules.values()
            if rule.active and (not rule.url_patterns or "*" in rule.url_patterns)
        ]
        
        # Calculate compliance score
        compliance_score = self._calculate_site_compliance_score(
            robots_allowed, gdpr_compliant, ccpa_compliant, 
            len(applicable_rules), privacy_policy_url is not None
        )
        
        return SiteCompliance(
            domain=domain,
            robots_allowed=robots_allowed,
            robots_crawl_delay=crawl_delay,
            robots_request_rate=request_rate,
            privacy_policy_url=privacy_policy_url,
            terms_of_service_url=terms_url,
            gdpr_compliant=gdpr_compliant,
            ccpa_compliant=ccpa_compliant,
            data_categories_allowed=data_categories_allowed,
            compliance_rules=applicable_rules,
            last_checked=datetime.now(),
            compliance_score=compliance_score
        )
    
    async def _find_privacy_policy(self, domain: str) -> Optional[str]:
        """Try to find privacy policy URL"""
        base_url = f"https://{domain}"
        
        common_paths = [
            "/privacy",
            "/privacy-policy", 
            "/privacy_policy",
            "/legal/privacy",
            "/terms/privacy",
            "/policy/privacy"
        ]
        
        async with aiohttp.ClientSession() as session:
            for path in common_paths:
                try:
                    url = base_url + path
                    async with session.head(url, timeout=5) as response:
                        if response.status == 200:
                            return url
                except:
                    continue
        
        return None
    
    async def _find_terms_of_service(self, domain: str) -> Optional[str]:
        """Try to find terms of service URL"""
        base_url = f"https://{domain}"
        
        common_paths = [
            "/terms",
            "/terms-of-service",
            "/terms_of_service", 
            "/legal/terms",
            "/tos",
            "/legal"
        ]
        
        async with aiohttp.ClientSession() as session:
            for path in common_paths:
                try:
                    url = base_url + path
                    async with session.head(url, timeout=5) as response:
                        if response.status == 200:
                            return url
                except:
                    continue
        
        return None
    
    def _determine_final_action(self, 
                              rule_evaluations: List[Tuple[ComplianceRule, ComplianceAction]]) -> Tuple[ComplianceAction, List[ComplianceRule]]:
        """Determine the final compliance action"""
        if not rule_evaluations:
            return ComplianceAction.ALLOW, []
        
        # Find the most restrictive action
        blocking_rules = []
        highest_priority_action = ComplianceAction.ALLOW
        
        for rule, action in rule_evaluations:
            if action == ComplianceAction.BLOCK:
                blocking_rules.append(rule)
                highest_priority_action = ComplianceAction.BLOCK
            elif action == ComplianceAction.WARN and highest_priority_action != ComplianceAction.BLOCK:
                highest_priority_action = ComplianceAction.WARN
            elif action == ComplianceAction.DELAY and highest_priority_action == ComplianceAction.ALLOW:
                highest_priority_action = ComplianceAction.DELAY
        
        return highest_priority_action, blocking_rules
    
    def _calculate_compliance_score(self,
                                  robots_allowed: bool,
                                  site_compliance: SiteCompliance,
                                  rule_evaluations: List[Tuple[ComplianceRule, ComplianceAction]]) -> float:
        """Calculate overall compliance score (0-100)"""
        score = 100.0
        
        # Robots.txt compliance
        if not robots_allowed:
            score -= 30
        
        # Site compliance factors
        if site_compliance.gdpr_compliant:
            score += 10
        else:
            score -= 10
        
        if site_compliance.ccpa_compliant:
            score += 5
        
        if site_compliance.privacy_policy_url:
            score += 10
        else:
            score -= 10
        
        # Rule violations
        for rule, action in rule_evaluations:
            if action == ComplianceAction.BLOCK:
                score -= 20
            elif action == ComplianceAction.WARN:
                score -= 10
        
        return max(0.0, min(100.0, score))
    
    def _calculate_site_compliance_score(self,
                                       robots_allowed: bool,
                                       gdpr_compliant: bool,
                                       ccpa_compliant: bool,
                                       num_rules: int,
                                       has_privacy_policy: bool) -> float:
        """Calculate site-specific compliance score"""
        score = 50.0  # Base score
        
        if robots_allowed:
            score += 20
        
        if gdpr_compliant:
            score += 15
        
        if ccpa_compliant:
            score += 10
        
        if has_privacy_policy:
            score += 10
        
        # Penalty for many applicable rules (suggests complex compliance requirements)
        score -= min(10, num_rules)
        
        return max(0.0, min(100.0, score))
    
    def _generate_recommendations(self,
                                site_compliance: SiteCompliance,
                                rule_evaluations: List[Tuple[ComplianceRule, ComplianceAction]],
                                robots_allowed: bool) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if not robots_allowed:
            recommendations.append("URL is blocked by robots.txt - consider respecting this restriction")
        
        if site_compliance.robots_crawl_delay:
            recommendations.append(f"Respect crawl delay of {site_compliance.robots_crawl_delay} seconds")
        
        if site_compliance.robots_request_rate:
            recommendations.append(f"Limit requests to {site_compliance.robots_request_rate[0]} per {site_compliance.robots_request_rate[1]} seconds")
        
        if not site_compliance.gdpr_compliant:
            recommendations.append("Site may not be GDPR compliant - exercise caution with personal data")
        
        if not site_compliance.privacy_policy_url:
            recommendations.append("No privacy policy found - avoid collecting personal data")
        
        # Rule-specific recommendations
        for rule, action in rule_evaluations:
            if action == ComplianceAction.BLOCK:
                recommendations.append(f"BLOCKED: {rule.description}")
            elif action == ComplianceAction.WARN:
                recommendations.append(f"WARNING: {rule.description}")
        
        return recommendations
    
    async def close(self):
        """Close the compliance engine"""
        logger.info("Global Compliance Engine closed")


# Factory function
def create_global_compliance_engine(
    compliance_level: ComplianceLevel = ComplianceLevel.STANDARD
) -> GlobalComplianceEngine:
    """Factory function to create Global Compliance Engine"""
    return GlobalComplianceEngine(compliance_level)


# Example usage
async def example_compliance_checking():
    """Example of compliance checking"""
    
    # Create compliance engine
    engine = create_global_compliance_engine(ComplianceLevel.STRICT)
    
    # Test URLs
    test_urls = [
        "https://example.com/page1",
        "https://facebook.com/public-page",
        "https://healthcare-site.com/patient-data"
    ]
    
    # Check compliance for each URL
    for url in test_urls:
        print(f"\n🔍 Checking compliance for: {url}")
        
        # Check with different data categories
        data_categories = [DataCategory.PUBLIC, DataCategory.PERSONAL]
        jurisdiction = LegalJurisdiction.GDPR_EU
        
        result = await engine.check_url_compliance(
            url, 
            data_categories=data_categories,
            jurisdiction=jurisdiction
        )
        
        print(f"✅ Allowed: {result['compliance_allowed']}")
        print(f"📊 Score: {result['compliance_score']:.1f}/100")
        print(f"🤖 Robots: {'✅' if result['robots_allowed'] else '❌'}")
        print(f"⏱️  Crawl delay: {result.get('crawl_delay', 'None')}")
        print(f"🔒 Blocking rules: {len(result['blocking_rules'])}")
        
        if result['recommendations']:
            print("💡 Recommendations:")
            for rec in result['recommendations'][:3]:
                print(f"   • {rec}")
    
    # Get violation statistics
    violations = engine.rule_engine.get_violations(hours=1)
    print(f"\n⚠️  Recent violations: {len(violations)}")
    
    await engine.close()


if __name__ == "__main__":
    asyncio.run(example_compliance_checking())
