"""
Advanced Requests-IP-Rotator Integration for Ultimate Scraping System

Integrerar requests-ip-rotator-funktionalitet med våra befintliga stealth-system
för att skapa avancerad IP-rotation via AWS API Gateway med intelligenta
strategier för proxy-management och fingerprint-konsistens.

Baserat på: https://github.com/Ge0rg3/requests-ip-rotator
"""

import asyncio
import logging
import time
import json
import random
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import concurrent.futures
import ipaddress

try:
    from requests_ip_rotator import ApiGateway, DEFAULT_REGIONS, EXTRA_REGIONS, ALL_REGIONS
    import requests
    import boto3
    REQUESTS_IP_ROTATOR_AVAILABLE = True
except ImportError:
    REQUESTS_IP_ROTATOR_AVAILABLE = False
    logging.warning("Requests-IP-Rotator not available - IP rotation disabled")

# Import våra stealth-system
try:
    from enhanced_stealth_integration import EnhancedStealthManager, EnhancedStealthConfig
    STEALTH_INTEGRATION_AVAILABLE = True
except ImportError:
    STEALTH_INTEGRATION_AVAILABLE = False

try:
    from advanced_fake_useragent_integration import AdvancedUserAgentManager, UserAgentData
    FAKE_USERAGENT_INTEGRATION_AVAILABLE = True
except ImportError:
    FAKE_USERAGENT_INTEGRATION_AVAILABLE = False

# Fallback proxy providers (för när AWS inte är tillgängligt)
FALLBACK_PROXY_PROVIDERS = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "socks5://proxy3.example.com:1080"
]

@dataclass
class IPRotationConfig:
    """Konfiguration för Advanced IP-Rotation Integration"""
    
    # AWS Konfiguration
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    regions: List[str] = field(default_factory=lambda: DEFAULT_REGIONS.copy())
    
    # Rotation-strategier
    rotation_strategy: str = "random"  # random, sequential, round_robin, weighted
    rotation_interval: int = 50  # Requests mellan IP-rotations
    ip_persistence: bool = False  # Håll samma IP per session
    
    # Performance-inställningar
    max_concurrent_gateways: int = 10
    gateway_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    # Fallback-inställningar
    enable_fallback_proxies: bool = True
    fallback_proxies: List[str] = field(default_factory=lambda: FALLBACK_PROXY_PROVIDERS.copy())
    
    # Fingerprint-konsistens
    maintain_ip_fingerprint_consistency: bool = True
    ip_geolocation_consistency: bool = True
    
    # Monitoring och logging
    log_ip_changes: bool = True
    track_ip_performance: bool = True
    ip_blacklist_enabled: bool = True
    
    # Advanced-inställningar
    custom_x_forwarded_for: bool = True
    randomize_x_forwarded_for: bool = True
    clean_headers: bool = True

@dataclass
class IPRotationData:
    """Data för en IP-rotation session"""
    
    current_ip: str
    region: str
    endpoint: str
    gateway_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    requests_made: int = 0
    success_rate: float = 100.0
    avg_response_time: float = 0.0
    last_used: float = field(default_factory=time.time)
    performance_score: float = 100.0
    blacklisted: bool = False
    geolocation: Dict[str, Any] = field(default_factory=dict)


