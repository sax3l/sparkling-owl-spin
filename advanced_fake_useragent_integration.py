"""
Advanced Fake-UserAgent Integration for Ultimate Scraping System

Integrerar fake-useragent-funktionalitet med våra befintliga stealth-system
för att skapa intelligenta, dynamiska user-agent strategier med avancerade
rotations- och filtrerings-funktioner.

Baserat på: https://github.com/fake-useragent/fake-useragent
"""

import json
import logging
import random
import time
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import hashlib

try:
    from fake_useragent import FakeUserAgent
    from fake_useragent.utils import BrowserUserAgentData
    FAKE_USERAGENT_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_AVAILABLE = False
    logging.warning("Fake-UserAgent not available - using fallback user agents")

# Import våra stealth-system
try:
    from enhanced_stealth_integration import EnhancedStealthManager, EnhancedStealthConfig
    STEALTH_INTEGRATION_AVAILABLE = True
except ImportError:
    STEALTH_INTEGRATION_AVAILABLE = False

# Fallback user agents om fake-useragent inte är tillgängligt
FALLBACK_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"
]

@dataclass
class UserAgentConfig:
    """Konfiguration för Advanced User-Agent Integration"""
    
    # Browser-filter
    browsers: List[str] = field(default_factory=lambda: [
        "Chrome", "Firefox", "Safari", "Edge", "Opera"
    ])
    
    # OS-filter
    os_list: List[str] = field(default_factory=lambda: [
        "Windows", "Mac OS X", "Linux", "Android", "iOS"
    ])
    
    # Platform-filter
    platforms: List[str] = field(default_factory=lambda: [
        "desktop", "mobile", "tablet"
    ])
    
    # Version-filter
    min_version: float = 90.0  # Minimum browser version
    min_percentage: float = 0.1  # Minimum usage percentage
    
    # Rotation-strategier
    rotation_strategy: str = "random"  # random, sequential, weighted
    rotation_interval: int = 100  # Requests mellan rotations
    session_persistence: bool = False  # Håll samma UA per session
    
    # Caching
    cache_enabled: bool = True
    cache_ttl: int = 3600  # Cache TTL i sekunder
    cache_size: int = 1000  # Max cached user agents
    
    # Fingerprint-konsistens
    maintain_consistency: bool = True  # Matcha UA med andra fingerprint-data
    validate_headers: bool = True  # Validera att headers matchar UA

@dataclass
class UserAgentData:
    """Utökad user-agent data med metadata"""
    
    user_agent: str
    browser: str
    browser_version: str
    os: str
    platform: str
    percentage: float
    headers: Dict[str, str] = field(default_factory=dict)
    fingerprint_data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    usage_count: int = 0


