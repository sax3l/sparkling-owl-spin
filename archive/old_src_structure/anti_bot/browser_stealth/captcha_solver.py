"""
CAPTCHA detection and handling system.

This module provides ethical CAPTCHA handling including:
- CAPTCHA detection and logging
- Manual intervention hooks  
- Rate limiting adjustments
- Respectful retry mechanisms

NOTE: This implementation does NOT attempt to automatically solve or bypass 
CAPTCHAs, in accordance with ethical scraping practices and ToS compliance.
"""

import time
import asyncio
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import base64
from datetime import datetime, timedelta

from utils.logger import get_logger

logger = get_logger(__name__)

class CaptchaType(Enum):
    """Types of CAPTCHA challenges detected."""
    RECAPTCHA_V2 = "recaptcha_v2"
    RECAPTCHA_V3 = "recaptcha_v3" 
    HCAPTCHA = "hcaptcha"
    CLOUDFLARE = "cloudflare"
    SIMPLE_MATH = "simple_math"
    IMAGE_SELECTION = "image_selection"
    TEXT_CAPTCHA = "text_captcha"
    UNKNOWN = "unknown"

@dataclass
class CaptchaDetection:
    """Information about a detected CAPTCHA."""
    captcha_type: CaptchaType
    detected_at: datetime
    url: str
    source_html: str
    screenshot_data: Optional[str] = None
    selector: Optional[str] = None
    challenge_text: Optional[str] = None
    confidence: float = 0.0

