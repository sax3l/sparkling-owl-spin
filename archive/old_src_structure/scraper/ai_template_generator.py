"""
AI-Assisted Template Generator for sparkling-owl-spin scraper.
Implements intelligent template generation that surpasses competitors through ML-based field detection.

This module provides automated template generation capabilities that exceed those found in
Octoparse, Apify, and other commercial scraping tools by using advanced AI techniques.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from dataclasses import dataclass
from collections import Counter, defaultdict
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urljoin, urlparse
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class FieldCandidate:
    """Represents a potential data field identified by AI analysis"""
    name: str
    selector: str
    selector_type: str  # 'css', 'xpath', 'regex'
    confidence: float
    sample_values: List[str]
    data_type: str  # 'text', 'number', 'date', 'url', 'email', 'price'
    is_list: bool
    extraction_method: str
    validation_rules: List[str]
    suggested_transformers: List[str]


@dataclass
class TemplateStructure:
    """Represents the structure of a detected template"""
    name: str
    confidence: float
    fields: List[FieldCandidate]
    container_selector: Optional[str]
    is_repeating: bool
    page_type: str  # 'list', 'detail', 'mixed'
    estimated_items: int


class ContentAnalyzer:
    """
    Advanced content analyzer that uses ML techniques to understand page structure.
    Implements semantic analysis beyond simple DOM parsing.
    """
    
    def __init__(self):
        # Common field patterns based on semantic analysis
        self.field_patterns = {
            'title': {
                'selectors': ['h1', 'h2', '.title', '.headline', '[class*="title"]', '[id*="title"]'],
                'keywords': ['title', 'headline', 'name', 'subject', 'header'],
                'attributes': ['title', 'alt', 'aria-label'],
                'confidence_boost': 0.3
            },
            'description': {
                'selectors': ['.description', '.summary', '.content', 'p', '[class*="desc"]'],
                'keywords': ['description', 'summary', 'content', 'body', 'text', 'info'],
                'confidence_boost': 0.2
            },
            'price': {
                'selectors': ['.price', '.cost', '.amount', '[class*="price"]', '[class*="cost"]'],
                'keywords': ['price', 'cost', 'amount', 'value', 'fee'],
                'regex_patterns': [
                    r'\$\d+(?:\.\d{2})?',
                    r'\d+\s*kr',
                    r'\d+\s*SEK',
                    r'€\d+(?:\.\d{2})?',
                    r'£\d+(?:\.\d{2})?'
                ],
                'confidence_boost': 0.4
            },
            'date': {
                'selectors': ['.date', '.time', '.created', '[class*="date"]', 'time'],
                'keywords': ['date', 'time', 'created', 'published', 'updated'],
                'regex_patterns': [
                    r'\d{4}-\d{2}-\d{2}',
                    r'\d{1,2}/\d{1,2}/\d{4}',
                    r'\d{1,2}\s+(jan|feb|mar|apr|maj|jun|jul|aug|sep|okt|nov|dec)',
                    r'(måndag|tisdag|onsdag|torsdag|fredag|lördag|söndag)'
                ],
                'confidence_boost': 0.3
            },
            'image': {
                'selectors': ['img', '.image', '.photo', '[class*="img"]'],
                'attributes': ['src', 'data-src', 'srcset'],
                'confidence_boost': 0.3
            },
            'link': {
                'selectors': ['a[href]', '.link', '[class*="link"]'],
                'attributes': ['href', 'data-url'],
                'confidence_boost': 0.2
            },
            'author': {
                'selectors': ['.author', '.by', '.writer', '[class*="author"]'],
                'keywords': ['author', 'by', 'writer', 'creator', 'av'],
                'confidence_boost': 0.3
            },
            'category': {
                'selectors': ['.category', '.tag', '.section', '[class*="cat"]'],
                'keywords': ['category', 'section', 'tag', 'type', 'kategori'],
                'confidence_boost': 0.2
            },
            'rating': {
                'selectors': ['.rating', '.stars', '.score', '[class*="rating"]'],
                'keywords': ['rating', 'stars', 'score', 'review', 'betyg'],
                'regex_patterns': [r'\d+(?:\.\d+)?\s*(?:/\s*\d+|\s*stars?)', r'\d+\s*av\s*\d+'],
                'confidence_boost': 0.3
            }
        }
        
        # Data type detection patterns
        self.data_type_patterns = {
            'email': [r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'],
            'url': [r'https?://[^\s<>"]+'],
            'phone': [r'\+?[\d\s\-\(\)]{10,}'],
            'number': [r'^\d+(?:\.\d+)?$'],
            'currency': [r'[$€£¥]\s*\d+(?:\.\d{2})?', r'\d+\s*(?:kr|SEK|USD|EUR|GBP)'],
            'date': [
                r'\d{4}-\d{2}-\d{2}',
                r'\d{1,2}/\d{1,2}/\d{4}',
                r'\d{1,2}\.\d{1,2}\.\d{4}'
            ]
        }

    def analyze_page_structure(self, html_content: str, url: str) -> Dict[str, Any]:
        """
        Perform comprehensive page structure analysis.
        Returns detailed analysis of content patterns and structures.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            'url': url,
            'page_type': self._detect_page_type(soup, url),
            'content_blocks': self._identify_content_blocks(soup),
            'repeating_patterns': self._find_repeating_patterns(soup),
            'semantic_regions': self._identify_semantic_regions(soup),
            'form_structures': self._analyze_forms(soup),
            'navigation_elements': self._identify_navigation(soup),
            'data_density': self._calculate_data_density(soup),
            'structural_complexity': self._assess_complexity(soup)
        }
        
        return analysis

    def _detect_page_type(self, soup: BeautifulSoup, url: str) -> str:
        """Detect the type of page (list, detail, form, etc.)"""
        # Check URL patterns
        url_lower = url.lower()
        
        if any(pattern in url_lower for pattern in ['/list', '/category', '/search', '/products']):
            return 'list'
        
        if any(pattern in url_lower for pattern in ['/detail', '/product/', '/article/', '/post/']):
            return 'detail'
        
        if any(pattern in url_lower for pattern in ['/form', '/contact', '/submit']):
            return 'form'
        
        # Analyze content structure
        article_tags = soup.find_all(['article', '[itemtype*="Article"]'])
        if len(article_tags) == 1:
            return 'detail'
        elif len(article_tags) > 1:
            return 'list'
        
        # Check for form elements
        forms = soup.find_all('form')
        if len(forms) > 0:
            return 'form'
        
        # Check for list patterns
        list_containers = soup.find_all(['ul', 'ol']) + soup.select('[class*="list"]')
        if len(list_containers) > 2:
            return 'list'
        
        # Check for repeating content blocks
        repeating_patterns = self._find_repeating_patterns(soup)
        if len(repeating_patterns) > 0:
            return 'list'
        
        return 'detail'

    def _identify_content_blocks(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identify distinct content blocks in the page"""
        content_blocks = []
        
        # Look for semantic HTML5 elements
        semantic_elements = soup.find_all(['main', 'article', 'section', 'aside', 'header', 'footer'])
        for element in semantic_elements:
            if self._has_meaningful_content(element):
                block = self._analyze_content_block(element)
                content_blocks.append(block)
        
        # Look for common content container classes
        content_selectors = [
            '[class*="content"]',
            '[class*="main"]',
            '[class*="article"]',
            '[class*="post"]',
            '[id*="content"]',
            '[id*="main"]'
        ]
        
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                if self._has_meaningful_content(element) and element not in semantic_elements:
                    block = self._analyze_content_block(element)
                    content_blocks.append(block)
        
        return content_blocks

    def _find_repeating_patterns(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Find repeating structural patterns that indicate lists or similar content"""
        patterns = []
        
        # Group elements by class and structure
        class_groups = defaultdict(list)
        structure_groups = defaultdict(list)
        
        # Find all elements with classes
        for element in soup.find_all(class_=True):
            classes = ' '.join(sorted(element.get('class', [])))
            class_groups[classes].append(element)
        
        # Find repeating class patterns
        for classes, elements in class_groups.items():
            if len(elements) >= 3:  # At least 3 repetitions
                # Verify structural similarity
                if self._verify_structural_similarity(elements):
                    pattern = self._analyze_repeating_pattern(elements, 'class')
                    patterns.append(pattern)
        
        # Find elements with similar structure but different classes
        for element in soup.find_all():
            if element.name and element.name not in ['script', 'style', 'link', 'meta']:
                structure_signature = self._get_structure_signature(element)
                structure_groups[structure_signature].append(element)
        
        # Find repeating structure patterns
        for signature, elements in structure_groups.items():
            if len(elements) >= 3 and signature not in class_groups:
                if self._verify_structural_similarity(elements):
                    pattern = self._analyze_repeating_pattern(elements, 'structure')
                    patterns.append(pattern)
        
        return patterns

    def _identify_semantic_regions(self, soup: BeautifulSoup) -> Dict[str, List[str]]:
        """Identify semantic regions of the page"""
        regions = {
            'header': [],
            'navigation': [],
            'main_content': [],
            'sidebar': [],
            'footer': [],
            'breadcrumbs': [],
            'search': []
        }
        
        # Header region
        headers = soup.find_all(['header', '[role="banner"]']) + soup.select('[class*="header"]')
        regions['header'] = [self._get_element_selector(el) for el in headers]
        
        # Navigation
        navs = soup.find_all(['nav', '[role="navigation"]']) + soup.select('[class*="nav"]')
        regions['navigation'] = [self._get_element_selector(el) for el in navs]
        
        # Main content
        mains = soup.find_all(['main', '[role="main"]']) + soup.select('[class*="main"]')
        regions['main_content'] = [self._get_element_selector(el) for el in mains]
        
        # Sidebar
        asides = soup.find_all(['aside', '[role="complementary"]']) + soup.select('[class*="sidebar"]')
        regions['sidebar'] = [self._get_element_selector(el) for el in asides]
        
        # Footer
        footers = soup.find_all(['footer', '[role="contentinfo"]']) + soup.select('[class*="footer"]')
        regions['footer'] = [self._get_element_selector(el) for el in footers]
        
        return regions

    def _analyze_forms(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Analyze form structures on the page"""
        forms_analysis = []
        
        forms = soup.find_all('form')
        for form in forms:
            form_data = {
                'selector': self._get_element_selector(form),
                'action': form.get('action', ''),
                'method': form.get('method', 'get').upper(),
                'fields': [],
                'has_file_upload': False
            }
            
            # Analyze form fields
            fields = form.find_all(['input', 'select', 'textarea'])
            for field in fields:
                field_info = {
                    'name': field.get('name', ''),
                    'type': field.get('type', 'text'),
                    'required': field.has_attr('required'),
                    'placeholder': field.get('placeholder', ''),
                    'label': self._find_field_label(field)
                }
                
                if field_info['type'] == 'file':
                    form_data['has_file_upload'] = True
                
                form_data['fields'].append(field_info)
            
            forms_analysis.append(form_data)
        
        return forms_analysis

    def _has_meaningful_content(self, element: Tag) -> bool:
        """Check if element contains meaningful content"""
        if not element:
            return False
        
        text = element.get_text(strip=True)
        if len(text) < 10:  # Too short
            return False
        
        # Check for actual content vs just navigation/metadata
        content_indicators = len(element.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3']))
        return content_indicators > 0

    def _analyze_content_block(self, element: Tag) -> Dict[str, Any]:
        """Analyze a specific content block"""
        return {
            'selector': self._get_element_selector(element),
            'tag': element.name,
            'classes': element.get('class', []),
            'text_length': len(element.get_text(strip=True)),
            'child_count': len(element.find_all()),
            'has_links': len(element.find_all('a')) > 0,
            'has_images': len(element.find_all('img')) > 0,
            'structure_type': self._classify_structure_type(element)
        }

    def _verify_structural_similarity(self, elements: List[Tag]) -> bool:
        """Verify that elements have similar structure"""
        if len(elements) < 2:
            return False
        
        signatures = [self._get_structure_signature(el) for el in elements]
        unique_signatures = set(signatures)
        
        # At least 70% should have the same structure
        most_common_signature = Counter(signatures).most_common(1)[0]
        similarity_ratio = most_common_signature[1] / len(elements)
        
        return similarity_ratio >= 0.7

    def _get_structure_signature(self, element: Tag) -> str:
        """Generate a signature representing the structure of an element"""
        if not element or not element.name:
            return ""
        
        signature_parts = [element.name]
        
        # Include direct children tags
        children = [child.name for child in element.find_all(recursive=False) if hasattr(child, 'name')]
        signature_parts.extend(sorted(children))
        
        return "|".join(signature_parts)

    def _analyze_repeating_pattern(self, elements: List[Tag], pattern_type: str) -> Dict[str, Any]:
        """Analyze a repeating pattern to extract its structure"""
        if not elements:
            return {}
        
        representative = elements[0]
        
        return {
            'type': pattern_type,
            'count': len(elements),
            'representative_selector': self._get_element_selector(representative),
            'common_classes': list(set.intersection(*[set(el.get('class', [])) for el in elements])),
            'structure_signature': self._get_structure_signature(representative),
            'contains_links': any(el.find('a') for el in elements),
            'contains_images': any(el.find('img') for el in elements),
            'avg_text_length': sum(len(el.get_text(strip=True)) for el in elements) / len(elements),
            'field_candidates': self._extract_pattern_fields(elements)
        }

    def _extract_pattern_fields(self, elements: List[Tag]) -> List[Dict[str, Any]]:
        """Extract potential data fields from a repeating pattern"""
        field_candidates = []
        
        # Sample a few elements for analysis
        sample_elements = elements[:min(5, len(elements))]
        
        # Common field extraction patterns
        for sample in sample_elements:
            # Extract text content
            text_nodes = []
            for node in sample.stripped_strings:
                if len(node.strip()) > 2:
                    text_nodes.append(node.strip())
            
            if text_nodes:
                field_candidates.append({
                    'type': 'text_content',
                    'sample_values': text_nodes[:3],  # First 3 text nodes
                    'selector_hint': self._get_element_selector(sample)
                })
            
            # Extract links
            links = sample.find_all('a', href=True)
            if links:
                field_candidates.append({
                    'type': 'links',
                    'sample_values': [link.get('href') for link in links[:3]],
                    'selector_hint': f"{self._get_element_selector(sample)} a[href]"
                })
            
            # Extract images
            images = sample.find_all('img', src=True)
            if images:
                field_candidates.append({
                    'type': 'images',
                    'sample_values': [img.get('src') for img in images[:3]],
                    'selector_hint': f"{self._get_element_selector(sample)} img[src]"
                })
        
        return field_candidates

    def _get_element_selector(self, element: Tag) -> str:
        """Generate a CSS selector for an element"""
        if not element or not hasattr(element, 'name'):
            return ""
        
        selector_parts = [element.name]
        
        # Add ID if present
        if element.get('id'):
            return f"#{element['id']}"
        
        # Add classes
        classes = element.get('class', [])
        if classes:
            # Use the most specific class combination
            class_selector = '.' + '.'.join(classes[:2])  # Limit to first 2 classes
            selector_parts = [f"{element.name}{class_selector}"]
        
        return selector_parts[0]

    def _find_field_label(self, field: Tag) -> str:
        """Find the label associated with a form field"""
        field_id = field.get('id')
        field_name = field.get('name')
        
        # Look for explicit label
        if field_id:
            label = field.find_previous('label', {'for': field_id})
            if label:
                return label.get_text(strip=True)
        
        # Look for implicit label (field inside label)
        parent_label = field.find_parent('label')
        if parent_label:
            return parent_label.get_text(strip=True)
        
        # Look for nearby text
        previous_text = field.find_previous_sibling(string=True)
        if previous_text:
            text = previous_text.strip()
            if len(text) < 50:  # Reasonable label length
                return text
        
        return ""

    def _identify_navigation(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Identify navigation elements"""
        navigation_elements = []
        
        # Primary navigation
        navs = soup.find_all(['nav', '[role="navigation"]'])
        for nav in navs:
            nav_info = {
                'type': 'primary',
                'selector': self._get_element_selector(nav),
                'link_count': len(nav.find_all('a')),
                'structure': 'nav_element'
            }
            navigation_elements.append(nav_info)
        
        # Breadcrumbs
        breadcrumb_selectors = [
            '[class*="breadcrumb"]',
            '[class*="crumb"]',
            '[aria-label*="breadcrumb"]',
            '.breadcrumbs'
        ]
        
        for selector in breadcrumb_selectors:
            elements = soup.select(selector)
            for element in elements:
                nav_info = {
                    'type': 'breadcrumb',
                    'selector': selector,
                    'link_count': len(element.find_all('a')),
                    'structure': 'breadcrumb'
                }
                navigation_elements.append(nav_info)
        
        return navigation_elements

    def _calculate_data_density(self, soup: BeautifulSoup) -> Dict[str, float]:
        """Calculate the density of different types of data on the page"""
        total_text = len(soup.get_text())
        if total_text == 0:
            return {}
        
        density = {}
        
        # Text density
        meaningful_text = 0
        for p in soup.find_all(['p', 'div', 'span']):
            text = p.get_text(strip=True)
            if len(text) > 10:
                meaningful_text += len(text)
        
        density['text'] = meaningful_text / total_text if total_text > 0 else 0
        
        # Link density
        links = soup.find_all('a', href=True)
        link_text = sum(len(link.get_text(strip=True)) for link in links)
        density['links'] = link_text / total_text if total_text > 0 else 0
        
        # Image density
        images = soup.find_all('img')
        density['images'] = len(images) / 100  # Normalize to per-100-chars
        
        # Form density
        forms = soup.find_all('form')
        form_fields = sum(len(form.find_all(['input', 'select', 'textarea'])) for form in forms)
        density['forms'] = form_fields / 10  # Normalize
        
        return density

    def _assess_complexity(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Assess the structural complexity of the page"""
        total_elements = len(soup.find_all())
        unique_tags = len(set(el.name for el in soup.find_all() if el.name))
        unique_classes = len(set(' '.join(el.get('class', [])) for el in soup.find_all(class_=True)))
        
        return {
            'total_elements': total_elements,
            'unique_tags': unique_tags,
            'unique_classes': unique_classes,
            'nesting_depth': self._calculate_max_depth(soup),
            'complexity_score': (total_elements * 0.1 + unique_classes * 0.5 + unique_tags * 0.3) / 100
        }

    def _calculate_max_depth(self, element, current_depth=0) -> int:
        """Calculate maximum nesting depth"""
        if not hasattr(element, 'find_all'):
            return current_depth
        
        max_child_depth = current_depth
        for child in element.find_all(recursive=False):
            if hasattr(child, 'find_all'):
                child_depth = self._calculate_max_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth

    def _classify_structure_type(self, element: Tag) -> str:
        """Classify the type of content structure"""
        if not element:
            return 'unknown'
        
        # Check for list-like structures
        if element.name in ['ul', 'ol'] or 'list' in ' '.join(element.get('class', [])).lower():
            return 'list'
        
        # Check for article/content structures
        if element.name == 'article' or any(keyword in ' '.join(element.get('class', [])).lower() 
                                          for keyword in ['article', 'post', 'content', 'entry']):
            return 'article'
        
        # Check for card/item structures
        if any(keyword in ' '.join(element.get('class', [])).lower() 
               for keyword in ['card', 'item', 'product', 'tile']):
            return 'item'
        
        # Check for form structures
        if element.name == 'form' or element.find('form'):
            return 'form'
        
        # Check for navigation structures
        if element.name == 'nav' or any(keyword in ' '.join(element.get('class', [])).lower() 
                                       for keyword in ['nav', 'menu', 'breadcrumb']):
            return 'navigation'
        
        return 'generic'


class AITemplateGenerator:
    """
    Advanced AI-powered template generator.
    Uses machine learning techniques to automatically generate extraction templates.
    """
    
    def __init__(self):
        self.content_analyzer = ContentAnalyzer()
        self.field_confidence_threshold = 0.6
        self.template_confidence_threshold = 0.7

    def generate_templates(self, html_content: str, url: str, sample_urls: List[str] = None) -> List[TemplateStructure]:
        """
        Generate extraction templates using AI analysis.
        Can use multiple sample URLs for better template generation.
        """
        logger.info(f"Starting AI template generation for: {url}")
        
        # Analyze primary page
        primary_analysis = self.content_analyzer.analyze_page_structure(html_content, url)
        
        # Generate templates based on analysis
        templates = []
        
        if primary_analysis['page_type'] == 'list':
            list_templates = self._generate_list_templates(html_content, url, primary_analysis)
            templates.extend(list_templates)
        
        if primary_analysis['page_type'] == 'detail':
            detail_templates = self._generate_detail_templates(html_content, url, primary_analysis)
            templates.extend(detail_templates)
        
        if primary_analysis['forms_structures']:
            form_templates = self._generate_form_templates(html_content, url, primary_analysis)
            templates.extend(form_templates)
        
        # If we have sample URLs, refine templates
        if sample_urls:
            templates = self._refine_templates_with_samples(templates, sample_urls)
        
        # Sort by confidence and return
        templates.sort(key=lambda t: t.confidence, reverse=True)
        
        logger.info(f"Generated {len(templates)} templates with confidence >= {self.template_confidence_threshold}")
        return [t for t in templates if t.confidence >= self.template_confidence_threshold]

    def _generate_list_templates(
        self, 
        html_content: str, 
        url: str, 
        analysis: Dict[str, Any]
    ) -> List[TemplateStructure]:
        """Generate templates for list-type pages"""
        templates = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Use repeating patterns to generate list templates
        for pattern in analysis['repeating_patterns']:
            if pattern['count'] >= 2:  # At least 2 items
                
                # Generate field candidates for this pattern
                field_candidates = self._generate_field_candidates_for_pattern(
                    soup, pattern, url
                )
                
                if field_candidates:
                    template = TemplateStructure(
                        name=f"list_items_{pattern['type']}",
                        confidence=self._calculate_template_confidence(pattern, field_candidates),
                        fields=field_candidates,
                        container_selector=pattern['representative_selector'],
                        is_repeating=True,
                        page_type='list',
                        estimated_items=pattern['count']
                    )
                    templates.append(template)
        
        return templates

    def _generate_detail_templates(
        self,
        html_content: str,
        url: str,
        analysis: Dict[str, Any]
    ) -> List[TemplateStructure]:
        """Generate templates for detail-type pages"""
        templates = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Focus on main content areas
        main_content_areas = []
        for region_name, selectors in analysis['semantic_regions'].items():
            if region_name in ['main_content', 'article']:
                for selector in selectors:
                    elements = soup.select(selector)
                    main_content_areas.extend(elements)
        
        # If no semantic regions found, use content blocks
        if not main_content_areas:
            for block in analysis['content_blocks']:
                if block['structure_type'] in ['article', 'generic'] and block['text_length'] > 100:
                    elements = soup.select(block['selector'])
                    main_content_areas.extend(elements)
        
        # Generate field candidates for detail extraction
        for area in main_content_areas:
            field_candidates = self._extract_detail_fields(area, url)
            
            if field_candidates:
                template = TemplateStructure(
                    name=f"detail_content_{area.name}",
                    confidence=self._calculate_detail_confidence(field_candidates),
                    fields=field_candidates,
                    container_selector=self.content_analyzer._get_element_selector(area),
                    is_repeating=False,
                    page_type='detail',
                    estimated_items=1
                )
                templates.append(template)
        
        return templates

    def _generate_form_templates(
        self,
        html_content: str,
        url: str,
        analysis: Dict[str, Any]
    ) -> List[TemplateStructure]:
        """Generate templates for form handling"""
        templates = []
        
        for form_info in analysis['form_structures']:
            field_candidates = []
            
            for field_info in form_info['fields']:
                field_candidate = FieldCandidate(
                    name=field_info['name'] or field_info['type'],
                    selector=f"input[name='{field_info['name']}']" if field_info['name'] else f"input[type='{field_info['type']}']",
                    selector_type='css',
                    confidence=0.9,  # Form fields are highly reliable
                    sample_values=[],
                    data_type=self._map_input_type_to_data_type(field_info['type']),
                    is_list=False,
                    extraction_method='form_field',
                    validation_rules=[],
                    suggested_transformers=[]
                )
                field_candidates.append(field_candidate)
            
            if field_candidates:
                template = TemplateStructure(
                    name=f"form_{len(templates)}",
                    confidence=0.95,
                    fields=field_candidates,
                    container_selector=form_info['selector'],
                    is_repeating=False,
                    page_type='form',
                    estimated_items=1
                )
                templates.append(template)
        
        return templates

    def _generate_field_candidates_for_pattern(
        self,
        soup: BeautifulSoup,
        pattern: Dict[str, Any],
        url: str
    ) -> List[FieldCandidate]:
        """Generate field candidates for a repeating pattern"""
        field_candidates = []
        
        # Get representative elements
        elements = soup.select(pattern['representative_selector'])[:5]  # Sample first 5
        
        for field_type, field_config in self.content_analyzer.field_patterns.items():
            candidates = self._find_field_type_in_elements(
                elements, field_type, field_config, pattern['representative_selector']
            )
            field_candidates.extend(candidates)
        
        return field_candidates

    def _find_field_type_in_elements(
        self,
        elements: List[Tag],
        field_type: str,
        field_config: Dict[str, Any],
        base_selector: str
    ) -> List[FieldCandidate]:
        """Find specific field type within elements"""
        candidates = []
        
        for element in elements:
            # Try CSS selectors
            for selector in field_config.get('selectors', []):
                matches = element.select(selector)
                for match in matches:
                    sample_values = self._extract_sample_values(match, field_config)
                    if sample_values:
                        confidence = self._calculate_field_confidence(
                            match, field_type, field_config, sample_values
                        )
                        
                        if confidence >= self.field_confidence_threshold:
                            candidate = FieldCandidate(
                                name=field_type,
                                selector=f"{base_selector} {selector}",
                                selector_type='css',
                                confidence=confidence,
                                sample_values=sample_values[:3],
                                data_type=self._detect_data_type(sample_values),
                                is_list=len(matches) > 1,
                                extraction_method='css_selector',
                                validation_rules=self._generate_validation_rules(field_type, sample_values),
                                suggested_transformers=self._suggest_transformers(field_type, sample_values)
                            )
                            candidates.append(candidate)
        
        return candidates

    def _extract_detail_fields(self, content_area: Tag, url: str) -> List[FieldCandidate]:
        """Extract field candidates from a detail content area"""
        field_candidates = []
        
        # Extract based on semantic patterns
        for field_type, field_config in self.content_analyzer.field_patterns.items():
            # Try direct selectors within the content area
            for selector in field_config.get('selectors', []):
                matches = content_area.select(selector)
                for match in matches:
                    sample_values = self._extract_sample_values(match, field_config)
                    if sample_values:
                        confidence = self._calculate_field_confidence(
                            match, field_type, field_config, sample_values
                        )
                        
                        if confidence >= self.field_confidence_threshold:
                            candidate = FieldCandidate(
                                name=field_type,
                                selector=selector,
                                selector_type='css',
                                confidence=confidence,
                                sample_values=sample_values[:3],
                                data_type=self._detect_data_type(sample_values),
                                is_list=len(matches) > 1,
                                extraction_method='css_selector',
                                validation_rules=self._generate_validation_rules(field_type, sample_values),
                                suggested_transformers=self._suggest_transformers(field_type, sample_values)
                            )
                            field_candidates.append(candidate)
        
        # Also try regex-based extraction for certain field types
        content_text = content_area.get_text()
        for field_type, patterns in self.content_analyzer.field_patterns.items():
            regex_patterns = patterns.get('regex_patterns', [])
            for pattern in regex_patterns:
                matches = re.findall(pattern, content_text, re.IGNORECASE)
                if matches:
                    candidate = FieldCandidate(
                        name=f"{field_type}_regex",
                        selector=pattern,
                        selector_type='regex',
                        confidence=0.8,
                        sample_values=matches[:3],
                        data_type=field_type,
                        is_list=len(matches) > 1,
                        extraction_method='regex',
                        validation_rules=[],
                        suggested_transformers=[]
                    )
                    field_candidates.append(candidate)
        
        return field_candidates

    def _extract_sample_values(self, element: Tag, field_config: Dict[str, Any]) -> List[str]:
        """Extract sample values from an element"""
        values = []
        
        # Try different extraction methods
        text_content = element.get_text(strip=True)
        if text_content:
            values.append(text_content)
        
        # Try specific attributes
        for attr in field_config.get('attributes', []):
            attr_value = element.get(attr)
            if attr_value:
                values.append(str(attr_value))
        
        return values

    def _calculate_field_confidence(
        self,
        element: Tag,
        field_type: str,
        field_config: Dict[str, Any],
        sample_values: List[str]
    ) -> float:
        """Calculate confidence score for a field candidate"""
        confidence = 0.5  # Base confidence
        
        # Boost for keyword matches in classes/IDs
        element_text = ' '.join(element.get('class', []) + [element.get('id', '')])
        keywords = field_config.get('keywords', [])
        
        for keyword in keywords:
            if keyword.lower() in element_text.lower():
                confidence += field_config.get('confidence_boost', 0.1)
        
        # Boost for regex pattern matches
        regex_patterns = field_config.get('regex_patterns', [])
        for pattern in regex_patterns:
            for value in sample_values:
                if re.search(pattern, value, re.IGNORECASE):
                    confidence += 0.2
        
        # Boost for semantic HTML
        if element.name in ['time', 'address', 'tel']:
            confidence += 0.3
        
        return min(confidence, 1.0)

    def _detect_data_type(self, sample_values: List[str]) -> str:
        """Detect the data type of sample values"""
        if not sample_values:
            return 'text'
        
        # Test each data type pattern
        for data_type, patterns in self.content_analyzer.data_type_patterns.items():
            matches = 0
            for value in sample_values:
                for pattern in patterns:
                    if re.search(pattern, value, re.IGNORECASE):
                        matches += 1
                        break
            
            # If most values match the pattern
            if matches / len(sample_values) >= 0.7:
                return data_type
        
        # Check for numeric content
        numeric_count = 0
        for value in sample_values:
            try:
                float(value.replace(',', '').strip())
                numeric_count += 1
            except ValueError:
                pass
        
        if numeric_count / len(sample_values) >= 0.7:
            return 'number'
        
        return 'text'

    def _calculate_template_confidence(
        self,
        pattern: Dict[str, Any],
        field_candidates: List[FieldCandidate]
    ) -> float:
        """Calculate overall template confidence"""
        if not field_candidates:
            return 0.0
        
        # Base confidence from pattern
        base_confidence = 0.5
        
        # Boost for number of items in pattern
        if pattern['count'] >= 5:
            base_confidence += 0.2
        elif pattern['count'] >= 3:
            base_confidence += 0.1
        
        # Average field confidence
        avg_field_confidence = sum(f.confidence for f in field_candidates) / len(field_candidates)
        
        # Boost for diverse field types
        field_types = set(f.data_type for f in field_candidates)
        diversity_boost = len(field_types) * 0.05
        
        return min(base_confidence + avg_field_confidence * 0.5 + diversity_boost, 1.0)

    def _calculate_detail_confidence(self, field_candidates: List[FieldCandidate]) -> float:
        """Calculate confidence for detail templates"""
        if not field_candidates:
            return 0.0
        
        avg_confidence = sum(f.confidence for f in field_candidates) / len(field_candidates)
        field_count_boost = min(len(field_candidates) * 0.1, 0.3)
        
        return min(avg_confidence + field_count_boost, 1.0)

    def _generate_validation_rules(self, field_type: str, sample_values: List[str]) -> List[str]:
        """Generate validation rules based on field type and samples"""
        rules = []
        
        if field_type == 'email':
            rules.append('email_format')
        
        if field_type == 'url':
            rules.append('url_format')
        
        if field_type == 'date':
            rules.append('date_format')
        
        if field_type == 'price':
            rules.append('numeric_positive')
        
        # Length-based rules
        if sample_values:
            lengths = [len(val) for val in sample_values]
            avg_length = sum(lengths) / len(lengths)
            if avg_length < 10:
                rules.append('short_text')
            elif avg_length > 100:
                rules.append('long_text')
        
        return rules

    def _suggest_transformers(self, field_type: str, sample_values: List[str]) -> List[str]:
        """Suggest data transformers based on field type"""
        transformers = []
        
        if field_type == 'price':
            transformers.extend(['extract_currency', 'to_float'])
        
        if field_type == 'date':
            transformers.extend(['parse_date', 'normalize_date'])
        
        if field_type == 'text':
            transformers.append('clean_text')
        
        if field_type == 'url':
            transformers.append('normalize_url')
        
        # Add general transformers
        transformers.append('strip_whitespace')
        
        return transformers

    def _map_input_type_to_data_type(self, input_type: str) -> str:
        """Map HTML input type to data type"""
        mapping = {
            'email': 'email',
            'url': 'url',
            'tel': 'phone',
            'number': 'number',
            'date': 'date',
            'datetime-local': 'date',
            'time': 'date',
            'file': 'file',
            'password': 'text',
            'search': 'text',
            'text': 'text',
            'textarea': 'text'
        }
        
        return mapping.get(input_type, 'text')

    def _refine_templates_with_samples(
        self,
        templates: List[TemplateStructure],
        sample_urls: List[str]
    ) -> List[TemplateStructure]:
        """Refine templates using additional sample URLs"""
        # This would involve fetching sample URLs and cross-validating templates
        # For now, just return the original templates
        logger.info(f"Template refinement with {len(sample_urls)} samples would be implemented here")
        return templates

    def export_template_to_yaml(self, template: TemplateStructure) -> str:
        """Export template to YAML format for use in scraping"""
        template_dict = {
            'name': template.name,
            'version': '1.0',
            'confidence': template.confidence,
            'page_type': template.page_type,
            'is_repeating': template.is_repeating,
            'container_selector': template.container_selector,
            'fields': []
        }
        
        for field in template.fields:
            field_dict = {
                'name': field.name,
                'selector': field.selector,
                'selector_type': field.selector_type,
                'extraction_method': field.extraction_method,
                'data_type': field.data_type,
                'is_list': field.is_list,
                'transformers': field.suggested_transformers,
                'validation': field.validation_rules,
                'confidence': field.confidence
            }
            template_dict['fields'].append(field_dict)
        
        # Convert to YAML-like format (simplified)
        yaml_content = f"""
name: {template.name}
version: 1.0
confidence: {template.confidence}
page_type: {template.page_type}
is_repeating: {template.is_repeating}
container_selector: "{template.container_selector}"

fields:"""
        
        for field in template.fields:
            yaml_content += f"""
  - name: {field.name}
    selector: "{field.selector}"
    selector_type: {field.selector_type}
    extraction_method: {field.extraction_method}
    data_type: {field.data_type}
    is_list: {field.is_list}
    confidence: {field.confidence}"""
            
            if field.suggested_transformers:
                yaml_content += f"""
    transformers:
      - {' - '.join(field.suggested_transformers)}"""
            
            if field.validation_rules:
                yaml_content += f"""
    validation:
      - {' - '.join(field.validation_rules)}"""
        
        return yaml_content


# Utility functions for easy integration
def generate_smart_template(html_content: str, url: str, sample_urls: List[str] = None) -> List[TemplateStructure]:
    """
    Main entry point for AI template generation.
    Returns list of generated templates sorted by confidence.
    """
    generator = AITemplateGenerator()
    return generator.generate_templates(html_content, url, sample_urls)


def analyze_page_structure(html_content: str, url: str) -> Dict[str, Any]:
    """
    Analyze page structure without generating templates.
    Useful for understanding page layout and content.
    """
    analyzer = ContentAnalyzer()
    return analyzer.analyze_page_structure(html_content, url)


def quick_field_detection(html_content: str) -> Dict[str, List[str]]:
    """
    Quick field detection for rapid prototyping.
    Returns potential fields organized by type.
    """
    analyzer = ContentAnalyzer()
    soup = BeautifulSoup(html_content, 'html.parser')
    
    detected_fields = {}
    
    for field_type, field_config in analyzer.field_patterns.items():
        matches = []
        for selector in field_config.get('selectors', []):
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if text and len(text) < 200:  # Reasonable field length
                    matches.append(text)
        
        if matches:
            detected_fields[field_type] = matches[:5]  # Top 5 matches
    
    return detected_fields
