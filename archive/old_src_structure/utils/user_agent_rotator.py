"""
User-Agent rotation system for ECaDP platform.

Provides realistic User-Agent strings for web scraping with rotation capabilities.
"""

import random
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class UserAgentInfo:
    """Information about a User-Agent string."""
    agent_string: str
    browser: str
    os: str
    version: str
    popularity_score: float = 1.0
    last_used: Optional[datetime] = None
    usage_count: int = 0

class UserAgentRotator:
    """Manages User-Agent rotation for anti-detection."""
    
    def __init__(self, strategy: str = "random"):
        self.strategy = strategy
        self.user_agents = self._load_user_agents()
        self._usage_history = {}
        
    def _load_user_agents(self) -> List[UserAgentInfo]:
        """Load comprehensive list of realistic User-Agent strings."""
        # Modern Chrome on Windows
        chrome_windows = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        
        # Modern Chrome on macOS
        chrome_macos = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Apple M1 Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        
        # Modern Firefox on Windows
        firefox_windows = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        ]
        
        # Modern Firefox on macOS
        firefox_macos = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:119.0) Gecko/20100101 Firefox/119.0",
        ]
        
        # Safari on macOS
        safari_macos = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        ]
        
        # Edge on Windows
        edge_windows = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        ]
        
        # Mobile User Agents
        mobile_agents = [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
            "Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        ]
        
        user_agents = []
        
        # Chrome agents (highest popularity)
        for ua in chrome_windows:
            user_agents.append(UserAgentInfo(ua, "Chrome", "Windows", "120", 2.0))
        for ua in chrome_macos:
            user_agents.append(UserAgentInfo(ua, "Chrome", "macOS", "120", 1.8))
            
        # Firefox agents (medium popularity)
        for ua in firefox_windows:
            user_agents.append(UserAgentInfo(ua, "Firefox", "Windows", "120", 1.2))
        for ua in firefox_macos:
            user_agents.append(UserAgentInfo(ua, "Firefox", "macOS", "120", 1.0))
            
        # Safari agents (macOS specific)
        for ua in safari_macos:
            user_agents.append(UserAgentInfo(ua, "Safari", "macOS", "17", 1.5))
            
        # Edge agents (moderate popularity)
        for ua in edge_windows:
            user_agents.append(UserAgentInfo(ua, "Edge", "Windows", "120", 1.3))
            
        # Mobile agents (lower priority for web scraping)
        for ua in mobile_agents:
            user_agents.append(UserAgentInfo(ua, "Mobile", "Mobile", "Various", 0.8))
        
        return user_agents
    
    def get_user_agent(self, browser: Optional[str] = None, os: Optional[str] = None) -> str:
        """Get a User-Agent string based on strategy and filters."""
        filtered_agents = self.user_agents
        
        # Apply filters
        if browser:
            filtered_agents = [ua for ua in filtered_agents if ua.browser.lower() == browser.lower()]
        if os:
            filtered_agents = [ua for ua in filtered_agents if ua.os.lower() == os.lower()]
        
        if not filtered_agents:
            logger.warning(f"No user agents found for browser={browser}, os={os}")
            filtered_agents = self.user_agents
        
        # Apply selection strategy
        if self.strategy == "random":
            selected = random.choice(filtered_agents)
        elif self.strategy == "weighted":
            selected = self._weighted_selection(filtered_agents)
        elif self.strategy == "round_robin":
            selected = self._round_robin_selection(filtered_agents)
        elif self.strategy == "least_used":
            selected = self._least_used_selection(filtered_agents)
        else:
            selected = random.choice(filtered_agents)
        
        # Update usage tracking
        selected.usage_count += 1
        selected.last_used = datetime.now()
        
        return selected.agent_string
    
    def _weighted_selection(self, agents: List[UserAgentInfo]) -> UserAgentInfo:
        """Select User-Agent based on popularity weights."""
        weights = [ua.popularity_score for ua in agents]
        return random.choices(agents, weights=weights)[0]
    
    def _round_robin_selection(self, agents: List[UserAgentInfo]) -> UserAgentInfo:
        """Select User-Agent using round-robin strategy."""
        return min(agents, key=lambda ua: ua.usage_count)
    
    def _least_used_selection(self, agents: List[UserAgentInfo]) -> UserAgentInfo:
        """Select least recently used User-Agent."""
        return min(agents, key=lambda ua: ua.last_used or datetime.min)
    
    def get_browser_specific_agent(self, browser: str) -> str:
        """Get User-Agent for specific browser."""
        return self.get_user_agent(browser=browser)
    
    def get_desktop_agent(self) -> str:
        """Get desktop User-Agent (excludes mobile)."""
        desktop_agents = [ua for ua in self.user_agents if ua.browser != "Mobile"]
        if self.strategy == "weighted":
            return self._weighted_selection(desktop_agents).agent_string
        else:
            return random.choice(desktop_agents).agent_string
    
    def get_mobile_agent(self) -> str:
        """Get mobile User-Agent."""
        mobile_agents = [ua for ua in self.user_agents if ua.browser == "Mobile"]
        return random.choice(mobile_agents).agent_string
    
    def get_chrome_agent(self) -> str:
        """Get Chrome User-Agent (most common)."""
        return self.get_user_agent(browser="Chrome")
    
    def get_firefox_agent(self) -> str:
        """Get Firefox User-Agent."""
        return self.get_user_agent(browser="Firefox")
    
    def get_safari_agent(self) -> str:
        """Get Safari User-Agent."""
        return self.get_user_agent(browser="Safari")
    
    def get_usage_stats(self) -> Dict[str, any]:
        """Get usage statistics for User-Agents."""
        total_usage = sum(ua.usage_count for ua in self.user_agents)
        browser_stats = {}
        os_stats = {}
        
        for ua in self.user_agents:
            # Browser stats
            if ua.browser not in browser_stats:
                browser_stats[ua.browser] = {"count": 0, "usage": 0}
            browser_stats[ua.browser]["count"] += 1
            browser_stats[ua.browser]["usage"] += ua.usage_count
            
            # OS stats
            if ua.os not in os_stats:
                os_stats[ua.os] = {"count": 0, "usage": 0}
            os_stats[ua.os]["count"] += 1
            os_stats[ua.os]["usage"] += ua.usage_count
        
        return {
            "total_agents": len(self.user_agents),
            "total_usage": total_usage,
            "strategy": self.strategy,
            "browser_distribution": browser_stats,
            "os_distribution": os_stats
        }
    
    def reset_usage_stats(self):
        """Reset usage statistics."""
        for ua in self.user_agents:
            ua.usage_count = 0
            ua.last_used = None

# Global rotator instance
_rotator = None

def get_user_agent_rotator(strategy: str = "random") -> UserAgentRotator:
    """Get global User-Agent rotator instance."""
    global _rotator
    if _rotator is None or _rotator.strategy != strategy:
        _rotator = UserAgentRotator(strategy)
    return _rotator

def get_random_user_agent() -> str:
    """Convenience function to get random User-Agent."""
    return get_user_agent_rotator().get_user_agent()

def get_chrome_user_agent() -> str:
    """Convenience function to get Chrome User-Agent."""
    return get_user_agent_rotator().get_chrome_agent()

__all__ = [
    "UserAgentInfo", "UserAgentRotator", 
    "get_user_agent_rotator", "get_random_user_agent", "get_chrome_user_agent"
]