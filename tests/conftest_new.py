"""
Conftest.py - Delade fixtures för alla tester

För nybörjare: En fixture är som en förberedd testmiljö du kan återanvända.
Ex: en test-DB, en falsk Redis, eller en laddad mall.

GitHub Copilot förstår dessa fixtures och föreslår automatiskt rätt kod.
"""

import os
import json
import yaml
import pytest
import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# ---------- Async event loop för pytest-asyncio ----------
@pytest.fixture(scope="session")
def event_loop():
    """Skapar en event loop för async tester"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# ---------- Helpers: ladda YAML/HTML/JSON från fixtures ----------
@pytest.fixture
def load_template():
    """Laddar YAML-mallar från data/templates/"""
    def _load(name: str) -> dict:
        p = Path(__file__).parent.parent / "data" / "templates" / f"{name}.yaml"
        if not p.exists():
            # Skapa minimal mall för test om den inte finns
            return {
                "template": name,
                "url_pattern": "*/test/*",
                "fields": [
                    {
                        "name": "test_field",
                        "selector": "//div[@class='test']",
                        "attr": "text",
                        "type": "string"
                    }
                ]
            }
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    return _load

@pytest.fixture
def load_html():
    """Laddar HTML-fixtures från data/samples/html/"""
    def _load(name: str) -> str:
        p = Path(__file__).parent.parent / "data" / "samples" / "html" / f"{name}.html"
        if not p.exists():
            # Skapa minimal HTML för test om den inte finns
            return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Test</title></head>
<body><div class="test">Test content for {name}</div></body>
</html>"""
        return p.read_text(encoding="utf-8")
    return _load

@pytest.fixture
def load_json():
    """Laddar JSON-fixtures från data/samples/expected/"""
    def _load(name: str) -> dict:
        p = Path(__file__).parent.parent / "data" / "samples" / "expected" / f"{name}.json"
        if not p.exists():
            # Skapa minimal JSON för test
            return {"test": True, "name": name}
        return json.loads(p.read_text(encoding="utf-8"))
    return _load

# ---------- Fake Redis (ersätt med fakeredis i skarp test) ----------
class FakeRedis:
    """Enkel fake Redis för tester som inte behöver riktig Redis"""
    def __init__(self):
        self.store = {}
        self.sets = {}
        self.lists = {}
    
    async def get(self, k):
        return self.store.get(k)
    
    async def set(self, k, v, ex=None):
        self.store[k] = v
        return True
    
    async def delete(self, k):
        return self.store.pop(k, None) is not None
    
    async def incr(self, k, amt=1):
        self.store[k] = int(self.store.get(k, 0)) + amt
        return self.store[k]
    
    async def sadd(self, k, *values):
        if k not in self.sets:
            self.sets[k] = set()
        for v in values:
            self.sets[k].add(v)
        return len(values)
    
    async def smembers(self, k):
        return list(self.sets.get(k, set()))
    
    async def lpush(self, k, *values):
        if k not in self.lists:
            self.lists[k] = []
        for v in reversed(values):
            self.lists[k].insert(0, v)
        return len(self.lists[k])
    
    async def rpop(self, k):
        if k in self.lists and self.lists[k]:
            return self.lists[k].pop()
        return None

@pytest.fixture
async def redis_client():
    """Fake Redis client för tester"""
    return FakeRedis()

# ---------- Testkonfig (anti_bot.yml, performance-defaults.yml) ----------
@pytest.fixture
def test_config():
    """Laddar testkonfiguration med fallbacks"""
    cfg_dir = Path(__file__).parent / "fixtures" / "config"
    
    # Default anti_bot config om fil inte finns
    default_anti_bot = {
        "domains": {
            "default": {
                "transport": "http",
                "headers": {
                    "accept_language": "sv-SE,sv;q=0.9,en;q=0.8",
                    "user_agent_pool": [
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
                    ]
                },
                "delays": {"min": 0.8, "max": 2.2},
                "retry": {"max_attempts": 3, "backoff": "exponential"}
            },
            "synthetic": {
                "transport": "browser",
                "delays": {"min": 0.6, "max": 1.6},
                "retry": {"max_attempts": 2, "backoff": "linear"}
            }
        }
    }
    
    # Default performance config
    default_perf = {
        "http": {
            "concurrency_per_worker": 50,
            "connect_timeout": 8,
            "read_timeout": 15,
            "p95_latency_budget_ms": 1800
        },
        "browser": {
            "max_instances_per_node": 4,
            "per_domain_parallelism": 1,
            "navigation_timeout": 30,
            "p95_latency_budget_ms": 7000
        }
    }
    
    # Försök ladda från fil, fallback till default
    try:
        anti_bot_file = cfg_dir / "anti_bot.yml"
        if anti_bot_file.exists():
            anti_bot = yaml.safe_load(anti_bot_file.read_text(encoding="utf-8"))
        else:
            anti_bot = default_anti_bot
    except:
        anti_bot = default_anti_bot
    
    try:
        perf_file = cfg_dir / "performance-defaults.yml"
        if perf_file.exists():
            perf = yaml.safe_load(perf_file.read_text(encoding="utf-8"))
        else:
            perf = default_perf
    except:
        perf = default_perf
    
    return {
        "anti_bot": anti_bot,
        "perf": perf,
    }

