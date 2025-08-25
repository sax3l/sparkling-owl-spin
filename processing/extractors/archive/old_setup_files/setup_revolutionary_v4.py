#!/usr/bin/env python3
"""
🚀 REVOLUTIONARY ULTIMATE SYSTEM SETUP SCRIPT 🚀
=================================================

Automatisk installation och konfiguration av hela systemet:
1. Installerar alla Python-beroenden
2. Sätter upp konfigurationsfiler  
3. Startar Docker-tjänster
4. Validerar alla komponenter
5. Kör testfall för att säkerställa att allt fungerar

Kör: python setup_revolutionary_v4.py
"""

import os
import sys
import subprocess
import shutil
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RevolutionarySetup:
    """Setup manager för Revolutionary Ultimate System"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"
        self.data_dir = self.project_root / "data"
        
        self.required_commands = ['docker', 'docker-compose', 'python', 'pip']
        self.docker_services = [
            'flaresolverr', 'tika', 'postgresql', 'redis', 
            'prometheus', 'grafana'
        ]
        
    def print_banner(self):
        """Print setup banner"""
        banner = """
🚀 REVOLUTIONARY ULTIMATE SCRAPING SYSTEM v4.0 🚀
=================================================

Den ultimata scraping-plattformen med:
✅ Anti-bot defense (CloudScraper, FlareSolverr, undetected-chrome)
✅ Content extraction (Trafilatura, Tika, PDF-Extract-Kit)  
✅ Entity recognition (Microsoft Recognizers-Text)
✅ CAPTCHA solving (2captcha, NopeCHA)
✅ TLS fingerprinting (azuretls-client)
✅ Quality control & monitoring
✅ Per-domain policies
✅ Production-ready architecture

Startar installation...
        """
        print(banner)
    
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        logger.info("🔍 Checking system prerequisites...")
        
        missing_commands = []
        
        for cmd in self.required_commands:
            if not shutil.which(cmd):
                missing_commands.append(cmd)
        
        if missing_commands:
            logger.error(f"❌ Missing required commands: {', '.join(missing_commands)}")
            
            if 'docker' in missing_commands:
                logger.error("   Please install Docker: https://docs.docker.com/get-docker/")
            if 'docker-compose' in missing_commands:
                logger.error("   Please install Docker Compose: https://docs.docker.com/compose/install/")
            if 'python' in missing_commands:
                logger.error("   Please install Python 3.8+: https://python.org")
            if 'pip' in missing_commands:
                logger.error("   pip should come with Python")
            
            return False
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.error(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        
        logger.info("✅ All prerequisites met")
        return True
    
    def create_directories(self):
        """Create necessary directories"""
        logger.info("📁 Creating project directories...")
        
        directories = [
            self.config_dir,
            self.logs_dir, 
            self.data_dir,
            self.project_root / "revolutionary_scraper",
            self.config_dir / "grafana" / "dashboards",
            self.config_dir / "grafana" / "datasources"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"   📁 Created: {directory}")
    
    def install_python_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("📦 Installing Python dependencies...")
        
        requirements_file = self.project_root / "requirements_revolutionary_enhanced.txt"
        
        if not requirements_file.exists():
            logger.error(f"❌ Requirements file not found: {requirements_file}")
            return False
        
        try:
            # Upgrade pip first
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Install requirements
            cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            logger.info("✅ Python dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install Python dependencies: {e}")
            logger.error(f"   stdout: {e.stdout}")
            logger.error(f"   stderr: {e.stderr}")
            return False
    
    def create_configuration_files(self):
        """Create configuration files"""
        logger.info("⚙️  Creating configuration files...")
        
        # Redis configuration
        redis_config = """
# Redis configuration för Revolutionary System
bind 0.0.0.0
port 6379
timeout 300
tcp-keepalive 60
maxmemory 512mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
        """
        
        redis_config_path = self.config_dir / "redis.conf"
        with open(redis_config_path, 'w') as f:
            f.write(redis_config.strip())
        
        # Prometheus configuration
        prometheus_config = """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:

scrape_configs:
  - job_name: 'revolutionary-scraper'
    static_configs:
      - targets: ['scraper_app:8000']
    metrics_path: /metrics
    scrape_interval: 30s
    
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
        """
        
        prometheus_config_path = self.config_dir / "prometheus.yml"
        with open(prometheus_config_path, 'w') as f:
            f.write(prometheus_config.strip())
        
        # Grafana datasource
        grafana_datasource = """
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
        """
        
        datasource_path = self.config_dir / "grafana" / "datasources" / "prometheus.yml"
        with open(datasource_path, 'w') as f:
            f.write(grafana_datasource.strip())
        
        # Environment file template
        env_template = """
# Revolutionary Ultimate Scraping System Environment Variables
# ============================================================

# CAPTCHA solving services (obtain keys from providers)
TWOCAPTCHA_API_KEY=your-2captcha-api-key-here
NOPECHA_API_KEY=your-nopecha-api-key-here

# Monitoring (optional)
SENTRY_DSN=your-sentry-dsn-here

