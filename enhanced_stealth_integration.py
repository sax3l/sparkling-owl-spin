"""
Enhanced Playwright Stealth Integration for Ultimate Scraping System

Integrerar playwright_stealth-funktionalitet för att maskera browser fingerprinting
och undvika detektering. Stöder både Playwright och Selenium WebDriver med
avancerade anti-detektionsstrategier.

Baserat på: https://github.com/AtuboDad/playwright_stealth
"""

import json
import logging
import random
import string
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
import time

# Importera stealth-skript från playwright_stealth
try:
    from playwright_stealth.stealth import Stealth
    PLAYWRIGHT_STEALTH_AVAILABLE = True
    SCRIPTS = {}  # Modern playwright-stealth doesn't expose SCRIPTS directly
except ImportError:
    PLAYWRIGHT_STEALTH_AVAILABLE = False
    SCRIPTS = {}

try:
    from playwright.async_api import Page as AsyncPage, BrowserContext as AsyncBrowserContext
    from playwright.sync_api import Page as SyncPage, BrowserContext as SyncBrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# User agents pool för rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# WebGL vendors och renderers för fingerprint masking
WEBGL_VENDORS = [
    "Google Inc. (Intel)",
    "Google Inc. (NVIDIA)",
    "Google Inc. (AMD)",
    "Intel Inc.",
    "NVIDIA Corporation",
    "Advanced Micro Devices, Inc."
]

WEBGL_RENDERERS = [
    "Intel Iris OpenGL Engine",
    "Intel HD Graphics 630",
    "NVIDIA GeForce GTX 1060",
    "AMD Radeon RX 580",
    "Intel UHD Graphics 620",
    "NVIDIA GeForce RTX 3060"
]

PLATFORMS = [
    "Win32",
    "MacIntel",
    "Linux x86_64"
]

LANGUAGES = [
    ("en-US", "en"),
    ("en-GB", "en"),
    ("en-CA", "en"),
    ("fr-FR", "fr"),
    ("de-DE", "de"),
    ("es-ES", "es")
]

@dataclass
class EnhancedStealthConfig:
    """
    Förbättrad stealth-konfiguration med fler anti-detektionsstrategier
    """
    
    # Playwright stealth options
    webdriver: bool = True
    webgl_vendor: bool = True
    chrome_app: bool = True
    chrome_csi: bool = True
    chrome_load_times: bool = True
    chrome_runtime: bool = True
    iframe_content_window: bool = True
    media_codecs: bool = True
    navigator_hardware_concurrency: int = field(default_factory=lambda: random.randint(2, 16))
    navigator_languages: bool = True
    navigator_permissions: bool = True
    navigator_platform: bool = True
    navigator_plugins: bool = True
    navigator_user_agent: bool = True
    navigator_vendor: bool = True
    outerdimensions: bool = True
    hairline: bool = True

    # Anpassningsbara egenskaper
    vendor: str = field(default_factory=lambda: random.choice(WEBGL_VENDORS))
    renderer: str = field(default_factory=lambda: random.choice(WEBGL_RENDERERS))
    nav_vendor: str = "Google Inc."
    nav_user_agent: Optional[str] = field(default_factory=lambda: random.choice(USER_AGENTS))
    nav_platform: Optional[str] = field(default_factory=lambda: random.choice(PLATFORMS))
    languages: Tuple[str] = field(default_factory=lambda: random.choice(LANGUAGES))
    runOnInsecureOrigins: Optional[bool] = None
    
    # Ytterligare anti-detection
    randomize_canvas: bool = True
    randomize_audio: bool = True
    block_webrtc: bool = True
    randomize_screen_size: bool = True
    fake_battery: bool = True
    randomize_timezone: bool = True
    
    def to_playwright_config(self) -> Optional[Dict[str, Any]]:
        """Konverterar config till format som kan användas med playwright-stealth"""
        if PLAYWRIGHT_STEALTH_AVAILABLE:
            # Modern playwright-stealth uses all evasions by default
            return {}
        return None

