"""
Cloudflare Challenge Detection and Policy Management.

This module focuses on ethical detection and handling of Cloudflare protection:
- Detection of Cloudflare challenge pages
- Policy-based response decisions
- Graceful job suspension when challenges are detected
- Respect for website protection mechanisms

IMPORTANT: This module does NOT attempt to bypass Cloudflare protection.
It follows ethical crawling practices by detecting and respecting anti-bot measures.
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse

from playwright.async_api import Page
from lxml import html

from ...utils.logger import get_logger
from ...observability.metrics import MetricsCollector

logger = get_logger(__name__)


@dataclass
class CloudflareDetection:
    """Result of Cloudflare detection analysis."""
    is_cloudflare: bool
    challenge_type: Optional[str] = None
    challenge_page_content: Optional[str] = None
    estimated_wait_time: Optional[int] = None
    bypass_recommended: bool = False
    policy_action: str = "respect"  # always respect
    
    
class CloudflareDetector:
    """
    Ethical Cloudflare challenge detector and policy manager.
    
    Detects Cloudflare protection mechanisms and recommends appropriate
    policy responses that respect website protection measures.
    """
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        
        # Cloudflare detection patterns
        self.cloudflare_indicators = [
            "Checking your browser before accessing",
            "DDoS protection by Cloudflare",
            "cf-browser-verification",
            "cf-challenge-page",
            "cf-wrapper",
            "cloudflare",
            "ray-id",
            "__cf_bm",
            "cf_clearance"
        ]
        
        # Challenge types we can detect
        self.challenge_types = {
            "browser_check": ["Checking your browser", "browser check"],
            "captcha": ["captcha", "recaptcha", "hcaptcha"],
            "rate_limit": ["rate limit", "too many requests"],
            "bot_detection": ["bot detected", "automated requests"],
            "under_attack": ["under attack mode", "ddos protection"]
        }
        
    async def detect_cloudflare_challenge(self, page: Page, url: str) -> CloudflareDetection:
        """
        Detect if current page shows a Cloudflare challenge.
        
        Args:
            page: Playwright page object
            url: URL being accessed
            
        Returns:
            CloudflareDetection with analysis results
        """
        try:
            # Get page content and title
            content = await page.content()
            title = await page.title()
            
            # Check for Cloudflare indicators
            content_lower = content.lower()
            title_lower = title.lower()
            
            is_cloudflare = any(
                indicator.lower() in content_lower or indicator.lower() in title_lower
                for indicator in self.cloudflare_indicators
            )
            
            if not is_cloudflare:
                return CloudflareDetection(is_cloudflare=False)
                
            # Determine challenge type
            challenge_type = self._identify_challenge_type(content_lower, title_lower)
            
            # Estimate wait time based on challenge type
            estimated_wait = self._estimate_wait_time(challenge_type)
            
            # Log detection
            logger.warning(f"Cloudflare challenge detected on {url}: {challenge_type}")
            
            # Update metrics
            self.metrics.counter(f"cloudflare_challenge_{challenge_type}", 1)
            self.metrics.counter("cloudflare_challenges_total", 1)
            
            return CloudflareDetection(
                is_cloudflare=True,
                challenge_type=challenge_type,
                challenge_page_content=content[:1000],  # Store snippet
                estimated_wait_time=estimated_wait,
                bypass_recommended=False,  # Never recommend bypass
                policy_action="respect"
            )
            
        except Exception as e:
            logger.error(f"Error detecting Cloudflare challenge: {e}")
            return CloudflareDetection(is_cloudflare=False)
            
    def _identify_challenge_type(self, content: str, title: str) -> str:
        """Identify the specific type of Cloudflare challenge."""
        text = f"{content} {title}"
        
        for challenge_type, keywords in self.challenge_types.items():
            if any(keyword in text for keyword in keywords):
                return challenge_type
                
        return "unknown_challenge"
        
    def _estimate_wait_time(self, challenge_type: str) -> int:
        """Estimate wait time based on challenge type."""
        wait_times = {
            "browser_check": 5,      # Browser verification usually takes ~5 seconds
            "captcha": 30,           # CAPTCHA requires human intervention
            "rate_limit": 60,        # Rate limiting typically 1+ minutes
            "bot_detection": 300,    # Bot detection can be longer
            "under_attack": 600,     # Under attack mode can be very long
            "unknown_challenge": 30  # Default conservative estimate
        }
        
        return wait_times.get(challenge_type, 30)
        
    async def handle_cloudflare_policy(
        self, 
        detection: CloudflareDetection, 
        domain: str
    ) -> Dict[str, Any]:
        """
        Handle Cloudflare detection according to ethical policy.
        
        Args:
            detection: CloudflareDetection result
            domain: Domain being accessed
            
        Returns:
            Policy action recommendations
        """
        if not detection.is_cloudflare:
            return {"action": "continue", "wait_time": 0}
            
        # Log the policy decision
        logger.info(f"Cloudflare detected on {domain} - applying ethical policy")
        
        # Update domain-specific metrics
        self.metrics.counter(f"cloudflare_policy_applied_{domain}", 1)
        
        # Ethical policy: respect the protection
        policy_response = {
            "action": "suspend",  # Suspend the crawling job
            "reason": f"Cloudflare {detection.challenge_type} detected",
            "respect_protection": True,
            "retry_after": detection.estimated_wait_time * 2,  # Conservative retry
            "domain": domain,
            "challenge_type": detection.challenge_type,
            "estimated_wait": detection.estimated_wait_time,
            "recommendation": (
                f"Cloudflare protection detected. "
                f"Suspending crawling to respect anti-bot measures. "
                f"Consider manual verification or contact site owner."
            )
        }
        
        return policy_response
        
    async def wait_for_challenge_completion(
        self, 
        page: Page, 
        max_wait_time: int = 30
    ) -> bool:
        """
        Wait for Cloudflare challenge to complete (if automatic).
        
        Only waits for automatic browser verification, not CAPTCHAs.
        
        Args:
            page: Playwright page object
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            True if challenge completed, False if still blocked
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # Check if we're still on a Cloudflare challenge page
                content = await page.content()
                detection = await self.detect_cloudflare_challenge(page, page.url)
                
                if not detection.is_cloudflare:
                    logger.info("Cloudflare challenge completed automatically")
                    return True
                    
                # Only wait for automatic browser checks
                if detection.challenge_type not in ["browser_check"]:
                    logger.info(f"Manual intervention required for {detection.challenge_type}")
                    return False
                    
                # Wait a bit before checking again
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error waiting for challenge completion: {e}")
                return False
                
        logger.warning(f"Cloudflare challenge did not complete within {max_wait_time} seconds")
        return False
        
    def get_domain_cloudflare_stats(self, domain: str) -> Dict[str, Any]:
        """Get Cloudflare-related statistics for a domain."""
        # This would integrate with metrics collector to get historical data
        return {
            "domain": domain,
            "total_challenges": 0,  # Would be retrieved from metrics
            "challenge_types": {},   # Would be aggregated from metrics
            "last_challenge": None,  # Would be retrieved from storage
            "success_rate": 0.0,     # Would be calculated from metrics
            "average_wait_time": 0.0 # Would be calculated from metrics
        }
        
    def create_challenge_report(self, detection: CloudflareDetection, url: str) -> Dict[str, Any]:
        """Create a detailed report of the Cloudflare challenge."""
        return {
            "timestamp": time.time(),
            "url": url,
            "domain": urlparse(url).netloc,
            "challenge_detected": detection.is_cloudflare,
            "challenge_type": detection.challenge_type,
            "estimated_wait_time": detection.estimated_wait_time,
            "policy_action": detection.policy_action,
            "content_snippet": detection.challenge_page_content,
            "ethical_compliance": True,
            "bypass_attempted": False,
            "recommendations": [
                "Respect the website's anti-bot protection",
                "Consider contacting site owner for API access",
                "Implement longer delays between requests",
                "Review crawling necessity and ethics"
            ]
        }


