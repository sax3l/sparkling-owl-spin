"""
Human behavior simulation for stealth browsing.

Implements realistic human-like interactions including:
- Natural mouse movements and patterns
- Realistic scrolling behaviors
- Human typing patterns with variations
- Reading time simulation
- Click patterns and timing
"""

import random
import time
import asyncio
import math
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)

class UserProfile(Enum):
    """Different user behavior profiles."""
    CAREFUL = "careful"      # Slow, deliberate actions
    NORMAL = "normal"        # Average user behavior
    POWER_USER = "power"     # Fast, efficient actions
    ELDERLY = "elderly"      # Slower, more pauses
    MOBILE = "mobile"        # Touch-like interactions

@dataclass
class BehaviorConfig:
    """Configuration for human behavior simulation."""
    reading_speed_wpm: int  # Words per minute
    typing_speed_wpm: int   # Typing words per minute
    mistake_probability: float  # Probability of typing mistakes
    pause_probability: float    # Probability of pauses
    scroll_speed: float         # Pixels per second
    click_precision: float      # Click accuracy (0-1)
    attention_span: int         # Seconds before getting distracted

class HumanBehaviorSimulator:
    """Simulates realistic human behavior patterns."""
    
    def __init__(self, profile: UserProfile = UserProfile.NORMAL):
        self.profile = profile
        self.config = self._get_profile_config(profile)
        self.session_start = time.time()
        self.total_actions = 0
        self.fatigue_factor = 0.0  # Increases over time
    
    def _get_profile_config(self, profile: UserProfile) -> BehaviorConfig:
        """Get behavior configuration for different user profiles."""
        configs = {
            UserProfile.CAREFUL: BehaviorConfig(
                reading_speed_wpm=180,
                typing_speed_wpm=25,
                mistake_probability=0.02,
                pause_probability=0.3,
                scroll_speed=200,
                click_precision=0.95,
                attention_span=45
            ),
            UserProfile.NORMAL: BehaviorConfig(
                reading_speed_wpm=250,
                typing_speed_wpm=40,
                mistake_probability=0.05,
                pause_probability=0.2,
                scroll_speed=400,
                click_precision=0.9,
                attention_span=30
            ),
            UserProfile.POWER_USER: BehaviorConfig(
                reading_speed_wpm=350,
                typing_speed_wpm=65,
                mistake_probability=0.08,
                pause_probability=0.1,
                scroll_speed=600,
                click_precision=0.85,
                attention_span=60
            ),
            UserProfile.ELDERLY: BehaviorConfig(
                reading_speed_wpm=150,
                typing_speed_wpm=15,
                mistake_probability=0.03,
                pause_probability=0.4,
                scroll_speed=150,
                click_precision=0.8,
                attention_span=20
            ),
            UserProfile.MOBILE: BehaviorConfig(
                reading_speed_wpm=200,
                typing_speed_wpm=20,
                mistake_probability=0.1,
                pause_probability=0.25,
                scroll_speed=300,
                click_precision=0.8,
                attention_span=25
            )
        }
        return configs[profile]
    
    def calculate_reading_time(self, text: str) -> float:
        """Calculate realistic reading time for text."""
        word_count = len(text.split())
        base_time = (word_count / self.config.reading_speed_wpm) * 60
        
        # Add fatigue factor
        fatigue_multiplier = 1 + (self.fatigue_factor * 0.3)
        
        # Add random variation (±20%)
        variation = random.uniform(0.8, 1.2)
        
        # Minimum reading time
        min_time = max(1.0, word_count * 0.1)
        
        return max(min_time, base_time * fatigue_multiplier * variation)
    
    def calculate_typing_delay(self, char: str, prev_char: str = None) -> float:
        """Calculate realistic delay between keystrokes."""
        base_delay = 60 / (self.config.typing_speed_wpm * 5)  # Average char per minute
        
        # Character-specific delays
        if char == ' ':
            delay_multiplier = random.uniform(1.2, 2.0)  # Longer pause for spaces
        elif char in '.,!?;:':
            delay_multiplier = random.uniform(1.5, 2.5)  # Pause after punctuation
        elif char.isupper():
            delay_multiplier = random.uniform(1.1, 1.4)  # Shift key delay
        elif prev_char and prev_char.islower() and char.isupper():
            delay_multiplier = random.uniform(1.3, 1.6)  # Case change
        else:
            delay_multiplier = random.uniform(0.8, 1.2)
        
        # Add fatigue
        fatigue_multiplier = 1 + (self.fatigue_factor * 0.5)
        
        # Random hesitation
        if random.random() < self.config.pause_probability:
            hesitation = random.uniform(0.5, 2.0)
        else:
            hesitation = 0
        
        return (base_delay * delay_multiplier * fatigue_multiplier) + hesitation
    
    def should_make_typing_mistake(self) -> bool:
        """Determine if a typing mistake should occur."""
        mistake_prob = self.config.mistake_probability * (1 + self.fatigue_factor)
        return random.random() < mistake_prob
    
    def generate_typing_mistake(self, correct_char: str) -> str:
        """Generate a realistic typing mistake."""
        # Common keyboard layout mistakes
        qwerty_neighbors = {
            'q': ['w', 'a'], 'w': ['q', 'e', 's'], 'e': ['w', 'r', 'd'],
            'r': ['e', 't', 'f'], 't': ['r', 'y', 'g'], 'y': ['t', 'u', 'h'],
            'u': ['y', 'i', 'j'], 'i': ['u', 'o', 'k'], 'o': ['i', 'p', 'l'],
            'p': ['o', 'l'], 'a': ['q', 's', 'z'], 's': ['a', 'w', 'd', 'x'],
            'd': ['s', 'e', 'f', 'c'], 'f': ['d', 'r', 'g', 'v'],
            'g': ['f', 't', 'h', 'b'], 'h': ['g', 'y', 'j', 'n'],
            'j': ['h', 'u', 'k', 'm'], 'k': ['j', 'i', 'l'], 'l': ['k', 'o', 'p'],
            'z': ['a', 's', 'x'], 'x': ['z', 's', 'd', 'c'], 'c': ['x', 'd', 'f', 'v'],
            'v': ['c', 'f', 'g', 'b'], 'b': ['v', 'g', 'h', 'n'],
            'n': ['b', 'h', 'j', 'm'], 'm': ['n', 'j', 'k']
        }
        
        char_lower = correct_char.lower()
        if char_lower in qwerty_neighbors:
            mistake_char = random.choice(qwerty_neighbors[char_lower])
            return mistake_char.upper() if correct_char.isupper() else mistake_char
        
        return correct_char  # No mistake if no neighbors defined
    
    async def simulate_typing(self, text: str, element=None) -> List[Dict[str, Any]]:
        """Simulate realistic typing with mistakes and corrections."""
        actions = []
        typed_text = ""
        
        i = 0
        while i < len(text):
            char = text[i]
            prev_char = text[i-1] if i > 0 else None
            
            # Calculate delay
            delay = self.calculate_typing_delay(char, prev_char)
            
            # Check for typing mistake
            if self.should_make_typing_mistake() and char.isalpha():
                mistake_char = self.generate_typing_mistake(char)
                
                # Type mistake
                actions.append({
                    'action': 'type',
                    'char': mistake_char,
                    'delay_before': delay,
                    'is_mistake': True
                })
                typed_text += mistake_char
                
                # Realize mistake after a short delay
                correction_delay = random.uniform(0.3, 1.5)
                actions.append({
                    'action': 'pause',
                    'duration': correction_delay,
                    'reason': 'mistake_realization'
                })
                
                # Backspace to correct
                actions.append({
                    'action': 'backspace',
                    'delay_before': random.uniform(0.1, 0.3)
                })
                typed_text = typed_text[:-1]
                
                # Type correct character
                correction_delay = random.uniform(0.2, 0.6)
                actions.append({
                    'action': 'type',
                    'char': char,
                    'delay_before': correction_delay,
                    'is_correction': True
                })
                typed_text += char
            else:
                # Type correct character
                actions.append({
                    'action': 'type',
                    'char': char,
                    'delay_before': delay,
                    'is_mistake': False
                })
                typed_text += char
            
            i += 1
            self.total_actions += 1
            self._update_fatigue()
        
        return actions
    
    def generate_mouse_path(self, start: Tuple[int, int], 
                          end: Tuple[int, int], 
                          num_points: int = None) -> List[Tuple[int, int]]:
        """Generate realistic mouse movement path."""
        start_x, start_y = start
        end_x, end_y = end
        
        distance = math.sqrt((end_x - start_x) ** 2 + (end_y - start_y) ** 2)
        
        if num_points is None:
            # More points for longer distances
            num_points = max(5, int(distance / 50))
        
        # Generate path with some natural curvature
        points = [start]
        
        for i in range(1, num_points):
            progress = i / num_points
            
            # Linear interpolation with curve
            base_x = start_x + (end_x - start_x) * progress
            base_y = start_y + (end_y - start_y) * progress
            
            # Add natural curve/wobble
            curve_intensity = distance * 0.1
            wobble_x = random.uniform(-curve_intensity, curve_intensity) * math.sin(progress * math.pi)
            wobble_y = random.uniform(-curve_intensity, curve_intensity) * math.cos(progress * math.pi)
            
            # Add precision factor
            precision_noise = (1 - self.config.click_precision) * 10
            noise_x = random.uniform(-precision_noise, precision_noise)
            noise_y = random.uniform(-precision_noise, precision_noise)
            
            final_x = int(base_x + wobble_x + noise_x)
            final_y = int(base_y + wobble_y + noise_y)
            
            points.append((final_x, final_y))
        
        points.append(end)
        return points
    
    def calculate_mouse_speed(self, distance: float) -> float:
        """Calculate realistic mouse movement speed."""
        # Fitts's Law approximation for mouse movement time
        base_time = 0.1 + 0.2 * math.log2(1 + distance / 50)
        
        # Add profile-specific variation
        speed_multiplier = {
            UserProfile.CAREFUL: 1.3,
            UserProfile.NORMAL: 1.0,
            UserProfile.POWER_USER: 0.7,
            UserProfile.ELDERLY: 1.6,
            UserProfile.MOBILE: 1.2
        }[self.profile]
        
        # Add fatigue effect
        fatigue_multiplier = 1 + (self.fatigue_factor * 0.4)
        
        return base_time * speed_multiplier * fatigue_multiplier
    
    async def simulate_scroll(self, direction: str = "down", 
                            amount: int = None) -> Dict[str, Any]:
        """Simulate realistic scrolling behavior."""
        if amount is None:
            # Random scroll amount based on viewport
            amount = random.randint(100, 400)
        
        # Calculate scroll duration
        pixels_per_second = self.config.scroll_speed * (1 - self.fatigue_factor * 0.3)
        duration = amount / pixels_per_second
        
        # Add natural variation to scrolling
        scroll_pattern = []
        remaining = amount
        
        while remaining > 0:
            # Variable scroll chunks
            chunk_size = min(remaining, random.randint(50, 150))
            chunk_duration = chunk_size / pixels_per_second
            
            scroll_pattern.append({
                'pixels': chunk_size,
                'duration': chunk_duration,
                'direction': direction
            })
            
            remaining -= chunk_size
            
            # Small pause between chunks
            if remaining > 0:
                pause_duration = random.uniform(0.05, 0.2)
                scroll_pattern.append({
                    'pause': pause_duration
                })
        
        return {
            'pattern': scroll_pattern,
            'total_duration': duration,
            'total_amount': amount
        }
    
    def calculate_page_dwell_time(self, page_complexity: str = "medium") -> float:
        """Calculate how long to spend on a page."""
        base_times = {
            "simple": 3,
            "medium": 8,
            "complex": 20
        }
        
        base_time = base_times.get(page_complexity, 8)
        
        # Profile-specific adjustments
        profile_multipliers = {
            UserProfile.CAREFUL: 1.5,
            UserProfile.NORMAL: 1.0,
            UserProfile.POWER_USER: 0.6,
            UserProfile.ELDERLY: 2.0,
            UserProfile.MOBILE: 1.2
        }
        
        multiplier = profile_multipliers[self.profile]
        
        # Add random variation
        variation = random.uniform(0.7, 1.5)
        
        # Consider fatigue
        fatigue_effect = 1 + (self.fatigue_factor * 0.5)
        
        return base_time * multiplier * variation * fatigue_effect
    
    def should_get_distracted(self) -> bool:
        """Determine if user should get distracted."""
        session_time = time.time() - self.session_start
        
        # Probability increases over time and with fatigue
        base_prob = 0.02
        time_factor = min(session_time / 3600, 1.0)  # Max after 1 hour
        distraction_prob = base_prob + (time_factor * 0.1) + (self.fatigue_factor * 0.15)
        
        return random.random() < distraction_prob
    
    def generate_distraction_behavior(self) -> Dict[str, Any]:
        """Generate distraction behavior (pause, tab switch, etc.)."""
        distraction_types = [
            {"type": "pause", "duration": random.uniform(2, 10), "reason": "thinking"},
            {"type": "pause", "duration": random.uniform(5, 30), "reason": "distraction"},
            {"type": "tab_switch", "duration": random.uniform(3, 15)},
            {"type": "scroll_up", "reason": "re-reading"},
            {"type": "mouse_fidget", "duration": random.uniform(1, 5)}
        ]
        
        return random.choice(distraction_types)
    
    def _update_fatigue(self):
        """Update fatigue factor based on session time and actions."""
        session_time = time.time() - self.session_start
        
        # Fatigue increases with time and number of actions
        time_fatigue = min(session_time / 7200, 0.5)  # Max 0.5 after 2 hours
        action_fatigue = min(self.total_actions / 1000, 0.3)  # Max 0.3 after 1000 actions
        
        self.fatigue_factor = time_fatigue + action_fatigue
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        session_time = time.time() - self.session_start
        
        return {
            "profile": self.profile.value,
            "session_duration": session_time,
            "total_actions": self.total_actions,
            "fatigue_factor": self.fatigue_factor,
            "actions_per_minute": self.total_actions / max(session_time / 60, 1),
            "config": {
                "reading_speed_wpm": self.config.reading_speed_wpm,
                "typing_speed_wpm": self.config.typing_speed_wpm,
                "mistake_probability": self.config.mistake_probability
            }
        }