# ---------- Endpoints för syntetiska sajter (via docker-compose) ----------
@pytest.fixture(scope="session")
def synthetic_hosts():
    """URL:er till syntetiska testsajter (matchar docker-compose.synthetic.yml)"""
    return {
        "static": "http://localhost:8081",
        "scroll": "http://localhost:8082", 
        "form": "http://localhost:8083",
    }

# ---------- Mock för databas ----------
@pytest.fixture
def mock_db():
    """Mock databas för tester som inte behöver riktig DB"""
    db = Mock()
    db.execute = Mock()
    db.fetchall = Mock(return_value=[])
    db.fetchone = Mock(return_value=None)
    db.commit = Mock()
    db.rollback = Mock()
    return db

# ---------- Mock för HTTP-klienter ----------
@pytest.fixture
def mock_http_client():
    """Mock HTTP-klient för tester"""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    return client

# ---------- Produktions-readiness helpers ----------
@pytest.fixture
def production_analysis_data():
    """Mock data för production readiness analys"""
    return {
        "modules": {
            "ANTI_BOT": {"files": 6, "implemented": 4, "percentage": 66.7},
            "SCRAPER": {"files": 12, "implemented": 12, "percentage": 100.0},
            "SCHEDULER": {"files": 7, "implemented": 5, "percentage": 71.4},
            "DATABASE": {"files": 3, "implemented": 3, "percentage": 100.0},
            "PROXY_POOL": {"files": 8, "implemented": 8, "percentage": 100.0},
            "CRAWLER": {"files": 4, "implemented": 4, "percentage": 100.0},
            "WEBAPP": {"files": 5, "implemented": 3, "percentage": 60.0}
        },
        "overall": {
            "total_modules": 7,
            "production_ready": 5,
            "percentage": 71.4
        }
    }

# ---------- Shared test utilities ----------
@pytest.fixture
def sample_proxy_data():
    """Sample proxy data för tester"""
    return [
        {"addr": "1.1.1.1:8080", "quality": 0.9, "country": "SE"},
        {"addr": "2.2.2.2:8080", "quality": 0.7, "country": "NO"},
        {"addr": "3.3.3.3:8080", "quality": 0.5, "country": "DK"}
    ]

@pytest.fixture
def sample_crawl_data():
    """Sample crawl data för tester"""
    return {
        "urls": [
            {"url": "http://test.com/page1", "depth": 1, "parent": None},
            {"url": "http://test.com/page2", "depth": 2, "parent": "http://test.com/page1"},
            {"url": "http://test.com/item/123", "depth": 2, "parent": "http://test.com/page1"}
        ]
    }

@pytest.fixture
def sample_scrape_result():
    """Sample scraping resultat för tester"""
    return {
        "data": {
            "registration_number": "ABC123",
            "model_year": 2021,
            "co2_wltp": 132.5,
            "make": "Volvo",
            "model": "XC60"
        },
        "dq": {
            "completeness": 0.95,
            "validity": 0.98,
            "consistency": 0.92
        },
        "metadata": {
            "url": "http://test.com/item/123",
            "template": "vehicle_detail_v3",
            "run_id": "test-run-001",
            "timestamp": "2024-12-19T10:00:00Z"
        }
    }

# ---------- Väntare för docker-sajter (automatisk i CI) ----------
@pytest.fixture(scope="session", autouse=True)
def _wait_for_synthetic_services(synthetic_hosts):
    """Väntar på att docker-sajter ska starta (automatiskt i alla tester)"""
    import requests
    
    # Kontrollera bara om vi kör i CI eller om docker-compose körs
    if os.environ.get("CI") or os.environ.get("DOCKER_COMPOSE_RUNNING"):
        for name, base in synthetic_hosts.items():
            ok = False
            for attempt in range(30):  # 30 sekunder max väntetid
                try:
                    r = requests.get(base, timeout=1.0)
                    if r.status_code in (200, 404):  # 404 är OK för rot-sida
                        ok = True
                        break
                except Exception:
                    time.sleep(1)
            
            if not ok:
                print(f"[WARN] Synthetic service '{name}' not ready at {base}")
                print(f"[INFO] Tests using this service may be skipped")
    
    yield
