#!/usr/bin/env python3
"""
Enhanced Undetected Browser System för Sparkling-Owl-Spin
Integrerat system med undetected-chromedriver, stealth patches, TLS impersonation
"""

import logging
import asyncio
import json
import time
import tempfile
import os
import platform
import random
import string
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import subprocess
import shutil
from urllib.parse import urlparse

# Import alla tillgängliga browser automation bibliotek
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions  
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False

try:
    from selenium_stealth import stealth
    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False

try:
    from fake_useragent import UserAgent
    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import requests
    import urllib3
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

class BrowserEngine(Enum):
    """Enhanced browser engines"""
    UNDETECTED_CHROME = "undetected_chrome"
    STEALTH_CHROME = "stealth_chrome"
    REGULAR_CHROME = "regular_chrome"
    FIREFOX = "firefox"
    HEADLESS_CHROME = "headless_chrome"
    MOBILE_CHROME = "mobile_chrome"
    CUSTOM_CHROME = "custom_chrome"

class StealthLevel(Enum):
    """Stealth detection avoidance levels"""
    MINIMAL = "minimal"      # Basic user agent spoofing
    MODERATE = "moderate"    # + Canvas/WebGL fingerprinting
    HIGH = "high"           # + JavaScript execution patterns
    MAXIMUM = "maximum"     # + Hardware fingerprinting + timing attacks
    PARANOID = "paranoid"   # + Custom patches + randomization

class DetectionVector(Enum):
    """Detection vectors att skydda mot"""
    USER_AGENT = "user_agent"
    WEBDRIVER_PRESENCE = "webdriver_presence" 
    AUTOMATION_FLAGS = "automation_flags"
    CANVAS_FINGERPRINT = "canvas_fingerprint"
    WEBGL_FINGERPRINT = "webgl_fingerprint"
    AUDIO_FINGERPRINT = "audio_fingerprint"
    SCREEN_RESOLUTION = "screen_resolution"
    TIMEZONE = "timezone"
    LANGUAGE = "language"
    PLUGINS = "plugins"
    FONTS = "fonts"
    HARDWARE_CONCURRENCY = "hardware_concurrency"
    DEVICE_MEMORY = "device_memory"
    PLATFORM = "platform"
    CHROME_RUNTIME = "chrome_runtime"
    PERMISSIONS = "permissions"
    NAVIGATOR_PROPERTIES = "navigator_properties"
    JAVASCRIPT_EXECUTION = "javascript_execution"
    MOUSE_MOVEMENT = "mouse_movement"
    TYPING_PATTERNS = "typing_patterns"
    REQUEST_TIMING = "request_timing"
    TLS_FINGERPRINT = "tls_fingerprint"

@dataclass
class BrowserProfile:
    """Enhanced browser profile för stealth"""
    name: str
    engine: BrowserEngine
    user_agent: Optional[str] = None
    viewport: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    timezone: Optional[str] = None
    language: str = "sv-SE,sv;q=0.9,en;q=0.8"
    platform: Optional[str] = None
    chrome_version: Optional[str] = None
    plugins: List[str] = field(default_factory=list)
    webgl_vendor: Optional[str] = None
    webgl_renderer: Optional[str] = None
    canvas_hash: Optional[str] = None
    screen_info: Dict[str, Any] = field(default_factory=dict)
    hardware_concurrency: int = 8
    device_memory: int = 8
    max_touch_points: int = 0
    permissions: Dict[str, str] = field(default_factory=dict)
    extra_flags: List[str] = field(default_factory=list)
    proxy: Optional[str] = None
    custom_headers: Dict[str, str] = field(default_factory=dict)
    stealth_patches: List[str] = field(default_factory=list)

@dataclass
class BrowserSession:
    """Enhanced browser session management"""
    session_id: str
    driver: Any
    profile: BrowserProfile
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    page_count: int = 0
    stealth_score: float = 0.0
    detection_events: List[str] = field(default_factory=list)
    current_url: Optional[str] = None
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    local_storage: Dict[str, str] = field(default_factory=dict)
    session_storage: Dict[str, str] = field(default_factory=dict)
    javascript_state: Dict[str, Any] = field(default_factory=dict)

