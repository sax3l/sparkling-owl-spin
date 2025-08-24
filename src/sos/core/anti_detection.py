"""
Advanced Anti-Detection System
Integrates techniques from leading stealth crawling tools and frameworks
"""

import asyncio
import random
import string
import time
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from urllib.parse import urlparse, urljoin
import base64
import re

class DetectionType(Enum):
    RATE_LIMITING = "rate_limiting"
    CAPTCHA = "captcha"  
    IP_BLOCKING = "ip_blocking"
    BROWSER_FINGERPRINTING = "browser_fingerprinting"
    BEHAVIOR_ANALYSIS = "behavior_analysis"
    CONTENT_ENCODING = "content_encoding"

@dataclass
class DetectionEvent:
    """Detection event data"""
    detection_type: DetectionType
    url: str
    timestamp: float
    details: Dict[str, Any]
    severity: int  # 1-10

class ProxyRotator:
    """Advanced proxy rotation with health monitoring"""
    
    def __init__(self, proxy_list: List[str]):
        self.proxy_list = proxy_list
        self.proxy_stats = {}
        self.failed_proxies = set()
        self.current_index = 0
        self.logger = logging.getLogger("proxy_rotator")
        
        # Initialize stats
        for proxy in proxy_list:
            self.proxy_stats[proxy] = {
                'success_count': 0,
                'failure_count': 0,
                'avg_response_time': 0,
                'last_used': 0,
                'consecutive_failures': 0,
                'blocked_until': 0  # Timestamp when proxy becomes available again
            }
    
    def get_best_proxy(self) -> Optional[str]:
        """Get the best available proxy based on performance"""
        current_time = time.time()
        available_proxies = []
        
        for proxy in self.proxy_list:
            stats = self.proxy_stats[proxy]
            
            # Skip if proxy is temporarily blocked
            if stats['blocked_until'] > current_time:
                continue
            
            # Skip if too many consecutive failures
            if stats['consecutive_failures'] >= 3:
                continue
            
            # Calculate proxy score (higher is better)
            success_rate = stats['success_count'] / max(1, stats['success_count'] + stats['failure_count'])
            response_time_penalty = min(stats['avg_response_time'] / 10, 1)  # Penalty for slow proxies
            freshness = max(0, 1 - (current_time - stats['last_used']) / 3600)  # Prefer recently unused
            
            score = success_rate - response_time_penalty + freshness * 0.1
            available_proxies.append((proxy, score))
        
        if not available_proxies:
            # Reset all proxies if none available
            self._reset_failed_proxies()
            return self.proxy_list[0] if self.proxy_list else None
        
        # Sort by score and return best
        available_proxies.sort(key=lambda x: x[1], reverse=True)
        return available_proxies[0][0]
    
    def mark_success(self, proxy: str, response_time: float):
        """Mark proxy as successful"""
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats['success_count'] += 1
            stats['consecutive_failures'] = 0
            stats['last_used'] = time.time()
            
            # Update average response time
            if stats['avg_response_time'] == 0:
                stats['avg_response_time'] = response_time
            else:
                stats['avg_response_time'] = (stats['avg_response_time'] * 0.8) + (response_time * 0.2)
    
    def mark_failure(self, proxy: str, block_duration: int = 300):
        """Mark proxy as failed"""
        if proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            stats['failure_count'] += 1
            stats['consecutive_failures'] += 1
            stats['blocked_until'] = time.time() + block_duration
            
            self.logger.warning(f"Proxy {proxy} failed. Consecutive failures: {stats['consecutive_failures']}")
    
    def _reset_failed_proxies(self):
        """Reset failed proxies after cooldown"""
        current_time = time.time()
        for proxy in self.proxy_stats:
            stats = self.proxy_stats[proxy]
            if stats['blocked_until'] <= current_time:
                stats['consecutive_failures'] = 0
                stats['blocked_until'] = 0

class UserAgentRotator:
    """Advanced user agent rotation with consistency"""
    
    def __init__(self):
        self.user_agents = {
            'chrome_windows': [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            ],
            'chrome_mac': [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            ],
            'firefox_windows': [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
            ],
            'safari_mac': [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            ],
            'mobile_chrome': [
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            ]
        }
        
        self.session_agents = {}  # Maintain consistency per session
    
    def get_consistent_agent(self, session_id: str, category: str = None) -> str:
        """Get consistent user agent for session"""
        if session_id in self.session_agents:
            return self.session_agents[session_id]
        
        if category is None:
            category = random.choice(list(self.user_agents.keys()))
        
        agent = random.choice(self.user_agents[category])
        self.session_agents[session_id] = agent
        return agent
    
    def get_matching_headers(self, user_agent: str) -> Dict[str, str]:
        """Get headers that match the user agent"""
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Browser-specific headers
        if 'Chrome' in user_agent:
            headers.update({
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?1' if 'Mobile' in user_agent else '?0',
                'sec-ch-ua-platform': '"Android"' if 'Android' in user_agent else '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
            })
        elif 'Firefox' in user_agent:
            headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        
        return headers

