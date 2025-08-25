#!/usr/bin/env python3
"""
GitHub Integration Configuration - Revolutionary Ultimate System v4.0
Centralized configuration for all GitHub-based integrations
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContentExtractionConfig:
    """Configuration for content extraction integrations"""
    # Apache Tika
    apache_tika_enabled: bool = True
    apache_tika_server_url: str = "http://localhost:9998"
    apache_tika_java_path: Optional[str] = None
    apache_tika_memory: str = "1g"
    apache_tika_timeout: int = 60
    apache_tika_ocr_enabled: bool = True
    
    # Trafilatura
    trafilatura_enabled: bool = True
    trafilatura_fallback_candidates: bool = True
    trafilatura_include_comments: bool = False
    trafilatura_include_tables: bool = True
    trafilatura_include_images: bool = False
    trafilatura_deduplicate: bool = True
    
    # PDF-Extract-Kit
    pdf_extract_kit_enabled: bool = True
    pdf_extract_kit_layout_analysis: bool = True
    pdf_extract_kit_table_extraction: bool = True
    pdf_extract_kit_figure_extraction: bool = True
    pdf_extract_kit_formula_recognition: bool = True
    pdf_extract_kit_reading_order: bool = True

@dataclass
class ProxyManagementConfig:
    """Configuration for proxy management integrations"""
    # ProxyBroker
    proxy_broker_enabled: bool = True
    proxy_broker_max_proxies: int = 100
    proxy_broker_timeout: int = 30
    proxy_broker_countries: list = None
    proxy_broker_protocols: list = None
    proxy_broker_anonymity: str = "high"
    
    # Proxy Pool
    proxy_pool_enabled: bool = True
    proxy_pool_redis_url: Optional[str] = None
    proxy_pool_check_interval: int = 300
    proxy_pool_max_pool_size: int = 1000
    proxy_pool_min_pool_size: int = 50
    
    # Requests IP Rotator
    requests_ip_rotator_enabled: bool = True
    requests_ip_rotator_aws_access_key: Optional[str] = None
    requests_ip_rotator_aws_secret_key: Optional[str] = None
    requests_ip_rotator_regions: list = None

@dataclass
class URLDiscoveryConfig:
    """Configuration for URL discovery integrations"""
    # Katana
    katana_enabled: bool = True
    katana_binary_path: Optional[str] = None
    katana_auto_install: bool = False
    katana_max_depth: int = 3
    katana_max_urls: int = 1000
    katana_concurrency: int = 10
    katana_timeout: int = 30
    
    # Photon
    photon_enabled: bool = True
    photon_max_depth: int = 2
    photon_max_urls: int = 500
    photon_threads: int = 10
    photon_timeout: int = 30
    photon_extract_data: bool = True
    
    # Colly
    colly_enabled: bool = True
    colly_go_binary: Optional[str] = None
    colly_auto_compile: bool = False
    colly_server_port: int = 8080
    colly_concurrent_requests: int = 5
    colly_delay: float = 1.0

@dataclass
class AntiBotDefenseConfig:
    """Configuration for anti-bot defense integrations"""
    # FlareSolverr
    flaresolverr_enabled: bool = True
    flaresolverr_server_url: str = "http://localhost:8191"
    flaresolverr_auto_start: bool = False
    flaresolverr_timeout: int = 60
    flaresolverr_max_timeout: int = 120
    
    # Undetected Chrome
    undetected_chrome_enabled: bool = True
    undetected_chrome_headless: bool = True
    undetected_chrome_no_sandbox: bool = True
    undetected_chrome_user_data_dir: Optional[str] = None
    undetected_chrome_proxy: Optional[str] = None
    
    # CloudScraper
    cloudscraper_enabled: bool = True
    cloudscraper_browser: str = "chrome"
    cloudscraper_captcha_solver: Optional[str] = None
    cloudscraper_delay: float = 1.0
    
    # CloudFlare-Scrape
    cloudflare_scrape_enabled: bool = True
    cloudflare_scrape_delay: float = 1.0
    cloudflare_scrape_timeout: int = 30

@dataclass
class BrowserAutomationConfig:
    """Configuration for browser automation integrations"""
    # Playwright
    playwright_enabled: bool = True
    playwright_browser: str = "chromium"
    playwright_headless: bool = True
    playwright_viewport_width: int = 1920
    playwright_viewport_height: int = 1080
    playwright_timeout: int = 30000
    playwright_user_agent: Optional[str] = None
    playwright_proxy: Optional[str] = None
    
    # DrissionPage
    drission_page_enabled: bool = True
    drission_page_headless: bool = True
    drission_page_window_width: int = 1920
    drission_page_window_height: int = 1080
    drission_page_timeout: int = 30
    drission_page_user_agent: Optional[str] = None

@dataclass
class CrawlingFrameworksConfig:
    """Configuration for crawling framework integrations"""
    # Crawlee
    crawlee_enabled: bool = True
    crawlee_server_port: int = 3000
    crawlee_node_binary: Optional[str] = None
    crawlee_npm_binary: Optional[str] = None
    crawlee_auto_start_server: bool = False
    crawlee_max_concurrent: int = 10
    crawlee_request_delay: float = 1.0
    crawlee_timeout: int = 30

@dataclass
class GitHubIntegrationsConfig:
    """Complete configuration for all GitHub integrations"""
    content_extraction: ContentExtractionConfig = None
    proxy_management: ProxyManagementConfig = None
    url_discovery: URLDiscoveryConfig = None
    anti_bot_defense: AntiBotDefenseConfig = None
    browser_automation: BrowserAutomationConfig = None
    crawling_frameworks: CrawlingFrameworksConfig = None
    
    def __post_init__(self):
        if self.content_extraction is None:
            self.content_extraction = ContentExtractionConfig()
        if self.proxy_management is None:
            self.proxy_management = ProxyManagementConfig()
        if self.url_discovery is None:
            self.url_discovery = URLDiscoveryConfig()
        if self.anti_bot_defense is None:
            self.anti_bot_defense = AntiBotDefenseConfig()
        if self.browser_automation is None:
            self.browser_automation = BrowserAutomationConfig()
        if self.crawling_frameworks is None:
            self.crawling_frameworks = CrawlingFrameworksConfig()

class GitHubIntegrationsConfigManager:
    """Manager for GitHub integrations configuration"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("github_integrations_config.yaml")
        self.config = GitHubIntegrationsConfig()
        
    def load_config(self) -> GitHubIntegrationsConfig:
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    if self.config_path.suffix.lower() == '.yaml' or self.config_path.suffix.lower() == '.yml':
                        data = yaml.safe_load(f)
                    else:
                        data = json.load(f)
                        
                # Convert nested dictionaries to dataclass instances
                content_extraction = ContentExtractionConfig(**data.get('content_extraction', {}))
                proxy_management = ProxyManagementConfig(**data.get('proxy_management', {}))
                url_discovery = URLDiscoveryConfig(**data.get('url_discovery', {}))
                anti_bot_defense = AntiBotDefenseConfig(**data.get('anti_bot_defense', {}))
                browser_automation = BrowserAutomationConfig(**data.get('browser_automation', {}))
                crawling_frameworks = CrawlingFrameworksConfig(**data.get('crawling_frameworks', {}))
                
                self.config = GitHubIntegrationsConfig(
                    content_extraction=content_extraction,
                    proxy_management=proxy_management,
                    url_discovery=url_discovery,
                    anti_bot_defense=anti_bot_defense,
                    browser_automation=browser_automation,
                    crawling_frameworks=crawling_frameworks
                )
                
                logger.info(f"✅ Configuration loaded from {self.config_path}")
            else:
                logger.info("⚙️ Using default configuration")
                self.save_config()  # Save default config for reference
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {str(e)}")
            logger.info("⚙️ Using default configuration")
            
        return self.config
        
    def save_config(self, config: Optional[GitHubIntegrationsConfig] = None) -> bool:
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            config_dict = asdict(config_to_save)
            
            with open(self.config_path, 'w') as f:
                if self.config_path.suffix.lower() == '.yaml' or self.config_path.suffix.lower() == '.yml':
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
                    
            logger.info(f"✅ Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save configuration: {str(e)}")
            return False
            
    def get_adapter_config(self, integration_name: str) -> Dict[str, Any]:
        """Get configuration for specific adapter"""
        config_mapping = {
            # Content Extraction
            'apache_tika': {
                'enabled': self.config.content_extraction.apache_tika_enabled,
                'server_url': self.config.content_extraction.apache_tika_server_url,
                'java_path': self.config.content_extraction.apache_tika_java_path,
                'memory_allocation': self.config.content_extraction.apache_tika_memory,
                'timeout': self.config.content_extraction.apache_tika_timeout,
                'ocr_enabled': self.config.content_extraction.apache_tika_ocr_enabled
            },
            'trafilatura': {
                'enabled': self.config.content_extraction.trafilatura_enabled,
                'fallback_candidates': self.config.content_extraction.trafilatura_fallback_candidates,
                'include_comments': self.config.content_extraction.trafilatura_include_comments,
                'include_tables': self.config.content_extraction.trafilatura_include_tables,
                'include_images': self.config.content_extraction.trafilatura_include_images,
                'deduplicate': self.config.content_extraction.trafilatura_deduplicate
            },
            'pdf_extract_kit': {
                'enabled': self.config.content_extraction.pdf_extract_kit_enabled,
                'layout_analysis': self.config.content_extraction.pdf_extract_kit_layout_analysis,
                'table_extraction': self.config.content_extraction.pdf_extract_kit_table_extraction,
                'figure_extraction': self.config.content_extraction.pdf_extract_kit_figure_extraction,
                'formula_recognition': self.config.content_extraction.pdf_extract_kit_formula_recognition,
                'reading_order': self.config.content_extraction.pdf_extract_kit_reading_order
            },
            
            # Proxy Management
            'proxy_broker': {
                'enabled': self.config.proxy_management.proxy_broker_enabled,
                'max_proxies': self.config.proxy_management.proxy_broker_max_proxies,
                'timeout': self.config.proxy_management.proxy_broker_timeout,
                'countries': self.config.proxy_management.proxy_broker_countries or ['US', 'GB', 'DE'],
                'protocols': self.config.proxy_management.proxy_broker_protocols or ['HTTP', 'HTTPS'],
                'anonymity': self.config.proxy_management.proxy_broker_anonymity
            },
            'proxy_pool': {
                'enabled': self.config.proxy_management.proxy_pool_enabled,
                'redis_url': self.config.proxy_management.proxy_pool_redis_url,
                'check_interval': self.config.proxy_management.proxy_pool_check_interval,
                'max_pool_size': self.config.proxy_management.proxy_pool_max_pool_size,
                'min_pool_size': self.config.proxy_management.proxy_pool_min_pool_size
            },
            'requests_ip_rotator': {
                'enabled': self.config.proxy_management.requests_ip_rotator_enabled,
                'aws_access_key': self.config.proxy_management.requests_ip_rotator_aws_access_key,
                'aws_secret_key': self.config.proxy_management.requests_ip_rotator_aws_secret_key,
                'regions': self.config.proxy_management.requests_ip_rotator_regions or ['us-east-1', 'us-west-2']
            },
            
            # URL Discovery
            'katana': {
                'enabled': self.config.url_discovery.katana_enabled,
                'binary_path': self.config.url_discovery.katana_binary_path,
                'auto_install': self.config.url_discovery.katana_auto_install,
                'max_depth': self.config.url_discovery.katana_max_depth,
                'max_urls': self.config.url_discovery.katana_max_urls,
                'concurrency': self.config.url_discovery.katana_concurrency,
                'timeout': self.config.url_discovery.katana_timeout
            },
            'photon': {
                'enabled': self.config.url_discovery.photon_enabled,
                'max_depth': self.config.url_discovery.photon_max_depth,
                'max_urls': self.config.url_discovery.photon_max_urls,
                'threads': self.config.url_discovery.photon_threads,
                'timeout': self.config.url_discovery.photon_timeout,
                'extract_data': self.config.url_discovery.photon_extract_data
            },
            'colly': {
                'enabled': self.config.url_discovery.colly_enabled,
                'go_binary': self.config.url_discovery.colly_go_binary,
                'auto_compile': self.config.url_discovery.colly_auto_compile,
                'server_port': self.config.url_discovery.colly_server_port,
                'concurrent_requests': self.config.url_discovery.colly_concurrent_requests,
                'delay': self.config.url_discovery.colly_delay
            },
            
            # Anti-bot Defense
            'flaresolverr': {
                'enabled': self.config.anti_bot_defense.flaresolverr_enabled,
                'server_url': self.config.anti_bot_defense.flaresolverr_server_url,
                'auto_start': self.config.anti_bot_defense.flaresolverr_auto_start,
                'timeout': self.config.anti_bot_defense.flaresolverr_timeout,
                'max_timeout': self.config.anti_bot_defense.flaresolverr_max_timeout
            },
            'undetected_chrome': {
                'enabled': self.config.anti_bot_defense.undetected_chrome_enabled,
                'headless': self.config.anti_bot_defense.undetected_chrome_headless,
                'no_sandbox': self.config.anti_bot_defense.undetected_chrome_no_sandbox,
                'user_data_dir': self.config.anti_bot_defense.undetected_chrome_user_data_dir,
                'proxy': self.config.anti_bot_defense.undetected_chrome_proxy
            },
            'cloudscraper': {
                'enabled': self.config.anti_bot_defense.cloudscraper_enabled,
                'browser': self.config.anti_bot_defense.cloudscraper_browser,
                'captcha_solver': self.config.anti_bot_defense.cloudscraper_captcha_solver,
                'delay': self.config.anti_bot_defense.cloudscraper_delay
            },
            'cloudflare_scrape': {
                'enabled': self.config.anti_bot_defense.cloudflare_scrape_enabled,
                'delay': self.config.anti_bot_defense.cloudflare_scrape_delay,
                'timeout': self.config.anti_bot_defense.cloudflare_scrape_timeout
            },
            
            # Browser Automation
            'playwright': {
                'enabled': self.config.browser_automation.playwright_enabled,
                'browser_type': self.config.browser_automation.playwright_browser,
                'headless': self.config.browser_automation.playwright_headless,
                'viewport': {
                    'width': self.config.browser_automation.playwright_viewport_width,
                    'height': self.config.browser_automation.playwright_viewport_height
                },
                'timeout': self.config.browser_automation.playwright_timeout,
                'user_agent': self.config.browser_automation.playwright_user_agent,
                'proxy': self.config.browser_automation.playwright_proxy
            },
            'drission_page': {
                'enabled': self.config.browser_automation.drission_page_enabled,
                'headless': self.config.browser_automation.drission_page_headless,
                'window_size': (
                    self.config.browser_automation.drission_page_window_width,
                    self.config.browser_automation.drission_page_window_height
                ),
                'page_load_timeout': self.config.browser_automation.drission_page_timeout,
                'user_agent': self.config.browser_automation.drission_page_user_agent
            },
            
            # Crawling Frameworks
            'crawlee': {
                'enabled': self.config.crawling_frameworks.crawlee_enabled,
                'server_port': self.config.crawling_frameworks.crawlee_server_port,
                'node_binary_path': self.config.crawling_frameworks.crawlee_node_binary,
                'npm_binary_path': self.config.crawling_frameworks.crawlee_npm_binary,
                'auto_start_server': self.config.crawling_frameworks.crawlee_auto_start_server,
                'max_concurrent_crawlers': self.config.crawling_frameworks.crawlee_max_concurrent,
                'default_delay': self.config.crawling_frameworks.crawlee_request_delay,
                'default_timeout': self.config.crawling_frameworks.crawlee_timeout
            }
        }
        
        return config_mapping.get(integration_name, {'enabled': False})
        
    def update_adapter_config(self, integration_name: str, updates: Dict[str, Any]) -> bool:
        """Update configuration for specific adapter"""
        try:
            # This is a simplified update - in practice, you'd want to map back to the dataclass fields
            logger.info(f"⚙️ Configuration update requested for {integration_name}")
            # Would implement reverse mapping here
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update configuration for {integration_name}: {str(e)}")
            return False

