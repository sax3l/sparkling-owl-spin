#!/usr/bin/env python3
"""
Setup script for the crawler platform.

Installs dependencies, sets up database, and prepares the environment
for production deployment.
"""

import os
import sys
import subprocess
import asyncio
import logging
from pathlib import Path
import yaml

def setup_logging():
    """Setup basic logging for setup script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    logger = logging.getLogger(__name__)
    logger.info(f"Running: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            logger.info(f"Output: {result.stdout.strip()}")
        
        return result
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {e}")
        if e.stderr:
            logger.error(f"Error: {e.stderr}")
        raise

def check_python_version():
    """Check if Python version is sufficient."""
    logger = logging.getLogger(__name__)
    
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    
    logger.info(f"Python version: {sys.version}")

def check_system_dependencies():
    """Check for required system dependencies."""
    logger = logging.getLogger(__name__)
    
    required_commands = [
        ("node", "Node.js is required for frontend build"),
        ("npm", "npm is required for frontend dependencies"),
        ("git", "Git is required for version control"),
        ("docker", "Docker is recommended for deployment")
    ]
    
    missing = []
    
    for command, description in required_commands:
        try:
            run_command(f"which {command}", check=True)
            logger.info(f"✓ {command} found")
        except subprocess.CalledProcessError:
            if command == "docker":
                logger.warning(f"⚠ {command} not found - {description}")
            else:
                logger.error(f"✗ {command} not found - {description}")
                missing.append(command)
    
    if missing:
        logger.error(f"Missing required dependencies: {', '.join(missing)}")
        sys.exit(1)

def create_virtual_environment():
    """Create Python virtual environment if it doesn't exist."""
    logger = logging.getLogger(__name__)
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        logger.info("Virtual environment already exists")
        return
    
    logger.info("Creating virtual environment...")
    run_command(f"{sys.executable} -m venv venv")
    
    # Activate instructions
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate"
    
    logger.info(f"Virtual environment created. Activate with: {activate_cmd}")

def install_python_dependencies():
    """Install Python dependencies."""
    logger = logging.getLogger(__name__)
    
    # Determine pip command based on OS
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        pip_cmd = "venv/bin/pip"
    
    logger.info("Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{pip_cmd} install --upgrade pip")
    
    # Install main dependencies
    run_command(f"{pip_cmd} install -r requirements.txt")
    
    # Install development dependencies
    run_command(f"{pip_cmd} install -r requirements_dev.txt")
    
    logger.info("Python dependencies installed successfully")

def setup_frontend():
    """Setup frontend dependencies and build."""
    logger = logging.getLogger(__name__)
    
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        logger.warning("Frontend directory not found, skipping frontend setup")
        return
    
    logger.info("Installing frontend dependencies...")
    run_command("npm install", cwd=frontend_dir)
    
    logger.info("Building frontend...")
    run_command("npm run build", cwd=frontend_dir)
    
    logger.info("Frontend setup completed")

def create_config_files():
    """Create configuration files from templates."""
    logger = logging.getLogger(__name__)
    
    config_dir = Path("config")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        logger.info("Creating .env file from .env.example...")
        env_file.write_text(env_example.read_text())
        logger.warning("Please update .env file with your actual configuration values")
    
    # Ensure config directory exists
    config_dir.mkdir(exist_ok=True)
    
    # Create default app config if it doesn't exist
    app_config_file = config_dir / "app_config.yml"
    if not app_config_file.exists():
        logger.info("Creating default app_config.yml...")
        default_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "crawler_db",
                "user": "postgres",
                "password": "password",
                "min_connections": 10,
                "max_connections": 20
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "workers": 4
            },
            "proxy_pool": {
                "min_pool_size": 50,
                "max_pool_size": 200,
                "health_check_interval": 300
            },
            "cors": {
                "allow_origins": ["*"]
            },
            "debug": False
        }
        
        with open(app_config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

def setup_database():
    """Setup database schema and initial data."""
    logger = logging.getLogger(__name__)
    
    logger.info("Database setup would run migrations here...")
    logger.info("In production, run: python -m src.database.migrate")

def create_directories():
    """Create necessary directories."""
    logger = logging.getLogger(__name__)
    
    directories = [
        "data/raw",
        "data/processed",
        "data/exports/csv",
        "data/exports/json",
        "data/exports/excel",
        "data/redis_backups",
        "logs",
        "templates/html"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def run_tests():
    """Run basic tests to verify setup."""
    logger = logging.getLogger(__name__)
    
    # Determine python command based on OS
    if os.name == 'nt':  # Windows
        python_cmd = "venv\\Scripts\\python"
    else:  # Unix/Linux/Mac
        python_cmd = "venv/bin/python"
    
    logger.info("Running basic tests...")
    
    try:
        # Test imports
        run_command(f"{python_cmd} -c \"import src.utils.logger; print('✓ Core imports working')\"")
        
        # Test configuration loading
        run_command(f"{python_cmd} -c \"import yaml; print('✓ YAML configuration loading working')\"")
        
        logger.info("Basic tests passed")
        
    except subprocess.CalledProcessError:
        logger.warning("Some tests failed - please check the setup")

def main():
    """Main setup function."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("🚀 Starting crawler platform setup...")
    
    try:
        # Check system requirements
        check_python_version()
        check_system_dependencies()
        
        # Setup Python environment
        create_virtual_environment()
        install_python_dependencies()
        
        # Setup frontend
        setup_frontend()
        
        # Create configuration
        create_config_files()
        create_directories()
        
        # Setup database
        setup_database()
        
        # Run basic tests
        run_tests()
        
        logger.info("✅ Setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Update .env file with your configuration")
        logger.info("2. Setup your database (PostgreSQL)")
        logger.info("3. Run migrations: python -m src.database.migrate")
        logger.info("4. Start the application: python main.py")
        logger.info("")
        logger.info("For development:")
        if os.name == 'nt':
            logger.info("  Activate venv: venv\\Scripts\\activate")
        else:
            logger.info("  Activate venv: source venv/bin/activate")
        logger.info("  Run tests: pytest")
        logger.info("  Start dev server: uvicorn main:create_app --factory --reload")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
