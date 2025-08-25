"""
Advanced pagination and infinite scroll handler for the sparkling-owl-spin crawler.
Implements sophisticated pagination detection and handling as recommended in the analysis report.

This module provides enterprise-grade pagination handling that surpasses competitors like
Octoparse by automatically detecting and navigating various pagination patterns.
"""

import re
import json
import asyncio
from typing import List, Dict, Optional, Set, Tuple, Any
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class PaginationPattern:
    """Represents a detected pagination pattern"""
    
    def __init__(
        self,
        pattern_type: str,
        base_url: str,
        current_page: int = 1,
        total_pages: Optional[int] = None,
        next_url: Optional[str] = None,
        prev_url: Optional[str] = None,
        page_param: Optional[str] = None,
        url_template: Optional[str] = None,
        confidence: float = 0.5
    ):
        self.pattern_type = pattern_type
        self.base_url = base_url
        self.current_page = current_page
        self.total_pages = total_pages
        self.next_url = next_url
        self.prev_url = prev_url
        self.page_param = page_param
        self.url_template = url_template
        self.confidence = confidence


class SmartPaginationDetector:
    """
    Intelligent pagination detection system that learns from various patterns.
    Implements advanced heuristics to detect pagination better than competitors.
    """
    
    def __init__(self):
        self.pagination_indicators = [
            # English
            'next', 'previous', 'prev', 'page', 'more', 'load more', 'show more',
            'first', 'last', 'continue', '»', '«', '›', '‹', '→', '←',
            # Swedish
            'nästa', 'föregående', 'sida', 'mer', 'ladda mer', 'visa mer',
            'första', 'sista', 'fortsätt',
            # Numbers and symbols
            r'\d+', r'^\d+$', r'page\s*\d+', r'sida\s*\d+'
        ]
        
        self.pagination_selectors = [
            # Standard pagination
            '.pagination', '.pager', '.page-nav', '.page-numbers',
            # WordPress
            '.wp-pagenavi', '.page-links',
            # Bootstrap
            '.pagination-wrapper', 'nav[aria-label*="pagination"]',
            # Custom classes
            '.paginate', '.paging', '.page-control',
            # ARIA labels
            '[role="navigation"]', 'nav[aria-label*="Page"]',
            # Common patterns
            '.next', '.prev', '.previous'
        ]
        
        self.infinite_scroll_indicators = [
            'infinite-scroll', 'endless-scroll', 'auto-load', 'lazy-load',
            'load-more', 'scroll-load', 'infinite', 'endless'
        ]

    def detect_pagination(self, html_content: str, base_url: str) -> List[PaginationPattern]:
        """
        Comprehensive pagination detection using multiple strategies.
        Returns list of detected pagination patterns with confidence scores.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        patterns = []
        
        # Strategy 1: Detect standard pagination elements
        standard_patterns = self._detect_standard_pagination(soup, base_url)
        patterns.extend(standard_patterns)
        
        # Strategy 2: Detect URL parameter-based pagination
        param_patterns = self._detect_parameter_pagination(soup, base_url)
        patterns.extend(param_patterns)
        
        # Strategy 3: Detect JavaScript-based pagination
        js_patterns = self._detect_javascript_pagination(soup, base_url)
        patterns.extend(js_patterns)
        
        # Strategy 4: Detect infinite scroll
        infinite_patterns = self._detect_infinite_scroll(soup, base_url)
        patterns.extend(infinite_patterns)
        
        # Strategy 5: Detect numbered pagination
        numbered_patterns = self._detect_numbered_pagination(soup, base_url)
        patterns.extend(numbered_patterns)
        
        # Remove duplicates and sort by confidence
        unique_patterns = self._deduplicate_patterns(patterns)
        return sorted(unique_patterns, key=lambda p: p.confidence, reverse=True)

    def _detect_standard_pagination(self, soup: BeautifulSoup, base_url: str) -> List[PaginationPattern]:
        """Detect standard pagination with next/previous links"""
        patterns = []
        
        # Look for next/previous links with high confidence
        next_links = soup.find_all('a', href=True)
        for link in next_links:
            href = link.get('href')
            text = link.get_text(strip=True).lower()
            classes = ' '.join(link.get('class', [])).lower()
            
            # Check for next page indicators
            is_next = any(indicator in text for indicator in ['next', 'nästa', '>', '»', '›', '→'])
            is_next = is_next or any(indicator in classes for indicator in ['next', 'nästa'])
            is_next = is_next or link.get('rel') == ['next']
            
            if is_next:
                absolute_url = urljoin(base_url, href)
                confidence = self._calculate_confidence(link, 'next')
                
                pattern = PaginationPattern(
                    pattern_type='standard_next',
                    base_url=base_url,
                    next_url=absolute_url,
                    confidence=confidence
                )
                patterns.append(pattern)
        
        return patterns

    def _detect_parameter_pagination(self, soup: BeautifulSoup, base_url: str) -> List[PaginationPattern]:
        """Detect URL parameter-based pagination (e.g., ?page=2, ?p=3)"""
        patterns = []
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)
        
        # Common page parameters
        page_params = ['page', 'p', 'pg', 'pagenum', 'offset', 'start', 'sida']
        
        for param in page_params:
            if param in query_params:
                try:
                    current_page = int(query_params[param][0])
                    
                    # Try to detect total pages from pagination links
                    total_pages = self._extract_total_pages(soup)
                    
                    # Generate next URL
                    next_params = query_params.copy()
                    next_params[param] = [str(current_page + 1)]
                    next_query = urlencode(next_params, doseq=True)
                    next_url = urlunparse(parsed_url._replace(query=next_query))
                    
                    pattern = PaginationPattern(
                        pattern_type='parameter',
                        base_url=base_url,
                        current_page=current_page,
                        total_pages=total_pages,
                        next_url=next_url,
                        page_param=param,
                        confidence=0.8
                    )
                    patterns.append(pattern)
                    
                except (ValueError, IndexError):
                    continue
        
        return patterns

    def _detect_javascript_pagination(self, soup: BeautifulSoup, base_url: str) -> List[PaginationPattern]:
        """Detect JavaScript-based pagination (AJAX, SPA)"""
        patterns = []
        
        # Look for JavaScript pagination handlers
        buttons = soup.find_all(['button', 'a'], attrs={'onclick': True})
        for button in buttons:
            onclick = button.get('onclick', '')
            text = button.get_text(strip=True).lower()
            
            # Check for pagination-related JavaScript
            if any(indicator in text for indicator in ['next', 'previous', 'more', 'load']):
                # Extract page information from JavaScript
                page_match = re.search(r'page[=:]\s*(\d+)', onclick, re.IGNORECASE)
                if page_match:
                    page_num = int(page_match.group(1))
                    
                    pattern = PaginationPattern(
                        pattern_type='javascript',
                        base_url=base_url,
                        current_page=page_num,
                        confidence=0.6
                    )
                    patterns.append(pattern)
        
        # Look for data attributes
        elements = soup.find_all(attrs={'data-page': True})
        for elem in elements:
            try:
                page_num = int(elem.get('data-page'))
                pattern = PaginationPattern(
                    pattern_type='data_attribute',
                    base_url=base_url,
                    current_page=page_num,
                    confidence=0.7
                )
                patterns.append(pattern)
            except (ValueError, TypeError):
                continue
        
        return patterns

    def _detect_infinite_scroll(self, soup: BeautifulSoup, base_url: str) -> List[PaginationPattern]:
        """Detect infinite scroll patterns"""
        patterns = []
        
        # Check for infinite scroll indicators in classes/IDs
        for indicator in self.infinite_scroll_indicators:
            elements = soup.find_all(class_=indicator) + soup.find_all(id=indicator)
            if elements:
                pattern = PaginationPattern(
                    pattern_type='infinite_scroll',
                    base_url=base_url,
                    confidence=0.9
                )
                patterns.append(pattern)
                break
        
        # Check for load more buttons
        load_more_texts = [
            'load more', 'show more', 'see more', 'more items',
            'ladda mer', 'visa mer', 'se mer', 'fler objekt'
        ]
        
        buttons = soup.find_all(['button', 'a'])
        for button in buttons:
            text = button.get_text(strip=True).lower()
            if any(phrase in text for phrase in load_more_texts):
                pattern = PaginationPattern(
                    pattern_type='load_more',
                    base_url=base_url,
                    confidence=0.8
                )
                patterns.append(pattern)
        
        # Check JavaScript for infinite scroll
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                content = script.string.lower()
                if ('infinite' in content and 'scroll' in content) or 'onscroll' in content:
                    pattern = PaginationPattern(
                        pattern_type='js_infinite_scroll',
                        base_url=base_url,
                        confidence=0.7
                    )
                    patterns.append(pattern)
        
        return patterns

    def _detect_numbered_pagination(self, soup: BeautifulSoup, base_url: str) -> List[PaginationPattern]:
        """Detect numbered pagination (1, 2, 3, ... 10)"""
        patterns = []
        
        # Look for pagination containers
        for selector in self.pagination_selectors:
            containers = soup.select(selector)
            for container in containers:
                page_links = container.find_all('a', href=True)
                page_numbers = []
                
                for link in page_links:
                    text = link.get_text(strip=True)
                    if text.isdigit():
                        page_numbers.append((int(text), link.get('href')))
                
                if len(page_numbers) >= 2:  # At least 2 page numbers
                    page_numbers.sort(key=lambda x: x[0])
                    
                    # Detect pattern
                    if len(page_numbers) > 1:
                        # Try to determine URL pattern
                        url_template = self._extract_url_template(page_numbers, base_url)
                        total_pages = max(num for num, _ in page_numbers)
                        
                        pattern = PaginationPattern(
                            pattern_type='numbered',
                            base_url=base_url,
                            total_pages=total_pages,
                            url_template=url_template,
                            confidence=0.9
                        )
                        patterns.append(pattern)
        
        return patterns

    def _calculate_confidence(self, element, pagination_type: str) -> float:
        """Calculate confidence score for pagination element"""
        confidence = 0.5
        
        text = element.get_text(strip=True).lower()
        classes = ' '.join(element.get('class', [])).lower()
        
        # Text-based confidence
        if pagination_type == 'next':
            if 'next' in text or 'nästa' in text:
                confidence += 0.3
            if '>' in text or '»' in text or '›' in text:
                confidence += 0.2
        
        # Class-based confidence
        pagination_classes = ['next', 'prev', 'previous', 'pagination', 'pager']
        if any(pc in classes for pc in pagination_classes):
            confidence += 0.2
        
        # Rel attribute
        if element.get('rel') in [['next'], ['prev'], ['previous']]:
            confidence += 0.3
        
        return min(confidence, 1.0)

    def _extract_total_pages(self, soup: BeautifulSoup) -> Optional[int]:
        """Try to extract total number of pages"""
        # Look for "Page X of Y" patterns
        page_info_patterns = [
            r'page\s+\d+\s+of\s+(\d+)',
            r'sida\s+\d+\s+av\s+(\d+)',
            r'showing\s+\d+\s*-\s*\d+\s+of\s+(\d+)',
            r'visar\s+\d+\s*-\s*\d+\s+av\s+(\d+)'
        ]
        
        text_content = soup.get_text().lower()
        for pattern in page_info_patterns:
            match = re.search(pattern, text_content)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue
        
        # Look for highest numbered page link
        page_links = soup.find_all('a', href=True)
        max_page = 0
        
        for link in page_links:
            text = link.get_text(strip=True)
            if text.isdigit():
                max_page = max(max_page, int(text))
        
        return max_page if max_page > 1 else None

    def _extract_url_template(self, page_numbers: List[Tuple[int, str]], base_url: str) -> Optional[str]:
        """Extract URL template from page number links"""
        if len(page_numbers) < 2:
            return None
        
        # Get URLs for first two pages
        url1 = urljoin(base_url, page_numbers[0][1])
        url2 = urljoin(base_url, page_numbers[1][1])
        
        # Try to find the difference
        parsed1 = urlparse(url1)
        parsed2 = urlparse(url2)
        
        # Check if it's parameter-based
        if parsed1.path == parsed2.path:
            # Parameter-based pagination
            params1 = parse_qs(parsed1.query)
            params2 = parse_qs(parsed2.query)
            
            for param in params1:
                if param in params2:
                    try:
                        val1 = int(params1[param][0])
                        val2 = int(params2[param][0])
                        if val2 == val1 + 1:
                            # Found the page parameter
                            template = url1.replace(str(val1), '{page}')
                            return template
                    except (ValueError, IndexError):
                        continue
        
        # Path-based pagination
        if page_numbers[0][0] == 1 and page_numbers[1][0] == 2:
            # Try to replace the number in the path
            path1 = parsed1.path
            path2 = parsed2.path
            
            # Find differing parts
            for i, (c1, c2) in enumerate(zip(path1, path2)):
                if c1 != c2:
                    if c1 == '1' and c2 == '2':
                        template = url1.replace('1', '{page}')
                        return template
        
        return None

    def _deduplicate_patterns(self, patterns: List[PaginationPattern]) -> List[PaginationPattern]:
        """Remove duplicate patterns, keeping the highest confidence ones"""
        seen_types = set()
        unique_patterns = []
        
        # Sort by confidence desc, then by type
        patterns.sort(key=lambda p: (p.confidence, p.pattern_type), reverse=True)
        
        for pattern in patterns:
            if pattern.pattern_type not in seen_types:
                unique_patterns.append(pattern)
                seen_types.add(pattern.pattern_type)
        
        return unique_patterns


class PaginationNavigator:
    """
    Advanced pagination navigator that can traverse different pagination types.
    Implements intelligent navigation strategies based on detected patterns.
    """
    
    def __init__(self, max_pages: int = 100, delay_between_pages: float = 1.0):
        self.max_pages = max_pages
        self.delay_between_pages = delay_between_pages
        self.visited_urls = set()
        
    async def navigate_pagination(
        self,
        initial_url: str,
        patterns: List[PaginationPattern],
        http_client,  # HTTP client for fetching pages
        callback=None  # Callback function for each page
    ) -> List[Dict[str, Any]]:
        """
        Navigate through pagination using detected patterns.
        Returns list of page results.
        """
        results = []
        
        if not patterns:
            logger.warning("No pagination patterns detected")
            return results
        
        # Use the highest confidence pattern
        primary_pattern = patterns[0]
        
        if primary_pattern.pattern_type == 'infinite_scroll':
            results = await self._handle_infinite_scroll(
                initial_url, primary_pattern, http_client, callback
            )
        elif primary_pattern.pattern_type in ['numbered', 'parameter']:
            results = await self._handle_numbered_pagination(
                initial_url, primary_pattern, http_client, callback
            )
        elif primary_pattern.pattern_type in ['standard_next', 'load_more']:
            results = await self._handle_sequential_pagination(
                initial_url, primary_pattern, http_client, callback
            )
        else:
            logger.info(f"Unsupported pagination type: {primary_pattern.pattern_type}")
        
        return results

    async def _handle_numbered_pagination(
        self,
        base_url: str,
        pattern: PaginationPattern,
        http_client,
        callback=None
    ) -> List[Dict[str, Any]]:
        """Handle numbered pagination (1, 2, 3, ...)"""
        results = []
        
        if not pattern.url_template:
            logger.warning("No URL template for numbered pagination")
            return results
        
        total_pages = min(pattern.total_pages or self.max_pages, self.max_pages)
        
        for page_num in range(1, total_pages + 1):
            if len(results) >= self.max_pages:
                break
            
            page_url = pattern.url_template.replace('{page}', str(page_num))
            
            if page_url in self.visited_urls:
                continue
                
            self.visited_urls.add(page_url)
            
            try:
                logger.info(f"Fetching page {page_num}: {page_url}")
                response = await http_client.get(page_url)
                
                if response.status_code == 200:
                    page_data = {
                        'url': page_url,
                        'page_number': page_num,
                        'content': response.text,
                        'status': 'success'
                    }
                    
                    if callback:
                        await callback(page_data)
                    
                    results.append(page_data)
                else:
                    logger.warning(f"Failed to fetch page {page_num}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"Error fetching page {page_num}: {e}")
                continue
            
            # Respectful delay between requests
            if page_num < total_pages:
                await asyncio.sleep(self.delay_between_pages)
        
        return results

    async def _handle_sequential_pagination(
        self,
        initial_url: str,
        pattern: PaginationPattern,
        http_client,
        callback=None
    ) -> List[Dict[str, Any]]:
        """Handle sequential pagination (next -> next -> next)"""
        results = []
        current_url = pattern.next_url or initial_url
        page_num = 1
        
        while current_url and len(results) < self.max_pages:
            if current_url in self.visited_urls:
                break
                
            self.visited_urls.add(current_url)
            
            try:
                logger.info(f"Fetching sequential page {page_num}: {current_url}")
                response = await http_client.get(current_url)
                
                if response.status_code == 200:
                    page_data = {
                        'url': current_url,
                        'page_number': page_num,
                        'content': response.text,
                        'status': 'success'
                    }
                    
                    if callback:
                        await callback(page_data)
                    
                    results.append(page_data)
                    
                    # Find next URL in this page
                    detector = SmartPaginationDetector()
                    new_patterns = detector.detect_pagination(response.text, current_url)
                    
                    next_url = None
                    for new_pattern in new_patterns:
                        if new_pattern.next_url and new_pattern.next_url != current_url:
                            next_url = new_pattern.next_url
                            break
                    
                    current_url = next_url
                    page_num += 1
                    
                else:
                    logger.warning(f"Failed to fetch page {page_num}: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"Error fetching page {page_num}: {e}")
                break
            
            # Respectful delay
            if current_url:
                await asyncio.sleep(self.delay_between_pages)
        
        return results

    async def _handle_infinite_scroll(
        self,
        base_url: str,
        pattern: PaginationPattern,
        http_client,
        callback=None
    ) -> List[Dict[str, Any]]:
        """
        Handle infinite scroll pagination.
        Note: This is a simplified implementation. Real infinite scroll
        would require browser automation (Selenium/Playwright).
        """
        results = []
        
        logger.info("Infinite scroll detected - would need browser automation for full support")
        
        # For now, just return the initial page
        try:
            response = await http_client.get(base_url)
            if response.status_code == 200:
                page_data = {
                    'url': base_url,
                    'page_number': 1,
                    'content': response.text,
                    'status': 'success',
                    'note': 'Infinite scroll requires browser automation'
                }
                
                if callback:
                    await callback(page_data)
                
                results.append(page_data)
                
        except Exception as e:
            logger.error(f"Error fetching infinite scroll page: {e}")
        
        return results


class PaginationManager:
    """
    High-level manager for pagination handling.
    Integrates detection and navigation for complete pagination support.
    """
    
    def __init__(
        self,
        max_pages: int = 100,
        delay_between_pages: float = 1.0,
        respect_robots: bool = True
    ):
        self.detector = SmartPaginationDetector()
        self.navigator = PaginationNavigator(max_pages, delay_between_pages)
        self.respect_robots = respect_robots
        
    async def handle_pagination(
        self,
        url: str,
        html_content: str,
        http_client,
        page_callback=None
    ) -> Dict[str, Any]:
        """
        Complete pagination handling pipeline.
        Returns comprehensive pagination results.
        """
        logger.info(f"Starting pagination analysis for: {url}")
        
        # Detect pagination patterns
        patterns = self.detector.detect_pagination(html_content, url)
        
        if not patterns:
            logger.info("No pagination patterns detected")
            return {
                'initial_url': url,
                'patterns_detected': [],
                'pages_found': 1,
                'pages': [{
                    'url': url,
                    'page_number': 1,
                    'content': html_content,
                    'status': 'success'
                }]
            }
        
        logger.info(f"Detected {len(patterns)} pagination patterns:")
        for i, pattern in enumerate(patterns):
            logger.info(f"  {i+1}. {pattern.pattern_type} (confidence: {pattern.confidence:.2f})")
        
        # Navigate pagination
        page_results = await self.navigator.navigate_pagination(
            url, patterns, http_client, page_callback
        )
        
        # Include initial page if not already included
        initial_included = any(result['url'] == url for result in page_results)
        if not initial_included:
            page_results.insert(0, {
                'url': url,
                'page_number': 1,
                'content': html_content,
                'status': 'success'
            })
        
        return {
            'initial_url': url,
            'patterns_detected': [
                {
                    'type': p.pattern_type,
                    'confidence': p.confidence,
                    'total_pages': p.total_pages,
                    'current_page': p.current_page
                } for p in patterns
            ],
            'pages_found': len(page_results),
            'pages': page_results
        }

    def analyze_pagination_only(self, html_content: str, base_url: str) -> Dict[str, Any]:
        """
        Analyze pagination without navigating.
        Useful for understanding pagination structure.
        """
        patterns = self.detector.detect_pagination(html_content, base_url)
        
        return {
            'url': base_url,
            'has_pagination': len(patterns) > 0,
            'patterns': [
                {
                    'type': p.pattern_type,
                    'confidence': p.confidence,
                    'total_pages': p.total_pages,
                    'current_page': p.current_page,
                    'next_url': p.next_url,
                    'url_template': p.url_template
                } for p in patterns
            ],
            'recommendations': self._generate_recommendations(patterns)
        }
    
    def _generate_recommendations(self, patterns: List[PaginationPattern]) -> List[str]:
        """Generate recommendations based on detected patterns"""
        recommendations = []
        
        if not patterns:
            recommendations.append("No pagination detected - single page content")
            return recommendations
        
        primary_pattern = patterns[0]
        
        if primary_pattern.pattern_type == 'infinite_scroll':
            recommendations.append("Infinite scroll detected - consider using browser automation for full extraction")
        
        if primary_pattern.pattern_type == 'javascript':
            recommendations.append("JavaScript-based pagination - may require browser automation")
        
        if primary_pattern.total_pages:
            recommendations.append(f"Estimated {primary_pattern.total_pages} total pages")
        
        if primary_pattern.confidence < 0.7:
            recommendations.append("Low confidence pagination detection - manual verification recommended")
        
        return recommendations


# Utility functions
def quick_pagination_check(html_content: str, base_url: str) -> bool:
    """Quick check if page has pagination"""
    detector = SmartPaginationDetector()
    patterns = detector.detect_pagination(html_content, base_url)
    return len(patterns) > 0


def extract_pagination_info(html_content: str, base_url: str) -> Dict[str, Any]:
    """Extract pagination information without navigation"""
    manager = PaginationManager()
    return manager.analyze_pagination_only(html_content, base_url)