class AdvancedIPRotationManager:
    """
    Avancerad manager för IP-rotation med AWS API Gateway och stealth integration
    """
    
    def __init__(self, site_url: str, config: Optional[IPRotationConfig] = None):
        self.site_url = site_url.rstrip('/')
        self.config = config or IPRotationConfig()
        self.gateways = {}
        self.active_sessions = {}
        self.rotation_counter = 0
        self.current_session_ip = None
        self.ip_performance_data = {}
        self.blacklisted_ips = set()
        
        # Integration managers
        self.stealth_manager = None
        self.ua_manager = None
        
        # Statistik
        self.stats = {
            'gateways_created': 0,
            'rotations_performed': 0,
            'requests_through_rotation': 0,
            'fallback_used': 0,
            'ip_blacklisted': 0,
            'avg_response_time': 0.0,
            'total_execution_time': 0.0,
            'success_rate': 100.0
        }
        
        # Initialisera integrations
        if STEALTH_INTEGRATION_AVAILABLE:
            self.stealth_manager = EnhancedStealthManager()
            
        if FAKE_USERAGENT_INTEGRATION_AVAILABLE:
            self.ua_manager = AdvancedUserAgentManager()
            
        logging.info(f"Advanced IP Rotation Manager initialized for {self.site_url}")
        
    async def initialize_gateways(self, force_recreate: bool = False) -> Dict[str, Any]:
        """Initialisera AWS API Gateways för IP-rotation"""
        
        if not REQUESTS_IP_ROTATOR_AVAILABLE:
            logging.warning("Requests-IP-Rotator not available, using fallback proxies")
            return self._initialize_fallback_proxies()
            
        try:
            # Skapa API Gateway för varje region
            gateway_results = {}
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_concurrent_gateways) as executor:
                futures = {}
                
                for region in self.config.regions:
                    future = executor.submit(
                        self._create_gateway_for_region,
                        region, 
                        force_recreate
                    )
                    futures[future] = region
                    
                # Samla resultat
                for future in concurrent.futures.as_completed(futures):
                    region = futures[future]
                    try:
                        result = future.result()
                        if result['success']:
                            gateway_results[region] = result
                            self.stats['gateways_created'] += 1
                        else:
                            logging.warning(f"Failed to create gateway in {region}: {result.get('error', 'Unknown error')}")
                    except Exception as e:
                        logging.error(f"Exception creating gateway in {region}: {e}")
                        
            if gateway_results:
                self.gateways = gateway_results
                logging.info(f"Successfully initialized {len(gateway_results)} gateways")
                return {
                    'success': True,
                    'gateways_created': len(gateway_results),
                    'regions': list(gateway_results.keys())
                }
            else:
                logging.warning("No gateways could be created, falling back to proxy providers")
                return self._initialize_fallback_proxies()
                
        except Exception as e:
            logging.error(f"Failed to initialize gateways: {e}")
            return self._initialize_fallback_proxies()
            
    def _create_gateway_for_region(self, region: str, force_recreate: bool = False) -> Dict[str, Any]:
        """Skapa API Gateway för en specifik region"""
        
        try:
            gateway = ApiGateway(
                self.site_url,
                regions=[region],
                access_key_id=self.config.aws_access_key_id,
                access_key_secret=self.config.aws_secret_access_key,
                verbose=False
            )
            
            endpoints = gateway.start(force=force_recreate)
            
            if endpoints:
                return {
                    'success': True,
                    'gateway': gateway,
                    'endpoints': endpoints,
                    'region': region
                }
            else:
                return {
                    'success': False,
                    'error': 'No endpoints created',
                    'region': region
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'region': region
            }
            
    def _initialize_fallback_proxies(self) -> Dict[str, Any]:
        """Initialisera fallback proxy providers"""
        
        if not self.config.enable_fallback_proxies:
            return {'success': False, 'error': 'Fallback proxies disabled'}
            
        active_proxies = []
        
        # Test varje proxy för tillgänglighet
        for proxy in self.config.fallback_proxies:
            try:
                # Quick test av proxy
                test_response = requests.get(
                    "http://httpbin.org/ip",
                    proxies={'http': proxy, 'https': proxy},
                    timeout=5
                )
                if test_response.ok:
                    active_proxies.append(proxy)
            except Exception as e:
                logging.warning(f"Fallback proxy {proxy} not available: {e}")
                
        if active_proxies:
            self.fallback_proxies = active_proxies
            self.stats['fallback_used'] = len(active_proxies)
            logging.info(f"Initialized {len(active_proxies)} fallback proxies")
            return {
                'success': True,
                'fallback_mode': True,
                'active_proxies': len(active_proxies)
            }
        else:
            return {
                'success': False,
                'error': 'No fallback proxies available'
            }
            
    def get_rotated_session(self, force_rotation: bool = False) -> requests.Session:
        """Hämta en requests session med roterad IP"""
        
        # Session persistence check
        if (self.config.ip_persistence and 
            self.current_session_ip and 
            not force_rotation):
            return self._get_session_for_ip(self.current_session_ip)
            
        # Rotation strategy check
        if (self.rotation_counter >= self.config.rotation_interval or 
            force_rotation):
            self._perform_ip_rotation()
            
        # Få aktuell IP-data
        ip_data = self._select_optimal_ip()
        
        if not ip_data:
            raise Exception("No IP addresses available for rotation")
            
        # Skapa session
        session = self._create_session_for_ip(ip_data)
        
        # Uppdatera statistik
        self.rotation_counter += 1
        self.stats['requests_through_rotation'] += 1
        
        return session
        
    def _perform_ip_rotation(self):
        """Utför IP-rotation"""
        
        self.rotation_counter = 0
        self.current_session_ip = None
        self.stats['rotations_performed'] += 1
        
        # Rensa gamla performance data
        self._cleanup_old_performance_data()
        
        if self.config.log_ip_changes:
            logging.info("IP rotation performed")
            
    def _select_optimal_ip(self) -> Optional[IPRotationData]:
        """Välj optimal IP baserat på strategi och prestanda"""
        
        available_ips = self._get_available_ips()
        
        if not available_ips:
            return None
            
        # Filtrera blacklistade IPs
        if self.config.ip_blacklist_enabled:
            available_ips = [ip for ip in available_ips if not ip.blacklisted]
            
        if not available_ips:
            logging.warning("All IPs are blacklisted, clearing blacklist")
            self._clear_blacklist()
            available_ips = self._get_available_ips()
            
        # Välj baserat på strategi
        if self.config.rotation_strategy == "random":
            selected_ip = random.choice(available_ips)
        elif self.config.rotation_strategy == "sequential":
            selected_ip = available_ips[self.rotation_counter % len(available_ips)]
        elif self.config.rotation_strategy == "weighted":
            selected_ip = self._select_weighted_ip(available_ips)
        else:
            selected_ip = available_ips[0]
            
        # Uppdatera usage data
        selected_ip.last_used = time.time()
        selected_ip.requests_made += 1
        
        # Session persistence
        if self.config.ip_persistence:
            self.current_session_ip = selected_ip
            
        return selected_ip
        
    def _get_available_ips(self) -> List[IPRotationData]:
        """Hämta tillgängliga IP-adresser"""
        
        available_ips = []
        
        # AWS Gateway IPs
        for region, gateway_data in self.gateways.items():
            for endpoint in gateway_data.get('endpoints', []):
                ip_data = IPRotationData(
                    current_ip=self._resolve_endpoint_ip(endpoint),
                    region=region,
                    endpoint=endpoint,
                    performance_score=self._calculate_performance_score(endpoint)
                )
                available_ips.append(ip_data)
                
        # Fallback proxy IPs
        if hasattr(self, 'fallback_proxies'):
            for proxy in self.fallback_proxies:
                ip_data = IPRotationData(
                    current_ip=self._extract_proxy_ip(proxy),
                    region="fallback",
                    endpoint=proxy,
                    performance_score=50.0  # Lower score for fallbacks
                )
                available_ips.append(ip_data)
                
        return available_ips
        
    def _resolve_endpoint_ip(self, endpoint: str) -> str:
        """Resolva endpoint till IP-adress"""
        try:
            import socket
            ip = socket.gethostbyname(endpoint.split('.')[0])
            return ip
        except Exception:
            return endpoint  # Fallback till endpoint name
            
    def _extract_proxy_ip(self, proxy_url: str) -> str:
        """Extrahera IP från proxy URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(proxy_url)
            return parsed.hostname or "unknown"
        except Exception:
            return "fallback-proxy"
            
    def _select_weighted_ip(self, available_ips: List[IPRotationData]) -> IPRotationData:
        """Välj IP baserat på viktad prestanda"""
        
        # Beräkna vikter baserat på performance score
        weights = [ip.performance_score for ip in available_ips]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return random.choice(available_ips)
            
        # Viktad slumpmässig selection
        r = random.uniform(0, total_weight)
        upto = 0
        for i, weight in enumerate(weights):
            if upto + weight >= r:
                return available_ips[i]
            upto += weight
            
        return available_ips[-1]  # Fallback
        
    def _calculate_performance_score(self, endpoint: str) -> float:
        """Beräkna performance score för en endpoint"""
        
        perf_data = self.ip_performance_data.get(endpoint, {
            'response_times': [],
            'success_count': 0,
            'failure_count': 0
        })
        
        # Base score
        score = 100.0
        
        # Success rate factor
        total_requests = perf_data['success_count'] + perf_data['failure_count']
        if total_requests > 0:
            success_rate = perf_data['success_count'] / total_requests
            score *= success_rate
            
        # Response time factor
        if perf_data['response_times']:
            avg_response_time = sum(perf_data['response_times']) / len(perf_data['response_times'])
            # Penalty för långsamma endpoints
            if avg_response_time > 2.0:
                score *= 0.8
            elif avg_response_time > 1.0:
                score *= 0.9
                
        return max(score, 1.0)  # Minimum score
        
    def _create_session_for_ip(self, ip_data: IPRotationData) -> requests.Session:
        """Skapa requests session för specifik IP"""
        
        session = requests.Session()
        
        # Konfigurera session baserat på IP-typ
        if ip_data.region != "fallback":
            # AWS Gateway session
            if ip_data.region in self.gateways:
                gateway = self.gateways[ip_data.region]['gateway']
                session.mount("http://", gateway)
                session.mount("https://", gateway)
        else:
            # Proxy session
            proxy_config = {
                'http': ip_data.endpoint,
                'https': ip_data.endpoint
            }
            session.proxies.update(proxy_config)
            
        # Integrera med stealth system
        if self.stealth_manager and self.ua_manager:
            ua_data = self.ua_manager.get_random_user_agent()
            session.headers.update(ua_data.headers)
            
            # Konsistent fingerprinting för IP
            self._apply_ip_consistent_fingerprinting(session, ip_data, ua_data)
            
        # Anpassade headers
        if self.config.custom_x_forwarded_for:
            if self.config.randomize_x_forwarded_for:
                fake_ip = self._generate_fake_forwarded_ip()
                session.headers['X-Forwarded-For'] = fake_ip
                
        # Clean headers som kan avslöja automation
        if self.config.clean_headers:
            headers_to_remove = [
                'User-Agent-Automation',
                'X-Automation',
                'X-Scraper'
            ]
            for header in headers_to_remove:
                session.headers.pop(header, None)
                
        return session
        
    def _apply_ip_consistent_fingerprinting(self, 
                                          session: requests.Session, 
                                          ip_data: IPRotationData,
                                          ua_data) -> None:
        """Applicera konsistent fingerprinting för IP-adress"""
        
        if not self.config.maintain_ip_fingerprint_consistency:
            return
            
        # Generera konsistent fingerprint baserat på IP
        ip_hash = hashlib.md5(ip_data.current_ip.encode()).hexdigest()
        
        # Konsistent timezone baserat på region
        if self.config.ip_geolocation_consistency:
            timezone = self._get_timezone_for_region(ip_data.region)
            if timezone:
                session.headers['X-Timezone'] = timezone
                
        # Konsistent språk baserat på region
        language = self._get_language_for_region(ip_data.region)
        if language:
            session.headers['Accept-Language'] = language
            
    def _generate_fake_forwarded_ip(self) -> str:
        """Generera fake IP för X-Forwarded-For header"""
        
        # Generera realistisk privat IP eller publik IP
        ip_ranges = [
            (ipaddress.IPv4Network('192.168.0.0/16'), 0.3),
            (ipaddress.IPv4Network('10.0.0.0/8'), 0.2),
            (ipaddress.IPv4Network('172.16.0.0/12'), 0.1),
            (ipaddress.IPv4Network('0.0.0.0/0'), 0.4)  # Public IPs
        ]
        
        # Viktad selection
        r = random.random()
        cumulative = 0
        for network, weight in ip_ranges:
            cumulative += weight
            if r <= cumulative:
                # Generera IP i detta nätverk
                if network.network_address == ipaddress.IPv4Address('0.0.0.0'):
                    # Public IP - välj från vanliga ranges
                    public_ranges = [
                        ipaddress.IPv4Network('8.8.8.0/24'),
                        ipaddress.IPv4Network('1.1.1.0/24'),
                        ipaddress.IPv4Network('208.67.222.0/24')
                    ]
                    network = random.choice(public_ranges)
                    
                # Generera slumpmässig IP i nätverket
                host_bits = 32 - network.prefixlen
                max_hosts = (2 ** host_bits) - 1
                random_host = random.randint(1, max_hosts)
                ip = network.network_address + random_host
                return str(ip)
                
        return "192.168.1.100"  # Fallback
        
    def _get_timezone_for_region(self, region: str) -> Optional[str]:
        """Få timezone för AWS region"""
        
        region_timezones = {
            'us-east-1': 'America/New_York',
            'us-east-2': 'America/New_York', 
            'us-west-1': 'America/Los_Angeles',
            'us-west-2': 'America/Los_Angeles',
            'eu-west-1': 'Europe/Dublin',
            'eu-west-2': 'Europe/London',
            'eu-west-3': 'Europe/Paris',
            'eu-central-1': 'Europe/Berlin',
            'ca-central-1': 'America/Toronto',
            'ap-south-1': 'Asia/Mumbai',
            'ap-northeast-1': 'Asia/Tokyo',
            'ap-southeast-1': 'Asia/Singapore'
        }
        
        return region_timezones.get(region)
        
    def _get_language_for_region(self, region: str) -> Optional[str]:
        """Få språk för AWS region"""
        
        region_languages = {
            'us-east-1': 'en-US,en;q=0.9',
            'us-east-2': 'en-US,en;q=0.9',
            'us-west-1': 'en-US,en;q=0.9',
            'us-west-2': 'en-US,en;q=0.9',
            'eu-west-1': 'en-IE,en;q=0.9',
            'eu-west-2': 'en-GB,en;q=0.9',
            'eu-west-3': 'fr-FR,fr;q=0.9,en;q=0.8',
            'eu-central-1': 'de-DE,de;q=0.9,en;q=0.8',
            'ca-central-1': 'en-CA,en;q=0.9,fr-CA;q=0.8'
        }
        
        return region_languages.get(region, 'en-US,en;q=0.9')
        
    def _cleanup_old_performance_data(self):
        """Rensa gammal performance data"""
        
        current_time = time.time()
        cleanup_threshold = 3600  # 1 timme
        
        for endpoint in list(self.ip_performance_data.keys()):
            data = self.ip_performance_data[endpoint]
            if current_time - data.get('last_updated', 0) > cleanup_threshold:
                del self.ip_performance_data[endpoint]
                
    def _clear_blacklist(self):
        """Rensa IP blacklist"""
        self.blacklisted_ips.clear()
        logging.info("IP blacklist cleared")
        
    def track_request_performance(self, endpoint: str, 
                                response_time: float, 
                                success: bool):
        """Spåra prestanda för requests"""
        
        if not self.config.track_ip_performance:
            return
            
        if endpoint not in self.ip_performance_data:
            self.ip_performance_data[endpoint] = {
                'response_times': [],
                'success_count': 0,
                'failure_count': 0,
                'last_updated': time.time()
            }
            
        data = self.ip_performance_data[endpoint]
        data['response_times'].append(response_time)
        
        # Begränsa historik
        if len(data['response_times']) > 100:
            data['response_times'] = data['response_times'][-50:]
            
        if success:
            data['success_count'] += 1
        else:
            data['failure_count'] += 1
            
        data['last_updated'] = time.time()
        
        # Blacklist endpoint om prestanda är för dålig
        if self.config.ip_blacklist_enabled:
            total_requests = data['success_count'] + data['failure_count']
            if total_requests >= 10:
                success_rate = data['success_count'] / total_requests
                if success_rate < 0.5:  # Mindre än 50% success rate
                    self.blacklisted_ips.add(endpoint)
                    logging.warning(f"Blacklisted endpoint {endpoint} due to poor performance")
                    
    def get_statistics(self) -> Dict[str, Any]:
        """Hämta detaljerad statistik"""
        stats = self.stats.copy()
        
        # Lägg till live data
        stats.update({
            'active_gateways': len(self.gateways),
            'blacklisted_ips': len(self.blacklisted_ips),
            'performance_tracked_endpoints': len(self.ip_performance_data),
            'current_session_ip': self.current_session_ip.current_ip if self.current_session_ip else None,
            'available_regions': list(self.gateways.keys()),
            'fallback_proxies_active': len(getattr(self, 'fallback_proxies', []))
        })
        
        return stats
        
    async def cleanup_gateways(self):
        """Rensa upp AWS API Gateways"""
        
        if not REQUESTS_IP_ROTATOR_AVAILABLE or not self.gateways:
            return
            
        cleanup_tasks = []
        for region, gateway_data in self.gateways.items():
            if 'gateway' in gateway_data:
                task = asyncio.create_task(
                    self._cleanup_gateway_async(gateway_data['gateway'])
                )
                cleanup_tasks.append(task)
                
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks)
            logging.info(f"Cleaned up {len(cleanup_tasks)} gateways")
            
    async def _cleanup_gateway_async(self, gateway):
        """Async cleanup av en gateway"""
        try:
            gateway.shutdown()
        except Exception as e:
            logging.error(f"Error cleaning up gateway: {e}")


class StealthIPRotator:
    """
    Bekvämlighets-klass som kombinerar IP rotation med stealth
    """
    
    def __init__(self, site_url: str, **config_kwargs):
        self.site_url = site_url
        self.config = IPRotationConfig(**config_kwargs)
        self.ip_manager = AdvancedIPRotationManager(site_url, self.config)
        self.initialized = False
        
    async def initialize(self, force_recreate: bool = False) -> Dict[str, Any]:
        """Initialisera IP rotation system"""
        result = await self.ip_manager.initialize_gateways(force_recreate)
        self.initialized = result['success']
        return result
        
    def get_stealth_session(self, force_rotation: bool = False) -> requests.Session:
        """Få stealth-optimerad session med IP rotation"""
        if not self.initialized:
            raise Exception("IP Rotator not initialized. Call initialize() first.")
            
        return self.ip_manager.get_rotated_session(force_rotation)
        
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Gör request med automatisk IP rotation och stealth"""
        
        session = self.get_stealth_session()
        start_time = time.time()
        
        try:
            response = session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            
            # Spåra prestanda
            if hasattr(self.ip_manager, 'current_session_ip') and self.ip_manager.current_session_ip:
                endpoint = self.ip_manager.current_session_ip.endpoint
                self.ip_manager.track_request_performance(endpoint, response_time, response.ok)
                
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Spåra misslyckade requests
            if hasattr(self.ip_manager, 'current_session_ip') and self.ip_manager.current_session_ip:
                endpoint = self.ip_manager.current_session_ip.endpoint
                self.ip_manager.track_request_performance(endpoint, response_time, False)
                
            raise e
            
    def get_statistics(self) -> Dict[str, Any]:
        """Få statistik"""
        return self.ip_manager.get_statistics()
        
    async def cleanup(self):
        """Rensa upp resurser"""
        await self.ip_manager.cleanup_gateways()


