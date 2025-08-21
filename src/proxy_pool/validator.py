"""
Proxy validation system for ECaDP proxy pool.

Validates proxy functionality, speed, and reliability.
"""

import asyncio
import aiohttp
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class ProxyValidationResult:
    """Result of proxy validation."""
    is_valid: bool
    response_time_ms: int
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    provider: Optional[str] = None
    tested_at: datetime = None

    def __post_init__(self):
        if self.tested_at is None:
            self.tested_at = datetime.now()

class ProxyValidator:
    """Validates proxy servers for reliability and performance."""
    
    def __init__(self, timeout_seconds: int = 10, max_concurrent: int = 50):
        self.timeout_seconds = timeout_seconds
        self.max_concurrent = max_concurrent
        self.test_urls = [
            "http://httpbin.org/ip",
            "https://httpbin.org/ip", 
            "http://ip-api.com/json",
            "https://ifconfig.me/ip"
        ]
        self._session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout_seconds),
            connector=aiohttp.TCPConnector(limit=self.max_concurrent)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    async def validate_proxy(self, proxy_url: str, test_https: bool = True) -> ProxyValidationResult:
        """Validate a single proxy."""
        try:
            start_time = time.time()
            
            # Choose test URL based on HTTPS requirement
            test_url = self.test_urls[1] if test_https else self.test_urls[0]
            
            async with self._session.get(
                test_url,
                proxy=proxy_url,
                ssl=False if not test_https else None
            ) as response:
                response_time_ms = int((time.time() - start_time) * 1000)
                
                if response.status == 200:
                    response_data = await response.json()
                    ip_address = response_data.get('origin', response_data.get('ip'))
                    
                    return ProxyValidationResult(
                        is_valid=True,
                        response_time_ms=response_time_ms,
                        status_code=response.status,
                        ip_address=ip_address
                    )
                else:
                    return ProxyValidationResult(
                        is_valid=False,
                        response_time_ms=response_time_ms,
                        status_code=response.status,
                        error_message=f"HTTP {response.status}"
                    )
                    
        except asyncio.TimeoutError:
            return ProxyValidationResult(
                is_valid=False,
                response_time_ms=self.timeout_seconds * 1000,
                error_message="Timeout"
            )
        except Exception as e:
            return ProxyValidationResult(
                is_valid=False,
                response_time_ms=0,
                error_message=str(e)
            )
    
    async def validate_proxy_list(self, proxy_urls: List[str]) -> Dict[str, ProxyValidationResult]:
        """Validate multiple proxies concurrently."""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def validate_with_semaphore(proxy_url: str) -> Tuple[str, ProxyValidationResult]:
            async with semaphore:
                result = await self.validate_proxy(proxy_url)
                return proxy_url, result
        
        tasks = [validate_with_semaphore(proxy) for proxy in proxy_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        validated_proxies = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Error validating proxy: {result}")
                continue
                
            proxy_url, validation_result = result
            validated_proxies[proxy_url] = validation_result
        
        return validated_proxies
    
    async def test_proxy_anonymity(self, proxy_url: str) -> Dict[str, bool]:
        """Test proxy anonymity level."""
        try:
            # Test direct connection to get real IP
            async with self._session.get(self.test_urls[0]) as response:
                real_ip_data = await response.json()
                real_ip = real_ip_data.get('origin')
            
            # Test through proxy
            async with self._session.get(
                self.test_urls[0],
                proxy=proxy_url
            ) as response:
                proxy_ip_data = await response.json()
                proxy_ip = proxy_ip_data.get('origin')
            
            return {
                "is_anonymous": real_ip != proxy_ip,
                "real_ip": real_ip,
                "proxy_ip": proxy_ip
            }
            
        except Exception as e:
            logger.error(f"Error testing proxy anonymity: {e}")
            return {"is_anonymous": False, "error": str(e)}
    
    def calculate_reliability_score(self, validation_results: List[ProxyValidationResult]) -> float:
        """Calculate reliability score based on validation history."""
        if not validation_results:
            return 0.0
        
        total_tests = len(validation_results)
        successful_tests = sum(1 for result in validation_results if result.is_valid)
        avg_response_time = sum(
            result.response_time_ms for result in validation_results 
            if result.is_valid
        ) / max(successful_tests, 1)
        
        # Score based on success rate and response time
        success_rate = successful_tests / total_tests
        speed_score = max(0, (5000 - avg_response_time) / 5000)  # Normalize to 0-1
        
        return (success_rate * 0.7) + (speed_score * 0.3)
    
    def is_proxy_reliable(self, validation_results: List[ProxyValidationResult], 
                         min_reliability: float = 0.8) -> bool:
        """Check if proxy meets reliability threshold."""
        return self.calculate_reliability_score(validation_results) >= min_reliability

# Utility functions
async def validate_single_proxy(proxy_url: str, timeout: int = 10) -> ProxyValidationResult:
    """Convenience function to validate a single proxy."""
    async with ProxyValidator(timeout_seconds=timeout) as validator:
        return await validator.validate_proxy(proxy_url)

async def bulk_validate_proxies(proxy_urls: List[str], max_concurrent: int = 50) -> Dict[str, ProxyValidationResult]:
    """Convenience function to validate multiple proxies."""
    async with ProxyValidator(max_concurrent=max_concurrent) as validator:
        return await validator.validate_proxy_list(proxy_urls)

__all__ = [
    "ProxyValidationResult", "ProxyValidator", 
    "validate_single_proxy", "bulk_validate_proxies"
]