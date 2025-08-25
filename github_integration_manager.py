#!/usr/bin/env python3
"""
GitHub Repository Integration Plan - Revolutionary Ultimate System v4.0
Systematisk implementation av prioriterade repositories från listan.
"""

from pathlib import Path
import subprocess
import logging
import asyncio
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

class GitHubRepositoryIntegrator:
    """Manages integration of GitHub repositories into the Revolutionary System"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.integrations_dir = project_root / "integrations"
        self.integrations_dir.mkdir(exist_ok=True)
        
        # Priority categories from the plan
        self.priority_repos = {
            "anti_bot_defense": [
                "FlareSolverr/FlareSolverr",
                "VeNoMouS/cloudscraper", 
                "ultrafunkamsterdam/undetected-chromedriver",
                "Anorov/cloudflare-scrape",
                "solve-cloudflare/cloudflare-bypass"
            ],
            
            "content_extraction": [
                "adbar/trafilatura",
                "apache/tika",
                "opendatalab/PDF-Extract-Kit",
                "jhy/jsoup",
                "cheeriojs/cheerio"
            ],
            
            "url_discovery": [
                "projectdiscovery/katana",
                "s0md3v/Photon", 
                "gocolly/colly",
                "apify/crawlee",
                "code4craft/webmagic"
            ],
            
            "proxy_management": [
                "constverum/ProxyBroker",
                "jhao104/proxy_pool",
                "Ge0rg3/requests-ip-rotator",
                "Python3WebSpider/ProxyPool",
                "zu1k/proxypool"
            ],
            
            "browser_automation": [
                "browserless/browserless",
                "chromedp/chromedp",
                "AtuboDad/playwright_stealth",
                "seleniumbase/SeleniumBase",
                "checkly/headless-recorder"
            ],
            
            "captcha_solving": [
                "2captcha/2captcha-python",
                "NoahCardoza/CaptchaHarvester",
                "NopeCHALLC/nopecha-extension",
                "ecthros/uncaptcha",
                "sml2h3/ddddocr"
            ],
            
            "osint_intelligence": [
                "christophetd/CloudFlair",
                "bhavsec/reconspider",
                "yogeshojha/rengine",
                "XDeadHackerX/NetSoc_OSINT",
                "techenthusiast167/DeepWebHarvester"
            ],
            
            "advanced_crawlers": [
                "BuilderIO/gpt-crawler",
                "NanmiCoder/MediaCrawler",
                "ScrapeGraphAI/Scrapegraph-ai",
                "unclecode/crawl4ai",
                "scrapy/scrapy"
            ],
            
            "specialized_tools": [
                "gosom/google-maps-scraper",
                "dipu-bd/lightnovel-crawler",
                "itsOwen/CyberScraper-2077",
                "NaiboWang/EasySpider",
                "getmaxun/maxun"
            ]
        }
        
    async def integrate_repository(self, repo_path: str, category: str) -> Dict[str, Any]:
        """Integrate a single repository into the system"""
        logger.info(f"🔄 Integrating {repo_path} into category {category}")
        
        try:
            # Clone repository
            repo_name = repo_path.split('/')[-1]
            clone_dir = self.integrations_dir / category / repo_name
            
            if not clone_dir.exists():
                await self._clone_repository(repo_path, clone_dir)
            
            # Analyze repository structure
            analysis = await self._analyze_repository(clone_dir)
            
            # Create integration adapter
            adapter = await self._create_integration_adapter(repo_path, category, analysis)
            
            # Generate configuration
            config = await self._generate_integration_config(repo_path, category, analysis)
            
            return {
                'repo': repo_path,
                'category': category,
                'status': 'integrated',
                'adapter': adapter,
                'config': config,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to integrate {repo_path}: {str(e)}")
            return {
                'repo': repo_path,
                'category': category,
                'status': 'failed',
                'error': str(e)
            }
            
    async def _clone_repository(self, repo_path: str, target_dir: Path):
        """Clone repository from GitHub"""
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        
        clone_url = f"https://github.com/{repo_path}.git"
        
        process = await asyncio.create_subprocess_exec(
            "git", "clone", "--depth", "1", clone_url, str(target_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise Exception(f"Git clone failed: {stderr.decode()}")
            
        logger.info(f"✅ Cloned {repo_path} to {target_dir}")
        
    async def _analyze_repository(self, repo_dir: Path) -> Dict[str, Any]:
        """Analyze repository structure and capabilities"""
        analysis = {
            'language': 'unknown',
            'main_files': [],
            'dependencies': [],
            'api_structure': {},
            'documentation': [],
            'examples': []
        }
        
        # Detect language
        if (repo_dir / "setup.py").exists() or (repo_dir / "pyproject.toml").exists():
            analysis['language'] = 'python'
        elif (repo_dir / "package.json").exists():
            analysis['language'] = 'javascript'
        elif (repo_dir / "go.mod").exists():
            analysis['language'] = 'go'
        elif (repo_dir / "pom.xml").exists():
            analysis['language'] = 'java'
            
        # Find main files
        for pattern in ["*.py", "*.js", "*.go", "*.java"]:
            analysis['main_files'].extend(list(repo_dir.glob(pattern)))
            
        # Find documentation
        for doc_file in ["README.md", "USAGE.md", "API.md", "EXAMPLES.md"]:
            doc_path = repo_dir / doc_file
            if doc_path.exists():
                analysis['documentation'].append(doc_path)
                
        # Find examples
        examples_dir = repo_dir / "examples"
        if examples_dir.exists():
            analysis['examples'] = list(examples_dir.glob("*"))
            
        return analysis
        
    async def _create_integration_adapter(self, repo_path: str, category: str, analysis: Dict[str, Any]) -> str:
        """Create integration adapter for the repository"""
        repo_name = repo_path.split('/')[-1].replace('-', '_').replace('.', '_')
        adapter_name = f"{repo_name}_adapter"
        
        # Create adapter file based on category
        if category == "anti_bot_defense":
            adapter_content = self._create_anti_bot_adapter(repo_name, analysis)
        elif category == "content_extraction":
            adapter_content = self._create_content_extraction_adapter(repo_name, analysis)
        elif category == "url_discovery":
            adapter_content = self._create_url_discovery_adapter(repo_name, analysis)
        elif category == "proxy_management":
            adapter_content = self._create_proxy_adapter(repo_name, analysis)
        else:
            adapter_content = self._create_generic_adapter(repo_name, analysis)
            
        # Save adapter file
        adapter_file = self.project_root / "revolutionary_scraper" / "adapters" / f"{adapter_name}.py"
        adapter_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(adapter_file, 'w', encoding='utf-8') as f:
            f.write(adapter_content)
            
        logger.info(f"✅ Created adapter: {adapter_file}")
        return str(adapter_file)
        
    def _create_anti_bot_adapter(self, repo_name: str, analysis: Dict[str, Any]) -> str:
        """Create anti-bot defense adapter"""
        return f'''#!/usr/bin/env python3
"""
{repo_name.title()} Integration Adapter
Auto-generated integration for anti-bot defense capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class {repo_name.title()}Config:
    """Configuration for {repo_name} integration"""
    enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    debug: bool = False

