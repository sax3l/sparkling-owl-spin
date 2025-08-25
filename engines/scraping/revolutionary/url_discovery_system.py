#!/usr/bin/env python3
"""
Revolutionary URL Discovery System v4.0
Advanced URL discovery and deep crawling capabilities using multiple engines.

Integrates:
- ProjectDiscovery Katana (CLI crawler for automation pipelines)
- Photon (OSINT-style asset discovery) 
- Colly-style link extraction
- Sitemap parsing and robots.txt respect
- Deep crawling with infinite scroll support
"""

import asyncio
import logging
import subprocess
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from urllib.parse import urljoin, urlparse, parse_qs
import aiohttp
import yaml
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

@dataclass
class URLDiscoveryResult:
    """Result from URL discovery operation"""
    urls: Set[str] = field(default_factory=set)
    depth: int = 0
    discovery_method: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamps: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

@dataclass
class CrawlPolicy:
    """Policy configuration for URL discovery"""
    max_depth: int = 3
    max_urls_per_domain: int = 1000
    respect_robots_txt: bool = True
    follow_redirects: bool = True
    extract_forms: bool = True
    extract_api_endpoints: bool = True
    extract_js_urls: bool = True
    infinite_scroll: bool = False
    custom_selectors: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=list)
    discovery_engines: List[str] = field(default_factory=lambda: ['beautifulsoup', 'selenium'])

class KatanaIntegration:
    """Integration with ProjectDiscovery Katana CLI crawler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.katana_path = config.get('katana_path', 'katana')
        self.timeout = config.get('timeout', 300)
        
    async def discover_urls(self, target_url: str, policy: CrawlPolicy) -> URLDiscoveryResult:
        """Use Katana for URL discovery"""
        result = URLDiscoveryResult()
        result.discovery_method = "katana"
        
        try:
            # Build katana command
            cmd = [
                self.katana_path,
                '-u', target_url,
                '-d', str(policy.max_depth),
                '-jc',  # JavaScript crawling
                '-duc',  # Disable unique condition
                '-silent',
                '-jsonl'  # Output in JSONL format
            ]
            
            # Add headless mode if configured
            if self.config.get('headless', True):
                cmd.append('-headless')
                
            # Add custom headers if configured
            if 'headers' in self.config:
                for header in self.config['headers']:
                    cmd.extend(['-H', header])
                    
            # Add rate limiting
            if 'rate_limit' in self.config:
                cmd.extend(['-rl', str(self.config['rate_limit'])])
                
            logger.info(f"Running Katana with command: {' '.join(cmd)}")
            
            # Run Katana process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout
            )
            
            if process.returncode == 0:
                # Parse JSONL output
                for line in stdout.decode().strip().split('\n'):
                    if line:
                        try:
                            data = json.loads(line)
                            if 'url' in data:
                                result.urls.add(data['url'])
                                
                            # Extract metadata
                            if 'status_code' in data:
                                result.metadata.setdefault('status_codes', {})[data['url']] = data['status_code']
                                
                        except json.JSONDecodeError as e:
                            logger.warning(f"Failed to parse Katana output line: {line}")
                            
                logger.info(f"Katana discovered {len(result.urls)} URLs")
                
            else:
                error_msg = stderr.decode() if stderr else "Unknown Katana error"
                logger.error(f"Katana failed with return code {process.returncode}: {error_msg}")
                result.errors.append(f"Katana error: {error_msg}")
                
        except asyncio.TimeoutError:
            logger.error(f"Katana timed out after {self.timeout} seconds")
            result.errors.append(f"Katana timeout ({self.timeout}s)")
        except Exception as e:
            logger.error(f"Katana execution failed: {str(e)}")
            result.errors.append(f"Katana exception: {str(e)}")
            
        return result

class PhotonIntegration:
    """Integration with Photon OSINT crawler"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.photon_path = config.get('photon_path', 'photon')
        self.timeout = config.get('timeout', 300)
        
    async def discover_urls(self, target_url: str, policy: CrawlPolicy) -> URLDiscoveryResult:
        """Use Photon for OSINT-style URL discovery"""
        result = URLDiscoveryResult()
        result.discovery_method = "photon"
        
        try:
            # Parse domain from URL
            parsed = urlparse(target_url)
            domain = parsed.netloc
            
            # Build photon command
            cmd = [
                'python3',
                self.photon_path,
                '-u', target_url,
                '-l', str(policy.max_depth),
                '--wayback',  # Use Wayback Machine
                '--dns',      # DNS enumeration
                '--export', 'json'
            ]
            
            # Add output directory
            output_dir = f"/tmp/photon_{domain}"
            cmd.extend(['-o', output_dir])
            
            logger.info(f"Running Photon with command: {' '.join(cmd)}")
            
            # Run Photon process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=self.timeout
            )
            
            if process.returncode == 0:
                # Read results from output files
                output_path = Path(output_dir)
                
                # Read URLs from various files
                for file_name in ['internal.txt', 'external.txt', 'fuzzable.txt']:
                    file_path = output_path / domain / file_name
                    if file_path.exists():
                        with open(file_path, 'r') as f:
                            for line in f:
                                url = line.strip()
                                if url:
                                    result.urls.add(url)
                                    
                # Read API endpoints if available
                api_file = output_path / domain / 'endpoints.txt'
                if api_file.exists():
                    result.metadata['api_endpoints'] = []
                    with open(api_file, 'r') as f:
                        for line in f:
                            endpoint = line.strip()
                            if endpoint:
                                result.metadata['api_endpoints'].append(endpoint)
                                result.urls.add(urljoin(target_url, endpoint))
                                
                logger.info(f"Photon discovered {len(result.urls)} URLs")
                
            else:
                error_msg = stderr.decode() if stderr else "Unknown Photon error"
                logger.error(f"Photon failed with return code {process.returncode}: {error_msg}")
                result.errors.append(f"Photon error: {error_msg}")
                
        except asyncio.TimeoutError:
            logger.error(f"Photon timed out after {self.timeout} seconds")
            result.errors.append(f"Photon timeout ({self.timeout}s)")
        except Exception as e:
            logger.error(f"Photon execution failed: {str(e)}")
            result.errors.append(f"Photon exception: {str(e)}")
            
        return result

