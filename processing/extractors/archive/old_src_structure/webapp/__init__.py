"""
WebApp Module - Web interface and APIs.

Provides comprehensive web interface including:
- Administrative dashboards
- Real-time monitoring views
- Template management interface
- Job control and monitoring
- User authentication and authorization
- API endpoints (REST and GraphQL)

Main Components:
- WebApp: Main Flask/FastAPI application
- Views: Dashboard and interface views
- APIs: REST and GraphQL endpoints
- Authentication: User management and security
- Templates: UI template management

API Modules:
- AuthAPI: Authentication endpoints
- JobsAPI: Job management endpoints
- TemplatesAPI: Template management
- MonitoringAPI: Real-time monitoring
- ExportsAPI: Data export functionality
- WebhooksAPI: Webhook management
"""

from .app import create_app
from .views import DashboardViews, TemplateViews, JobViews
from .auth import AuthManager, AuthenticationRequired
from .security import SecurityManager
from .api import APIRouter

# API modules
from .api import (
    AuthAPI, JobsAPI, TemplatesAPI, 
    MonitoringAPI, ExportsAPI, WebhooksAPI
)

__all__ = [
    "create_app",
    "DashboardViews",
    "TemplateViews", 
    "JobViews",
    "AuthManager",
    "AuthenticationRequired",
    "SecurityManager",
    "APIRouter",
    "AuthAPI",
    "JobsAPI",
    "TemplatesAPI",
    "MonitoringAPI", 
    "ExportsAPI",
    "WebhooksAPI"
]