#!/usr/bin/env python3
"""
Revolutionary Advanced OSINT & Analytics System v4.0
Comprehensive intelligence gathering, analysis, and threat assessment.

Integrates:
- CloudFlair (origin server discovery behind CDNs)
- ReconSpider-style OSINT capabilities  
- IP quality assessment and honeypot detection
- Domain intelligence and reputation analysis
- Network fingerprinting and security assessment
"""

import asyncio
import logging
import json
import time
import re
import socket
import ssl
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from urllib.parse import urlparse, urljoin
import dns.resolver
import whois
import requests
import aiohttp
import yaml
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Additional OSINT libraries
try:
    import shodan
    SHODAN_AVAILABLE = True
except ImportError:
    SHODAN_AVAILABLE = False
    
try:
    from censys.search import CensysHosts
    from censys.common.exceptions import CensysException
    CENSYS_AVAILABLE = True
except ImportError:
    CENSYS_AVAILABLE = False

try:
    import maxminddb
    MAXMIND_AVAILABLE = True
except ImportError:
    MAXMIND_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class DomainIntelligence:
    """Intelligence data for a domain"""
    domain: str
    ip_addresses: List[str] = field(default_factory=list)
    origin_servers: List[str] = field(default_factory=list)
    cdn_info: Dict[str, Any] = field(default_factory=dict)
    ssl_info: Dict[str, Any] = field(default_factory=dict)
    dns_records: Dict[str, List[str]] = field(default_factory=dict)
    whois_info: Dict[str, Any] = field(default_factory=dict)
    subdomains: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    security_headers: Dict[str, Any] = field(default_factory=dict)
    threat_indicators: List[str] = field(default_factory=list)
    reputation_score: float = 0.0
    risk_level: str = "unknown"  # low, medium, high, critical
    last_updated: float = field(default_factory=time.time)

@dataclass
class IPIntelligence:
    """Intelligence data for an IP address"""
    ip: str
    hostname: Optional[str] = None
    asn: Optional[str] = None
    organization: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    is_proxy: bool = False
    is_vpn: bool = False
    is_tor: bool = False
    is_honeypot: bool = False
    is_malicious: bool = False
    open_ports: List[int] = field(default_factory=list)
    services: Dict[int, str] = field(default_factory=dict)
    ssl_certificates: List[Dict[str, Any]] = field(default_factory=dict)
    reputation_score: float = 0.0
    threat_categories: List[str] = field(default_factory=list)
    last_seen: float = field(default_factory=time.time)

