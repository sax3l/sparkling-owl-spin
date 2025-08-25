#!/usr/bin/env python3
"""
Revolutionary Ultimate System v4.0 - Complete Setup Script
Automated installation and configuration of all system components.
"""

import os
import sys
import subprocess
import platform
import shutil
import urllib.request
import tarfile
import zipfile
from pathlib import Path
import json
import yaml
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemSetup:
    """Complete system setup and installation manager"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.architecture()[0]
        self.python_version = sys.version_info
        
        # Paths
        self.project_root = Path.cwd()
        self.tools_dir = self.project_root / "tools"
        self.data_dir = self.project_root / "data"
        self.logs_dir = self.project_root / "logs"
        
        logger.info(f"🚀 Initializing Revolutionary Ultimate System v4.0 Setup")
        logger.info(f"   System: {self.system} ({self.architecture})")
        logger.info(f"   Python: {self.python_version.major}.{self.python_version.minor}")
        logger.info(f"   Project root: {self.project_root}")
        
    def setup_directories(self):
        """Create necessary directories"""
        logger.info("📁 Creating project directories...")
        
        directories = [
            self.tools_dir,
            self.data_dir, 
            self.logs_dir,
            self.project_root / "config",
            self.project_root / "output",
            self.project_root / "cache",
            self.project_root / "browser_data",
            self.project_root / "proxies"
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
            logger.info(f"✅ Created directory: {directory.name}")
            
    def check_python_version(self):
        """Check Python version compatibility"""
        logger.info("🐍 Checking Python version...")
        
        if self.python_version < (3, 8):
            logger.error("❌ Python 3.8+ required")
            sys.exit(1)
            
        logger.info(f"✅ Python {self.python_version.major}.{self.python_version.minor} is compatible")
        
    def install_python_packages(self):
        """Install all Python dependencies"""
        logger.info("📦 Installing Python packages...")
        
        # Core requirements
        core_packages = [
            "requests[security,socks]>=2.31.0",
            "aiohttp>=3.9.0",
            "asyncio-throttle>=1.0.2",
            "cloudscraper>=1.2.71",
            "selenium>=4.15.0",
            "undetected-chromedriver>=3.5.4",
            "playwright>=1.40.0",
            "beautifulsoup4>=4.12.0",
            "lxml>=4.9.0",
            "trafilatura>=1.6.0",
            "readability-lxml>=0.8.1",
            "newspaper3k>=0.2.8",
            "python-tika>=2.6.0",
            "PyPDF2>=3.0.0",
            "pdfplumber>=0.10.0",
            "pdf-extract-kit>=0.1.0",
            "spacy>=3.7.0",
            "nltk>=3.8.0",
            "textblob>=0.17.1"
        ]
        
        # URL discovery packages
        discovery_packages = [
            "proxybroker>=0.3.2",
            "fake-useragent>=1.4.0",
            "user-agent>=0.1.10",
            "python-whois>=0.8.0",
            "dnspython>=2.4.0",
            "python-nmap>=0.7.1",
            "censys>=2.2.0",
            "shodan>=1.30.0",
            "virustotal-python>=1.0.3"
        ]
        
        # Web scraping enhancement packages
        enhancement_packages = [
            "selenium-stealth>=1.0.6",
            "selenium-profiles>=2.2.3",
            "helium>=3.1.3",
            "pyautogui>=0.9.54",
            "opencv-python>=4.8.0",
            "pillow>=10.1.0",
            "pytesseract>=0.3.10"
        ]
        
        # CAPTCHA solving packages
        captcha_packages = [
            "2captcha-python>=1.1.3",
            "anticaptchaofficial>=1.0.46",
            "python-anticaptcha>=1.0.0",
            "nopecha>=0.4.0"
        ]
        
        # Database and storage packages
        storage_packages = [
            "sqlalchemy>=2.0.0",
            "alembic>=1.13.0",
            "psycopg2-binary>=2.9.0",
            "redis>=5.0.0",
            "pymongo>=4.6.0",
            "elasticsearch>=8.11.0"
        ]
        
        # Monitoring and observability packages
        monitoring_packages = [
            "structlog>=23.2.0",
            "sentry-sdk>=1.38.0",
            "prometheus-client>=0.19.0",
            "opentelemetry-api>=1.21.0",
            "opentelemetry-sdk>=1.21.0"
        ]
        
        # Configuration and utilities packages
        utility_packages = [
            "pyyaml>=6.0.1",
            "pydantic>=2.5.0",
            "click>=8.1.0",
            "rich>=13.7.0",
            "tqdm>=4.66.0",
            "python-dotenv>=1.0.0",
            "schedule>=1.2.0"
        ]
        
        # Quality and testing packages
        quality_packages = [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0"
        ]
        
        all_packages = (
            core_packages + discovery_packages + enhancement_packages + 
            captcha_packages + storage_packages + monitoring_packages +
            utility_packages + quality_packages
        )
        
        logger.info(f"📦 Installing {len(all_packages)} Python packages...")
        
        # Install packages in batches to avoid timeout
        batch_size = 10
        for i in range(0, len(all_packages), batch_size):
            batch = all_packages[i:i+batch_size]
            logger.info(f"📦 Installing batch {i//batch_size + 1}/{(len(all_packages) + batch_size - 1)//batch_size}")
            
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + batch
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    logger.warning(f"⚠️ Some packages in batch failed: {result.stderr}")
                else:
                    logger.info(f"✅ Batch {i//batch_size + 1} installed successfully")
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Batch {i//batch_size + 1} installation timed out")
            except Exception as e:
                logger.error(f"❌ Error installing batch {i//batch_size + 1}: {str(e)}")
                
    def install_system_tools(self):
        """Install system-level tools and binaries"""
        logger.info("🔧 Installing system tools...")
        
        # Install Katana
        self._install_katana()
        
        # Install Chrome/Chromium for browser automation
        self._install_chrome()
        
        # Install additional tools based on OS
        if self.system == "linux":
            self._install_linux_tools()
        elif self.system == "windows":
            self._install_windows_tools()
        elif self.system == "darwin":
            self._install_macos_tools()
            
    def _install_katana(self):
        """Install Katana URL discovery tool"""
        logger.info("🔍 Installing Katana...")
        
        katana_dir = self.tools_dir / "katana"
        katana_dir.mkdir(exist_ok=True)
        
        # Determine download URL based on OS and architecture
        system_map = {
            "linux": "linux",
            "darwin": "macOS",
            "windows": "windows"
        }
        
        arch_map = {
            "64bit": "amd64",
            "32bit": "386"
        }
        
        os_name = system_map.get(self.system, "linux")
        arch_name = arch_map.get(self.architecture, "amd64")
        
        if self.system == "windows":
            filename = f"katana_2.0.4_{os_name}_{arch_name}.zip"
            binary_name = "katana.exe"
        else:
            filename = f"katana_2.0.4_{os_name}_{arch_name}.tar.gz"
            binary_name = "katana"
            
        download_url = f"https://github.com/projectdiscovery/katana/releases/download/v2.0.4/{filename}"
        
        try:
            logger.info(f"📥 Downloading Katana from {download_url}")
            download_path = katana_dir / filename
            
            urllib.request.urlretrieve(download_url, download_path)
            
            # Extract archive
            if filename.endswith('.zip'):
                with zipfile.ZipFile(download_path, 'r') as zip_ref:
                    zip_ref.extractall(katana_dir)
            else:
                with tarfile.open(download_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(katana_dir)
                    
            # Make binary executable on Unix systems
            binary_path = katana_dir / binary_name
            if self.system != "windows":
                os.chmod(binary_path, 0o755)
                
            logger.info(f"✅ Katana installed: {binary_path}")
            
            # Cleanup download
            download_path.unlink()
            
        except Exception as e:
            logger.error(f"❌ Failed to install Katana: {str(e)}")
            
    def _install_chrome(self):
        """Install Chrome/Chromium for browser automation"""
        logger.info("🌐 Setting up Chrome for browser automation...")
        
        try:
            # Install playwright browsers
            result = subprocess.run([
                sys.executable, "-m", "playwright", "install", "chromium"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Playwright Chromium installed")
            else:
                logger.warning(f"⚠️ Playwright install warning: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Failed to install Playwright browsers: {str(e)}")
            
    def _install_linux_tools(self):
        """Install Linux-specific tools"""
        logger.info("🐧 Installing Linux tools...")
        
        # Tools to install via apt/yum
        tools = [
            "curl",
            "wget", 
            "jq",
            "nmap",
            "whois",
            "dig",
            "tesseract-ocr",
            "poppler-utils"
        ]
        
        # Try apt first
        for tool in tools:
            try:
                result = subprocess.run([
                    "sudo", "apt-get", "install", "-y", tool
                ], capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    logger.info(f"✅ Installed {tool} via apt")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning(f"⚠️ Could not install {tool} via apt")
                
    def _install_windows_tools(self):
        """Install Windows-specific tools"""
        logger.info("🪟 Installing Windows tools...")
        
        # Check if chocolatey is available
        try:
            subprocess.run(["choco", "--version"], capture_output=True, check=True)
            choco_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            choco_available = False
            
        if choco_available:
            tools = ["curl", "wget", "jq", "nmap", "tesseract"]
            for tool in tools:
                try:
                    result = subprocess.run([
                        "choco", "install", tool, "-y"
                    ], capture_output=True, text=True, timeout=120)
                    
                    if result.returncode == 0:
                        logger.info(f"✅ Installed {tool} via chocolatey")
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Installation of {tool} timed out")
                    
        else:
            logger.warning("⚠️ Chocolatey not found. Some tools may not be available.")
            
    def _install_macos_tools(self):
        """Install macOS-specific tools"""
        logger.info("🍎 Installing macOS tools...")
        
        # Check if homebrew is available
        try:
            subprocess.run(["brew", "--version"], capture_output=True, check=True)
            brew_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            brew_available = False
            
        if brew_available:
            tools = ["curl", "wget", "jq", "nmap", "whois", "tesseract", "poppler"]
            for tool in tools:
                try:
                    result = subprocess.run([
                        "brew", "install", tool
                    ], capture_output=True, text=True, timeout=120)
                    
                    if result.returncode == 0:
                        logger.info(f"✅ Installed {tool} via homebrew")
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"⚠️ Installation of {tool} timed out")
                    
        else:
            logger.warning("⚠️ Homebrew not found. Some tools may not be available.")
            
    def install_language_models(self):
        """Install language models for NLP tasks"""
        logger.info("🧠 Installing language models...")
        
        # Install spaCy models
        models = [
            "en_core_web_sm",
            "en_core_web_md", 
            "sv_core_news_sm"  # Swedish model
        ]
        
        for model in models:
            try:
                result = subprocess.run([
                    sys.executable, "-m", "spacy", "download", model
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info(f"✅ Installed spaCy model: {model}")
                else:
                    logger.warning(f"⚠️ Failed to install spaCy model {model}")
                    
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ spaCy model {model} installation timed out")
                
        # Download NLTK data
        try:
            import nltk
            nltk.download('punkt')
            nltk.download('stopwords')
            nltk.download('wordnet')
            nltk.download('averaged_perceptron_tagger')
            logger.info("✅ NLTK data downloaded")
        except Exception as e:
            logger.error(f"❌ Failed to download NLTK data: {str(e)}")
            
    def setup_configuration_files(self):
        """Create configuration files"""
        logger.info("⚙️ Setting up configuration files...")
        
        config_dir = self.project_root / "config"
        
        # Create main configuration
        main_config = {
            'system': {
                'name': 'Revolutionary Ultimate System v4.0',
                'version': '4.0.0',
                'debug': False,
                'max_concurrent_sessions': 100
            },
            'anti_bot': {
                'default_strategy': 'cloudscraper',
                'escalation_enabled': True
            },
            'content_extraction': {
                'default_method': 'hybrid',
                'quality_assessment': True
            },
            'url_discovery': {
                'engines': {
                    'katana': {'enabled': True, 'binary_path': str(self.tools_dir / "katana" / ("katana.exe" if self.system == "windows" else "katana"))},
                    'photon': {'enabled': True},
                    'sitemap': {'enabled': True},
                    'selenium': {'enabled': False}
                }
            },
            'proxy_management': {
                'enabled': True,
                'pool_size': 100
            },
            'osint_analytics': {
                'enabled': True,
                'threat_intelligence': {}
            },
            'domain_policies': {
                'default': {
                    'name': 'default',
                    'pattern': '*',
                    'anti_bot_level': 'medium',
                    'proxy_rotation': True
                }
            }
        }
        
        config_file = config_dir / "revolutionary-config.yml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(main_config, f, default_flow_style=False, indent=2)
            
        logger.info(f"✅ Main configuration created: {config_file}")
        
        # Create .env template
        env_template = """# Revolutionary Ultimate System v4.0 Configuration
