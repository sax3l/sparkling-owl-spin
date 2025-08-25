"""
Proxy Pool API Module - RESTful API for proxy management.

Provides HTTP API endpoints for proxy pool operations including:
- Proxy acquisition and release
- Health monitoring and statistics
- Pool management and configuration
- Real-time metrics and monitoring

Main Components:
- ProxyAPI: Main API application
- ProxyServer: FastAPI server implementation
- ProxyEndpoints: REST endpoint definitions
"""

from .server import create_proxy_api, create_proxy_server

__all__ = [
    "create_proxy_api",
    "create_proxy_server"
]