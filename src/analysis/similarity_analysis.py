"""
Similarity Analysis - Advanced content and structure similarity detection.
Provides comprehensive analysis of webpage similarity, template detection,
and content drift monitoring for robust web scraping operations.
"""

import hashlib
import re
import statistics
from collections import Counter, defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from urllib.parse import urlparse

from utils.logger import get_logger
from observability.metrics import MetricsCollector

logger = get_logger(__name__)


@dataclass
class PageStructure:
    """Representation of webpage structure for similarity analysis."""
    url: str
    title: str
    tag_structure: List[str]
    text_blocks: List[str]
    form_elements: List[Dict[str, str]]
    link_patterns: List[str]
    css_selectors: Set[str]
    dom_hash: str
    content_hash: str
    analyzed_at: datetime


@dataclass
class SimilarityScore:
    """Comprehensive similarity scoring between pages."""
    structural_similarity: float
    content_similarity: float
    template_similarity: float
    overall_similarity: float
    confidence: float
    common_elements: List[str]
    differences: List[str]


@dataclass
class SimilarityResult:
    """Result of similarity analysis between pages."""
    url1: str
    url2: str
    similarity_score: SimilarityScore
    analysis_timestamp: datetime
    template_cluster: Optional[str] = None
    drift_detected: bool = False
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []


