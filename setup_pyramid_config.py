#!/usr/bin/env python3
"""
Pyramid Architecture Configuration Setup
Genererar konfigurationsfiler för alla lager i pyramid-arkitekturen
"""

import os
import yaml
import json
from pathlib import Path

def create_pyramid_config():
    """Create configuration för pyramid architecture"""
    
    base_path = Path(__file__).parent
    config_dir = base_path / "config"
    
    # Create config directories
    for env in ["development", "testing", "production"]:
        env_dir = config_dir / env
        env_dir.mkdir(parents=True, exist_ok=True)
        
        # Core configuration
        core_config = {
            "log_level": "INFO" if env == "production" else "DEBUG",
            "max_workers": 4 if env == "development" else 8,
            "timeout": 300,
            "debug": env == "development",
            "metrics_enabled": True,
            "environment": env
        }
        
        with open(env_dir / "core.yml", 'w') as f:
            yaml.dump(core_config, f, default_flow_style=False)
            
        # Security configuration
        security_config = {
            "authorized_domains": [
                "localhost",
                "127.0.0.1",
                "*.localhost"
            ] + (["*.test.example.com"] if env != "production" else []),
            "rate_limit": 100 if env == "development" else 1000,
            "security_level": "high" if env == "production" else "medium",
            "require_domain_authorization": True,
            "log_all_requests": True,
            "block_suspicious_requests": True,
            "pentest_session_timeout_hours": 24,
            "max_pentest_sessions": 5
        }
        
        with open(env_dir / "security.yml", 'w') as f:
            yaml.dump(security_config, f, default_flow_style=False)
            
        # API configuration
        api_config = {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ],
            "max_request_size": "10MB",
            "rate_limit": 1000,
            "enable_docs": env != "production",
            "api_version": "v1"
        }
        
        with open(env_dir / "api.yml", 'w') as f:
            yaml.dump(api_config, f, default_flow_style=False)
            
        # AI configuration
        ai_config = {
            "openai": {
                "api_key": "${OPENAI_API_KEY}",
                "model": "gpt-4",
                "max_tokens": 2000,
                "temperature": 0.7
            },
            "max_agents": 5,
            "default_model": "gpt-4",
            "crew_max_execution_time": 1800,
            "enable_memory": True,
            "verbose": env == "development"
        }
        
        with open(env_dir / "ai.yml", 'w') as f:
            yaml.dump(ai_config, f, default_flow_style=False)
            
        # Scraping configuration
        scraping_config = {
            "max_concurrent_requests": 10 if env == "development" else 20,
            "request_delay": 1.0,
            "max_retries": 3,
            "timeout": 30,
            "respect_robots_txt": True,
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            ],
            "engines": {
                "beautifulsoup": {"enabled": True},
                "scrapy": {"enabled": True, "concurrent_requests": 16},
                "playwright": {"enabled": True, "headless": env == "production"},
                "crawlee": {"enabled": False}
            }
        }
        
        with open(env_dir / "scraping.yml", 'w') as f:
            yaml.dump(scraping_config, f, default_flow_style=False)
            
        # Bypass configuration
        bypass_config = {
            "cloudflare": {
                "flaresolverr_url": "http://localhost:8191",
                "cloudscraper_enabled": True,
                "auto_retry": True,
                "max_retries": 3
            },
            "captcha": {
                "twocaptcha_api_key": "${TWOCAPTCHA_API_KEY}",
                "capmonster_api_key": "${CAPMONSTER_API_KEY}",
                "nopecha_api_key": "${NOPECHA_API_KEY}",
                "local_ocr_enabled": True,
                "default_service": "2captcha"
            },
            "browser": {
                "undetected_chrome": True,
                "headless": env == "production",
                "user_data_dir": "./browser_profiles",
                "max_instances": 3,
                "stealth_mode": True
            }
        }
        
        with open(env_dir / "bypass.yml", 'w') as f:
            yaml.dump(bypass_config, f, default_flow_style=False)
            
        # Data sources configuration
        data_sources_config = {
            "swedish": {
                "blocket_api_key": "${BLOCKET_API_KEY}",
                "bytbil_enabled": True,
                "max_results": 1000,
                "cache_ttl": 3600,
                "regions": ["all"],
                "categories": ["cars", "motorcycles", "boats"]
            }
        }
        
        with open(env_dir / "data_sources.yml", 'w') as f:
            yaml.dump(data_sources_config, f, default_flow_style=False)
            
        print(f"✅ Created configuration för {env} environment")
        
    # Create example environment file
    env_example = """# Sparkling-Owl-Spin Environment Variables

# Core system
SPARKLING_ENV=development
LOG_LEVEL=INFO

# External APIs
OPENAI_API_KEY=your_openai_api_key_here
TWOCAPTCHA_API_KEY=your_2captcha_api_key_here
CAPMONSTER_API_KEY=your_capmonster_api_key_here
NOPECHA_API_KEY=your_nopecha_api_key_here
BLOCKET_API_KEY=your_blocket_api_key_here

# Security
SECURITY_LEVEL=medium
REQUIRE_DOMAIN_AUTHORIZATION=true

# Database (if needed)
DATABASE_URL=sqlite:///sparkling_owl_spin.db

# Monitoring
METRICS_ENABLED=true
"""
    
    with open(base_path / ".env.example", 'w') as f:
        f.write(env_example)
        
    print("✅ Created .env.example file")
    print("\n🔧 Next steps:")
    print("1. Copy .env.example to .env and configure your API keys")
    print("2. Review configuration files in config/development/")
    print("3. Run: python main_pyramid.py")

if __name__ == "__main__":
    create_pyramid_config()
