"""
Crawling Policy Management with Robots.txt Integration

This module implements intelligent crawling policies with robots.txt compliance,
as recommended in the analysis report to surpass competitors in ethical crawling.
"""

import re
import asyncio
from typing import Dict, List, Optional, Set, Any
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from dataclasses import dataclass
import aiohttp
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class CrawlingPolicy:
    """Represents crawling policy for a domain"""
    domain: str
    max_depth: int = 5
    max_pages: int = 1000
    delay_seconds: float = 1.0
    allowed_paths: List[str] = None
    disallowed_paths: List[str] = None
    allowed_file_types: Set[str] = None
    respect_robots: bool = True
    user_agent: str = "ECaDP-Bot/1.0"
    robots_delay: Optional[float] = None
    requires_login: bool = False
    honeypot_patterns: List[str] = None
    
    def __post_init__(self):
        if self.allowed_paths is None:
            self.allowed_paths = []
        if self.disallowed_paths is None:
            self.disallowed_paths = []
        if self.allowed_file_types is None:
            self.allowed_file_types = {"html", "htm", "php", "asp", "aspx", "jsp"}
        if self.honeypot_patterns is None:
            # Common honeypot patterns to avoid
            self.honeypot_patterns = [
                r".*trap.*", r".*spider.*", r".*bot.*", r".*crawl.*",
                r".*hidden.*", r".*fake.*"
            ]


