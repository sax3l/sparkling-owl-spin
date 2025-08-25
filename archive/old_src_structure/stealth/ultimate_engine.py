"""
Ultimate Stealth Engine - Konsoliderat System

Världens mest avancerade stealth-system som konsoliderar alla anti-detektionstekniker
i en enhetlig, intelligent motor för maximalt oblockerbar webscraping.
"""

import asyncio
import random
import json
import logging
import time
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Browser automation imports
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

# Stealth imports (with fallbacks)
try:
    import undetected_chromedriver as uc
    UNDETECTED_CHROME_AVAILABLE = True
except ImportError:
    UNDETECTED_CHROME_AVAILABLE = False

try:
    from selenium_stealth import stealth
    SELENIUM_STEALTH_AVAILABLE = True
except ImportError:
    SELENIUM_STEALTH_AVAILABLE = False

# Internal imports
from src.utils.logger import get_logger
from src.captcha.solver import CaptchaSolverManager, CaptchaTask, CaptchaType

logger = get_logger(__name__)


class StealthLevel(Enum):
    """Stealth detection evasion levels"""
    BASIC = "basic"
    STANDARD = "standard" 
    ADVANCED = "advanced"
    ULTIMATE = "ultimate"
    PARANOID = "paranoid"


class BrowserEngine(Enum):
    """Browser engines for stealth operation"""
    PLAYWRIGHT_CHROMIUM = "playwright_chromium"
    PLAYWRIGHT_FIREFOX = "playwright_firefox"
    PLAYWRIGHT_WEBKIT = "playwright_webkit"
    SELENIUM_CHROME = "selenium_chrome"
    SELENIUM_FIREFOX = "selenium_firefox" 
    UNDETECTED_CHROME = "undetected_chrome"


class AntiDetectionStrategy(Enum):
    """Anti-detection strategies"""
    FINGERPRINT_ROTATION = "fingerprint_rotation"
    BEHAVIORAL_MIMICRY = "behavioral_mimicry"
    NETWORK_OBFUSCATION = "network_obfuscation"
    TIMING_RANDOMIZATION = "timing_randomization"
    CAPTCHA_HANDLING = "captcha_handling"
    SESSION_MANAGEMENT = "session_management"
    ADAPTIVE_LEARNING = "adaptive_learning"


@dataclass
class BrowserFingerprint:
    """Comprehensive browser fingerprint"""
    user_agent: str
    viewport_width: int
    viewport_height: int
    screen_width: int
    screen_height: int
    color_depth: int
    device_scale_factor: float
    languages: List[str]
    timezone: str
    platform: str
    hardware_concurrency: int
    device_memory: int
    webgl_vendor: str
    webgl_renderer: str
    canvas_fingerprint: str
    audio_fingerprint: str
    fonts: List[str]
    plugins: List[str]
    cookies_enabled: bool
    do_not_track: bool
    webrtc_enabled: bool
    geolocation_enabled: bool
    permissions: Dict[str, str]


@dataclass 
class StealthConfig:
    """Configuration for stealth operations"""
    stealth_level: StealthLevel
    browser_engine: BrowserEngine
    strategies: List[AntiDetectionStrategy]
    fingerprint_rotation_interval: int = 300  # seconds
    behavioral_delays: Tuple[float, float] = (1.0, 5.0)
    captcha_solver_enabled: bool = True
    adaptive_learning_enabled: bool = True
    proxy_rotation_enabled: bool = True
    session_persistence_enabled: bool = True
    max_concurrent_contexts: int = 5


@dataclass
class DetectionEvent:
    """Event when bot detection is detected"""
    timestamp: float
    url: str
    detection_type: str
    response_code: int
    response_headers: Dict[str, str]
    response_body_sample: str
    fingerprint_used: BrowserFingerprint
    countermeasures_applied: List[str]


