#!/usr/bin/env python3
"""
⚙️ REVOLUTIONARY ULTIMATE SYSTEM CONFIGURATION ⚙️
==================================================

Centraliserad konfiguration för hela det revolutionära systemet:
- Anti-bot defense policies
- Content extraction pipelines  
- URL discovery strategies
- Proxy & network configuration
- CAPTCHA solving services
- Quality control & monitoring

🎯 YAML-BASED CONFIGURATION SYSTEM:
- Per-domain policies (engine selection, retry logic)
- Fallback strategies (requests → cloudscraper → headless)
- Quality thresholds & content validation
- Rate limiting & performance tuning
"""

import yaml
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path
import os
import logging

logger = logging.getLogger(__name__)


@dataclass
class DomainPolicy:
    """Per-domain crawling policy"""
    # Anti-bot strategy
    engine: str = "requests"                    # requests|cloudscraper|playwright|undetected_chrome
    flare_solverr: bool = False                # Use FlareSolverr for Cloudflare
    captcha: str = "none"                      # none|2captcha|nopecha|auto
    tls_fingerprint: str = "default"           # default|azuretls|cycle
    
    # Content extraction
    extract_html: str = "trafilatura"          # trafilatura|beautifulsoup|tika
    extract_pdf: str = "tika"                  # tika|pdf-extract-kit|pymupdf
    extract_entities: bool = True               # Extract dates, amounts, etc
    
    # URL discovery
    seed_mode: str = "sitemap"                 # katana|photon|sitemap|manual
    max_depth: int = 3                         # Crawling depth
    follow_links: bool = True                  # Follow discovered links
    
    # Quality control
    min_quality: float = 0.3                   # Minimum content quality score
    max_retries: int = 3                       # Maximum retry attempts
    retry_delay: float = 2.0                   # Base retry delay
    
    # Performance
    rate_limit: float = 1.0                    # Requests per second
    timeout: int = 30                          # Request timeout
    concurrent: int = 5                        # Concurrent requests
    
    # Headers & fingerprinting
    user_agent: str = "auto"                   # auto|random|specific
    custom_headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)


@dataclass
class GlobalConfig:
    """Global system configuration"""
    
    # System identification
    name: str = "Revolutionary Ultimate Scraping System"
    version: str = "4.0"
    
    # Default policies
    default_policy: DomainPolicy = field(default_factory=DomainPolicy)
    
    # Domain-specific policies
    domains: Dict[str, DomainPolicy] = field(default_factory=dict)
    
    # Anti-bot services
    flaresolverr_url: str = "http://localhost:8191/v1"
    twocaptcha_api_key: Optional[str] = None
    nopecha_api_key: Optional[str] = None
    
    # Content extraction services
    tika_server_url: str = "http://localhost:9998"
    
    # Database & storage
    database_url: str = "postgresql://localhost/revolutionary_scraper"
    redis_url: str = "redis://localhost:6379/0"
    
    # Monitoring & logging
    log_level: str = "INFO"
    metrics_enabled: bool = True
    sentry_dsn: Optional[str] = None
    
    # Performance tuning
    global_rate_limit: float = 10.0            # Global requests per second
    max_concurrent_domains: int = 10           # Max domains to scrape simultaneously
    memory_limit_mb: int = 2048               # Memory usage limit
    
    # Quality control
    content_deduplication: bool = True         # Enable content deduplication
    similarity_threshold: float = 0.85         # Duplicate detection threshold
    
    # Feature flags
    features: Dict[str, bool] = field(default_factory=lambda: {
        'ai_extraction': True,
        'entity_recognition': True,
        'proxy_rotation': True,
        'behavioral_simulation': True,
        'content_quality_scoring': True,
        'automatic_retries': True,
        'cloudflare_bypass': True,
        'captcha_solving': True
    })