class BehaviorAnalyzer:
    """Analyzes and validates behavior patterns for realism."""
    
    def __init__(self):
        self.action_history = []
        self.timing_patterns = []
    
    def record_action(self, action_type: str, timestamp: float, 
                     duration: float = None, metadata: Dict = None):
        """Record an action for analysis."""
        self.action_history.append({
            "type": action_type,
            "timestamp": timestamp,
            "duration": duration,
            "metadata": metadata or {}
        })
    
    def analyze_typing_patterns(self) -> Dict[str, Any]:
        """Analyze typing patterns for realism."""
        typing_actions = [a for a in self.action_history if a["type"] == "type"]
        
        if len(typing_actions) < 10:
            return {"status": "insufficient_data"}
        
        # Calculate inter-keystroke intervals
        intervals = []
        for i in range(1, len(typing_actions)):
            interval = typing_actions[i]["timestamp"] - typing_actions[i-1]["timestamp"]
            intervals.append(interval)
        
        # Statistical analysis
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        
        # Check for too regular patterns (bot-like)
        regularity_score = 1 - (variance / (avg_interval ** 2))
        
        return {
            "status": "analyzed",
            "avg_interval": avg_interval,
            "variance": variance,
            "regularity_score": regularity_score,
            "is_human_like": regularity_score < 0.7  # Threshold for human-like
        }
    
    def analyze_mouse_patterns(self) -> Dict[str, Any]:
        """Analyze mouse movement patterns."""
        mouse_actions = [a for a in self.action_history if a["type"] == "mouse_move"]
        
        if len(mouse_actions) < 5:
            return {"status": "insufficient_data"}
        
        # Analyze movement smoothness and naturality
        velocities = []
        for i in range(1, len(mouse_actions)):
            prev_action = mouse_actions[i-1]
            curr_action = mouse_actions[i]
            
            time_diff = curr_action["timestamp"] - prev_action["timestamp"]
            if time_diff > 0:
                # Calculate velocity (simplified)
                velocity = 1 / time_diff  # Simplified velocity measure
                velocities.append(velocity)
        
        if velocities:
            avg_velocity = sum(velocities) / len(velocities)
            velocity_variance = sum((v - avg_velocity) ** 2 for v in velocities) / len(velocities)
            
            return {
                "status": "analyzed",
                "avg_velocity": avg_velocity,
                "velocity_variance": velocity_variance,
                "num_movements": len(mouse_actions)
            }
        
        return {"status": "no_movement_data"}

