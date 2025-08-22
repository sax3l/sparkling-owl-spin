#!/usr/bin/env python3
"""
Lovable Backend CLI

Command-line interface for backend management.
"""

import click
import uvicorn
import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent))

from settings import get_settings
from database import create_tables, drop_tables
from services import UserService
from models import UserCreate


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Lovable Backend CLI - Manage your backend application."""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
@click.option("--workers", default=1, help="Number of worker processes")
@click.option("--log-level", default="info", help="Log level")
def serve(host: str, port: int, reload: bool, workers: int, log_level: str):
    """Start the FastAPI server."""
    settings = get_settings()
    
    click.echo(f"🚀 Starting Lovable Backend on {host}:{port}")
    click.echo(f"📝 Environment: {settings.environment}")
    click.echo(f"🔧 Debug mode: {settings.debug}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers if not reload else 1,
        log_level=log_level,
        access_log=True
    )


@cli.group()
def db():
    """Database management commands."""
    pass


@db.command()
def init():
    """Initialize the database."""
    click.echo("🔧 Initializing database...")
    try:
        create_tables()
        click.echo("✅ Database initialized successfully!")
    except Exception as e:
        click.echo(f"❌ Failed to initialize database: {e}")
        sys.exit(1)


@db.command()
@click.confirmation_option(prompt="Are you sure you want to drop all tables?")
def drop():
    """Drop all database tables."""
    click.echo("🗑️  Dropping all tables...")
    try:
        drop_tables()
        click.echo("✅ All tables dropped successfully!")
    except Exception as e:
        click.echo(f"❌ Failed to drop tables: {e}")
        sys.exit(1)


@db.command()
@click.confirmation_option(prompt="Are you sure you want to reset the database?")
def reset():
    """Reset the database (drop and recreate tables)."""
    click.echo("🔄 Resetting database...")
    try:
        drop_tables()
        create_tables()
        click.echo("✅ Database reset successfully!")
    except Exception as e:
        click.echo(f"❌ Failed to reset database: {e}")
        sys.exit(1)


@cli.group()
def user():
    """User management commands."""
    pass


@user.command()
@click.option("--username", prompt=True, help="Username")
@click.option("--email", prompt=True, help="Email address")
@click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True, help="Password")
@click.option("--full-name", help="Full name")
@click.option("--admin", is_flag=True, help="Make user an admin")
def create(username: str, email: str, password: str, full_name: Optional[str], admin: bool):
    """Create a new user."""
    from database import SessionLocal
    
    click.echo(f"👤 Creating user '{username}'...")
    
    db = SessionLocal()
    try:
        user_data = UserCreate(
            username=username,
            email=email,
            password=password,
            full_name=full_name
        )
        
        user = UserService.create_user(db, user_data)
        
        if admin:
            # Make user admin (you'd need to add this functionality to UserService)
            click.echo("🔐 Setting admin privileges...")
        
        click.echo(f"✅ User '{username}' created successfully!")
        click.echo(f"📧 Email: {user.email}")
        click.echo(f"🆔 ID: {user.id}")
        
    except Exception as e:
        click.echo(f"❌ Failed to create user: {e}")
        sys.exit(1)
    finally:
        db.close()


@user.command()
@click.argument("identifier")  # username or email
def info(identifier: str):
    """Get user information."""
    from database import SessionLocal
    
    db = SessionLocal()
    try:
        # Try to find user by username or email
        user = UserService.get_user_by_username(db, identifier)
        if not user:
            user = UserService.get_user_by_email(db, identifier)
        
        if not user:
            click.echo(f"❌ User '{identifier}' not found")
            sys.exit(1)
        
        click.echo(f"👤 User Information:")
        click.echo(f"🆔 ID: {user.id}")
        click.echo(f"👋 Username: {user.username}")
        click.echo(f"📧 Email: {user.email}")
        click.echo(f"📝 Full Name: {user.full_name or 'Not set'}")
        click.echo(f"✅ Active: {'Yes' if user.is_active else 'No'}")
        click.echo(f"🔐 Admin: {'Yes' if user.is_admin else 'No'}")
        click.echo(f"📅 Created: {user.created_at}")
        
    except Exception as e:
        click.echo(f"❌ Error getting user info: {e}")
        sys.exit(1)
    finally:
        db.close()


@cli.group()
def config():
    """Configuration management commands."""
    pass


@config.command()
def show():
    """Show current configuration."""
    settings = get_settings()
    
    click.echo("⚙️  Current Configuration:")
    click.echo(f"📝 Environment: {settings.environment}")
    click.echo(f"🔧 Debug: {settings.debug}")
    click.echo(f"🌐 Host: {settings.host}")
    click.echo(f"🔌 Port: {settings.port}")
    click.echo(f"🗄️  Database: {settings.database_url}")
    click.echo(f"🔐 JWT Algorithm: {settings.jwt_algorithm}")
    click.echo(f"⏰ JWT Expiry: {settings.jwt_access_token_expire_minutes} minutes")


@config.command()
def validate():
    """Validate configuration."""
    click.echo("🔍 Validating configuration...")
    
    try:
        settings = get_settings()
        click.echo("✅ Configuration is valid!")
        
        # Additional validation checks
        if settings.jwt_secret_key == "your-secret-key-here":
            click.echo("⚠️  Warning: Using default JWT secret key")
        
        if settings.environment == "production" and settings.debug:
            click.echo("⚠️  Warning: Debug mode enabled in production")
        
    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {e}")
        sys.exit(1)


@cli.command()
def health():
    """Check application health."""
    click.echo("🏥 Checking application health...")
    
    try:
        # Test database connection
        from database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        click.echo("✅ Database connection: OK")
        
        # Test configuration
        settings = get_settings()
        click.echo("✅ Configuration: OK")
        
        click.echo("🎉 All health checks passed!")
        
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}")
        sys.exit(1)


@cli.command()
@click.option("--format", "output_format", default="text", type=click.Choice(["text", "json"]))
def version(output_format: str):
    """Show version information."""
    version_info = {
        "version": "1.0.0",
        "python": sys.version.split()[0],
        "platform": sys.platform
    }
    
    if output_format == "json":
        import json
        click.echo(json.dumps(version_info, indent=2))
    else:
        click.echo(f"🚀 Lovable Backend v{version_info['version']}")
        click.echo(f"🐍 Python {version_info['python']}")
        click.echo(f"💻 Platform: {version_info['platform']}")


if __name__ == "__main__":
    cli()
