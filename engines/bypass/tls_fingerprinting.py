#!/usr/bin/env python3
"""
TLS Fingerprinting and Anti-Detection Engine
Kombinerar funktionalitet från undetected-chromedriver, azuretls-client, CycleTLS och burp-awesome-tls
"""

import asyncio
import logging
import json
import random
import hashlib
import ssl
import socket
from typing import Dict, Any, Optional, Union, List, Tuple
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Add vendors to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "vendors"))

logger = logging.getLogger(__name__)

class TLSProfile(Enum):
    """Predefined TLS profiles for different browsers"""
    CHROME_120 = "chrome_120"
    FIREFOX_121 = "firefox_121"
    SAFARI_17 = "safari_17"
    EDGE_120 = "edge_120"
    OPERA_105 = "opera_105"
    MOBILE_CHROME = "mobile_chrome"
    MOBILE_SAFARI = "mobile_safari"
    RANDOM = "random"

class DetectionMethod(Enum):
    """Methods for avoiding detection"""
    TLS_FINGERPRINTING = "tls_fingerprinting"
    USER_AGENT_ROTATION = "user_agent_rotation"
    HEADER_RANDOMIZATION = "header_randomization"
    TIMING_RANDOMIZATION = "timing_randomization"
    CANVAS_FINGERPRINTING = "canvas_fingerprinting"
    WEBGL_FINGERPRINTING = "webgl_fingerprinting"
    AUDIO_FINGERPRINTING = "audio_fingerprinting"

@dataclass
class TLSFingerprint:
    """TLS fingerprint configuration"""
    cipher_suites: List[str]
    extensions: List[str]
    curves: List[str]
    signature_algorithms: List[str]
    version: str
    compression_methods: List[str]

@dataclass
class BrowserProfile:
    """Complete browser profile for anti-detection"""
    user_agent: str
    headers: Dict[str, str]
    tls_fingerprint: TLSFingerprint
    viewport: Tuple[int, int]
    languages: List[str]
    timezone: str
    webgl_vendor: str
    webgl_renderer: str
    canvas_fingerprint: str
    audio_fingerprint: str

