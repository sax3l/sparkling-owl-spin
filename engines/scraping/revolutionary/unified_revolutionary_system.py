#!/usr/bin/env python3
"""
Revolutionary Ultimate System v4.0 - Unified Integration
Complete integration of all high-priority components and advanced features.

This is the master system that coordinates:
- Anti-bot Defense System (v4.0)
- Content Extraction System (v4.0)  
- URL Discovery System (v4.0)
- Advanced Proxy Management (v4.0)
- OSINT & Analytics System (v4.0)
- Configuration Management (v4.0)
"""

import asyncio
import logging
import time
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from urllib.parse import urlparse, urljoin

# Import all integrated systems
from .anti_bot_system import AntiBottSystem, BotDefenseResult
from .content_extraction_system import ContentExtractionSystem, ExtractionResult, QualityScore
from .url_discovery_system import URLDiscoverySystem, URLDiscoveryResult, CrawlPolicy
from .advanced_proxy_system import ProxyManager, ProxyInfo
from .advanced_osint_system import OSINTAnalytics, DomainIntelligence, IPIntelligence
from .system_configuration import SystemConfiguration, DomainPolicy
from .revolutionary_ultimate_v4 import RevolutionaryUltimateSystem

# GitHub Integration Registry
try:
    from .integrations.github_registry import (
        registry as github_registry,
        IntegrationCategory,
        load_integration,
        execute_integration_operation,
        get_integration_recommendations,
        perform_integration_health_check
    )
    GITHUB_REGISTRY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"GitHub integration registry not available: {e}")
    GITHUB_REGISTRY_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class UnifiedCrawlResult:
    """Complete result from unified crawling operation"""
    url: str
    success: bool = False
    status_code: Optional[int] = None
    
    # Content data
    content: Optional[ExtractionResult] = None
    quality_score: Optional[QualityScore] = None
    
    # Discovery data
    discovered_urls: Set[str] = field(default_factory=set)
    discovery_metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Intelligence data
    domain_intel: Optional[DomainIntelligence] = None
    ip_intel: Dict[str, IPIntelligence] = field(default_factory=dict)
    
    # Technical data
    bot_defense: Optional[BotDefenseResult] = None
    proxy_used: Optional[ProxyInfo] = None
    response_time: float = 0.0
    
    # Metadata
    timestamp: float = field(default_factory=time.time)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

@dataclass
class CrawlSession:
    """Session tracking for unified crawling"""
    session_id: str
    start_time: float
    target_domain: str
    policy: DomainPolicy
    results: List[UnifiedCrawlResult] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    active: bool = True