class AdvancedUserAgentManager:
    """
    Avancerad manager för User-Agent hantering med intelligenta strategier
    """
    
    def __init__(self, config: Optional[UserAgentConfig] = None):
        self.config = config or UserAgentConfig()
        self.fake_ua = None
        self.user_agent_cache = {}
        self.rotation_counter = 0
        self.current_session_ua = None
        self.stealth_manager = None
        
        # Statistik
        self.stats = {
            'user_agents_generated': 0,
            'rotations_performed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'fallback_used': 0,
            'consistency_checks': 0,
            'validation_failures': 0
        }
        
        # Initialisera fake-useragent om tillgängligt
        if FAKE_USERAGENT_AVAILABLE:
            try:
                # Använd standardkonstruktorn först för att testa
                self.fake_ua = FakeUserAgent()
                logging.info("FakeUserAgent initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize FakeUserAgent: {e}")
                self.fake_ua = None
                
        # Initialisera stealth integration om tillgängligt
        if STEALTH_INTEGRATION_AVAILABLE:
            self.stealth_manager = EnhancedStealthManager()
            
        logging.info("Advanced UserAgent Manager initialized")
        
    def get_user_agent(self, 
                      browser: Optional[str] = None,
                      os: Optional[str] = None,
                      platform: Optional[str] = None,
                      force_new: bool = False) -> UserAgentData:
        """Hämta en user agent baserat på kriterier"""
        
        # Session persistence check
        if (self.config.session_persistence and 
            self.current_session_ua and 
            not force_new):
            self.current_session_ua.usage_count += 1
            return self.current_session_ua
            
        # Rotation strategy check
        if (self.rotation_counter >= self.config.rotation_interval and 
            not force_new):
            self._perform_rotation()
            
        # Cache key generation
        cache_key = self._generate_cache_key(browser, os, platform)
        
        # Cache lookup
        if self.config.cache_enabled and cache_key in self.user_agent_cache:
            cached_ua = self.user_agent_cache[cache_key]
            if time.time() - cached_ua.created_at < self.config.cache_ttl:
                self.stats['cache_hits'] += 1
                cached_ua.usage_count += 1
                return cached_ua
            else:
                # Cache expired
                del self.user_agent_cache[cache_key]
                
        self.stats['cache_misses'] += 1
        
        # Generate new user agent
        ua_data = self._generate_user_agent(browser, os, platform)
        
        # Cache new user agent
        if self.config.cache_enabled:
            self._cache_user_agent(cache_key, ua_data)
            
        # Update session UA if persistence enabled
        if self.config.session_persistence:
            self.current_session_ua = ua_data
            
        self.rotation_counter += 1
        self.stats['user_agents_generated'] += 1
        
        return ua_data
        
    def _generate_user_agent(self, 
                           browser: Optional[str] = None,
                           os: Optional[str] = None, 
                           platform: Optional[str] = None) -> UserAgentData:
        """Generera en ny user agent"""
        
        try:
            if self.fake_ua:
                # Använd fake-useragent direkt med enkla properties
                if browser:
                    browser_lower = browser.lower()
                    if browser_lower == 'chrome':
                        ua_string = self.fake_ua.chrome
                    elif browser_lower == 'firefox':
                        ua_string = self.fake_ua.firefox
                    elif browser_lower == 'safari':
                        ua_string = self.fake_ua.safari
                    elif browser_lower == 'edge':
                        ua_string = self.fake_ua.edge  
                    elif browser_lower == 'opera':
                        ua_string = self.fake_ua.opera
                    else:
                        ua_string = self.fake_ua.random
                else:
                    ua_string = self.fake_ua.random
                    
                ua_data = UserAgentData(
                    user_agent=ua_string,
                    browser=self._extract_browser_from_ua(ua_string),
                    browser_version=self._extract_version_from_ua(ua_string),
                    os=self._extract_os_from_ua(ua_string),
                    platform=platform or "desktop",
                    percentage=100.0  # Fake placeholder
                )
                
            else:
                # Fallback
                ua_string = random.choice(FALLBACK_USER_AGENTS)
                self.stats['fallback_used'] += 1
                
                ua_data = UserAgentData(
                    user_agent=ua_string,
                    browser=self._extract_browser_from_ua(ua_string),
                    browser_version="Unknown",
                    os=self._extract_os_from_ua(ua_string),
                    platform=platform or "desktop",
                    percentage=0.0
                )
                
        except Exception as e:
            logging.error(f"Error generating user agent: {e}")
            ua_string = FALLBACK_USER_AGENTS[0]
            self.stats['fallback_used'] += 1
            
            ua_data = UserAgentData(
                user_agent=ua_string,
                browser="Chrome",
                browser_version="120.0",
                os="Windows",
                platform="desktop",
                percentage=0.0
            )
            
        # Enhance with headers and fingerprint data
        ua_data.headers = self._generate_matching_headers(ua_data)
        ua_data.fingerprint_data = self._generate_fingerprint_data(ua_data)
        
        # Validate consistency if enabled
        if self.config.maintain_consistency:
            self._validate_consistency(ua_data)
            
        return ua_data
        
    def _get_browser_data(self, browser: str) -> Dict[str, Any]:
        """Hämta detaljerad browser-data"""
        
        if not self.fake_ua:
            return {}
            
        try:
            method_name = f"get{browser.capitalize()}"
            if hasattr(self.fake_ua, method_name):
                return getattr(self.fake_ua, method_name)
            else:
                return self.fake_ua.getRandom
        except Exception as e:
            logging.error(f"Error getting browser data for {browser}: {e}")
            return {}
            
    def _generate_cache_key(self, 
                          browser: Optional[str],
                          os: Optional[str],
                          platform: Optional[str]) -> str:
        """Generera cache-nyckel"""
        
        key_parts = [
            browser or "any",
            os or "any", 
            platform or "any",
            str(self.config.min_version),
            str(self.config.min_percentage)
        ]
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
        
    def _cache_user_agent(self, cache_key: str, ua_data: UserAgentData):
        """Cacha en user agent"""
        
        # Cache size management
        if len(self.user_agent_cache) >= self.config.cache_size:
            # Remove oldest entries
            oldest_key = min(
                self.user_agent_cache.keys(),
                key=lambda k: self.user_agent_cache[k].created_at
            )
            del self.user_agent_cache[oldest_key]
            
        self.user_agent_cache[cache_key] = ua_data
        
    def _perform_rotation(self):
        """Utför user-agent rotation"""
        
        self.rotation_counter = 0
        self.current_session_ua = None
        self.stats['rotations_performed'] += 1
        
        logging.info("User agent rotation performed")
        
    def _extract_version_from_ua(self, ua: str) -> str:
        """Extrahera browser version från user agent string"""
        
        import re
        
        # Chrome version pattern
        chrome_match = re.search(r'Chrome/(\d+\.\d+)', ua)
        if chrome_match:
            return chrome_match.group(1)
            
        # Firefox version pattern
        firefox_match = re.search(r'Firefox/(\d+\.\d+)', ua)
        if firefox_match:
            return firefox_match.group(1)
            
        # Safari version pattern
        safari_match = re.search(r'Version/(\d+\.\d+)', ua)
        if safari_match:
            return safari_match.group(1)
            
        # Edge version pattern
        edge_match = re.search(r'Edg?/(\d+\.\d+)', ua)
        if edge_match:
            return edge_match.group(1)
            
        return "Unknown"
        
    def _extract_browser_from_ua(self, ua: str) -> str:
        """Extrahera browser från user agent string"""
        
        ua_lower = ua.lower()
        
        if 'chrome' in ua_lower and 'edg' not in ua_lower:
            return 'Chrome'
        elif 'firefox' in ua_lower:
            return 'Firefox'
        elif 'safari' in ua_lower and 'chrome' not in ua_lower:
            return 'Safari'
        elif 'edg' in ua_lower:
            return 'Edge'
        elif 'opera' in ua_lower or 'opr' in ua_lower:
            return 'Opera'
        else:
            return 'Unknown'
            
    def _extract_os_from_ua(self, ua: str) -> str:
        """Extrahera OS från user agent string"""
        
        ua_lower = ua.lower()
        
        if 'windows nt 10.0' in ua_lower:
            return 'Windows'
        elif 'macintosh' in ua_lower or 'mac os x' in ua_lower:
            return 'Mac OS X'
        elif 'linux' in ua_lower:
            return 'Linux'
        elif 'android' in ua_lower:
            return 'Android'
        elif 'iphone' in ua_lower or 'ipad' in ua_lower:
            return 'iOS'
        else:
            return 'Unknown'
            
    def _generate_matching_headers(self, ua_data: UserAgentData) -> Dict[str, str]:
        """Generera matchande headers för user agent"""
        
        headers = {
            'User-Agent': ua_data.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # Browser-specific headers
        if ua_data.browser.lower() == 'chrome':
            headers['sec-ch-ua'] = '"Google Chrome";v="120", "Chromium";v="120", "Not:A-Brand";v="99"'
            headers['sec-ch-ua-mobile'] = '?0'
            headers['sec-ch-ua-platform'] = f'"{ua_data.os}"'
            headers['Sec-Fetch-Dest'] = 'document'
            headers['Sec-Fetch-Mode'] = 'navigate'
            headers['Sec-Fetch-Site'] = 'none'
            headers['Sec-Fetch-User'] = '?1'
            
        elif ua_data.browser.lower() == 'firefox':
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            headers['DNT'] = '1'
            
        elif ua_data.browser.lower() == 'safari':
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            
        # Platform-specific adjustments
        if ua_data.platform == 'mobile':
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
            if 'sec-ch-ua-mobile' in headers:
                headers['sec-ch-ua-mobile'] = '?1'
                
        return headers
        
    def _generate_fingerprint_data(self, ua_data: UserAgentData) -> Dict[str, Any]:
        """Generera fingerprint-data som matchar user agent"""
        
        fingerprint = {
            'screen_resolution': self._get_typical_resolution(ua_data.platform),
            'timezone': self._get_typical_timezone(),
            'language': 'en-US',
            'color_depth': 24,
            'device_memory': self._get_typical_memory(ua_data.platform),
            'hardware_concurrency': self._get_typical_cores(ua_data.platform),
            'touch_support': ua_data.platform == 'mobile'
        }
        
        # Browser-specific fingerprint data
        if ua_data.browser.lower() == 'chrome':
            fingerprint['webgl_vendor'] = 'Google Inc. (Intel)'
            fingerprint['webgl_renderer'] = 'Intel HD Graphics 630'
            
        elif ua_data.browser.lower() == 'firefox':
            fingerprint['webgl_vendor'] = 'Mozilla'
            fingerprint['webgl_renderer'] = 'Intel Open Source Technology Center'
            
        return fingerprint
        
    def _get_typical_resolution(self, platform: str) -> Tuple[int, int]:
        """Få typisk skärmupplösning för plattform"""
        
        if platform == 'mobile':
            resolutions = [(375, 667), (414, 896), (360, 640), (393, 851)]
        elif platform == 'tablet':
            resolutions = [(1024, 768), (768, 1024), (800, 1280), (1200, 1920)]
        else:  # desktop
            resolutions = [(1920, 1080), (1366, 768), (1440, 900), (1536, 864)]
            
        return random.choice(resolutions)
        
    def _get_typical_timezone(self) -> str:
        """Få typisk timezone"""
        timezones = ['America/New_York', 'Europe/London', 'America/Los_Angeles', 'UTC']
        return random.choice(timezones)
        
    def _get_typical_memory(self, platform: str) -> int:
        """Få typisk device memory för plattform"""
        
        if platform == 'mobile':
            return random.choice([2, 4, 6, 8])
        elif platform == 'tablet':
            return random.choice([3, 4, 6, 8])
        else:  # desktop
            return random.choice([4, 8, 16, 32])
            
    def _get_typical_cores(self, platform: str) -> int:
        """Få typisk antal CPU cores för plattform"""
        
        if platform == 'mobile':
            return random.choice([4, 6, 8])
        elif platform == 'tablet':
            return random.choice([4, 6, 8])
        else:  # desktop
            return random.choice([4, 6, 8, 12, 16])
            
    def _validate_consistency(self, ua_data: UserAgentData):
        """Validera konsistens mellan UA och fingerprint-data"""
        
        self.stats['consistency_checks'] += 1
        
        # Validera platform consistency
        ua_lower = ua_data.user_agent.lower()
        if ua_data.platform == 'mobile' and 'mobile' not in ua_lower:
            if 'android' not in ua_lower and 'iphone' not in ua_lower:
                self.stats['validation_failures'] += 1
                logging.warning(f"Platform consistency issue: {ua_data.platform} vs {ua_data.user_agent}")
                
        # Validera browser version consistency
        if ua_data.browser_version == "Unknown":
            self.stats['validation_failures'] += 1
            
    def get_random_user_agent(self) -> UserAgentData:
        """Få en slumpmässig user agent"""
        return self.get_user_agent()
        
    def get_chrome_user_agent(self) -> UserAgentData:
        """Få en Chrome user agent"""
        return self.get_user_agent(browser="chrome")
        
    def get_firefox_user_agent(self) -> UserAgentData:
        """Få en Firefox user agent"""
        return self.get_user_agent(browser="firefox")
        
    def get_mobile_user_agent(self) -> UserAgentData:
        """Få en mobil user agent"""
        return self.get_user_agent(platform="mobile")
        
    def get_desktop_user_agent(self) -> UserAgentData:
        """Få en desktop user agent"""
        return self.get_user_agent(platform="desktop")
        
    def clear_cache(self):
        """Rensa user agent cache"""
        self.user_agent_cache.clear()
        logging.info("User agent cache cleared")
        
    def reset_session(self):
        """Återställ session (för ny session persistence)"""
        self.current_session_ua = None
        self.rotation_counter = 0
        logging.info("User agent session reset")
        
    def get_statistics(self) -> Dict[str, Any]:
        """Hämta detaljerad statistik"""
        stats = self.stats.copy()
        stats.update({
            'cache_size': len(self.user_agent_cache),
            'cache_hit_rate': (
                self.stats['cache_hits'] / 
                max(1, self.stats['cache_hits'] + self.stats['cache_misses'])
            ) * 100,
            'fallback_rate': (
                self.stats['fallback_used'] / 
                max(1, self.stats['user_agents_generated'])
            ) * 100,
            'current_session_ua': self.current_session_ua.user_agent if self.current_session_ua else None
        })
        return stats
        
    def integrate_with_stealth(self, ua_data: UserAgentData) -> Dict[str, Any]:
        """Integrera user agent med stealth manager"""
        
        if not self.stealth_manager:
            return {}
            
        # Update stealth config with UA data
        self.stealth_manager.config.nav_user_agent = ua_data.user_agent
        
        # Set consistent fingerprint data
        if ua_data.fingerprint_data:
            self.stealth_manager.config.vendor = ua_data.fingerprint_data.get(
                'webgl_vendor', self.stealth_manager.config.vendor
            )
            self.stealth_manager.config.renderer = ua_data.fingerprint_data.get(
                'webgl_renderer', self.stealth_manager.config.renderer  
            )
            
        return {
            'stealth_config_updated': True,
            'fingerprint_consistency': True
        }


class StealthUserAgentRotator:
    """
    Bekvämlighets-klass som kombinerar user-agent management med stealth
    """
    
    def __init__(self, **config_kwargs):
        self.config = UserAgentConfig(**config_kwargs)
        self.ua_manager = AdvancedUserAgentManager(self.config)
        
    def get_stealth_headers(self, **filters) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """Få stealth-optimerade headers och fingerprint data"""
        
        ua_data = self.ua_manager.get_user_agent(**filters)
        stealth_integration = self.ua_manager.integrate_with_stealth(ua_data)
        
        return ua_data.headers, ua_data.fingerprint_data
        
    def rotate_user_agent(self, **filters) -> UserAgentData:
        """Forcera rotation och få ny user agent"""
        return self.ua_manager.get_user_agent(force_new=True, **filters)
        
    def get_session_headers(self, **filters) -> Dict[str, str]:
        """Få konsistenta headers för en session"""
        ua_data = self.ua_manager.get_user_agent(**filters)
        return ua_data.headers
        
    def get_statistics(self) -> Dict[str, Any]:
        """Få statistik"""
        return self.ua_manager.get_statistics()


async def demo_fake_useragent():
    """Demo av Advanced Fake-UserAgent Integration"""
    
    print("🎭 Advanced Fake-UserAgent Integration Demo")
    
    # Test basic functionality
    rotator = StealthUserAgentRotator(
        rotation_interval=3,
        session_persistence=False,
        cache_enabled=True
    )
    
    print("🎯 Testing random user agents...")
    for i in range(5):
        ua_data = rotator.ua_manager.get_random_user_agent()
        print(f"  {i+1}. {ua_data.browser} {ua_data.browser_version} on {ua_data.os}")
        print(f"     Platform: {ua_data.platform}, Usage: {ua_data.percentage:.1f}%")
        print(f"     UA: {ua_data.user_agent[:80]}...")
        
    print("\n🌐 Testing browser-specific agents...")
    
    # Test Chrome
    chrome_ua = rotator.ua_manager.get_chrome_user_agent()
    print(f"Chrome: {chrome_ua.browser} {chrome_ua.browser_version}")
    
    # Test Firefox  
    firefox_ua = rotator.ua_manager.get_firefox_user_agent()
    print(f"Firefox: {firefox_ua.browser} {firefox_ua.browser_version}")
    
    # Test Mobile
    mobile_ua = rotator.ua_manager.get_mobile_user_agent()
    print(f"Mobile: {mobile_ua.browser} on {mobile_ua.platform}")
    
    print("\n📱 Testing stealth integration...")
    headers, fingerprint = rotator.get_stealth_headers(browser="chrome")
    
    print("🔧 Generated Headers:")
    for key, value in list(headers.items())[:5]:
        print(f"  {key}: {value}")
        
    print("\n👁️ Generated Fingerprint Data:")
    for key, value in list(fingerprint.items())[:5]:
        print(f"  {key}: {value}")
        
    # Test rotation
    print("\n🔄 Testing forced rotation...")
    ua1 = rotator.ua_manager.get_user_agent()
    ua2 = rotator.rotate_user_agent()
    
    print(f"Before: {ua1.user_agent[:50]}...")
    print(f"After:  {ua2.user_agent[:50]}...")
    print(f"Different: {ua1.user_agent != ua2.user_agent}")
    
    # Statistics
    stats = rotator.get_statistics()
    print(f"\n📈 Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_fake_useragent())