class SitemapParser:
    """Parser for robots.txt and sitemap.xml files"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        
    async def discover_urls(self, target_url: str, policy: CrawlPolicy) -> URLDiscoveryResult:
        """Discover URLs from robots.txt and sitemaps"""
        result = URLDiscoveryResult()
        result.discovery_method = "sitemap"
        
        try:
            parsed = urlparse(target_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Parse robots.txt
            if policy.respect_robots_txt:
                await self._parse_robots_txt(base_url, result)
                
            # Parse sitemap.xml
            await self._parse_sitemap(base_url, result)
            
            logger.info(f"Sitemap parser discovered {len(result.urls)} URLs")
            
        except Exception as e:
            logger.error(f"Sitemap parsing failed: {str(e)}")
            result.errors.append(f"Sitemap error: {str(e)}")
            
        return result
    
    async def _parse_robots_txt(self, base_url: str, result: URLDiscoveryResult):
        """Parse robots.txt file"""
        try:
            robots_url = urljoin(base_url, '/robots.txt')
            response = self.session.get(robots_url, timeout=10)
            
            if response.status_code == 200:
                sitemaps = []
                disallowed = []
                
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line.lower().startswith('sitemap:'):
                        sitemap_url = line.split(':', 1)[1].strip()
                        sitemaps.append(sitemap_url)
                    elif line.lower().startswith('disallow:'):
                        path = line.split(':', 1)[1].strip()
                        if path and path != '/':
                            disallowed.append(path)
                            
                result.metadata['robots_txt'] = {
                    'sitemaps': sitemaps,
                    'disallowed': disallowed
                }
                
                # Add sitemap URLs for parsing
                for sitemap_url in sitemaps:
                    result.urls.add(sitemap_url)
                    
        except Exception as e:
            logger.warning(f"Failed to parse robots.txt: {str(e)}")
    
    async def _parse_sitemap(self, base_url: str, result: URLDiscoveryResult):
        """Parse sitemap.xml files"""
        try:
            sitemap_urls = [
                urljoin(base_url, '/sitemap.xml'),
                urljoin(base_url, '/sitemap_index.xml'),
                urljoin(base_url, '/sitemap.xml.gz')
            ]
            
            # Add sitemaps from robots.txt if available
            if 'robots_txt' in result.metadata:
                sitemap_urls.extend(result.metadata['robots_txt']['sitemaps'])
                
            for sitemap_url in sitemap_urls:
                try:
                    response = self.session.get(sitemap_url, timeout=10)
                    if response.status_code == 200:
                        await self._parse_sitemap_xml(response.text, result)
                except Exception as e:
                    logger.debug(f"Failed to fetch sitemap {sitemap_url}: {str(e)}")
                    
        except Exception as e:
            logger.warning(f"Sitemap parsing error: {str(e)}")
            
    async def _parse_sitemap_xml(self, xml_content: str, result: URLDiscoveryResult):
        """Parse individual sitemap XML content"""
        try:
            root = ET.fromstring(xml_content)
            
            # Handle sitemap index files
            for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc_elem = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    # Recursively parse nested sitemaps
                    try:
                        response = self.session.get(loc_elem.text, timeout=10)
                        if response.status_code == 200:
                            await self._parse_sitemap_xml(response.text, result)
                    except Exception as e:
                        logger.debug(f"Failed to parse nested sitemap: {str(e)}")
                        
            # Handle URL entries
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc_elem = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None and loc_elem.text:
                    result.urls.add(loc_elem.text)
                    
                    # Extract metadata
                    lastmod_elem = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod')
                    if lastmod_elem is not None and lastmod_elem.text:
                        result.metadata.setdefault('lastmod', {})[loc_elem.text] = lastmod_elem.text
                        
                    priority_elem = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}priority')
                    if priority_elem is not None and priority_elem.text:
                        result.metadata.setdefault('priority', {})[loc_elem.text] = float(priority_elem.text)
                        
        except ET.ParseError as e:
            logger.debug(f"XML parse error in sitemap: {str(e)}")
        except Exception as e:
            logger.warning(f"Error parsing sitemap XML: {str(e)}")

class SeleniumLinkExtractor:
    """Advanced link extraction using Selenium with infinite scroll support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.driver = None
        
    async def discover_urls(self, target_url: str, policy: CrawlPolicy) -> URLDiscoveryResult:
        """Discover URLs using Selenium with advanced features"""
        result = URLDiscoveryResult()
        result.discovery_method = "selenium"
        
        try:
            await self._setup_driver()
            
            # Navigate to target URL
            self.driver.get(target_url)
            
            # Handle infinite scroll if enabled
            if policy.infinite_scroll:
                await self._handle_infinite_scroll()
                
            # Extract all links
            await self._extract_links(result, policy)
            
            # Extract form endpoints if enabled
            if policy.extract_forms:
                await self._extract_forms(result)
                
            # Extract API endpoints from JavaScript if enabled
            if policy.extract_api_endpoints:
                await self._extract_api_endpoints(result)
                
            # Extract JavaScript URLs if enabled  
            if policy.extract_js_urls:
                await self._extract_js_urls(result)
                
            logger.info(f"Selenium discovered {len(result.urls)} URLs")
            
        except Exception as e:
            logger.error(f"Selenium discovery failed: {str(e)}")
            result.errors.append(f"Selenium error: {str(e)}")
        finally:
            await self._cleanup_driver()
            
        return result
    
    async def _setup_driver(self):
        """Setup Selenium WebDriver"""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if self.config.get('headless', True):
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        # Add user agent
        if 'user_agent' in self.config:
            options.add_argument(f'--user-agent={self.config["user_agent"]}')
            
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_page_load_timeout(self.config.get('page_timeout', 30))
        
    async def _cleanup_driver(self):
        """Cleanup Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                logger.warning(f"Error cleaning up driver: {str(e)}")
            finally:
                self.driver = None
                
    async def _handle_infinite_scroll(self):
        """Handle infinite scroll pages"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            scroll_attempts = 0
            max_scrolls = self.config.get('max_scrolls', 10)
            
            while scroll_attempts < max_scrolls:
                # Scroll to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
                # Wait for new content to load
                await asyncio.sleep(2)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_attempts += 1
                
            logger.info(f"Performed {scroll_attempts} scroll attempts")
            
        except Exception as e:
            logger.warning(f"Infinite scroll handling failed: {str(e)}")
            
    async def _extract_links(self, result: URLDiscoveryResult, policy: CrawlPolicy):
        """Extract all links from the page"""
        try:
            # Get all anchor tags
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                try:
                    href = link.get_attribute("href")
                    if href and self._should_include_url(href, policy):
                        result.urls.add(href)
                except Exception as e:
                    logger.debug(f"Error extracting link: {str(e)}")
                    
            # Extract links from custom selectors
            for selector in policy.custom_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href") or element.get_attribute("data-href")
                        if href and self._should_include_url(href, policy):
                            result.urls.add(href)
                except Exception as e:
                    logger.debug(f"Error with custom selector {selector}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Link extraction failed: {str(e)}")
            
    async def _extract_forms(self, result: URLDiscoveryResult):
        """Extract form endpoints"""
        try:
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            form_endpoints = []
            
            for form in forms:
                try:
                    action = form.get_attribute("action")
                    method = form.get_attribute("method") or "GET"
                    
                    if action:
                        # Convert relative URLs to absolute
                        if action.startswith('/'):
                            current_url = self.driver.current_url
                            parsed = urlparse(current_url)
                            action = f"{parsed.scheme}://{parsed.netloc}{action}"
                        elif not action.startswith('http'):
                            action = urljoin(self.driver.current_url, action)
                            
                        form_endpoints.append({
                            'url': action,
                            'method': method.upper(),
                            'inputs': self._extract_form_inputs(form)
                        })
                        
                        result.urls.add(action)
                        
                except Exception as e:
                    logger.debug(f"Error extracting form: {str(e)}")
                    
            result.metadata['forms'] = form_endpoints
            
        except Exception as e:
            logger.error(f"Form extraction failed: {str(e)}")
            
    def _extract_form_inputs(self, form):
        """Extract input fields from a form"""
        inputs = []
        try:
            input_elements = form.find_elements(By.TAG_NAME, "input")
            input_elements.extend(form.find_elements(By.TAG_NAME, "select"))
            input_elements.extend(form.find_elements(By.TAG_NAME, "textarea"))
            
            for inp in input_elements:
                try:
                    inputs.append({
                        'name': inp.get_attribute('name'),
                        'type': inp.get_attribute('type'),
                        'required': inp.get_attribute('required') is not None,
                        'placeholder': inp.get_attribute('placeholder')
                    })
                except Exception as e:
                    logger.debug(f"Error extracting input: {str(e)}")
                    
        except Exception as e:
            logger.debug(f"Error extracting form inputs: {str(e)}")
            
        return inputs
    
    async def _extract_api_endpoints(self, result: URLDiscoveryResult):
        """Extract API endpoints from JavaScript"""
        try:
            # Get all script content
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            api_patterns = [
                r'["\'/]api/[^"\'>\s]+',
                r'["\'/]v\d+/[^"\'>\s]+',
                r'["\']https?://[^"\']+/api/[^"\']+',
                r'fetch\s*\(\s*["\']([^"\']+)',
                r'axios\.[get|post|put|delete]+\s*\(\s*["\']([^"\']+)',
                r'XMLHttpRequest.*open\s*\(\s*["\'][^"\']*["\'],\s*["\']([^"\']+)'
            ]
            
            api_endpoints = set()
            
            for script in scripts:
                try:
                    content = script.get_attribute("innerHTML")
                    if content:
                        for pattern in api_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if isinstance(match, tuple):
                                    match = match[0]
                                if match and not match.startswith('data:'):
                                    # Convert relative URLs
                                    if match.startswith('/'):
                                        current_url = self.driver.current_url
                                        parsed = urlparse(current_url)
                                        match = f"{parsed.scheme}://{parsed.netloc}{match}"
                                    elif not match.startswith('http'):
                                        match = urljoin(self.driver.current_url, match)
                                    
                                    api_endpoints.add(match)
                                    result.urls.add(match)
                                    
                except Exception as e:
                    logger.debug(f"Error extracting from script: {str(e)}")
                    
            result.metadata['api_endpoints'] = list(api_endpoints)
            logger.info(f"Extracted {len(api_endpoints)} API endpoints")
            
        except Exception as e:
            logger.error(f"API endpoint extraction failed: {str(e)}")
            
    async def _extract_js_urls(self, result: URLDiscoveryResult):
        """Extract JavaScript file URLs"""
        try:
            scripts = self.driver.find_elements(By.TAG_NAME, "script")
            js_urls = set()
            
            for script in scripts:
                try:
                    src = script.get_attribute("src")
                    if src:
                        # Convert relative URLs
                        if src.startswith('/'):
                            current_url = self.driver.current_url
                            parsed = urlparse(current_url)
                            src = f"{parsed.scheme}://{parsed.netloc}{src}"
                        elif not src.startswith('http'):
                            src = urljoin(self.driver.current_url, src)
                            
                        js_urls.add(src)
                        result.urls.add(src)
                        
                except Exception as e:
                    logger.debug(f"Error extracting JS URL: {str(e)}")
                    
            result.metadata['js_urls'] = list(js_urls)
            logger.info(f"Extracted {len(js_urls)} JavaScript URLs")
            
        except Exception as e:
            logger.error(f"JavaScript URL extraction failed: {str(e)}")
    
    def _should_include_url(self, url: str, policy: CrawlPolicy) -> bool:
        """Check if URL should be included based on policy"""
        try:
            # Skip invalid URLs
            if not url or url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                return False
                
            # Check exclude patterns
            for pattern in policy.exclude_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False
                    
            # Check include patterns (if any)
            if policy.include_patterns:
                for pattern in policy.include_patterns:
                    if re.search(pattern, url, re.IGNORECASE):
                        return True
                return False
                
            return True
            
        except Exception as e:
            logger.debug(f"Error checking URL inclusion: {str(e)}")
            return False

