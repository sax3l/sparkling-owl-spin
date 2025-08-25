#!/usr/bin/env python3
"""
Katana URL Discovery Integration - Revolutionary Ultimate System v4.0
Advanced URL discovery and crawling using ProjectDiscovery's Katana
"""

import asyncio
import logging
import time
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union, Set
from dataclasses import dataclass, asdict
from urllib.parse import urljoin, urlparse, urlencode
import re

logger = logging.getLogger(__name__)

@dataclass
class KatanaConfig:
    """Configuration for Katana URL discovery"""
    enabled: bool = True
    katana_path: str = "katana"
    timeout: int = 300
    max_depth: int = 3
    max_urls: int = 1000
    concurrency: int = 10
    delay: float = 0.0
    random_delay: bool = False
    headless: bool = True
    chrome_path: Optional[str] = None
    user_agent: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    cookies: Optional[Dict[str, str]] = None
    proxy: Optional[str] = None
    scope: Optional[List[str]] = None  # Regex patterns for scope
    exclude: Optional[List[str]] = None  # Regex patterns to exclude
    extensions: Optional[List[str]] = None  # File extensions to include
    filter_codes: Optional[List[int]] = None  # HTTP status codes to filter
    js_crawling: bool = True
    xhr_extraction: bool = True
    form_extraction: bool = True
    robots_txt: bool = False
    sitemap: bool = True
    passive_sources: bool = False
    debug: bool = False
    output_format: str = "json"  # json, txt

@dataclass
class DiscoveredURL:
    """Container for discovered URL information"""
    url: str
    method: str = "GET"
    status_code: Optional[int] = None
    content_length: Optional[int] = None
    content_type: Optional[str] = None
    source: str = "crawl"  # crawl, js, xhr, form, sitemap, etc.
    depth: int = 0
    parent_url: Optional[str] = None
    title: Optional[str] = None
    technologies: Optional[List[str]] = None
    response_time: Optional[float] = None
    discovered_at: Optional[float] = None