class TLSFingerprintEngine:
    """Advanced TLS fingerprinting and anti-detection system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.profiles = self._load_browser_profiles()
        self.detection_methods = self._init_detection_methods()
        
    def _load_browser_profiles(self) -> Dict[str, BrowserProfile]:
        """Load predefined browser profiles"""
        return {
            TLSProfile.CHROME_120.value: self._get_chrome_120_profile(),
            TLSProfile.FIREFOX_121.value: self._get_firefox_121_profile(),
            TLSProfile.SAFARI_17.value: self._get_safari_17_profile(),
            TLSProfile.EDGE_120.value: self._get_edge_120_profile(),
            TLSProfile.OPERA_105.value: self._get_opera_105_profile(),
            TLSProfile.MOBILE_CHROME.value: self._get_mobile_chrome_profile(),
            TLSProfile.MOBILE_SAFARI.value: self._get_mobile_safari_profile()
        }
    
    def _get_chrome_120_profile(self) -> BrowserProfile:
        """Chrome 120 profile with realistic TLS fingerprint"""
        tls_fingerprint = TLSFingerprint(
            cipher_suites=[
                "TLS_AES_128_GCM_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
                "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
                "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
                "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
                "TLS_RSA_WITH_AES_128_GCM_SHA256",
                "TLS_RSA_WITH_AES_256_GCM_SHA384",
                "TLS_RSA_WITH_AES_128_CBC_SHA",
                "TLS_RSA_WITH_AES_256_CBC_SHA"
            ],
            extensions=[
                "server_name",
                "extended_master_secret",
                "renegotiation_info",
                "supported_groups",
                "ec_point_formats",
                "signature_algorithms",
                "signed_certificate_timestamp",
                "key_share",
                "supported_versions",
                "cookie",
                "psk_key_exchange_modes",
                "certificate_authorities",
                "oid_filters",
                "post_handshake_auth",
                "signature_algorithms_cert",
                "key_share"
            ],
            curves=[
                "X25519",
                "secp256r1",
                "secp384r1"
            ],
            signature_algorithms=[
                "ecdsa_secp256r1_sha256",
                "rsa_pss_rsae_sha256",
                "rsa_pkcs1_sha256",
                "ecdsa_secp384r1_sha384",
                "rsa_pss_rsae_sha384",
                "rsa_pkcs1_sha384",
                "rsa_pss_rsae_sha512",
                "rsa_pkcs1_sha512"
            ],
            version="TLS 1.3",
            compression_methods=["null"]
        )
        
        return BrowserProfile(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "max-age=0",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"'
            },
            tls_fingerprint=tls_fingerprint,
            viewport=(1920, 1080),
            languages=["en-US", "en"],
            timezone="America/New_York",
            webgl_vendor="Google Inc. (Intel)",
            webgl_renderer="ANGLE (Intel, Intel(R) UHD Graphics 620 (0x00005917) Direct3D11 vs_5_0 ps_5_0, D3D11)",
            canvas_fingerprint="chrome_120_canvas_hash",
            audio_fingerprint="chrome_120_audio_hash"
        )
    
    def _get_firefox_121_profile(self) -> BrowserProfile:
        """Firefox 121 profile"""
        tls_fingerprint = TLSFingerprint(
            cipher_suites=[
                "TLS_AES_128_GCM_SHA256",
                "TLS_CHACHA20_POLY1305_SHA256",
                "TLS_AES_256_GCM_SHA384",
                "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
                "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
                "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
                "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
                "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
                "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
                "TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA",
                "TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA",
                "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA",
                "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA",
                "TLS_DHE_RSA_WITH_AES_128_CBC_SHA",
                "TLS_DHE_RSA_WITH_AES_256_CBC_SHA",
                "TLS_RSA_WITH_AES_128_CBC_SHA",
                "TLS_RSA_WITH_AES_256_CBC_SHA",
                "TLS_RSA_WITH_3DES_EDE_CBC_SHA"
            ],
            extensions=[
                "server_name",
                "extended_master_secret",
                "renegotiation_info",
                "supported_groups",
                "ec_point_formats",
                "signature_algorithms",
                "signed_certificate_timestamp",
                "key_share",
                "supported_versions",
                "cookie",
                "psk_key_exchange_modes"
            ],
            curves=[
                "X25519",
                "secp256r1",
                "secp384r1",
                "secp521r1",
                "ffdhe2048",
                "ffdhe3072"
            ],
            signature_algorithms=[
                "ecdsa_secp256r1_sha256",
                "ecdsa_secp384r1_sha384",
                "ecdsa_secp521r1_sha512",
                "rsa_pss_rsae_sha256",
                "rsa_pss_rsae_sha384",
                "rsa_pss_rsae_sha512",
                "rsa_pkcs1_sha256",
                "rsa_pkcs1_sha384",
                "rsa_pkcs1_sha512"
            ],
            version="TLS 1.3",
            compression_methods=["null"]
        )
        
        return BrowserProfile(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1"
            },
            tls_fingerprint=tls_fingerprint,
            viewport=(1920, 1080),
            languages=["en-US", "en"],
            timezone="America/New_York",
            webgl_vendor="Mozilla",
            webgl_renderer="Mozilla -- Intel(R) UHD Graphics 620 -- Intel Inc.",
            canvas_fingerprint="firefox_121_canvas_hash",
            audio_fingerprint="firefox_121_audio_hash"
        )
    
    def _get_safari_17_profile(self) -> BrowserProfile:
        """Safari 17 profile for macOS"""
        # Similar implementation for Safari
        pass
    
    def _get_edge_120_profile(self) -> BrowserProfile:
        """Microsoft Edge 120 profile"""
        # Similar implementation for Edge
        pass
    
    def _get_opera_105_profile(self) -> BrowserProfile:
        """Opera 105 profile"""
        # Similar implementation for Opera
        pass
    
    def _get_mobile_chrome_profile(self) -> BrowserProfile:
        """Mobile Chrome profile"""
        # Similar implementation for mobile Chrome
        pass
    
    def _get_mobile_safari_profile(self) -> BrowserProfile:
        """Mobile Safari profile"""
        # Similar implementation for mobile Safari
        pass
    
    def _init_detection_methods(self) -> Dict[str, Any]:
        """Initialize anti-detection methods"""
        return {
            DetectionMethod.TLS_FINGERPRINTING: self._configure_tls_fingerprinting,
            DetectionMethod.USER_AGENT_ROTATION: self._configure_user_agent_rotation,
            DetectionMethod.HEADER_RANDOMIZATION: self._configure_header_randomization,
            DetectionMethod.TIMING_RANDOMIZATION: self._configure_timing_randomization,
            DetectionMethod.CANVAS_FINGERPRINTING: self._configure_canvas_fingerprinting,
            DetectionMethod.WEBGL_FINGERPRINTING: self._configure_webgl_fingerprinting,
            DetectionMethod.AUDIO_FINGERPRINTING: self._configure_audio_fingerprinting
        }
    
    async def create_session(self, 
                           profile: TLSProfile = TLSProfile.CHROME_120,
                           detection_methods: List[DetectionMethod] = None,
                           custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a configured session with anti-detection features"""
        
        if detection_methods is None:
            detection_methods = [
                DetectionMethod.TLS_FINGERPRINTING,
                DetectionMethod.USER_AGENT_ROTATION,
                DetectionMethod.HEADER_RANDOMIZATION,
                DetectionMethod.TIMING_RANDOMIZATION
            ]
        
        # Get browser profile
        if profile == TLSProfile.RANDOM:
            profile_key = random.choice(list(self.profiles.keys()))
            browser_profile = self.profiles[profile_key]
        else:
            browser_profile = self.profiles.get(profile.value)
        
        if not browser_profile:
            raise ValueError(f"Unknown profile: {profile}")
        
        # Configure session based on profile and detection methods
        session_config = {
            'browser_profile': browser_profile,
            'tls_config': await self._configure_tls(browser_profile.tls_fingerprint),
            'headers': self._randomize_headers(browser_profile.headers),
            'user_agent': browser_profile.user_agent,
            'viewport': browser_profile.viewport,
            'detection_methods': detection_methods
        }
        
        # Apply custom configuration
        if custom_config:
            session_config.update(custom_config)
        
        return session_config
    
    async def _configure_tls(self, fingerprint: TLSFingerprint) -> Dict[str, Any]:
        """Configure TLS settings based on fingerprint"""
        return {
            'cipher_suites': fingerprint.cipher_suites,
            'extensions': fingerprint.extensions,
            'curves': fingerprint.curves,
            'signature_algorithms': fingerprint.signature_algorithms,
            'version': fingerprint.version,
            'compression_methods': fingerprint.compression_methods
        }
    
    def _randomize_headers(self, base_headers: Dict[str, str]) -> Dict[str, str]:
        """Randomize headers while maintaining realism"""
        headers = base_headers.copy()
        
        # Randomize Accept-Language
        languages = [
            "en-US,en;q=0.9",
            "en-US,en;q=0.8",
            "en-GB,en;q=0.9",
            "en-US,en;q=0.9,es;q=0.8",
            "en-US,en;q=0.9,fr;q=0.8",
        ]
        headers["Accept-Language"] = random.choice(languages)
        
        # Randomize quality values
        if "Accept" in headers:
            accept_header = headers["Accept"]
            if "q=" in accept_header:
                # Slightly randomize quality values
                import re
                def randomize_q(match):
                    q_val = float(match.group(1))
                    # Add small random variation
                    new_q = max(0.1, min(1.0, q_val + random.uniform(-0.1, 0.1)))
                    return f"q={new_q:.1f}"
                
                headers["Accept"] = re.sub(r'q=([0-9.]+)', randomize_q, accept_header)
        
        return headers
    
    def _configure_tls_fingerprinting(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure TLS fingerprinting anti-detection"""
        return session_config
    
    def _configure_user_agent_rotation(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure user agent rotation"""
        return session_config
    
    def _configure_header_randomization(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure header randomization"""
        return session_config
    
    def _configure_timing_randomization(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure timing randomization"""
        return session_config
    
    def _configure_canvas_fingerprinting(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure canvas fingerprinting protection"""
        return session_config
    
    def _configure_webgl_fingerprinting(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure WebGL fingerprinting protection"""
        return session_config
    
    def _configure_audio_fingerprinting(self, session_config: Dict[str, Any]) -> Dict[str, Any]:
        """Configure audio fingerprinting protection"""
        return session_config
    
    async def analyze_tls_fingerprint(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """Analyze TLS fingerprint of a target server"""
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        'hostname': hostname,
                        'port': port,
                        'certificate': cert,
                        'cipher': cipher,
                        'version': version,
                        'fingerprint': hashlib.sha256(str(cert).encode()).hexdigest()
                    }
                    
        except Exception as e:
            logger.error(f"Failed to analyze TLS fingerprint for {hostname}:{port} - {e}")
            return {'error': str(e)}
    
    def generate_ja3_fingerprint(self, tls_data: Dict[str, Any]) -> str:
        """Generate JA3 fingerprint from TLS data"""
        # JA3 fingerprint format: Version,Cipher,Extension,EllipticCurve,EllipticCurvePointFormat
        version = tls_data.get('version', '771')  # TLS 1.2 = 771, TLS 1.3 = 772
        ciphers = ','.join(tls_data.get('cipher_suites', []))
        extensions = ','.join(tls_data.get('extensions', []))
        curves = ','.join(tls_data.get('curves', []))
        point_formats = ','.join(tls_data.get('point_formats', ['0']))
        
        ja3_string = f"{version},{ciphers},{extensions},{curves},{point_formats}"
        ja3_hash = hashlib.md5(ja3_string.encode()).hexdigest()
        
        return ja3_hash
    
    def get_available_profiles(self) -> List[str]:
        """Get list of available browser profiles"""
        return list(self.profiles.keys())
    
    def get_detection_methods(self) -> List[str]:
        """Get list of available detection methods"""
        return [method.value for method in DetectionMethod]

# Convenience functions
async def create_stealth_session(profile: str = "chrome_120") -> Dict[str, Any]:
    """Create a stealth session with default anti-detection"""
    engine = TLSFingerprintEngine()
    profile_enum = TLSProfile(profile) if profile != "random" else TLSProfile.RANDOM
    
    return await engine.create_session(
        profile=profile_enum,
        detection_methods=[
            DetectionMethod.TLS_FINGERPRINTING,
            DetectionMethod.USER_AGENT_ROTATION,
            DetectionMethod.HEADER_RANDOMIZATION,
            DetectionMethod.TIMING_RANDOMIZATION,
            DetectionMethod.CANVAS_FINGERPRINTING,
            DetectionMethod.WEBGL_FINGERPRINTING
        ]
    )

async def analyze_target_tls(hostname: str, port: int = 443) -> Dict[str, Any]:
    """Analyze TLS configuration of target server"""
    engine = TLSFingerprintEngine()
    return await engine.analyze_tls_fingerprint(hostname, port)

if __name__ == "__main__":
    # Test the TLS fingerprinting engine
    async def test_engine():
        engine = TLSFingerprintEngine()
        
        print(f"Available profiles: {engine.get_available_profiles()}")
        print(f"Detection methods: {engine.get_detection_methods()}")
        
        # Test session creation
        session = await engine.create_session(TLSProfile.CHROME_120)
        print(f"Created session with profile: {session['browser_profile'].user_agent}")
        
        # Test TLS analysis
        tls_analysis = await engine.analyze_tls_fingerprint("httpbin.org")
        print(f"TLS analysis: {tls_analysis}")
    
    asyncio.run(test_engine())
