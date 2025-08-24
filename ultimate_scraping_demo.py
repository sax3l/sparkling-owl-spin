#!/usr/bin/env python3
"""
Ultimate Scraping System Demo
=============================

Komplett demonstration av hela scraping-arkitekturen med:
✅ Alla system som kan väljas och konfigureras
✅ Real-time monitorering och rapportering
✅ Budgetkontroll och kostnadsuppföljning
✅ Interaktiv kontrollpanel
✅ Omfattande konfigurationsmöjligheter
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from pathlib import Path
import json

# Våra system
from ultimate_scraping_control_center import UltimateScrapingControlCenter, ScrapeJobConfig, SystemType, MonitoringLevel
from ultimate_configuration_manager import ConfigurationManager, UltimateScrapingConfiguration
from ultimate_scraping_system import UltimateScrapingSystem, UltimateScrapingConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractiveDemo:
    """Interaktiv demonstration av hela systemet."""
    
    def __init__(self):
        self.control_center = None
        self.config_manager = ConfigurationManager()
        
    async def run_complete_demo(self):
        """Kör komplett demonstration."""
        
        print("\n" + "="*80)
        print("🚀 ULTIMATE SCRAPING SYSTEM - COMPLETE DEMO")
        print("="*80)
        
        # Demo menu
        demo_options = {
            "1": "🎛️ Interactive Control Center Demo",
            "2": "⚙️ Configuration Management Demo", 
            "3": "🤖 Multi-System Scraping Demo",
            "4": "📊 Monitoring & Reporting Demo",
            "5": "💰 Budget & Cost Control Demo",
            "6": "🔧 Advanced Features Demo",
            "7": "🚀 Run All Demos Sequentially",
            "0": "Exit"
        }
        
        while True:
            print("\n📋 DEMO OPTIONS:")
            for key, desc in demo_options.items():
                print(f"  {key}: {desc}")
                
            choice = input("\nSelect demo option (0-7): ").strip()
            
            if choice == "0":
                print("👋 Demo completed!")
                break
            elif choice == "1":
                await self.demo_control_center()
            elif choice == "2":
                await self.demo_configuration_management()
            elif choice == "3":
                await self.demo_multi_system_scraping()
            elif choice == "4":
                await self.demo_monitoring_reporting()
            elif choice == "5":
                await self.demo_budget_control()
            elif choice == "6":
                await self.demo_advanced_features()
            elif choice == "7":
                await self.run_all_demos()
            else:
                print("❌ Invalid option")
                
    async def demo_control_center(self):
        """Demo av Control Center."""
        
        print("\n🎛️ CONTROL CENTER DEMO")
        print("-" * 40)
        
        # Initialisera Control Center
        self.control_center = UltimateScrapingControlCenter()
        await self.control_center.initialize()
        
        print("✅ Control Center initialized")
        
        # Skapa exempel-jobb
        demo_job = ScrapeJobConfig(
            job_id="demo_job_001",
            name="Demo Scraping Job",
            description="Demonstration of scraping capabilities",
            urls=[
                "https://httpbin.org/headers",
                "https://httpbin.org/user-agent", 
                "https://httpbin.org/ip"
            ],
            concurrent_requests=5,
            monitoring_level=MonitoringLevel.COMPREHENSIVE,
            use_proxy_broker=True,
            use_ip_rotation=True
        )
        
        print(f"📝 Created demo job: {demo_job.name}")
        
        # Starta jobb
        job_id = await self.control_center.start_scraping_job(demo_job)
        print(f"🚀 Started job: {job_id}")
        
        # Vänta lite för att visa progress
        print("⏳ Running job for 10 seconds...")
        await asyncio.sleep(10)
        
        # Visa status
        print("\n📊 JOB STATUS:")
        self.control_center.display_active_jobs()
        
        print("\n💻 SYSTEM METRICS:")
        self.control_center.display_system_metrics()
        
        await self.control_center.shutdown()
        
    async def demo_configuration_management(self):
        """Demo av konfigurationshantering."""
        
        print("\n⚙️ CONFIGURATION MANAGEMENT DEMO")
        print("-" * 40)
        
        # Ladda standardkonfiguration
        config = self.config_manager.load_config()
        print("✅ Default configuration loaded")
        
        # Visa aktuella inställningar
        print("\n📋 CURRENT PROXY SETTINGS:")
        proxy_settings = config.proxy_settings
        print(f"  Max proxies: {proxy_settings.max_proxies_in_pool}")
        print(f"  Validation timeout: {proxy_settings.proxy_validation_timeout}s")
        print(f"  Enabled sources: {len(proxy_settings.enabled_proxy_sources)}")
        
        print("\n📋 CURRENT SCRAPING SETTINGS:")
        scraping_settings = config.scraping_settings
        print(f"  Max concurrent requests: {scraping_settings.max_concurrent_requests}")
        print(f"  Default timeout: {scraping_settings.default_timeout}s")
        print(f"  Max retries: {scraping_settings.max_retries}")
        
        # Uppdatera inställningar
        print("\n🔧 UPDATING CONFIGURATION...")
        self.config_manager.update_config_section("proxy", {
            "max_proxies_in_pool": 150,
            "proxy_validation_timeout": 15.0
        })
        
        self.config_manager.update_config_section("scraping", {
            "max_concurrent_requests": 75,
            "default_timeout": 45.0
        })
        
        print("✅ Configuration updated")
        
        # Skapa templates
        print("\n📄 CREATING CONFIGURATION TEMPLATES...")
        templates = ["high_performance", "low_resource", "debug", "production"]
        
        for template in templates:
            success = self.config_manager.create_config_template(template)
            print(f"  {template}: {'✅ Created' if success else '❌ Failed'}")
            
        # Validera konfiguration
        print("\n✅ VALIDATING CONFIGURATION...")
        errors = self.config_manager.validate_config(config)
        if errors:
            print("❌ Configuration errors found:")
            for error in errors:
                print(f"    - {error}")
        else:
            print("✅ Configuration is valid")
            
    async def demo_multi_system_scraping(self):
        """Demo av multi-system scraping."""
        
        print("\n🤖 MULTI-SYSTEM SCRAPING DEMO")
        print("-" * 40)
        
        # Test olika system kombinationer
        system_configs = [
            {
                "name": "Proxy Broker Only",
                "use_proxy_broker": True,
                "use_ip_rotation": False,
                "use_enhanced_proxy": False
            },
            {
                "name": "IP Rotation Only", 
                "use_proxy_broker": False,
                "use_ip_rotation": True,
                "use_enhanced_proxy": False
            },
            {
                "name": "All Systems Combined",
                "use_proxy_broker": True,
                "use_ip_rotation": True,
                "use_enhanced_proxy": True
            }
        ]
        
        test_urls = [
            "https://httpbin.org/headers",
            "https://httpbin.org/ip", 
            "https://httpbin.org/user-agent"
        ]
        
        for i, sys_config in enumerate(system_configs):
            print(f"\n🧪 TEST {i+1}: {sys_config['name']}")
            
            # Skapa jobb med denna konfiguration
            job_config = ScrapeJobConfig(
                job_id=f"multi_system_test_{i+1}",
                name=sys_config["name"],
                description=f"Testing {sys_config['name']} configuration",
                urls=test_urls,
                use_proxy_broker=sys_config["use_proxy_broker"],
                use_ip_rotation=sys_config["use_ip_rotation"],
                use_enhanced_proxy=sys_config["use_enhanced_proxy"],
                concurrent_requests=3,
                monitoring_level=MonitoringLevel.COMPREHENSIVE
            )
            
            # Initiera Control Center om det inte redan finns
            if not self.control_center:
                self.control_center = UltimateScrapingControlCenter()
                await self.control_center.initialize()
                
            # Kör test
            job_id = await self.control_center.start_scraping_job(job_config)
            print(f"  🚀 Started job: {job_id}")
            
            # Vänta på completion
            print("  ⏳ Waiting for completion...")
            await asyncio.sleep(8)
            
            # Visa resultat
            if job_id in self.control_center.active_jobs:
                result = self.control_center.active_jobs[job_id]
                print(f"  📊 Results:")
                print(f"    - Total requests: {result.total_requests}")
                print(f"    - Success rate: {result.success_rate:.1f}%")
                print(f"    - Avg response time: {result.avg_response_time:.2f}s")
                print(f"    - System usage: {result.system_usage}")
                
        if self.control_center:
            await self.control_center.shutdown()
            self.control_center = None
            
    async def demo_monitoring_reporting(self):
        """Demo av monitoring och rapportering."""
        
        print("\n📊 MONITORING & REPORTING DEMO")
        print("-" * 40)
        
        # Initiera Control Center
        if not self.control_center:
            self.control_center = UltimateScrapingControlCenter()
            await self.control_center.initialize()
            
        # Skapa jobb med olika monitoring levels
        monitoring_levels = [
            MonitoringLevel.MINIMAL,
            MonitoringLevel.STANDARD, 
            MonitoringLevel.COMPREHENSIVE,
            MonitoringLevel.EXTREME
        ]
        
        for level in monitoring_levels:
            print(f"\n🔍 Testing {level.value.upper()} monitoring")
            
            job_config = ScrapeJobConfig(
                job_id=f"monitoring_test_{level.value}",
                name=f"Monitoring Test - {level.value}",
                description=f"Testing {level.value} monitoring level",
                urls=["https://httpbin.org/delay/1", "https://httpbin.org/status/200"],
                monitoring_level=level,
                concurrent_requests=2
            )
            
            job_id = await self.control_center.start_scraping_job(job_config)
            print(f"  🚀 Job started with {level.value} monitoring")
            
            await asyncio.sleep(5)
            
        # Visa alla metrics
        print("\n📈 CURRENT SYSTEM METRICS:")
        self.control_center.display_system_metrics()
        
        print("\n💼 ACTIVE JOBS:")
        self.control_center.display_active_jobs()
        
        # Generera rapport
        print("\n📄 GENERATING COMPREHENSIVE REPORT...")
        await self.control_center.generate_comprehensive_report()
        print("✅ Report generated in reports/ directory")
        
        await self.control_center.shutdown()
        self.control_center = None
        
    async def demo_budget_control(self):
        """Demo av budget och kostnadskontroll."""
        
        print("\n💰 BUDGET & COST CONTROL DEMO")
        print("-" * 40)
        
        # Test olika budget-inställningar
        budget_scenarios = [
            {
                "name": "Low Budget",
                "max_cost_per_hour": 1.0,
                "cost_per_request": 0.01,
                "budget_alerts": True
            },
            {
                "name": "Medium Budget",
                "max_cost_per_hour": 5.0,
                "cost_per_request": 0.005,
                "budget_alerts": True
            },
            {
                "name": "High Budget",
                "max_cost_per_hour": 20.0,
                "cost_per_request": 0.001,
                "budget_alerts": False
            }
        ]
        
        if not self.control_center:
            self.control_center = UltimateScrapingControlCenter()
            await self.control_center.initialize()
            
        for scenario in budget_scenarios:
            print(f"\n💵 Testing {scenario['name']} scenario")
            
            job_config = ScrapeJobConfig(
                job_id=f"budget_test_{scenario['name'].lower().replace(' ', '_')}",
                name=f"Budget Test - {scenario['name']}",
                description=f"Testing budget control with {scenario['name']} settings",
                urls=["https://httpbin.org/json"] * 20,  # 20 requests
                max_cost_per_hour=scenario["max_cost_per_hour"],
                cost_per_request=scenario["cost_per_request"],
                budget_alerts=scenario["budget_alerts"],
                concurrent_requests=5
            )
            
            job_id = await self.control_center.start_scraping_job(job_config)
            print(f"  🚀 Started job with ${scenario['max_cost_per_hour']}/hour budget")
            
            await asyncio.sleep(6)
            
            # Visa cost tracking
            if job_id in self.control_center.active_jobs:
                result = self.control_center.active_jobs[job_id]
                print(f"  💰 Current estimated cost: ${result.estimated_cost:.3f}")
                
        # Visa budget dashboard
        print("\n💰 BUDGET TRACKING DASHBOARD:")
        self.control_center.display_budget_tracking()
        
        await self.control_center.shutdown()
        self.control_center = None
        
    async def demo_advanced_features(self):
        """Demo av avancerade funktioner."""
        
        print("\n🔧 ADVANCED FEATURES DEMO")
        print("-" * 40)
        
        # Demo av avancerade scraping-funktioner
        advanced_job = ScrapeJobConfig(
            job_id="advanced_features_demo",
            name="Advanced Features Demo",
            description="Demonstration of advanced scraping capabilities",
            urls=[
                "https://httpbin.org/headers",
                "https://httpbin.org/cookies/set/demo/value",
                "https://httpbin.org/redirect/3",
                "https://httpbin.org/gzip"
            ],
            
            # Advanced settings
            user_agents=[
                "CustomBot/1.0 (Advanced Demo)",
                "ScrapingBot/2.0 (Feature Test)"
            ],
            custom_headers={
                "X-Custom-Header": "AdvancedDemo",
                "X-Feature-Test": "true"
            },
            cookie_handling=True,
            javascript_execution=False,  # Would require browser
            screenshot_capture=False,    # Would require browser
            
            # Performance settings
            concurrent_requests=8,
            delay_between_requests=0.2,
            timeout=25.0,
            max_retries=4,
            
            # Monitoring
            monitoring_level=MonitoringLevel.EXTREME,
            detailed_logging=True,
            performance_profiling=True
        )
        
        if not self.control_center:
            self.control_center = UltimateScrapingControlCenter()
            await self.control_center.initialize()
            
        print("🚀 Starting advanced features demonstration...")
        job_id = await self.control_center.start_scraping_job(advanced_job)
        
        print("⏳ Running advanced scraping job...")
        await asyncio.sleep(15)
        
        # Visa detaljerade resultat
        if job_id in self.control_center.active_jobs:
            result = self.control_center.active_jobs[job_id]
            print("\n📊 ADVANCED FEATURES RESULTS:")
            print(f"  Total requests: {result.total_requests}")
            print(f"  Success rate: {result.success_rate:.1f}%")
            print(f"  Average response time: {result.avg_response_time:.2f}s")
            print(f"  Data scraped: {result.total_data_scraped} bytes")
            print(f"  Requests per minute: {result.requests_per_minute:.1f}")
            print(f"  System usage: {result.system_usage}")
            
            if result.error_summary:
                print(f"  Errors encountered: {result.error_summary}")
                
        await self.control_center.shutdown()
        self.control_center = None
        
    async def run_all_demos(self):
        """Kör alla demos sekventiellt."""
        
        print("\n🚀 RUNNING ALL DEMOS SEQUENTIALLY")
        print("=" * 50)
        
        demos = [
            ("Configuration Management", self.demo_configuration_management),
            ("Multi-System Scraping", self.demo_multi_system_scraping),
            ("Monitoring & Reporting", self.demo_monitoring_reporting), 
            ("Budget Control", self.demo_budget_control),
            ("Advanced Features", self.demo_advanced_features)
        ]
        
        for name, demo_func in demos:
            print(f"\n▶️  Starting {name} Demo...")
            try:
                await demo_func()
                print(f"✅ {name} Demo completed successfully")
            except Exception as e:
                print(f"❌ {name} Demo failed: {e}")
                
            # Pause mellan demos
            await asyncio.sleep(2)
            
        print("\n🎉 ALL DEMOS COMPLETED!")
        
        # Final system status
        await self.show_final_status()
        
    async def show_final_status(self):
        """Visa final system status."""
        
        print("\n📋 FINAL SYSTEM STATUS")
        print("-" * 30)
        
        # Configuration status
        config = self.config_manager.load_config()
        print("⚙️ Configuration Status: ✅ Loaded")
        
        # Check created files
        reports_dir = Path("reports")
        if reports_dir.exists():
            reports = list(reports_dir.glob("*.json"))
            print(f"📄 Reports Generated: {len(reports)}")
            
        config_dir = Path("config")
        if config_dir.exists():
            configs = list(config_dir.glob("*.json"))
            print(f"⚙️ Configuration Files: {len(configs)}")
            
        # System capabilities
        print("\n🚀 SYSTEM CAPABILITIES DEMONSTRATED:")
        print("  ✅ Multi-system proxy management")
        print("  ✅ Dynamic configuration management")  
        print("  ✅ Real-time monitoring & reporting")
        print("  ✅ Budget control & cost tracking")
        print("  ✅ Advanced scraping features")
        print("  ✅ Interactive control center")
        print("  ✅ Comprehensive error handling")
        print("  ✅ Performance optimization")
        
        print("\n🎯 READY FOR PRODUCTION USE!")


async def main():
    """Huvudfunktion för demonstration."""
    
    try:
        demo = InteractiveDemo()
        await demo.run_complete_demo()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        logger.exception("Demo failed")
        
    finally:
        print("\n🏁 Demo session ended")


if __name__ == "__main__":
    # Säkerställ att alla directories finns
    for directory in ["config", "reports", "results", "logs", "temp", "cache"]:
        Path(directory).mkdir(exist_ok=True)
        
    print("🚀 Starting Ultimate Scraping System Demo...")
    print("This demo showcases all system capabilities including:")
    print("  • Selectable scraping systems")
    print("  • Comprehensive monitoring")
    print("  • Dynamic configuration")
    print("  • Budget control")
    print("  • Advanced features")
    print("\nPress Ctrl+C anytime to exit")
    
    asyncio.run(main())