class URLDiscoverySystem:
    """Main URL discovery system coordinating multiple engines"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.engines = self._initialize_engines()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or defaults"""
        default_config = {
            'katana': {
                'enabled': True,
                'katana_path': 'katana',
                'headless': True,
                'timeout': 300,
                'rate_limit': 100
            },
            'photon': {
                'enabled': True,
                'photon_path': '/opt/Photon/photon.py',
                'timeout': 300
            },
            'sitemap': {
                'enabled': True,
                'timeout': 30
            },
            'selenium': {
                'enabled': True,
                'headless': True,
                'page_timeout': 30,
                'max_scrolls': 10,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    # Merge configurations
                    for key, value in file_config.items():
                        if key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {str(e)}")
                
        return default_config
    
    def _initialize_engines(self) -> Dict[str, Any]:
        """Initialize discovery engines based on configuration"""
        engines = {}
        
        if self.config.get('katana', {}).get('enabled', False):
            engines['katana'] = KatanaIntegration(self.config['katana'])
            
        if self.config.get('photon', {}).get('enabled', False):
            engines['photon'] = PhotonIntegration(self.config['photon'])
            
        if self.config.get('sitemap', {}).get('enabled', True):
            engines['sitemap'] = SitemapParser(self.config['sitemap'])
            
        if self.config.get('selenium', {}).get('enabled', True):
            engines['selenium'] = SeleniumLinkExtractor(self.config['selenium'])
            
        return engines
    
    async def discover_urls(self, target_url: str, policy: Optional[CrawlPolicy] = None) -> Dict[str, URLDiscoveryResult]:
        """Discover URLs using all enabled engines"""
        if policy is None:
            policy = CrawlPolicy()
            
        results = {}
        
        # Run discovery engines based on policy
        for engine_name in policy.discovery_engines:
            if engine_name in self.engines:
                try:
                    logger.info(f"Running URL discovery with {engine_name}")
                    result = await self.engines[engine_name].discover_urls(target_url, policy)
                    results[engine_name] = result
                    logger.info(f"{engine_name} discovered {len(result.urls)} URLs with {len(result.errors)} errors")
                except Exception as e:
                    logger.error(f"Engine {engine_name} failed: {str(e)}")
                    results[engine_name] = URLDiscoveryResult()
                    results[engine_name].errors.append(f"Engine failure: {str(e)}")
            else:
                logger.warning(f"Engine {engine_name} not available")
                
        return results
    
    async def discover_urls_comprehensive(self, target_url: str, policy: Optional[CrawlPolicy] = None) -> URLDiscoveryResult:
        """Run comprehensive URL discovery with all engines and merge results"""
        if policy is None:
            policy = CrawlPolicy()
            
        # Run all engines
        results = await self.discover_urls(target_url, policy)
        
        # Merge results
        merged_result = URLDiscoveryResult()
        merged_result.discovery_method = "comprehensive"
        
        for engine_name, result in results.items():
            merged_result.urls.update(result.urls)
            merged_result.errors.extend(result.errors)
            
            # Merge metadata
            for key, value in result.metadata.items():
                if key not in merged_result.metadata:
                    merged_result.metadata[key] = value
                elif isinstance(value, list):
                    if isinstance(merged_result.metadata[key], list):
                        merged_result.metadata[key].extend(value)
                elif isinstance(value, dict):
                    if isinstance(merged_result.metadata[key], dict):
                        merged_result.metadata[key].update(value)
                        
        # Remove duplicates and apply filters
        filtered_urls = set()
        for url in merged_result.urls:
            if len(filtered_urls) >= policy.max_urls_per_domain:
                break
            if self._should_include_url(url, policy):
                filtered_urls.add(url)
                
        merged_result.urls = filtered_urls
        
        logger.info(f"Comprehensive discovery found {len(merged_result.urls)} unique URLs")
        return merged_result
    
    def _should_include_url(self, url: str, policy: CrawlPolicy) -> bool:
        """Check if URL should be included based on policy"""
        try:
            # Skip invalid URLs
            if not url or url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                return False
                
            # Check exclude patterns
            for pattern in policy.exclude_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False
                    
            # Check include patterns (if any)
            if policy.include_patterns:
                for pattern in policy.include_patterns:
                    if re.search(pattern, url, re.IGNORECASE):
                        return True
                return False
                
            return True
            
        except Exception as e:
            logger.debug(f"Error checking URL inclusion: {str(e)}")
            return False

# Example usage and CLI interface
async def main():
    """Example usage of URL Discovery System"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Revolutionary URL Discovery System v4.0")
    parser.add_argument("url", help="Target URL to discover")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--depth", type=int, default=3, help="Maximum crawl depth")
    parser.add_argument("--max-urls", type=int, default=1000, help="Maximum URLs per domain")
    parser.add_argument("--engines", nargs="+", default=['sitemap', 'selenium'], 
                       help="Discovery engines to use")
    parser.add_argument("--infinite-scroll", action="store_true", help="Enable infinite scroll")
    parser.add_argument("--extract-forms", action="store_true", help="Extract form endpoints")
    parser.add_argument("--extract-api", action="store_true", help="Extract API endpoints")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create discovery system
    system = URLDiscoverySystem(args.config)
    
    # Create crawl policy
    policy = CrawlPolicy(
        max_depth=args.depth,
        max_urls_per_domain=args.max_urls,
        discovery_engines=args.engines,
        infinite_scroll=args.infinite_scroll,
        extract_forms=args.extract_forms,
        extract_api_endpoints=args.extract_api
    )
    
    try:
        # Run comprehensive discovery
        result = await system.discover_urls_comprehensive(args.url, policy)
        
        # Display results
        print(f"\n🎯 URL Discovery Results for: {args.url}")
        print(f"📊 Total URLs discovered: {len(result.urls)}")
        print(f"🔧 Discovery method: {result.discovery_method}")
        
        if result.errors:
            print(f"❌ Errors: {len(result.errors)}")
            for error in result.errors[:5]:  # Show first 5 errors
                print(f"   • {error}")
                
        # Show sample URLs
        print(f"\n📋 Sample URLs:")
        for i, url in enumerate(sorted(result.urls)[:10]):
            print(f"   {i+1}. {url}")
            
        if len(result.urls) > 10:
            print(f"   ... and {len(result.urls) - 10} more URLs")
            
        # Show metadata
        if result.metadata:
            print(f"\n📋 Metadata:")
            for key, value in result.metadata.items():
                if isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                elif isinstance(value, dict):
                    print(f"   {key}: {len(value)} entries") 
                else:
                    print(f"   {key}: {value}")
                    
        # Save results if requested
        if args.output:
            output_data = {
                'target_url': args.url,
                'discovery_method': result.discovery_method,
                'total_urls': len(result.urls),
                'urls': list(result.urls),
                'metadata': result.metadata,
                'errors': result.errors
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
                
            print(f"\n💾 Results saved to: {args.output}")
            
    except KeyboardInterrupt:
        print("\n🛑 Discovery interrupted by user")
    except Exception as e:
        print(f"\n❌ Discovery failed: {str(e)}")
        logger.exception("Discovery failed")

if __name__ == "__main__":
    asyncio.run(main())
