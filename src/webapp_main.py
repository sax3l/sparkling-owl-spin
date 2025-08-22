"""
Lovable Backend WebApp Entry Point (Standalone)

Standalone entry point för bara WebApp-delen utan crawler-beroendet.
"""

import uvicorn
from src.webapp.app import create_app
from src.settings import get_settings


def main():
    """Starta bara WebApp-servern."""
    settings = get_settings()
    app = create_app()
    
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
        reload=settings.debug,
        access_log=True
    )


if __name__ == "__main__":
    main()
