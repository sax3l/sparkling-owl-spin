"""
Proxy Pool Module - Advanced proxy management and rotation.

Provides comprehensive proxy pool management including:
- Proxy collection from multiple sources
- Health monitoring and validation
- Quality filtering and scoring
- Intelligent rotation and assignment
- Performance monitoring
- Geographic and anonymity-based selection

Main Components:
- ProxyManager: Core proxy management
- ProxyCollector: Proxy source collection
- ProxyValidator: Health checking and validation
- ProxyMonitor: Real-time monitoring
- ProxyQualityFilter: Proxy quality assessment
- ProxyRotator: Intelligent rotation logic
- PoolAdapter: Protocol adaptation
"""

from .manager import ProxyManager
from .collector import ProxyCollector
from .validator import ProxyValidator
from .monitor import ProxyMonitor
from .quality_filter import ProxyQualityFilter
from .rotator import ProxyRotator
from .adapters import PoolAdapter

# API components
from .api import create_proxy_api

__all__ = [
    "ProxyManager",
    "ProxyCollector",
    "ProxyValidator",
    "ProxyMonitor", 
    "ProxyQualityFilter",
    "ProxyRotator",
    "PoolAdapter",
    "create_proxy_api"
]