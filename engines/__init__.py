#!/usr/bin/env python3
"""
Engines Package för Sparkling-Owl-Spin
Pyramid Architecture Engine Layer - Specialiserade motorkomponenter
"""

__version__ = "1.0.0"

# Engine categories
from . import scraping
from . import bypass
from . import network

# Engine registry
AVAILABLE_ENGINES = {
    "scraping": [
        "scraping_framework"
    ],
    "bypass": [
        "cloudflare_bypass",
        "captcha_solver", 
        "undetected_browser"
    ],
    "network": [
        "proxy_manager",
        "rate_limiter"
    ]
}

def get_available_engines():
    """Get list of all available engines"""
    engines = []
    for category, engine_list in AVAILABLE_ENGINES.items():
        engines.extend([f"{category}.{engine}" for engine in engine_list])
    return engines

__all__ = [
    "scraping",
    "bypass", 
    "network",
    "AVAILABLE_ENGINES",
    "get_available_engines"
]