# Copy this file to .env and fill in your API keys

# CAPTCHA Solving Services
TWOCAPTCHA_API_KEY=your_2captcha_api_key_here
ANTICAPTCHA_API_KEY=your_anticaptcha_api_key_here
NOPECHA_API_KEY=your_nopecha_api_key_here

# OSINT and Threat Intelligence APIs
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
SHODAN_API_KEY=your_shodan_api_key_here
CENSYS_API_ID=your_censys_api_id_here
CENSYS_API_SECRET=your_censys_api_secret_here
ABUSE_IP_API_KEY=your_abuseip_api_key_here

# AWS Credentials (for proxy rotation)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_DEFAULT_REGION=us-east-1

# Service Endpoints
FLARESOLVERR_ENDPOINT=http://localhost:8191/v1
TIKA_SERVER_URL=http://localhost:9998

# Database Configuration
DATABASE_URL=sqlite:///revolutionary_system.db
REDIS_URL=redis://localhost:6379/0

# Monitoring and Logging
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# System Configuration
REVOLUTIONARY_DEBUG=false
REVOLUTIONARY_MAX_WORKERS=10
"""
        
        env_file = self.project_root / ".env.template"
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
            
        logger.info(f"✅ Environment template created: {env_file}")
        
    def setup_docker_services(self):
        """Set up Docker services"""
        logger.info("🐳 Setting up Docker services...")
        
        # Check if Docker is available
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            docker_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            docker_available = False
            
        if not docker_available:
            logger.warning("⚠️ Docker not found. Skipping Docker services setup.")
            return
            
        # Start essential services
        services = [
            "flaresolverr/flaresolverr:latest",
            "apache/tika:latest-full",
            "redis:7-alpine"
        ]
        
        for service in services:
            try:
                # Pull image
                logger.info(f"📥 Pulling Docker image: {service}")
                subprocess.run([
                    "docker", "pull", service
                ], capture_output=True, timeout=300)
                
                logger.info(f"✅ Pulled: {service}")
                
            except subprocess.TimeoutExpired:
                logger.warning(f"⚠️ Timeout pulling {service}")
            except Exception as e:
                logger.error(f"❌ Failed to pull {service}: {str(e)}")
                
        logger.info("✅ Docker services setup complete")
        
    def create_startup_scripts(self):
        """Create startup scripts"""
        logger.info("📜 Creating startup scripts...")
        
        # Python startup script
        python_script = f'''#!/usr/bin/env python3
"""Revolutionary Ultimate System v4.0 - Startup Script"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from revolutionary_scraper.unified_revolutionary_system import UnifiedRevolutionarySystem