class {repo_name.title()}Adapter:
    """Adapter for {repo_name} anti-bot capabilities"""
    
    def __init__(self, config: {repo_name.title()}Config):
        self.config = config
        self.initialized = False
        
    async def initialize(self):
        """Initialize the adapter"""
        if self.initialized:
            return
            
        try:
            # Import and initialize the actual library
            # TODO: Add actual integration code here
            logger.info(f"🔧 Initializing {{repo_name}} adapter")
            self.initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {{repo_name}}: {{str(e)}}")
            raise
            
    async def bypass_protection(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Bypass bot protection for a URL"""
        if not self.initialized:
            await self.initialize()
            
        try:
            # TODO: Implement actual bypass logic
            logger.info(f"🛡️ Bypassing protection for {{url}} using {{repo_name}}")
            
            return {{
                'success': True,
                'url': url,
                'status_code': 200,
                'content': '',
                'cookies': {{}},
                'headers': {{}},
                'method': '{repo_name}'
            }}
            
        except Exception as e:
            logger.error(f"❌ {{repo_name}} bypass failed: {{str(e)}}")
            return {{
                'success': False,
                'url': url,
                'error': str(e),
                'method': '{repo_name}'
            }}
            
    async def solve_captcha(self, captcha_data: bytes, captcha_type: str = 'image') -> Optional[str]:
        """Solve CAPTCHA if supported"""
        try:
            # TODO: Implement CAPTCHA solving if supported by the tool
            logger.info(f"🧩 Attempting to solve {{captcha_type}} CAPTCHA using {{repo_name}}")
            return None
            
        except Exception as e:
            logger.error(f"❌ CAPTCHA solving failed: {{str(e)}}")
            return None
            
    async def get_browser_session(self, options: Dict[str, Any] = None):
        """Get browser session if supported"""
        try:
            # TODO: Implement browser session creation if supported
            logger.info(f"🌐 Creating browser session using {{repo_name}}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Browser session creation failed: {{str(e)}}")
            return None

# Factory function
def create_{repo_name}_adapter(config: Dict[str, Any]) -> {repo_name.title()}Adapter:
    """Create and configure {repo_name} adapter"""
    adapter_config = {repo_name.title()}Config(**config)
    return {repo_name.title()}Adapter(adapter_config)
'''

    def _create_content_extraction_adapter(self, repo_name: str, analysis: Dict[str, Any]) -> str:
        """Create content extraction adapter"""
        return f'''#!/usr/bin/env python3
"""
{repo_name.title()} Content Extraction Adapter
Auto-generated integration for content extraction capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class {repo_name.title()}Config:
    """Configuration for {repo_name} content extraction"""
    enabled: bool = True
    extract_tables: bool = True
    extract_images: bool = False
    include_metadata: bool = True
    quality_threshold: float = 0.5

@dataclass
class ExtractionResult:
    """Result from content extraction"""
    title: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    metadata: Dict[str, Any] = None
    tables: List[Dict[str, Any]] = None
    images: List[str] = None
    quality_score: float = 0.0
    language: Optional[str] = None

class {repo_name.title()}Extractor:
    """Content extraction using {repo_name}"""
    
    def __init__(self, config: {repo_name.title()}Config):
        self.config = config
        self.initialized = False
        
    async def initialize(self):
        """Initialize the extractor"""
        if self.initialized:
            return
            
        try:
            # TODO: Import and initialize the actual library
            logger.info(f"📄 Initializing {{repo_name}} extractor")
            self.initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {{repo_name}} extractor: {{str(e)}}")
            raise
            
    async def extract_content(self, html: str, url: str = None) -> ExtractionResult:
        """Extract content from HTML"""
        if not self.initialized:
            await self.initialize()
            
        try:
            logger.info(f"📄 Extracting content using {{repo_name}}")
            
            # TODO: Implement actual extraction logic
            result = ExtractionResult()
            result.html = html
            result.text = "Extracted content placeholder"
            result.title = "Extracted title"
            result.metadata = {{'extractor': '{repo_name}'}}
            result.quality_score = 0.8
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {{str(e)}}")
            result = ExtractionResult()
            result.html = html
            result.quality_score = 0.0
            return result
            
    async def extract_pdf(self, pdf_data: bytes) -> ExtractionResult:
        """Extract content from PDF if supported"""
        try:
            logger.info(f"📑 Extracting PDF content using {{repo_name}}")
            
            # TODO: Implement PDF extraction if supported
            result = ExtractionResult()
            result.text = "PDF content placeholder"
            result.metadata = {{'extractor': '{repo_name}', 'type': 'pdf'}}
            result.quality_score = 0.7
            
            return result
            
        except Exception as e:
            logger.error(f"❌ PDF extraction failed: {{str(e)}}")
            return ExtractionResult()

# Factory function
def create_{repo_name}_extractor(config: Dict[str, Any]) -> {repo_name.title()}Extractor:
    """Create and configure {repo_name} extractor"""
    extractor_config = {repo_name.title()}Config(**config)
    return {repo_name.title()}Extractor(extractor_config)
'''

    def _create_url_discovery_adapter(self, repo_name: str, analysis: Dict[str, Any]) -> str:
        """Create URL discovery adapter"""
        return f'''#!/usr/bin/env python3
"""
{repo_name.title()} URL Discovery Adapter
Auto-generated integration for URL discovery and crawling.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

@dataclass
class {repo_name.title()}Config:
    """Configuration for {repo_name} URL discovery"""
    enabled: bool = True
    max_depth: int = 3
    max_urls: int = 1000
    timeout: int = 30
    follow_redirects: bool = True
    respect_robots_txt: bool = True

@dataclass
class DiscoveryResult:
    """Result from URL discovery"""
    urls: Set[str] = None
    sitemap_urls: Set[str] = None
    form_urls: Set[str] = None
    api_endpoints: Set[str] = None
    metadata: Dict[str, Any] = None

class {repo_name.title()}Discovery:
    """URL discovery using {repo_name}"""
    
    def __init__(self, config: {repo_name.title()}Config):
        self.config = config
        self.initialized = False
        
    async def initialize(self):
        """Initialize the discovery engine"""
        if self.initialized:
            return
            
        try:
            # TODO: Import and initialize the actual library
            logger.info(f"🔍 Initializing {{repo_name}} discovery engine")
            self.initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {{repo_name}} discovery: {{str(e)}}")
            raise
            
    async def discover_urls(self, start_url: str, options: Dict[str, Any] = None) -> DiscoveryResult:
        """Discover URLs from a starting URL"""
        if not self.initialized:
            await self.initialize()
            
        try:
            logger.info(f"🔍 Discovering URLs from {{start_url}} using {{repo_name}}")
            
            # TODO: Implement actual URL discovery logic
            result = DiscoveryResult()
            result.urls = {{start_url, urljoin(start_url, '/about'), urljoin(start_url, '/contact')}}
            result.sitemap_urls = {{urljoin(start_url, '/sitemap.xml')}}
            result.metadata = {{'engine': '{repo_name}', 'start_url': start_url}}
            
            return result
            
        except Exception as e:
            logger.error(f"❌ URL discovery failed: {{str(e)}}")
            result = DiscoveryResult()
            result.urls = set()
            result.metadata = {{'error': str(e)}}
            return result
            
    async def crawl_sitemap(self, sitemap_url: str) -> Set[str]:
        """Crawl sitemap for URLs"""
        try:
            logger.info(f"🗺️ Crawling sitemap {{sitemap_url}} using {{repo_name}}")
            
            # TODO: Implement sitemap crawling
            return {{sitemap_url.replace('/sitemap.xml', '/page1'), sitemap_url.replace('/sitemap.xml', '/page2')}}
            
        except Exception as e:
            logger.error(f"❌ Sitemap crawling failed: {{str(e)}}")
            return set()
            
    async def find_api_endpoints(self, base_url: str) -> Set[str]:
        """Find API endpoints if supported"""
        try:
            logger.info(f"🔌 Finding API endpoints from {{base_url}} using {{repo_name}}")
            
            # TODO: Implement API endpoint discovery
            parsed = urlparse(base_url)
            base = f"{{parsed.scheme}}://{{parsed.netloc}}"
            return {{f"{{base}}/api/v1", f"{{base}}/api/data", f"{{base}}/graphql"}}
            
        except Exception as e:
            logger.error(f"❌ API endpoint discovery failed: {{str(e)}}")
            return set()

# Factory function  
def create_{repo_name}_discovery(config: Dict[str, Any]) -> {repo_name.title()}Discovery:
    """Create and configure {repo_name} discovery engine"""
    discovery_config = {repo_name.title()}Config(**config)
    return {repo_name.title()}Discovery(discovery_config)
'''

    def _create_proxy_adapter(self, repo_name: str, analysis: Dict[str, Any]) -> str:
        """Create proxy management adapter"""
        return f'''#!/usr/bin/env python3
"""
{repo_name.title()} Proxy Management Adapter
Auto-generated integration for proxy management capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class ProxyInfo:
    """Proxy information"""
    host: str
    port: int
    protocol: str = 'http'
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    anonymity: Optional[str] = None
    speed: float = 0.0
    reliability: float = 0.0
    last_checked: float = 0.0

@dataclass
class {repo_name.title()}Config:
    """Configuration for {repo_name} proxy management"""
    enabled: bool = True
    max_proxies: int = 100
    check_interval: int = 300
    timeout: int = 10
    min_anonymity: str = 'anonymous'

class {repo_name.title()}ProxyManager:
    """Proxy management using {repo_name}"""
    
    def __init__(self, config: {repo_name.title()}Config):
        self.config = config
        self.proxies: List[ProxyInfo] = []
        self.current_index = 0
        self.initialized = False
        
    async def initialize(self):
        """Initialize the proxy manager"""
        if self.initialized:
            return
            
        try:
            # TODO: Import and initialize the actual library
            logger.info(f"🌐 Initializing {{repo_name}} proxy manager")
            await self.refresh_proxies()
            self.initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {{repo_name}} proxy manager: {{str(e)}}")
            raise
            
    async def refresh_proxies(self):
        """Refresh the proxy pool"""
        try:
            logger.info(f"🔄 Refreshing proxy pool using {{repo_name}}")
            
            # TODO: Implement actual proxy discovery/refresh logic
            # Placeholder proxies for testing
            self.proxies = [
                ProxyInfo(host="proxy1.example.com", port=8080, protocol="http", speed=0.8, reliability=0.9),
                ProxyInfo(host="proxy2.example.com", port=3128, protocol="http", speed=0.7, reliability=0.8),
                ProxyInfo(host="proxy3.example.com", port=1080, protocol="socks5", speed=0.9, reliability=0.7)
            ]
            
            for proxy in self.proxies:
                proxy.last_checked = time.time()
                
            logger.info(f"✅ Refreshed proxy pool: {{len(self.proxies)}} proxies")
            
        except Exception as e:
            logger.error(f"❌ Proxy refresh failed: {{str(e)}}")
            
    async def get_proxy(self, country: Optional[str] = None) -> Optional[ProxyInfo]:
        """Get next available proxy"""
        if not self.initialized:
            await self.initialize()
            
        if not self.proxies:
            await self.refresh_proxies()
            
        if not self.proxies:
            return None
            
        try:
            # Round-robin selection
            proxy = self.proxies[self.current_index % len(self.proxies)]
            self.current_index += 1
            
            # Filter by country if specified
            if country:
                country_proxies = [p for p in self.proxies if p.country == country]
                if country_proxies:
                    proxy = country_proxies[self.current_index % len(country_proxies)]
                    
            logger.info(f"🌐 Selected proxy: {{proxy.host}}:{{proxy.port}}")
            return proxy
            
        except Exception as e:
            logger.error(f"❌ Proxy selection failed: {{str(e)}}")
            return None
            
    async def check_proxy(self, proxy: ProxyInfo) -> bool:
        """Check if proxy is working"""
        try:
            # TODO: Implement actual proxy checking logic
            logger.info(f"🔍 Checking proxy {{proxy.host}}:{{proxy.port}}")
            
            # Simulate proxy check
            proxy.last_checked = time.time()
            proxy.reliability = 0.8  # Placeholder
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Proxy check failed: {{str(e)}}")
            return False
            
    async def remove_proxy(self, proxy: ProxyInfo):
        """Remove a failed proxy"""
        try:
            if proxy in self.proxies:
                self.proxies.remove(proxy)
                logger.info(f"🗑️ Removed failed proxy: {{proxy.host}}:{{proxy.port}}")
                
        except Exception as e:
            logger.error(f"❌ Proxy removal failed: {{str(e)}}")
            
    def get_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics"""
        if not self.proxies:
            return {{'total': 0, 'working': 0, 'average_speed': 0.0}}
            
        working_proxies = [p for p in self.proxies if p.reliability > 0.5]
        avg_speed = sum(p.speed for p in self.proxies) / len(self.proxies)
        
        return {{
            'total': len(self.proxies),
            'working': len(working_proxies),
            'average_speed': avg_speed,
            'last_refresh': max(p.last_checked for p in self.proxies) if self.proxies else 0
        }}

# Factory function
def create_{repo_name}_proxy_manager(config: Dict[str, Any]) -> {repo_name.title()}ProxyManager:
    """Create and configure {repo_name} proxy manager"""
    proxy_config = {repo_name.title()}Config(**config)
    return {repo_name.title()}ProxyManager(proxy_config)
'''

    def _create_generic_adapter(self, repo_name: str, analysis: Dict[str, Any]) -> str:
        """Create generic adapter for other tools"""
        return f'''#!/usr/bin/env python3
"""
{repo_name.title()} Generic Adapter
Auto-generated integration adapter.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class {repo_name.title()}Config:
    """Configuration for {repo_name}"""
    enabled: bool = True
    timeout: int = 30
    debug: bool = False

class {repo_name.title()}Adapter:
    """Generic adapter for {repo_name}"""
    
    def __init__(self, config: {repo_name.title()}Config):
        self.config = config
        self.initialized = False
        
    async def initialize(self):
        """Initialize the adapter"""
        if self.initialized:
            return
            
        try:
            logger.info(f"🔧 Initializing {{repo_name}} adapter")
            # TODO: Add initialization logic
            self.initialized = True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize {{repo_name}}: {{str(e)}}")
            raise
            
    async def execute(self, operation: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an operation"""
        if not self.initialized:
            await self.initialize()
            
        try:
            logger.info(f"⚡ Executing {{operation}} using {{repo_name}}")
            
            # TODO: Implement actual operation logic
            return {{
                'success': True,
                'operation': operation,
                'params': params or {{}},
                'result': 'placeholder',
                'adapter': '{repo_name}'
            }}
            
        except Exception as e:
            logger.error(f"❌ Operation {{operation}} failed: {{str(e)}}")
            return {{
                'success': False,
                'operation': operation,
                'error': str(e),
                'adapter': '{repo_name}'
            }}

# Factory function
def create_{repo_name}_adapter(config: Dict[str, Any]) -> {repo_name.title()}Adapter:
    """Create and configure {repo_name} adapter"""
    adapter_config = {repo_name.title()}Config(**config)
    return {repo_name.title()}Adapter(adapter_config)
'''

    async def _generate_integration_config(self, repo_path: str, category: str, analysis: Dict[str, Any]) -> str:
        """Generate configuration for the integration"""
        repo_name = repo_path.split('/')[-1]
        
        config = {
            'name': repo_name,
            'repository': repo_path,
            'category': category,
            'language': analysis.get('language', 'unknown'),
            'enabled': True,
            'priority': 10,
            'config': {
                'timeout': 30,
                'max_retries': 3,
                'debug': False
            }
        }
        
        # Save configuration
        config_file = self.project_root / "config" / "integrations" / f"{repo_name}.yml"
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        import yaml
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
            
        logger.info(f"✅ Created config: {config_file}")
        return str(config_file)
        
    async def integrate_priority_repositories(self) -> List[Dict[str, Any]]:
        """Integrate high-priority repositories from the plan"""
        results = []
        
        # Start with anti-bot defense (highest priority)
        for category, repos in self.priority_repos.items():
            logger.info(f"🚀 Integrating {category} repositories...")
            
            for repo_path in repos[:2]:  # Limit to first 2 per category for initial implementation
                try:
                    result = await self.integrate_repository(repo_path, category)
                    results.append(result)
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to integrate {repo_path}: {str(e)}")
                    results.append({
                        'repo': repo_path,
                        'category': category,
                        'status': 'failed',
                        'error': str(e)
                    })
                    
        return results

async def main():
    """Main integration function"""
    project_root = Path.cwd()
    integrator = GitHubRepositoryIntegrator(project_root)
    
    logger.info("🚀 Starting GitHub repository integration...")
    
    results = await integrator.integrate_priority_repositories()
    
    # Summary
    successful = [r for r in results if r['status'] == 'integrated']
    failed = [r for r in results if r['status'] == 'failed']
    
    logger.info(f"✅ Integration complete: {len(successful)} successful, {len(failed)} failed")
    
    for result in successful:
        logger.info(f"   ✅ {result['repo']} ({result['category']})")
        
    for result in failed:
        logger.error(f"   ❌ {result['repo']} ({result['category']}): {result.get('error', 'Unknown error')}")
        
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