# Ethical utility functions
def should_respect_cloudflare(challenge_type: str) -> bool:
    """
    Always return True - we always respect Cloudflare protection.
    
    This function exists to make the ethical stance explicit in code.
    """
    return True


def get_ethical_recommendations(challenge_type: str) -> List[str]:
    """Get ethical recommendations for handling Cloudflare challenges."""
    base_recommendations = [
        "Respect the website's protection mechanisms",
        "Do not attempt to bypass anti-bot measures",
        "Consider if crawling is necessary and ethical",
        "Implement appropriate delays and rate limiting"
    ]
    
    specific_recommendations = {
        "browser_check": [
            "Allow automatic browser verification to complete",
            "Ensure browser fingerprint appears legitimate"
        ],
        "captcha": [
            "Do not use automated CAPTCHA solving",
            "Consider manual verification if absolutely necessary",
            "Evaluate if the data is available through legitimate APIs"
        ],
        "rate_limit": [
            "Significantly reduce request rate",
            "Implement exponential backoff",
            "Consider spreading requests over longer time periods"
        ],
        "bot_detection": [
            "Review and improve bot detection avoidance strategies",
            "Ensure requests appear more human-like",
            "Consider contacting site owner for permission"
        ],
        "under_attack": [
            "Suspend crawling activities temporarily",
            "Respect the site's need for protection",
            "Try again much later or seek alternative data sources"
        ]
    }
    
    return base_recommendations + specific_recommendations.get(challenge_type, [])