class KatanaURLDiscovery:
    """
    Katana URL discovery manager for comprehensive web crawling.
    
    Features:
    - Deep URL discovery with JavaScript support
    - Form extraction and analysis
    - XHR endpoint discovery
    - Sitemap parsing
    - Technology detection
    - Scope-based filtering
    """
    
    def __init__(self, config: KatanaConfig):
        self.config = config
        self.temp_dir = None
        self._stats = {
            'crawls_total': 0,
            'urls_discovered': 0,
            'total_processing_time': 0.0
        }
        
    async def initialize(self):
        """Initialize Katana URL discovery"""
        
        if not self.config.enabled:
            return
            
        # Check if Katana is available
        try:
            result = subprocess.run([self.config.katana_path, '-version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version = result.stdout.strip()
                logger.info(f"✅ Katana found: {version}")
            else:
                # Try alternative check
                result = subprocess.run([self.config.katana_path, '-h'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info("✅ Katana found (help displayed)")
                else:
                    raise RuntimeError("Katana not responding")
                    
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            logger.error(f"❌ Katana not available: {str(e)}")
            if self.config.enabled:
                logger.warning("⚠️ Install Katana: go install github.com/projectdiscovery/katana/cmd/katana@latest")
            return
            
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="katana_"))
        
        logger.info("✅ Katana URL discovery initialized")
        
    async def discover_urls(self, target: Union[str, List[str]],
                          custom_config: Optional[Dict[str, Any]] = None) -> List[DiscoveredURL]:
        """Discover URLs from target(s) using Katana"""
        
        if not self.config.enabled:
            return []
            
        start_time = time.time()
        self._stats['crawls_total'] += 1
        
        try:
            logger.info(f"🔍 Starting URL discovery with Katana")
            
            # Prepare targets
            targets = target if isinstance(target, list) else [target]
            
            # Build Katana command
            cmd = await self._build_katana_command(targets, custom_config)
            
            # Run Katana
            result = await self._run_katana(cmd)
            
            if result['success']:
                urls = await self._parse_katana_output(result['output'], targets[0])
                
                processing_time = time.time() - start_time
                self._stats['urls_discovered'] += len(urls)
                self._stats['total_processing_time'] += processing_time
                
                logger.info(f"✅ Discovered {len(urls)} URLs ({processing_time:.2f}s)")
                return urls
            else:
                logger.error(f"❌ Katana failed: {result['error']}")
                return []
                
        except Exception as e:
            logger.error(f"❌ URL discovery failed: {str(e)}")
            return []
            
    async def _build_katana_command(self, targets: List[str],
                                  custom_config: Optional[Dict[str, Any]] = None) -> List[str]:
        """Build Katana command line arguments"""
        
        cmd = [self.config.katana_path]
        
        # Add targets
        for target in targets:
            cmd.extend(['-u', target])
            
        # Basic options
        cmd.extend(['-d', str(self.config.max_depth)])
        cmd.extend(['-c', str(self.config.concurrency)])
        cmd.extend(['-timeout', str(self.config.timeout)])
        
        if self.config.max_urls:
            cmd.extend(['-rl', str(self.config.max_urls)])
            
        # Delay settings
        if self.config.delay > 0:
            cmd.extend(['-delay', str(int(self.config.delay * 1000))])  # Convert to ms
            
        if self.config.random_delay:
            cmd.append('-rd')
            
        # Browser settings
        if self.config.headless:
            cmd.append('-headless')
            
        if self.config.chrome_path:
            cmd.extend(['-chrome-path', self.config.chrome_path])
            
        # HTTP settings
        if self.config.user_agent:
            cmd.extend(['-H', f'User-Agent: {self.config.user_agent}'])
            
        # Headers
        if self.config.headers:
            for name, value in self.config.headers.items():
                cmd.extend(['-H', f'{name}: {value}'])
                
        # Cookies
        if self.config.cookies:
            cookie_str = '; '.join([f'{k}={v}' for k, v in self.config.cookies.items()])
            cmd.extend(['-H', f'Cookie: {cookie_str}'])
            
        # Proxy
        if self.config.proxy:
            cmd.extend(['-proxy', self.config.proxy])
            
        # Crawling options
        if self.config.js_crawling:
            cmd.append('-js-crawl')
            
        if self.config.xhr_extraction:
            cmd.append('-xhr')
            
        if self.config.form_extraction:
            cmd.append('-forms')
            
        if self.config.robots_txt:
            cmd.append('-robots')
            
        if self.config.sitemap:
            cmd.append('-sitemap')
            
        if self.config.passive_sources:
            cmd.append('-passive')
            
        # Scope filtering
        if self.config.scope:
            for pattern in self.config.scope:
                cmd.extend(['-scope', pattern])
                
        # Exclusion patterns
        if self.config.exclude:
            for pattern in self.config.exclude:
                cmd.extend(['-exclude', pattern])
                
        # File extensions
        if self.config.extensions:
            ext_str = ','.join(self.config.extensions)
            cmd.extend(['-extension', ext_str])
            
        # Status code filtering
        if self.config.filter_codes:
            code_str = ','.join(map(str, self.config.filter_codes))
            cmd.extend(['-mc', code_str])
            
        # Output format
        if self.config.output_format == 'json':
            cmd.append('-json')
            
        # Debug mode
        if self.config.debug:
            cmd.append('-debug')
            
        # Silent mode (reduce noise)
        if not self.config.debug:
            cmd.append('-silent')
            
        # Apply custom config
        if custom_config:
            for key, value in custom_config.items():
                if isinstance(value, bool) and value:
                    cmd.append(f'-{key}')
                elif isinstance(value, (str, int, float)):
                    cmd.extend([f'-{key}', str(value)])
                elif isinstance(value, list):
                    for item in value:
                        cmd.extend([f'-{key}', str(item)])
                        
        return cmd
        
    async def _run_katana(self, cmd: List[str]) -> Dict[str, Any]:
        """Run Katana command and capture output"""
        
        try:
            logger.info(f"🚀 Running Katana: {' '.join(cmd[:5])}...")  # Show first few args
            
            # Run Katana process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.temp_dir
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.config.timeout + 30
            )
            
            if process.returncode == 0:
                return {
                    'success': True,
                    'output': stdout.decode('utf-8', errors='ignore'),
                    'errors': stderr.decode('utf-8', errors='ignore')
                }
            else:
                return {
                    'success': False,
                    'error': stderr.decode('utf-8', errors='ignore') or f'Process exited with code {process.returncode}',
                    'output': stdout.decode('utf-8', errors='ignore')
                }
                
        except asyncio.TimeoutError:
            return {
                'success': False,
                'error': 'Katana execution timeout'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
            
    async def _parse_katana_output(self, output: str, base_url: str) -> List[DiscoveredURL]:
        """Parse Katana output and extract discovered URLs"""
        
        discovered_urls = []
        current_time = time.time()
        
        try:
            if self.config.output_format == 'json':
                # Parse JSON output
                for line in output.strip().split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            url_obj = await self._create_url_object(data, base_url, current_time)
                            if url_obj:
                                discovered_urls.append(url_obj)
                        except json.JSONDecodeError:
                            # Handle non-JSON lines
                            if line.strip().startswith('http'):
                                url_obj = DiscoveredURL(
                                    url=line.strip(),
                                    discovered_at=current_time
                                )
                                discovered_urls.append(url_obj)
            else:
                # Parse text output
                for line in output.strip().split('\n'):
                    line = line.strip()
                    if line.startswith('http'):
                        url_obj = DiscoveredURL(
                            url=line,
                            discovered_at=current_time
                        )
                        discovered_urls.append(url_obj)
                        
        except Exception as e:
            logger.error(f"❌ Failed to parse Katana output: {str(e)}")
            # Fallback: extract URLs with regex
            url_pattern = r'https?://[^\s<>"\'{}|\\^`\[\]]+[^\s<>"\'{}|\\^`\[\].,;!?)]'
            urls = re.findall(url_pattern, output)
            
            for url in urls:
                url_obj = DiscoveredURL(
                    url=url,
                    discovered_at=current_time
                )
                discovered_urls.append(url_obj)
                
        # Remove duplicates
        seen_urls = set()
        unique_urls = []
        for url_obj in discovered_urls:
            if url_obj.url not in seen_urls:
                seen_urls.add(url_obj.url)
                unique_urls.append(url_obj)
                
        return unique_urls
        
    async def _create_url_object(self, data: Dict[str, Any], base_url: str, 
                               discovered_at: float) -> Optional[DiscoveredURL]:
        """Create DiscoveredURL object from Katana JSON data"""
        
        try:
            url = data.get('url', '')
            if not url:
                return None
                
            return DiscoveredURL(
                url=url,
                method=data.get('method', 'GET'),
                status_code=data.get('status_code'),
                content_length=data.get('content_length'),
                content_type=data.get('content_type'),
                source=data.get('source', 'crawl'),
                depth=data.get('depth', 0),
                parent_url=data.get('parent', base_url),
                title=data.get('title'),
                technologies=data.get('technologies', []),
                response_time=data.get('response_time'),
                discovered_at=discovered_at
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to create URL object: {str(e)}")
            return None
            
    async def discover_from_multiple_sources(self, targets: List[str],
                                           custom_configs: Optional[List[Dict[str, Any]]] = None,
                                           merge_results: bool = True) -> Union[List[DiscoveredURL], List[List[DiscoveredURL]]]:
        """Discover URLs from multiple sources with different configurations"""
        
        if custom_configs and len(custom_configs) != len(targets):
            raise ValueError("Number of custom configs must match number of targets")
            
        tasks = []
        for i, target in enumerate(targets):
            config = custom_configs[i] if custom_configs else None
            tasks.append(self.discover_urls(target, config))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        valid_results = []
        for result in results:
            if isinstance(result, list):
                valid_results.append(result)
            else:
                logger.error(f"❌ Discovery task failed: {str(result)}")
                valid_results.append([])
                
        if merge_results:
            # Merge all results
            all_urls = []
            seen_urls = set()
            
            for result_list in valid_results:
                for url_obj in result_list:
                    if url_obj.url not in seen_urls:
                        seen_urls.add(url_obj.url)
                        all_urls.append(url_obj)
                        
            return all_urls
        else:
            return valid_results
            
    async def filter_urls(self, urls: List[DiscoveredURL],
                         filters: Dict[str, Any]) -> List[DiscoveredURL]:
        """Filter discovered URLs based on criteria"""
        
        filtered_urls = []
        
        for url_obj in urls:
            include = True
            
            # Status code filter
            if 'status_codes' in filters:
                if url_obj.status_code not in filters['status_codes']:
                    include = False
                    
            # Content type filter
            if 'content_types' in filters and include:
                if url_obj.content_type:
                    if not any(ct in url_obj.content_type for ct in filters['content_types']):
                        include = False
                        
            # URL pattern filter
            if 'url_patterns' in filters and include:
                if not any(re.search(pattern, url_obj.url, re.IGNORECASE) 
                          for pattern in filters['url_patterns']):
                    include = False
                    
            # Exclude patterns
            if 'exclude_patterns' in filters and include:
                if any(re.search(pattern, url_obj.url, re.IGNORECASE) 
                       for pattern in filters['exclude_patterns']):
                    include = False
                    
            # Depth filter
            if 'max_depth' in filters and include:
                if url_obj.depth > filters['max_depth']:
                    include = False
                    
            # Source filter
            if 'sources' in filters and include:
                if url_obj.source not in filters['sources']:
                    include = False
                    
            if include:
                filtered_urls.append(url_obj)
                
        return filtered_urls
        
    def get_stats(self) -> Dict[str, Any]:
        """Get discovery statistics"""
        avg_processing_time = 0.0
        if self._stats['crawls_total'] > 0:
            avg_processing_time = self._stats['total_processing_time'] / self._stats['crawls_total']
            
        urls_per_crawl = 0.0
        if self._stats['crawls_total'] > 0:
            urls_per_crawl = self._stats['urls_discovered'] / self._stats['crawls_total']
            
        return {
            **self._stats,
            'average_processing_time': avg_processing_time,
            'average_urls_per_crawl': urls_per_crawl,
            'config': asdict(self.config)
        }
        
    async def cleanup(self):
        """Clean up temporary resources"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"🧹 Cleaned up Katana temp directory")
            except Exception as e:
                logger.error(f"❌ Failed to cleanup temp dir: {str(e)}")

class KatanaAdapter:
    """High-level adapter for Katana URL discovery"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = KatanaConfig(**config)
        self.discovery = KatanaURLDiscovery(self.config) if self.config.enabled else None
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("Katana adapter disabled")
            return
            
        if self.discovery:
            await self.discovery.initialize()
            logger.info("✅ Katana adapter initialized")
        else:
            logger.error("❌ Katana discovery not available")
            
    async def discover_urls_comprehensive(self, target: Union[str, List[str]],
                                        max_depth: Optional[int] = None,
                                        max_urls: Optional[int] = None,
                                        include_js: bool = True,
                                        include_forms: bool = True,
                                        include_xhr: bool = True,
                                        custom_scope: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Comprehensive URL discovery with advanced options.
        
        Returns:
        {
            'success': bool,
            'target': str,
            'urls_discovered': list,
            'total_urls': int,
            'unique_domains': int,
            'by_source': dict,
            'by_depth': dict,
            'discovery_time': float
        }
        """
        
        if not self.config.enabled or not self.discovery:
            return {
                'success': False,
                'target': str(target),
                'error': 'Katana is disabled or not available'
            }
            
        try:
            start_time = time.time()
            
            # Prepare custom config
            custom_config = {}
            if max_depth is not None:
                custom_config['d'] = max_depth
            if max_urls is not None:
                custom_config['rl'] = max_urls
            if not include_js:
                custom_config['no-js-crawl'] = True
            if not include_forms:
                custom_config['no-forms'] = True
            if not include_xhr:
                custom_config['no-xhr'] = True
            if custom_scope:
                custom_config['scope'] = custom_scope
                
            # Discover URLs
            discovered_urls = await self.discovery.discover_urls(target, custom_config)
            
            discovery_time = time.time() - start_time
            
            # Analyze results
            analysis = await self._analyze_discovered_urls(discovered_urls)
            
            return {
                'success': True,
                'target': str(target),
                'urls_discovered': [asdict(url) for url in discovered_urls],
                'total_urls': len(discovered_urls),
                'unique_domains': analysis['unique_domains'],
                'by_source': analysis['by_source'],
                'by_depth': analysis['by_depth'],
                'by_method': analysis['by_method'],
                'by_status_code': analysis['by_status_code'],
                'discovery_time': discovery_time,
                'method': 'katana'
            }
            
        except Exception as e:
            logger.error(f"❌ Comprehensive URL discovery failed: {str(e)}")
            return {
                'success': False,
                'target': str(target),
                'error': str(e),
                'method': 'katana'
            }
            
    async def _analyze_discovered_urls(self, urls: List[DiscoveredURL]) -> Dict[str, Any]:
        """Analyze discovered URLs and generate statistics"""
        
        unique_domains = set()
        by_source = {}
        by_depth = {}
        by_method = {}
        by_status_code = {}
        
        for url_obj in urls:
            # Extract domain
            try:
                parsed = urlparse(url_obj.url)
                domain = parsed.netloc
                unique_domains.add(domain)
            except:
                pass
                
            # Count by source
            source = url_obj.source or 'unknown'
            by_source[source] = by_source.get(source, 0) + 1
            
            # Count by depth
            depth = url_obj.depth or 0
            by_depth[depth] = by_depth.get(depth, 0) + 1
            
            # Count by method
            method = url_obj.method or 'GET'
            by_method[method] = by_method.get(method, 0) + 1
            
            # Count by status code
            if url_obj.status_code:
                by_status_code[url_obj.status_code] = by_status_code.get(url_obj.status_code, 0) + 1
                
        return {
            'unique_domains': len(unique_domains),
            'by_source': by_source,
            'by_depth': by_depth,
            'by_method': by_method,
            'by_status_code': by_status_code
        }
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        base_stats = {
            'enabled': self.config.enabled,
            'config': asdict(self.config)
        }
        
        if self.discovery:
            base_stats['discovery_stats'] = self.discovery.get_stats()
        else:
            base_stats['discovery_stats'] = {}
            
        return base_stats
        
    async def cleanup(self):
        """Clean up all resources"""
        if self.discovery:
            await self.discovery.cleanup()

# Factory function
def create_katana_adapter(config: Dict[str, Any]) -> KatanaAdapter:
    """Create and configure Katana adapter"""
    return KatanaAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'max_depth': 2,
        'max_urls': 100,
        'js_crawling': True,
        'xhr_extraction': True,
        'form_extraction': True,
        'debug': True
    }
    
    adapter = create_katana_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Test URL discovery
        result = await adapter.discover_urls_comprehensive(
            'https://example.com',
            max_depth=2,
            include_js=True,
            include_forms=True
        )
        
        if result['success']:
            print(f"✅ Success: Discovered {result['total_urls']} URLs")
            print(f"Unique domains: {result['unique_domains']}")
            print(f"By source: {result['by_source']}")
        else:
            print(f"❌ Failed: {result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