# Factory function for creating behavior simulators
def create_behavior_simulator(profile: UserProfile = UserProfile.NORMAL) -> HumanBehaviorSimulator:
    """Create a human behavior simulator with specified profile."""
    return HumanBehaviorSimulator(profile)

# Utility functions
async def simulate_realistic_page_visit(simulator: HumanBehaviorSimulator, 
                                      page_content: str,
                                      complexity: str = "medium") -> Dict[str, Any]:
    """Simulate a complete realistic page visit."""
    start_time = time.time()
    
    # Calculate reading time
    reading_time = simulator.calculate_reading_time(page_content)
    
    # Calculate dwell time
    dwell_time = simulator.calculate_page_dwell_time(complexity)
    
    # Simulate scrolling behavior
    num_scrolls = random.randint(2, 5)
    scroll_actions = []
    
    for _ in range(num_scrolls):
        scroll_data = await simulator.simulate_scroll()
        scroll_actions.append(scroll_data)
        
        # Pause between scrolls
        pause_time = random.uniform(1, 4)
        await asyncio.sleep(pause_time)
    
    # Check for distractions
    distractions = []
    if simulator.should_get_distracted():
        distraction = simulator.generate_distraction_behavior()
        distractions.append(distraction)
    
    total_time = time.time() - start_time
    
    return {
        "reading_time": reading_time,
        "dwell_time": dwell_time,
        "actual_time": total_time,
        "scrolls": scroll_actions,
        "distractions": distractions,
        "session_stats": simulator.get_session_stats()
    }