class CloudFlairAnalyzer:
    """CloudFlair-style origin server discovery"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    async def find_origin_servers(self, domain: str) -> List[str]:
        """Find origin servers behind CloudFlare/CloudFront"""
        origin_servers = []
        
        try:
            # Check if domain uses CloudFlare/CloudFront
            is_cloudflare = await self._is_behind_cloudflare(domain)
            is_cloudfront = await self._is_behind_cloudfront(domain)
            
            if not (is_cloudflare or is_cloudfront):
                logger.info(f"{domain} is not behind CloudFlare/CloudFront")
                return origin_servers
                
            logger.info(f"{domain} is behind CDN, searching for origin servers...")
            
            # Method 1: Certificate transparency search
            ct_servers = await self._search_certificate_transparency(domain)
            origin_servers.extend(ct_servers)
            
            # Method 2: DNS history search
            dns_servers = await self._search_dns_history(domain)
            origin_servers.extend(dns_servers)
            
            # Method 3: Subdomain enumeration
            subdomain_servers = await self._search_subdomains(domain)
            origin_servers.extend(subdomain_servers)
            
            # Method 4: Port scanning common hosting IPs
            hosting_servers = await self._search_hosting_ranges(domain)
            origin_servers.extend(hosting_servers)
            
            # Validate discovered servers
            validated_servers = await self._validate_origin_servers(domain, origin_servers)
            
            logger.info(f"Found {len(validated_servers)} potential origin servers for {domain}")
            return validated_servers
            
        except Exception as e:
            logger.error(f"Origin server discovery failed for {domain}: {str(e)}")
            return []
    
    async def _is_behind_cloudflare(self, domain: str) -> bool:
        """Check if domain is behind CloudFlare"""
        try:
            # Check CNAME records
            answers = dns.resolver.resolve(domain, 'CNAME')
            for answer in answers:
                if 'cloudflare' in str(answer).lower():
                    return True
                    
            # Check NS records
            answers = dns.resolver.resolve(domain, 'NS')
            for answer in answers:
                if 'cloudflare' in str(answer).lower():
                    return True
                    
            # Check IP ranges
            answers = dns.resolver.resolve(domain, 'A')
            for answer in answers:
                ip = str(answer)
                if await self._is_cloudflare_ip(ip):
                    return True
                    
        except Exception as e:
            logger.debug(f"CloudFlare check failed for {domain}: {str(e)}")
            
        return False
    
    async def _is_behind_cloudfront(self, domain: str) -> bool:
        """Check if domain is behind CloudFront"""
        try:
            # Check CNAME records
            answers = dns.resolver.resolve(domain, 'CNAME')
            for answer in answers:
                answer_str = str(answer).lower()
                if 'cloudfront' in answer_str or 'amazonaws.com' in answer_str:
                    return True
                    
        except Exception as e:
            logger.debug(f"CloudFront check failed for {domain}: {str(e)}")
            
        return False
    
    async def _is_cloudflare_ip(self, ip: str) -> bool:
        """Check if IP belongs to CloudFlare"""
        cloudflare_ranges = [
            '173.245.48.0/20', '103.21.244.0/22', '103.22.200.0/22',
            '103.31.4.0/22', '141.101.64.0/18', '108.162.192.0/18',
            '190.93.240.0/20', '188.114.96.0/20', '197.234.240.0/22',
            '198.41.128.0/17', '162.158.0.0/15', '104.16.0.0/13',
            '104.24.0.0/14', '172.64.0.0/13', '131.0.72.0/22'
        ]
        
        try:
            import ipaddress
            ip_addr = ipaddress.ip_address(ip)
            
            for range_str in cloudflare_ranges:
                network = ipaddress.ip_network(range_str)
                if ip_addr in network:
                    return True
                    
        except Exception as e:
            logger.debug(f"IP range check failed for {ip}: {str(e)}")
            
        return False
    
    async def _search_certificate_transparency(self, domain: str) -> List[str]:
        """Search certificate transparency logs for related IPs"""
        servers = []
        
        if not CENSYS_AVAILABLE:
            logger.warning("Censys not available for certificate transparency search")
            return servers
            
        try:
            api_key = self.config.get('censys_api_key')
            api_secret = self.config.get('censys_api_secret')
            
            if not (api_key and api_secret):
                logger.warning("Censys API credentials not configured")
                return servers
                
            censys = CensysHosts(api_key, api_secret)
            
            # Search for certificates containing the domain
            query = f"services.tls.certificates.leaf_data.subject.common_name:\"{domain}\""
            
            for result in censys.search(query, pages=3):  # Limit to 3 pages
                ip = result.get('ip')
                if ip and not await self._is_cloudflare_ip(ip):
                    servers.append(ip)
                    
            logger.info(f"Certificate transparency search found {len(servers)} IPs")
            
        except Exception as e:
            logger.error(f"Certificate transparency search failed: {str(e)}")
            
        return servers
    
    async def _search_dns_history(self, domain: str) -> List[str]:
        """Search DNS history for old IP addresses"""
        servers = []
        
        try:
            # Use SecurityTrails API if available
            api_key = self.config.get('securitytrails_api_key')
            if api_key:
                url = f"https://api.securitytrails.com/v1/history/{domain}/dns/a"
                headers = {'APIKEY': api_key}
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            for record in data.get('records', []):
                                for value in record.get('values', []):
                                    ip = value.get('ip')
                                    if ip and not await self._is_cloudflare_ip(ip):
                                        servers.append(ip)
                                        
            logger.info(f"DNS history search found {len(servers)} IPs")
            
        except Exception as e:
            logger.error(f"DNS history search failed: {str(e)}")
            
        return servers
    
    async def _search_subdomains(self, domain: str) -> List[str]:
        """Search subdomains for direct-connect servers"""
        servers = []
        
        try:
            # Common subdomain prefixes that might point to origin
            prefixes = [
                'direct', 'origin', 'source', 'backend', 'api', 'admin',
                'staging', 'dev', 'test', 'old', 'legacy', 'internal'
            ]
            
            for prefix in prefixes:
                subdomain = f"{prefix}.{domain}"
                try:
                    answers = dns.resolver.resolve(subdomain, 'A')
                    for answer in answers:
                        ip = str(answer)
                        if not await self._is_cloudflare_ip(ip):
                            servers.append(ip)
                            
                except dns.resolver.NXDOMAIN:
                    continue
                except Exception as e:
                    logger.debug(f"Subdomain lookup failed for {subdomain}: {str(e)}")
                    
            logger.info(f"Subdomain search found {len(servers)} IPs")
            
        except Exception as e:
            logger.error(f"Subdomain search failed: {str(e)}")
            
        return servers
    
    async def _search_hosting_ranges(self, domain: str) -> List[str]:
        """Search common hosting provider IP ranges"""
        servers = []
        
        try:
            # Get hosting provider from WHOIS
            whois_info = whois.whois(domain)
            hosting_provider = None
            
            if hasattr(whois_info, 'org') and whois_info.org:
                hosting_provider = whois_info.org.lower()
            elif hasattr(whois_info, 'registrar') and whois_info.registrar:
                hosting_provider = whois_info.registrar.lower()
                
            if hosting_provider:
                # Search Shodan for servers from same hosting provider
                if SHODAN_AVAILABLE:
                    api_key = self.config.get('shodan_api_key')
                    if api_key:
                        api = shodan.Shodan(api_key)
                        query = f"ssl.cert.subject.cn:\"{domain}\" org:\"{hosting_provider}\""
                        
                        try:
                            results = api.search(query, limit=50)
                            for result in results['matches']:
                                ip = result['ip_str']
                                if not await self._is_cloudflare_ip(ip):
                                    servers.append(ip)
                        except Exception as e:
                            logger.debug(f"Shodan search failed: {str(e)}")
                            
            logger.info(f"Hosting range search found {len(servers)} IPs")
            
        except Exception as e:
            logger.error(f"Hosting range search failed: {str(e)}")
            
        return servers
    
    async def _validate_origin_servers(self, domain: str, candidates: List[str]) -> List[str]:
        """Validate potential origin servers"""
        validated = []
        
        # Get original page content for comparison
        original_content = await self._get_page_content(f"https://{domain}")
        if not original_content:
            return validated
            
        # Test each candidate
        for ip in set(candidates):  # Remove duplicates
            try:
                # Test HTTP and HTTPS
                for scheme in ['http', 'https']:
                    url = f"{scheme}://{ip}"
                    content = await self._get_page_content(url, host_header=domain)
                    
                    if content and self._compare_content(original_content, content):
                        validated.append(ip)
                        logger.info(f"Validated origin server: {ip}")
                        break
                        
            except Exception as e:
                logger.debug(f"Validation failed for {ip}: {str(e)}")
                
        return validated
    
    async def _get_page_content(self, url: str, host_header: Optional[str] = None) -> Optional[str]:
        """Get page content with optional Host header"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if host_header:
                headers['Host'] = host_header
                
            response = self.session.get(url, headers=headers, timeout=10, verify=False)
            if response.status_code == 200:
                return response.text
                
        except Exception as e:
            logger.debug(f"Failed to get content from {url}: {str(e)}")
            
        return None
    
    def _compare_content(self, content1: str, content2: str, threshold: float = 0.8) -> bool:
        """Compare two HTML contents for similarity"""
        try:
            # Simple similarity check based on title and key elements
            from bs4 import BeautifulSoup
            
            soup1 = BeautifulSoup(content1, 'html.parser')
            soup2 = BeautifulSoup(content2, 'html.parser')
            
            # Compare titles
            title1 = soup1.find('title')
            title2 = soup2.find('title')
            
            if title1 and title2:
                if title1.get_text().strip() == title2.get_text().strip():
                    return True
                    
            # Compare meta descriptions
            desc1 = soup1.find('meta', attrs={'name': 'description'})
            desc2 = soup2.find('meta', attrs={'name': 'description'})
            
            if desc1 and desc2:
                content1_desc = desc1.get('content', '')
                content2_desc = desc2.get('content', '')
                if content1_desc and content1_desc == content2_desc:
                    return True
                    
            # Simple text similarity
            text1 = soup1.get_text()
            text2 = soup2.get_text()
            
            # Remove whitespace and compare lengths
            clean_text1 = re.sub(r'\s+', ' ', text1).strip()
            clean_text2 = re.sub(r'\s+', ' ', text2).strip()
            
            if len(clean_text1) > 0 and len(clean_text2) > 0:
                # Simple Jaccard similarity on words
                words1 = set(clean_text1.lower().split())
                words2 = set(clean_text2.lower().split())
                
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                
                if union > 0:
                    similarity = intersection / union
                    return similarity >= threshold
                    
        except Exception as e:
            logger.debug(f"Content comparison failed: {str(e)}")
            
        return False

