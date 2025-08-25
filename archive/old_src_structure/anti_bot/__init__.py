"""
Anti-Bot Module - Advanced stealth and detection avoidance.

Provides comprehensive anti-bot protection including:
- Browser fingerprint modification
- Human behavior simulation
- Request pattern randomization
- Header and session management
- CAPTCHA detection and handling
- Policy-based protection strategies

Main Components:
- PolicyManager: Protection policy management
- HeaderGenerator: Realistic header generation
- SessionManager: Session and cookie management
- DelayStrategy: Human-like timing patterns
- FallbackStrategy: Adaptive protection strategies
- CredentialManager: Authentication handling

Browser Stealth:
- StealthBrowser: Advanced browser protection
- HumanBehavior: Human interaction simulation
- CaptchaSolver: CAPTCHA detection and response
- CloudflareDetector: Cloudflare protection detection and policy management

Diagnostics:
- DiagnoseURL: Website protection analysis
"""

from .policy_manager import PolicyManager, DomainPolicy, RiskLevel, PolicyAction, DetectionSignal
from .header_generator import HeaderGenerator
from .session_manager import SessionManager
from .delay_strategy import DelayStrategy
from .fallback_strategy import FallbackStrategy
from .credential_manager import CredentialManager

# Browser stealth components
from .browser_stealth import StealthBrowser, HumanBehavior, CaptchaSolver, CloudflareDetector

# Diagnostic tools
from .diagnostics import DiagnoseURL

__all__ = [
    "PolicyManager",
    "AntiBot",
    "HeaderGenerator",
    "SessionManager",
    "DelayStrategy", 
    "FallbackStrategy",
    "CredentialManager",
    "StealthBrowser",
    "HumanBehavior",
    "CaptchaSolver",
    "CloudflareDetector",
    "DiagnoseURL"
]