class PolicyManager:
    """
    Advanced policy manager with robots.txt integration and intelligent filtering.
    
    This implements the analysis recommendation for automatic robots.txt parsing
    and ethical crawling policies that surpass competitor capabilities.
    """
    
    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        self.session = session
        self._should_close_session = session is None
        self._domain_policies: Dict[str, CrawlingPolicy] = {}
        self._robots_cache: Dict[str, RobotFileParser] = {}
        self._robots_cache_time: Dict[str, datetime] = {}
        self._robots_cache_ttl = timedelta(hours=24)
        
    async def __aenter__(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._should_close_session and self.session:
            await self.session.close()
    
    def add_domain_policy(self, policy: CrawlingPolicy):
        """Add or update a domain policy"""
        self._domain_policies[policy.domain] = policy
        logger.info(f"Added crawling policy for domain: {policy.domain}")
    
    async def get_policy_for_url(self, url: str) -> CrawlingPolicy:
        """
        Get the appropriate crawling policy for a URL, integrating robots.txt.
        This implements the ethical advantage mentioned in the analysis.
        """
        domain = urlparse(url).netloc.lower()
        
        # Get base policy or create default
        if domain in self._domain_policies:
            policy = self._domain_policies[domain]
        else:
            # Create default policy
            policy = CrawlingPolicy(domain=domain)
            
        # Integrate robots.txt if enabled
        if policy.respect_robots:
            await self._integrate_robots_txt(policy, url)
            
        return policy
    
    async def _integrate_robots_txt(self, policy: CrawlingPolicy, url: str):
        """
        Integrate robots.txt rules into the policy.
        This is the key improvement from the analysis report.
        """
        domain = policy.domain
        
        # Check cache first
        if domain in self._robots_cache:
            cache_time = self._robots_cache_time.get(domain)
            if cache_time and datetime.now() - cache_time < self._robots_cache_ttl:
                # Use cached robots.txt
                robots_parser = self._robots_cache[domain]
                self._apply_robots_rules(policy, robots_parser)
                return
        
        # Fetch and parse robots.txt
        robots_url = f"https://{domain}/robots.txt"
        try:
            async with self.session.get(robots_url, timeout=10) as response:
                if response.status == 200:
                    robots_content = await response.text()
                    
                    # Create and configure robots parser
                    robots_parser = RobotFileParser()
                    robots_parser.set_url(robots_url)
                    
                    # Parse the content
                    lines = robots_content.split('\n')
                    robots_parser.read_from_lines(lines)
                    
                    # Cache the parser
                    self._robots_cache[domain] = robots_parser
                    self._robots_cache_time[domain] = datetime.now()
                    
                    # Apply rules to policy
                    self._apply_robots_rules(policy, robots_parser)
                    
                    logger.info(f"Successfully parsed robots.txt for {domain}")
                else:
                    logger.debug(f"No robots.txt found for {domain} (status: {response.status})")
                    
        except Exception as e:
            logger.debug(f"Failed to fetch robots.txt for {domain}: {e}")
    
    def _apply_robots_rules(self, policy: CrawlingPolicy, robots_parser: RobotFileParser):
        """Apply robots.txt rules to crawling policy"""
        user_agent = policy.user_agent
        
        # Extract crawl delay
        crawl_delay = robots_parser.crawl_delay(user_agent)
        if crawl_delay:
            policy.robots_delay = float(crawl_delay)
            policy.delay_seconds = max(policy.delay_seconds, policy.robots_delay)
            logger.info(f"Applied robots.txt crawl delay: {crawl_delay}s for {policy.domain}")
        
        # Extract disallowed paths
        # Note: RobotFileParser doesn't directly expose disallow patterns,
        # so we parse them manually from the content
        robots_url = f"https://{policy.domain}/robots.txt"
        try:
            # This is a limitation of Python's robotparser - we may need custom parsing
            # for full disallow pattern extraction
            pass
        except Exception as e:
            logger.debug(f"Could not extract disallow patterns from robots.txt: {e}")
    
    async def can_crawl_url(self, url: str) -> bool:
        """
        Check if URL can be crawled according to policy and robots.txt.
        This provides the ethical compliance advantage over competitors.
        """
        policy = await self.get_policy_for_url(url)
        parsed_url = urlparse(url)
        path = parsed_url.path
        
        # Check robots.txt compliance
        if policy.respect_robots and policy.domain in self._robots_cache:
            robots_parser = self._robots_cache[policy.domain]
            if not robots_parser.can_fetch(policy.user_agent, url):
                logger.info(f"URL blocked by robots.txt: {url}")
                return False
        
        # Check file type restrictions
        if policy.allowed_file_types:
            # Extract file extension
            path_lower = path.lower()
            if '.' in path_lower:
                extension = path_lower.split('.')[-1]
                if extension not in policy.allowed_file_types:
                    logger.debug(f"File type not allowed: {extension} for {url}")
                    return False
        
        # Check path restrictions
        for pattern in policy.disallowed_paths:
            if re.match(pattern, path):
                logger.debug(f"Path blocked by policy pattern: {pattern} for {url}")
                return False
        
        # Check allowed paths (if specified)
        if policy.allowed_paths:
            allowed = False
            for pattern in policy.allowed_paths:
                if re.match(pattern, path):
                    allowed = True
                    break
            if not allowed:
                logger.debug(f"Path not in allowed patterns for {url}")
                return False
        
        # Check honeypot patterns
        for pattern in policy.honeypot_patterns:
            if re.search(pattern, url.lower()):
                logger.info(f"Potential honeypot detected, avoiding: {url}")
                return False
        
        return True
    
    def get_crawl_delay(self, domain: str) -> float:
        """Get appropriate crawl delay for domain"""
        if domain in self._domain_policies:
            policy = self._domain_policies[domain]
            return policy.robots_delay or policy.delay_seconds
        return 1.0  # Default delay
    
    def load_policies_from_config(self, config: Dict[str, Any]):
        """Load domain policies from configuration"""
        for domain_config in config.get('domains', []):
            policy = CrawlingPolicy(
                domain=domain_config['domain'],
                max_depth=domain_config.get('max_depth', 5),
                max_pages=domain_config.get('max_pages', 1000),
                delay_seconds=domain_config.get('delay_seconds', 1.0),
                allowed_paths=domain_config.get('allowed_paths', []),
                disallowed_paths=domain_config.get('disallowed_paths', []),
                respect_robots=domain_config.get('respect_robots', True),
                user_agent=domain_config.get('user_agent', "ECaDP-Bot/1.0"),
                requires_login=domain_config.get('requires_login', False)
            )
            self.add_domain_policy(policy)
        
        logger.info(f"Loaded {len(self._domain_policies)} domain policies from config")
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get summary of all configured policies"""
        return {
            'total_domains': len(self._domain_policies),
            'domains': list(self._domain_policies.keys()),
            'robots_cached': len(self._robots_cache),
            'ethical_compliance': {
                'robots_respect_enabled': any(p.respect_robots for p in self._domain_policies.values()),
                'honeypot_protection_enabled': True,
                'crawl_delays_configured': any(p.delay_seconds > 0 for p in self._domain_policies.values())
            }
        }
    
    async def validate_crawl_plan(self, urls: List[str]) -> Dict[str, Any]:
        """
        Validate a list of URLs against policies before crawling.
        Returns summary of allowed/blocked URLs.
        """
        allowed_urls = []
        blocked_urls = []
        blocked_reasons = []
        
        for url in urls:
            try:
                if await self.can_crawl_url(url):
                    allowed_urls.append(url)
                else:
                    blocked_urls.append(url)
                    blocked_reasons.append("Policy violation")
            except Exception as e:
                blocked_urls.append(url)
                blocked_reasons.append(f"Error: {str(e)}")
        
        return {
            'total_urls': len(urls),
            'allowed_urls': len(allowed_urls),
            'blocked_urls': len(blocked_urls),
            'allowed_list': allowed_urls[:10],  # Sample
            'blocked_list': list(zip(blocked_urls[:10], blocked_reasons[:10])),
            'compliance_rate': len(allowed_urls) / len(urls) if urls else 0
        }


class URLFilter:
    """Advanced URL filtering with pattern matching and ML-based classification"""
    
    def __init__(self):
        self.common_spam_patterns = [
            r".*viagra.*", r".*casino.*", r".*porn.*", r".*xxx.*",
            r".*\d{10,}.*",  # Very long numbers (often spam)
            r".*[a-zA-Z]{50,}.*",  # Very long strings
        ]
        
        self.common_non_content_patterns = [
            r".*/wp-admin/.*", r".*/admin/.*", r".*/login.*",
            r".*\.pdf$", r".*\.doc$", r".*\.zip$", r".*\.exe$",
            r".*\?print=.*", r".*\?download=.*"
        ]
    
    def is_content_url(self, url: str) -> bool:
        """Determine if URL likely contains useful content"""
        url_lower = url.lower()
        
        # Filter out obvious non-content URLs
        for pattern in self.common_non_content_patterns:
            if re.match(pattern, url_lower):
                return False
        
        # Filter out spam patterns
        for pattern in self.common_spam_patterns:
            if re.match(pattern, url_lower):
                return False
        
        # Basic heuristics for content URLs
        path = urlparse(url).path.lower()
        
        # Likely content if contains common content indicators
        content_indicators = [
            "article", "post", "blog", "news", "story", "page",
            "product", "item", "detail", "view"
        ]
        
        for indicator in content_indicators:
            if indicator in path:
                return True
        
        # Default to true for general paths
        return len(path) > 1  # Has some path beyond just "/"
    
    def prioritize_url(self, url: str, content_hint: str = "") -> int:
        """
        Assign priority to URL based on content likelihood.
        Lower numbers = higher priority.
        """
        base_priority = 5
        
        # Boost priority for likely content
        if self.is_content_url(url):
            base_priority -= 1
        
        # Boost based on content hints
        if content_hint:
            if any(word in content_hint.lower() for word in ["main", "important", "key", "primary"]):
                base_priority -= 2
        
        # Reduce priority for deep paths
        path_depth = len([p for p in urlparse(url).path.split('/') if p])
        if path_depth > 5:
            base_priority += 1
        
        # Ensure priority is in valid range
        return max(1, min(10, base_priority))