class ThreatIntelligence:
    """Threat intelligence and reputation analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = requests.Session()
        
    async def analyze_domain(self, domain: str) -> DomainIntelligence:
        """Comprehensive domain threat analysis"""
        intel = DomainIntelligence(domain=domain)
        
        try:
            # DNS analysis
            await self._analyze_dns(domain, intel)
            
            # WHOIS analysis
            await self._analyze_whois(domain, intel)
            
            # SSL/TLS analysis
            await self._analyze_ssl(domain, intel)
            
            # Security headers analysis
            await self._analyze_security_headers(domain, intel)
            
            # Technology detection
            await self._detect_technologies(domain, intel)
            
            # Reputation analysis
            await self._analyze_reputation(domain, intel)
            
            # Calculate risk level
            intel.risk_level = self._calculate_risk_level(intel)
            intel.last_updated = time.time()
            
        except Exception as e:
            logger.error(f"Domain analysis failed for {domain}: {str(e)}")
            
        return intel
    
    async def analyze_ip(self, ip: str) -> IPIntelligence:
        """Comprehensive IP threat analysis"""
        intel = IPIntelligence(ip=ip)
        
        try:
            # Geolocation analysis
            await self._analyze_geolocation(ip, intel)
            
            # Network analysis (ASN, organization)
            await self._analyze_network(ip, intel)
            
            # Port scanning
            await self._scan_ports(ip, intel)
            
            # Proxy/VPN detection
            await self._detect_proxy_vpn(ip, intel)
            
            # Honeypot detection
            await self._detect_honeypot(ip, intel)
            
            # Threat reputation
            await self._analyze_ip_reputation(ip, intel)
            
            intel.last_seen = time.time()
            
        except Exception as e:
            logger.error(f"IP analysis failed for {ip}: {str(e)}")
            
        return intel
    
    async def _analyze_dns(self, domain: str, intel: DomainIntelligence):
        """Analyze DNS records"""
        record_types = ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                records = [str(answer) for answer in answers]
                intel.dns_records[record_type] = records
                
                if record_type == 'A':
                    intel.ip_addresses.extend(records)
                    
            except dns.resolver.NoAnswer:
                intel.dns_records[record_type] = []
            except Exception as e:
                logger.debug(f"DNS lookup failed for {domain} {record_type}: {str(e)}")
                intel.dns_records[record_type] = []
    
    async def _analyze_whois(self, domain: str, intel: DomainIntelligence):
        """Analyze WHOIS information"""
        try:
            w = whois.whois(domain)
            
            intel.whois_info = {
                'registrar': getattr(w, 'registrar', None),
                'creation_date': str(getattr(w, 'creation_date', None)),
                'expiration_date': str(getattr(w, 'expiration_date', None)),
                'updated_date': str(getattr(w, 'updated_date', None)),
                'name_servers': getattr(w, 'name_servers', []),
                'org': getattr(w, 'org', None),
                'country': getattr(w, 'country', None)
            }
            
            # Threat indicators from WHOIS
            if hasattr(w, 'creation_date') and w.creation_date:
                # Recently registered domains are higher risk
                if isinstance(w.creation_date, list):
                    creation_date = w.creation_date[0]
                else:
                    creation_date = w.creation_date
                    
                days_old = (time.time() - creation_date.timestamp()) / 86400
                if days_old < 30:
                    intel.threat_indicators.append('recently_registered')
                    
        except Exception as e:
            logger.debug(f"WHOIS lookup failed for {domain}: {str(e)}")
    
    async def _analyze_ssl(self, domain: str, intel: DomainIntelligence):
        """Analyze SSL/TLS certificate"""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    intel.ssl_info = {
                        'subject': cert.get('subject', []),
                        'issuer': cert.get('issuer', []),
                        'version': cert.get('version'),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'serial_number': cert.get('serialNumber'),
                        'subject_alt_name': cert.get('subjectAltName', [])
                    }
                    
                    # Check for self-signed certificates
                    subject = dict(cert.get('subject', []))
                    issuer = dict(cert.get('issuer', []))
                    
                    if subject.get('organizationName') == issuer.get('organizationName'):
                        intel.threat_indicators.append('self_signed_certificate')
                        
        except Exception as e:
            logger.debug(f"SSL analysis failed for {domain}: {str(e)}")
    
    async def _analyze_security_headers(self, domain: str, intel: DomainIntelligence):
        """Analyze HTTP security headers"""
        try:
            response = self.session.head(f"https://{domain}", timeout=10)
            headers = response.headers
            
            security_headers = [
                'Content-Security-Policy',
                'Strict-Transport-Security',
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection',
                'Referrer-Policy',
                'Permissions-Policy'
            ]
            
            for header in security_headers:
                intel.security_headers[header] = headers.get(header)
                
            # Score security headers
            present_headers = sum(1 for h in security_headers if headers.get(h))
            intel.security_headers['score'] = present_headers / len(security_headers)
            
            # Threat indicators
            if not headers.get('Strict-Transport-Security'):
                intel.threat_indicators.append('missing_hsts')
                
            if not headers.get('Content-Security-Policy'):
                intel.threat_indicators.append('missing_csp')
                
        except Exception as e:
            logger.debug(f"Security headers analysis failed for {domain}: {str(e)}")
    
    async def _detect_technologies(self, domain: str, intel: DomainIntelligence):
        """Detect web technologies"""
        try:
            response = self.session.get(f"https://{domain}", timeout=10)
            headers = response.headers
            content = response.text
            
            # Server detection
            server = headers.get('Server', '')
            if server:
                intel.technologies.append(f"Server: {server}")
                
            # X-Powered-By detection
            powered_by = headers.get('X-Powered-By', '')
            if powered_by:
                intel.technologies.append(f"Powered-By: {powered_by}")
                
            # Content-based detection
            tech_patterns = {
                'WordPress': r'wp-content|wp-includes|wordpress',
                'jQuery': r'jquery',
                'Bootstrap': r'bootstrap',
                'Angular': r'ng-app|angular',
                'React': r'react',
                'Vue.js': r'vue\.js'
            }
            
            for tech, pattern in tech_patterns.items():
                if re.search(pattern, content, re.IGNORECASE):
                    intel.technologies.append(tech)
                    
        except Exception as e:
            logger.debug(f"Technology detection failed for {domain}: {str(e)}")
    
    async def _analyze_reputation(self, domain: str, intel: DomainIntelligence):
        """Analyze domain reputation"""
        try:
            # VirusTotal integration
            vt_api_key = self.config.get('virustotal_api_key')
            if vt_api_key:
                url = f"https://www.virustotal.com/vtapi/v2/domain/report"
                params = {'apikey': vt_api_key, 'domain': domain}
                
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    positives = data.get('positives', 0)
                    total = data.get('total', 1)
                    
                    # Calculate reputation score (0-1, higher is better)
                    intel.reputation_score = max(0, 1 - (positives / total))
                    
                    if positives > 0:
                        intel.threat_indicators.append(f'malicious_reports_{positives}')
                        
            # Additional reputation sources can be added here
            
        except Exception as e:
            logger.debug(f"Reputation analysis failed for {domain}: {str(e)}")
    
    async def _analyze_geolocation(self, ip: str, intel: IPIntelligence):
        """Analyze IP geolocation"""
        if not MAXMIND_AVAILABLE:
            return
            
        try:
            # Use MaxMind GeoLite2 database if available
            db_path = self.config.get('maxmind_db_path')
            if db_path and Path(db_path).exists():
                with maxminddb.open_database(db_path) as reader:
                    data = reader.get(ip)
                    if data:
                        intel.country = data.get('country', {}).get('iso_code')
                        intel.city = data.get('city', {}).get('names', {}).get('en')
                        
        except Exception as e:
            logger.debug(f"Geolocation analysis failed for {ip}: {str(e)}")
    
    async def _analyze_network(self, ip: str, intel: IPIntelligence):
        """Analyze network information"""
        try:
            # Reverse DNS lookup
            try:
                intel.hostname = socket.gethostbyaddr(ip)[0]
            except socket.herror:
                pass
                
            # ASN lookup using WHOIS
            try:
                result = subprocess.run(['whois', ip], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    whois_text = result.stdout
                    
                    # Parse ASN
                    asn_match = re.search(r'AS(\d+)', whois_text)
                    if asn_match:
                        intel.asn = asn_match.group(1)
                        
                    # Parse organization
                    org_match = re.search(r'org(?:name)?:\s*(.+)', whois_text, re.IGNORECASE)
                    if org_match:
                        intel.organization = org_match.group(1).strip()
                        
            except Exception as e:
                logger.debug(f"WHOIS lookup failed for {ip}: {str(e)}")
                
        except Exception as e:
            logger.debug(f"Network analysis failed for {ip}: {str(e)}")
    
    async def _scan_ports(self, ip: str, intel: IPIntelligence):
        """Basic port scanning"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 443, 993, 995, 3389, 5432, 3306]
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((ip, port))
                
                if result == 0:
                    intel.open_ports.append(port)
                    
                    # Basic service detection
                    service = {
                        21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
                        53: 'DNS', 80: 'HTTP', 110: 'POP3', 443: 'HTTPS',
                        993: 'IMAPS', 995: 'POP3S', 3389: 'RDP',
                        5432: 'PostgreSQL', 3306: 'MySQL'
                    }.get(port, 'Unknown')
                    
                    intel.services[port] = service
                    
                sock.close()
                
            except Exception as e:
                logger.debug(f"Port scan failed for {ip}:{port}: {str(e)}")
    
    async def _detect_proxy_vpn(self, ip: str, intel: IPIntelligence):
        """Detect if IP is proxy/VPN"""
        try:
            # Check common proxy/VPN indicators
            if intel.organization:
                org_lower = intel.organization.lower()
                
                proxy_keywords = [
                    'proxy', 'vpn', 'virtual', 'private', 'network',
                    'datacenter', 'hosting', 'cloud', 'server'
                ]
                
                for keyword in proxy_keywords:
                    if keyword in org_lower:
                        if keyword in ['proxy']:
                            intel.is_proxy = True
                        elif keyword in ['vpn', 'virtual', 'private']:
                            intel.is_vpn = True
                        break
                        
            # Additional proxy detection logic can be added here
            
        except Exception as e:
            logger.debug(f"Proxy/VPN detection failed for {ip}: {str(e)}")
    
    async def _detect_honeypot(self, ip: str, intel: IPIntelligence):
        """Detect if IP is a honeypot"""
        try:
            # Simple honeypot detection based on open ports
            suspicious_combinations = [
                [21, 22, 23, 25, 53, 80, 110, 443],  # Too many services
                [23],  # Telnet (commonly used in honeypots)
            ]
            
            for combination in suspicious_combinations:
                if all(port in intel.open_ports for port in combination):
                    intel.is_honeypot = True
                    intel.threat_categories.append('honeypot')
                    break
                    
        except Exception as e:
            logger.debug(f"Honeypot detection failed for {ip}: {str(e)}")
    
    async def _analyze_ip_reputation(self, ip: str, intel: IPIntelligence):
        """Analyze IP reputation"""
        try:
            # VirusTotal IP reputation
            vt_api_key = self.config.get('virustotal_api_key')
            if vt_api_key:
                url = f"https://www.virustotal.com/vtapi/v2/ip-address/report"
                params = {'apikey': vt_api_key, 'ip': ip}
                
                response = self.session.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    
                    positives = data.get('positives', 0)
                    total = data.get('total', 1)
                    
                    intel.reputation_score = max(0, 1 - (positives / total))
                    
                    if positives > 0:
                        intel.is_malicious = True
                        intel.threat_categories.append('malicious')
                        
                    # Extract detected threats
                    detected_urls = data.get('detected_urls', [])
                    if detected_urls:
                        intel.threat_categories.append('hosting_malware')
                        
        except Exception as e:
            logger.debug(f"IP reputation analysis failed for {ip}: {str(e)}")
    
    def _calculate_risk_level(self, intel: DomainIntelligence) -> str:
        """Calculate overall risk level for domain"""
        risk_score = 0
        
        # Threat indicators scoring
        threat_weights = {
            'recently_registered': 2,
            'self_signed_certificate': 1,
            'missing_hsts': 1,
            'missing_csp': 1,
            'malicious_reports': 5
        }
        
        for indicator in intel.threat_indicators:
            for threat, weight in threat_weights.items():
                if threat in indicator:
                    risk_score += weight
                    
        # Reputation scoring
        if intel.reputation_score < 0.5:
            risk_score += 3
        elif intel.reputation_score < 0.8:
            risk_score += 1
            
        # Security headers scoring
        security_score = intel.security_headers.get('score', 1.0)
        if security_score < 0.3:
            risk_score += 2
        elif security_score < 0.6:
            risk_score += 1
            
        # Determine risk level
        if risk_score >= 7:
            return 'critical'
        elif risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'

