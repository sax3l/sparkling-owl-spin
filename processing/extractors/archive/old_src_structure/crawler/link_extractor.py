import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
from typing import Set, List, Dict, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# Common non-document extensions to ignore during crawling
IGNORED_EXTENSIONS = {
    '.zip', '.rar', '.tar', '.gz', '.7z',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.exe', '.dmg', '.iso', '.css', '.js', '.ico'
}

# URL patterns that typically indicate non-content pages
NON_CONTENT_PATTERNS = [
    r'.*/(login|register|signup|signin).*',
    r'.*/(admin|wp-admin).*',
    r'.*/(api|json|xml|rss).*',
    r'.*\.(css|js|ico|xml|txt)$',
    r'.*\?.*print.*',
    r'.*\?.*download.*',
    r'.*mailto:.*',
    r'.*tel:.*',
    r'.*javascript:.*'
]

# Patterns that suggest valuable content
CONTENT_PATTERNS = [
    r'.*/article/.*',
    r'.*/post/.*',
    r'.*/blog/.*',
    r'.*/news/.*',
    r'.*/product/.*',
    r'.*/item/.*',
    r'.*/detail/.*',
    r'.*/page/.*'
]


def extract_links(base_url: str, html_content: str, respect_nofollow: bool = True) -> Set[str]:
    """
    Extracts all valid, crawlable, absolute HTTP/HTTPS links from HTML content.
    Enhanced version with better filtering as per analysis recommendations.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    
    for a_tag in soup.find_all('a', href=True):
        # Respect rel="nofollow" as a politeness signal
        if respect_nofollow and a_tag.get('rel') and 'nofollow' in a_tag.get('rel'):
            continue

        href = a_tag['href']
        absolute_url = urljoin(base_url, href)
        parsed_url = urlparse(absolute_url)

        # Ensure it's a valid HTTP/HTTPS link
        if parsed_url.scheme not in ['http', 'https']:
            continue
        
        # Enhanced filtering with pattern matching
        if _should_ignore_url(absolute_url):
            continue
            
        links.add(absolute_url)
            
    return links


def _should_ignore_url(url: str) -> bool:
    """Advanced URL filtering logic"""
    url_lower = url.lower()
    parsed = urlparse(url_lower)
    
    # Check file extensions
    path_lower = parsed.path.lower()
    if any(path_lower.endswith(ext) for ext in IGNORED_EXTENSIONS):
        return True
    
    # Check non-content patterns
    for pattern in NON_CONTENT_PATTERNS:
        if re.match(pattern, url_lower):
            return True
    
    # Additional heuristics
    # Skip URLs with too many query parameters (often tracking/session URLs)
    if len(parse_qs(parsed.query)) > 5:
        return True
    
    # Skip very long URLs (often auto-generated)
    if len(url) > 500:
        return True
        
    return False


class AdvancedLinkExtractor:
    """
    Advanced link extraction with intelligent filtering and categorization.
    Implements improvements from the analysis report for better link discovery.
    """
    
    def __init__(
        self, 
        respect_nofollow: bool = True,
        extract_images: bool = False,
        extract_forms: bool = False,
        domain_filter: Optional[str] = None
    ):
        self.respect_nofollow = respect_nofollow
        self.extract_images = extract_images
        self.extract_forms = extract_forms
        self.domain_filter = domain_filter
        
    def extract_comprehensive(self, base_url: str, html_content: str) -> Dict[str, Any]:
        """
        Extract comprehensive link information including categorization.
        Returns structured data about discovered links.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        base_domain = urlparse(base_url).netloc.lower()
        
        result = {
            'internal_links': [],
            'external_links': [],
            'content_links': [],
            'pagination_links': [],
            'navigation_links': [],
            'images': [],
            'forms': [],
            'social_links': [],
            'metadata': {
                'total_links': 0,
                'total_unique_domains': 0,
                'has_pagination': False,
                'has_infinite_scroll': False
            }
        }
        
        # Extract regular links
        self._extract_regular_links(soup, base_url, base_domain, result)
        
        # Extract pagination links
        self._extract_pagination_links(soup, base_url, result)
        
        # Extract images if requested
        if self.extract_images:
            self._extract_images(soup, base_url, result)
        
        # Extract forms if requested
        if self.extract_forms:
            self._extract_forms(soup, base_url, result)
            
        # Detect infinite scroll
        result['metadata']['has_infinite_scroll'] = self._detect_infinite_scroll(soup)
        
        # Update metadata
        all_links = result['internal_links'] + result['external_links']
        result['metadata']['total_links'] = len(all_links)
        
        unique_domains = set()
        for link in all_links:
            domain = urlparse(link['url']).netloc
            unique_domains.add(domain)
        result['metadata']['total_unique_domains'] = len(unique_domains)
        
        return result
    
    def _extract_regular_links(self, soup: BeautifulSoup, base_url: str, base_domain: str, result: Dict):
        """Extract and categorize regular <a> tag links"""
        for a_tag in soup.find_all('a', href=True):
            # Respect nofollow
            if self.respect_nofollow and self._has_nofollow(a_tag):
                continue
                
            href = a_tag['href']
            absolute_url = urljoin(base_url, href)
            
            # Skip invalid URLs
            if not self._is_valid_url(absolute_url):
                continue
                
            # Extract link metadata
            link_info = {
                'url': absolute_url,
                'text': a_tag.get_text(strip=True)[:200],  # Truncate long text
                'title': a_tag.get('title', ''),
                'rel': a_tag.get('rel', []),
                'class': a_tag.get('class', []),
                'is_internal': urlparse(absolute_url).netloc.lower() == base_domain
            }
            
            # Categorize link
            self._categorize_link(link_info, a_tag, result)
    
    def _categorize_link(self, link_info: Dict, a_tag, result: Dict):
        """Categorize link based on various heuristics"""
        url = link_info['url']
        text = link_info['text'].lower()
        classes = ' '.join(link_info['class']).lower()
        
        # Check if internal or external
        if link_info['is_internal']:
            result['internal_links'].append(link_info)
            
            # Further categorize internal links
            if self._is_content_link(url, text, classes):
                result['content_links'].append(link_info)
            elif self._is_navigation_link(url, text, classes):
                result['navigation_links'].append(link_info)
        else:
            result['external_links'].append(link_info)
            
            # Check for social media links
            if self._is_social_link(url):
                result['social_links'].append(link_info)
    
    def _extract_pagination_links(self, soup: BeautifulSoup, base_url: str, result: Dict):
        """Extract pagination-specific links with intelligent detection"""
        pagination_indicators = [
            'next', 'previous', 'prev', 'page', 'more',
            'nästa', 'föregående', 'sida', 'mer'  # Swedish
        ]
        
        pagination_selectors = [
            'a[rel="next"]',
            'a[rel="prev"]', 
            'a[rel="previous"]',
            '.pagination a',
            '.pager a',
            '.page-numbers a',
            'nav a'
        ]
        
        for selector in pagination_selectors:
            for a_tag in soup.select(selector):
                if not a_tag.get('href'):
                    continue
                    
                absolute_url = urljoin(base_url, a_tag['href'])
                if not self._is_valid_url(absolute_url):
                    continue
                
                link_text = a_tag.get_text(strip=True).lower()
                
                # Check if this looks like pagination
                is_pagination = any(indicator in link_text for indicator in pagination_indicators)
                is_pagination = is_pagination or any(indicator in ' '.join(a_tag.get('class', [])).lower() 
                                                   for indicator in pagination_indicators)
                
                if is_pagination:
                    pagination_info = {
                        'url': absolute_url,
                        'text': a_tag.get_text(strip=True),
                        'type': self._classify_pagination_type(link_text),
                        'rel': a_tag.get('rel', [])
                    }
                    result['pagination_links'].append(pagination_info)
                    result['metadata']['has_pagination'] = True
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str, result: Dict):
        """Extract image links for download functionality"""
        for img_tag in soup.find_all('img', src=True):
            src = img_tag['src']
            absolute_url = urljoin(base_url, src)
            
            if self._is_valid_image_url(absolute_url):
                image_info = {
                    'url': absolute_url,
                    'alt': img_tag.get('alt', ''),
                    'title': img_tag.get('title', ''),
                    'width': img_tag.get('width'),
                    'height': img_tag.get('height')
                }
                result['images'].append(image_info)
    
    def _extract_forms(self, soup: BeautifulSoup, base_url: str, result: Dict):
        """Extract form information for form flow analysis"""
        for form_tag in soup.find_all('form'):
            action = form_tag.get('action', '')
            if action:
                action_url = urljoin(base_url, action)
            else:
                action_url = base_url
                
            form_info = {
                'action_url': action_url,
                'method': form_tag.get('method', 'get').lower(),
                'fields': [],
                'has_file_upload': False
            }
            
            # Extract form fields
            for input_tag in form_tag.find_all(['input', 'select', 'textarea']):
                field_info = {
                    'name': input_tag.get('name', ''),
                    'type': input_tag.get('type', 'text'),
                    'required': input_tag.has_attr('required'),
                    'placeholder': input_tag.get('placeholder', '')
                }
                
                if field_info['type'] == 'file':
                    form_info['has_file_upload'] = True
                    
                form_info['fields'].append(field_info)
                
            result['forms'].append(form_info)
    
    def _detect_infinite_scroll(self, soup: BeautifulSoup) -> bool:
        """Detect if page has infinite scroll functionality"""
        infinite_scroll_indicators = [
            'infinite-scroll',
            'endless-scroll',
            'auto-load',
            'lazy-load',
            'load-more',
            'scroll-load'
        ]
        
        # Check for common infinite scroll classes or IDs
        for indicator in infinite_scroll_indicators:
            if soup.find(class_=indicator) or soup.find(id=indicator):
                return True
                
        # Check for load more buttons
        load_more_texts = ['load more', 'show more', 'see more', 'visa mer', 'ladda mer']
        for button in soup.find_all(['button', 'a']):
            text = button.get_text(strip=True).lower()
            if any(phrase in text for phrase in load_more_texts):
                return True
                
        # Check for JavaScript patterns
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                script_content = script.string.lower()
                if 'infinite' in script_content and 'scroll' in script_content:
                    return True
                if 'onscroll' in script_content or 'scroll' in script_content:
                    return True
                    
        return False
    
    def _has_nofollow(self, a_tag) -> bool:
        """Check if link has nofollow attribute"""
        rel = a_tag.get('rel')
        return rel and ('nofollow' in rel or 'noindex' in rel)
    
    def _is_valid_url(self, url: str) -> bool:
        """Enhanced URL validation"""
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ['http', 'https']:
                return False
            if not parsed.netloc:
                return False
            return not _should_ignore_url(url)
        except:
            return False
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Check if URL is a valid image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp'}
        path = urlparse(url).path.lower()
        return any(path.endswith(ext) for ext in image_extensions)
    
    def _is_content_link(self, url: str, text: str, classes: str) -> bool:
        """Determine if link likely leads to content"""
        # Check URL patterns
        for pattern in CONTENT_PATTERNS:
            if re.match(pattern, url.lower()):
                return True
        
        # Check text content
        content_keywords = [
            'read more', 'continue reading', 'full article', 'details',
            'läs mer', 'fortsätt läsa', 'detaljer'  # Swedish
        ]
        
        return any(keyword in text for keyword in content_keywords)
    
    def _is_navigation_link(self, url: str, text: str, classes: str) -> bool:
        """Determine if link is navigation"""
        nav_keywords = [
            'home', 'about', 'contact', 'menu', 'nav',
            'hem', 'om', 'kontakt', 'meny'  # Swedish
        ]
        
        nav_classes = ['nav', 'menu', 'navigation', 'header', 'footer']
        
        return (any(keyword in text for keyword in nav_keywords) or
                any(nav_class in classes for nav_class in nav_classes))
    
    def _is_social_link(self, url: str) -> bool:
        """Determine if link is to social media"""
        social_domains = [
            'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
            'youtube.com', 'tiktok.com', 'snapchat.com', 'pinterest.com'
        ]
        
        domain = urlparse(url).netloc.lower()
        return any(social_domain in domain for social_domain in social_domains)
    
    def _classify_pagination_type(self, text: str) -> str:
        """Classify pagination link type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['next', 'nästa', '>']):
            return 'next'
        elif any(word in text_lower for word in ['prev', 'previous', 'föregående', '<']):
            return 'previous'
        elif any(word in text_lower for word in ['first', 'första']):
            return 'first'
        elif any(word in text_lower for word in ['last', 'sista']):
            return 'last'
        elif text_lower.isdigit():
            return 'page_number'
        else:
            return 'other'


class SmartLinkFilter:
    """
    Intelligent link filtering system that learns from crawling patterns.
    Implements ML-based filtering as suggested in the analysis report.
    """
    
    def __init__(self):
        self.link_stats = {}
        self.domain_patterns = {}
        self.successful_patterns = set()
        self.failed_patterns = set()
    
    def should_crawl(self, url: str, context: Dict = None) -> Tuple[bool, str]:
        """
        Determine if URL should be crawled based on learned patterns.
        Returns (should_crawl, reason)
        """
        domain = urlparse(url).netloc.lower()
        
        # Basic filtering first
        if _should_ignore_url(url):
            return False, "matches_ignore_pattern"
        
        # Check against successful patterns
        if self._matches_successful_pattern(url):
            return True, "matches_successful_pattern"
        
        # Check against failed patterns
        if self._matches_failed_pattern(url):
            return False, "matches_failed_pattern"
        
        # Domain-specific intelligence
        if domain in self.domain_patterns:
            pattern_info = self.domain_patterns[domain]
            if self._url_matches_domain_pattern(url, pattern_info):
                confidence = pattern_info.get('success_rate', 0.5)
                return confidence > 0.7, f"domain_pattern_confidence_{confidence:.2f}"
        
        # Default to crawl with monitoring
        return True, "default_allow"
    
    def record_crawl_result(self, url: str, success: bool, content_quality: float = 0.5):
        """Record crawl result for learning"""
        domain = urlparse(url).netloc.lower()
        
        # Update link statistics
        if url not in self.link_stats:
            self.link_stats[url] = {
                'attempts': 0,
                'successes': 0,
                'avg_quality': 0.0
            }
        
        stats = self.link_stats[url]
        stats['attempts'] += 1
        if success:
            stats['successes'] += 1
            stats['avg_quality'] = (stats['avg_quality'] + content_quality) / 2
        
        # Learn patterns
        self._learn_url_pattern(url, success, content_quality)
        
        # Update domain patterns
        if domain not in self.domain_patterns:
            self.domain_patterns[domain] = {
                'total_crawls': 0,
                'successful_crawls': 0,
                'patterns': {}
            }
        
        domain_info = self.domain_patterns[domain]
        domain_info['total_crawls'] += 1
        if success:
            domain_info['successful_crawls'] += 1
        
        domain_info['success_rate'] = domain_info['successful_crawls'] / domain_info['total_crawls']
    
    def _learn_url_pattern(self, url: str, success: bool, quality: float):
        """Learn URL patterns from crawling results"""
        parsed = urlparse(url)
        
        # Extract pattern components
        path_segments = [seg for seg in parsed.path.split('/') if seg]
        query_params = list(parse_qs(parsed.query).keys())
        
        # Create pattern signature
        pattern_components = []
        
        # Path-based patterns
        if len(path_segments) > 0:
            # First segment pattern
            pattern_components.append(f"first_segment:{path_segments[0]}")
            
            # Path depth pattern
            pattern_components.append(f"depth:{len(path_segments)}")
            
            # Numeric segments (often IDs)
            numeric_segments = sum(1 for seg in path_segments if seg.isdigit())
            if numeric_segments > 0:
                pattern_components.append(f"numeric_segments:{numeric_segments}")
        
        # Query parameter patterns
        if query_params:
            pattern_components.append(f"has_params:{len(query_params)}")
            for param in query_params[:3]:  # Top 3 params
                pattern_components.append(f"param:{param}")
        
        # File extension pattern
        if '.' in parsed.path:
            ext = parsed.path.split('.')[-1].lower()
            pattern_components.append(f"ext:{ext}")
        
        pattern = "|".join(pattern_components)
        
        # Record pattern success/failure
        if success and quality > 0.7:
            self.successful_patterns.add(pattern)
        elif not success or quality < 0.3:
            self.failed_patterns.add(pattern)
    
    def _matches_successful_pattern(self, url: str) -> bool:
        """Check if URL matches a known successful pattern"""
        # Implementation would check against learned patterns
        return False  # Simplified for now
    
    def _matches_failed_pattern(self, url: str) -> bool:
        """Check if URL matches a known failed pattern"""
        # Implementation would check against learned failed patterns
        return False  # Simplified for now
    
    def _url_matches_domain_pattern(self, url: str, pattern_info: Dict) -> bool:
        """Check if URL matches domain-specific patterns"""
        return pattern_info.get('success_rate', 0) > 0.5
    
    def get_crawl_priority(self, url: str) -> float:
        """Calculate crawl priority based on learned patterns"""
        if url in self.link_stats:
            stats = self.link_stats[url]
            if stats['attempts'] > 0:
                success_rate = stats['successes'] / stats['attempts']
                return success_rate * stats['avg_quality']
        
        # Default priority for new URLs
        return 0.5


class LinkExtractor:
    """Object-oriented wrapper for link extraction functionality."""
    
    def __init__(self, respect_nofollow: bool = True):
        self.respect_nofollow = respect_nofollow
        self.advanced_extractor = AdvancedLinkExtractor(respect_nofollow=respect_nofollow)
        self.smart_filter = SmartLinkFilter()
    
    def extract(self, base_url: str, html_content: str) -> Set[str]:
        """Basic link extraction using the enhanced extract_links function"""
        return extract_links(base_url, html_content, self.respect_nofollow)
    
    def extract_comprehensive(self, base_url: str, html_content: str) -> Dict[str, Any]:
        """Extract comprehensive link information with categorization"""
        return self.advanced_extractor.extract_comprehensive(base_url, html_content)
    
    def extract_with_filtering(self, base_url: str, html_content: str) -> Dict[str, List[str]]:
        """Extract links with intelligent filtering applied"""
        comprehensive_data = self.extract_comprehensive(base_url, html_content)
        
        filtered_results = {
            'high_priority': [],
            'medium_priority': [],
            'low_priority': [],
            'filtered_out': []
        }
        
        # Apply smart filtering to internal links
        for link_info in comprehensive_data['internal_links']:
            url = link_info['url']
            should_crawl, reason = self.smart_filter.should_crawl(url, link_info)
            
            if should_crawl:
                priority = self.smart_filter.get_crawl_priority(url)
                if priority > 0.7:
                    filtered_results['high_priority'].append(url)
                elif priority > 0.4:
                    filtered_results['medium_priority'].append(url)
                else:
                    filtered_results['low_priority'].append(url)
            else:
                filtered_results['filtered_out'].append(url)
        
        return filtered_results
    
    def record_crawl_result(self, url: str, success: bool, content_quality: float = 0.5):
        """Record crawl result for learning"""
        self.smart_filter.record_crawl_result(url, success, content_quality)
    
    def extract_from_url(self, url: str) -> Set[str]:
        """Extract links by fetching content from URL."""
        # This would need HTTP client implementation
        # For now, just return empty set
        return set()


class AjaxLinkExtractor:
    """
    Specialized extractor for AJAX and dynamic content links.
    Implements advanced analysis recommendations for SPA support.
    """
    
    def __init__(self):
        self.api_patterns = [
            r'.*/api/.*',
            r'.*/json/.*',
            r'.*/ajax/.*',
            r'.*\.json$',
            r'.*\.xml$'
        ]
    
    def extract_ajax_endpoints(self, html_content: str, base_url: str) -> List[Dict]:
        """Extract potential AJAX endpoints from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        endpoints = []
        
        # Extract from script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                endpoints.extend(self._extract_from_script(script.string, base_url))
        
        # Extract from data attributes
        for elem in soup.find_all(attrs={'data-url': True}):
            data_url = elem.get('data-url')
            if data_url:
                absolute_url = urljoin(base_url, data_url)
                endpoints.append({
                    'url': absolute_url,
                    'type': 'data_attribute',
                    'method': 'GET',
                    'element': elem.name
                })
        
        # Extract from form actions that look like API endpoints
        forms = soup.find_all('form', action=True)
        for form in forms:
            action = form['action']
            absolute_url = urljoin(base_url, action)
            
            if any(re.match(pattern, absolute_url.lower()) for pattern in self.api_patterns):
                endpoints.append({
                    'url': absolute_url,
                    'type': 'api_form',
                    'method': form.get('method', 'POST').upper(),
                    'element': 'form'
                })
        
        return endpoints
    
    def _extract_from_script(self, script_content: str, base_url: str) -> List[Dict]:
        """Extract URLs from JavaScript code"""
        endpoints = []
        
        # Common patterns for AJAX URLs in JavaScript
        url_patterns = [
            r'["\']([^"\']*(?:api|ajax|json)[^"\']*)["\']',  # API/AJAX/JSON paths
            r'fetch\(["\']([^"\']+)["\']',  # fetch() calls
            r'\.ajax\([^{]*url:\s*["\']([^"\']+)["\']',  # jQuery AJAX
            r'XMLHttpRequest.*["\']([^"\']*(?:api|json)[^"\']*)["\']',  # XHR
        ]
        
        for pattern in url_patterns:
            matches = re.finditer(pattern, script_content, re.IGNORECASE)
            for match in matches:
                url = match.group(1)
                if url and not url.startswith('#') and not url.startswith('javascript:'):
                    absolute_url = urljoin(base_url, url)
                    endpoints.append({
                        'url': absolute_url,
                        'type': 'javascript',
                        'method': 'GET',  # Default, could be enhanced
                        'element': 'script'
                    })
        
        return endpoints
    
    def extract_spa_routes(self, html_content: str, base_url: str) -> List[Dict]:
        """Extract Single Page Application routes"""
        soup = BeautifulSoup(html_content, 'html.parser')
        routes = []
        
        # Look for router configurations in scripts
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # Angular routes
                angular_routes = re.finditer(
                    r'path:\s*["\']([^"\']+)["\']',
                    script.string,
                    re.IGNORECASE
                )
                for match in angular_routes:
                    route = match.group(1)
                    if route and not route.startswith('*'):
                        full_url = urljoin(base_url, route)
                        routes.append({
                            'url': full_url,
                            'type': 'angular_route',
                            'framework': 'angular'
                        })
                
                # React Router routes
                react_routes = re.finditer(
                    r'<Route[^>]*path=["\']([^"\']+)["\']',
                    script.string,
                    re.IGNORECASE
                )
                for match in react_routes:
                    route = match.group(1)
                    if route:
                        full_url = urljoin(base_url, route)
                        routes.append({
                            'url': full_url,
                            'type': 'react_route',
                            'framework': 'react'
                        })
        
        # Look for pushState/replaceState usage
        for script in scripts:
            if script.string and ('pushState' in script.string or 'replaceState' in script.string):
                # Extract potential route patterns
                route_patterns = re.finditer(
                    r'["\']([^"\']*\/[^"\']*)["\']',
                    script.string
                )
                for match in route_patterns:
                    route = match.group(1)
                    if route and route.startswith('/') and len(route) > 1:
                        full_url = urljoin(base_url, route)
                        routes.append({
                            'url': full_url,
                            'type': 'history_api',
                            'framework': 'vanilla'
                        })
        
        return routes


