"""
Advanced Selenium Stealth Integration for Ultimate Scraping System

Integrerar selenium-stealth-biblioteket med förbättringar för maximal anti-detection.
Kombinerar selenium-stealth funktionalitet med våra egna avancerade tekniker för
optimal skydd mot bot-detektering.

Baserat på: https://github.com/diprajpatra/selenium-stealth
"""

import logging
import random
import time
import json
import hashlib
import uuid
import os
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from pathlib import Path

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.webdriver import WebDriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available - Advanced Selenium Stealth disabled")

try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False

# Försök importera original selenium-stealth
try:
    from selenium_stealth import stealth
    SELENIUM_STEALTH_AVAILABLE = True
except ImportError:
    SELENIUM_STEALTH_AVAILABLE = False

# Browser fingerprint data
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
]

PLATFORMS = ["Win32", "MacIntel", "Linux x86_64"]
VENDORS = ["Google Inc.", "Intel Inc.", "Microsoft Corporation"]
WEBGL_VENDORS = ["Intel Inc.", "Google Inc. (Intel)", "NVIDIA Corporation", "AMD"]
WEBGL_RENDERERS = [
    "Intel Iris OpenGL Engine",
    "Intel HD Graphics 630",
    "NVIDIA GeForce GTX 1060",
    "AMD Radeon RX 580",
    "Intel UHD Graphics 620"
]

LANGUAGES = [
    ["en-US", "en"],
    ["en-GB", "en"], 
    ["de-DE", "de", "en"],
    ["fr-FR", "fr", "en"],
    ["es-ES", "es", "en"],
    ["ja-JP", "ja", "en"]
]

@dataclass
class AdvancedStealthConfig:
    """Avancerad konfiguration för selenium stealth"""
    
    # Grundläggande stealth-inställningar
    user_agent: Optional[str] = None
    languages: List[str] = field(default_factory=lambda: random.choice(LANGUAGES))
    vendor: str = field(default_factory=lambda: random.choice(VENDORS))
    platform: str = field(default_factory=lambda: random.choice(PLATFORMS))
    webgl_vendor: str = field(default_factory=lambda: random.choice(WEBGL_VENDORS))
    renderer: str = field(default_factory=lambda: random.choice(WEBGL_RENDERERS))
    fix_hairline: bool = True
    run_on_insecure_origins: bool = True
    
    # Avancerade inställningar
    randomize_canvas: bool = True
    randomize_audio: bool = True
    block_webrtc: bool = True
    fake_battery: bool = True
    randomize_screen_size: bool = True
    randomize_timezone: bool = True
    enable_proxy_rotation: bool = True
    
    # Beteende-inställningar
    human_behavior_enabled: bool = True
    random_delays: Tuple[float, float] = (1.0, 3.0)
    mouse_movement: bool = True
    scroll_simulation: bool = True
    
    # Advanced evasion
    use_undetected_chrome: bool = True
    rotate_fingerprint_interval: int = 300  # seconds
    max_detection_retries: int = 3
    
    def randomize(self):
        """Randomisera konfiguration för variation"""
        self.user_agent = random.choice(USER_AGENTS)
        self.languages = random.choice(LANGUAGES)
        self.vendor = random.choice(VENDORS)
        self.platform = random.choice(PLATFORMS)
        self.webgl_vendor = random.choice(WEBGL_VENDORS)
        self.renderer = random.choice(WEBGL_RENDERERS)


