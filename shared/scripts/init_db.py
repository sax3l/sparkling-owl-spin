#!/usr/bin/env python3
"""
Database initialization script for ECaDP Platform
Creates database, tables, and initial data
"""

import os
import sys
import yaml
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.database.models import Base

def load_config():
    """Load configuration from YAML files"""
    load_dotenv()
    
    # Load main config
    with open(os.path.join(project_root, "config", "app_config.yml"), "r") as f:
        config = yaml.safe_load(f)
    
    # Load environment-specific config
    env = os.getenv("ENVIRONMENT", "development")
    env_config_path = os.path.join(project_root, "config", "env", f"{env}.yml")
    
    if os.path.exists(env_config_path):
        with open(env_config_path, "r") as f:
            env_config = yaml.safe_load(f)
            # Merge configs (env config overrides main config)
            config.update(env_config)
    
    return config

def get_database_url(config: dict, admin: bool = False) -> str:
    """Get database URL from config"""
    db_config = config.get("database", {}).get("mysql", {})
    
    host = os.getenv("MYSQL_HOST", db_config.get("host", "localhost"))
    port = os.getenv("MYSQL_PORT", db_config.get("port", 3306))
    database = os.getenv("MYSQL_DATABASE", db_config.get("database", "ecadp"))
    
    if admin:
        # Use root user to create database
        username = "root"
        password = os.getenv("MYSQL_ROOT_PASSWORD")
        database = ""  # Connect without specific database
    else:
        username = os.getenv("MYSQL_USER", db_config.get("username", "ecadp_user"))
        password = os.getenv("MYSQL_PASSWORD")
    
    if not password:
        raise ValueError(f"Password not set for {'root' if admin else 'user'}")
    
    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8mb4"

def create_database(config: dict):
    """Create the database if it doesn't exist"""
    print("🗄️  Creating database...")
    
    try:
        # Connect as root to create database
        admin_url = get_database_url(config, admin=True)
        admin_engine = create_engine(admin_url)
        
        database_name = os.getenv("MYSQL_DATABASE", "ecadp")
        
        with admin_engine.connect() as conn:
            # Create database
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database_name} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            print(f"✅ Database '{database_name}' created successfully")
            
            # Create user if not exists
            username = os.getenv("MYSQL_USER", "ecadp_user")
            password = os.getenv("MYSQL_PASSWORD")
            
            conn.execute(text(f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{password}'"))
            conn.execute(text(f"GRANT ALL PRIVILEGES ON {database_name}.* TO '{username}'@'%'"))
            conn.execute(text("FLUSH PRIVILEGES"))
            print(f"✅ User '{username}' created and granted privileges")
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False
    
    return True

def test_connection(config: dict):
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        database_url = get_database_url(config)
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test")).fetchone()
            if result and result[0] == 1:
                print("✅ Database connection successful")
                return True
            else:
                print("❌ Database connection test failed")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def main():
    """Main initialization function"""
    print("🚀 Initializing ECaDP Platform Database")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded")
        
        # Create database
        if not create_database(config):
            sys.exit(1)
        
        # Test connection
        if not test_connection(config):
            sys.exit(1)
        
        print("\n🎉 Database initialization completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start the web application: python -m uvicorn src.webapp.app:app --reload")
        print("3. Access the frontend: http://localhost:3000")
        print("4. Access the API documentation: http://localhost:8000/docs")
        
    except Exception as e:
        print(f"💥 Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()