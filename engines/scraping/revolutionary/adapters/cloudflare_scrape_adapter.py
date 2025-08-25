#!/usr/bin/env python3
"""
CloudFlare-Scrape Integration - Revolutionary Ultimate System v4.0
Node.js-based CloudFlare bypass solution
"""

import asyncio
import logging
import time
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
import aiofiles
import aiohttp

logger = logging.getLogger(__name__)

@dataclass
class CloudFlareScrapeConfig:
    """Configuration for CloudFlare-Scrape"""
    enabled: bool = True
    nodejs_path: str = "node"
    npm_path: str = "npm"
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 3.0
    debug: bool = False
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    cookies: Optional[Dict[str, str]] = None
    headers: Optional[Dict[str, str]] = None
    cloudflare_scrape_path: Optional[str] = None
    auto_install: bool = True

class CloudFlareScrapeManager:
    """
    CloudFlare-Scrape manager using Node.js implementation.
    
    Features:
    - Node.js-based CloudFlare bypass
    - Automatic challenge solving
    - Cookie and session management
    - JavaScript execution support
    """
    
    def __init__(self, config: CloudFlareScrapeConfig):
        self.config = config
        self.temp_dir = None
        self.scrape_script_path = None
        self.node_modules_installed = False
        
    async def initialize(self):
        """Initialize the CloudFlare-Scrape environment"""
        
        if not self.config.enabled:
            return
            
        try:
            # Check Node.js availability
            result = subprocess.run([self.config.nodejs_path, '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                raise RuntimeError("Node.js not found")
                
            node_version = result.stdout.strip()
            logger.info(f"✅ Node.js found: {node_version}")
            
        except (subprocess.TimeoutExpired, FileNotFoundError, RuntimeError) as e:
            logger.error(f"❌ Node.js not available: {str(e)}")
            if self.config.enabled:
                raise RuntimeError("Node.js required for CloudFlare-Scrape")
            return
            
        # Create temporary directory
        self.temp_dir = Path(tempfile.mkdtemp(prefix="cf_scrape_"))
        
        # Create or find CloudFlare scrape script
        if self.config.cloudflare_scrape_path and Path(self.config.cloudflare_scrape_path).exists():
            self.scrape_script_path = Path(self.config.cloudflare_scrape_path)
        else:
            await self._create_scrape_script()
            
        # Install dependencies if needed
        if self.config.auto_install:
            await self._install_dependencies()
            
        logger.info("✅ CloudFlare-Scrape manager initialized")
        
    async def _create_scrape_script(self):
        """Create the Node.js CloudFlare bypass script"""
        
        script_content = '''
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

async function bypassCloudflare(config) {
    const {
        url,
        userAgent,
        proxy,
        cookies,
        headers,
        timeout,
        waitFor,
        executeJs,
        screenshot
    } = config;
    
    let browser;
    let page;
    
    try {
        // Browser options
        const browserOptions = {
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor'
            ],
            timeout: timeout || 60000
        };
        
        if (proxy) {
            browserOptions.args.push(`--proxy-server=${proxy}`);
        }
        
        // Launch browser
        browser = await puppeteer.launch(browserOptions);
        page = await browser.newPage();
        
        // Set user agent
        if (userAgent) {
            await page.setUserAgent(userAgent);
        }
        
        // Set extra headers
        if (headers) {
            await page.setExtraHTTPHeaders(headers);
        }
        
        // Set cookies
        if (cookies) {
            await page.setCookie(...cookies);
        }
        
        // Set viewport
        await page.setViewport({ width: 1920, height: 1080 });
        
        // Navigate to URL
        console.log(`Navigating to: ${url}`);
        const response = await page.goto(url, {
            waitUntil: 'networkidle2',
            timeout: timeout || 60000
        });
        
        // Wait for specific element if requested
        if (waitFor) {
            try {
                await page.waitForSelector(waitFor, { timeout: 10000 });
            } catch (e) {
                console.warn(`Element not found: ${waitFor}`);
            }
        }
        
        // Wait for CloudFlare challenge to complete
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        // Check if still on CloudFlare challenge page
        const title = await page.title();
        const url_current = page.url();
        
        if (title.includes('Just a moment') || title.includes('Checking your browser')) {
            console.log('CloudFlare challenge detected, waiting...');
            await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 30000 });
        }
        
        // Execute custom JavaScript if provided
        let jsResult = null;
        if (executeJs) {
            try {
                jsResult = await page.evaluate(executeJs);
            } catch (e) {
                console.warn(`JavaScript execution failed: ${e.message}`);
            }
        }
        
        // Get page content
        const content = await page.content();
        const finalUrl = page.url();
        const finalTitle = await page.title();
        
        // Get cookies
        const pageCookies = await page.cookies();
        const cookieDict = {};
        pageCookies.forEach(cookie => {
            cookieDict[cookie.name] = cookie.value;
        });
        
        // Take screenshot if requested
        let screenshotData = null;
        if (screenshot) {
            screenshotData = await page.screenshot({ 
                encoding: 'base64',
                fullPage: false
            });
        }
        
        const result = {
            success: true,
            url: finalUrl,
            title: finalTitle,
            html_content: content,
            cookies: cookieDict,
            status_code: response.status(),
            response_time: Date.now() - startTime,
            js_result: jsResult,
            screenshot: screenshotData
        };
        
        console.log(JSON.stringify(result));
        return result;
        
    } catch (error) {
        const result = {
            success: false,
            url: url,
            error: error.message,
            error_type: error.name
        };
        
        console.log(JSON.stringify(result));
        return result;
        
    } finally {
        if (page) await page.close();
        if (browser) await browser.close();
    }
}

// Parse command line arguments
const args = process.argv.slice(2);
const configJson = args[0];

if (!configJson) {
    console.error('No configuration provided');
    process.exit(1);
}

const startTime = Date.now();

try {
    const config = JSON.parse(configJson);
    bypassCloudflare(config);
} catch (error) {
    console.log(JSON.stringify({
        success: false,
        error: `Configuration error: ${error.message}`
    }));
    process.exit(1);
}
'''
        
        # Write script to temp directory
        self.scrape_script_path = self.temp_dir / "cloudflare_scraper.js"
        
        async with aiofiles.open(self.scrape_script_path, 'w') as f:
            await f.write(script_content)
            
        logger.info(f"📝 Created CloudFlare scrape script: {self.scrape_script_path}")
        
    async def _install_dependencies(self):
        """Install required Node.js dependencies"""
        
        if self.node_modules_installed:
            return
            
        package_json = {
            "name": "cloudflare-scraper",
            "version": "1.0.0",
            "dependencies": {
                "puppeteer-extra": "^3.3.6",
                "puppeteer-extra-plugin-stealth": "^2.11.2",
                "puppeteer": "^21.0.0"
            }
        }
        
        # Write package.json
        package_json_path = self.temp_dir / "package.json"
        async with aiofiles.open(package_json_path, 'w') as f:
            await f.write(json.dumps(package_json, indent=2))
            
        logger.info("📦 Installing Node.js dependencies...")
        
        try:
            # Install dependencies
            result = subprocess.run([
                self.config.npm_path, 'install'
            ], cwd=self.temp_dir, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"❌ npm install failed: {result.stderr}")
                raise RuntimeError(f"Failed to install dependencies: {result.stderr}")
                
            self.node_modules_installed = True
            logger.info("✅ Node.js dependencies installed")
            
        except subprocess.TimeoutExpired:
            logger.error("❌ npm install timeout")
            raise RuntimeError("npm install timeout")
            
    async def bypass_cloudflare(self, url: str,
                              user_agent: Optional[str] = None,
                              proxy: Optional[str] = None,
                              cookies: Optional[Dict[str, str]] = None,
                              headers: Optional[Dict[str, str]] = None,
                              wait_for: Optional[str] = None,
                              execute_js: Optional[str] = None,
                              screenshot: bool = False) -> Dict[str, Any]:
        """Bypass CloudFlare using Node.js script"""
        
        if not self.scrape_script_path or not self.scrape_script_path.exists():
            raise RuntimeError("CloudFlare scrape script not available")
            
        try:
            logger.info(f"🌩️ Bypassing CloudFlare for: {url}")
            start_time = time.time()
            
            # Prepare configuration
            config = {
                'url': url,
                'timeout': self.config.timeout * 1000,  # Convert to milliseconds
                'userAgent': user_agent or self.config.user_agent,
                'proxy': proxy or self.config.proxy,
                'headers': headers or self.config.headers,
                'waitFor': wait_for,
                'executeJs': execute_js,
                'screenshot': screenshot
            }
            
            # Convert cookies to Puppeteer format
            if cookies or self.config.cookies:
                cookie_list = []
                cookie_dict = cookies or self.config.cookies
                for name, value in cookie_dict.items():
                    cookie_list.append({
                        'name': name,
                        'value': value,
                        'domain': url.split('/')[2] if '//' in url else url
                    })
                config['cookies'] = cookie_list
                
            config_json = json.dumps(config)
            
            # Execute Node.js script
            result = subprocess.run([
                self.config.nodejs_path,
                str(self.scrape_script_path),
                config_json
            ], cwd=self.temp_dir, capture_output=True, text=True, 
               timeout=self.config.timeout + 10)
            
            if result.returncode != 0:
                logger.error(f"❌ Node.js script failed: {result.stderr}")
                return {
                    'success': False,
                    'url': url,
                    'error': f'Script execution failed: {result.stderr}',
                    'error_type': 'script_error'
                }
                
            # Parse output
            try:
                output_lines = result.stdout.strip().split('\n')
                # Find the JSON result (last line usually)
                json_output = None
                for line in reversed(output_lines):
                    try:
                        json_output = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
                        
                if not json_output:
                    raise ValueError("No valid JSON output found")
                    
                response_time = time.time() - start_time
                json_output['response_time'] = response_time
                
                if json_output.get('success'):
                    logger.info(f"✅ CloudFlare bypassed: {url} ({response_time:.2f}s)")
                else:
                    logger.error(f"❌ CloudFlare bypass failed: {json_output.get('error')}")
                    
                return json_output
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Failed to parse script output: {str(e)}")
                logger.debug(f"Script output: {result.stdout}")
                return {
                    'success': False,
                    'url': url,
                    'error': f'Failed to parse output: {str(e)}',
                    'error_type': 'parse_error'
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ CloudFlare bypass timeout for: {url}")
            return {
                'success': False,
                'url': url,
                'error': 'Request timeout',
                'error_type': 'timeout'
            }
            
        except Exception as e:
            logger.error(f"❌ CloudFlare bypass failed: {str(e)}")
            return {
                'success': False,
                'url': url,
                'error': str(e),
                'error_type': 'general_error'
            }
            
    def get_stats(self) -> Dict[str, Any]:
        """Get manager statistics"""
        return {
            'initialized': self.scrape_script_path is not None,
            'node_modules_installed': self.node_modules_installed,
            'temp_dir': str(self.temp_dir) if self.temp_dir else None,
            'script_path': str(self.scrape_script_path) if self.scrape_script_path else None
        }
        
    async def cleanup(self):
        """Clean up temporary resources"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"🧹 Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"❌ Failed to cleanup temp dir: {str(e)}")

class CloudFlareScrapeAdapter:
    """High-level adapter for CloudFlare-Scrape integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = CloudFlareScrapeConfig(**config)
        self.manager = CloudFlareScrapeManager(self.config)
        
    async def initialize(self):
        """Initialize the adapter"""
        if not self.config.enabled:
            logger.info("CloudFlare-Scrape adapter disabled")
            return
            
        try:
            await self.manager.initialize()
            logger.info("✅ CloudFlare-Scrape adapter initialized")
        except Exception as e:
            logger.error(f"❌ CloudFlare-Scrape initialization failed: {str(e)}")
            if self.config.enabled:
                raise
                
    async def get_page_bypass(self, url: str,
                            user_agent: Optional[str] = None,
                            proxy: Optional[str] = None,
                            cookies: Optional[Dict[str, str]] = None,
                            headers: Optional[Dict[str, str]] = None,
                            wait_for: Optional[str] = None,
                            execute_js: Optional[str] = None,
                            screenshot: bool = False,
                            max_retries: Optional[int] = None) -> Dict[str, Any]:
        """
        Bypass CloudFlare and get page content.
        
        Returns:
        {
            'success': bool,
            'url': str,
            'title': str,
            'html_content': str,
            'cookies': dict,
            'status_code': int,
            'response_time': float,
            'js_result': any (if execute_js provided),
            'screenshot': str (base64 if screenshot=True)
        }
        """
        
        if not self.config.enabled:
            return {
                'success': False,
                'url': url,
                'error': 'CloudFlare-Scrape is disabled'
            }
            
        max_retries = max_retries or self.config.max_retries
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Retry attempt {attempt}/{max_retries} for {url}")
                    await asyncio.sleep(self.config.retry_delay * attempt)
                    
                result = await self.manager.bypass_cloudflare(
                    url=url,
                    user_agent=user_agent,
                    proxy=proxy,
                    cookies=cookies,
                    headers=headers,
                    wait_for=wait_for,
                    execute_js=execute_js,
                    screenshot=screenshot
                )
                
                if result['success']:
                    result['method'] = 'cloudflare-scrape'
                    return result
                else:
                    last_error = result['error']
                    # Don't retry certain error types
                    if result.get('error_type') in ['script_error', 'parse_error']:
                        break
                        
            except Exception as e:
                last_error = str(e)
                logger.error(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                
        return {
            'success': False,
            'url': url,
            'error': last_error or 'All retry attempts failed',
            'method': 'cloudflare-scrape'
        }
        
    async def execute_js_on_page(self, url: str, script: str,
                               **kwargs) -> Dict[str, Any]:
        """Execute JavaScript on a CloudFlare-protected page"""
        
        return await self.get_page_bypass(
            url=url,
            execute_js=script,
            **kwargs
        )
        
    async def take_screenshot(self, url: str, **kwargs) -> Dict[str, Any]:
        """Take a screenshot of a CloudFlare-protected page"""
        
        return await self.get_page_bypass(
            url=url,
            screenshot=True,
            **kwargs
        )
        
    async def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            'enabled': self.config.enabled,
            'config': asdict(self.config),
            'manager_stats': self.manager.get_stats()
        }
        
    async def cleanup(self):
        """Clean up all resources"""
        await self.manager.cleanup()

# Factory function
def create_cloudflare_scrape_adapter(config: Dict[str, Any]) -> CloudFlareScrapeAdapter:
    """Create and configure CloudFlare-Scrape adapter"""
    return CloudFlareScrapeAdapter(config)

# Example usage
async def main():
    """Example usage"""
    config = {
        'enabled': True,
        'debug': True,
        'timeout': 60,
        'auto_install': True
    }
    
    adapter = create_cloudflare_scrape_adapter(config)
    
    try:
        await adapter.initialize()
        
        # Test CloudFlare bypass
        result = await adapter.get_page_bypass(
            'https://nowsecure.nl',
            wait_for='body',
            screenshot=False
        )
        
        if result['success']:
            print(f"✅ Success: {result['title']}")
            print(f"Content length: {len(result['html_content'])}")
        else:
            print(f"❌ Failed: {result['error']}")
            
    finally:
        await adapter.cleanup()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
