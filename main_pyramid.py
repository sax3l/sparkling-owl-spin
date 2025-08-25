#!/usr/bin/env python3
"""
🦉 SPARKLING-OWL-SPIN MAIN ENTRY POINT
=====================================

Det här är den ENDA huvudingången för hela systemet.
Alla andra main*.py filer har arkiverats för att undvika förvirring.

Pyramid Architecture System - Core Application Launcher
Swedish Web Intelligence & Data Extraction Platform
"""

import asyncio
import logging
import sys
import signal
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core import initialize_core_system, shutdown_core_system, get_core_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sparkling_owl_spin.log')
    ]
)

logger = logging.getLogger(__name__)

class SparklingOwlSpinApplication:
    """Main application class"""
    
    def __init__(self):
        self.orchestrator = None
        self.running = False
        
    async def start(self):
        """Start the application"""
        try:
            logger.info("🦉 Starting Sparkling-Owl-Spin System")
            
            # Initialize core system
            self.orchestrator = await initialize_core_system()
            self.running = True
            
            # Print startup banner
            await self._print_startup_banner()
            
            # Keep running
            while self.running:
                await asyncio.sleep(1.0)
                
        except KeyboardInterrupt:
            logger.info("🛑 Shutdown requested by user")
            await self.shutdown()
        except Exception as e:
            logger.error(f"❌ Fatal error: {str(e)}")
            await self.shutdown()
            raise
            
    async def shutdown(self):
        """Shutdown the application"""
        if self.running:
            self.running = False
            logger.info("🔄 Shutting down Sparkling-Owl-Spin System")
            
            if self.orchestrator:
                await shutdown_core_system()
                
            logger.info("✅ Shutdown complete")
            
    async def _print_startup_banner(self):
        """Print startup banner"""
        
        status = get_core_status()
        
        banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  🦉 SPARKLING-OWL-SPIN - PYRAMID ARCHITECTURE SYSTEM                        ║
║                                                                              ║
║  Version: {status.get('version', '1.0.0'):<15} Status: {'✅ OPERATIONAL' if status.get('initialized', False) else '❌ ERROR':<15}              ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🏗️  PYRAMID ARCHITECTURE LAYERS:                                           ║
║                                                                              ║
║  📊 Layer 6: Configuration & Deployment                                     ║
║      └── Environment management, CI/CD, Infrastructure                      ║
║                                                                              ║
║  🌐 Layer 5: API & Interfaces                                               ║
║      └── REST API, Web UI, CLI, External integrations                      ║
║                                                                              ║
║  🔄 Layer 4: Data Processing                                                ║
║      └── Data sources, ETL pipelines, Export tools                         ║
║                                                                              ║
║  🤖 Layer 3: AI Agents                                                      ║
║      └── CrewAI agents, Task orchestration, Intelligence                   ║
║                                                                              ║
║  ⚙️  Layer 2: Engines                                                        ║
║      └── Scraping, Bypass, Network, Security engines                       ║
║                                                                              ║
║  🎯 Layer 1: Core                                                           ║
║      └── Orchestrator, Configuration, Security, API Gateway                ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🔧 SYSTEM COMPONENTS:                                                       ║
║                                                                              ║
"""
        
        components = status.get('components', {})
        for component, active in components.items():
            status_icon = "✅" if active else "❌"
            banner += f"║  {status_icon} {component:<30} {'ACTIVE' if active else 'INACTIVE':<10}                     ║\n"
            
        banner += f"""║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🛡️  SECURITY NOTICE:                                                        ║
║                                                                              ║
║  ⚠️  ENDAST FÖR AUKTORISERAD PENETRATIONSTESTNING                            ║
║  ⚠️  ENDAST EGNA SERVRAR OCH GODKÄNDA TESTMILJÖER                           ║
║  ⚠️  ALL AKTIVITET LOGGAS OCH ÖVERVAKAS                                     ║
║                                                                              ║
║  📋 GODKÄNDA ANVÄNDNINGSOMRÅDEN:                                             ║
║  • Penetrationstestning av egna system                                      ║
║  • Säkerhetsbedömning av auktoriserade mål                                  ║
║  • Dataextrahering från egna webbplatser                                    ║
║  • Automatisering av godkända processer                                     ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🌐 ACCESS POINTS:                                                           ║
║                                                                              ║
║  • API Gateway: http://localhost:8000                                       ║
║  • Health Check: http://localhost:8000/health                              ║
║  • Documentation: http://localhost:8000/docs                               ║
║  • System Status: http://localhost:8000/status                             ║
║                                                                              ║
║  🔍 AVAILABLE ENGINES:                                                       ║
║  • Enhanced Scraping Framework (Scrapy, Playwright, BeautifulSoup)         ║
║  • Cloudflare Bypass (FlareSolverr, CloudScraper, Undetected Chrome)      ║
║  • CAPTCHA Solver (2captcha, CapMonster, NopeCHA, Local OCR)               ║
║  • Undetected Browser Automation                                            ║
║  • Swedish Data Sources (Blocket, Bytbil, Company Registry)                ║
║  • AI Agent System (CrewAI, Specialized Agents)                            ║
║                                                                              ║
║  📖 QUICK START:                                                             ║
║  1. Skapa penetrationstestsession: POST /api/v1/security/pentest-sessions  ║
║  2. Skapa workflow: POST /api/v1/workflows                                  ║
║  3. Kör workflow: POST /api/v1/workflows/{{id}}/execute                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

🦉 System ready för authorized operations! Press Ctrl+C to shutdown.
"""
        
        print(banner)

def setup_signal_handlers(app):
    """Setup signal handlers för graceful shutdown"""
    
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(app.shutdown())
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point"""
    
    app = SparklingOwlSpinApplication()
    setup_signal_handlers(app)
    
    try:
        await app.start()
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
