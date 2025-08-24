"""
Unit tests för SOS Proxy Pool

Testar proxy rotation, fail-over, och quality management.
"""

import pytest
import time
from unittest.mock import Mock, patch

from sos.proxy.pool import ProxyPool


class TestProxyPool:
    """Test suite för ProxyPool funktionalitet"""
    
    def test_proxy_pool_initialization(self):
        """Test skapande av proxy pool"""
        proxies = ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"]
        pool = ProxyPool(proxies)
        
        assert len(pool._proxies) == 3
        assert pool._iter is not None
        
    def test_empty_proxy_pool(self):
        """Test tom proxy pool"""
        pool = ProxyPool([])
        
        assert pool.next() is None
        assert pool._iter is None
        
    def test_proxy_rotation(self):
        """Test att proxies roteras korrekt"""
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        pool = ProxyPool(proxies)
        
        # Första anropen ska ge olika proxies
        first = pool.next()
        second = pool.next()
        third = pool.next()  # Ska rotera tillbaka till första
        
        assert first in proxies
        assert second in proxies
        assert first != second
        assert third == first  # Rotation
        
    def test_mark_bad_proxy(self):
        """Test markering av dåliga proxies"""
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        pool = ProxyPool(proxies)
        
        # Markera första proxy som dålig
        first_proxy = pool.next()
        pool.mark_bad(first_proxy, ban_seconds=1)
        
        # Nästa anrop ska skippa den dåliga proxyn
        second_proxy = pool.next()
        assert second_proxy != first_proxy
        
        # Efter ban-tiden ska proxyn vara tillgänglig igen
        time.sleep(1.1)
        available_proxy = pool.next()
        assert available_proxy == first_proxy  # Första proxyn tillgänglig igen
        
    def test_all_proxies_bad(self):
        """Test när alla proxies är markerade som dåliga"""
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        pool = ProxyPool(proxies)
        
        # Markera alla som dåliga
        for proxy in proxies:
            pool.mark_bad(proxy, ban_seconds=60)
            
        # Ska returnera None när alla är dåliga
        assert pool.next() is None
        
    def test_from_env_parsing(self):
        """Test parsing av proxy URLs från miljövariabel"""
        
        # Tom sträng
        pool = ProxyPool.from_env("")
        assert len(pool._proxies) == 0
        
        # Single proxy
        pool = ProxyPool.from_env("http://proxy1:8080")
        assert len(pool._proxies) == 1
        assert pool._proxies[0] == "http://proxy1:8080"
        
        # Flera proxies med komma-separator
        csv = "http://proxy1:8080, http://proxy2:8080 , http://proxy3:8080"
        pool = ProxyPool.from_env(csv)
        assert len(pool._proxies) == 3
        assert "http://proxy1:8080" in pool._proxies
        assert "http://proxy2:8080" in pool._proxies
        assert "http://proxy3:8080" in pool._proxies
        
        # Hantera tomma entries
        csv_with_empty = "http://proxy1:8080,,http://proxy2:8080,"
        pool = ProxyPool.from_env(csv_with_empty)
        assert len(pool._proxies) == 2
        
    def test_ban_timeout_management(self):
        """Test hantering av ban timeouts"""
        proxies = ["http://proxy1:8080"]
        pool = ProxyPool(proxies)
        
        proxy = pool.next()
        assert proxy is not None
        
        # Markera som dålig med kort ban
        pool.mark_bad(proxy, ban_seconds=0.1)
        
        # Omedelbart efter ban ska proxy inte vara tillgänglig
        assert pool.next() is None
        
        # Efter timeout ska proxy vara tillgänglig
        time.sleep(0.2)
        recovered_proxy = pool.next()
        assert recovered_proxy == proxy


class TestProxyPoolAdvanced:
    """Avancerade tester för proxy pool"""
    
    def test_concurrent_proxy_access(self):
        """Test concurrent access till proxy pool"""
        import threading
        
        proxies = ["http://proxy1:8080", "http://proxy2:8080", "http://proxy3:8080"]
        pool = ProxyPool(proxies)
        results = []
        
        def get_proxy():
            proxy = pool.next()
            results.append(proxy)
            
        # Starta flera threads samtidigt
        threads = []
        for _ in range(10):
            t = threading.Thread(target=get_proxy)
            threads.append(t)
            t.start()
            
        # Vänta på alla threads
        for t in threads:
            t.join()
            
        # Alla ska ha fått en proxy
        assert len(results) == 10
        assert all(r in proxies for r in results)
        
    def test_proxy_quality_tracking(self):
        """Test tracking av proxy kvalitet över tid"""
        proxies = ["http://fast-proxy:8080", "http://slow-proxy:8080"]
        pool = ProxyPool(proxies)
        
        # Simulera att en proxy är långsam/opålitlig
        slow_proxy = "http://slow-proxy:8080"
        
        # Markera som dålig flera gånger
        for _ in range(3):
            pool.mark_bad(slow_proxy, ban_seconds=0.1)
            time.sleep(0.2)
            
        # Den andra proxyn ska föredras
        selected_proxies = [pool.next() for _ in range(5)]
        fast_proxy_count = selected_proxies.count("http://fast-proxy:8080")
        
        # Fast proxy ska väljas oftare (även om rotation sker)
        assert fast_proxy_count >= 2
        
    def test_proxy_health_monitoring(self):
        """Test proxy health monitoring"""
        
        class HealthMonitoringProxyPool(ProxyPool):
            def __init__(self, proxies):
                super().__init__(proxies)
                self.health_stats = {}
                
            def mark_bad(self, proxy, ban_seconds=120):
                super().mark_bad(proxy, ban_seconds)
                # Tracking av failures
                if proxy not in self.health_stats:
                    self.health_stats[proxy] = 0
                self.health_stats[proxy] += 1
                
            def get_health_stats(self):
                return self.health_stats
        
        proxies = ["http://proxy1:8080", "http://proxy2:8080"]
        pool = HealthMonitoringProxyPool(proxies)
        
        # Simulera failures
        pool.mark_bad("http://proxy1:8080")
        pool.mark_bad("http://proxy1:8080")
        pool.mark_bad("http://proxy2:8080")
        
        stats = pool.get_health_stats()
        assert stats["http://proxy1:8080"] == 2
        assert stats["http://proxy2:8080"] == 1