class EnhancedUndetectedBrowserAdapter:
    """Enhanced Undetected Browser med alla stealth techniques"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.initialized = False
        
        # Browser sessions
        self.active_sessions: Dict[str, BrowserSession] = {}
        self.profile_templates: Dict[str, BrowserProfile] = {}
        
        # Stealth configuration
        self.stealth_level = StealthLevel.HIGH
        self.enabled_protections: set[DetectionVector] = set()
        
        # Browser binaries och paths
        self.chrome_binary_path: Optional[str] = None
        self.chromedriver_path: Optional[str] = None
        self.firefox_binary_path: Optional[str] = None
        self.geckodriver_path: Optional[str] = None
        
        # Stealth scripts och patches
        self.stealth_scripts: Dict[str, str] = {}
        self.javascript_patches: Dict[str, str] = {}
        
        # User agents och fingerprints
        self.user_agent_pool: List[str] = []
        self.fingerprint_pool: List[Dict[str, Any]] = []
        
        # Penetrationstestning disclaimer
        self.authorized_domains = set()
        
        # Session management
        self.max_sessions = 10
        self.session_timeout = timedelta(hours=1)
        self.session_rotation_interval = timedelta(minutes=30)
        
        # Detection evasion
        self.mouse_movements: List[Dict[str, Any]] = []
        self.typing_patterns: List[Dict[str, Any]] = []
        self.timing_randomization = True
        
        # Statistik
        self.stats = {
            "total_sessions_created": 0,
            "successful_navigations": 0,
            "detection_events": 0,
            "stealth_score_average": 0.0,
            "by_engine": {},
            "by_stealth_level": {},
            "by_detection_vector": {},
            "active_sessions": 0,
            "session_duration_average": 0.0
        }
        
    async def initialize(self):
        """Initialize Enhanced Undetected Browser adapter"""
        try:
            logger.info("🌐 Initializing Enhanced Undetected Browser Adapter (Authorized Pentest Only)")
            
            # Kontrollera tillgängliga browser engines
            available_engines = await self._detect_available_engines()
            logger.info(f"📋 Available browser engines: {', '.join(available_engines)}")
            
            # Konfigurera stealth protection
            await self._configure_stealth_protection()
            
            # Ladda user agent pool
            await self._load_user_agent_pool()
            
            # Ladda fingerprint pool
            await self._load_fingerprint_pool()
            
            # Ladda stealth scripts
            await self._load_stealth_scripts()
            
            # Skapa profile templates
            await self._create_profile_templates()
            
            # Initiera statistik
            for engine in BrowserEngine:
                self.stats["by_engine"][engine.value] = {
                    "sessions": 0,
                    "navigations": 0,
                    "detections": 0,
                    "avg_stealth_score": 0.0
                }
                
            for level in StealthLevel:
                self.stats["by_stealth_level"][level.value] = {
                    "sessions": 0,
                    "avg_stealth_score": 0.0
                }
                
            for vector in DetectionVector:
                self.stats["by_detection_vector"][vector.value] = {
                    "detections": 0,
                    "protection_enabled": vector in self.enabled_protections
                }
            
            self.initialized = True
            logger.info("✅ Enhanced Undetected Browser Adapter initialized för penetrationstestning")
            logger.warning("⚠️ ENDAST FÖR PENETRATIONSTESTNING AV EGNA SERVRAR")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Enhanced Undetected Browser: {str(e)}")
            self.initialized = True  # Continue with basic functionality
            
    async def _detect_available_engines(self) -> List[str]:
        """Detect tillgängliga browser engines"""
        available = []
        
        if SELENIUM_AVAILABLE:
            available.append("selenium")
            
        if UNDETECTED_CHROME_AVAILABLE:
            available.append("undetected-chrome")
            
        if STEALTH_AVAILABLE:
            available.append("selenium-stealth")
            
        # Försök hitta Chrome binary
        self.chrome_binary_path = await self._find_chrome_binary()
        if self.chrome_binary_path:
            available.append("chrome-binary")
            
        # Försök hitta Firefox binary
        self.firefox_binary_path = await self._find_firefox_binary()
        if self.firefox_binary_path:
            available.append("firefox-binary")
            
        return available
        
    async def _find_chrome_binary(self) -> Optional[str]:
        """Hitta Chrome binary path"""
        common_paths = []
        
        if platform.system() == "Windows":
            common_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            ]
        elif platform.system() == "Darwin":  # macOS
            common_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/usr/bin/google-chrome",
            ]
        else:  # Linux
            common_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable", 
                "/usr/bin/chromium-browser",
                "/snap/bin/chromium",
            ]
            
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"✅ Found Chrome binary: {path}")
                return path
                
        # Försök via PATH
        try:
            result = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome")
            if result:
                logger.info(f"✅ Found Chrome binary via PATH: {result}")
                return result
        except Exception:
            pass
            
        logger.warning("⚠️ Chrome binary not found")
        return None
        
    async def _find_firefox_binary(self) -> Optional[str]:
        """Hitta Firefox binary path"""
        common_paths = []
        
        if platform.system() == "Windows":
            common_paths = [
                r"C:\Program Files\Mozilla Firefox\firefox.exe",
                r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
            ]
        elif platform.system() == "Darwin":
            common_paths = [
                "/Applications/Firefox.app/Contents/MacOS/firefox",
            ]
        else:
            common_paths = [
                "/usr/bin/firefox",
                "/usr/bin/firefox-esr",
                "/snap/bin/firefox",
            ]
            
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"✅ Found Firefox binary: {path}")
                return path
                
        try:
            result = shutil.which("firefox")
            if result:
                logger.info(f"✅ Found Firefox binary via PATH: {result}")
                return result
        except Exception:
            pass
            
        logger.warning("⚠️ Firefox binary not found")
        return None
        
    async def _configure_stealth_protection(self):
        """Konfigurera stealth protection based on level"""
        
        if self.stealth_level == StealthLevel.MINIMAL:
            self.enabled_protections = {
                DetectionVector.USER_AGENT,
                DetectionVector.LANGUAGE
            }
        elif self.stealth_level == StealthLevel.MODERATE:
            self.enabled_protections = {
                DetectionVector.USER_AGENT,
                DetectionVector.WEBDRIVER_PRESENCE,
                DetectionVector.AUTOMATION_FLAGS,
                DetectionVector.CANVAS_FINGERPRINT,
                DetectionVector.LANGUAGE,
                DetectionVector.TIMEZONE
            }
        elif self.stealth_level == StealthLevel.HIGH:
            self.enabled_protections = {
                DetectionVector.USER_AGENT,
                DetectionVector.WEBDRIVER_PRESENCE,
                DetectionVector.AUTOMATION_FLAGS,
                DetectionVector.CANVAS_FINGERPRINT,
                DetectionVector.WEBGL_FINGERPRINT,
                DetectionVector.SCREEN_RESOLUTION,
                DetectionVector.TIMEZONE,
                DetectionVector.LANGUAGE,
                DetectionVector.PLUGINS,
                DetectionVector.NAVIGATOR_PROPERTIES,
                DetectionVector.JAVASCRIPT_EXECUTION
            }
        elif self.stealth_level == StealthLevel.MAXIMUM:
            self.enabled_protections = set(DetectionVector)  # All protections
        elif self.stealth_level == StealthLevel.PARANOID:
            self.enabled_protections = set(DetectionVector)
            # Additional paranoid settings
            self.timing_randomization = True
            self.mouse_movements = await self._generate_human_mouse_patterns()
            self.typing_patterns = await self._generate_human_typing_patterns()
            
        logger.info(f"🛡️ Configured {len(self.enabled_protections)} stealth protections för {self.stealth_level.value}")
        
    async def _load_user_agent_pool(self):
        """Ladda pool av realistic user agents"""
        
        # Vanliga svenska user agents för realistiska requests
        swedish_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
        ]
        
        self.user_agent_pool = swedish_user_agents
        
        # Försök ladda från fake_useragent om tillgängligt
        if FAKE_USERAGENT_AVAILABLE:
            try:
                ua = UserAgent()
                for _ in range(10):
                    chrome_ua = ua.chrome
                    firefox_ua = ua.firefox
                    if chrome_ua not in self.user_agent_pool:
                        self.user_agent_pool.append(chrome_ua)
                    if firefox_ua not in self.user_agent_pool:
                        self.user_agent_pool.append(firefox_ua)
            except Exception as e:
                logger.warning(f"Failed to load fake user agents: {str(e)}")
                
        logger.info(f"📱 Loaded {len(self.user_agent_pool)} user agents")
        
    async def _load_fingerprint_pool(self):
        """Ladda pool av realistic device fingerprints"""
        
        # Vanliga svenska device fingerprints
        fingerprints = [
            {
                "platform": "Win32",
                "hardware_concurrency": 8,
                "device_memory": 8,
                "screen": {"width": 1920, "height": 1080, "colorDepth": 24},
                "timezone": "Europe/Stockholm",
                "language": "sv-SE",
                "webgl_vendor": "Google Inc. (Intel)",
                "webgl_renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)"
            },
            {
                "platform": "MacIntel", 
                "hardware_concurrency": 8,
                "device_memory": 16,
                "screen": {"width": 1440, "height": 900, "colorDepth": 24},
                "timezone": "Europe/Stockholm",
                "language": "sv-SE",
                "webgl_vendor": "Apple Inc.",
                "webgl_renderer": "Apple M1"
            },
            {
                "platform": "Linux x86_64",
                "hardware_concurrency": 12,
                "device_memory": 16,
                "screen": {"width": 2560, "height": 1440, "colorDepth": 24},
                "timezone": "Europe/Stockholm", 
                "language": "sv-SE",
                "webgl_vendor": "X.Org",
                "webgl_renderer": "AMD Radeon RX 6700 XT (NAVI22, DRM 3.44.0, 5.15.0-56-generic, LLVM 14.0.0)"
            }
        ]
        
        self.fingerprint_pool = fingerprints
        logger.info(f"🔍 Loaded {len(self.fingerprint_pool)} device fingerprints")
        
    async def _load_stealth_scripts(self):
        """Ladda JavaScript stealth scripts"""
        
        # WebDriver detection bypass
        webdriver_bypass = """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
            configurable: true
        });
        
        delete navigator.__proto__.webdriver;
        """
        
        # Chrome runtime detection bypass
        chrome_runtime_bypass = """
        window.chrome = {
            runtime: {
                onConnect: undefined,
                onMessage: undefined,
                connect: undefined,
                sendMessage: undefined
            }
        };
        """
        
        # Navigator properties override
        navigator_override = """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['sv-SE', 'sv', 'en-US', 'en'],
            configurable: true
        });
        
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                {
                    name: 'Chrome PDF Plugin',
                    filename: 'internal-pdf-viewer',
                    description: 'Portable Document Format'
                }
            ],
            configurable: true
        });
        """
        
        # Canvas fingerprint randomization
        canvas_randomization = """
        const getImageData = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(format) {
            const context = this.getContext('2d');
            const originalData = context.getImageData(0, 0, this.width, this.height);
            
            // Add slight noise to canvas data
            for (let i = 0; i < originalData.data.length; i += 4) {
                originalData.data[i] += Math.random() * 2 - 1;
                originalData.data[i + 1] += Math.random() * 2 - 1;  
                originalData.data[i + 2] += Math.random() * 2 - 1;
            }
            
            context.putImageData(originalData, 0, 0);
            return getImageData.apply(this, arguments);
        };
        """
        
        # Mouse event simulation
        mouse_simulation = """
        let lastMouseMove = Date.now();
        const originalAddEventListener = EventTarget.prototype.addEventListener;
        
        EventTarget.prototype.addEventListener = function(type, listener, options) {
            if (type === 'mousemove') {
                const wrappedListener = function(event) {
                    lastMouseMove = Date.now();
                    return listener.call(this, event);
                };
                return originalAddEventListener.call(this, type, wrappedListener, options);
            }
            return originalAddEventListener.call(this, type, listener, options);
        };
        
        setInterval(() => {
            if (Date.now() - lastMouseMove > 60000) {
                document.dispatchEvent(new MouseEvent('mousemove', {
                    clientX: Math.random() * window.innerWidth,
                    clientY: Math.random() * window.innerHeight
                }));
            }
        }, 30000);
        """
        
        self.stealth_scripts = {
            "webdriver_bypass": webdriver_bypass,
            "chrome_runtime_bypass": chrome_runtime_bypass,
            "navigator_override": navigator_override,
            "canvas_randomization": canvas_randomization,
            "mouse_simulation": mouse_simulation
        }
        
        logger.info(f"📜 Loaded {len(self.stealth_scripts)} stealth scripts")
        
    async def _create_profile_templates(self):
        """Skapa browser profile templates"""
        
        # High stealth Chrome profile
        high_stealth_chrome = BrowserProfile(
            name="high_stealth_chrome",
            engine=BrowserEngine.UNDETECTED_CHROME,
            viewport={"width": 1920, "height": 1080},
            timezone="Europe/Stockholm",
            language="sv-SE,sv;q=0.9,en;q=0.8",
            platform="Win32",
            hardware_concurrency=8,
            device_memory=8,
            stealth_patches=[
                "webdriver_bypass",
                "chrome_runtime_bypass", 
                "navigator_override",
                "canvas_randomization"
            ],
            extra_flags=[
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--disable-extensions",
                "--disable-plugins",
                "--disable-images",
                "--disable-javascript"
            ]
        )
        
        # Mobile Chrome profile
        mobile_chrome = BrowserProfile(
            name="mobile_chrome",
            engine=BrowserEngine.MOBILE_CHROME,
            viewport={"width": 375, "height": 667},
            timezone="Europe/Stockholm",
            language="sv-SE,sv;q=0.9,en;q=0.8",
            platform="iPhone",
            max_touch_points=5,
            extra_flags=[
                "--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            ]
        )
        
        # Headless stealth profile
        headless_stealth = BrowserProfile(
            name="headless_stealth", 
            engine=BrowserEngine.HEADLESS_CHROME,
            viewport={"width": 1920, "height": 1080},
            timezone="Europe/Stockholm",
            language="sv-SE,sv;q=0.9,en;q=0.8",
            stealth_patches=[
                "webdriver_bypass",
                "navigator_override"
            ],
            extra_flags=[
                "--headless=new",
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        
        # Firefox profile
        firefox_profile = BrowserProfile(
            name="stealth_firefox",
            engine=BrowserEngine.FIREFOX,
            viewport={"width": 1920, "height": 1080},
            timezone="Europe/Stockholm", 
            language="sv-SE,sv;q=0.9,en;q=0.8",
            platform="Win32"
        )
        
        self.profile_templates = {
            "high_stealth_chrome": high_stealth_chrome,
            "mobile_chrome": mobile_chrome,
            "headless_stealth": headless_stealth,
            "stealth_firefox": firefox_profile
        }
        
        logger.info(f"👤 Created {len(self.profile_templates)} browser profile templates")
        
    def add_authorized_domain(self, domain: str):
        """Lägg till auktoriserad domän för browser testing"""
        self.authorized_domains.add(domain.lower())
        logger.info(f"✅ Added authorized domain för browser testing: {domain}")
        
    def _is_domain_authorized(self, url: str) -> bool:
        """Kontrollera om domän är auktoriserad för testning"""
        domain = urlparse(url).netloc.lower()
        
        if domain in self.authorized_domains:
            return True
            
        for auth_domain in self.authorized_domains:
            if domain.endswith(f".{auth_domain}"):
                return True
                
        return False
        
    async def create_session(self, profile_name: str = "high_stealth_chrome",
                           custom_profile: Optional[BrowserProfile] = None,
                           session_id: Optional[str] = None) -> str:
        """Skapa ny enhanced browser session"""
        
        if not self.initialized:
            await self.initialize()
            
        # Clean expired sessions
        await self._cleanup_expired_sessions()
        
        # Check session limit
        if len(self.active_sessions) >= self.max_sessions:
            await self._cleanup_oldest_session()
            
        # Generate session ID
        if not session_id:
            session_id = f"session_{int(time.time())}_{random.randint(1000, 9999)}"
            
        # Get profile
        if custom_profile:
            profile = custom_profile
        else:
            profile = self.profile_templates.get(profile_name)
            if not profile:
                logger.warning(f"Profile {profile_name} not found, using default")
                profile = self.profile_templates["high_stealth_chrome"]
                
        # Select random fingerprint
        fingerprint = random.choice(self.fingerprint_pool)
        profile.platform = fingerprint["platform"]
        profile.hardware_concurrency = fingerprint["hardware_concurrency"]
        profile.device_memory = fingerprint["device_memory"]
        profile.screen_info = fingerprint["screen"]
        profile.timezone = fingerprint["timezone"]
        profile.webgl_vendor = fingerprint.get("webgl_vendor")
        profile.webgl_renderer = fingerprint.get("webgl_renderer")
        
        # Select random user agent if not set
        if not profile.user_agent:
            profile.user_agent = random.choice(self.user_agent_pool)
            
        try:
            # Create driver based on engine
            driver = await self._create_driver(profile)
            
            # Apply stealth patches
            await self._apply_stealth_patches(driver, profile)
            
            # Create session
            session = BrowserSession(
                session_id=session_id,
                driver=driver,
                profile=profile
            )
            
            self.active_sessions[session_id] = session
            self.stats["total_sessions_created"] += 1
            self.stats["active_sessions"] = len(self.active_sessions)
            self.stats["by_engine"][profile.engine.value]["sessions"] += 1
            
            logger.info(f"✅ Created enhanced browser session: {session_id} ({profile.engine.value})")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create browser session: {str(e)}")
            raise
            
    async def _create_driver(self, profile: BrowserProfile):
        """Skapa browser driver baserat på engine"""
        
        if profile.engine == BrowserEngine.UNDETECTED_CHROME:
            if not UNDETECTED_CHROME_AVAILABLE:
                raise Exception("Undetected Chrome not available")
                
            options = uc.ChromeOptions()
            
            # Apply profile flags
            for flag in profile.extra_flags:
                options.add_argument(flag)
                
            if profile.user_agent:
                options.add_argument(f"--user-agent={profile.user_agent}")
                
            if profile.proxy:
                options.add_argument(f"--proxy-server={profile.proxy}")
                
            # Set window size
            options.add_argument(f"--window-size={profile.viewport['width']},{profile.viewport['height']}")
            
            driver = uc.Chrome(options=options, version_main=None)
            
        elif profile.engine == BrowserEngine.STEALTH_CHROME:
            if not SELENIUM_AVAILABLE or not STEALTH_AVAILABLE:
                raise Exception("Stealth Chrome requirements not available")
                
            options = ChromeOptions()
            
            for flag in profile.extra_flags:
                options.add_argument(flag)
                
            if profile.user_agent:
                options.add_argument(f"--user-agent={profile.user_agent}")
                
            driver = webdriver.Chrome(options=options)
            
            # Apply selenium-stealth
            stealth(driver,
                   languages=[profile.language.split(',')[0]],
                   vendor="Google Inc.",
                   platform=profile.platform,
                   webgl_vendor=profile.webgl_vendor or "Intel Inc.",
                   renderer=profile.webgl_renderer or "Intel Iris OpenGL Engine",
                   fix_hairline=True)
                   
        elif profile.engine == BrowserEngine.FIREFOX:
            if not SELENIUM_AVAILABLE:
                raise Exception("Firefox requirements not available")
                
            options = FirefoxOptions()
            
            # Firefox preferences
            options.set_preference("general.useragent.override", profile.user_agent)
            options.set_preference("intl.accept_languages", profile.language)
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            
            if profile.proxy:
                proxy_host, proxy_port = profile.proxy.split(':')
                options.set_preference("network.proxy.type", 1)
                options.set_preference("network.proxy.http", proxy_host)
                options.set_preference("network.proxy.http_port", int(proxy_port))
                
            driver = webdriver.Firefox(options=options)
            
        else:  # Regular Chrome fallback
            if not SELENIUM_AVAILABLE:
                raise Exception("Chrome requirements not available")
                
            options = ChromeOptions()
            
            for flag in profile.extra_flags:
                options.add_argument(flag)
                
            if profile.user_agent:
                options.add_argument(f"--user-agent={profile.user_agent}")
                
            driver = webdriver.Chrome(options=options)
            
        # Set viewport
        driver.set_window_size(profile.viewport["width"], profile.viewport["height"])
        
        return driver
        
    async def _apply_stealth_patches(self, driver, profile: BrowserProfile):
        """Apply stealth patches to driver"""
        
        for patch_name in profile.stealth_patches:
            script = self.stealth_scripts.get(patch_name)
            if script:
                try:
                    driver.execute_script(script)
                    logger.debug(f"✅ Applied stealth patch: {patch_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to apply patch {patch_name}: {str(e)}")
                    
    async def navigate(self, session_id: str, url: str, 
                      wait_for_element: Optional[str] = None,
                      timeout: int = 30) -> Dict[str, Any]:
        """Enhanced navigation med stealth och detection avoidance"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        # Check domain authorization
        if not self._is_domain_authorized(url):
            error_msg = f"🚫 Domain not authorized för browser testing: {url}"
            logger.error(error_msg)
            session.detection_events.append(f"Unauthorized domain access blocked: {url}")
            raise ValueError(error_msg)
            
        start_time = time.time()
        
        try:
            # Pre-navigation human simulation
            if self.timing_randomization:
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
            # Navigate
            session.driver.get(url)
            session.current_url = url
            session.page_count += 1
            session.last_activity = datetime.now()
            
            # Wait for element if specified
            if wait_for_element:
                wait = WebDriverWait(session.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_element)))
                
            # Post-navigation stealth actions
            await self._perform_human_simulation(session)
            
            # Check för detection
            detection_score = await self._check_detection_signals(session)
            session.stealth_score = (session.stealth_score + detection_score) / 2
            
            navigation_time = time.time() - start_time
            
            self.stats["successful_navigations"] += 1
            self.stats["by_engine"][session.profile.engine.value]["navigations"] += 1
            
            logger.info(f"✅ Navigation successful: {url} ({navigation_time:.2f}s, stealth: {detection_score:.2f})")
            
            return {
                "success": True,
                "url": url,
                "navigation_time": navigation_time,
                "stealth_score": detection_score,
                "page_count": session.page_count,
                "title": session.driver.title,
                "current_url": session.driver.current_url
            }
            
        except TimeoutException:
            logger.error(f"❌ Navigation timeout: {url}")
            session.detection_events.append(f"Navigation timeout: {url}")
            raise
        except Exception as e:
            logger.error(f"❌ Navigation failed: {str(e)}")
            session.detection_events.append(f"Navigation error: {str(e)}")
            raise
            
    async def _perform_human_simulation(self, session: BrowserSession):
        """Perform human-like actions för stealth"""
        
        if DetectionVector.MOUSE_MOVEMENT in self.enabled_protections:
            # Random mouse movement
            if random.random() < 0.3:  # 30% chance
                try:
                    action = ActionChains(session.driver)
                    x = random.randint(100, session.profile.viewport["width"] - 100)
                    y = random.randint(100, session.profile.viewport["height"] - 100)
                    action.move_by_offset(x, y)
                    action.perform()
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                except Exception:
                    pass
                    
        if DetectionVector.JAVASCRIPT_EXECUTION in self.enabled_protections:
            # Random scroll
            if random.random() < 0.4:  # 40% chance
                try:
                    scroll_amount = random.randint(100, 500)
                    session.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    await asyncio.sleep(random.uniform(0.2, 0.8))
                except Exception:
                    pass
                    
    async def _check_detection_signals(self, session: BrowserSession) -> float:
        """Check för detection signals och beräkna stealth score"""
        
        detection_signals = 0
        total_checks = 0
        
        try:
            # Check webdriver presence
            total_checks += 1
            webdriver_detected = session.driver.execute_script("return navigator.webdriver;")
            if webdriver_detected:
                detection_signals += 1
                session.detection_events.append("WebDriver property detected")
                
            # Check Chrome runtime
            total_checks += 1 
            chrome_runtime = session.driver.execute_script("return window.chrome && window.chrome.runtime;")
            if not chrome_runtime and "chrome" in session.profile.user_agent.lower():
                detection_signals += 1
                session.detection_events.append("Missing Chrome runtime")
                
            # Check for automation flags
            total_checks += 1
            automation_flags = session.driver.execute_script("""
                return window.navigator.webdriver ||
                       window.navigator.userAgent.includes('HeadlessChrome') ||
                       window.outerHeight === 0 ||
                       window.outerWidth === 0;
            """)
            if automation_flags:
                detection_signals += 1
                session.detection_events.append("Automation flags detected")
                
            # Check plugin count
            total_checks += 1
            plugin_count = session.driver.execute_script("return navigator.plugins.length;")
            if plugin_count == 0:
                detection_signals += 1
                session.detection_events.append("No plugins detected")
                
        except Exception as e:
            logger.warning(f"Detection check failed: {str(e)}")
            
        # Calculate stealth score (1.0 = perfect stealth, 0.0 = completely detected)
        if total_checks > 0:
            stealth_score = 1.0 - (detection_signals / total_checks)
        else:
            stealth_score = 1.0
            
        self.stats["detection_events"] += detection_signals
        self.stats["stealth_score_average"] = (
            (self.stats["stealth_score_average"] * (self.stats["successful_navigations"] - 1) + stealth_score)
            / self.stats["successful_navigations"]
        ) if self.stats["successful_navigations"] > 0 else stealth_score
        
        return stealth_score
        
    async def execute_script(self, session_id: str, script: str, 
                           human_timing: bool = True) -> Any:
        """Execute JavaScript med human timing"""
        
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        if human_timing:
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
        try:
            result = session.driver.execute_script(script)
            session.last_activity = datetime.now()
            return result
        except Exception as e:
            session.detection_events.append(f"Script execution error: {str(e)}")
            raise
            
    async def close_session(self, session_id: str):
        """Stäng browser session"""
        session = self.active_sessions.get(session_id)
        if session:
            try:
                session.driver.quit()
                logger.info(f"✅ Closed browser session: {session_id}")
            except Exception as e:
                logger.warning(f"⚠️ Error closing session {session_id}: {str(e)}")
            finally:
                del self.active_sessions[session_id]
                self.stats["active_sessions"] = len(self.active_sessions)
                
    async def _cleanup_expired_sessions(self):
        """Rensa gamla sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                expired_sessions.append(session_id)
                
        for session_id in expired_sessions:
            await self.close_session(session_id)
            logger.info(f"🗑️ Cleaned up expired session: {session_id}")
            
    async def _cleanup_oldest_session(self):
        """Rensa äldsta session"""
        if not self.active_sessions:
            return
            
        oldest_session_id = min(self.active_sessions.keys(), 
                               key=lambda sid: self.active_sessions[sid].created_at)
        await self.close_session(oldest_session_id)
        logger.info(f"🗑️ Cleaned up oldest session: {oldest_session_id}")
        
    async def _generate_human_mouse_patterns(self) -> List[Dict[str, Any]]:
        """Generate human-like mouse movement patterns"""
        patterns = []
        
        # Olika typer av mänskliga mönster
        for i in range(10):
            pattern = {
                "type": random.choice(["linear", "curved", "erratic"]),
                "speed": random.uniform(100, 800),  # pixels per second
                "pause_probability": random.uniform(0.1, 0.3),
                "pause_duration": random.uniform(0.5, 2.0)
            }
            patterns.append(pattern)
            
        return patterns
        
    async def _generate_human_typing_patterns(self) -> List[Dict[str, Any]]:
        """Generate human-like typing patterns"""
        patterns = []
        
        for i in range(5):
            pattern = {
                "wpm": random.randint(40, 120),  # words per minute
                "error_rate": random.uniform(0.01, 0.05),  # 1-5% errors
                "pause_between_words": random.uniform(0.1, 0.5),
                "backspace_probability": random.uniform(0.02, 0.08)
            }
            patterns.append(pattern)
            
        return patterns
        
    def get_enhanced_statistics(self) -> Dict[str, Any]:
        """Hämta enhanced browser statistics"""
        
        return {
            "total_sessions_created": self.stats["total_sessions_created"],
            "active_sessions": self.stats["active_sessions"],
            "successful_navigations": self.stats["successful_navigations"],
            "detection_events": self.stats["detection_events"],
            "stealth_score_average": self.stats["stealth_score_average"],
            "by_engine": self.stats["by_engine"],
            "by_stealth_level": self.stats["by_stealth_level"],
            "by_detection_vector": self.stats["by_detection_vector"],
            "stealth_level": self.stealth_level.value,
            "enabled_protections": [v.value for v in self.enabled_protections],
            "authorized_domains": list(self.authorized_domains),
            "profile_templates": list(self.profile_templates.keys()),
            "user_agent_pool_size": len(self.user_agent_pool),
            "fingerprint_pool_size": len(self.fingerprint_pool),
            "stealth_scripts": list(self.stealth_scripts.keys()),
            "max_sessions": self.max_sessions,
            "timing_randomization": self.timing_randomization
        }
        
    async def cleanup(self):
        """Cleanup Enhanced Undetected Browser adapter"""
        logger.info("🧹 Cleaning up Enhanced Undetected Browser Adapter")
        
        # Close all active sessions
        session_ids = list(self.active_sessions.keys())
        for session_id in session_ids:
            await self.close_session(session_id)
            
        self.profile_templates.clear()
        self.user_agent_pool.clear()
        self.fingerprint_pool.clear()
        self.stealth_scripts.clear()
        self.authorized_domains.clear()
        self.stats.clear()
        self.initialized = False
        logger.info("✅ Enhanced Undetected Browser Adapter cleanup completed")