async def main():
    """Main startup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Revolutionary Ultimate System v4.0")
    parser.add_argument("urls", nargs="*", help="URLs to crawl")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--batch-file", help="File containing URLs to crawl")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["json", "yaml", "csv"], default="json", help="Output format")
    parser.add_argument("--concurrent", type=int, default=5, help="Concurrent requests")
    parser.add_argument("--intelligence", action="store_true", help="Enable intelligence gathering")
    parser.add_argument("--discovery", action="store_true", help="Enable URL discovery")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    # Load URLs
    urls = list(args.urls) if args.urls else []
    
    if args.batch_file:
        with open(args.batch_file, 'r') as f:
            batch_urls = [line.strip() for line in f if line.strip()]
            urls.extend(batch_urls)
            
    if not urls and not args.interactive:
        parser.print_help()
        return
        
    # Initialize system
    system = UnifiedRevolutionarySystem(args.config)
    
    try:
        await system.initialize_async()
        
        print("🚀 Revolutionary Ultimate System v4.0 Ready!")
        
        if args.interactive:
            # Interactive mode
            while True:
                try:
                    url = input("\\nEnter URL to crawl (or 'quit' to exit): ").strip()
                    if url.lower() in ['quit', 'exit', 'q']:
                        break
                        
                    if url:
                        result = await system.unified_crawl(url)
                        
                        if result.success:
                            print(f"✅ Success: {{result.url}}")
                            if result.content:
                                print(f"   Content: {{len(result.content.text) if result.content.text else 0}} chars")
                            if result.discovered_urls:
                                print(f"   Discovered: {{len(result.discovered_urls)}} URLs")
                        else:
                            print(f"❌ Failed: {{result.url}}")
                            for error in result.errors:
                                print(f"   Error: {{error}}")
                                
                except KeyboardInterrupt:
                    break
        else:
            # Batch mode
            policy_override = {{}}
            if args.intelligence:
                policy_override['intelligence_gathering'] = True
            if args.discovery:
                policy_override['url_discovery_enabled'] = True
                
            results = await system.batch_crawl(
                urls,
                max_concurrent=args.concurrent,
                policy_override=policy_override if policy_override else None
            )
            
            # Display results
            successful = [r for r in results if r.success]
            print(f"\\n✅ Crawl complete: {{len(successful)}}/{{len(results)}} successful")
            
            # Save results
            if args.output:
                output_data = []
                for result in results:
                    result_dict = {{
                        'url': result.url,
                        'success': result.success,
                        'status_code': result.status_code,
                        'content_length': len(result.content.text) if result.content and result.content.text else 0,
                        'quality_score': result.content.quality_score.overall_score if result.content and result.content.quality_score else None,
                        'discovered_urls': len(result.discovered_urls),
                        'errors': result.errors
                    }}
                    output_data.append(result_dict)
                    
                if args.format == "json":
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(output_data, f, indent=2)
                elif args.format == "yaml":
                    import yaml
                    with open(args.output, 'w') as f:
                        yaml.dump(output_data, f, indent=2)
                elif args.format == "csv":
                    import csv
                    with open(args.output, 'w', newline='') as f:
                        if output_data:
                            writer = csv.DictWriter(f, fieldnames=output_data[0].keys())
                            writer.writeheader()
                            writer.writerows(output_data)
                            
                print(f"💾 Results saved to: {{args.output}}")
                
    finally:
        await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
'''
        
        startup_file = self.project_root / "start_revolutionary.py"
        with open(startup_file, 'w', encoding='utf-8') as f:
            f.write(python_script)
            
        # Make executable on Unix systems
        if self.system != "windows":
            os.chmod(startup_file, 0o755)
            
        logger.info(f"✅ Python startup script created: {startup_file}")
        
        # PowerShell script for Windows
        if self.system == "windows":
            powershell_script = f'''# Revolutionary Ultimate System v4.0 - Windows Startup Script

param(
    [string[]]$Urls,
    [string]$Config,
    [string]$BatchFile,
    [string]$Output,
    [string]$Format = "json",
    [int]$Concurrent = 5,
    [switch]$Intelligence,
    [switch]$Discovery,
    [switch]$Interactive
)

Write-Host "🚀 Starting Revolutionary Ultimate System v4.0..." -ForegroundColor Green

# Build arguments
$args = @()
if ($Urls) {{ $args += $Urls }}
if ($Config) {{ $args += "--config"; $args += $Config }}
if ($BatchFile) {{ $args += "--batch-file"; $args += $BatchFile }}
if ($Output) {{ $args += "--output"; $args += $Output }}
if ($Format) {{ $args += "--format"; $args += $Format }}
if ($Concurrent) {{ $args += "--concurrent"; $args += $Concurrent }}
if ($Intelligence) {{ $args += "--intelligence" }}
if ($Discovery) {{ $args += "--discovery" }}
if ($Interactive) {{ $args += "--interactive" }}

# Run Python script
& python "{startup_file}" @args
'''
            
            ps_file = self.project_root / "start_revolutionary.ps1"
            with open(ps_file, 'w', encoding='utf-8') as f:
                f.write(powershell_script)
                
            logger.info(f"✅ PowerShell startup script created: {ps_file}")
            
        # Bash script for Unix systems
        else:
            bash_script = f'''#!/bin/bash
# Revolutionary Ultimate System v4.0 - Unix Startup Script

echo "🚀 Starting Revolutionary Ultimate System v4.0..."

# Run Python script with all arguments
python3 "{startup_file}" "$@"
'''
            
            bash_file = self.project_root / "start_revolutionary.sh"
            with open(bash_file, 'w', encoding='utf-8') as f:
                f.write(bash_script)
                
            os.chmod(bash_file, 0o755)
            logger.info(f"✅ Bash startup script created: {bash_file}")
            
    def run_system_tests(self):
        """Run basic system tests"""
        logger.info("🧪 Running system tests...")
        
        try:
            # Test basic imports
            test_imports = [
                "requests",
                "aiohttp", 
                "cloudscraper",
                "selenium",
                "playwright",
                "beautifulsoup4",
                "trafilatura",
                "spacy"
            ]
            
            for module in test_imports:
                try:
                    __import__(module.replace('-', '_'))
                    logger.info(f"✅ Import test passed: {module}")
                except ImportError as e:
                    logger.error(f"❌ Import test failed: {module} - {str(e)}")
                    
            # Test tools
            tool_tests = [
                (str(self.tools_dir / "katana" / ("katana.exe" if self.system == "windows" else "katana")), ["--version"]),
                ("python", ["-c", "import spacy; print('spaCy version:', spacy.__version__)"]),
            ]
            
            for tool, args in tool_tests:
                try:
                    result = subprocess.run([tool] + args, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        logger.info(f"✅ Tool test passed: {Path(tool).name}")
                    else:
                        logger.warning(f"⚠️ Tool test warning: {Path(tool).name}")
                except Exception as e:
                    logger.error(f"❌ Tool test failed: {Path(tool).name} - {str(e)}")
                    
            logger.info("✅ System tests completed")
            
        except Exception as e:
            logger.error(f"❌ System tests failed: {str(e)}")
            
    def print_completion_message(self):
        """Print setup completion message"""
        print("\n" + "="*80)
        print("🎉 REVOLUTIONARY ULTIMATE SYSTEM v4.0 SETUP COMPLETE! 🎉")
        print("="*80)
        print()
        print("📋 SYSTEM CAPABILITIES:")
        print("   ✅ Anti-bot defense with CloudFlare bypass")
        print("   ✅ Advanced content extraction and quality assessment")
        print("   ✅ Multi-engine URL discovery and deep crawling")
        print("   ✅ Enterprise proxy management with AWS rotation")
        print("   ✅ OSINT threat intelligence and security analysis")
        print("   ✅ Per-domain policy configuration")
        print()
        print("🚀 GETTING STARTED:")
        print("   1. Copy .env.template to .env and configure your API keys")
        print("   2. Start Docker services (optional): docker-compose up -d")
        print("   3. Run the system:")
        if self.system == "windows":
            print(f"      .\\start_revolutionary.ps1 --interactive")
        else:
            print(f"      ./start_revolutionary.sh --interactive")
        print()
        print("📖 EXAMPLES:")
        print("   # Interactive mode")
        if self.system == "windows":
            print("   .\\start_revolutionary.ps1 --interactive")
            print("   # Single URL with intelligence")
            print("   .\\start_revolutionary.ps1 https://example.com --intelligence --discovery")
            print("   # Batch crawling")
            print("   .\\start_revolutionary.ps1 --batch-file urls.txt --output results.json")
        else:
            print("   ./start_revolutionary.sh --interactive")
            print("   # Single URL with intelligence")
            print("   ./start_revolutionary.sh https://example.com --intelligence --discovery")
            print("   # Batch crawling")
            print("   ./start_revolutionary.sh --batch-file urls.txt --output results.json")
        print()
        print("📁 PROJECT STRUCTURE:")
        print("   config/          - Configuration files")
        print("   tools/           - External tools (Katana, etc.)")
        print("   data/            - Data storage")
        print("   logs/            - System logs")
        print("   output/          - Crawling results")
        print("   cache/           - System cache")
        print()
        print("🔧 CONFIGURATION:")
        print(f"   Main config:     {self.project_root}/config/revolutionary-config.yml")
        print(f"   Environment:     {self.project_root}/.env (create from .env.template)")
        print()
        print("Happy Crawling! 🕷️✨")
        print("="*80)
        
    def run_setup(self):
        """Run complete system setup"""
        start_time = time.time()
        
        try:
            # Setup steps
            steps = [
                ("Checking Python version", self.check_python_version),
                ("Setting up directories", self.setup_directories),
                ("Installing Python packages", self.install_python_packages),
                ("Installing system tools", self.install_system_tools),
                ("Installing language models", self.install_language_models),
                ("Setting up configuration files", self.setup_configuration_files),
                ("Setting up Docker services", self.setup_docker_services),
                ("Creating startup scripts", self.create_startup_scripts),
                ("Running system tests", self.run_system_tests)
            ]
            
            for i, (description, step_func) in enumerate(steps, 1):
                logger.info(f"[{i}/{len(steps)}] {description}...")
                try:
                    step_func()
                    logger.info(f"✅ [{i}/{len(steps)}] {description} completed")
                except Exception as e:
                    logger.error(f"❌ [{i}/{len(steps)}] {description} failed: {str(e)}")
                    # Continue with other steps
                    
            setup_time = time.time() - start_time
            logger.info(f"⏱️ Total setup time: {setup_time:.1f} seconds")
            
            # Print completion message
            self.print_completion_message()
            
        except KeyboardInterrupt:
            logger.info("\n🛑 Setup interrupted by user")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Setup failed: {str(e)}")
            sys.exit(1)

def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Revolutionary Ultimate System v4.0 Setup")
    parser.add_argument("--skip-packages", action="store_true", help="Skip Python package installation")
    parser.add_argument("--skip-tools", action="store_true", help="Skip system tools installation")
    parser.add_argument("--skip-docker", action="store_true", help="Skip Docker services setup")
    parser.add_argument("--skip-tests", action="store_true", help="Skip system tests")
    parser.add_argument("--config-only", action="store_true", help="Only create configuration files")
    
    args = parser.parse_args()
    
    setup = SystemSetup()
    
    if args.config_only:
        setup.setup_directories()
        setup.setup_configuration_files()
        setup.create_startup_scripts()
        print("✅ Configuration setup complete!")
        return
        
    # Skip certain steps based on arguments
    if args.skip_packages:
        setup.install_python_packages = lambda: logger.info("⏭️ Skipping Python packages")
    if args.skip_tools:
        setup.install_system_tools = lambda: logger.info("⏭️ Skipping system tools")
    if args.skip_docker:
        setup.setup_docker_services = lambda: logger.info("⏭️ Skipping Docker services")
    if args.skip_tests:
        setup.run_system_tests = lambda: logger.info("⏭️ Skipping system tests")
        
    setup.run_setup()

if __name__ == "__main__":
    main()