class OSINTAnalytics:
    """Main OSINT analytics system"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.cloudflair = CloudFlairAnalyzer(self.config.get('cloudflair', {}))
        self.threat_intel = ThreatIntelligence(self.config.get('threat_intel', {}))
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            'cloudflair': {
                'censys_api_key': None,
                'censys_api_secret': None,
                'shodan_api_key': None,
                'securitytrails_api_key': None
            },
            'threat_intel': {
                'virustotal_api_key': None,
                'maxmind_db_path': None
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = yaml.safe_load(f)
                    self._deep_merge(default_config, file_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {str(e)}")
                
        return default_config
    
    def _deep_merge(self, base: dict, update: dict):
        """Deep merge dictionaries"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    async def analyze_target(self, target: str) -> Dict[str, Any]:
        """Comprehensive target analysis"""
        results = {
            'target': target,
            'timestamp': time.time(),
            'domain_intel': None,
            'ip_intel': {},
            'origin_servers': []
        }
        
        try:
            # Determine if target is domain or IP
            try:
                socket.inet_aton(target)
                is_ip = True
            except socket.error:
                is_ip = False
                
            if is_ip:
                # Analyze IP directly
                results['ip_intel'][target] = await self.threat_intel.analyze_ip(target)
            else:
                # Analyze domain
                results['domain_intel'] = await self.threat_intel.analyze_domain(target)
                
                # Analyze associated IPs
                for ip in results['domain_intel'].ip_addresses:
                    results['ip_intel'][ip] = await self.threat_intel.analyze_ip(ip)
                    
                # Find origin servers behind CDN
                origins = await self.cloudflair.find_origin_servers(target)
                results['origin_servers'] = origins
                
                # Analyze origin server IPs
                for ip in origins:
                    if ip not in results['ip_intel']:
                        results['ip_intel'][ip] = await self.threat_intel.analyze_ip(ip)
                        
        except Exception as e:
            logger.error(f"Target analysis failed for {target}: {str(e)}")
            results['error'] = str(e)
            
        return results