class CaptchaSolver:
    """CAPTCHA detection and solving system"""
    
    def __init__(self):
        self.detection_patterns = [
            r'captcha',
            r'recaptcha',
            r'hcaptcha',
            r'cloudflare',
            r'security.check',
            r'robot.verification',
            r'prove.you.are.human',
        ]
        self.logger = logging.getLogger("captcha_solver")
    
    def detect_captcha(self, content: str, url: str) -> bool:
        """Detect if page contains CAPTCHA"""
        content_lower = content.lower()
        
        for pattern in self.detection_patterns:
            if re.search(pattern, content_lower):
                self.logger.warning(f"CAPTCHA detected on {url}: {pattern}")
                return True
        
        # Check for common CAPTCHA indicators
        indicators = [
            'challenge-form',
            'cf-browser-verification',
            'g-recaptcha',
            'h-captcha',
            'captcha-container',
        ]
        
        for indicator in indicators:
            if indicator in content_lower:
                self.logger.warning(f"CAPTCHA indicator found on {url}: {indicator}")
                return True
        
        return False
    
    async def solve_captcha(self, page_content: str, url: str) -> Optional[Dict[str, Any]]:
        """Attempt to solve CAPTCHA (placeholder for integration with services)"""
        self.logger.info(f"Attempting to solve CAPTCHA for {url}")
        
        # This would integrate with services like 2captcha, AntiCaptcha, etc.
        # For now, return failure to trigger retry logic
        return None
    
    def get_bypass_strategy(self, captcha_type: str) -> str:
        """Get strategy to bypass specific CAPTCHA type"""
        strategies = {
            'cloudflare': 'wait_and_retry',
            'recaptcha': 'service_solve',
            'hcaptcha': 'service_solve',
            'simple': 'ocr_solve',
        }
        
        return strategies.get(captcha_type, 'wait_and_retry')

