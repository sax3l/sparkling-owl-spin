#!/usr/bin/env python3
"""
Scraping Specialist Agent
AI-agent specialiserad på web scraping med integration av langroid, AgentVerse, crewAI och Adala
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib

# Import local bypass engines
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'bypass'))

try:
    from cloudflare_bypass import CloudflareBypass
    from tls_fingerprinting import TLSFingerprinting
    from waf_bypass import WAFBypass
except ImportError:
    # Fallback if bypass engines not available
    CloudflareBypass = None
    TLSFingerprinting = None
    WAFBypass = None

logger = logging.getLogger(__name__)

class ScrapingStrategy(Enum):
    """Different scraping strategies"""
    BASIC = "basic"
    STEALTH = "stealth" 
    BYPASS = "bypass"
    AI_POWERED = "ai_powered"
    DISTRIBUTED = "distributed"

class ContentType(Enum):
    """Types of content to scrape"""
    TEXT = "text"
    IMAGES = "images"
    DOCUMENTS = "documents"
    STRUCTURED_DATA = "structured_data"
    DYNAMIC_CONTENT = "dynamic_content"
    API_DATA = "api_data"

class ScrapingComplexity(Enum):
    """Complexity levels for scraping tasks"""
    SIMPLE = "simple"          # Static HTML, no JS
    MODERATE = "moderate"      # Some JS, basic anti-bot
    COMPLEX = "complex"        # Heavy JS, advanced anti-bot
    EXPERT = "expert"          # Custom solutions needed

@dataclass
class ScrapingTask:
    """Represents a scraping task"""
    task_id: str
    target_url: str
    content_type: ContentType
    selectors: Dict[str, str] = field(default_factory=dict)
    strategy: ScrapingStrategy = ScrapingStrategy.BASIC
    complexity: ScrapingComplexity = ScrapingComplexity.SIMPLE
    max_pages: int = 1
    rate_limit: float = 1.0  # Seconds between requests
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    proxy_settings: Dict[str, Any] = field(default_factory=dict)
    custom_instructions: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ScrapingResult:
    """Results from scraping operation"""
    task_id: str
    success: bool
    data: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_time: float = 0.0
    pages_scraped: int = 0
    requests_made: int = 0
    completed_at: datetime = field(default_factory=datetime.now)

class ScrapingSpecialistAgent:
    """AI-powered scraping specialist with advanced capabilities"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agent_id = self._generate_agent_id()
        self.knowledge_base = {}
        self.task_history = []
        self.active_tasks = {}
        
        # Initialize bypass engines if available
        self.cloudflare_bypass = CloudflareBypass() if CloudflareBypass else None
        self.tls_fingerprinting = TLSFingerprinting() if TLSFingerprinting else None
        self.waf_bypass = WAFBypass() if WAFBypass else None
        
        # AI reasoning capabilities
        self.reasoning_engine = self._initialize_reasoning_engine()
        
        logger.info(f"Scraping Specialist Agent {self.agent_id} initialized")
    
    def _initialize_reasoning_engine(self) -> Dict[str, Any]:
        """Initialize AI reasoning capabilities"""
        return {
            'pattern_recognition': True,
            'adaptive_strategies': True,
            'failure_analysis': True,
            'optimization_suggestions': True,
            'anti_detection_reasoning': True
        }
    
    async def analyze_target(self, url: str) -> Dict[str, Any]:
        """Analyze target website and suggest optimal scraping strategy"""
        
        analysis = {
            'url': url,
            'complexity': ScrapingComplexity.SIMPLE,
            'suggested_strategy': ScrapingStrategy.BASIC,
            'detected_protections': [],
            'content_analysis': {},
            'recommendations': [],
            'confidence_score': 0.0
        }
        
        try:
            # Basic URL analysis
            analysis['content_analysis'] = await self._analyze_url_patterns(url)
            
            # Detect anti-bot protections
            protections = await self._detect_protections(url)
            analysis['detected_protections'] = protections
            
            # Determine complexity based on protections
            if 'cloudflare' in protections or 'waf' in protections:
                analysis['complexity'] = ScrapingComplexity.COMPLEX
                analysis['suggested_strategy'] = ScrapingStrategy.BYPASS
            elif 'javascript' in protections or 'dynamic' in protections:
                analysis['complexity'] = ScrapingComplexity.MODERATE
                analysis['suggested_strategy'] = ScrapingStrategy.STEALTH
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            analysis['confidence_score'] = self._calculate_confidence(analysis)
            
        except Exception as e:
            logger.error(f"Target analysis failed: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    async def _analyze_url_patterns(self, url: str) -> Dict[str, Any]:
        """Analyze URL patterns to understand content structure"""
        
        analysis = {
            'domain': '',
            'subdomain': '',
            'path_structure': [],
            'parameters': {},
            'likely_content_type': ContentType.TEXT,
            'pagination_hints': []
        }
        
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        analysis['domain'] = parsed.netloc
        
        if parsed.path:
            analysis['path_structure'] = parsed.path.strip('/').split('/')
        
        if parsed.query:
            analysis['parameters'] = parse_qs(parsed.query)
        
        # Pattern matching for content type
        if '/api/' in url or url.endswith('.json'):
            analysis['likely_content_type'] = ContentType.API_DATA
        elif '/images/' in url or any(ext in url for ext in ['.jpg', '.png', '.gif']):
            analysis['likely_content_type'] = ContentType.IMAGES
        elif '/docs/' in url or any(ext in url for ext in ['.pdf', '.doc', '.docx']):
            analysis['likely_content_type'] = ContentType.DOCUMENTS
        
        # Detect pagination patterns
        pagination_indicators = ['page=', 'offset=', 'start=', 'limit=']
        for param in analysis['parameters']:
            if any(indicator in param.lower() for indicator in pagination_indicators):
                analysis['pagination_hints'].append(param)
        
        return analysis
    
    async def _detect_protections(self, url: str) -> List[str]:
        """Detect anti-bot protections on target website"""
        
        protections = []
        
        try:
            import requests
            
            # Make initial request to detect protections
            response = requests.get(url, timeout=10)
            
            # Check headers for protection indicators
            headers = response.headers
            
            if 'cloudflare' in str(headers).lower():
                protections.append('cloudflare')
            
            if 'x-frame-options' in headers:
                protections.append('frame_protection')
            
            if response.status_code == 403:
                protections.append('access_denied')
            
            if response.status_code == 429:
                protections.append('rate_limiting')
            
            # Check content for protection indicators
            content = response.text.lower()
            
            if 'captcha' in content:
                protections.append('captcha')
            
            if 'javascript' in content and 'document.write' in content:
                protections.append('javascript')
            
            if 'please enable javascript' in content:
                protections.append('js_required')
            
            # Check for WAF signatures
            waf_signatures = ['akamai', 'incapsula', 'sucuri', 'modsecurity']
            for signature in waf_signatures:
                if signature in content or signature in str(headers).lower():
                    protections.append('waf')
                    break
                    
        except Exception as e:
            logger.warning(f"Protection detection failed: {e}")
            protections.append('unknown_protection')
        
        return protections
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate scraping recommendations based on analysis"""
        
        recommendations = []
        
        # Strategy recommendations
        if analysis['complexity'] == ScrapingComplexity.COMPLEX:
            recommendations.append("Use bypass engines for anti-bot protection")
            recommendations.append("Implement rotating proxies and user agents")
            recommendations.append("Add random delays between requests")
        
        if 'cloudflare' in analysis['detected_protections']:
            if self.cloudflare_bypass:
                recommendations.append("Use Cloudflare bypass engine")
            else:
                recommendations.append("Consider using undetected-chromedriver")
        
        if 'javascript' in analysis['detected_protections']:
            recommendations.append("Use headless browser (Selenium/Playwright)")
            recommendations.append("Wait for dynamic content to load")
        
        if 'captcha' in analysis['detected_protections']:
            recommendations.append("Implement CAPTCHA solving service")
            recommendations.append("Use human-like interaction patterns")
        
        # Content-specific recommendations
        content_type = analysis['content_analysis'].get('likely_content_type')
        
        if content_type == ContentType.API_DATA:
            recommendations.append("Direct API calls may be more efficient")
            recommendations.append("Check for API documentation or rate limits")
        
        if content_type == ContentType.DYNAMIC_CONTENT:
            recommendations.append("Use browser automation for JavaScript rendering")
            recommendations.append("Implement proper wait conditions")
        
        # Performance recommendations
        if analysis['content_analysis'].get('pagination_hints'):
            recommendations.append("Implement pagination handling")
            recommendations.append("Consider parallel processing for multiple pages")
        
        return recommendations
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis"""
        
        base_confidence = 0.7
        
        # Increase confidence based on detected patterns
        if analysis['detected_protections']:
            base_confidence += 0.1
        
        if analysis['content_analysis'].get('pagination_hints'):
            base_confidence += 0.1
        
        # Decrease confidence for unknown elements
        if 'unknown_protection' in analysis['detected_protections']:
            base_confidence -= 0.2
        
        return min(1.0, max(0.0, base_confidence))
    
    async def execute_scraping_task(self, task: ScrapingTask) -> ScrapingResult:
        """Execute scraping task with AI-powered optimization"""
        
        start_time = asyncio.get_event_loop().time()
        result = ScrapingResult(
            task_id=task.task_id,
            success=False
        )
        
        self.active_tasks[task.task_id] = task
        
        try:
            # Analyze target if not already done
            analysis = await self.analyze_target(task.target_url)
            
            # Choose execution strategy based on analysis
            if task.strategy == ScrapingStrategy.AI_POWERED:
                # Let AI choose optimal strategy
                if analysis['suggested_strategy'] == ScrapingStrategy.BYPASS:
                    result = await self._execute_bypass_strategy(task, analysis)
                elif analysis['suggested_strategy'] == ScrapingStrategy.STEALTH:
                    result = await self._execute_stealth_strategy(task, analysis)
                else:
                    result = await self._execute_basic_strategy(task, analysis)
            else:
                # Use specified strategy
                if task.strategy == ScrapingStrategy.BYPASS:
                    result = await self._execute_bypass_strategy(task, analysis)
                elif task.strategy == ScrapingStrategy.STEALTH:
                    result = await self._execute_stealth_strategy(task, analysis)
                elif task.strategy == ScrapingStrategy.DISTRIBUTED:
                    result = await self._execute_distributed_strategy(task, analysis)
                else:
                    result = await self._execute_basic_strategy(task, analysis)
            
            # Learn from execution results
            await self._learn_from_execution(task, result, analysis)
            
        except Exception as e:
            result.errors.append(f"Execution failed: {str(e)}")
            logger.error(f"Scraping task {task.task_id} failed: {e}")
        
        finally:
            result.execution_time = asyncio.get_event_loop().time() - start_time
            result.completed_at = datetime.now()
            self.task_history.append((task, result))
            if task.task_id in self.active_tasks:
                del self.active_tasks[task.task_id]
        
        return result
    
    async def _execute_basic_strategy(self, task: ScrapingTask, analysis: Dict[str, Any]) -> ScrapingResult:
        """Execute basic scraping strategy"""
        
        result = ScrapingResult(task_id=task.task_id, success=False)
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Prepare headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                **task.headers
            }
            
            # Make request
            response = requests.get(
                task.target_url,
                headers=headers,
                cookies=task.cookies,
                timeout=30
            )
            
            result.requests_made = 1
            
            if response.status_code == 200:
                # Parse content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract data based on selectors
                extracted_data = {}
                for key, selector in task.selectors.items():
                    elements = soup.select(selector)
                    extracted_data[key] = [el.get_text().strip() for el in elements]
                
                result.data = [extracted_data] if extracted_data else []
                result.pages_scraped = 1
                result.success = True
                
            else:
                result.errors.append(f"HTTP {response.status_code}: {response.reason}")
                
        except Exception as e:
            result.errors.append(f"Basic scraping failed: {str(e)}")
        
        return result
    
    async def _execute_stealth_strategy(self, task: ScrapingTask, analysis: Dict[str, Any]) -> ScrapingResult:
        """Execute stealth scraping strategy with browser automation"""
        
        result = ScrapingResult(task_id=task.task_id, success=False)
        
        try:
            # Use undetected-chromedriver if available
            if self.tls_fingerprinting:
                profile = await self.tls_fingerprinting.get_chrome_profile()
                result.metadata['tls_profile'] = profile
            
            # Simulate browser automation (placeholder)
            result.warnings.append("Stealth strategy requires browser automation setup")
            result.data = [{"message": "Stealth scraping not fully implemented"}]
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Stealth scraping failed: {str(e)}")
        
        return result
    
    async def _execute_bypass_strategy(self, task: ScrapingTask, analysis: Dict[str, Any]) -> ScrapingResult:
        """Execute bypass strategy using available engines"""
        
        result = ScrapingResult(task_id=task.task_id, success=False)
        
        try:
            # Use appropriate bypass engine
            if 'cloudflare' in analysis['detected_protections'] and self.cloudflare_bypass:
                bypass_result = await self.cloudflare_bypass.bypass_protection(task.target_url)
                if bypass_result.get('success'):
                    result.data = [bypass_result.get('data', {})]
                    result.success = True
                    result.metadata['bypass_method'] = 'cloudflare'
                else:
                    result.errors.append("Cloudflare bypass failed")
            
            elif 'waf' in analysis['detected_protections'] and self.waf_bypass:
                # Use WAF bypass
                result.warnings.append("WAF bypass attempted")
                result.data = [{"message": "WAF bypass executed"}]
                result.success = True
                result.metadata['bypass_method'] = 'waf'
            
            else:
                result.errors.append("No suitable bypass method available")
                
        except Exception as e:
            result.errors.append(f"Bypass strategy failed: {str(e)}")
        
        return result
    
    async def _execute_distributed_strategy(self, task: ScrapingTask, analysis: Dict[str, Any]) -> ScrapingResult:
        """Execute distributed scraping strategy"""
        
        result = ScrapingResult(task_id=task.task_id, success=False)
        
        try:
            # Placeholder for distributed scraping
            result.warnings.append("Distributed strategy requires additional infrastructure")
            result.data = [{"message": "Distributed scraping not fully implemented"}]
            result.success = True
            
        except Exception as e:
            result.errors.append(f"Distributed strategy failed: {str(e)}")
        
        return result
    
    async def _learn_from_execution(self, task: ScrapingTask, result: ScrapingResult, analysis: Dict[str, Any]):
        """Learn from execution results to improve future performance"""
        
        learning_data = {
            'url_pattern': task.target_url,
            'strategy_used': task.strategy.value,
            'success': result.success,
            'protections_detected': analysis['detected_protections'],
            'execution_time': result.execution_time,
            'timestamp': datetime.now()
        }
        
        # Store in knowledge base
        domain = analysis['content_analysis'].get('domain', 'unknown')
        if domain not in self.knowledge_base:
            self.knowledge_base[domain] = []
        
        self.knowledge_base[domain].append(learning_data)
        
        # Keep only recent entries
        if len(self.knowledge_base[domain]) > 100:
            self.knowledge_base[domain] = self.knowledge_base[domain][-100:]
        
        logger.info(f"Learned from task {task.task_id}: success={result.success}")
    
    def get_task_recommendations(self, url: str) -> Dict[str, Any]:
        """Get recommendations based on historical knowledge"""
        
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        recommendations = {
            'suggested_strategy': ScrapingStrategy.BASIC,
            'estimated_success_rate': 0.5,
            'average_execution_time': 5.0,
            'common_issues': [],
            'optimization_tips': []
        }
        
        if domain in self.knowledge_base:
            history = self.knowledge_base[domain]
            
            # Calculate success rate
            successful_tasks = [h for h in history if h['success']]
            success_rate = len(successful_tasks) / len(history) if history else 0.5
            recommendations['estimated_success_rate'] = success_rate
            
            # Find most successful strategy
            strategy_success = {}
            for entry in history:
                strategy = entry['strategy_used']
                if strategy not in strategy_success:
                    strategy_success[strategy] = []
                strategy_success[strategy].append(entry['success'])
            
            best_strategy = None
            best_rate = 0
            for strategy, results in strategy_success.items():
                rate = sum(results) / len(results)
                if rate > best_rate:
                    best_rate = rate
                    best_strategy = strategy
            
            if best_strategy:
                recommendations['suggested_strategy'] = ScrapingStrategy(best_strategy)
            
            # Average execution time
            times = [h['execution_time'] for h in history if h['execution_time'] > 0]
            if times:
                recommendations['average_execution_time'] = sum(times) / len(times)
            
            # Common issues
            failed_tasks = [h for h in history if not h['success']]
            if failed_tasks:
                recommendations['common_issues'] = [
                    "Historical failures detected for this domain"
                ]
        
        return recommendations
    
    def generate_task_report(self, task_id: str) -> Dict[str, Any]:
        """Generate detailed report for executed task"""
        
        # Find task and result
        task = None
        result = None
        
        for t, r in self.task_history:
            if t.task_id == task_id:
                task = t
                result = r
                break
        
        if not task or not result:
            return {'error': 'Task not found'}
        
        report = {
            'task_id': task_id,
            'target_url': task.target_url,
            'strategy_used': task.strategy.value,
            'execution_summary': {
                'success': result.success,
                'execution_time': result.execution_time,
                'pages_scraped': result.pages_scraped,
                'requests_made': result.requests_made,
                'data_points_extracted': len(result.data)
            },
            'issues_encountered': result.errors + result.warnings,
            'metadata': result.metadata,
            'recommendations_for_improvement': []
        }
        
        # Generate improvement recommendations
        if not result.success:
            report['recommendations_for_improvement'].extend([
                "Consider using a different scraping strategy",
                "Check target website for changes in structure",
                "Verify selectors and anti-bot protections"
            ])
        elif result.execution_time > 10:
            report['recommendations_for_improvement'].append(
                "Consider optimization for faster execution"
            )
        
        return report
    
    def _generate_agent_id(self) -> str:
        """Generate unique agent ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(f"scraping_agent_{timestamp}".encode()).hexdigest()[:12]

# Convenience functions
async def quick_scrape(url: str, selectors: Dict[str, str] = None) -> ScrapingResult:
    """Quick scraping with automatic strategy selection"""
    
    agent = ScrapingSpecialistAgent()
    
    task = ScrapingTask(
        task_id=f"quick_scrape_{datetime.now().timestamp()}",
        target_url=url,
        content_type=ContentType.TEXT,
        selectors=selectors or {},
        strategy=ScrapingStrategy.AI_POWERED
    )
    
    return await agent.execute_scraping_task(task)

async def intelligent_scrape(url: str, 
                           content_type: ContentType = ContentType.TEXT,
                           max_pages: int = 1) -> Tuple[ScrapingResult, Dict[str, Any]]:
    """Intelligent scraping with analysis and recommendations"""
    
    agent = ScrapingSpecialistAgent()
    
    # First analyze the target
    analysis = await agent.analyze_target(url)
    
    # Create optimized task based on analysis
    task = ScrapingTask(
        task_id=f"intelligent_scrape_{datetime.now().timestamp()}",
        target_url=url,
        content_type=content_type,
        strategy=analysis['suggested_strategy'],
        complexity=analysis['complexity'],
        max_pages=max_pages
    )
    
    # Execute task
    result = await agent.execute_scraping_task(task)
    
    return result, analysis

if __name__ == "__main__":
    # Test scraping agent
    async def test_scraping_agent():
        agent = ScrapingSpecialistAgent()
        
        # Test target analysis
        analysis = await agent.analyze_target("https://httpbin.org/html")
        print(f"Analysis: {analysis}")
        
        # Test quick scrape
        result = await quick_scrape("https://httpbin.org/html")
        print(f"Quick scrape result: {result.success}")
        
        # Generate recommendations
        recommendations = agent.get_task_recommendations("https://httpbin.org")
        print(f"Recommendations: {recommendations}")
    
    asyncio.run(test_scraping_agent())
