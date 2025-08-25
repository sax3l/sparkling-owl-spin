#!/usr/bin/env python3
"""
NER Service Adapter för Sparkling-Owl-Spin
Named Entity Recognition med stöd för spaCy, NLTK, och Hugging Face
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re

logger = logging.getLogger(__name__)

class EntityType(Enum):
    """Entity types för NER"""
    PERSON = "PERSON"
    ORGANIZATION = "ORG"
    LOCATION = "GPE"
    DATE = "DATE"
    TIME = "TIME"
    MONEY = "MONEY"
    PERCENT = "PERCENT"
    EMAIL = "EMAIL"
    URL = "URL"
    IP_ADDRESS = "IP"
    PHONE = "PHONE"
    PRODUCT = "PRODUCT"
    EVENT = "EVENT"
    LANGUAGE = "LANGUAGE"

@dataclass
class Entity:
    """Extracted entity"""
    text: str
    label: EntityType
    start: int
    end: int
    confidence: float = 1.0
    context: str = ""
    
@dataclass
class NERResult:
    """NER analysis result"""
    text: str
    entities: List[Entity]
    processing_time: float
    model_used: str
    language: str = "en"

class NERServiceAdapter:
    """NER Service integration för entity extraction"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.models = {}
        self.initialized = False
        self.available_models = ["spacy_sm", "spacy_lg", "nltk", "huggingface", "regex"]
        self.regex_patterns = {}
        
    async def initialize(self):
        """Initiera NER Service"""
        try:
            logger.info("🧠 Initializing NER Service Adapter")
            
            # Try to initialize different NER models
            await self._initialize_models()
            await self._setup_regex_patterns()
            
            self.initialized = True
            logger.info("✅ NER Service Adapter initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize NER Service: {str(e)}")
            raise
            
    async def _initialize_models(self):
        """Initialize NER models"""
        
        # Try spaCy
        try:
            # import spacy  # Uncomment when available
            logger.info("📚 spaCy model initialization (mock)")
            self.models["spacy_sm"] = {"model": "mock_spacy_sm", "languages": ["en", "sv"]}
            self.models["spacy_lg"] = {"model": "mock_spacy_lg", "languages": ["en", "sv"]}
        except ImportError:
            logger.warning("⚠️ spaCy not available")
            
        # Try NLTK
        try:
            # import nltk  # Uncomment when available
            logger.info("📚 NLTK model initialization (mock)")
            self.models["nltk"] = {"model": "mock_nltk", "languages": ["en"]}
        except ImportError:
            logger.warning("⚠️ NLTK not available")
            
        # Try Hugging Face Transformers
        try:
            # from transformers import AutoTokenizer, AutoModelForTokenClassification  # Uncomment when available
            logger.info("🤗 Hugging Face model initialization (mock)")
            self.models["huggingface"] = {
                "model": "mock_bert_ner",
                "tokenizer": "mock_tokenizer",
                "languages": ["en", "sv", "de", "fr"]
            }
        except ImportError:
            logger.warning("⚠️ Hugging Face Transformers not available")
            
        # Regex patterns always available
        self.models["regex"] = {"model": "regex_patterns", "languages": ["all"]}
        
        logger.info(f"📊 Initialized {len(self.models)} NER models")
        
    async def _setup_regex_patterns(self):
        """Setup regex patterns för entity extraction"""
        
        # Email patterns
        self.regex_patterns[EntityType.EMAIL] = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        ]
        
        # URL patterns
        self.regex_patterns[EntityType.URL] = [
            r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            r'www\.(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?'
        ]
        
        # IP Address patterns
        self.regex_patterns[EntityType.IP_ADDRESS] = [
            r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
        ]
        
        # Phone patterns
        self.regex_patterns[EntityType.PHONE] = [
            r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            r'\+46[-.\s]?\d{1,3}[-.\s]?\d{6,7}'  # Swedish phone
        ]
        
        # Money patterns
        self.regex_patterns[EntityType.MONEY] = [
            r'\$\d+(?:,\d{3})*(?:\.\d{2})?',
            r'\d+(?:,\d{3})*(?:\.\d{2})?\s?(?:USD|EUR|SEK|GBP)',
            r'\d+\s?(?:kronor|dollar|euro)'
        ]
        
        # Date patterns
        self.regex_patterns[EntityType.DATE] = [
            r'\d{4}-\d{2}-\d{2}',
            r'\d{2}/\d{2}/\d{4}',
            r'\d{1,2}\s(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s\d{4}',
            r'(?:januari|februari|mars|april|maj|juni|juli|augusti|september|oktober|november|december)\s\d{1,2},?\s\d{4}'
        ]
        
        logger.info(f"🔍 Setup regex patterns för {len(self.regex_patterns)} entity types")
        
    async def extract_entities(self, text: str, model_name: str = "regex", language: str = "en") -> NERResult:
        """Extract entities från text"""
        import time
        start_time = time.time()
        
        if not self.initialized:
            await self.initialize()
            
        if model_name not in self.models:
            model_name = "regex"  # Fallback
            
        logger.info(f"🔍 Extracting entities using {model_name} model")
        
        if model_name == "regex":
            entities = await self._extract_with_regex(text)
        elif model_name.startswith("spacy"):
            entities = await self._extract_with_spacy(text, model_name, language)
        elif model_name == "nltk":
            entities = await self._extract_with_nltk(text)
        elif model_name == "huggingface":
            entities = await self._extract_with_huggingface(text, language)
        else:
            entities = []
            
        processing_time = time.time() - start_time
        
        return NERResult(
            text=text,
            entities=entities,
            processing_time=processing_time,
            model_used=model_name,
            language=language
        )
        
    async def _extract_with_regex(self, text: str) -> List[Entity]:
        """Extract entities med regex patterns"""
        entities = []
        
        for entity_type, patterns in self.regex_patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    entity = Entity(
                        text=match.group(),
                        label=entity_type,
                        start=match.start(),
                        end=match.end(),
                        confidence=0.8,  # Regex has good precision but lower recall
                        context=text[max(0, match.start()-20):min(len(text), match.end()+20)]
                    )
                    entities.append(entity)
                    
        return entities
        
    async def _extract_with_spacy(self, text: str, model_name: str, language: str) -> List[Entity]:
        """Extract entities med spaCy (mock implementation)"""
        await asyncio.sleep(0.1)  # Simulate processing
        
        # Mock spaCy extraction
        entities = []
        
        # Mock some common entities
        if "John Doe" in text:
            entities.append(Entity("John Doe", EntityType.PERSON, text.find("John Doe"), text.find("John Doe")+8, 0.95))
        if "Stockholm" in text:
            entities.append(Entity("Stockholm", EntityType.LOCATION, text.find("Stockholm"), text.find("Stockholm")+9, 0.92))
        if "Google" in text:
            entities.append(Entity("Google", EntityType.ORGANIZATION, text.find("Google"), text.find("Google")+6, 0.88))
            
        # Add regex entities as backup
        regex_entities = await self._extract_with_regex(text)
        entities.extend(regex_entities)
        
        return entities
        
    async def _extract_with_nltk(self, text: str) -> List[Entity]:
        """Extract entities med NLTK (mock implementation)"""
        await asyncio.sleep(0.15)  # Simulate processing
        
        entities = []
        
        # Mock NLTK named entities
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                start_pos = text.find(word)
                if start_pos != -1:
                    entity = Entity(
                        text=word,
                        label=EntityType.PERSON,  # NLTK often classifies proper nouns as PERSON
                        start=start_pos,
                        end=start_pos + len(word),
                        confidence=0.7
                    )
                    entities.append(entity)
                    
        return entities
        
    async def _extract_with_huggingface(self, text: str, language: str) -> List[Entity]:
        """Extract entities med Hugging Face (mock implementation)"""
        await asyncio.sleep(0.3)  # Simulate more complex processing
        
        entities = []
        
        # Mock transformer-based NER
        mock_entities = [
            ("Microsoft", EntityType.ORGANIZATION, 0.94),
            ("Python", EntityType.PRODUCT, 0.89),
            ("OpenAI", EntityType.ORGANIZATION, 0.96),
            ("Stockholm", EntityType.LOCATION, 0.93)
        ]
        
        for entity_text, entity_type, confidence in mock_entities:
            if entity_text.lower() in text.lower():
                start_pos = text.lower().find(entity_text.lower())
                end_pos = start_pos + len(entity_text)
                
                entity = Entity(
                    text=text[start_pos:end_pos],  # Preserve original casing
                    label=entity_type,
                    start=start_pos,
                    end=end_pos,
                    confidence=confidence,
                    context=text[max(0, start_pos-30):min(len(text), end_pos+30)]
                )
                entities.append(entity)
                
        return entities
        
    async def batch_extract(self, texts: List[str], model_name: str = "regex", language: str = "en") -> List[NERResult]:
        """Batch entity extraction"""
        results = []
        for text in texts:
            result = await self.extract_entities(text, model_name, language)
            results.append(result)
        return results
        
    def get_supported_models(self) -> List[Dict[str, Any]]:
        """Hämta supported models"""
        return [
            {
                "name": model_name,
                "available": model_name in self.models,
                "languages": self.models[model_name].get("languages", []) if model_name in self.models else [],
                "type": self._get_model_type(model_name)
            }
            for model_name in self.available_models
        ]
        
    def _get_model_type(self, model_name: str) -> str:
        """Get model type"""
        if model_name.startswith("spacy"):
            return "statistical"
        elif model_name == "nltk":
            return "rule_based"
        elif model_name == "huggingface":
            return "transformer"
        elif model_name == "regex":
            return "pattern_based"
        else:
            return "unknown"
            
    def get_entity_statistics(self, result: NERResult) -> Dict[str, Any]:
        """Get entity statistics från result"""
        entity_counts = {}
        confidence_scores = []
        
        for entity in result.entities:
            entity_type = entity.label.value
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            confidence_scores.append(entity.confidence)
            
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "total_entities": len(result.entities),
            "entity_types": len(entity_counts),
            "entity_distribution": entity_counts,
            "average_confidence": round(avg_confidence, 3),
            "processing_time": round(result.processing_time, 3),
            "model_used": result.model_used,
            "text_length": len(result.text)
        }
        
    async def cleanup(self):
        """Cleanup NER Service"""
        logger.info("🧹 Cleaning up NER Service Adapter")
        self.models.clear()
        self.regex_patterns.clear()
        self.initialized = False
        logger.info("✅ NER Service cleanup completed")