class SimilarityAnalyzer:
    """
    Advanced webpage similarity analysis system.
    
    Features:
    - DOM structure comparison
    - Content similarity detection
    - Template pattern recognition
    - Drift detection and monitoring
    - Clustering similar pages
    - Performance optimized analysis
    """
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        similarity_threshold: float = 0.8,
        structural_weight: float = 0.4,
        content_weight: float = 0.3,
        template_weight: float = 0.3
    ):
        self.metrics = metrics_collector
        self.similarity_threshold = similarity_threshold
        self.structural_weight = structural_weight
        self.content_weight = content_weight
        self.template_weight = template_weight
        
        # Cache for analyzed pages
        self.page_cache: Dict[str, PageStructure] = {}
        self.similarity_cache: Dict[Tuple[str, str], SimilarityScore] = {}
        
        # Template clusters
        self.template_clusters: Dict[str, List[str]] = defaultdict(list)
        
    async def analyze_page_structure(
        self, 
        url: str, 
        html_content: str, 
        page_title: str = ""
    ) -> PageStructure:
        """
        Analyze webpage structure for similarity comparison.
        
        Args:
            url: Page URL
            html_content: Raw HTML content
            page_title: Page title (optional)
            
        Returns:
            PageStructure object with extracted features
        """
        logger.debug(f"Analyzing page structure for: {url}")
        
        try:
            # Extract structural features
            tag_structure = self._extract_tag_structure(html_content)
            text_blocks = self._extract_text_blocks(html_content)
            form_elements = self._extract_form_elements(html_content)
            link_patterns = self._extract_link_patterns(html_content)
            css_selectors = self._extract_css_selectors(html_content)
            
            # Generate hashes
            dom_hash = self._generate_dom_hash(tag_structure)
            content_hash = self._generate_content_hash(text_blocks)
            
            # Create page structure
            page_structure = PageStructure(
                url=url,
                title=page_title,
                tag_structure=tag_structure,
                text_blocks=text_blocks,
                form_elements=form_elements,
                link_patterns=link_patterns,
                css_selectors=css_selectors,
                dom_hash=dom_hash,
                content_hash=content_hash,
                analyzed_at=datetime.now()
            )
            
            # Cache the analysis
            self.page_cache[url] = page_structure
            
            # Update metrics
            self.metrics.counter("similarity_analysis_pages_analyzed", 1)
            
            return page_structure
            
        except Exception as e:
            logger.error(f"Error analyzing page structure for {url}: {e}")
            raise
            
    def _extract_tag_structure(self, html_content: str) -> List[str]:
        """Extract DOM tag structure pattern."""
        # Remove content but keep tag structure
        tag_pattern = re.compile(r'<(/?)(\w+)[^>]*>')
        tags = []
        
        for match in tag_pattern.finditer(html_content):
            closing = match.group(1)
            tag_name = match.group(2).lower()
            
            # Skip script and style tags
            if tag_name in ['script', 'style']:
                continue
                
            tags.append(f"{'/' if closing else ''}{tag_name}")
            
        return tags
        
    def _extract_text_blocks(self, html_content: str) -> List[str]:
        """Extract meaningful text blocks from HTML."""
        # Remove scripts and styles
        clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.DOTALL | re.IGNORECASE)
        
        # Extract text content
        text_content = re.sub(r'<[^>]+>', ' ', clean_html)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        # Split into blocks and filter
        blocks = [
            block.strip() 
            for block in text_content.split('\n') 
            if block.strip() and len(block.strip()) > 10
        ]
        
        return blocks[:50]  # Limit to avoid memory issues
        
    def _extract_form_elements(self, html_content: str) -> List[Dict[str, str]]:
        """Extract form element patterns."""
        forms = []
        
        # Find form elements
        form_pattern = re.compile(r'<(input|select|textarea)[^>]*>', re.IGNORECASE)
        
        for match in form_pattern.finditer(html_content):
            element = match.group(0)
            
            # Extract key attributes
            form_element = {
                'tag': match.group(1).lower(),
                'type': self._extract_attribute(element, 'type'),
                'name': self._extract_attribute(element, 'name'),
                'id': self._extract_attribute(element, 'id'),
                'class': self._extract_attribute(element, 'class')
            }
            
            forms.append(form_element)
            
        return forms
        
    def _extract_link_patterns(self, html_content: str) -> List[str]:
        """Extract link URL patterns."""
        link_pattern = re.compile(r'<a[^>]+href=[\'"]([^\'"]+)[\'"][^>]*>', re.IGNORECASE)
        links = []
        
        for match in link_pattern.finditer(html_content):
            href = match.group(1)
            
            # Normalize and pattern-ize URLs
            pattern = self._generalize_url_pattern(href)
            if pattern:
                links.append(pattern)
                
        return list(set(links))  # Remove duplicates
        
    def _extract_css_selectors(self, html_content: str) -> Set[str]:
        """Extract potential CSS selectors from HTML."""
        selectors = set()
        
        # Extract class attributes
        class_pattern = re.compile(r'class=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
        for match in class_pattern.finditer(html_content):
            classes = match.group(1).split()
            for cls in classes:
                if cls and cls.isidentifier():
                    selectors.add(f".{cls}")
                    
        # Extract id attributes
        id_pattern = re.compile(r'id=[\'"]([^\'"]+)[\'"]', re.IGNORECASE)
        for match in id_pattern.finditer(html_content):
            id_value = match.group(1)
            if id_value and id_value.replace('-', '').replace('_', '').isalnum():
                selectors.add(f"#{id_value}")
                
        return selectors
        
    def _extract_attribute(self, element: str, attr_name: str) -> str:
        """Extract specific attribute value from element."""
        pattern = rf'{attr_name}=[\'"]([^\'"]*)[\'"]'
        match = re.search(pattern, element, re.IGNORECASE)
        return match.group(1) if match else ""
        
    def _generalize_url_pattern(self, url: str) -> str:
        """Generalize URL to pattern by replacing dynamic parts."""
        # Replace numbers with placeholders
        pattern = re.sub(r'\d+', '{ID}', url)
        
        # Replace UUIDs
        pattern = re.sub(
            r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
            '{UUID}', pattern, flags=re.IGNORECASE
        )
        
        # Replace common parameter patterns
        pattern = re.sub(r'\?.*$', '?{PARAMS}', pattern)
        
        return pattern
        
    def _generate_dom_hash(self, tag_structure: List[str]) -> str:
        """Generate hash for DOM structure."""
        structure_str = ''.join(tag_structure)
        return hashlib.md5(structure_str.encode()).hexdigest()
        
    def _generate_content_hash(self, text_blocks: List[str]) -> str:
        """Generate hash for content."""
        content_str = '\n'.join(text_blocks)
        return hashlib.md5(content_str.encode()).hexdigest()
        
    async def compare_pages(
        self, 
        page1: PageStructure, 
        page2: PageStructure
    ) -> SimilarityScore:
        """
        Compare two pages and return comprehensive similarity score.
        
        Args:
            page1: First page structure
            page2: Second page structure
            
        Returns:
            SimilarityScore with detailed comparison metrics
        """
        cache_key = (page1.url, page2.url)
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
            
        logger.debug(f"Comparing pages: {page1.url} vs {page2.url}")
        
        try:
            # Calculate different similarity dimensions
            structural_sim = self._calculate_structural_similarity(page1, page2)
            content_sim = self._calculate_content_similarity(page1, page2)
            template_sim = self._calculate_template_similarity(page1, page2)
            
            # Calculate weighted overall similarity
            overall_sim = (
                structural_sim * self.structural_weight +
                content_sim * self.content_weight +
                template_sim * self.template_weight
            )
            
            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(page1, page2, overall_sim)
            
            # Find common elements and differences
            common_elements = self._find_common_elements(page1, page2)
            differences = self._find_differences(page1, page2)
            
            similarity_score = SimilarityScore(
                structural_similarity=structural_sim,
                content_similarity=content_sim,
                template_similarity=template_sim,
                overall_similarity=overall_sim,
                confidence=confidence,
                common_elements=common_elements,
                differences=differences
            )
            
            # Cache the result
            self.similarity_cache[cache_key] = similarity_score
            
            # Update metrics
            self.metrics.histogram("similarity_analysis_score", overall_sim)
            self.metrics.counter("similarity_analysis_comparisons", 1)
            
            return similarity_score
            
        except Exception as e:
            logger.error(f"Error comparing pages {page1.url} vs {page2.url}: {e}")
            raise
            
    def _calculate_structural_similarity(
        self, 
        page1: PageStructure, 
        page2: PageStructure
    ) -> float:
        """Calculate structural similarity between pages."""
        # Compare tag structures
        tag_similarity = SequenceMatcher(
            None, page1.tag_structure, page2.tag_structure
        ).ratio()
        
        # Compare form elements
        form_similarity = self._compare_form_elements(
            page1.form_elements, page2.form_elements
        )
        
        # Compare CSS selectors
        css_similarity = self._compare_sets(
            page1.css_selectors, page2.css_selectors
        )
        
        # Weighted average
        return (tag_similarity * 0.5 + form_similarity * 0.3 + css_similarity * 0.2)
        
    def _calculate_content_similarity(
        self, 
        page1: PageStructure, 
        page2: PageStructure
    ) -> float:
        """Calculate content similarity between pages."""
        # Quick check with content hashes
        if page1.content_hash == page2.content_hash:
            return 1.0
            
        # Compare text blocks
        text_similarity = self._compare_text_blocks(
            page1.text_blocks, page2.text_blocks
        )
        
        # Compare link patterns
        link_similarity = self._compare_sets(
            set(page1.link_patterns), set(page2.link_patterns)
        )
        
        return (text_similarity * 0.7 + link_similarity * 0.3)
        
    def _calculate_template_similarity(
        self, 
        page1: PageStructure, 
        page2: PageStructure
    ) -> float:
        """Calculate template-level similarity."""
        # Quick check with DOM hashes
        if page1.dom_hash == page2.dom_hash:
            return 1.0
            
        # Analyze structural patterns
        pattern_similarity = self._analyze_structural_patterns(page1, page2)
        
        # Compare URL patterns (if same domain)
        url_similarity = 0.0
        if urlparse(page1.url).netloc == urlparse(page2.url).netloc:
            url_similarity = self._compare_url_structures(page1.url, page2.url)
            
        return (pattern_similarity * 0.8 + url_similarity * 0.2)
        
    def _compare_form_elements(
        self, 
        forms1: List[Dict[str, str]], 
        forms2: List[Dict[str, str]]
    ) -> float:
        """Compare form element structures."""
        if not forms1 and not forms2:
            return 1.0
        if not forms1 or not forms2:
            return 0.0
            
        # Create signature for each form set
        sig1 = self._create_form_signature(forms1)
        sig2 = self._create_form_signature(forms2)
        
        return SequenceMatcher(None, sig1, sig2).ratio()
        
    def _create_form_signature(self, forms: List[Dict[str, str]]) -> str:
        """Create a signature string for form elements."""
        signatures = []
        for form in forms:
            sig = f"{form['tag']}:{form['type']}:{form['name']}"
            signatures.append(sig)
        return '|'.join(sorted(signatures))
        
    def _compare_sets(self, set1: Set[str], set2: Set[str]) -> float:
        """Compare two sets and return similarity ratio."""
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
            
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
        
    def _compare_text_blocks(
        self, 
        blocks1: List[str], 
        blocks2: List[str]
    ) -> float:
        """Compare text block content."""
        if not blocks1 and not blocks2:
            return 1.0
        if not blocks1 or not blocks2:
            return 0.0
            
        # Use sequence matcher on combined text
        text1 = ' '.join(blocks1)
        text2 = ' '.join(blocks2)
        
        return SequenceMatcher(None, text1, text2).ratio()
        
    def _analyze_structural_patterns(
        self, 
        page1: PageStructure, 
        page2: PageStructure
    ) -> float:
        """Analyze high-level structural patterns."""
        # Compare tag frequency patterns
        counter1 = Counter(page1.tag_structure)
        counter2 = Counter(page2.tag_structure)
        
        all_tags = set(counter1.keys()) | set(counter2.keys())
        if not all_tags:
            return 1.0
            
        similarity_sum = 0.0
        for tag in all_tags:
            freq1 = counter1.get(tag, 0)
            freq2 = counter2.get(tag, 0)
            max_freq = max(freq1, freq2)
            if max_freq > 0:
                similarity_sum += min(freq1, freq2) / max_freq
                
        return similarity_sum / len(all_tags)
        
    def _compare_url_structures(self, url1: str, url2: str) -> float:
        """Compare URL path structures."""
        path1 = urlparse(url1).path.strip('/')
        path2 = urlparse(url2).path.strip('/')
        
        if not path1 and not path2:
            return 1.0
        if not path1 or not path2:
            return 0.0
            
        parts1 = path1.split('/')
        parts2 = path2.split('/')
        
        return SequenceMatcher(None, parts1, parts2).ratio()
        
    def _calculate_confidence(
        self, 
        page1: PageStructure, 
        page2: PageStructure, 
        similarity: float
    ) -> float:
        """Calculate confidence in similarity score."""
        factors = []
        
        # More content = higher confidence
        content_factor = min(1.0, (len(page1.text_blocks) + len(page2.text_blocks)) / 20)
        factors.append(content_factor)
        
        # More structure = higher confidence
        structure_factor = min(1.0, (len(page1.tag_structure) + len(page2.tag_structure)) / 100)
        factors.append(structure_factor)
        
        # CSS selector coverage
        css_factor = min(1.0, (len(page1.css_selectors) + len(page2.css_selectors)) / 20)
        factors.append(css_factor)
        
        # Extreme similarities are less confident unless perfect
        if 0.1 < similarity < 0.9:
            similarity_factor = 1.0
        elif similarity == 0.0 or similarity == 1.0:
            similarity_factor = 1.0
        else:
            similarity_factor = 0.8
        factors.append(similarity_factor)
        
        return statistics.mean(factors)
        
    def _find_common_elements(
        self, 
        page1: PageStructure, 
        page2: PageStructure
    ) -> List[str]:
        """Find common elements between pages."""
        common = []
        
        # Common CSS selectors
        common_css = page1.css_selectors.intersection(page2.css_selectors)
        common.extend([f"css:{selector}" for selector in list(common_css)[:10]])
        
        # Common link patterns
        common_links = set(page1.link_patterns).intersection(set(page2.link_patterns))
        common.extend([f"link:{pattern}" for pattern in list(common_links)[:5]])
        
        # Common form elements
        forms1_sigs = {self._create_form_signature([form]) for form in page1.form_elements}
        forms2_sigs = {self._create_form_signature([form]) for form in page2.form_elements}
        common_forms = forms1_sigs.intersection(forms2_sigs)
        common.extend([f"form:{sig}" for sig in list(common_forms)[:5]])
        
        return common
        
    def _find_differences(
        self, 
        page1: PageStructure, 
        page2: PageStructure
    ) -> List[str]:
        """Find key differences between pages."""
        differences = []
        
        # Tag structure differences
        if len(page1.tag_structure) != len(page2.tag_structure):
            differences.append(
                f"structure_length:{len(page1.tag_structure)} vs {len(page2.tag_structure)}"
            )
            
        # Content differences
        if len(page1.text_blocks) != len(page2.text_blocks):
            differences.append(
                f"content_blocks:{len(page1.text_blocks)} vs {len(page2.text_blocks)}"
            )
            
        # Form differences
        if len(page1.form_elements) != len(page2.form_elements):
            differences.append(
                f"form_elements:{len(page1.form_elements)} vs {len(page2.form_elements)}"
            )
            
        return differences
        
    async def cluster_similar_pages(
        self, 
        pages: List[PageStructure], 
        cluster_threshold: float = None
    ) -> Dict[str, List[str]]:
        """
        Cluster pages by similarity.
        
        Args:
            pages: List of page structures to cluster
            cluster_threshold: Similarity threshold for clustering
            
        Returns:
            Dictionary mapping cluster IDs to lists of URLs
        """
        if cluster_threshold is None:
            cluster_threshold = self.similarity_threshold
            
        logger.info(f"Clustering {len(pages)} pages with threshold {cluster_threshold}")
        
        clusters = {}
        cluster_id = 0
        
        for page in pages:
            assigned_cluster = None
            
            # Check against existing clusters
            for cid, cluster_pages in clusters.items():
                # Compare with first page in cluster (representative)
                if cluster_pages:
                    representative_url = cluster_pages[0]
                    representative_page = self.page_cache.get(representative_url)
                    
                    if representative_page:
                        similarity = await self.compare_pages(page, representative_page)
                        if similarity.overall_similarity >= cluster_threshold:
                            assigned_cluster = cid
                            break
                            
            # Assign to existing cluster or create new one
            if assigned_cluster is not None:
                clusters[assigned_cluster].append(page.url)
            else:
                clusters[cluster_id] = [page.url]
                cluster_id += 1
                
        # Update template clusters
        self.template_clusters.clear()
        for cid, urls in clusters.items():
            self.template_clusters[f"cluster_{cid}"] = urls
            
        logger.info(f"Created {len(clusters)} clusters")
        
        # Update metrics
        self.metrics.gauge("similarity_analysis_clusters", len(clusters))
        
        return clusters
        
    def detect_template_drift(
        self, 
        baseline_page: PageStructure, 
        current_page: PageStructure,
        drift_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect template drift between baseline and current page.
        
        Args:
            baseline_page: Baseline page structure
            current_page: Current page structure
            drift_threshold: Threshold for detecting significant drift
            
        Returns:
            Dictionary with drift analysis results
        """
        similarity = self.compare_pages(baseline_page, current_page)
        
        drift_detected = similarity.overall_similarity < (1.0 - drift_threshold)
        
        drift_analysis = {
            'drift_detected': drift_detected,
            'similarity_score': similarity.overall_similarity,
            'confidence': similarity.confidence,
            'drift_magnitude': 1.0 - similarity.overall_similarity,
            'affected_areas': {
                'structural': 1.0 - similarity.structural_similarity > drift_threshold,
                'content': 1.0 - similarity.content_similarity > drift_threshold,
                'template': 1.0 - similarity.template_similarity > drift_threshold
            },
            'differences': similarity.differences,
            'analysis_timestamp': datetime.now()
        }
        
        if drift_detected:
            logger.warning(
                f"Template drift detected: {baseline_page.url} -> {current_page.url} "
                f"(similarity: {similarity.overall_similarity:.2f})"
            )
            self.metrics.counter("similarity_analysis_drift_detected", 1)
        
        return drift_analysis
        
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get comprehensive analysis statistics."""
        return {
            'pages_analyzed': len(self.page_cache),
            'comparisons_cached': len(self.similarity_cache),
            'template_clusters': len(self.template_clusters),
            'cache_size_mb': self._estimate_cache_size(),
            'analysis_coverage': self._calculate_coverage()
        }
        
    def _estimate_cache_size(self) -> float:
        """Estimate cache size in MB."""
        # Rough estimation
        return (len(self.page_cache) * 10 + len(self.similarity_cache) * 2) / 1024
        
    def _calculate_coverage(self) -> Dict[str, float]:
        """Calculate analysis coverage metrics."""
        if not self.page_cache:
            return {'structural': 0.0, 'content': 0.0, 'template': 0.0}
            
        pages_with_structure = sum(
            1 for p in self.page_cache.values() 
            if p.tag_structure
        )
        pages_with_content = sum(
            1 for p in self.page_cache.values() 
            if p.text_blocks
        )
        pages_with_css = sum(
            1 for p in self.page_cache.values() 
            if p.css_selectors
        )
        
        total = len(self.page_cache)
        
        return {
            'structural': pages_with_structure / total,
            'content': pages_with_content / total,
            'template': pages_with_css / total
        }
        
    def clear_cache(self):
        """Clear analysis cache to free memory."""
        self.page_cache.clear()
        self.similarity_cache.clear()
        self.template_clusters.clear()
        logger.info("Similarity analysis cache cleared")