class FingerprintGenerator:
    """Generate realistic browser fingerprints"""
    
    def __init__(self):
        self.user_agents = self._load_user_agents()
        self.screen_resolutions = self._load_screen_resolutions()
        self.timezones = self._load_timezones()
        self.languages = self._load_languages()
        self.webgl_vendors = self._load_webgl_vendors()
        
    def _load_user_agents(self) -> List[str]:
        """Load realistic user agent strings"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
        ]
    
    def _load_screen_resolutions(self) -> List[Tuple[int, int]]:
        """Load common screen resolutions"""
        return [
            (1920, 1080), (1366, 768), (1440, 900), (1536, 864),
            (1280, 720), (1600, 900), (1024, 768), (1680, 1050),
            (2560, 1440), (3840, 2160), (1280, 800), (1920, 1200)
        ]
    
    def _load_timezones(self) -> List[str]:
        """Load realistic timezones"""
        return [
            "America/New_York", "America/Los_Angeles", "Europe/London",
            "Europe/Berlin", "Europe/Paris", "Asia/Tokyo", "Asia/Shanghai", 
            "Australia/Sydney", "America/Toronto", "Europe/Amsterdam"
        ]
    
    def _load_languages(self) -> List[List[str]]:
        """Load language preferences"""
        return [
            ["en-US", "en"],
            ["en-GB", "en"],
            ["de-DE", "de", "en"],
            ["fr-FR", "fr", "en"],
            ["es-ES", "es", "en"],
            ["ja-JP", "ja", "en"],
            ["zh-CN", "zh", "en"],
            ["ru-RU", "ru", "en"]
        ]
    
    def _load_webgl_vendors(self) -> List[Tuple[str, str]]:
        """Load WebGL vendor/renderer combinations"""
        return [
            ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) HD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 6800 XT Direct3D11 vs_5_0 ps_5_0, D3D11)"),
            ("Intel Inc.", "Intel Iris Pro OpenGL Engine"),
            ("ATI Technologies Inc.", "AMD Radeon Pro 5500M OpenGL Engine"),
            ("NVIDIA Corporation", "GeForce RTX 3070/PCIe/SSE2")
        ]
    
    def generate_fingerprint(self, 
                           platform: str = None,
                           mobile: bool = False) -> BrowserFingerprint:
        """Generate a realistic browser fingerprint"""
        
        # Select platform
        if not platform:
            platform = random.choice(["Windows NT 10.0", "Macintosh", "X11; Linux x86_64"])
        
        # Select user agent matching platform
        matching_agents = [ua for ua in self.user_agents if platform.split()[0].lower() in ua.lower()]
        user_agent = random.choice(matching_agents if matching_agents else self.user_agents)
        
        # Select screen resolution
        screen_width, screen_height = random.choice(self.screen_resolutions)
        
        # Viewport is typically smaller than screen
        viewport_width = min(screen_width, random.randint(1024, screen_width))
        viewport_height = min(screen_height, random.randint(720, screen_height))
        
        # Other properties
        languages = random.choice(self.languages)
        timezone = random.choice(self.timezones)
        webgl_vendor, webgl_renderer = random.choice(self.webgl_vendors)
        
        return BrowserFingerprint(
            user_agent=user_agent,
            viewport_width=viewport_width,
            viewport_height=viewport_height,
            screen_width=screen_width,
            screen_height=screen_height,
            color_depth=24,
            device_scale_factor=random.choice([1.0, 1.25, 1.5, 2.0]),
            languages=languages,
            timezone=timezone,
            platform=platform,
            hardware_concurrency=random.choice([2, 4, 6, 8, 12, 16]),
            device_memory=random.choice([4, 8, 16, 32]),
            webgl_vendor=webgl_vendor,
            webgl_renderer=webgl_renderer,
            canvas_fingerprint=self._generate_canvas_fingerprint(),
            audio_fingerprint=self._generate_audio_fingerprint(), 
            fonts=self._generate_font_list(),
            plugins=self._generate_plugin_list(),
            cookies_enabled=True,
            do_not_track=random.choice([True, False]),
            webrtc_enabled=random.choice([True, False]),
            geolocation_enabled=random.choice([True, False]),
            permissions=self._generate_permissions()
        )
    
    def _generate_canvas_fingerprint(self) -> str:
        """Generate randomized canvas fingerprint"""
        # Simple implementation - in practice, this would be more sophisticated
        random_data = f"{random.random()}{time.time()}"
        return hashlib.md5(random_data.encode()).hexdigest()[:16]
    
    def _generate_audio_fingerprint(self) -> str:
        """Generate randomized audio fingerprint"""
        random_data = f"audio{random.random()}{time.time()}"
        return hashlib.sha256(random_data.encode()).hexdigest()[:20]
    
    def _generate_font_list(self) -> List[str]:
        """Generate realistic font list"""
        common_fonts = [
            "Arial", "Helvetica", "Times New Roman", "Courier New", 
            "Verdana", "Georgia", "Palatino", "Garamond", "Bookman", 
            "Comic Sans MS", "Trebuchet MS", "Arial Black", "Impact"
        ]
        return random.sample(common_fonts, k=random.randint(8, 12))
    
    def _generate_plugin_list(self) -> List[str]:
        """Generate realistic plugin list"""
        plugins = [
            "Chrome PDF Plugin", "Chrome PDF Viewer", "Native Client",
            "Widevine Content Decryption Module", "Microsoft Edge PDF Plugin"
        ]
        return random.sample(plugins, k=random.randint(2, 4))
    
    def _generate_permissions(self) -> Dict[str, str]:
        """Generate permission states"""
        return {
            "notifications": random.choice(["granted", "denied", "default"]),
            "geolocation": random.choice(["granted", "denied", "default"]),
            "camera": random.choice(["granted", "denied", "default"]),
            "microphone": random.choice(["granted", "denied", "default"])
        }


class BehaviorSimulator:
    """Simulate human-like browsing behavior"""
    
    def __init__(self):
        self.mouse_movements = []
        self.scroll_patterns = []
        self.typing_patterns = []
    
    async def simulate_human_navigation(self, page: Page, delay_range: Tuple[float, float] = (2.0, 5.0)):
        """Simulate human navigation delays"""
        delay = random.uniform(*delay_range)
        await asyncio.sleep(delay)
    
    async def simulate_reading_behavior(self, page: Page, read_time_factor: float = 1.0):
        """Simulate human reading behavior with realistic pauses"""
        try:
            # Get page content length to estimate reading time
            content_length = await page.evaluate("""
                () => {
                    const text = document.body.innerText || '';
                    return text.length;
                }
            """)
            
            # Estimate reading time (average 250 words per minute, 5 chars per word)
            base_reading_time = (content_length / (250 * 5)) * 60 * read_time_factor
            reading_time = max(2.0, min(30.0, base_reading_time + random.uniform(-5.0, 10.0)))
            
            # Simulate scrolling during reading
            scroll_count = max(1, int(reading_time / 3))
            for _ in range(scroll_count):
                await self.simulate_scrolling(page)
                await asyncio.sleep(reading_time / scroll_count)
                
        except Exception as e:
            logger.debug(f"Reading simulation failed: {e}")
            await asyncio.sleep(random.uniform(3.0, 8.0))
    
    async def simulate_scrolling(self, page: Page):
        """Simulate human-like scrolling"""
        try:
            # Get page height
            page_height = await page.evaluate("document.body.scrollHeight")
            viewport_height = await page.evaluate("window.innerHeight")
            
            if page_height <= viewport_height:
                return  # No need to scroll
            
            # Random scroll distance and speed
            scroll_distance = random.randint(100, 500)
            scroll_steps = random.randint(3, 8)
            
            for i in range(scroll_steps):
                step_distance = scroll_distance // scroll_steps
                await page.evaluate(f"window.scrollBy(0, {step_distance})")
                await asyncio.sleep(random.uniform(0.1, 0.3))
                
        except Exception as e:
            logger.debug(f"Scrolling simulation failed: {e}")
    
    async def simulate_mouse_movement(self, page: Page):
        """Simulate random mouse movements"""
        try:
            viewport = await page.viewport_size()
            if not viewport:
                return
            
            # Generate random mouse path
            start_x = random.randint(0, viewport['width'])
            start_y = random.randint(0, viewport['height'])
            
            for _ in range(random.randint(2, 5)):
                target_x = random.randint(0, viewport['width'])
                target_y = random.randint(0, viewport['height'])
                
                await page.mouse.move(target_x, target_y)
                await asyncio.sleep(random.uniform(0.1, 0.5))
                
        except Exception as e:
            logger.debug(f"Mouse simulation failed: {e}")
    
    async def simulate_typing(self, page: Page, element_selector: str, text: str):
        """Simulate human-like typing"""
        try:
            element = await page.query_selector(element_selector)
            if not element:
                return
            
            await element.click()
            await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Type with realistic delays
            for char in text:
                await element.type(char)
                # Vary typing speed
                if char == ' ':
                    delay = random.uniform(0.1, 0.3)
                else:
                    delay = random.uniform(0.05, 0.15)
                await asyncio.sleep(delay)
                
        except Exception as e:
            logger.debug(f"Typing simulation failed: {e}")


class DetectionAnalyzer:
    """Analyze responses for bot detection indicators"""
    
    def __init__(self):
        self.detection_patterns = self._load_detection_patterns()
        self.blocked_responses = []
    
    def _load_detection_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate bot detection"""
        return {
            "status_codes": [403, 429, 503],
            "headers": [
                "cf-ray",  # Cloudflare
                "x-sucuri-id",  # Sucuri
                "server: cloudflare",
                "x-frame-options: deny"
            ],
            "body_patterns": [
                "access denied",
                "blocked",
                "bot detected", 
                "suspicious activity",
                "captcha",
                "rate limit",
                "cloudflare",
                "please complete the security check",
                "ddos protection",
                "firewall"
            ],
            "javascript_checks": [
                "navigator.webdriver",
                "window.chrome.runtime",
                "_phantom",
                "__selenium",
                "webdriver"
            ]
        }
    
    def analyze_response(self, response: Response, page: Page = None) -> Optional[DetectionEvent]:
        """Analyze response for bot detection indicators"""
        detection_indicators = []
        
        # Check status code
        if response.status in self.detection_patterns["status_codes"]:
            detection_indicators.append(f"blocked_status_code_{response.status}")
        
        # Check headers
        headers_lower = {k.lower(): v.lower() for k, v in response.headers.items()}
        for pattern in self.detection_patterns["headers"]:
            if any(pattern.lower() in key or pattern.lower() in value 
                   for key, value in headers_lower.items()):
                detection_indicators.append(f"blocked_header_{pattern}")
        
        # Check response body if available
        try:
            # This is async and might not be available
            # In practice, you'd need to handle this differently
            pass
        except:
            pass
        
        if detection_indicators:
            return DetectionEvent(
                timestamp=time.time(),
                url=response.url,
                detection_type=",".join(detection_indicators),
                response_code=response.status,
                response_headers=dict(response.headers),
                response_body_sample="",  # Would be filled if available
                fingerprint_used=None,  # Would be filled with current fingerprint
                countermeasures_applied=[]
            )
        
        return None


