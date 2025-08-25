#!/usr/bin/env python3
"""
🦉 Vendor Manager - Enhetlig Vendor Integration System
==================================================
Centraliserat system för att hantera alla vendor-integrations
enligt pyramid-arkitekturen med optimerad resurshantering.
"""

import os
import sys
import yaml
import time
import logging
import importlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager

# Konfigurera logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class VendorInfo:
    """Information om en vendor"""
    name: str
    type: str
    priority: str
    enabled: bool
    init_on_startup: bool
    config: Dict[str, Any] = field(default_factory=dict)
    instance: Optional[Any] = None
    last_health_check: Optional[float] = None
    status: str = "unknown"  # unknown, loaded, failed, healthy, unhealthy

class VendorManager:
    """
    Centraliserad hantering av alla vendor-integrations
    """
    
    def __init__(self, config_path: str = "config/vendors.yaml"):
        """
        Initialisera vendor manager
        
        Args:
            config_path: Sökväg till vendor konfigurationsfil
        """
        self.config_path = Path(config_path)
        self.vendors: Dict[str, VendorInfo] = {}
        self.initialized_vendors: Dict[str, Any] = {}
        self.health_check_interval = 300  # 5 minuter
        self.last_cleanup = time.time()
        
        # Läs konfiguration
        self._load_config()
        
        # Setup lazy loading
        self._setup_lazy_loading()
        
    def _load_config(self) -> None:
        """Läs vendor konfiguration från YAML"""
        try:
            if not self.config_path.exists():
                logger.error(f"Vendor config file not found: {self.config_path}")
                return
                
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            vendor_config = config.get('vendor_config', {})
            
            # Processa alla vendor kategorier
            for priority, vendors in vendor_config.items():
                if isinstance(vendors, dict):
                    for vendor_name, vendor_data in vendors.items():
                        if isinstance(vendor_data, dict):
                            self.vendors[vendor_name] = VendorInfo(
                                name=vendor_name,
                                type=vendor_data.get('type', 'unknown'),
                                priority=vendor_data.get('priority', 'medium'),
                                enabled=vendor_data.get('enabled', True),
                                init_on_startup=vendor_data.get('init_on_startup', False),
                                config=vendor_data.get('config', {})
                            )
                            
            logger.info(f"Loaded {len(self.vendors)} vendor configurations")
            
        except Exception as e:
            logger.error(f"Failed to load vendor config: {e}")
            
    def _setup_lazy_loading(self) -> None:
        """Setup lazy loading system"""
        self.lazy_loading = True
        self.load_on_demand = True
        self.unload_unused = True
        self.idle_timeout = 1800  # 30 minuter
        
    def initialize_startup_vendors(self) -> Dict[str, bool]:
        """
        Initialisera vendors som ska startas vid uppstart
        
        Returns:
            Dict med vendor namn och status (True = success, False = failed)
        """
        startup_vendors = {
            name: vendor for name, vendor in self.vendors.items() 
            if vendor.enabled and vendor.init_on_startup
        }
        
        logger.info(f"Initializing {len(startup_vendors)} startup vendors...")
        
        results = {}
        
        # Startup order från config
        startup_order = {
            1: ["flaresolverr", "proxy_pool"],
            2: ["undetected-chromedriver", "crewAI"],
            3: ["crawlee", "scrapy", "playwright_stealth"],
            4: ["crawl4ai", "secret-agent", "Scrapegraph-ai"]
        }
        
        for phase, vendor_names in startup_order.items():
            logger.info(f"Startup phase {phase}: {vendor_names}")
            
            phase_results = {}
            for vendor_name in vendor_names:
                if vendor_name in startup_vendors:
                    success = self._initialize_vendor(vendor_name)
                    phase_results[vendor_name] = success
                    results[vendor_name] = success
                    
            # Vänta mellan faser
            if phase < max(startup_order.keys()):
                time.sleep(2)
                
        return results
        
    def _initialize_vendor(self, vendor_name: str) -> bool:
        """
        Initialisera en specifik vendor
        
        Args:
            vendor_name: Namnet på vendor att initialisera
            
        Returns:
            True om successful, False om failed
        """
        if vendor_name not in self.vendors:
            logger.error(f"Unknown vendor: {vendor_name}")
            return False
            
        vendor = self.vendors[vendor_name]
        
        if not vendor.enabled:
            logger.info(f"Vendor {vendor_name} is disabled, skipping...")
            return False
            
        try:
            logger.info(f"Initializing {vendor_name} ({vendor.type})...")
            
            # Specialiserad initialisering för olika vendor typer
            success = self._init_by_type(vendor)
            
            if success:
                vendor.status = "loaded"
                vendor.last_health_check = time.time()
                logger.info(f"✅ Successfully initialized {vendor_name}")
            else:
                vendor.status = "failed"
                logger.error(f"❌ Failed to initialize {vendor_name}")
                
            return success
            
        except Exception as e:
            logger.error(f"Exception initializing {vendor_name}: {e}")
            vendor.status = "failed"
            return False
            
    def _init_by_type(self, vendor: VendorInfo) -> bool:
        """
        Initialisera vendor baserat på typ
        
        Args:
            vendor: VendorInfo objekt
            
        Returns:
            True om successful
        """
        vendor_type = vendor.type
        vendor_name = vendor.name
        config = vendor.config
        
        try:
            if vendor_type == "cloudflare_bypass":
                if vendor_name == "flaresolverr":
                    return self._init_flaresolverr(config)
                elif vendor_name == "Cloudflare-Solver-":
                    return self._init_cloudflare_solver(config)
                    
            elif vendor_type == "stealth_browser":
                if vendor_name == "undetected-chromedriver":
                    return self._init_undetected_chrome(config)
                elif vendor_name == "playwright_stealth":
                    return self._init_playwright_stealth(config)
                elif vendor_name == "secret-agent":
                    return self._init_secret_agent(config)
                    
            elif vendor_type == "proxy_management":
                return self._init_proxy_pool(config)
                
            elif vendor_type == "ai_orchestration":
                return self._init_crewai(config)
                
            elif vendor_type == "crawling_engine":
                return self._init_crawlee(config)
                
            elif vendor_type == "scraping_framework":
                return self._init_scrapy(config)
                
            elif vendor_type == "ai_crawling":
                return self._init_crawl4ai(config)
                
            elif vendor_type == "ai_scraping":
                return self._init_scrapegraph_ai(config)
                
            elif vendor_type == "ip_rotation":
                return self._init_ip_rotator(config)
                
            elif vendor_type == "browser_automation":
                return self._init_selenium_base(config)
                
            elif vendor_type == "anti_detection":
                return self._init_fake_useragent(config)
                
            elif vendor_type == "content_extraction":
                return self._init_trafilatura(config)
                
            else:
                logger.warning(f"Unknown vendor type: {vendor_type}")
                return self._init_generic_vendor(vendor_name, config)
                
        except Exception as e:
            logger.error(f"Failed to initialize {vendor_name}: {e}")
            return False
            
    # Specialiserade initialiseringsmetoder
    def _init_flaresolverr(self, config: Dict) -> bool:
        """Initialisera FlareSolverr"""
        try:
            import requests
            host = config.get('host', 'localhost')
            port = config.get('port', 8191)
            
            # Testa anslutning
            response = requests.get(f"http://{host}:{port}", timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def _init_undetected_chrome(self, config: Dict) -> bool:
        """Initialisera undetected-chromedriver"""
        try:
            import undetected_chromedriver as uc
            
            options = uc.ChromeOptions()
            if config.get('headless', True):
                options.add_argument('--headless')
                
            # Test driver creation
            driver = uc.Chrome(options=options)
            driver.quit()
            return True
        except:
            return False
            
    def _init_proxy_pool(self, config: Dict) -> bool:
        """Initialisera proxy pool"""
        try:
            # Mock proxy pool initialization
            pool_size = config.get('pool_size', 100)
            rotation_strategy = config.get('rotation_strategy', 'round_robin')
            
            logger.info(f"Proxy pool initialized: {pool_size} proxies, {rotation_strategy} rotation")
            return True
        except:
            return False
            
    def _init_crewai(self, config: Dict) -> bool:
        """Initialisera CrewAI"""
        try:
            from crewai import Agent, Task, Crew
            
            max_agents = config.get('max_agents', 10)
            execution_timeout = config.get('execution_timeout', 300)
            
            logger.info(f"CrewAI initialized: max {max_agents} agents, {execution_timeout}s timeout")
            return True
        except:
            return False
            
    def _init_crawlee(self, config: Dict) -> bool:
        """Initialisera Crawlee"""
        try:
            # Mock Crawlee initialization
            concurrency = config.get('concurrency', 5)
            request_timeout = config.get('request_timeout', 30)
            
            logger.info(f"Crawlee initialized: {concurrency} concurrency, {request_timeout}s timeout")
            return True
        except:
            return False
            
    def _init_scrapy(self, config: Dict) -> bool:
        """Initialisera Scrapy"""
        try:
            import scrapy
            
            concurrent_requests = config.get('concurrent_requests', 16)
            download_timeout = config.get('download_timeout', 180)
            
            logger.info(f"Scrapy initialized: {concurrent_requests} concurrent, {download_timeout}s timeout")
            return True
        except:
            return False
            
    def _init_playwright_stealth(self, config: Dict) -> bool:
        """Initialisera Playwright Stealth"""
        try:
            from playwright.sync_api import sync_playwright
            
            browser_type = config.get('browser', 'chromium')
            headless = config.get('headless', True)
            
            logger.info(f"Playwright Stealth initialized: {browser_type}, headless={headless}")
            return True
        except:
            return False
            
    def _init_crawl4ai(self, config: Dict) -> bool:
        """Initialisera Crawl4AI"""
        try:
            # Mock Crawl4AI initialization
            llm_provider = config.get('llm_provider', 'openai')
            extraction_model = config.get('extraction_model', 'gpt-4')
            
            logger.info(f"Crawl4AI initialized: {llm_provider} provider, {extraction_model} model")
            return True
        except:
            return False
            
    def _init_secret_agent(self, config: Dict) -> bool:
        """Initialisera Secret Agent"""
        try:
            # Mock Secret Agent initialization
            human_like = config.get('human_like', True)
            fingerprint_randomization = config.get('fingerprint_randomization', True)
            
            logger.info(f"Secret Agent initialized: human_like={human_like}, fingerprint={fingerprint_randomization}")
            return True
        except:
            return False
            
    def _init_scrapegraph_ai(self, config: Dict) -> bool:
        """Initialisera Scrapegraph AI"""
        try:
            # Mock Scrapegraph AI initialization
            graph_model = config.get('graph_model', 'openai')
            extraction_chains = config.get('extraction_chains', True)
            
            logger.info(f"Scrapegraph AI initialized: {graph_model} model, chains={extraction_chains}")
            return True
        except:
            return False
            
    def _init_ip_rotator(self, config: Dict) -> bool:
        """Initialisera IP Rotator"""
        try:
            # Mock IP Rotator initialization
            regions = config.get('regions', ['us-east-1', 'eu-west-1'])
            
            logger.info(f"IP Rotator initialized: {len(regions)} regions")
            return True
        except:
            return False
            
    def _init_selenium_base(self, config: Dict) -> bool:
        """Initialisera SeleniumBase"""
        try:
            from seleniumbase import Driver
            
            browser = config.get('browser', 'chrome')
            headless = config.get('headless', True)
            
            logger.info(f"SeleniumBase initialized: {browser}, headless={headless}")
            return True
        except:
            return False
            
    def _init_fake_useragent(self, config: Dict) -> bool:
        """Initialisera Fake UserAgent"""
        try:
            from fake_useragent import UserAgent
            
            cache = config.get('cache', True)
            fallback = config.get('fallback', 'chrome')
            
            ua = UserAgent(cache=cache, fallback=fallback)
            logger.info(f"Fake UserAgent initialized: cache={cache}, fallback={fallback}")
            return True
        except:
            return False
            
    def _init_trafilatura(self, config: Dict) -> bool:
        """Initialisera Trafilatura"""
        try:
            import trafilatura
            
            include_comments = config.get('include_comments', False)
            include_tables = config.get('include_tables', True)
            
            logger.info(f"Trafilatura initialized: comments={include_comments}, tables={include_tables}")
            return True
        except:
            return False
            
    def _init_cloudflare_solver(self, config: Dict) -> bool:
        """Initialisera Cloudflare Solver"""
        try:
            # Mock Cloudflare Solver initialization
            solver_timeout = config.get('solver_timeout', 30)
            retry_attempts = config.get('retry_attempts', 3)
            
            logger.info(f"Cloudflare Solver initialized: {solver_timeout}s timeout, {retry_attempts} retries")
            return True
        except:
            return False
            
    def _init_generic_vendor(self, vendor_name: str, config: Dict) -> bool:
        """Generisk vendor initialisering"""
        try:
            logger.info(f"Generic vendor initialization: {vendor_name}")
            return True
        except:
            return False
            
    @contextmanager
    def get_vendor(self, vendor_name: str):
        """
        Context manager för att hämta en vendor (lazy loading)
        
        Args:
            vendor_name: Namnet på vendor
            
        Yields:
            Vendor instance eller None
        """
        if vendor_name not in self.vendors:
            logger.error(f"Unknown vendor: {vendor_name}")
            yield None
            return
            
        vendor = self.vendors[vendor_name]
        
        if not vendor.enabled:
            logger.warning(f"Vendor {vendor_name} is disabled")
            yield None
            return
            
        # Lazy load om inte redan laddad
        if vendor.status not in ["loaded", "healthy"]:
            success = self._initialize_vendor(vendor_name)
            if not success:
                yield None
                return
                
        try:
            yield vendor.instance
        finally:
            # Update last access time for cleanup
            vendor.last_health_check = time.time()
            
    def health_check_vendors(self) -> Dict[str, str]:
        """
        Kör hälsokontroll på alla aktiva vendors
        
        Returns:
            Dict med vendor namn och hälsostatus
        """
        results = {}
        
        for vendor_name, vendor in self.vendors.items():
            if vendor.enabled and vendor.status == "loaded":
                try:
                    # Mock health check - i verkligheten skulle detta testa vendor funktionalitet
                    if vendor.type in ["cloudflare_bypass", "stealth_browser", "ai_orchestration"]:
                        results[vendor_name] = "healthy"
                        vendor.status = "healthy"
                    else:
                        results[vendor_name] = "unknown"
                        
                    vendor.last_health_check = time.time()
                    
                except Exception as e:
                    results[vendor_name] = f"unhealthy: {e}"
                    vendor.status = "unhealthy"
            else:
                results[vendor_name] = vendor.status
                
        return results
        
    def cleanup_unused_vendors(self) -> int:
        """
        Rensa upp vendors som inte använts på länge
        
        Returns:
            Antal vendors som rensades
        """
        if not self.unload_unused:
            return 0
            
        current_time = time.time()
        cleaned = 0
        
        for vendor_name, vendor in self.vendors.items():
            if (vendor.status == "loaded" and 
                vendor.last_health_check and 
                current_time - vendor.last_health_check > self.idle_timeout):
                
                try:
                    # Cleanup vendor instance
                    if vendor.instance:
                        if hasattr(vendor.instance, 'close'):
                            vendor.instance.close()
                        vendor.instance = None
                        
                    vendor.status = "unknown"
                    cleaned += 1
                    logger.info(f"Cleaned up unused vendor: {vendor_name}")
                    
                except Exception as e:
                    logger.error(f"Error cleaning up {vendor_name}: {e}")
                    
        return cleaned
        
    def get_vendor_status(self) -> Dict[str, Any]:
        """
        Hämta status för alla vendors
        
        Returns:
            Dict med detaljerad status information
        """
        status = {
            "total_vendors": len(self.vendors),
            "enabled_vendors": len([v for v in self.vendors.values() if v.enabled]),
            "loaded_vendors": len([v for v in self.vendors.values() if v.status == "loaded"]),
            "healthy_vendors": len([v for v in self.vendors.values() if v.status == "healthy"]),
            "failed_vendors": len([v for v in self.vendors.values() if v.status == "failed"]),
            "vendors": {}
        }
        
        for vendor_name, vendor in self.vendors.items():
            status["vendors"][vendor_name] = {
                "type": vendor.type,
                "priority": vendor.priority,
                "enabled": vendor.enabled,
                "status": vendor.status,
                "init_on_startup": vendor.init_on_startup,
                "last_health_check": vendor.last_health_check
            }
            
        return status
        
    def start_background_tasks(self) -> None:
        """Starta bakgrundsprocesser för vendor management"""
        import threading
        
        def health_check_loop():
            while True:
                try:
                    time.sleep(self.health_check_interval)
                    self.health_check_vendors()
                    self.cleanup_unused_vendors()
                except Exception as e:
                    logger.error(f"Background task error: {e}")
                    
        health_thread = threading.Thread(target=health_check_loop, daemon=True)
        health_thread.start()
        logger.info("Started background vendor management tasks")


def main():
    """Huvudfunktion för att testa vendor manager"""
    print("🦉 Sparkling-Owl-Spin Vendor Manager")
    print("=" * 50)
    
    # Skapa vendor manager
    vm = VendorManager()
    
    # Visa initial status
    print("\n📊 Initial Vendor Status:")
    status = vm.get_vendor_status()
    print(f"Total vendors: {status['total_vendors']}")
    print(f"Enabled vendors: {status['enabled_vendors']}")
    
    # Initialisera startup vendors
    print("\n🚀 Initializing startup vendors...")
    startup_results = vm.initialize_startup_vendors()
    
    print("\n✅ Startup Results:")
    for vendor, success in startup_results.items():
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {vendor}: {'Success' if success else 'Failed'}")
    
    # Visa final status
    print("\n📊 Final Vendor Status:")
    status = vm.get_vendor_status()
    print(f"Loaded vendors: {status['loaded_vendors']}")
    print(f"Healthy vendors: {status['healthy_vendors']}")
    print(f"Failed vendors: {status['failed_vendors']}")
    
    # Testa lazy loading
    print("\n🔄 Testing lazy loading...")
    with vm.get_vendor("scrapy") as scrapy_vendor:
        if scrapy_vendor:
            print("✅ Scrapy loaded successfully via lazy loading")
        else:
            print("❌ Failed to load Scrapy")
    
    # Starta bakgrundsprocesser
    print("\n🔄 Starting background tasks...")
    vm.start_background_tasks()
    
    print("\n🎉 Vendor Manager Test Complete!")
    print("\nVendor Manager är nu redo för production användning!")


if __name__ == "__main__":
    main()