# Example usage and CLI interface
async def main():
    """Example usage of OSINT Analytics System"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Revolutionary Advanced OSINT & Analytics System v4.0")
    parser.add_argument("target", help="Target domain or IP to analyze")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--origin-only", action="store_true", help="Only find origin servers")
    parser.add_argument("--output", help="Output file for results")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create analytics system
    system = OSINTAnalytics(args.config)
    
    try:
        if args.origin_only:
            # Only run origin server discovery
            origins = await system.cloudflair.find_origin_servers(args.target)
            
            print(f"\n🎯 Origin Server Discovery for: {args.target}")
            if origins:
                print(f"📍 Found {len(origins)} potential origin servers:")
                for i, ip in enumerate(origins, 1):
                    print(f"   {i}. {ip}")
            else:
                print("❌ No origin servers found")
                
        else:
            # Full analysis
            results = await system.analyze_target(args.target)
            
            print(f"\n🔍 OSINT Analysis Results for: {args.target}")
            print(f"⏰ Analysis timestamp: {time.ctime(results['timestamp'])}")
            
            # Domain intelligence
            if results['domain_intel']:
                domain = results['domain_intel']
                print(f"\n🌐 Domain Intelligence:")
                print(f"   Risk Level: {domain.risk_level.upper()}")
                print(f"   Reputation Score: {domain.reputation_score:.2f}")
                print(f"   IP Addresses: {', '.join(domain.ip_addresses[:5])}")
                
                if domain.threat_indicators:
                    print(f"   ⚠️  Threat Indicators: {', '.join(domain.threat_indicators)}")
                    
                if domain.technologies:
                    print(f"   🛠️  Technologies: {', '.join(domain.technologies[:5])}")
                    
            # IP intelligence
            if results['ip_intel']:
                print(f"\n🖥️  IP Intelligence:")
                for ip, intel in results['ip_intel'].items():
                    risk_indicators = []
                    if intel.is_proxy:
                        risk_indicators.append("PROXY")
                    if intel.is_vpn:
                        risk_indicators.append("VPN") 
                    if intel.is_honeypot:
                        risk_indicators.append("HONEYPOT")
                    if intel.is_malicious:
                        risk_indicators.append("MALICIOUS")
                        
                    risk_str = f" [{', '.join(risk_indicators)}]" if risk_indicators else ""
                    print(f"   {ip}: {intel.organization or 'Unknown'} ({intel.country or 'Unknown'}){risk_str}")
                    
                    if intel.open_ports:
                        print(f"      Open Ports: {', '.join(map(str, intel.open_ports[:10]))}")
                        
            # Origin servers
            if results['origin_servers']:
                print(f"\n🎯 Origin Servers:")
                for ip in results['origin_servers']:
                    print(f"   • {ip}")
                    
            # Save results if requested
            if args.output:
                # Convert to JSON serializable format
                output_data = {
                    'target': results['target'],
                    'timestamp': results['timestamp'],
                    'domain_intel': results['domain_intel'].__dict__ if results['domain_intel'] else None,
                    'ip_intel': {ip: intel.__dict__ for ip, intel in results['ip_intel'].items()},
                    'origin_servers': results['origin_servers']
                }
                
                with open(args.output, 'w') as f:
                    json.dump(output_data, f, indent=2, default=str)
                    
                print(f"\n💾 Results saved to: {args.output}")
                
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        logger.exception("Analysis failed")

if __name__ == "__main__":
    asyncio.run(main())