class EnhancedStealthManager:
    """
    Förbättrad stealth manager med stöd för både Playwright och Selenium
    """
    
    def __init__(self, config: Optional[EnhancedStealthConfig] = None):
        self.config = config or EnhancedStealthConfig()
        self.stats = {
            'pages_stealthed': 0,
            'playwright_pages': 0,
            'selenium_pages': 0,
            'scripts_injected': 0
        }
        
    def stealth_playwright_sync(self, page: 'SyncPage') -> bool:
        """Applicera stealth på synkron Playwright-sida"""
        
        if not PLAYWRIGHT_AVAILABLE or not PLAYWRIGHT_STEALTH_AVAILABLE:
            logging.warning("Playwright eller playwright_stealth inte tillgängligt")
            return False
            
        try:
            playwright_config = self.config.to_playwright_config()
            if playwright_config is not None:
                # Använd modern playwright-stealth Stealth class
                stealth = Stealth()
                stealth.apply_stealth_sync(page)
                
                # Lägg till extra skript
                self._add_extra_scripts_sync(page)
                
                self.stats['pages_stealthed'] += 1
                self.stats['playwright_pages'] += 1
                logging.info("Playwright sync stealth applied successfully")
                return True
                
        except Exception as e:
            logging.error(f"Error applying Playwright sync stealth: {e}")
            
        return False
        
    async def stealth_playwright_async(self, page: 'AsyncPage') -> bool:
        """Applicera stealth på asynkron Playwright-sida"""
        
        if not PLAYWRIGHT_AVAILABLE or not PLAYWRIGHT_STEALTH_AVAILABLE:
            logging.warning("Playwright eller playwright_stealth inte tillgängligt")
            return False
            
        try:
            playwright_config = self.config.to_playwright_config()
            if playwright_config is not None:
                # Använd modern playwright-stealth Stealth class
                stealth = Stealth()
                await stealth.apply_stealth_async(page)
                
                # Lägg till extra skript
                await self._add_extra_scripts_async(page)
                
                self.stats['pages_stealthed'] += 1
                self.stats['playwright_pages'] += 1
                logging.info("Playwright async stealth applied successfully")
                return True
                
        except Exception as e:
            logging.error(f"Error applying Playwright async stealth: {e}")
            
        return False
        
    def stealth_selenium(self, driver: 'WebDriver') -> bool:
        """Applicera stealth på Selenium WebDriver"""
        
        if not SELENIUM_AVAILABLE:
            logging.warning("Selenium inte tillgängligt")
            return False
            
        try:
            # Injicera stealth-skript i Selenium
            scripts_injected = 0
            
            # Base options för skripten
            opts = {
                'webgl_vendor': self.config.vendor,
                'webgl_renderer': self.config.renderer,
                'navigator_vendor': self.config.nav_vendor,
                'navigator_platform': self.config.nav_platform,
                'navigator_user_agent': self.config.nav_user_agent,
                'languages': list(self.config.languages),
                'runOnInsecureOrigins': self.config.runOnInsecureOrigins,
            }
            
            # Injicera options
            driver.execute_script(f"window.stealthOpts = {json.dumps(opts)};")
            
            # Injicera stealth-skript
            if PLAYWRIGHT_STEALTH_AVAILABLE:
                for script_name, script_content in SCRIPTS.items():
                    if self._should_inject_script(script_name):
                        try:
                            driver.execute_script(script_content)
                            scripts_injected += 1
                        except Exception as e:
                            logging.warning(f"Failed to inject script {script_name}: {e}")
                            
            # Injicera extra stealth-skript
            extra_scripts = self._get_extra_selenium_scripts()
            for script in extra_scripts:
                try:
                    driver.execute_script(script)
                    scripts_injected += 1
                except Exception as e:
                    logging.warning(f"Failed to inject extra script: {e}")
                    
            self.stats['pages_stealthed'] += 1
            self.stats['selenium_pages'] += 1
            self.stats['scripts_injected'] += scripts_injected
            
            logging.info(f"Selenium stealth applied successfully ({scripts_injected} scripts)")
            return True
            
        except Exception as e:
            logging.error(f"Error applying Selenium stealth: {e}")
            
        return False
        
    def _should_inject_script(self, script_name: str) -> bool:
        """Bestäm om ett skript ska injiceras baserat på konfiguration"""
        
        script_map = {
            'chrome_app': self.config.chrome_app,
            'chrome_csi': self.config.chrome_csi,
            'chrome_load_times': self.config.chrome_load_times,
            'chrome_runtime': self.config.chrome_runtime,
            'chrome_hairline': self.config.hairline,
            'iframe_content_window': self.config.iframe_content_window,
            'media_codecs': self.config.media_codecs,
            'navigator_languages': self.config.navigator_languages,
            'navigator_permissions': self.config.navigator_permissions,
            'navigator_platform': self.config.navigator_platform,
            'navigator_plugins': self.config.navigator_plugins,
            'navigator_user_agent': self.config.navigator_user_agent,
            'navigator_vendor': self.config.navigator_vendor,
            'navigator_hardware_concurrency': True,  # Alltid på
            'outerdimensions': self.config.outerdimensions,
            'webdriver': self.config.webdriver,
            'webgl_vendor': self.config.webgl_vendor,
            'utils': True,  # Alltid på
            'generate_magic_arrays': True  # Alltid på
        }
        
        return script_map.get(script_name, False)
        
    def _add_extra_scripts_sync(self, page: 'SyncPage'):
        """Lägg till extra stealth-skript för Playwright sync"""
        
        extra_scripts = self._get_extra_scripts()
        for script in extra_scripts:
            page.add_init_script(script)
            
    async def _add_extra_scripts_async(self, page: 'AsyncPage'):
        """Lägg till extra stealth-skript för Playwright async"""
        
        extra_scripts = self._get_extra_scripts()
        for script in extra_scripts:
            await page.add_init_script(script)
            
    def _get_extra_scripts(self) -> List[str]:
        """Få extra stealth-skript för Playwright"""
        
        scripts = []
        
        if self.config.randomize_canvas:
            scripts.append(self._get_canvas_randomization_script())
            
        if self.config.randomize_audio:
            scripts.append(self._get_audio_randomization_script())
            
        if self.config.block_webrtc:
            scripts.append(self._get_webrtc_block_script())
            
        if self.config.randomize_screen_size:
            scripts.append(self._get_screen_randomization_script())
            
        if self.config.fake_battery:
            scripts.append(self._get_battery_fake_script())
            
        if self.config.randomize_timezone:
            scripts.append(self._get_timezone_randomization_script())
            
        return scripts
        
    def _get_extra_selenium_scripts(self) -> List[str]:
        """Få extra stealth-skript för Selenium"""
        return self._get_extra_scripts()  # Samma skript fungerar
        
    def _get_canvas_randomization_script(self) -> str:
        """Skript för att randomisera canvas fingerprinting"""
        return """
        (() => {
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                const context = getContext.call(this, type, attributes);
                if (type === '2d') {
                    const imageData = context.getImageData;
                    context.getImageData = function(sx, sy, sw, sh) {
                        const data = imageData.call(this, sx, sy, sw, sh);
                        for (let i = 0; i < data.data.length; i += 4) {
                            data.data[i] += Math.random() < 0.1 ? 1 : 0;
                        }
                        return data;
                    };
                }
                return context;
            };
        })();
        """
        
    def _get_audio_randomization_script(self) -> str:
        """Skript för att randomisera audio fingerprinting"""
        return """
        (() => {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                const createAnalyser = AudioContext.prototype.createAnalyser;
                AudioContext.prototype.createAnalyser = function() {
                    const analyser = createAnalyser.call(this);
                    const getFloatFrequencyData = analyser.getFloatFrequencyData;
                    analyser.getFloatFrequencyData = function(array) {
                        getFloatFrequencyData.call(this, array);
                        for (let i = 0; i < array.length; i++) {
                            array[i] += Math.random() * 0.001;
                        }
                    };
                    return analyser;
                };
            }
        })();
        """
        
    def _get_webrtc_block_script(self) -> str:
        """Skript för att blockera WebRTC IP-läckage"""
        return """
        (() => {
            const RTCPeerConnection = window.RTCPeerConnection || 
                                    window.webkitRTCPeerConnection || 
                                    window.mozRTCPeerConnection;
            if (RTCPeerConnection) {
                window.RTCPeerConnection = function() {
                    throw new Error('WebRTC blocked for privacy');
                };
                window.webkitRTCPeerConnection = window.RTCPeerConnection;
                window.mozRTCPeerConnection = window.RTCPeerConnection;
            }
        })();
        """
        
    def _get_screen_randomization_script(self) -> str:
        """Skript för att randomisera skärm-fingerprinting"""
        width_offset = random.randint(-10, 10)
        height_offset = random.randint(-10, 10)
        
        return f"""
        (() => {{
            Object.defineProperty(screen, 'width', {{
                get: () => screen.width + {width_offset}
            }});
            Object.defineProperty(screen, 'height', {{
                get: () => screen.height + {height_offset}
            }});
            Object.defineProperty(screen, 'availWidth', {{
                get: () => screen.availWidth + {width_offset}
            }});
            Object.defineProperty(screen, 'availHeight', {{
                get: () => screen.availHeight + {height_offset}
            }});
        }})();
        """
        
    def _get_battery_fake_script(self) -> str:
        """Skript för att dölja batteristatus"""
        return """
        (() => {
            if ('getBattery' in navigator) {
                navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: Infinity,
                    dischargingTime: Infinity,
                    level: Math.random()
                });
            }
        })();
        """
        
    def _get_timezone_randomization_script(self) -> str:
        """Skript för att randomisera timezone"""
        timezones = ['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo']
        selected_tz = random.choice(timezones)
        offset = random.randint(-720, 720)
        
        return f"""
        (() => {{
            const getTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {{
                return {offset};  // Random timezone offset
            }};
            
            if (Intl && Intl.DateTimeFormat) {{
                const resolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
                Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
                    const options = resolvedOptions.call(this);
                    options.timeZone = '{selected_tz}';
                    return options;
                }};
            }}
        }})();
        """
        
    def randomize_config(self):
        """Randomisera konfiguration för ökad variation"""
        
        self.config.vendor = random.choice(WEBGL_VENDORS)
        self.config.renderer = random.choice(WEBGL_RENDERERS)
        self.config.nav_user_agent = random.choice(USER_AGENTS)
        self.config.nav_platform = random.choice(PLATFORMS)
        self.config.languages = random.choice(LANGUAGES)
        self.config.navigator_hardware_concurrency = random.randint(2, 16)
        
        logging.info("Stealth config randomized")
        
    def get_stats(self) -> Dict[str, Any]:
        """Få statistik över stealth-tillämpningar"""
        return self.stats.copy()