# Utility functions for integration
def get_all_links(base_url: str, html_content: str, include_ajax: bool = True) -> Dict[str, Any]:
    """
    Comprehensive link extraction function that combines all extractors.
    This is the main entry point for advanced link discovery.
    """
    extractor = LinkExtractor()
    ajax_extractor = AjaxLinkExtractor()
    
    result = {
        'regular_links': extractor.extract_comprehensive(base_url, html_content),
        'ajax_endpoints': [],
        'spa_routes': []
    }
    
    if include_ajax:
        result['ajax_endpoints'] = ajax_extractor.extract_ajax_endpoints(html_content, base_url)
        result['spa_routes'] = ajax_extractor.extract_spa_routes(html_content, base_url)
    
    return result


def prioritize_links(links: List[str], smart_filter: SmartLinkFilter = None) -> Dict[str, List[str]]:
    """
    Prioritize links based on crawling intelligence.
    Returns categorized links by priority.
    """
    if not smart_filter:
        smart_filter = SmartLinkFilter()
    
    prioritized = {
        'high': [],
        'medium': [],
        'low': [],
        'skip': []
    }
    
    for link in links:
        should_crawl, reason = smart_filter.should_crawl(link)
        
        if not should_crawl:
            prioritized['skip'].append(link)
        else:
            priority = smart_filter.get_crawl_priority(link)
            if priority > 0.7:
                prioritized['high'].append(link)
            elif priority > 0.4:
                prioritized['medium'].append(link)
            else:
                prioritized['low'].append(link)
    
    return prioritized