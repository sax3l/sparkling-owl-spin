from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set

def extract_links(base_url: str, html_content: str) -> Set[str]:
    """
    Extracts all valid, absolute HTTP/HTTPS links from HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Create an absolute URL from a relative one
        absolute_url = urljoin(base_url, href)
        
        # Parse the URL to ensure it's valid and has a scheme
        parsed_url = urlparse(absolute_url)
        if parsed_url.scheme in ['http', 'https']:
            links.add(absolute_url)
            
    return links