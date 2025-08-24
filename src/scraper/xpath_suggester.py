"""
XPath Suggester - Intelligent selector generation and optimization.

This module implements advanced logic for automatically suggesting robust XPath and CSS
selectors by analyzing multiple pages of the same template. It uses DOM clustering,
variance analysis, and stability scoring techniques for reliable field extraction.

Key Features:
- Multi-page selector analysis
- Stability scoring and ranking
- Automatic field pattern detection
- Conflict resolution and optimization
- Template variance adaptation
"""

import re
import hashlib
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass
from lxml import html, etree
from difflib import SequenceMatcher

from utils.logger import get_logger
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


@dataclass
class SelectorCandidate:
    """Candidate selector with scoring metrics."""
    selector: str
    selector_type: str  # 'xpath' or 'css'
    field_name: str
    stability_score: float
    precision_score: float
    coverage: float
    variance: float
    sample_values: List[str]
    conflicts: List[str] = None
    
    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []


@dataclass
class FieldSuggestion:
    """Complete field suggestion with ranked selectors."""
    field_name: str
    primary_selector: SelectorCandidate
    fallback_selectors: List[SelectorCandidate]
    confidence: float
    data_type: str
    sample_values: List[str]


class XPathSuggester:
    """
    Advanced XPath and CSS selector suggestion system.
    
    Implements intelligent selector generation by analyzing multiple pages
    to identify stable, reliable selectors for data extraction.
    """
    
    def __init__(self, metrics_collector: MetricsCollector = None):
        self.metrics = metrics_collector
        self.min_stability_score = 0.7
        self.min_coverage = 0.8
        self.max_variance = 0.3
        
    def suggest_selectors_for_template(
        self, 
        html_samples: List[str], 
        field_hints: Dict[str, str] = None
    ) -> Dict[str, FieldSuggestion]:
        """
        Analyzes HTML documents and suggests stable selectors for fields.
        
        Args:
            html_samples: List of HTML documents from same template
            field_hints: Optional hints about expected field names/types
            
        Returns:
            Dictionary mapping field names to selector suggestions
        """
        logger.info(f"Analyzing {len(html_samples)} HTML samples for selector suggestions")
        
        if len(html_samples) < 2:
            raise ValueError("Need at least 2 HTML samples for comparison")
            
        # Parse all HTML samples
        parsed_docs = []
        for i, html_content in enumerate(html_samples):
            try:
                doc = html.fromstring(html_content)
                parsed_docs.append(doc)
            except Exception as e:
                logger.warning(f"Failed to parse HTML sample {i}: {e}")
                
        if len(parsed_docs) < 2:
            raise ValueError("Need at least 2 valid HTML documents")
            
        # Extract common structure patterns
        common_patterns = self._extract_common_patterns(parsed_docs)
        
        # Generate selector candidates
        candidates = self._generate_selector_candidates(parsed_docs, common_patterns)
        
        # Score and rank candidates
        scored_candidates = self._score_candidates(candidates, parsed_docs)
        
        # Group candidates by field and select best
        field_suggestions = self._group_and_select_best(scored_candidates, field_hints)
        
        # Resolve conflicts and optimize
        optimized_suggestions = self._optimize_suggestions(field_suggestions, parsed_docs)
        
        logger.info(f"Generated {len(optimized_suggestions)} field suggestions")
        
        if self.metrics:
            self.metrics.counter("xpath_suggester_analyses", 1)
            self.metrics.gauge("xpath_suggester_suggestions", len(optimized_suggestions))
            
        return optimized_suggestions
        
    def _extract_common_patterns(self, docs: List[html.HtmlElement]) -> Dict[str, Any]:
        """Extract common structural patterns across documents."""
        patterns = {
            'common_tags': [],
            'common_classes': [],
            'common_ids': [],
            'text_patterns': [],
            'structure_similarity': 0.0
        }
        
        # Extract tag sequences for each document
        tag_sequences = []
        all_classes = []
        all_ids = []
        
        for doc in docs:
            # Get tag sequence
            tags = [elem.tag for elem in doc.iter() if elem.tag != 'script' and elem.tag != 'style']
            tag_sequences.append(tags)
            
            # Get classes and IDs
            for elem in doc.iter():
                if elem.get('class'):
                    all_classes.extend(elem.get('class').split())
                if elem.get('id'):
                    all_ids.append(elem.get('id'))
                    
        # Find common elements
        if tag_sequences:
            # Compare tag sequences to find common structure
            base_sequence = tag_sequences[0]
            similarities = []
            
            for seq in tag_sequences[1:]:
                similarity = SequenceMatcher(None, base_sequence, seq).ratio()
                similarities.append(similarity)
                
            patterns['structure_similarity'] = sum(similarities) / len(similarities) if similarities else 0.0
            
            # Find most common tags
            all_tags = [tag for seq in tag_sequences for tag in seq]
            tag_counter = Counter(all_tags)
            patterns['common_tags'] = [tag for tag, count in tag_counter.most_common(20)]
            
        # Find common classes and IDs
        class_counter = Counter(all_classes)
        id_counter = Counter(all_ids)
        
        patterns['common_classes'] = [cls for cls, count in class_counter.most_common(10) if count > 1]
        patterns['common_ids'] = [id_val for id_val, count in id_counter.most_common(10) if count > 1]
        
        return patterns
        
    def _generate_selector_candidates(
        self, 
        docs: List[html.HtmlElement], 
        patterns: Dict[str, Any]
    ) -> List[SelectorCandidate]:
        """Generate candidate selectors based on common patterns."""
        candidates = []
        
        # Generate candidates for each document
        for doc_idx, doc in enumerate(docs):
            doc_candidates = self._extract_candidates_from_doc(doc, patterns, doc_idx)
            candidates.extend(doc_candidates)
            
        # Group similar candidates
        grouped_candidates = self._group_similar_candidates(candidates)
        
        return grouped_candidates
        
    def _extract_candidates_from_doc(
        self, 
        doc: html.HtmlElement, 
        patterns: Dict[str, Any], 
        doc_idx: int
    ) -> List[SelectorCandidate]:
        """Extract selector candidates from a single document."""
        candidates = []
        
        # Look for text-containing elements
        for elem in doc.iter():
            if elem.text and elem.text.strip() and len(elem.text.strip()) > 2:
                text_content = elem.text.strip()
                
                # Skip script and style content
                if elem.tag in ['script', 'style']:
                    continue
                    
                # Generate XPath
                xpath = self._generate_xpath_for_element(elem, doc)
                if xpath:
                    field_name = self._infer_field_name(elem, text_content)
                    
                    candidate = SelectorCandidate(
                        selector=xpath,
                        selector_type='xpath',
                        field_name=field_name,
                        stability_score=0.0,  # Will be calculated later
                        precision_score=0.0,
                        coverage=0.0,
                        variance=0.0,
                        sample_values=[text_content]
                    )
                    candidates.append(candidate)
                    
                # Generate CSS selector if element has class or ID
                css_selector = self._generate_css_for_element(elem)
                if css_selector:
                    field_name = self._infer_field_name(elem, text_content)
                    
                    candidate = SelectorCandidate(
                        selector=css_selector,
                        selector_type='css',
                        field_name=field_name,
                        stability_score=0.0,
                        precision_score=0.0,
                        coverage=0.0,
                        variance=0.0,
                        sample_values=[text_content]
                    )
                    candidates.append(candidate)
                    
        return candidates
        
    def _generate_xpath_for_element(self, elem: html.HtmlElement, doc: html.HtmlElement) -> str:
        """Generate XPath for an element with position tolerance."""
        try:
            # Get path to element
            path_elements = []
            current = elem
            
            while current is not None and current != doc:
                tag = current.tag
                
                # Add position predicate for non-unique elements
                siblings = [e for e in current.getparent() if e.tag == tag] if current.getparent() is not None else [current]
                
                if len(siblings) > 1:
                    position = siblings.index(current) + 1
                    path_elements.append(f"{tag}[{position}]")
                else:
                    path_elements.append(tag)
                    
                current = current.getparent()
                
            if path_elements:
                path_elements.reverse()
                xpath = "//" + "/".join(path_elements)
                return xpath
                
        except Exception as e:
            logger.debug(f"Error generating XPath: {e}")
            
        return None
        
    def _generate_css_for_element(self, elem: html.HtmlElement) -> str:
        """Generate CSS selector for element if it has class or ID."""
        selectors = []
        
        # Use ID if available
        elem_id = elem.get('id')
        if elem_id:
            return f"#{elem_id}"
            
        # Use class if available
        elem_class = elem.get('class')
        if elem_class:
            classes = elem_class.split()
            if classes:
                class_selector = "." + ".".join(classes)
                return f"{elem.tag}{class_selector}"
                
        return None
        
    def _infer_field_name(self, elem: html.HtmlElement, text_content: str) -> str:
        """Infer field name from element context and content."""
        # Check for common field indicators
        field_indicators = {
            'name': ['name', 'title', 'namn', 'titel'],
            'price': ['price', 'cost', 'pris', 'kostnad', '$', '€', 'kr'],
            'description': ['description', 'desc', 'beskrivning', 'info'],
            'date': ['date', 'time', 'datum', 'tid'],
            'email': ['email', 'mail', 'e-post'],
            'phone': ['phone', 'tel', 'telefon'],
            'address': ['address', 'location', 'adress', 'plats'],
            'id': ['id', 'identifier', 'ref', 'reference']
        }
        
        # Check element attributes
        for attr_name in ['class', 'id', 'name', 'data-field']:
            attr_value = elem.get(attr_name, '').lower()
            if attr_value:
                for field_type, keywords in field_indicators.items():
                    if any(keyword in attr_value for keyword in keywords):
                        return field_type
                        
        # Check text content patterns
        text_lower = text_content.lower()
        
        # Email pattern
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', text_content):
            return 'email'
            
        # Phone pattern
        if re.match(r'^[\+]?[\d\s\-\(\)]{7,}$', text_content):
            return 'phone'
            
        # Price pattern
        if re.search(r'[\$€£¥¢₹₽¤]|\d+[,.]?\d*\s*(kr|sek|usd|eur|gbp)', text_lower):
            return 'price'
            
        # Date pattern
        if re.search(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}', text_content):
            return 'date'
            
        # Default to content-based name
        content_words = re.findall(r'\w+', text_lower)
        if content_words:
            return content_words[0] if len(content_words[0]) > 2 else 'field'
            
        return 'unknown_field'
        
    def _group_similar_candidates(self, candidates: List[SelectorCandidate]) -> List[SelectorCandidate]:
        """Group candidates that target similar elements."""
        grouped = defaultdict(list)
        
        for candidate in candidates:
            # Create grouping key based on field name and selector similarity
            key = f"{candidate.field_name}_{candidate.selector_type}"
            grouped[key].append(candidate)
            
        # Merge similar candidates
        merged_candidates = []
        for group in grouped.values():
            if len(group) == 1:
                merged_candidates.append(group[0])
            else:
                # Merge candidates with same field name and type
                merged = self._merge_candidate_group(group)
                merged_candidates.append(merged)
                
        return merged_candidates
        
    def _merge_candidate_group(self, candidates: List[SelectorCandidate]) -> SelectorCandidate:
        """Merge a group of similar candidates."""
        # Use the most common selector
        selectors = [c.selector for c in candidates]
        selector_counts = Counter(selectors)
        most_common_selector = selector_counts.most_common(1)[0][0]
        
        # Combine sample values
        all_values = []
        for candidate in candidates:
            all_values.extend(candidate.sample_values)
            
        # Create merged candidate
        base_candidate = candidates[0]
        merged = SelectorCandidate(
            selector=most_common_selector,
            selector_type=base_candidate.selector_type,
            field_name=base_candidate.field_name,
            stability_score=0.0,
            precision_score=0.0,
            coverage=0.0,
            variance=0.0,
            sample_values=list(set(all_values))  # Remove duplicates
        )
        
        return merged
        
    def _score_candidates(
        self, 
        candidates: List[SelectorCandidate], 
        docs: List[html.HtmlElement]
    ) -> List[SelectorCandidate]:
        """Score candidates based on stability, precision, and coverage."""
        scored_candidates = []
        
        for candidate in candidates:
            scores = self._calculate_candidate_scores(candidate, docs)
            
            candidate.stability_score = scores['stability']
            candidate.precision_score = scores['precision']
            candidate.coverage = scores['coverage']
            candidate.variance = scores['variance']
            
            scored_candidates.append(candidate)
            
        return scored_candidates
        
    def _calculate_candidate_scores(
        self, 
        candidate: SelectorCandidate, 
        docs: List[html.HtmlElement]
    ) -> Dict[str, float]:
        """Calculate stability, precision, and coverage scores."""
        successful_extractions = 0
        extracted_values = []
        
        for doc in docs:
            try:
                if candidate.selector_type == 'xpath':
                    results = doc.xpath(candidate.selector)
                else:  # CSS
                    results = doc.cssselect(candidate.selector)
                    
                if results:
                    successful_extractions += 1
                    # Extract text content
                    for elem in results:
                        if hasattr(elem, 'text_content'):
                            text = elem.text_content().strip()
                        else:
                            text = (elem.text or '').strip()
                        if text:
                            extracted_values.append(text)
                            
            except Exception as e:
                logger.debug(f"Error applying selector {candidate.selector}: {e}")
                
        total_docs = len(docs)
        coverage = successful_extractions / total_docs if total_docs > 0 else 0.0
        
        # Calculate stability (consistency of extraction)
        stability = coverage  # Simple stability measure
        
        # Calculate precision (quality of extracted values)
        precision = 0.8 if extracted_values else 0.0  # Default precision
        
        # Calculate variance (consistency of extracted values)
        if len(extracted_values) > 1:
            # Simple variance based on value diversity
            unique_values = len(set(extracted_values))
            total_values = len(extracted_values)
            variance = unique_values / total_values
        else:
            variance = 0.0 if extracted_values else 1.0
            
        return {
            'stability': stability,
            'precision': precision,
            'coverage': coverage,
            'variance': variance
        }
        
    def _group_and_select_best(
        self, 
        candidates: List[SelectorCandidate], 
        field_hints: Dict[str, str] = None
    ) -> Dict[str, List[SelectorCandidate]]:
        """Group candidates by field name and rank them."""
        field_groups = defaultdict(list)
        
        for candidate in candidates:
            field_groups[candidate.field_name].append(candidate)
            
        # Rank candidates within each field group
        ranked_groups = {}
        for field_name, field_candidates in field_groups.items():
            # Sort by combined score
            ranked_candidates = sorted(
                field_candidates,
                key=lambda c: (
                    c.stability_score * 0.4 + 
                    c.precision_score * 0.3 + 
                    c.coverage * 0.3
                ),
                reverse=True
            )
            ranked_groups[field_name] = ranked_candidates
            
        return ranked_groups
        
    def _optimize_suggestions(
        self, 
        field_groups: Dict[str, List[SelectorCandidate]], 
        docs: List[html.HtmlElement]
    ) -> Dict[str, FieldSuggestion]:
        """Create optimized field suggestions with primary and fallback selectors."""
        suggestions = {}
        
        for field_name, candidates in field_groups.items():
            if not candidates:
                continue
                
            # Filter candidates that meet minimum requirements
            qualified_candidates = [
                c for c in candidates 
                if (c.stability_score >= self.min_stability_score and 
                    c.coverage >= self.min_coverage and 
                    c.variance <= self.max_variance)
            ]
            
            if not qualified_candidates:
                # Lower standards if no candidates meet requirements
                qualified_candidates = candidates[:1]
                
            primary = qualified_candidates[0]
            fallbacks = qualified_candidates[1:3]  # Max 2 fallbacks
            
            # Calculate overall confidence
            confidence = (
                primary.stability_score * 0.4 +
                primary.precision_score * 0.3 +
                primary.coverage * 0.3
            )
            
            # Infer data type from sample values
            data_type = self._infer_data_type(primary.sample_values)
            
            suggestion = FieldSuggestion(
                field_name=field_name,
                primary_selector=primary,
                fallback_selectors=fallbacks,
                confidence=confidence,
                data_type=data_type,
                sample_values=primary.sample_values
            )
            
            suggestions[field_name] = suggestion
            
        return suggestions
        
    def _infer_data_type(self, sample_values: List[str]) -> str:
        """Infer data type from sample values."""
        if not sample_values:
            return 'text'
            
        # Check patterns in sample values
        numeric_count = 0
        date_count = 0
        email_count = 0
        url_count = 0
        
        for value in sample_values:
            # Numeric
            if re.match(r'^\d+([.,]\d+)*$', value.replace(' ', '')):
                numeric_count += 1
            # Date
            elif re.search(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}', value):
                date_count += 1
            # Email
            elif re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
                email_count += 1
            # URL
            elif re.match(r'^https?://', value):
                url_count += 1
                
        total = len(sample_values)
        
        # Determine predominant type
        if numeric_count / total > 0.8:
            return 'numeric'
        elif date_count / total > 0.7:
            return 'date'
        elif email_count / total > 0.7:
            return 'email'
        elif url_count / total > 0.7:
            return 'url'
        else:
            return 'text'
            
    def generate_selector_report(self, suggestions: Dict[str, FieldSuggestion]) -> str:
        """Generate human-readable report of selector suggestions."""
        report_lines = []
        report_lines.append("XPath Suggester Analysis Report")
        report_lines.append("=" * 40)
        report_lines.append("")
        
        for field_name, suggestion in suggestions.items():
            report_lines.append(f"Field: {field_name} ({suggestion.data_type})")
            report_lines.append(f"Confidence: {suggestion.confidence:.2f}")
            report_lines.append(f"Primary Selector ({suggestion.primary_selector.selector_type}): {suggestion.primary_selector.selector}")
            report_lines.append(f"  Stability: {suggestion.primary_selector.stability_score:.2f}")
            report_lines.append(f"  Coverage: {suggestion.primary_selector.coverage:.2f}")
            
            if suggestion.fallback_selectors:
                report_lines.append("Fallback Selectors:")
                for i, fallback in enumerate(suggestion.fallback_selectors):
                    report_lines.append(f"  {i+1}. ({fallback.selector_type}) {fallback.selector}")
                    
            report_lines.append(f"Sample Values: {', '.join(suggestion.sample_values[:3])}")
            report_lines.append("")
            
        return "\n".join(report_lines)