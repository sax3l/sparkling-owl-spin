from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Set

# Common non-document extensions to ignore during crawling
IGNORED_EXTENSIONS = {
    '.zip', '.rar', '.tar', '.gz', '.7z',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv',
    '.exe', '.dmg', '.iso'
}

def extract_links(base_url: str, html_content: str, respect_nofollow: bool = True) -> Set[str]:
    """
    Extracts all valid, crawlable, absolute HTTP/HTTPS links from HTML content.
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
        
        # Filter out links to common non-document files
        path_lower = parsed_url.path.lower()
        if any(path_lower.endswith(ext) for ext in IGNORED_EXTENSIONS):
            continue
            
        links.add(absolute_url)
            
    return links