# Global configuration manager instance
config_manager = GitHubIntegrationsConfigManager()

# Convenience functions
def get_github_config() -> GitHubIntegrationsConfig:
    """Get the current GitHub integrations configuration"""
    return config_manager.load_config()

def get_adapter_config(integration_name: str) -> Dict[str, Any]:
    """Get configuration for specific adapter"""
    return config_manager.get_adapter_config(integration_name)

def save_github_config(config: GitHubIntegrationsConfig) -> bool:
    """Save GitHub integrations configuration"""
    return config_manager.save_config(config)

# Example usage and default configuration generation
def main():
    """Generate default configuration file"""
    config_manager = GitHubIntegrationsConfigManager(Path("example_github_integrations_config.yaml"))
    
    # Load or create default config
    config = config_manager.load_config()
    
    print("📋 GitHub Integrations Configuration Manager")
    print("=" * 60)
    
    print(f"Configuration file: {config_manager.config_path}")
    print(f"Content Extraction - Apache Tika: {'✅' if config.content_extraction.apache_tika_enabled else '❌'}")
    print(f"Proxy Management - ProxyBroker: {'✅' if config.proxy_management.proxy_broker_enabled else '❌'}")
    print(f"URL Discovery - Katana: {'✅' if config.url_discovery.katana_enabled else '❌'}")
    print(f"Anti-bot Defense - CloudScraper: {'✅' if config.anti_bot_defense.cloudscraper_enabled else '❌'}")
    print(f"Browser Automation - Playwright: {'✅' if config.browser_automation.playwright_enabled else '❌'}")
    print(f"Crawling Frameworks - Crawlee: {'✅' if config.crawling_frameworks.crawlee_enabled else '❌'}")
    
    print("\n✅ Configuration management ready!")

if __name__ == "__main__":
    main()