class UltimateStealthEngine:
    """
    Ultimate Stealth Engine - Konsoliderat system för maximal oblockerbarhet
    """
    
    def __init__(self, 
                 config: StealthConfig = None,
                 captcha_solver: CaptchaSolverManager = None):
        
        self.config = config or StealthConfig(
            stealth_level=StealthLevel.ULTIMATE,
            browser_engine=BrowserEngine.PLAYWRIGHT_CHROMIUM,
            strategies=[s for s in AntiDetectionStrategy]
        )
        
        self.fingerprint_generator = FingerprintGenerator()
        self.behavior_simulator = BehaviorSimulator()
        self.detection_analyzer = DetectionAnalyzer()
        self.captcha_solver = captcha_solver
        
        # State management
        self.current_fingerprint = None
        self.last_fingerprint_rotation = 0
        self.browser_contexts = {}
        self.detection_events = []
        self.adaptation_rules = {}
        
        # Browser automation
        self.playwright = None
        self.browser = None
        
        logger.info(f"Ultimate Stealth Engine initialized: {config.stealth_level.value}")
    
    async def initialize(self):
        """Initialize the stealth engine"""
        self.playwright = await async_playwright().start()
        
        # Launch browser based on config
        if self.config.browser_engine == BrowserEngine.PLAYWRIGHT_CHROMIUM:
            self.browser = await self._launch_stealth_chromium()
        elif self.config.browser_engine == BrowserEngine.PLAYWRIGHT_FIREFOX:
            self.browser = await self._launch_stealth_firefox()
        elif self.config.browser_engine == BrowserEngine.PLAYWRIGHT_WEBKIT:
            self.browser = await self._launch_stealth_webkit()
        else:
            raise ValueError(f"Unsupported browser engine: {self.config.browser_engine}")
        
        # Generate initial fingerprint
        await self.rotate_fingerprint()
        
        logger.info("Ultimate Stealth Engine initialized successfully")
    
    async def _launch_stealth_chromium(self) -> Browser:
        """Launch Chromium with maximum stealth"""
        args = [
            '--no-sandbox',
            '--disable-setuid-sandbox', 
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--no-zygote',
            '--disable-gpu',
            '--disable-background-networking',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            '--disable-client-side-phishing-detection',
            '--disable-sync',
            '--disable-translate',
            '--hide-scrollbars',
            '--mute-audio',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-default-apps',
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
            '--enable-automation=false',
            '--disable-blink-features=AutomationControlled'
        ]
        
        return await self.playwright.chromium.launch(
            headless=True,
            args=args,
            ignore_default_args=[
                '--enable-automation',
                '--enable-blink-features=IdleDetection'
            ]
        )
    
    async def _launch_stealth_firefox(self) -> Browser:
        """Launch Firefox with stealth configuration"""
        args = [
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ]
        
        return await self.playwright.firefox.launch(
            headless=True,
            args=args,
            firefox_user_prefs={
                'dom.webdriver.enabled': False,
                'useAutomationExtension': False,
                'general.platform.override': 'Linux x86_64'
            }
        )
    
    async def _launch_stealth_webkit(self) -> Browser:
        """Launch WebKit with stealth configuration"""
        return await self.playwright.webkit.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
    
    async def rotate_fingerprint(self) -> BrowserFingerprint:
        """Rotate browser fingerprint for enhanced stealth"""
        self.current_fingerprint = self.fingerprint_generator.generate_fingerprint()
        self.last_fingerprint_rotation = time.time()
        
        logger.info(f"Fingerprint rotated: {self.current_fingerprint.user_agent[:50]}...")
        return self.current_fingerprint
    
    async def create_stealth_context(self, proxy: Dict[str, str] = None) -> BrowserContext:
        """Create a stealth browser context"""
        
        # Check if fingerprint needs rotation
        if (time.time() - self.last_fingerprint_rotation > 
            self.config.fingerprint_rotation_interval):
            await self.rotate_fingerprint()
        
        # Create context with stealth settings
        context_options = {
            'user_agent': self.current_fingerprint.user_agent,
            'viewport': {
                'width': self.current_fingerprint.viewport_width,
                'height': self.current_fingerprint.viewport_height
            },
            'screen': {
                'width': self.current_fingerprint.screen_width,
                'height': self.current_fingerprint.screen_height
            },
            'device_scale_factor': self.current_fingerprint.device_scale_factor,
            'locale': self.current_fingerprint.languages[0],
            'timezone_id': self.current_fingerprint.timezone,
            'permissions': ['geolocation'] if self.current_fingerprint.geolocation_enabled else [],
            'extra_http_headers': self._generate_stealth_headers(),
            'ignore_https_errors': True,
            'color_scheme': 'light',
            'reduced_motion': 'no-preference'
        }
        
        # Add proxy if provided
        if proxy:
            context_options['proxy'] = proxy
        
        context = await self.browser.new_context(**context_options)
        
        # Apply advanced stealth measures
        await self._apply_stealth_scripts(context)
        
        # Store context
        context_id = str(uuid.uuid4())
        self.browser_contexts[context_id] = {
            'context': context,
            'fingerprint': self.current_fingerprint,
            'created_at': time.time()
        }
        
        return context
    
    def _generate_stealth_headers(self) -> Dict[str, str]:
        """Generate stealth HTTP headers"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': f"{self.current_fingerprint.languages[0]},en-US;q=0.9,en;q=0.8",
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1' if self.current_fingerprint.do_not_track else '0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    async def _apply_stealth_scripts(self, context: BrowserContext):
        """Apply comprehensive stealth scripts to context"""
        
        stealth_script = f"""
        // Remove webdriver traces
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined,
        }});
        
        // Mock chrome object
        window.chrome = {{
            runtime: {{}},
            app: {{
                isInstalled: false,
            }},
            webstore: {{
                onInstallStageChanged: {{}},
                onDownloadProgress: {{}},
            }},
        }};
        
        // Override navigator properties
        Object.defineProperty(navigator, 'languages', {{
            get: () => {json.dumps(self.current_fingerprint.languages)},
        }});
        
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{self.current_fingerprint.platform}',
        }});
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {self.current_fingerprint.hardware_concurrency},
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {self.current_fingerprint.device_memory},
        }});
        
        // Mock permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => {{
            const permission = parameters.name;
            const state = {json.dumps(self.current_fingerprint.permissions)}[permission] || 'denied';
            return Promise.resolve({{ state: state }});
        }};
        
        // Override WebGL
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) return '{self.current_fingerprint.webgl_vendor}';
            if (parameter === 37446) return '{self.current_fingerprint.webgl_renderer}';
            return getParameter.call(this, parameter);
        }};
        
        // Canvas fingerprinting protection
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(...args) {{
            const context = this.getContext('2d');
            if (context) {{
                // Add subtle noise to canvas
                context.fillStyle = 'rgba(255,255,255,0.01)';
                context.fillRect(Math.random() * 10, Math.random() * 10, 1, 1);
            }}
            return originalToDataURL.apply(this, args);
        }};
        
        // Audio context fingerprinting protection  
        const originalGetChannelData = AudioBuffer.prototype.getChannelData;
        AudioBuffer.prototype.getChannelData = function(...args) {{
            const data = originalGetChannelData.apply(this, args);
            for (let i = 0; i < data.length; i += 100) {{
                data[i] = data[i] + Math.random() * 0.0001 - 0.00005;
            }}
            return data;
        }};
        
        // Screen properties
        Object.defineProperty(screen, 'width', {{
            get: () => {self.current_fingerprint.screen_width},
        }});
        
        Object.defineProperty(screen, 'height', {{
            get: () => {self.current_fingerprint.screen_height},
        }});
        
        Object.defineProperty(screen, 'colorDepth', {{
            get: () => {self.current_fingerprint.color_depth},
        }});
        
        // Plugin spoofing
        Object.defineProperty(navigator, 'plugins', {{
            get: () => {json.dumps([{'name': p} for p in self.current_fingerprint.plugins])},
        }});
        
        // Timezone spoofing
        Date.prototype.getTimezoneOffset = function() {{
            return -120; // UTC+2 as example, should be calculated from timezone
        }};
        """
        
        await context.add_init_script(stealth_script)
    
    async def navigate_with_stealth(self, 
                                  context: BrowserContext,
                                  url: str,
                                  wait_until: str = 'networkidle',
                                  handle_captcha: bool = True) -> Tuple[Page, Response]:
        """Navigate to URL with full stealth measures"""
        
        page = await context.new_page()
        
        try:
            # Set up request interception for additional stealth
            await page.route("**/*", self._intercept_request)
            
            # Navigate with timeout
            response = await page.goto(url, wait_until=wait_until, timeout=30000)
            
            # Analyze response for detection
            detection_event = self.detection_analyzer.analyze_response(response, page)
            if detection_event:
                self.detection_events.append(detection_event)
                logger.warning(f"Bot detection detected: {detection_event.detection_type}")
                
                # Apply countermeasures
                await self._apply_countermeasures(page, detection_event)
            
            # Simulate human behavior
            if AntiDetectionStrategy.BEHAVIORAL_MIMICRY in self.config.strategies:
                await self.behavior_simulator.simulate_human_navigation(page)
                await self.behavior_simulator.simulate_reading_behavior(page)
            
            # Handle CAPTCHA if present
            if handle_captcha and self.captcha_solver:
                await self._handle_captcha(page)
            
            return page, response
            
        except Exception as e:
            logger.error(f"Stealth navigation failed: {e}")
            await page.close()
            raise
    
    async def _intercept_request(self, route):
        """Intercept and modify requests for stealth"""
        request = route.request
        
        # Modify headers for stealth
        headers = dict(request.headers)
        
        # Remove automation headers
        headers.pop('sec-fetch-dest', None)
        headers.pop('sec-fetch-mode', None)
        headers.pop('sec-fetch-site', None)
        
        # Add realistic headers
        if 'referer' not in headers and request.url != request.frame.url:
            headers['referer'] = request.frame.url
        
        await route.continue_(headers=headers)
    
    async def _handle_captcha(self, page: Page) -> bool:
        """Handle CAPTCHA if detected on page"""
        try:
            # Check for various CAPTCHA types
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                '.h-captcha',
                '.cf-turnstile',
                '[data-sitekey]',
                'iframe[src*="hcaptcha"]'
            ]
            
            for selector in captcha_selectors:
                captcha_element = await page.query_selector(selector)
                if captcha_element:
                    logger.info(f"CAPTCHA detected: {selector}")
                    
                    # Extract CAPTCHA details
                    if 'recaptcha' in selector:
                        site_key = await captcha_element.get_attribute('data-sitekey')
                        if site_key:
                            task = CaptchaTask(
                                task_id=str(uuid.uuid4()),
                                captcha_type=CaptchaType.RECAPTCHA_V2,
                                site_key=site_key,
                                page_url=page.url
                            )
                            
                            result = await self.captcha_solver.solve_captcha(task)
                            if result.success:
                                # Inject solution
                                await page.evaluate(f'''
                                    document.getElementById('g-recaptcha-response').innerHTML = '{result.solution}';
                                ''')
                                logger.info("CAPTCHA solved successfully")
                                return True
                    
            return False
            
        except Exception as e:
            logger.error(f"CAPTCHA handling failed: {e}")
            return False
    
    async def _apply_countermeasures(self, page: Page, detection_event: DetectionEvent):
        """Apply countermeasures when bot detection is detected"""
        countermeasures = []
        
        # Rotate fingerprint
        if AntiDetectionStrategy.FINGERPRINT_ROTATION in self.config.strategies:
            await self.rotate_fingerprint()
            countermeasures.append("fingerprint_rotation")
        
        # Add behavioral delays
        if AntiDetectionStrategy.BEHAVIORAL_MIMICRY in self.config.strategies:
            await asyncio.sleep(random.uniform(5.0, 15.0))
            countermeasures.append("behavioral_delay")
        
        # Simulate user interaction
        await self.behavior_simulator.simulate_mouse_movement(page)
        countermeasures.append("mouse_simulation")
        
        detection_event.countermeasures_applied = countermeasures
        logger.info(f"Applied countermeasures: {countermeasures}")
    
    async def close(self):
        """Close the stealth engine and cleanup resources"""
        try:
            # Close all browser contexts
            for context_data in self.browser_contexts.values():
                await context_data['context'].close()
            
            # Close browser
            if self.browser:
                await self.browser.close()
            
            # Close playwright
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("Ultimate Stealth Engine closed successfully")
            
        except Exception as e:
            logger.error(f"Error closing stealth engine: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get stealth engine statistics"""
        return {
            'total_contexts': len(self.browser_contexts),
            'detection_events': len(self.detection_events),
            'current_fingerprint': asdict(self.current_fingerprint) if self.current_fingerprint else None,
            'fingerprint_rotations': len([e for e in self.detection_events if 'fingerprint_rotation' in e.countermeasures_applied]),
            'captcha_encounters': len([e for e in self.detection_events if 'captcha' in e.detection_type]),
            'blocked_requests': len([e for e in self.detection_events if e.response_code in [403, 429, 503]])
        }