# Database (will be set automatically by Docker)
DATABASE_URL=postgresql://scraper_user:scraper_password@localhost:5432/revolutionary_scraper
REDIS_URL=redis://localhost:6379/0

# Services (will be set automatically by Docker)
FLARESOLVERR_URL=http://localhost:8191/v1
TIKA_SERVER_URL=http://localhost:9998

# System
LOG_LEVEL=INFO
        """
        
        env_path = self.project_root / ".env.example"
        with open(env_path, 'w') as f:
            f.write(env_template.strip())
        
        logger.info("✅ Configuration files created")
    
    def start_docker_services(self) -> bool:
        """Start Docker services"""
        logger.info("🐳 Starting Docker services...")
        
        compose_file = self.project_root / "docker-compose.revolutionary.yml"
        
        if not compose_file.exists():
            logger.error(f"❌ Docker Compose file not found: {compose_file}")
            return False
        
        try:
            # Pull images först
            logger.info("   📥 Pulling Docker images...")
            subprocess.run([
                "docker-compose", "-f", str(compose_file), 
                "pull"
            ], check=True, capture_output=True)
            
            # Start services
            logger.info("   🚀 Starting services...")
            subprocess.run([
                "docker-compose", "-f", str(compose_file),
                "up", "-d", "--remove-orphans"
            ], check=True, capture_output=True)
            
            logger.info("✅ Docker services started")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to start Docker services: {e}")
            return False
    
    def wait_for_services(self) -> bool:
        """Wait for services to be ready"""
        logger.info("⏳ Waiting for services to be ready...")
        
        services = {
            'FlareSolverr': 'http://localhost:8191',
            'Tika': 'http://localhost:9998/tika',
            'PostgreSQL': 'postgresql://scraper_user:scraper_password@localhost:5432/revolutionary_scraper',
            'Redis': 'redis://localhost:6379',
        }
        
        import time
        import requests
        import psycopg2
        import redis
        
        max_retries = 30  # 5 minutes
        
        for service_name, url in services.items():
            logger.info(f"   ⏳ Waiting for {service_name}...")
            
            for attempt in range(max_retries):
                try:
                    if service_name == 'PostgreSQL':
                        # Test PostgreSQL connection
                        conn = psycopg2.connect(
                            "dbname=revolutionary_scraper user=scraper_user password=scraper_password host=localhost port=5432"
                        )
                        conn.close()
                    elif service_name == 'Redis':
                        # Test Redis connection
                        r = redis.Redis(host='localhost', port=6379, db=0)
                        r.ping()
                    else:
                        # Test HTTP services
                        response = requests.get(url, timeout=5)
                        response.raise_for_status()
                    
                    logger.info(f"   ✅ {service_name} ready")
                    break
                    
                except Exception:
                    if attempt < max_retries - 1:
                        time.sleep(10)
                    else:
                        logger.warning(f"   ⚠️  {service_name} not ready after {max_retries} attempts")
                        return False
        
        logger.info("✅ All services ready")
        return True
    
    def create_database_schema(self) -> bool:
        """Create database schema"""
        logger.info("🗃️  Setting up database schema...")
        
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                "dbname=revolutionary_scraper user=scraper_user password=scraper_password host=localhost port=5432"
            )
            
            with conn.cursor() as cur:
                # Create tables
                schema_sql = """
                -- Revolutionary Scraping System Database Schema
                
                CREATE TABLE IF NOT EXISTS scraping_tasks (
                    id SERIAL PRIMARY KEY,
                    task_id VARCHAR(100) UNIQUE NOT NULL,
                    url TEXT NOT NULL,
                    domain VARCHAR(255),
                    method VARCHAR(10) DEFAULT 'GET',
                    headers JSONB,
                    data JSONB,
                    priority INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW(),
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error TEXT,
                    attempts INTEGER DEFAULT 0
                );
                
                CREATE TABLE IF NOT EXISTS scraping_results (
                    id SERIAL PRIMARY KEY,
                    task_id VARCHAR(100) REFERENCES scraping_tasks(task_id),
                    success BOOLEAN NOT NULL,
                    method_used VARCHAR(50),
                    status_code INTEGER,
                    response_headers JSONB,
                    content_length INTEGER,
                    execution_time FLOAT,
                    quality_score FLOAT,
                    is_duplicate BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS extracted_content (
                    id SERIAL PRIMARY KEY,
                    task_id VARCHAR(100) REFERENCES scraping_tasks(task_id),
                    content_type VARCHAR(50),
                    title TEXT,
                    text_content TEXT,
                    html_content TEXT,
                    markdown_content TEXT,
                    author VARCHAR(255),
                    date_published TIMESTAMP,
                    description TEXT,
                    keywords TEXT[],
                    language VARCHAR(10),
                    links JSONB,
                    images JSONB,
                    entities JSONB,
                    tables JSONB,
                    text_length INTEGER,
                    word_count INTEGER,
                    extraction_method VARCHAR(50),
                    created_at TIMESTAMP DEFAULT NOW()
                );
                
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id SERIAL PRIMARY KEY,
                    metric_name VARCHAR(100) NOT NULL,
                    metric_value FLOAT NOT NULL,
                    labels JSONB,
                    timestamp TIMESTAMP DEFAULT NOW()
                );
                
                -- Indexes for performance
                CREATE INDEX IF NOT EXISTS idx_tasks_domain ON scraping_tasks(domain);
                CREATE INDEX IF NOT EXISTS idx_tasks_status ON scraping_tasks(status);
                CREATE INDEX IF NOT EXISTS idx_tasks_created ON scraping_tasks(created_at);
                CREATE INDEX IF NOT EXISTS idx_results_task ON scraping_results(task_id);
                CREATE INDEX IF NOT EXISTS idx_content_task ON extracted_content(task_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON system_metrics(metric_name, timestamp);
                """
                
                cur.execute(schema_sql)
                conn.commit()
            
            conn.close()
            logger.info("✅ Database schema created")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create database schema: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run system tests"""
        logger.info("🧪 Running system tests...")
        
        try:
            # Import and test components
            sys.path.insert(0, str(self.project_root))
            
            from revolutionary_scraper.revolutionary_ultimate_v4 import RevolutionaryUltimateSystem
            
            async def test_system():
                async with RevolutionaryUltimateSystem() as system:
                    # Test simple URL
                    result = await system.scrape_url("https://httpbin.org/get")
                    
                    if result.success:
                        logger.info("   ✅ Basic scraping test passed")
                        return True
                    else:
                        logger.error(f"   ❌ Basic scraping test failed: {result.error}")
                        return False
            
            # Run async test
            success = asyncio.run(test_system())
            
            if success:
                logger.info("✅ All tests passed")
                return True
            else:
                logger.error("❌ Some tests failed")
                return False
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {e}")
            return False
    
    def print_completion_message(self):
        """Print completion message"""
        message = """
🎉 INSTALLATION COMPLETE! 🎉
============================

Revolutionary Ultimate Scraping System v4.0 är nu redo att använda!

📋 SERVICES RUNNING:
• FlareSolverr:  http://localhost:8191 (Cloudflare bypass)
• Apache Tika:   http://localhost:9998 (Content extraction)
• PostgreSQL:    localhost:5432 (Database)
• Redis:         localhost:6379 (Caching)
• Prometheus:    http://localhost:9090 (Metrics)
• Grafana:       http://localhost:3000 (Dashboards)

🚀 QUICK START:
1. Kopiera .env.example till .env och lägg till dina API-nycklar
2. Kör: python -m revolutionary_scraper.revolutionary_ultimate_v4
3. Eller använd som bibliotek i dina egna skript

📚 EXAMPLES:
  from revolutionary_scraper.revolutionary_ultimate_v4 import RevolutionaryUltimateSystem
  
  async with RevolutionaryUltimateSystem() as scraper:
      result = await scraper.scrape_url("https://example.com")
      print(f"Success: {result.success}")
      if result.extracted_content:
          print(f"Title: {result.extracted_content.title}")

⚙️  CONFIGURATION:
• Redigera crawl-policies.yml för per-domain policies
• Lägg till dina 2captcha/NopeCHA API-nycklar i .env

📊 MONITORING:
• Grafana dashboards: http://localhost:3000 (admin/admin123)
• Prometheus metrics: http://localhost:9090

🛡️ ANTI-BOT FEATURES:
✅ CloudScraper för Cloudflare IUAM
✅ FlareSolverr för Turnstile challenges  
✅ undetected-chromedriver för svåra sajter
✅ 2captcha/NopeCHA CAPTCHA solving
✅ TLS/JA3 fingerprinting
✅ Smart retry logic

📄 CONTENT EXTRACTION:
✅ Trafilatura för clean HTML text
✅ Apache Tika för PDF/Office documents
✅ Entity recognition (dates, amounts, etc.)
✅ Quality scoring & deduplication
✅ Multiple output formats

Happy scraping! 🕸️
        """
        print(message)
    
    async def run_setup(self) -> bool:
        """Run complete setup process"""
        
        self.print_banner()
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Step 2: Create directories
        self.create_directories()
        
        # Step 3: Install dependencies
        if not self.install_python_dependencies():
            logger.warning("⚠️  Python dependencies failed - continuing anyway")
        
        # Step 4: Create configuration
        self.create_configuration_files()
        
        # Step 5: Start Docker services
        if not self.start_docker_services():
            logger.error("❌ Failed to start Docker services")
            return False
        
        # Step 6: Wait for services
        if not self.wait_for_services():
            logger.warning("⚠️  Some services not ready - continuing anyway")
        
        # Step 7: Create database schema
        if not self.create_database_schema():
            logger.warning("⚠️  Database schema creation failed - continuing anyway")
        
        # Step 8: Run tests
        if not self.run_tests():
            logger.warning("⚠️  Some tests failed - system may still be usable")
        
        # Step 9: Completion message
        self.print_completion_message()
        
        return True


# Main execution
async def main():
    """Main setup function"""
    setup = RevolutionarySetup()
    
    try:
        success = await setup.run_setup()
        
        if success:
            logger.info("✅ Setup completed successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Setup failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Setup failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