class UnifiedRevolutionarySystem:
    """
    Master system integrating all Revolutionary v4.0 components.
    
    This system provides a unified interface to all advanced capabilities:
    - Intelligent anti-bot defense with escalation strategies
    - Multi-engine URL discovery and deep crawling
    - Advanced content extraction with quality assessment
    - Enterprise proxy management with AWS rotation
    - OSINT threat intelligence and security analysis
    - Per-domain policy configuration and management
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the unified revolutionary system"""
        logger.info("🚀 Initializing Revolutionary Ultimate System v4.0")
        
        # Load system configuration
        self.config = SystemConfiguration(config_path)
        
        # Initialize all subsystems
        self._initialize_subsystems()
        
        # Session management
        self.active_sessions: Dict[str, CrawlSession] = {}
        self.session_counter = 0
        
        # Performance metrics
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'avg_response_time': 0.0,
            'proxies_used': 0,
            'captchas_solved': 0,
            'urls_discovered': 0,
            'content_extracted': 0,
            'intelligence_gathered': 0
        }
        
        # Background tasks
        self._background_tasks: List[asyncio.Task] = []
        
    def _initialize_subsystems(self):
        """Initialize all integrated subsystems"""
        logger.info("🔧 Initializing integrated subsystems...")
        
        # Anti-bot defense system
        self.anti_bot = AntiBottSystem(self.config.get_anti_bot_config())
        logger.info("✅ Anti-bot defense system initialized")
        
        # Content extraction system  
        self.content_extractor = ContentExtractionSystem(self.config.get_extraction_config())
        logger.info("✅ Content extraction system initialized")
        
        # URL discovery system
        self.url_discovery = URLDiscoverySystem(self.config.get_url_discovery_config())
        logger.info("✅ URL discovery system initialized")
        
        # Proxy management system
        self.proxy_manager = ProxyManager(self.config.get_proxy_config())
        logger.info("✅ Advanced proxy management initialized")
        
        # OSINT analytics system
        self.osint_analytics = OSINTAnalytics(self.config.get_osint_config())
        logger.info("✅ OSINT & analytics system initialized")
        
        # Legacy revolutionary system for backward compatibility
        self.legacy_system = RevolutionaryUltimateSystem(self.config.config_path)
        logger.info("✅ Legacy system compatibility initialized")
        
        # GitHub Integration Registry
        self.github_integrations = {}
        self.github_registry_enabled = GITHUB_REGISTRY_AVAILABLE
        if self.github_registry_enabled:
            logger.info("✅ GitHub integration registry available")
        else:
            logger.warning("⚠️ GitHub integration registry not available")
        
        logger.info("🎯 All subsystems initialized successfully!")
        
    async def initialize_async(self):
        """Initialize async components"""
        logger.info("🔄 Starting async initialization...")
        
        # Initialize proxy manager
        await self.proxy_manager.initialize()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("✅ Async initialization complete")
        
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Metrics collection task
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self._background_tasks.append(metrics_task)
        
        # Session cleanup task
        cleanup_task = asyncio.create_task(self._session_cleanup_loop())
        self._background_tasks.append(cleanup_task)
        
        logger.info("🔄 Background tasks started")
        
    async def create_crawl_session(self, target_domain: str, policy_override: Optional[Dict[str, Any]] = None) -> str:
        """Create a new crawling session"""
        self.session_counter += 1
        session_id = f"session_{self.session_counter}_{int(time.time())}"
        
        # Get domain policy
        policy = self.config.get_domain_policy(target_domain)
        if policy_override:
            policy = policy.with_overrides(policy_override)
            
        # Create session
        session = CrawlSession(
            session_id=session_id,
            start_time=time.time(),
            target_domain=target_domain,
            policy=policy
        )
        
        self.active_sessions[session_id] = session
        
        logger.info(f"📋 Created crawl session {session_id} for domain {target_domain}")
        return session_id
        
    async def unified_crawl(self, url: str, session_id: Optional[str] = None, **kwargs) -> UnifiedCrawlResult:
        """
        Perform unified crawling with all integrated capabilities.
        
        This is the main entry point that orchestrates:
        1. URL discovery and expansion
        2. Intelligence gathering (OSINT)
        3. Anti-bot defense strategy selection
        4. Proxy selection and rotation
        5. Content extraction and quality assessment
        6. Result aggregation and analysis
        """
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        # Parse target URL
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Create result object
        result = UnifiedCrawlResult(url=url)
        
        try:
            # Get or create session
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
            else:
                session_id = await self.create_crawl_session(domain)
                session = self.active_sessions[session_id]
                
            policy = session.policy
            
            logger.info(f"🎯 Starting unified crawl for {url} with policy {policy.name}")
            
            # Phase 1: Intelligence Gathering (Optional)
            if policy.intelligence_gathering:
                await self._gather_intelligence(domain, result)
                
            # Phase 2: URL Discovery (if enabled)
            if policy.url_discovery_enabled:
                await self._discover_urls(url, policy, result)
                
            # Phase 3: Anti-bot Defense Strategy Selection
            defense_strategy = await self._select_defense_strategy(domain, result, policy)
            
            # Phase 4: Proxy Selection
            proxy = await self._select_proxy(domain, policy)
            if proxy:
                result.proxy_used = proxy
                
            # Phase 5: Content Retrieval with Defense
            content_success = await self._retrieve_content(url, defense_strategy, proxy, result, policy)
            
            # Phase 6: Content Extraction and Quality Assessment
            if content_success and result.content:
                await self._extract_and_assess_content(result, policy)
                
            # Phase 7: Result Finalization
            result.response_time = time.time() - start_time
            result.success = content_success
            
            # Update metrics
            if result.success:
                self.metrics['successful_requests'] += 1
                self.metrics['content_extracted'] += 1 if result.content else 0
            else:
                self.metrics['failed_requests'] += 1
                
            # Add to session
            session.results.append(result)
            
            logger.info(f"✅ Unified crawl completed for {url} in {result.response_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Unified crawl failed for {url}: {str(e)}")
            result.errors.append(f"Crawl failed: {str(e)}")
            result.response_time = time.time() - start_time
            self.metrics['failed_requests'] += 1
            
        return result
        
    async def _gather_intelligence(self, domain: str, result: UnifiedCrawlResult):
        """Gather intelligence about the target domain"""
        try:
            logger.info(f"🔍 Gathering intelligence for {domain}")
            
            # Perform comprehensive OSINT analysis
            intel_results = await self.osint_analytics.analyze_target(domain)
            
            # Extract domain intelligence
            if intel_results.get('domain_intel'):
                result.domain_intel = intel_results['domain_intel']
                
            # Extract IP intelligence
            result.ip_intel.update(intel_results.get('ip_intel', {}))
            
            # Log intelligence summary
            if result.domain_intel:
                risk_level = result.domain_intel.risk_level
                logger.info(f"📊 Domain intelligence: Risk level = {risk_level}")
                
            self.metrics['intelligence_gathered'] += 1
            
        except Exception as e:
            logger.warning(f"Intelligence gathering failed for {domain}: {str(e)}")
            result.warnings.append(f"Intelligence gathering failed: {str(e)}")
            
    async def _discover_urls(self, url: str, policy: DomainPolicy, result: UnifiedCrawlResult):
        """Discover additional URLs from the target"""
        try:
            if not policy.url_discovery_enabled:
                return
                
            logger.info(f"🔍 Discovering URLs from {url}")
            
            # Create crawl policy from domain policy
            crawl_policy = CrawlPolicy(
                max_depth=policy.url_discovery_depth,
                max_urls_per_domain=policy.max_urls_per_session,
                discovery_engines=policy.url_discovery_engines,
                extract_forms=policy.extract_forms,
                extract_api_endpoints=policy.extract_api_endpoints,
                infinite_scroll=policy.infinite_scroll_enabled
            )
            
            # Run URL discovery
            discovery_results = await self.url_discovery.discover_urls_comprehensive(url, crawl_policy)
            
            # Add discovered URLs to result
            result.discovered_urls.update(discovery_results.urls)
            result.discovery_metadata = discovery_results.metadata
            
            logger.info(f"📋 Discovered {len(discovery_results.urls)} URLs")
            self.metrics['urls_discovered'] += len(discovery_results.urls)
            
        except Exception as e:
            logger.warning(f"URL discovery failed for {url}: {str(e)}")
            result.warnings.append(f"URL discovery failed: {str(e)}")
            
    async def _select_defense_strategy(self, domain: str, result: UnifiedCrawlResult, policy: DomainPolicy) -> str:
        """Select appropriate anti-bot defense strategy"""
        try:
            # Base strategy on policy anti-bot level
            if policy.anti_bot_level == "maximum":
                strategy = "undetected_chrome"
            elif policy.anti_bot_level == "high":
                strategy = "cloudscraper"
            elif policy.anti_bot_level == "medium":
                strategy = "flaresolverr" if policy.cloudflare_bypass else "requests"
            else:
                strategy = "requests"
                
            # Adjust based on intelligence
            if result.domain_intel:
                threat_indicators = result.domain_intel.threat_indicators
                
                # Escalate if CloudFlare detected
                if any("cloudflare" in indicator.lower() for indicator in threat_indicators):
                    if strategy == "requests":
                        strategy = "cloudscraper"
                    elif strategy == "cloudscraper":
                        strategy = "flaresolverr"
                        
                # Use maximum defense for high-risk domains
                if result.domain_intel.risk_level in ["high", "critical"]:
                    strategy = "undetected_chrome"
                    
            logger.info(f"🛡️ Selected defense strategy: {strategy}")
            return strategy
            
        except Exception as e:
            logger.warning(f"Defense strategy selection failed: {str(e)}")
            return "requests"  # Fallback to basic strategy
            
    async def _select_proxy(self, domain: str, policy: DomainPolicy) -> Optional[ProxyInfo]:
        """Select appropriate proxy for the request"""
        try:
            if not policy.proxy_rotation:
                return None
                
            # Get proxy from advanced proxy manager
            proxy = await self.proxy_manager.get_proxy(domain)
            
            if isinstance(proxy, ProxyInfo):
                logger.info(f"🌐 Selected proxy: {proxy.host}:{proxy.port} (quality: {proxy.quality_score:.2f})")
                return proxy
            else:
                # AWS session returned
                logger.info("🌐 Using AWS Gateway rotation")
                return None
                
        except Exception as e:
            logger.warning(f"Proxy selection failed: {str(e)}")
            return None
            
    async def _retrieve_content(self, url: str, strategy: str, proxy: Optional[ProxyInfo], 
                              result: UnifiedCrawlResult, policy: DomainPolicy) -> bool:
        """Retrieve content using selected strategy and proxy"""
        try:
            logger.info(f"📥 Retrieving content from {url} using {strategy}")
            
            # Prepare defense options
            defense_options = {
                'strategy': strategy,
                'proxy': proxy,
                'captcha_solving': policy.captcha_solving,
                'tls_fingerprint': policy.tls_fingerprinting,
                'max_attempts': 3
            }
            
            # Use anti-bot system to retrieve content
            defense_result = await self.anti_bot.bypass_protection(url, defense_options)
            
            result.bot_defense = defense_result
            result.status_code = defense_result.status_code
            
            if defense_result.success and defense_result.html_content:
                # Create basic extraction result
                result.content = ExtractionResult(
                    url=url,
                    html=defense_result.html_content,
                    success=True
                )
                
                # Update metrics
                if defense_result.captcha_solved:
                    self.metrics['captchas_solved'] += 1
                    
                if proxy:
                    self.metrics['proxies_used'] += 1
                    
                return True
            else:
                result.errors.extend(defense_result.errors)
                return False
                
        except Exception as e:
            logger.error(f"Content retrieval failed for {url}: {str(e)}")
            result.errors.append(f"Content retrieval failed: {str(e)}")
            return False
            
    async def _extract_and_assess_content(self, result: UnifiedCrawlResult, policy: DomainPolicy):
        """Extract and assess content quality"""
        try:
            if not result.content or not result.content.html:
                return
                
            logger.info(f"📄 Extracting content from {result.url}")
            
            # Configure extraction options
            extraction_options = {
                'method': policy.content_extraction_method,
                'extract_tables': policy.extract_tables,
                'extract_images': policy.extract_images,
                'entity_recognition': policy.entity_recognition,
                'language_detection': True,
                'quality_assessment': True
            }
            
            # Extract content using content extraction system
            extraction_result = await self.content_extractor.extract_content(
                result.url, 
                result.content.html, 
                **extraction_options
            )
            
            # Update result with extracted content
            result.content = extraction_result
            
            # Assess quality
            if extraction_result.quality_score:
                quality_score = extraction_result.quality_score.overall_score
                logger.info(f"📊 Content quality score: {quality_score:.2f}")
                
                # Check if content meets quality threshold
                if quality_score < policy.quality_threshold:
                    result.warnings.append(f"Content quality below threshold: {quality_score:.2f} < {policy.quality_threshold}")
                    
        except Exception as e:
            logger.warning(f"Content extraction failed for {result.url}: {str(e)}")
            result.warnings.append(f"Content extraction failed: {str(e)}")
            
    async def batch_crawl(self, urls: List[str], session_id: Optional[str] = None, 
                         max_concurrent: int = 10, **kwargs) -> List[UnifiedCrawlResult]:
        """Perform batch crawling with concurrency control"""
        logger.info(f"🚀 Starting batch crawl of {len(urls)} URLs")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def crawl_with_semaphore(url: str) -> UnifiedCrawlResult:
            async with semaphore:
                return await self.unified_crawl(url, session_id, **kwargs)
                
        # Execute all crawls concurrently
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = UnifiedCrawlResult(url=urls[i])
                error_result.errors.append(f"Crawl exception: {str(result)}")
                valid_results.append(error_result)
            else:
                valid_results.append(result)
                
        success_count = sum(1 for r in valid_results if r.success)
        logger.info(f"✅ Batch crawl complete: {success_count}/{len(urls)} successful")
        
        return valid_results
        
    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a crawling session"""
        if session_id not in self.active_sessions:
            return None
            
        session = self.active_sessions[session_id]
        results = session.results
        
        if not results:
            return {
                'session_id': session_id,
                'start_time': session.start_time,
                'domain': session.target_domain,
                'total_crawls': 0,
                'successful_crawls': 0,
                'avg_response_time': 0.0,
                'urls_discovered': 0,
                'intelligence_gathered': False
            }
            
        successful = [r for r in results if r.success]
        response_times = [r.response_time for r in results if r.response_time > 0]
        
        return {
            'session_id': session_id,
            'start_time': session.start_time,
            'domain': session.target_domain,
            'total_crawls': len(results),
            'successful_crawls': len(successful),
            'success_rate': len(successful) / len(results),
            'avg_response_time': sum(response_times) / len(response_times) if response_times else 0.0,
            'urls_discovered': sum(len(r.discovered_urls) for r in results),
            'intelligence_gathered': any(r.domain_intel for r in results),
            'proxies_used': len(set(r.proxy_used.host for r in results if r.proxy_used)),
            'captchas_solved': sum(1 for r in results if r.bot_defense and r.bot_defense.captcha_solved),
            'quality_scores': [r.content.quality_score.overall_score 
                             for r in successful 
                             if r.content and r.content.quality_score]
        }
        
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        return {
            'uptime': time.time() - getattr(self, '_start_time', time.time()),
            'active_sessions': len(self.active_sessions),
            'total_requests': self.metrics['total_requests'],
            'successful_requests': self.metrics['successful_requests'],
            'failed_requests': self.metrics['failed_requests'],
            'success_rate': (self.metrics['successful_requests'] / max(1, self.metrics['total_requests'])),
            'avg_response_time': self.metrics['avg_response_time'],
            'urls_discovered': self.metrics['urls_discovered'],
            'content_extracted': self.metrics['content_extracted'],
            'intelligence_gathered': self.metrics['intelligence_gathered'],
            'proxies_used': self.metrics['proxies_used'],
            'captchas_solved': self.metrics['captchas_solved'],
            'proxy_pool_size': len(self.proxy_manager.pool.proxies) if hasattr(self.proxy_manager, 'pool') else 0,
            'working_proxies': len(self.proxy_manager.pool.get_working_proxies()) if hasattr(self.proxy_manager, 'pool') else 0
        }
        
    async def _metrics_collection_loop(self):
        """Background task for metrics collection"""
        while True:
            try:
                await asyncio.sleep(60)  # Update every minute
                
                # Update average response time
                if self.metrics['successful_requests'] > 0:
                    total_time = sum(
                        sum(r.response_time for r in session.results if r.success)
                        for session in self.active_sessions.values()
                    )
                    self.metrics['avg_response_time'] = total_time / self.metrics['successful_requests']
                    
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                
    async def _session_cleanup_loop(self):
        """Background task for cleaning up old sessions"""
        while True:
            try:
                await asyncio.sleep(3600)  # Check every hour
                
                current_time = time.time()
                max_age = 24 * 3600  # 24 hours
                
                # Find old sessions
                old_sessions = [
                    session_id for session_id, session in self.active_sessions.items()
                    if current_time - session.start_time > max_age
                ]
                
                # Remove old sessions
                for session_id in old_sessions:
                    del self.active_sessions[session_id]
                    logger.info(f"🧹 Cleaned up old session: {session_id}")
                    
            except Exception as e:
                logger.error(f"Session cleanup error: {str(e)}")
                
    # GitHub Integration Methods
    async def load_github_integration(self, integration_name: str, config: Dict[str, Any] = None) -> bool:
        """Load a GitHub integration adapter"""
        if not self.github_registry_enabled:
            logger.warning("GitHub registry not available")
            return False
            
        try:
            adapter = await load_integration(integration_name, config or {})
            if adapter:
                self.github_integrations[integration_name] = adapter
                logger.info(f"✅ Loaded GitHub integration: {integration_name}")
                return True
            else:
                logger.error(f"❌ Failed to load GitHub integration: {integration_name}")
                return False
        except Exception as e:
            logger.error(f"❌ Error loading GitHub integration {integration_name}: {str(e)}")
            return False
            
    async def execute_github_operation(self, integration_name: str, operation: str, *args, **kwargs) -> Dict[str, Any]:
        """Execute operation on GitHub integration"""
        if not self.github_registry_enabled:
            return {'success': False, 'error': 'GitHub registry not available'}
            
        try:
            result = await execute_integration_operation(integration_name, operation, *args, **kwargs)
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def get_github_recommendations(self, use_case: str) -> List[Dict[str, Any]]:
        """Get GitHub integration recommendations for use case"""
        if not self.github_registry_enabled:
            return []
            
        try:
            recommendations = get_integration_recommendations(use_case)
            return [
                {
                    'name': rec.name,
                    'display_name': rec.display_name,
                    'category': rec.category.value,
                    'description': rec.description,
                    'features': rec.primary_features,
                    'maturity': rec.maturity_level,
                    'performance': rec.performance_tier
                }
                for rec in recommendations
            ]
        except Exception as e:
            logger.error(f"❌ Error getting recommendations: {str(e)}")
            return []
            
    async def enhanced_content_extraction(self, url: str, html: str, integration_name: str = None) -> Dict[str, Any]:
        """Enhanced content extraction using GitHub integrations"""
        if not integration_name:
            # Auto-select based on content type and URL
            if url.endswith('.pdf'):
                integration_name = 'pdf_extract_kit'
            else:
                integration_name = 'apache_tika'  # Default to Tika for general content
                
        try:
            # Load integration if not already loaded
            if integration_name not in self.github_integrations:
                success = await self.load_github_integration(integration_name)
                if not success:
                    return {'success': False, 'error': f'Failed to load {integration_name}'}
                    
            # Execute extraction
            result = await self.execute_github_operation(
                integration_name, 
                'extract_content',
                content=html,
                url=url
            )
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    async def enhanced_url_discovery(self, start_url: str, integration_name: str = 'katana') -> Dict[str, Any]:
        """Enhanced URL discovery using GitHub integrations"""
        try:
            # Load integration if not already loaded
            if integration_name not in self.github_integrations:
                success = await self.load_github_integration(integration_name)
                if not success:
                    return {'success': False, 'error': f'Failed to load {integration_name}'}
                    
            # Execute URL discovery
            result = await self.execute_github_operation(
                integration_name, 
                'discover_urls',
                start_url=start_url,
                max_depth=3,
                max_urls=100
            )
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
                
    async def cleanup(self):
        """Cleanup system resources"""
        logger.info("🧹 Cleaning up Revolutionary Ultimate System v4.0")
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        # Cleanup GitHub integrations
        if self.github_registry_enabled:
            try:
                await github_registry.cleanup()
                logger.info("✅ GitHub integrations cleaned up")
            except Exception as e:
                logger.error(f"❌ GitHub registry cleanup failed: {str(e)}")
        
        # Clear integration cache
        self.github_integrations.clear()
                
        # Cleanup subsystems
        await self.proxy_manager.cleanup()
        
        # Clear sessions
        self.active_sessions.clear()
        
        logger.info("✅ Cleanup complete")
        
    def __repr__(self):
        return f"UnifiedRevolutionarySystem(sessions={len(self.active_sessions)}, requests={self.metrics['total_requests']})"

# Example usage and demonstration
async def main():
    """Example usage of the Unified Revolutionary System"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Revolutionary Ultimate System v4.0 - Unified Integration")
    parser.add_argument("urls", nargs="+", help="URLs to crawl")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--concurrent", type=int, default=5, help="Maximum concurrent crawls")
    parser.add_argument("--intelligence", action="store_true", help="Enable intelligence gathering")
    parser.add_argument("--discovery", action="store_true", help="Enable URL discovery")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create unified system
    system = UnifiedRevolutionarySystem(args.config)
    
    try:
        # Initialize system
        await system.initialize_async()
        
        print(f"\n🚀 Revolutionary Ultimate System v4.0 Ready!")
        print(f"📊 System capabilities:")
        print(f"   • Anti-bot defense with CloudFlare bypass")
        print(f"   • Advanced content extraction and quality assessment")
        print(f"   • Multi-engine URL discovery and deep crawling")
        print(f"   • Enterprise proxy management with AWS rotation")
        print(f"   • OSINT threat intelligence and security analysis")
        print(f"   • Per-domain policy configuration")
        
        # Create policy overrides
        policy_override = {}
        if args.intelligence:
            policy_override['intelligence_gathering'] = True
        if args.discovery:
            policy_override['url_discovery_enabled'] = True
            
        # Perform batch crawl
        print(f"\n🎯 Starting crawl of {len(args.urls)} URLs...")
        results = await system.batch_crawl(
            args.urls, 
            max_concurrent=args.concurrent,
            policy_override=policy_override if policy_override else None
        )
        
        # Display results
        successful = [r for r in results if r.success]
        print(f"\n✅ Crawl complete: {len(successful)}/{len(results)} successful")
        
        for i, result in enumerate(results, 1):
            status = "✅" if result.success else "❌"
            print(f"   {i}. {status} {result.url}")
            
            if result.success and result.content:
                text_length = len(result.content.text) if result.content.text else 0
                print(f"      📄 Content: {text_length} chars")
                
                if result.content.quality_score:
                    score = result.content.quality_score.overall_score
                    print(f"      📊 Quality: {score:.2f}")
                    
            if result.discovered_urls:
                print(f"      🔍 Discovered: {len(result.discovered_urls)} URLs")
                
            if result.domain_intel:
                risk = result.domain_intel.risk_level
                print(f"      🛡️ Risk Level: {risk}")
                
            if result.errors:
                for error in result.errors[:3]:  # Show first 3 errors
                    print(f"      ❌ {error}")
                    
        # Show system metrics
        metrics = system.get_system_metrics()
        print(f"\n📊 System Metrics:")
        print(f"   Success Rate: {metrics['success_rate']:.1%}")
        print(f"   Avg Response Time: {metrics['avg_response_time']:.2f}s")
        print(f"   URLs Discovered: {metrics['urls_discovered']}")
        print(f"   Content Extracted: {metrics['content_extracted']}")
        print(f"   Intelligence Gathered: {metrics['intelligence_gathered']}")
        print(f"   Proxies Used: {metrics['proxies_used']}")
        print(f"   CAPTCHAs Solved: {metrics['captchas_solved']}")
        
        # Save results if requested
        if args.output:
            output_data = []
            for result in results:
                result_dict = {
                    'url': result.url,
                    'success': result.success,
                    'status_code': result.status_code,
                    'response_time': result.response_time,
                    'content_length': len(result.content.text) if result.content and result.content.text else 0,
                    'quality_score': result.content.quality_score.overall_score if result.content and result.content.quality_score else None,
                    'discovered_urls': len(result.discovered_urls),
                    'risk_level': result.domain_intel.risk_level if result.domain_intel else None,
                    'proxy_used': f"{result.proxy_used.host}:{result.proxy_used.port}" if result.proxy_used else None,
                    'errors': result.errors
                }
                output_data.append(result_dict)
                
            with open(args.output, 'w') as f:
                json.dump({
                    'results': output_data,
                    'metrics': metrics,
                    'timestamp': time.time()
                }, f, indent=2)
                
            print(f"\n💾 Results saved to: {args.output}")
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ System error: {str(e)}")
        logger.exception("System failed")
    finally:
        await system.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