class ConfigurationManager:
    """Manages system configuration loading and validation"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = Path(config_path) if config_path else Path("crawl-policies.yml")
        self.config: Optional[GlobalConfig] = None
        
    def load_config(self) -> GlobalConfig:
        """Load configuration from YAML file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                # Parse global config
                global_data = data.get('global', {})
                config = GlobalConfig(**global_data)
                
                # Parse domain policies
                domains_data = data.get('domains', {})
                for domain, policy_data in domains_data.items():
                    policy = DomainPolicy(**policy_data)
                    config.domains[domain] = policy
                
                self.config = config
                logger.info(f"✅ Configuration loaded from {self.config_path}")
                
            except Exception as e:
                logger.error(f"❌ Failed to load configuration: {e}")
                self.config = GlobalConfig()  # Use defaults
        else:
            logger.warning(f"⚠️  Configuration file not found: {self.config_path}")
            self.config = GlobalConfig()  # Use defaults
        
        # Load environment variables
        self._load_environment_overrides()
        
        return self.config
    
    def _load_environment_overrides(self):
        """Load configuration overrides from environment variables"""
        if not self.config:
            return
        
        # API keys
        if os.getenv('TWOCAPTCHA_API_KEY'):
            self.config.twocaptcha_api_key = os.getenv('TWOCAPTCHA_API_KEY')
        
        if os.getenv('NOPECHA_API_KEY'):
            self.config.nopecha_api_key = os.getenv('NOPECHA_API_KEY')
        
        # Service URLs
        if os.getenv('FLARESOLVERR_URL'):
            self.config.flaresolverr_url = os.getenv('FLARESOLVERR_URL')
        
        if os.getenv('TIKA_SERVER_URL'):
            self.config.tika_server_url = os.getenv('TIKA_SERVER_URL')
        
        # Database
        if os.getenv('DATABASE_URL'):
            self.config.database_url = os.getenv('DATABASE_URL')
        
        if os.getenv('REDIS_URL'):
            self.config.redis_url = os.getenv('REDIS_URL')
        
        # Monitoring
        if os.getenv('SENTRY_DSN'):
            self.config.sentry_dsn = os.getenv('SENTRY_DSN')
        
        if os.getenv('LOG_LEVEL'):
            self.config.log_level = os.getenv('LOG_LEVEL')
    
    def save_config(self) -> bool:
        """Save current configuration to YAML file"""
        if not self.config:
            return False
        
        try:
            # Convert to dict
            config_dict = {
                'global': {
                    'name': self.config.name,
                    'version': self.config.version,
                    'flaresolverr_url': self.config.flaresolverr_url,
                    'tika_server_url': self.config.tika_server_url,
                    'database_url': self.config.database_url,
                    'redis_url': self.config.redis_url,
                    'log_level': self.config.log_level,
                    'metrics_enabled': self.config.metrics_enabled,
                    'global_rate_limit': self.config.global_rate_limit,
                    'max_concurrent_domains': self.config.max_concurrent_domains,
                    'memory_limit_mb': self.config.memory_limit_mb,
                    'content_deduplication': self.config.content_deduplication,
                    'similarity_threshold': self.config.similarity_threshold,
                    'features': self.config.features
                },
                'default_policy': asdict(self.config.default_policy),
                'domains': {
                    domain: asdict(policy) 
                    for domain, policy in self.config.domains.items()
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            logger.info(f"✅ Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def get_domain_policy(self, domain: str) -> DomainPolicy:
        """Get policy for specific domain"""
        if not self.config:
            self.load_config()
        
        # Check for exact domain match
        if domain in self.config.domains:
            return self.config.domains[domain]
        
        # Check for wildcard matches
        for pattern, policy in self.config.domains.items():
            if pattern.startswith('*.'):
                base_domain = pattern[2:]
                if domain.endswith(base_domain):
                    return policy
        
        # Return default policy
        return self.config.default_policy
    
    def add_domain_policy(self, domain: str, policy: DomainPolicy):
        """Add or update domain policy"""
        if not self.config:
            self.load_config()
        
        self.config.domains[domain] = policy
        logger.info(f"✅ Updated policy for domain: {domain}")
    
    def create_example_config(self) -> bool:
        """Create example configuration file"""
        example_config = {
            'global': {
                'name': 'Revolutionary Ultimate Scraping System',
                'version': '4.0',
                'flaresolverr_url': 'http://localhost:8191/v1',
                'tika_server_url': 'http://localhost:9998',
                'database_url': 'postgresql://localhost/revolutionary_scraper',
                'redis_url': 'redis://localhost:6379/0',
                'log_level': 'INFO',
                'metrics_enabled': True,
                'global_rate_limit': 10.0,
                'max_concurrent_domains': 10,
                'memory_limit_mb': 2048,
                'content_deduplication': True,
                'similarity_threshold': 0.85,
                'features': {
                    'ai_extraction': True,
                    'entity_recognition': True,
                    'proxy_rotation': True,
                    'behavioral_simulation': True,
                    'content_quality_scoring': True,
                    'automatic_retries': True,
                    'cloudflare_bypass': True,
                    'captcha_solving': True
                }
            },
            'default_policy': {
                'engine': 'requests',
                'flare_solverr': False,
                'captcha': 'none',
                'tls_fingerprint': 'default',
                'extract_html': 'trafilatura',
                'extract_pdf': 'tika',
                'extract_entities': True,
                'seed_mode': 'sitemap',
                'max_depth': 3,
                'follow_links': True,
                'min_quality': 0.3,
                'max_retries': 3,
                'retry_delay': 2.0,
                'rate_limit': 1.0,
                'timeout': 30,
                'concurrent': 5,
                'user_agent': 'auto',
                'custom_headers': {},
                'cookies': {}
            },
            'domains': {
                'example.se': {
                    'engine': 'cloudscraper',
                    'captcha': '2captcha',
                    'extract_html': 'trafilatura',
                    'rate_limit': 0.5,
                    'max_retries': 5,
                    'min_quality': 0.5
                },
                'cloudflare-protected.com': {
                    'engine': 'undetected_chrome',
                    'flare_solverr': True,
                    'captcha': '2captcha',
                    'tls_fingerprint': 'azuretls',
                    'rate_limit': 0.2,
                    'timeout': 60,
                    'max_retries': 5
                },
                '*.news.com': {
                    'engine': 'playwright',
                    'extract_html': 'trafilatura',
                    'extract_entities': True,
                    'seed_mode': 'katana',
                    'max_depth': 5,
                    'rate_limit': 2.0
                }
            }
        }
        
        try:
            config_path = Path("crawl-policies.yml")
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(example_config, f, default_flow_style=False, indent=2)
            
            logger.info(f"✅ Example configuration created: {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create example config: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigurationManager()


def get_config() -> GlobalConfig:
    """Get global configuration"""
    return config_manager.load_config()


def get_domain_policy(domain: str) -> DomainPolicy:
    """Get policy for specific domain"""
    return config_manager.get_domain_policy(domain)


def setup_logging(config: GlobalConfig):
    """Setup logging based on configuration"""
    import structlog
    
    # Configure logging level
    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# CLI interface for configuration management
import click

@click.group()
def cli():
    """Revolutionary Scraper Configuration Management"""
    pass


@cli.command()
def create_example():
    """Create example configuration file"""
    manager = ConfigurationManager()
    if manager.create_example_config():
        click.echo("✅ Example configuration created: crawl-policies.yml")
    else:
        click.echo("❌ Failed to create example configuration")


@cli.command()
@click.argument('domain')
@click.option('--engine', default='requests', help='Scraping engine')
@click.option('--captcha', default='none', help='CAPTCHA solver')
@click.option('--rate-limit', default=1.0, help='Rate limit')
def add_domain(domain, engine, captcha, rate_limit):
    """Add domain policy"""
    manager = ConfigurationManager()
    config = manager.load_config()
    
    policy = DomainPolicy(
        engine=engine,
        captcha=captcha,
        rate_limit=float(rate_limit)
    )
    
    manager.add_domain_policy(domain, policy)
    if manager.save_config():
        click.echo(f"✅ Added policy for domain: {domain}")
    else:
        click.echo("❌ Failed to save configuration")


@cli.command()
def show_config():
    """Show current configuration"""
    manager = ConfigurationManager()
    config = manager.load_config()
    
    click.echo(f"\n🚀 {config.name} v{config.version}")
    click.echo(f"📊 Default engine: {config.default_policy.engine}")
    click.echo(f"🔥 FlareSolverr: {config.flaresolverr_url}")
    click.echo(f"📄 Tika server: {config.tika_server_url}")
    click.echo(f"💾 Database: {config.database_url}")
    click.echo(f"\n🌐 Configured domains: {len(config.domains)}")
    
    for domain, policy in config.domains.items():
        click.echo(f"  • {domain}: {policy.engine} (rate: {policy.rate_limit}/s)")


if __name__ == "__main__":
    cli()