class CaptchaDetector:
    """Detects various types of CAPTCHA challenges."""
    
    def __init__(self):
        self.detection_patterns = self._load_detection_patterns()
        self.detection_history: List[CaptchaDetection] = []
    
    def _load_detection_patterns(self) -> Dict[CaptchaType, List[Dict[str, str]]]:
        """Load CAPTCHA detection patterns."""
        return {
            CaptchaType.RECAPTCHA_V2: [
                {"selector": "iframe[src*='recaptcha']", "confidence": 0.95},
                {"selector": ".g-recaptcha", "confidence": 0.9},
                {"text": "I'm not a robot", "confidence": 0.85},
                {"text": "verify that you are human", "confidence": 0.8}
            ],
            CaptchaType.RECAPTCHA_V3: [
                {"selector": "script[src*='recaptcha/api.js']", "confidence": 0.9},
                {"text": "grecaptcha", "confidence": 0.7}
            ],
            CaptchaType.HCAPTCHA: [
                {"selector": "iframe[src*='hcaptcha']", "confidence": 0.95},
                {"selector": ".h-captcha", "confidence": 0.9},
                {"text": "hCaptcha", "confidence": 0.85}
            ],
            CaptchaType.CLOUDFLARE: [
                {"text": "Checking your browser", "confidence": 0.9},
                {"text": "cloudflare", "confidence": 0.7},
                {"selector": "#challenge-form", "confidence": 0.8}
            ],
            CaptchaType.SIMPLE_MATH: [
                {"text_pattern": r"\d+\s*[+\-*\/]\s*\d+\s*=", "confidence": 0.8}
            ],
            CaptchaType.IMAGE_SELECTION: [
                {"text": "Select all images", "confidence": 0.8},
                {"text": "Click on all", "confidence": 0.7},
                {"selector": ".captcha-image", "confidence": 0.75}
            ]
        }
    
    async def detect_captcha(self, page_source: str, url: str, 
                           driver=None) -> Optional[CaptchaDetection]:
        """Detect CAPTCHA on the current page."""
        try:
            # Check each CAPTCHA type
            for captcha_type, patterns in self.detection_patterns.items():
                detection = await self._check_patterns(
                    captcha_type, patterns, page_source, url, driver
                )
                if detection:
                    self.detection_history.append(detection)
                    logger.warning(f"CAPTCHA detected: {captcha_type.value} on {url}")
                    return detection
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return None
    
    async def _check_patterns(self, captcha_type: CaptchaType, patterns: List[Dict],
                            page_source: str, url: str, driver) -> Optional[CaptchaDetection]:
        """Check detection patterns for a specific CAPTCHA type."""
        max_confidence = 0.0
        best_match = None
        
        for pattern in patterns:
            confidence = 0.0
            selector = None
            challenge_text = None
            
            # Check selector patterns
            if "selector" in pattern and driver:
                try:
                    elements = driver.find_elements("css selector", pattern["selector"])
                    if elements:
                        confidence = pattern["confidence"]
                        selector = pattern["selector"]
                except:
                    pass
            
            # Check text patterns
            if "text" in pattern:
                if pattern["text"].lower() in page_source.lower():
                    confidence = pattern["confidence"]
                    challenge_text = pattern["text"]
            
            # Check regex patterns
            if "text_pattern" in pattern:
                import re
                if re.search(pattern["text_pattern"], page_source, re.IGNORECASE):
                    confidence = pattern["confidence"]
            
            if confidence > max_confidence:
                max_confidence = confidence
                best_match = {
                    "selector": selector,
                    "challenge_text": challenge_text,
                    "confidence": confidence
                }
        
        # Threshold for positive detection
        if max_confidence > 0.7:
            screenshot_data = None
            if driver:
                try:
                    screenshot_data = driver.get_screenshot_as_base64()
                except:
                    pass
            
            return CaptchaDetection(
                captcha_type=captcha_type,
                detected_at=datetime.utcnow(),
                url=url,
                source_html=page_source[:1000],  # Truncate for storage
                screenshot_data=screenshot_data,
                selector=best_match["selector"],
                challenge_text=best_match["challenge_text"],
                confidence=max_confidence
            )
        
        return None
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get CAPTCHA detection statistics."""
        if not self.detection_history:
            return {"total_detections": 0}
        
        # Count by type
        type_counts = {}
        for detection in self.detection_history:
            type_name = detection.captcha_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        # Recent detections (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_detections = [
            d for d in self.detection_history 
            if d.detected_at > one_hour_ago
        ]
        
        return {
            "total_detections": len(self.detection_history),
            "detections_by_type": type_counts,
            "recent_detections_1h": len(recent_detections),
            "last_detection": self.detection_history[-1].detected_at.isoformat() if self.detection_history else None
        }

class CaptchaHandler:
    """Handles CAPTCHA encounters with ethical approaches."""
    
    def __init__(self, manual_solve_callback: Optional[Callable] = None):
        self.detector = CaptchaDetector()
        self.manual_solve_callback = manual_solve_callback
        self.rate_limit_adjustments = {}
        self.encounter_count = 0
        
    async def handle_captcha_encounter(self, page_source: str, url: str, 
                                     driver=None) -> Dict[str, Any]:
        """Handle a CAPTCHA encounter ethically."""
        self.encounter_count += 1
        
        # Detect CAPTCHA type
        detection = await self.detector.detect_captcha(page_source, url, driver)
        
        if not detection:
            return {"status": "no_captcha_detected"}
        
        logger.info(f"CAPTCHA encountered: {detection.captcha_type.value} on {url}")
        
        # Log the encounter for analysis
        await self._log_captcha_encounter(detection)
        
        # Apply rate limiting adjustments
        await self._adjust_rate_limits(detection)
        
        # Attempt ethical resolution
        resolution_result = await self._attempt_ethical_resolution(detection, driver)
        
        return {
            "status": "captcha_detected",
            "captcha_type": detection.captcha_type.value,
            "confidence": detection.confidence,
            "resolution": resolution_result,
            "recommendations": self._get_recommendations(detection)
        }
    
    async def _log_captcha_encounter(self, detection: CaptchaDetection):
        """Log CAPTCHA encounter for analysis and compliance."""
        log_data = {
            "event": "captcha_encounter",
            "captcha_type": detection.captcha_type.value,
            "url": detection.url,
            "timestamp": detection.detected_at.isoformat(),
            "confidence": detection.confidence,
            "encounter_count": self.encounter_count
        }
        
        # Log to structured logger
        logger.info("CAPTCHA encounter logged", extra=log_data)
        
        # Save screenshot if available (for manual review)
        if detection.screenshot_data:
            timestamp_str = detection.detected_at.strftime("%Y%m%d_%H%M%S")
            filename = f"captcha_screenshot_{timestamp_str}.png"
            
            try:
                # Save screenshot for manual review
                screenshot_data = base64.b64decode(detection.screenshot_data)
                with open(f"logs/{filename}", "wb") as f:
                    f.write(screenshot_data)
                logger.info(f"CAPTCHA screenshot saved: {filename}")
            except Exception as e:
                logger.error(f"Failed to save CAPTCHA screenshot: {e}")
    
    async def _adjust_rate_limits(self, detection: CaptchaDetection):
        """Adjust rate limits based on CAPTCHA encounter."""
        domain = detection.url.split('/')[2] if '/' in detection.url else detection.url
        
        # Increase delays for this domain
        current_delay = self.rate_limit_adjustments.get(domain, 1.0)
        new_delay = min(current_delay * 2, 60.0)  # Max 60 seconds
        
        self.rate_limit_adjustments[domain] = new_delay
        
        logger.info(f"Rate limit adjusted for {domain}: {new_delay}s delay")
    
    async def _attempt_ethical_resolution(self, detection: CaptchaDetection, 
                                        driver=None) -> Dict[str, Any]:
        """Attempt ethical CAPTCHA resolution."""
        
        # Option 1: Wait and retry (some CAPTCHAs are temporary)
        if detection.captcha_type == CaptchaType.CLOUDFLARE:
            logger.info("Cloudflare challenge detected, waiting for automatic resolution...")
            await asyncio.sleep(10)  # Wait for Cloudflare check
            return {"method": "wait", "status": "attempted"}
        
        # Option 2: Manual intervention callback
        if self.manual_solve_callback:
            logger.info("Calling manual solve callback...")
            try:
                result = await self.manual_solve_callback(detection, driver)
                return {"method": "manual_callback", "status": "completed", "result": result}
            except Exception as e:
                logger.error(f"Manual solve callback failed: {e}")
                return {"method": "manual_callback", "status": "failed", "error": str(e)}
        
        # Option 3: Respect the CAPTCHA and back off
        logger.info("No automated resolution attempted, respecting CAPTCHA challenge")
        return {
            "method": "respectful_backoff", 
            "status": "backed_off",
            "message": "CAPTCHA respected, no automated solving attempted"
        }
    
    def _get_recommendations(self, detection: CaptchaDetection) -> List[str]:
        """Get recommendations for handling this CAPTCHA type."""
        recommendations = [
            "Respect the website's anti-bot measures",
            "Consider reducing request rate",
            "Review robots.txt compliance",
            "Implement longer delays between requests"
        ]
        
        if detection.captcha_type == CaptchaType.RECAPTCHA_V2:
            recommendations.extend([
                "Consider using different user agents",
                "Rotate IP addresses if using proxies",
                "Add human-like browsing patterns"
            ])
        elif detection.captcha_type == CaptchaType.CLOUDFLARE:
            recommendations.extend([
                "Wait for automatic verification",
                "Use residential proxies if necessary",
                "Ensure browser fingerprint looks realistic"
            ])
        elif detection.captcha_type == CaptchaType.HCAPTCHA:
            recommendations.extend([
                "Review accessibility compliance",
                "Consider alternative data sources",
                "Implement manual intervention workflow"
            ])
        
        return recommendations
    
    def get_rate_limit_adjustment(self, domain: str) -> float:
        """Get rate limit adjustment for a domain."""
        return self.rate_limit_adjustments.get(domain, 1.0)
    
    def reset_rate_limit_adjustment(self, domain: str):
        """Reset rate limit adjustment for a domain."""
        if domain in self.rate_limit_adjustments:
            del self.rate_limit_adjustments[domain]
            logger.info(f"Rate limit adjustment reset for {domain}")

class CaptchaResponseTracker:
    """Tracks and analyzes CAPTCHA encounter patterns."""
    
    def __init__(self):
        self.encounters = []
        self.domain_stats = {}
    
    def record_encounter(self, detection: CaptchaDetection, resolution_result: Dict):
        """Record a CAPTCHA encounter and its resolution."""
        encounter_record = {
            "timestamp": detection.detected_at,
            "url": detection.url,
            "domain": detection.url.split('/')[2] if '/' in detection.url else detection.url,
            "captcha_type": detection.captcha_type,
            "confidence": detection.confidence,
            "resolution_method": resolution_result.get("method"),
            "resolution_status": resolution_result.get("status")
        }
        
        self.encounters.append(encounter_record)
        
        # Update domain statistics
        domain = encounter_record["domain"]
        if domain not in self.domain_stats:
            self.domain_stats[domain] = {
                "total_encounters": 0,
                "captcha_types": {},
                "last_encounter": None
            }
        
        stats = self.domain_stats[domain]
        stats["total_encounters"] += 1
        stats["last_encounter"] = detection.detected_at
        
        captcha_type = detection.captcha_type.value
        stats["captcha_types"][captcha_type] = stats["captcha_types"].get(captcha_type, 0) + 1
    
    def get_domain_analysis(self, domain: str) -> Dict[str, Any]:
        """Get analysis for a specific domain."""
        if domain not in self.domain_stats:
            return {"status": "no_data"}
        
        stats = self.domain_stats[domain]
        
        # Calculate encounter frequency
        domain_encounters = [e for e in self.encounters if e["domain"] == domain]
        if len(domain_encounters) > 1:
            time_diffs = []
            for i in range(1, len(domain_encounters)):
                diff = (domain_encounters[i]["timestamp"] - domain_encounters[i-1]["timestamp"]).total_seconds()
                time_diffs.append(diff)
            
            avg_time_between = sum(time_diffs) / len(time_diffs) if time_diffs else 0
        else:
            avg_time_between = 0
        
        return {
            "domain": domain,
            "total_encounters": stats["total_encounters"],
            "captcha_types": stats["captcha_types"],
            "last_encounter": stats["last_encounter"].isoformat() if stats["last_encounter"] else None,
            "avg_time_between_encounters": avg_time_between,
            "risk_level": self._assess_risk_level(stats["total_encounters"], avg_time_between)
        }
    
    def _assess_risk_level(self, total_encounters: int, avg_time_between: float) -> str:
        """Assess risk level for a domain based on CAPTCHA patterns."""
        if total_encounters == 0:
            return "none"
        elif total_encounters == 1:
            return "low"
        elif total_encounters < 5 and avg_time_between > 3600:  # < 5 encounters, > 1 hour apart
            return "medium"
        else:
            return "high"

# Factory functions
def create_captcha_detector() -> CaptchaDetector:
    """Create a CAPTCHA detector instance."""
    return CaptchaDetector()

def create_captcha_handler(manual_callback: Optional[Callable] = None) -> CaptchaHandler:
    """Create a CAPTCHA handler with optional manual intervention callback."""
    return CaptchaHandler(manual_callback)

# Utility function for manual intervention
async def manual_intervention_prompt(detection: CaptchaDetection, driver=None) -> Dict[str, Any]:
    """Prompt for manual intervention when CAPTCHA is encountered."""
    logger.info(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CAPTCHA DETECTED                          ║
    ╠══════════════════════════════════════════════════════════════╣
    ║ Type: {detection.captcha_type.value:<50} ║
    ║ URL: {detection.url:<51} ║
    ║ Confidence: {detection.confidence:<45.2f} ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Manual intervention required.
    Please resolve the CAPTCHA manually if appropriate and ethical.
    """)
    
    # In a real implementation, this might:
    # 1. Send notification to operator
    # 2. Pause automation
    # 3. Wait for manual resolution
    # 4. Return result
    
    return {
        "status": "manual_intervention_required",
        "message": "CAPTCHA requires manual review",
        "captcha_type": detection.captcha_type.value
    }


# Backward compatibility alias
CaptchaSolver = CaptchaHandler