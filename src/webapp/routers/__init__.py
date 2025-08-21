"""
Router package for the web application.
"""
from .health import router as health_router
from .auth import router as auth_router
from .data import router as data_router
from .jobs import router as jobs_router

# Import other routers as they are created
try:
    from .webhooks import router as webhooks_router
except ImportError:
    webhooks_router = None

try:
    from .admin import router as admin_router
except ImportError:
    admin_router = None

try:
    from .crawler import router as crawler_router
except ImportError:
    crawler_router = None

try:
    from .scraper import router as scraper_router
except ImportError:
    scraper_router = None

__all__ = [
    "health_router",
    "auth_router", 
    "data_router",
    "jobs_router",
    "webhooks_router",
    "admin_router",
    "crawler_router",
    "scraper_router"
]