async def demo_ip_rotation():
    """Demo av Advanced IP-Rotation Integration"""
    
    print("🌐 Advanced IP-Rotation Integration Demo")
    
    if not REQUESTS_IP_ROTATOR_AVAILABLE:
        print("❌ Requests-IP-Rotator not available - cannot run full demo")
        print("💡 Demo will show fallback proxy functionality")
        
    # Test utan AWS credentials (kommer använda fallback)
    rotator = StealthIPRotator(
        "https://httpbin.org",
        regions=["us-east-1", "eu-west-1"],  # Begränsa för demo
        enable_fallback_proxies=True,
        rotation_interval=2,
        log_ip_changes=True
    )
    
    print("🚀 Initializing IP rotation system...")
    init_result = await rotator.initialize()
    
    print(f"✅ Initialization {'successful' if init_result['success'] else 'failed'}")
    if init_result.get('fallback_mode'):
        print("🔄 Running in fallback proxy mode")
        
    if init_result['success']:
        print("\n📡 Testing rotated requests...")
        
        # Test flera requests med rotation
        for i in range(3):
            try:
                session = rotator.get_stealth_session(force_rotation=(i > 0))
                response = session.get("https://httpbin.org/ip")
                
                if response.ok:
                    data = response.json()
                    print(f"  Request {i+1}: IP = {data.get('origin', 'Unknown')}")
                else:
                    print(f"  Request {i+1}: Failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"  Request {i+1}: Error - {e}")
                
        # Test make_request method
        print("\n🎯 Testing integrated request method...")
        try:
            response = rotator.make_request("https://httpbin.org/user-agent")
            if response.ok:
                data = response.json()
                print(f"📱 User-Agent detected: {data.get('user-agent', 'Unknown')[:80]}...")
        except Exception as e:
            print(f"❌ Integrated request failed: {e}")
            
    # Statistics
    stats = rotator.get_statistics()
    print(f"\n📈 Statistics:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
            
    # Cleanup
    print("\n🧹 Cleaning up resources...")
    await rotator.cleanup()
    print("✅ Cleanup completed")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_ip_rotation())