class BehaviorMimicker:
    """Mimic human browsing behavior"""
    
    def __init__(self):
        self.session_behavior = {}
        self.logger = logging.getLogger("behavior_mimicker")
    
    async def mimic_human_timing(self, action_type: str = 'page_load'):
        """Add human-like delays"""
        delays = {
            'page_load': (2, 8),      # Time to read page
            'click': (0.5, 2),        # Time before clicking
            'typing': (0.1, 0.3),     # Time between keystrokes
            'scroll': (1, 4),         # Time spent reading between scrolls
            'navigation': (1, 3),     # Time between page navigations
        }
        
        min_delay, max_delay = delays.get(action_type, (1, 3))
        delay = random.uniform(min_delay, max_delay)
        
        self.logger.debug(f"Human timing delay for {action_type}: {delay:.2f}s")
        await asyncio.sleep(delay)
    
    def generate_realistic_headers(self, base_headers: Dict[str, str]) -> Dict[str, str]:
        """Generate realistic headers with variations"""
        headers = base_headers.copy()
        
        # Add random order variations
        header_items = list(headers.items())
        random.shuffle(header_items)
        
        # Add optional headers randomly
        optional_headers = {
            'Cache-Control': 'max-age=0',
            'Pragma': 'no-cache',
            'X-Requested-With': 'XMLHttpRequest' if random.random() < 0.1 else None,
        }
        
        for key, value in optional_headers.items():
            if value and random.random() < 0.3:
                headers[key] = value
        
        return headers
    
    def generate_mouse_movements(self, viewport_size: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate realistic mouse movement path"""
        width, height = viewport_size
        movements = []
        
        # Start at random position
        current_x = random.randint(100, width - 100)
        current_y = random.randint(100, height - 100)
        movements.append((current_x, current_y))
        
        # Generate curved path with 5-15 points
        num_points = random.randint(5, 15)
        for i in range(num_points):
            # Add some randomness with tendency to move toward target
            move_x = random.randint(-50, 50)
            move_y = random.randint(-50, 50)
            
            current_x = max(0, min(width, current_x + move_x))
            current_y = max(0, min(height, current_y + move_y))
            movements.append((current_x, current_y))
        
        return movements
    
    def simulate_typing_pattern(self, text: str) -> List[Tuple[str, float]]:
        """Generate realistic typing pattern with delays"""
        typing_events = []
        
        for char in text:
            # Base delay with variations
            if char == ' ':
                delay = random.uniform(0.1, 0.3)  # Longer for spaces
            elif char in '.,!?':
                delay = random.uniform(0.2, 0.5)  # Longer for punctuation
            else:
                delay = random.uniform(0.05, 0.15)  # Normal characters
            
            # Occasional longer pauses (thinking)
            if random.random() < 0.1:
                delay += random.uniform(0.5, 2.0)
            
            typing_events.append((char, delay))
        
        return typing_events

class AntiDetectionManager:
    """Main anti-detection coordinator"""
    
    def __init__(self, proxy_list: List[str] = None):
        self.proxy_rotator = ProxyRotator(proxy_list or [])
        self.user_agent_rotator = UserAgentRotator()
        self.captcha_solver = CaptchaSolver()
        self.behavior_mimicker = BehaviorMimicker()
        
        self.session_data = {}
        self.detection_events = []
        self.logger = logging.getLogger("anti_detection")
    
    def create_session(self, session_id: str = None) -> str:
        """Create new crawling session with consistent identity"""
        if session_id is None:
            session_id = self._generate_session_id()
        
        # Generate consistent identity for session
        user_agent = self.user_agent_rotator.get_consistent_agent(session_id)
        headers = self.user_agent_rotator.get_matching_headers(user_agent)
        
        self.session_data[session_id] = {
            'user_agent': user_agent,
            'headers': headers,
            'proxy': self.proxy_rotator.get_best_proxy(),
            'created': time.time(),
            'request_count': 0,
            'last_request': 0,
        }
        
        self.logger.info(f"Created session {session_id} with UA: {user_agent[:50]}...")
        return session_id
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(int(time.time()))
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        return f"session_{timestamp}_{random_part}"
    
    async def prepare_request(self, session_id: str, url: str) -> Dict[str, Any]:
        """Prepare request with anti-detection measures"""
        if session_id not in self.session_data:
            session_id = self.create_session(session_id)
        
        session = self.session_data[session_id]
        session['request_count'] += 1
        session['last_request'] = time.time()
        
        # Add behavioral timing
        await self.behavior_mimicker.mimic_human_timing('navigation')
        
        # Rotate proxy if needed
        if session['request_count'] % 10 == 0:  # Rotate every 10 requests
            session['proxy'] = self.proxy_rotator.get_best_proxy()
            self.logger.info(f"Rotated proxy for session {session_id}")
        
        # Generate realistic headers
        headers = self.behavior_mimicker.generate_realistic_headers(session['headers'])
        
        return {
            'headers': headers,
            'proxy': session['proxy'],
            'user_agent': session['user_agent'],
            'session_id': session_id,
        }
    
    async def handle_response(self, response_data: Dict[str, Any]) -> bool:
        """Handle response and detect anti-bot measures"""
        url = response_data.get('url', '')
        status_code = response_data.get('status_code', 200)
        content = response_data.get('content', '')
        session_id = response_data.get('session_id', '')
        
        # Check for various detection types
        detections = []
        
        # Rate limiting detection
        if status_code == 429:
            detections.append(DetectionEvent(
                DetectionType.RATE_LIMITING,
                url,
                time.time(),
                {'status_code': 429},
                8
            ))
        
        # CAPTCHA detection
        if self.captcha_solver.detect_captcha(content, url):
            detections.append(DetectionEvent(
                DetectionType.CAPTCHA,
                url,
                time.time(),
                {'type': 'captcha_page'},
                9
            ))
        
        # IP blocking detection
        if status_code in [403, 451] or 'access denied' in content.lower():
            detections.append(DetectionEvent(
                DetectionType.IP_BLOCKING,
                url,
                time.time(),
                {'status_code': status_code},
                9
            ))
        
        # Behavior analysis detection (suspicious redirects)
        if 'challenge' in content.lower() or 'verification' in content.lower():
            detections.append(DetectionEvent(
                DetectionType.BEHAVIOR_ANALYSIS,
                url,
                time.time(),
                {'type': 'challenge_page'},
                7
            ))
        
        # Process detections
        for detection in detections:
            await self._handle_detection(detection, session_id)
        
        return len(detections) == 0  # Return True if no detections
    
    async def _handle_detection(self, detection: DetectionEvent, session_id: str):
        """Handle specific detection event"""
        self.detection_events.append(detection)
        self.logger.warning(f"Detection event: {detection.detection_type.value} on {detection.url}")
        
        # Get session data
        session = self.session_data.get(session_id, {})
        current_proxy = session.get('proxy')
        
        if detection.detection_type == DetectionType.RATE_LIMITING:
            # Implement exponential backoff
            backoff_time = min(300, 10 * (2 ** len(self.detection_events)))
            self.logger.info(f"Rate limited. Backing off for {backoff_time}s")
            await asyncio.sleep(backoff_time)
        
        elif detection.detection_type == DetectionType.IP_BLOCKING:
            # Mark current proxy as failed and switch
            if current_proxy:
                self.proxy_rotator.mark_failure(current_proxy, block_duration=3600)
            session['proxy'] = self.proxy_rotator.get_best_proxy()
            self.logger.info("Switched proxy due to IP blocking")
        
        elif detection.detection_type == DetectionType.CAPTCHA:
            # Attempt to solve CAPTCHA or switch proxy
            solution = await self.captcha_solver.solve_captcha("", detection.url)
            if not solution:
                if current_proxy:
                    self.proxy_rotator.mark_failure(current_proxy, block_duration=1800)
                session['proxy'] = self.proxy_rotator.get_best_proxy()
                self.logger.info("CAPTCHA detected, switched proxy")
        
        elif detection.detection_type == DetectionType.BEHAVIOR_ANALYSIS:
            # Mimic more human-like behavior
            await self.behavior_mimicker.mimic_human_timing('page_load')
            self.logger.info("Behavioral detection, adjusting timing")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for session"""
        if session_id not in self.session_data:
            return {}
        
        session = self.session_data[session_id]
        current_time = time.time()
        
        return {
            'session_id': session_id,
            'requests_made': session['request_count'],
            'duration': current_time - session['created'],
            'current_proxy': session.get('proxy'),
            'user_agent': session['user_agent'][:50] + '...',
            'detections': len([d for d in self.detection_events if d.timestamp > session['created']]),
        }
    
    def get_detection_summary(self) -> Dict[str, Any]:
        """Get summary of all detection events"""
        detection_counts = {}
        for detection in self.detection_events:
            detection_type = detection.detection_type.value
            detection_counts[detection_type] = detection_counts.get(detection_type, 0) + 1
        
        recent_detections = [
            d for d in self.detection_events 
            if d.timestamp > time.time() - 3600  # Last hour
        ]
        
        return {
            'total_detections': len(self.detection_events),
            'recent_detections': len(recent_detections),
            'detection_types': detection_counts,
            'avg_severity': sum(d.severity for d in self.detection_events) / max(1, len(self.detection_events)),
        }

# Example usage
async def example_stealth_crawling():
    """Example of stealth crawling with anti-detection"""
    
    # Initialize anti-detection manager
    proxies = [
        "http://proxy1:8080",
        "http://proxy2:8080", 
        "http://proxy3:8080"
    ]
    
    anti_detection = AntiDetectionManager(proxy_list=proxies)
    
    # Create crawling session
    session_id = anti_detection.create_session()
    
    # Example URLs to crawl
    urls = [
        "https://example.com",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/headers",
    ]
    
    results = []
    
    for url in urls:
        try:
            # Prepare request with anti-detection measures
            request_config = await anti_detection.prepare_request(session_id, url)
            
            # Simulate making request (replace with actual HTTP client)
            print(f"Crawling {url} with proxy {request_config['proxy']}")
            print(f"Headers: {list(request_config['headers'].keys())}")
            
            # Simulate response
            response_data = {
                'url': url,
                'status_code': 200,
                'content': f'<html><title>Page for {url}</title></html>',
                'session_id': session_id,
            }
            
            # Handle response and check for detections
            success = await anti_detection.handle_response(response_data)
            
            if success:
                results.append(f"Successfully crawled {url}")
            else:
                results.append(f"Detections found for {url}")
        
        except Exception as e:
            print(f"Error crawling {url}: {str(e)}")
    
    # Print session statistics
    stats = anti_detection.get_session_stats(session_id)
    print(f"\nSession Stats: {stats}")
    
    detection_summary = anti_detection.get_detection_summary()
    print(f"Detection Summary: {detection_summary}")
    
    return results

if __name__ == "__main__":
    asyncio.run(example_stealth_crawling())
