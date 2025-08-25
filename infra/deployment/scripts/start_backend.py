#!/usr/bin/env python3
"""
Development server starter for the Main Crawler Project.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def start_backend():
    """Start the FastAPI backend server."""
    try:
        import uvicorn
        from src.webapp.main import create_app
        
        print("🚀 Starting Main Crawler Backend...")
        print("📡 Backend will be available at: http://localhost:8000")
        print("📋 API Documentation: http://localhost:8000/docs")
        print("🔍 GraphQL Playground: http://localhost:8000/graphql")
        print("⚡ Frontend (if running): http://localhost:8080")
        print("-" * 50)
        
        app = create_app()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["src"],
            log_level="info"
        )
        
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_backend()