# Factory function
async def create_ultimate_stealth_engine(
    stealth_level: StealthLevel = StealthLevel.ULTIMATE,
    browser_engine: BrowserEngine = BrowserEngine.PLAYWRIGHT_CHROMIUM,
    captcha_solver: CaptchaSolverManager = None
) -> UltimateStealthEngine:
    """Factory function to create Ultimate Stealth Engine"""
    
    config = StealthConfig(
        stealth_level=stealth_level,
        browser_engine=browser_engine,
        strategies=[s for s in AntiDetectionStrategy],
        fingerprint_rotation_interval=300,
        behavioral_delays=(2.0, 8.0),
        captcha_solver_enabled=bool(captcha_solver),
        adaptive_learning_enabled=True
    )
    
    engine = UltimateStealthEngine(config, captcha_solver)
    await engine.initialize()
    
    return engine


# Example usage
async def example_ultimate_stealth_crawling():
    """Example of ultimate stealth web crawling"""
    
    # Create stealth engine
    engine = await create_ultimate_stealth_engine(
        stealth_level=StealthLevel.ULTIMATE,
        browser_engine=BrowserEngine.PLAYWRIGHT_CHROMIUM
    )
    
    try:
        # Create stealth context
        context = await engine.create_stealth_context()
        
        # Navigate with maximum stealth
        page, response = await engine.navigate_with_stealth(
            context, 
            "https://httpbin.org/user-agent",
            handle_captcha=True
        )
        
        # Extract data
        content = await page.content()
        print(f"✅ Successfully crawled with stealth")
        print(f"Response code: {response.status}")
        print(f"User agent detected: {await page.evaluate('navigator.userAgent')}")
        
        # Get statistics
        stats = engine.get_statistics()
        print(f"Detection events: {stats['detection_events']}")
        print(f"Fingerprint rotations: {stats['fingerprint_rotations']}")
        
        await page.close()
        await context.close()
        
    finally:
        await engine.close()


if __name__ == "__main__":
    asyncio.run(example_ultimate_stealth_crawling())