class StealthBrowserFactory:
    """
    Factory för att skapa stealth-aktiverade webbläsare
    """
    
    def __init__(self, stealth_manager: Optional[EnhancedStealthManager] = None):
        self.stealth_manager = stealth_manager or EnhancedStealthManager()
        
    def create_stealth_playwright_browser(self, headless: bool = True, **kwargs):
        """Skapa stealth Playwright-webbläsare"""
        
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright inte tillgängligt")
            
        from playwright.sync_api import sync_playwright
        
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=headless, **kwargs)
        
        # Skapa stealth context
        context = browser.new_context(
            user_agent=self.stealth_manager.config.nav_user_agent,
            locale=self.stealth_manager.config.languages[0],
            extra_http_headers={
                'Accept-Language': ', '.join(self.stealth_manager.config.languages)
            }
        )
        
        return browser, context
        
    def create_stealth_selenium_driver(self, **kwargs):
        """Skapa stealth Selenium WebDriver"""
        
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium inte tillgängligt")
            
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        
        # Stealth options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        if self.stealth_manager.config.nav_user_agent:
            options.add_argument(f'--user-agent={self.stealth_manager.config.nav_user_agent}')
            
        driver = webdriver.Chrome(options=options, **kwargs)
        
        # Applicera stealth
        self.stealth_manager.stealth_selenium(driver)
        
        return driver


