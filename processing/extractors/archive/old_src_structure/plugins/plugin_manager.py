#!/usr/bin/env python3
"""
Sparkling-Owl-Spin Plugin Manager
Hanterar alla plugins enligt registry.yaml
"""

import os
import yaml
import logging
import asyncio
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

class PluginStatus(Enum):
    DISABLED = "disabled"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"

@dataclass
class PluginInfo:
    name: str
    enabled: bool
    category: str
    description: str
    github: str
    security_level: SecurityLevel
    location: str
    dependencies: List[str]
    status: PluginStatus = PluginStatus.DISABLED
    instance: Optional[Any] = None
    error: Optional[str] = None

class PluginManager:
    """Central plugin manager för Sparkling-Owl-Spin"""
    
    def __init__(self, config_path: str = None, environment: str = "development"):
        self.config_path = config_path or "src/plugins/registry.yaml"
        self.environment = environment
        self.plugins: Dict[str, PluginInfo] = {}
        self.loaded_plugins: Dict[str, Any] = {}
        self.registry_config = None
        
    async def initialize(self):
        """Ladda plugin registry och initiera alla aktiverade plugins"""
        logger.info("🔌 Initializing Plugin Manager")
        
        try:
            await self._load_registry()
            await self._validate_environment()
            await self._load_enabled_plugins()
            logger.info(f"✅ Plugin Manager initialized with {len(self.loaded_plugins)} active plugins")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Plugin Manager: {str(e)}")
            raise
            
    async def _load_registry(self):
        """Ladda plugin registry från YAML"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.registry_config = yaml.safe_load(f)
                
            # Parse plugins
            for name, config in self.registry_config.get('plugins', {}).items():
                plugin_info = PluginInfo(
                    name=name,
                    enabled=config.get('enabled', False),
                    category=config.get('category', 'unknown'),
                    description=config.get('description', ''),
                    github=config.get('github', ''),
                    security_level=SecurityLevel(config.get('security_level', 'red')),
                    location=config.get('location', ''),
                    dependencies=config.get('dependencies', [])
                )
                self.plugins[name] = plugin_info
                
            logger.info(f"📋 Loaded {len(self.plugins)} plugin definitions")
            
        except Exception as e:
            logger.error(f"Failed to load plugin registry: {str(e)}")
            raise
            
    async def _validate_environment(self):
        """Validera att plugins får köras i aktuell miljö"""
        env_config = self.registry_config.get('environments', {}).get(self.environment, {})
        
        for plugin_info in self.plugins.values():
            if not plugin_info.enabled:
                continue
                
            # Check security level permissions
            if plugin_info.security_level == SecurityLevel.RED:
                if not env_config.get('enable_red', False):
                    plugin_info.enabled = False
                    logger.warning(f"🚫 Plugin {plugin_info.name} disabled - RED security level not allowed in {self.environment}")
                    
            elif plugin_info.security_level == SecurityLevel.YELLOW:
                if not env_config.get('enable_yellow_with_review', False):
                    plugin_info.enabled = False
                    logger.warning(f"⚠️ Plugin {plugin_info.name} disabled - YELLOW security level requires review in {self.environment}")
                    
    async def _load_enabled_plugins(self):
        """Ladda alla aktiverade plugins"""
        for name, plugin_info in self.plugins.items():
            if not plugin_info.enabled:
                continue
                
            try:
                plugin_info.status = PluginStatus.LOADING
                logger.info(f"🔧 Loading plugin: {name} ({plugin_info.category})")
                
                # Check dependencies
                await self._check_dependencies(plugin_info)
                
                # Load plugin based on category
                plugin_instance = await self._load_plugin_by_category(plugin_info)
                
                if plugin_instance:
                    self.loaded_plugins[name] = plugin_instance
                    plugin_info.instance = plugin_instance
                    plugin_info.status = PluginStatus.READY
                    logger.info(f"✅ Plugin {name} loaded successfully")
                else:
                    plugin_info.status = PluginStatus.ERROR
                    plugin_info.error = "Failed to create plugin instance"
                    
            except Exception as e:
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error = str(e)
                logger.error(f"❌ Failed to load plugin {name}: {str(e)}")
                
    async def _check_dependencies(self, plugin_info: PluginInfo):
        """Kontrollera att alla beroenden finns"""
        for dep in plugin_info.dependencies:
            try:
                importlib.import_module(dep)
            except ImportError:
                logger.warning(f"⚠️ Missing dependency {dep} for plugin {plugin_info.name}")
                
    async def _load_plugin_by_category(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda plugin baserat på kategori"""
        try:
            if plugin_info.category == "orchestration":
                return await self._load_orchestration_plugin(plugin_info)
            elif plugin_info.category == "nlp":
                return await self._load_nlp_plugin(plugin_info)
            elif plugin_info.category == "engines":
                return await self._load_engine_plugin(plugin_info)
            elif plugin_info.category == "document":
                return await self._load_document_plugin(plugin_info)
            elif plugin_info.category == "network":
                return await self._load_network_plugin(plugin_info)
            elif plugin_info.category == "security":
                return await self._load_security_plugin(plugin_info)
            elif plugin_info.category == "data":
                return await self._load_data_plugin(plugin_info)
            elif plugin_info.category == "analysis":
                return await self._load_analysis_plugin(plugin_info)
            else:
                logger.warning(f"Unknown plugin category: {plugin_info.category}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to load {plugin_info.category} plugin {plugin_info.name}: {str(e)}")
            return None
            
    async def _load_orchestration_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda orkestrering plugins (FastAgency, CrewAI etc)"""
        if plugin_info.name == "agent_fastagency":
            from src.plugins.agent_fastagency.adapter import FastAgencyAdapter
            return FastAgencyAdapter(plugin_info)
        elif plugin_info.name == "crewai_integration":
            from src.plugins.agent_multi.crewai_adapter import CrewAIAdapter
            return CrewAIAdapter(plugin_info)
        return None
        
    async def _load_nlp_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda NLP plugins"""
        if plugin_info.name == "ner_service":
            from src.analysis.ner_service import NERService
            return NERService(plugin_info)
        elif plugin_info.name == "relation_extraction":
            from src.analysis.re_service import RelationExtractionService
            return RelationExtractionService(plugin_info)
        elif plugin_info.name == "microsoft_recognizers":
            from src.scraper.normalizers import MicrosoftNormalizers
            return MicrosoftNormalizers(plugin_info)
        return None
        
    async def _load_engine_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda crawling engine plugins"""
        if plugin_info.name == "scrapy_adapter":
            from src.plugins.engines.scrapy_adapter import ScrapyAdapter
            return ScrapyAdapter(plugin_info)
        elif plugin_info.name == "crawlee_adapter":
            from src.plugins.engines.crawlee_adapter import CrawleeAdapter
            return CrawleeAdapter(plugin_info)
        elif plugin_info.name == "katana_integration":
            from src.plugins.engines.katana_adapter import KatanaAdapter
            return KatanaAdapter(plugin_info)
        return None
        
    async def _load_document_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda document processing plugins"""
        if plugin_info.name == "tika_adapter":
            from src.plugins.document_ingest.tika_adapter import TikaAdapter
            return TikaAdapter(plugin_info)
        elif plugin_info.name == "trafilatura_adapter":
            from src.plugins.document_ingest.trafilatura_adapter import TrafilaturaAdapter
            return TrafilaturaAdapter(plugin_info)
        elif plugin_info.name == "pdf_extract_kit":
            from src.plugins.document_ingest.pdf_extract_kit import PDFExtractKit
            return PDFExtractKit(plugin_info)
        return None
        
    async def _load_network_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda network plugins"""
        if plugin_info.name == "rate_limiter":
            from src.webapp.middlewares.rate_limit import RateLimitMiddleware
            return RateLimitMiddleware(plugin_info)
        elif plugin_info.name == "proxy_pool_jhao":
            from src.proxy_pool.manager import ProxyPoolManager
            return ProxyPoolManager(plugin_info)
        return None
        
    async def _load_security_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda security plugins"""
        if plugin_info.name == "payloads_all_things":
            from src.security.payloads.manager import PayloadsManager
            return PayloadsManager(plugin_info)
        return None
        
    async def _load_data_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda data plugins"""
        if plugin_info.name == "swedish_vehicle_data":
            from database.seed.swedish_data.loader import SwedishDataLoader
            return SwedishDataLoader(plugin_info)
        return None
        
    async def _load_analysis_plugin(self, plugin_info: PluginInfo) -> Optional[Any]:
        """Ladda analysis plugins"""
        if plugin_info.name == "rapidfuzz_similarity":
            from src.analysis.similarity_analysis import SimilarityAnalyzer
            return SimilarityAnalyzer(plugin_info)
        return None
        
    def get_plugin(self, name: str) -> Optional[Any]:
        """Hämta plugin instance"""
        return self.loaded_plugins.get(name)
        
    def get_plugins_by_category(self, category: str) -> List[Any]:
        """Hämta alla plugins i kategori"""
        return [
            instance for name, instance in self.loaded_plugins.items()
            if self.plugins[name].category == category
        ]
        
    def get_status(self) -> Dict[str, Any]:
        """Hämta plugin status"""
        return {
            "total_plugins": len(self.plugins),
            "enabled_plugins": len([p for p in self.plugins.values() if p.enabled]),
            "loaded_plugins": len(self.loaded_plugins),
            "failed_plugins": len([p for p in self.plugins.values() if p.status == PluginStatus.ERROR]),
            "plugins": {
                name: {
                    "status": info.status.value,
                    "category": info.category,
                    "security_level": info.security_level.value,
                    "error": info.error
                }
                for name, info in self.plugins.items()
            }
        }
        
    async def cleanup(self):
        """Stäng ned alla plugins"""
        logger.info("🧹 Shutting down plugins")
        
        for name, instance in self.loaded_plugins.items():
            try:
                if hasattr(instance, 'cleanup'):
                    await instance.cleanup()
                logger.info(f"✅ Plugin {name} cleaned up")
            except Exception as e:
                logger.error(f"❌ Error cleaning up plugin {name}: {str(e)}")
                
        self.loaded_plugins.clear()
        logger.info("✅ Plugin Manager cleanup completed")