class AdvancedSeleniumStealth:
    """
    Avancerad Selenium Stealth Engine med förbättrade anti-detection tekniker
    """
    
    def __init__(self, config: Optional[AdvancedStealthConfig] = None):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium required for Advanced Selenium Stealth")
            
        self.config = config or AdvancedStealthConfig()
        self.drivers = {}  # Active drivers
        self.detection_events = []
        self.last_fingerprint_rotation = 0
        
        # Statistics
        self.stats = {
            'drivers_created': 0,
            'stealth_applications': 0,
            'detection_events': 0,
            'successful_navigations': 0,
            'failed_navigations': 0,
            'fingerprint_rotations': 0
        }
        
        logging.info("Advanced Selenium Stealth initialized")
        
    def create_stealth_driver(self, 
                            headless: bool = True,
                            proxy: Optional[str] = None,
                            user_data_dir: Optional[str] = None,
                            **kwargs) -> WebDriver:
        """Skapa en stealth-optimerad WebDriver"""
        
        # Rotera fingerprint om nödvändigt
        if (time.time() - self.last_fingerprint_rotation > 
            self.config.rotate_fingerprint_interval):
            self._rotate_fingerprint()
            
        driver = None
        
        try:
            # Försök använda undetected-chromedriver först
            if self.config.use_undetected_chrome and UNDETECTED_CHROME_AVAILABLE:
                driver = self._create_undetected_driver(headless, proxy, user_data_dir, **kwargs)
            else:
                driver = self._create_standard_driver(headless, proxy, user_data_dir, **kwargs)
                
            # Applicera stealth-tekniker
            self._apply_stealth_techniques(driver)
            
            # Registrera driver
            driver_id = str(uuid.uuid4())
            self.drivers[driver_id] = {
                'driver': driver,
                'created_at': time.time(),
                'config': self.config,
                'proxy': proxy
            }
            
            self.stats['drivers_created'] += 1
            logging.info(f"Stealth driver created: {driver_id}")
            return driver
            
        except Exception as e:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            logging.error(f"Failed to create stealth driver: {e}")
            raise
            
    def _create_undetected_driver(self, 
                                headless: bool,
                                proxy: Optional[str],
                                user_data_dir: Optional[str],
                                **kwargs) -> WebDriver:
        """Skapa driver med undetected-chromedriver"""
        
        options = uc.ChromeOptions()
        
        # Grundläggande stealth-argumenter
        stealth_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
            '--disable-gpu',
            '--disable-sync',
            '--disable-translate',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-client-side-phishing-detection',
            '--hide-scrollbars',
            '--mute-audio',
            '--disable-popup-blocking',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-domain-reliability',
            '--disable-component-extensions-with-background-pages',
            '--disable-background-mode',
            '--disable-features=TranslateUI,VizServiceSharedBitmapManager',
            '--disable-ipc-flooding-protection',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--no-crash-upload',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--ignore-certificate-errors',
            '--ignore-ssl-errors',
            '--ignore-certificate-errors-spki-list'
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
            
        # User agent
        if self.config.user_agent:
            options.add_argument(f'--user-agent={self.config.user_agent}')
            
        # Proxy
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        # User data directory
        if user_data_dir:
            options.add_argument(f'--user-data-dir={user_data_dir}')
            
        # Headless
        if headless:
            options.add_argument('--headless=new')
            
        # Experimental options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Preferences
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "geolocation": 2,
                "media_stream": 2,
            },
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 2,
            "profile.password_manager_enabled": False,
            "credentials_enable_service": False
        }
        options.add_experimental_option("prefs", prefs)
        
        return uc.Chrome(options=options, **kwargs)
        
    def _create_standard_driver(self,
                              headless: bool,
                              proxy: Optional[str], 
                              user_data_dir: Optional[str],
                              **kwargs) -> WebDriver:
        """Skapa standard Chrome WebDriver med stealth-optimering"""
        
        options = Options()
        
        # Samma stealth-argumenter som undetected
        stealth_args = [
            '--no-sandbox',
            '--disable-dev-shm-usage', 
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
            '--disable-gpu',
            '--disable-sync',
            '--disable-translate',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-client-side-phishing-detection',
            '--hide-scrollbars',
            '--mute-audio',
            '--disable-popup-blocking',
            '--disable-hang-monitor',
            '--disable-prompt-on-repost',
            '--disable-domain-reliability',
            '--disable-component-extensions-with-background-pages',
            '--disable-background-mode',
            '--disable-features=TranslateUI,VizServiceSharedBitmapManager',
            '--disable-ipc-flooding-protection',
            '--disable-field-trial-config',
            '--disable-back-forward-cache',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--no-crash-upload'
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
            
        # User agent
        if self.config.user_agent:
            options.add_argument(f'--user-agent={self.config.user_agent}')
            
        # Proxy
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
            
        # User data directory
        if user_data_dir:
            options.add_argument(f'--user-data-dir={user_data_dir}')
            
        # Headless
        if headless:
            options.add_argument('--headless=new')
            
        # Experimental options
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return webdriver.Chrome(options=options, **kwargs)
        
    def _apply_stealth_techniques(self, driver: WebDriver):
        """Applicera alla stealth-tekniker på driver"""
        
        try:
            # Applicera original selenium-stealth om tillgängligt
            if SELENIUM_STEALTH_AVAILABLE:
                stealth(
                    driver,
                    user_agent=self.config.user_agent,
                    languages=self.config.languages,
                    vendor=self.config.vendor,
                    platform=self.config.platform,
                    webgl_vendor=self.config.webgl_vendor,
                    renderer=self.config.renderer,
                    fix_hairline=self.config.fix_hairline,
                    run_on_insecure_origins=self.config.run_on_insecure_origins
                )
            else:
                # Applicera våra egna stealth-skript
                self._apply_custom_stealth_scripts(driver)
                
            # Applicera ytterligare avancerade tekniker
            self._apply_advanced_stealth(driver)
            
            self.stats['stealth_applications'] += 1
            logging.info("Stealth techniques applied successfully")
            
        except Exception as e:
            logging.error(f"Failed to apply stealth techniques: {e}")
            raise
            
    def _apply_custom_stealth_scripts(self, driver: WebDriver):
        """Applicera anpassade stealth-skript"""
        
        # Base stealth script
        stealth_script = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock chrome object
        window.chrome = {
            runtime: {},
            app: {
                isInstalled: false,
            },
            webstore: {
                onInstallStageChanged: {},
                onDownloadProgress: {},
            },
        };
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // Override plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
        
        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        """
        
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': stealth_script
        })
        
    def _apply_advanced_stealth(self, driver: WebDriver):
        """Applicera avancerade stealth-tekniker"""
        
        advanced_scripts = []
        
        # Canvas fingerprinting protection
        if self.config.randomize_canvas:
            advanced_scripts.append(self._get_canvas_protection_script())
            
        # Audio fingerprinting protection
        if self.config.randomize_audio:
            advanced_scripts.append(self._get_audio_protection_script())
            
        # WebRTC blocking
        if self.config.block_webrtc:
            advanced_scripts.append(self._get_webrtc_block_script())
            
        # Battery API spoofing
        if self.config.fake_battery:
            advanced_scripts.append(self._get_battery_spoof_script())
            
        # Screen size randomization
        if self.config.randomize_screen_size:
            advanced_scripts.append(self._get_screen_randomization_script())
            
        # Timezone randomization
        if self.config.randomize_timezone:
            advanced_scripts.append(self._get_timezone_spoof_script())
            
        # Applicera alla skript
        for script in advanced_scripts:
            try:
                driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                    'source': script
                })
            except Exception as e:
                logging.warning(f"Failed to apply advanced script: {e}")
                
    def _get_canvas_protection_script(self) -> str:
        """Canvas fingerprinting protection script"""
        return """
        (() => {
            const getContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                const context = getContext.call(this, type, attributes);
                if (type === '2d') {
                    const imageData = context.getImageData;
                    context.getImageData = function(sx, sy, sw, sh) {
                        const data = imageData.call(this, sx, sy, sw, sh);
                        // Add subtle noise
                        for (let i = 0; i < data.data.length; i += 4) {
                            if (Math.random() < 0.001) {
                                data.data[i] = Math.min(255, data.data[i] + 1);
                            }
                        }
                        return data;
                    };
                }
                return context;
            };
        })();
        """
        
    def _get_audio_protection_script(self) -> str:
        """Audio fingerprinting protection script"""
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
                        // Add subtle noise
                        for (let i = 0; i < array.length; i++) {
                            array[i] += (Math.random() - 0.5) * 0.0001;
                        }
                    };
                    return analyser;
                };
            }
        })();
        """
        
    def _get_webrtc_block_script(self) -> str:
        """WebRTC blocking script"""
        return """
        (() => {
            const RTCPeerConnection = window.RTCPeerConnection || 
                                    window.webkitRTCPeerConnection || 
                                    window.mozRTCPeerConnection;
            if (RTCPeerConnection) {
                window.RTCPeerConnection = function() {
                    throw new Error('WebRTC blocked');
                };
                window.webkitRTCPeerConnection = window.RTCPeerConnection;
                window.mozRTCPeerConnection = window.RTCPeerConnection;
            }
        })();
        """
        
    def _get_battery_spoof_script(self) -> str:
        """Battery API spoofing script"""
        return """
        (() => {
            if ('getBattery' in navigator) {
                navigator.getBattery = () => Promise.resolve({
                    charging: true,
                    chargingTime: Infinity,
                    dischargingTime: Infinity,
                    level: 0.85 + Math.random() * 0.1
                });
            }
        })();
        """
        
    def _get_screen_randomization_script(self) -> str:
        """Screen size randomization script"""
        offset_w = random.randint(-5, 5)
        offset_h = random.randint(-5, 5)
        
        return f"""
        (() => {{
            Object.defineProperty(screen, 'width', {{
                get: () => screen.width + {offset_w}
            }});
            Object.defineProperty(screen, 'height', {{
                get: () => screen.height + {offset_h}
            }});
        }})();
        """
        
    def _get_timezone_spoof_script(self) -> str:
        """Timezone spoofing script"""
        offset = random.randint(-720, 720)
        
        return f"""
        (() => {{
            const getTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {{
                return {offset};
            }};
        }})();
        """
        
    def navigate_with_stealth(self,
                            driver: WebDriver,
                            url: str,
                            timeout: int = 30,
                            retry_on_detection: bool = True) -> bool:
        """Navigera med stealth-tekniker och mänskligt beteende"""
        
        try:
            # Pre-navigation delay
            if self.config.human_behavior_enabled:
                delay = random.uniform(*self.config.random_delays)
                time.sleep(delay)
                
            # Navigate
            driver.get(url)
            
            # Wait for page load
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Simulate human behavior
            if self.config.human_behavior_enabled:
                self._simulate_human_behavior(driver)
                
            # Check for detection
            if self._check_for_detection(driver):
                self.stats['detection_events'] += 1
                
                if retry_on_detection and self.stats['detection_events'] < self.config.max_detection_retries:
                    logging.warning("Bot detection detected, applying countermeasures...")
                    self._apply_countermeasures(driver)
                    return self.navigate_with_stealth(driver, url, timeout, False)
                else:
                    logging.error("Bot detection detected, max retries reached")
                    self.stats['failed_navigations'] += 1
                    return False
                    
            self.stats['successful_navigations'] += 1
            return True
            
        except Exception as e:
            logging.error(f"Navigation failed: {e}")
            self.stats['failed_navigations'] += 1
            return False
            
    def _simulate_human_behavior(self, driver: WebDriver):
        """Simulera mänskligt beteende"""
        
        try:
            # Mouse movement
            if self.config.mouse_movement:
                self._simulate_mouse_movement(driver)
                
            # Scrolling
            if self.config.scroll_simulation:
                self._simulate_scrolling(driver)
                
            # Random pause
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            logging.debug(f"Human behavior simulation failed: {e}")
            
    def _simulate_mouse_movement(self, driver: WebDriver):
        """Simulera musrörelser"""
        
        try:
            actions = ActionChains(driver)
            
            # Get window size
            size = driver.get_window_size()
            width, height = size['width'], size['height']
            
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(0, width)
                y = random.randint(0, height)
                actions.move_by_offset(x, y)
                time.sleep(random.uniform(0.1, 0.3))
                
            actions.perform()
            
        except Exception as e:
            logging.debug(f"Mouse simulation failed: {e}")
            
    def _simulate_scrolling(self, driver: WebDriver):
        """Simulera scrollning"""
        
        try:
            # Get page height
            page_height = driver.execute_script("return document.body.scrollHeight")
            viewport_height = driver.execute_script("return window.innerHeight")
            
            if page_height <= viewport_height:
                return
                
            # Random scroll
            scroll_amount = random.randint(100, 500)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            logging.debug(f"Scroll simulation failed: {e}")
            
    def _check_for_detection(self, driver: WebDriver) -> bool:
        """Kontrollera om bot-detektering upptäckts"""
        
        detection_indicators = [
            "access denied",
            "blocked",
            "bot detected",
            "suspicious activity", 
            "captcha",
            "cloudflare",
            "ddos protection",
            "rate limit"
        ]
        
        try:
            page_source = driver.page_source.lower()
            page_title = driver.title.lower()
            
            for indicator in detection_indicators:
                if indicator in page_source or indicator in page_title:
                    logging.warning(f"Detection indicator found: {indicator}")
                    return True
                    
            # Check response status via JavaScript
            status_code = driver.execute_script("return document.readyState")
            if status_code != "complete":
                return True
                
        except Exception as e:
            logging.debug(f"Detection check failed: {e}")
            
        return False
        
    def _apply_countermeasures(self, driver: WebDriver):
        """Applicera motåtgärder vid detektering"""
        
        # Rotate fingerprint
        self._rotate_fingerprint()
        
        # Clear cookies and cache
        try:
            driver.delete_all_cookies()
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
        except Exception as e:
            logging.debug(f"Cache clearing failed: {e}")
            
        # Extended delay
        time.sleep(random.uniform(10.0, 30.0))
        
    def _rotate_fingerprint(self):
        """Rotera browser fingerprint"""
        
        self.config.randomize()
        self.last_fingerprint_rotation = time.time()
        self.stats['fingerprint_rotations'] += 1
        
        logging.info("Browser fingerprint rotated")
        
    def close_driver(self, driver: WebDriver):
        """Stäng driver säkert"""
        
        try:
            driver.quit()
            
            # Remove from registry
            for driver_id, data in list(self.drivers.items()):
                if data['driver'] == driver:
                    del self.drivers[driver_id]
                    break
                    
        except Exception as e:
            logging.error(f"Error closing driver: {e}")
            
    def close_all_drivers(self):
        """Stäng alla aktiva drivers"""
        
        for driver_id, data in list(self.drivers.items()):
            try:
                data['driver'].quit()
            except Exception as e:
                logging.error(f"Error closing driver {driver_id}: {e}")
                
        self.drivers.clear()
        logging.info("All drivers closed")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Få statistik över stealth-prestanda"""
        
        success_rate = 0.0
        total_navigations = self.stats['successful_navigations'] + self.stats['failed_navigations']
        
        if total_navigations > 0:
            success_rate = (self.stats['successful_navigations'] / total_navigations) * 100
            
        return {
            **self.stats,
            'active_drivers': len(self.drivers),
            'success_rate': round(success_rate, 2),
            'detection_rate': round((self.stats['detection_events'] / max(1, total_navigations)) * 100, 2)
        }


# Factory function
def create_advanced_stealth_driver(headless: bool = True,
                                 proxy: Optional[str] = None,
                                 config: Optional[AdvancedStealthConfig] = None) -> Tuple[WebDriver, AdvancedSeleniumStealth]:
    """Factory function för att skapa stealth driver"""
    
    stealth_engine = AdvancedSeleniumStealth(config)
    driver = stealth_engine.create_stealth_driver(headless=headless, proxy=proxy)
    
    return driver, stealth_engine


if __name__ == "__main__":
    # Demo av Advanced Selenium Stealth
    print("🥷 Advanced Selenium Stealth Integration Demo")
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not available - cannot run demo")
        exit(1)
        
    try:
        # Create stealth configuration
        config = AdvancedStealthConfig(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            human_behavior_enabled=True,
            use_undetected_chrome=False  # Disable undetected chrome for compatibility
        )
        
        # Create stealth engine
        stealth_engine = AdvancedSeleniumStealth(config)
        
        print(f"✅ Stealth engine created")
        print(f"🔧 Using undetected chrome: {config.use_undetected_chrome}")
        print(f"🤖 Human behavior enabled: {config.human_behavior_enabled}")
        
        # Create stealth driver
        driver = stealth_engine.create_stealth_driver(headless=True)
        
        print(f"🌐 Testing stealth navigation...")
        
        # Test navigation
        success = stealth_engine.navigate_with_stealth(
            driver, 
            "https://httpbin.org/user-agent"
        )
        
        if success:
            # Extract user agent
            page_source = driver.page_source
            print(f"✅ Navigation successful!")
            print(f"📄 Page length: {len(page_source)} chars")
            
            # Get detected user agent
            try:
                user_agent = driver.execute_script("return navigator.userAgent")
                print(f"🕵️ Detected User Agent: {user_agent[:100]}...")
            except:
                pass
        else:
            print(f"❌ Navigation failed")
            
        # Get statistics
        stats = stealth_engine.get_statistics()
        print(f"\n📊 Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
            
        # Cleanup
        stealth_engine.close_driver(driver)
        print(f"\n🎉 Advanced Selenium Stealth demo completed!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