if __name__ == "__main__":
    # Demo av Enhanced Stealth Integration
    print("🥷 Enhanced Playwright Stealth Integration Demo")
    
    # Test stealth manager
    stealth_manager = EnhancedStealthManager()
    
    print(f"✅ StealthManager created")
    print(f"📝 Config: UA={stealth_manager.config.nav_user_agent[:50]}...")
    print(f"🎯 WebGL Vendor: {stealth_manager.config.vendor}")
    print(f"🖥️ Platform: {stealth_manager.config.nav_platform}")
    
    # Test randomization
    print("\n🎲 Testing config randomization...")
    original_vendor = stealth_manager.config.vendor
    stealth_manager.randomize_config()
    print(f"🔄 Vendor changed: {original_vendor} → {stealth_manager.config.vendor}")
    
    # Test stealth scripts generation
    extra_scripts = stealth_manager._get_extra_scripts()
    print(f"📜 Generated {len(extra_scripts)} extra stealth scripts")
    
    # Test factory
    factory = StealthBrowserFactory(stealth_manager)
    print(f"🏭 StealthBrowserFactory created")
    
    # Show stats
    stats = stealth_manager.get_stats()
    print(f"\n📊 Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🎉 Enhanced Stealth Integration demo completed!")
    print("💡 Ready to create stealth browsers and evade detection!")
