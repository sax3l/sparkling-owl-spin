import hashlib
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "gclid", "fbclid", "msclkid", "dclid",
    "ref", "source"
}

SESSION_PARAMS = {"jsessionid", "phpsessid", "sid"}

def normalize_and_canonicalize_url(url: str) -> tuple[str, str]:
    """
    Normalizes a URL according to best practices and creates a canonical key.

    Normalization steps:
    1. Force scheme to https.
    2. Convert host to lowercase.
    3. Remove fragment (#...).
    4. Remove session and tracking query parameters.
    5. Sort remaining query parameters alphabetically.
    6. Create a canonical key using SHA-256 hash of the normalized URL.

    Returns:
        A tuple containing (normalized_url, canonical_key).
    """
    parsed = urlparse(url)

    # 1. Force scheme to https
    scheme = 'https'
    
    # 2. Convert host to lowercase
    netloc = parsed.netloc.lower()

    # 3. Remove fragment
    fragment = ''

    # 4 & 5. Filter and sort query parameters
    query_params = parse_qsl(parsed.query)
    filtered_params = [
        (k, v) for k, v in query_params 
        if k.lower() not in TRACKING_PARAMS and k.lower() not in SESSION_PARAMS
    ]
    sorted_params = sorted(filtered_params, key=lambda item: item[0])
    
    # Re-encode the query string
    query = urlencode(sorted_params)

    # Reconstruct the URL
    normalized_url = urlunparse((
        scheme,
        netloc,
        parsed.path,
        parsed.params,
        query,
        fragment
    ))

    # 6. Create canonical key
    canonical_key = hashlib.sha256(normalized_url.encode('utf-8')).hexdigest()

    return normalized_url, canonical_key