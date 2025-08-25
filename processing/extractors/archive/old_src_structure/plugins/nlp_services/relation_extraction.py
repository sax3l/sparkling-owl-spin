#!/usr/bin/env python3
"""
Relation Extraction Service för Sparkling-Owl-Spin
Extraktion av relationer mellan entities i text
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from itertools import combinations

logger = logging.getLogger(__name__)

class RelationType(Enum):
    """Relation types"""
    WORKS_FOR = "works_for"
    LOCATED_IN = "located_in"
    OWNS = "owns"
    PART_OF = "part_of"
    MARRIED_TO = "married_to"
    FOUNDED_BY = "founded_by"
    ACQUIRED_BY = "acquired_by"
    SUBSIDIARY_OF = "subsidiary_of"
    CEO_OF = "ceo_of"
    BORN_IN = "born_in"
    STUDIED_AT = "studied_at"
    COMPETITOR_OF = "competitor_of"
    PARTNER_WITH = "partner_with"
    CONNECTED_TO = "connected_to"
    
@dataclass
class Entity:
    """Entity för relation extraction"""
    text: str
    type: str
    start: int
    end: int
    
@dataclass 
class Relation:
    """Extracted relation"""
    source: Entity
    target: Entity
    relation_type: RelationType
    confidence: float
    evidence_text: str
    pattern_used: str = ""
    
@dataclass
class RelationExtractionResult:
    """Relation extraction result"""
    text: str
    entities: List[Entity]
    relations: List[Relation]
    processing_time: float
    method_used: str

class RelationExtractionAdapter:
    """Relation Extraction Service integration"""
    
    def __init__(self, plugin_info):
        self.plugin_info = plugin_info
        self.initialized = False
        self.relation_patterns = {}
        self.dependency_parsers = {}
        
    async def initialize(self):
        """Initiera Relation Extraction Service"""
        try:
            logger.info("🔗 Initializing Relation Extraction Service")
            
            await self._setup_relation_patterns()
            await self._initialize_parsers()
            
            self.initialized = True
            logger.info("✅ Relation Extraction Service initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Relation Extraction Service: {str(e)}")
            raise
            
    async def _setup_relation_patterns(self):
        """Setup patterns för relation extraction"""
        
        # Work relations
        self.relation_patterns[RelationType.WORKS_FOR] = [
            r'{entity1}.*(?:works for|employed by|works at|employee of).*{entity2}',
            r'{entity1}.*(?:is a|serves as).*(?:at|for).*{entity2}',
            r'{entity2}.*(?:employee|staff|worker|engineer|developer).*{entity1}'
        ]
        
        # Location relations
        self.relation_patterns[RelationType.LOCATED_IN] = [
            r'{entity1}.*(?:located in|based in|situated in|found in).*{entity2}',
            r'{entity1}.*(?:is in|resides in|operates in).*{entity2}',
            r'{entity2}.*(?:headquarters|office|branch).*{entity1}'
        ]
        
        # Ownership relations
        self.relation_patterns[RelationType.OWNS] = [
            r'{entity1}.*(?:owns|possesses|has|controls).*{entity2}',
            r'{entity2}.*(?:owned by|belongs to|property of).*{entity1}',
            r'{entity1}.*(?:owner of|proprietor of).*{entity2}'
        ]
        
        # Part-of relations
        self.relation_patterns[RelationType.PART_OF] = [
            r'{entity1}.*(?:part of|division of|subsidiary of|unit of).*{entity2}',
            r'{entity2}.*(?:includes|contains|comprises).*{entity1}',
            r'{entity1}.*(?:belongs to|member of).*{entity2}'
        ]
        
        # Leadership relations
        self.relation_patterns[RelationType.CEO_OF] = [
            r'{entity1}.*(?:CEO of|Chief Executive Officer of|leads|heads).*{entity2}',
            r'{entity2}.*(?:CEO|Chief Executive|leader).*{entity1}',
            r'{entity1}.*(?:founded|established|created).*{entity2}'
        ]
        
        # Personal relations
        self.relation_patterns[RelationType.MARRIED_TO] = [
            r'{entity1}.*(?:married to|spouse of|husband of|wife of).*{entity2}',
            r'{entity1}.*(?:and|&).*{entity2}.*(?:married|wed|couple)'
        ]
        
        # Birth/origin relations
        self.relation_patterns[RelationType.BORN_IN] = [
            r'{entity1}.*(?:born in|from|native of|originally from).*{entity2}',
            r'{entity1}.*(?:birthplace|hometown|origin).*{entity2}'
        ]
        
        # Education relations
        self.relation_patterns[RelationType.STUDIED_AT] = [
            r'{entity1}.*(?:studied at|graduated from|attended|alumnus of).*{entity2}',
            r'{entity1}.*(?:degree from|education at).*{entity2}',
            r'{entity2}.*(?:graduate|student|alumnus).*{entity1}'
        ]
        
        # Business relations
        self.relation_patterns[RelationType.ACQUIRED_BY] = [
            r'{entity1}.*(?:acquired by|bought by|purchased by).*{entity2}',
            r'{entity2}.*(?:acquired|bought|purchased).*{entity1}',
            r'{entity1}.*(?:acquisition|merger).*{entity2}'
        ]
        
        # Competition relations
        self.relation_patterns[RelationType.COMPETITOR_OF] = [
            r'{entity1}.*(?:competes with|rival of|competitor of).*{entity2}',
            r'{entity1}.*(?:and|vs|versus).*{entity2}.*(?:compete|rivalry|competition)'
        ]
        
        # Partnership relations
        self.relation_patterns[RelationType.PARTNER_WITH] = [
            r'{entity1}.*(?:partner with|partnership with|collaborates with).*{entity2}',
            r'{entity1}.*(?:and|&).*{entity2}.*(?:partnership|collaboration|joint)'
        ]
        
        logger.info(f"🎯 Setup patterns för {len(self.relation_patterns)} relation types")
        
    async def _initialize_parsers(self):
        """Initialize dependency parsers"""
        try:
            # Try to initialize spaCy for dependency parsing
            # import spacy  # Uncomment when available
            logger.info("📚 spaCy dependency parser initialization (mock)")
            self.dependency_parsers["spacy"] = {"model": "mock_spacy_dep", "available": True}
        except ImportError:
            logger.warning("⚠️ spaCy not available för dependency parsing")
            self.dependency_parsers["spacy"] = {"model": None, "available": False}
            
        # Regex-based fallback always available
        self.dependency_parsers["regex"] = {"model": "regex_patterns", "available": True}
        
    async def extract_relations(self, text: str, entities: List[Entity], method: str = "pattern_based") -> RelationExtractionResult:
        """Extract relations från text och entities"""
        import time
        start_time = time.time()
        
        if not self.initialized:
            await self.initialize()
            
        logger.info(f"🔍 Extracting relations using {method} method")
        
        if method == "pattern_based":
            relations = await self._extract_with_patterns(text, entities)
        elif method == "dependency_parsing":
            relations = await self._extract_with_dependency_parsing(text, entities)
        elif method == "hybrid":
            pattern_relations = await self._extract_with_patterns(text, entities)
            dep_relations = await self._extract_with_dependency_parsing(text, entities)
            relations = self._merge_relations(pattern_relations, dep_relations)
        else:
            relations = []
            
        processing_time = time.time() - start_time
        
        return RelationExtractionResult(
            text=text,
            entities=entities,
            relations=relations,
            processing_time=processing_time,
            method_used=method
        )
        
    async def _extract_with_patterns(self, text: str, entities: List[Entity]) -> List[Relation]:
        """Extract relations med pattern matching"""
        relations = []
        
        # Check all entity pairs
        for entity1, entity2 in combinations(entities, 2):
            # Test both directions
            for rel_type, patterns in self.relation_patterns.items():
                # Try entity1 -> entity2
                relation = await self._match_pattern(text, entity1, entity2, rel_type, patterns)
                if relation:
                    relations.append(relation)
                    continue
                    
                # Try entity2 -> entity1 för vissa relations
                if self._is_bidirectional_relation(rel_type):
                    relation = await self._match_pattern(text, entity2, entity1, rel_type, patterns)
                    if relation:
                        relations.append(relation)
                        
        return relations
        
    async def _match_pattern(self, text: str, entity1: Entity, entity2: Entity, 
                           rel_type: RelationType, patterns: List[str]) -> Optional[Relation]:
        """Match pattern mellan två entities"""
        
        # Get context window around entities
        start_pos = min(entity1.start, entity2.start)
        end_pos = max(entity1.end, entity2.end)
        context_start = max(0, start_pos - 100)
        context_end = min(len(text), end_pos + 100)
        context = text[context_start:context_end].lower()
        
        entity1_text = entity1.text.lower()
        entity2_text = entity2.text.lower()
        
        for pattern in patterns:
            # Replace placeholders with actual entity texts
            regex_pattern = pattern.replace('{entity1}', re.escape(entity1_text))
            regex_pattern = regex_pattern.replace('{entity2}', re.escape(entity2_text))
            
            match = re.search(regex_pattern, context, re.IGNORECASE | re.DOTALL)
            if match:
                confidence = self._calculate_pattern_confidence(pattern, match, context)
                
                return Relation(
                    source=entity1,
                    target=entity2,
                    relation_type=rel_type,
                    confidence=confidence,
                    evidence_text=match.group(),
                    pattern_used=pattern
                )
                
        return None
        
    def _calculate_pattern_confidence(self, pattern: str, match: re.Match, context: str) -> float:
        """Calculate confidence för pattern match"""
        base_confidence = 0.7
        
        # Boost confidence för exact matches
        if match.group() == pattern.replace('{entity1}', '').replace('{entity2}', '').strip():
            base_confidence += 0.2
            
        # Reduce confidence för very long matches (might be coincidental)
        if len(match.group()) > 200:
            base_confidence -= 0.1
            
        # Boost confidence för common relation indicators
        relation_indicators = ['is', 'was', 'works', 'located', 'owns', 'founded', 'CEO']
        for indicator in relation_indicators:
            if indicator.lower() in match.group().lower():
                base_confidence += 0.05
                break
                
        return min(0.95, max(0.3, base_confidence))
        
    async def _extract_with_dependency_parsing(self, text: str, entities: List[Entity]) -> List[Relation]:
        """Extract relations med dependency parsing (mock implementation)"""
        await asyncio.sleep(0.2)  # Simulate dependency parsing
        
        relations = []
        
        # Mock dependency parsing results
        if len(entities) >= 2:
            for i in range(0, len(entities)-1, 2):
                if i+1 < len(entities):
                    entity1 = entities[i]
                    entity2 = entities[i+1]
                    
                    # Mock relation based on entity types
                    if entity1.type == "PERSON" and entity2.type == "ORG":
                        relation = Relation(
                            source=entity1,
                            target=entity2,
                            relation_type=RelationType.WORKS_FOR,
                            confidence=0.8,
                            evidence_text=f"dependency parse: {entity1.text} -> {entity2.text}",
                            pattern_used="dependency_parsing"
                        )
                        relations.append(relation)
                    elif entity1.type == "ORG" and entity2.type == "GPE":
                        relation = Relation(
                            source=entity1,
                            target=entity2,
                            relation_type=RelationType.LOCATED_IN,
                            confidence=0.75,
                            evidence_text=f"dependency parse: {entity1.text} -> {entity2.text}",
                            pattern_used="dependency_parsing"
                        )
                        relations.append(relation)
                        
        return relations
        
    def _merge_relations(self, pattern_relations: List[Relation], dep_relations: List[Relation]) -> List[Relation]:
        """Merge relations från different methods"""
        merged = []
        seen_pairs = set()
        
        # Add pattern-based relations (higher confidence)
        for relation in pattern_relations:
            pair_key = (relation.source.text, relation.target.text, relation.relation_type.value)
            if pair_key not in seen_pairs:
                merged.append(relation)
                seen_pairs.add(pair_key)
                
        # Add dependency-based relations if not already seen
        for relation in dep_relations:
            pair_key = (relation.source.text, relation.target.text, relation.relation_type.value)
            if pair_key not in seen_pairs:
                merged.append(relation)
                seen_pairs.add(pair_key)
                
        return merged
        
    def _is_bidirectional_relation(self, rel_type: RelationType) -> bool:
        """Check if relation can be bidirectional"""
        bidirectional_relations = {
            RelationType.MARRIED_TO,
            RelationType.PARTNER_WITH,
            RelationType.COMPETITOR_OF,
            RelationType.CONNECTED_TO
        }
        return rel_type in bidirectional_relations
        
    def get_relation_graph(self, relations: List[Relation]) -> Dict[str, Any]:
        """Generate relation graph structure"""
        nodes = {}
        edges = []
        
        for relation in relations:
            # Add nodes
            source_id = f"{relation.source.text}_{relation.source.type}"
            target_id = f"{relation.target.text}_{relation.target.type}"
            
            nodes[source_id] = {
                "id": source_id,
                "label": relation.source.text,
                "type": relation.source.type
            }
            
            nodes[target_id] = {
                "id": target_id,
                "label": relation.target.text,
                "type": relation.target.type
            }
            
            # Add edge
            edges.append({
                "source": source_id,
                "target": target_id,
                "relation": relation.relation_type.value,
                "confidence": relation.confidence,
                "evidence": relation.evidence_text[:100] + "..." if len(relation.evidence_text) > 100 else relation.evidence_text
            })
            
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "metrics": {
                "total_nodes": len(nodes),
                "total_relations": len(relations),
                "relation_types": len(set(r.relation_type for r in relations))
            }
        }
        
    def get_relation_statistics(self, result: RelationExtractionResult) -> Dict[str, Any]:
        """Get relation statistics"""
        relation_counts = {}
        confidence_scores = []
        
        for relation in result.relations:
            rel_type = relation.relation_type.value
            relation_counts[rel_type] = relation_counts.get(rel_type, 0) + 1
            confidence_scores.append(relation.confidence)
            
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            "total_relations": len(result.relations),
            "relation_types": len(relation_counts),
            "relation_distribution": relation_counts,
            "average_confidence": round(avg_confidence, 3),
            "processing_time": round(result.processing_time, 3),
            "method_used": result.method_used,
            "entities_processed": len(result.entities)
        }
        
    async def cleanup(self):
        """Cleanup Relation Extraction Service"""
        logger.info("🧹 Cleaning up Relation Extraction Service")
        self.relation_patterns.clear()
        self.dependency_parsers.clear()
        self.initialized = False
        logger.info("✅ Relation Extraction Service cleanup completed")
