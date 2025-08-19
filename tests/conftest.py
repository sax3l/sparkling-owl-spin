import os, json, yaml, pytest, asyncio, time
from pathlib import Path

# 1) Event loop (för async-tester)
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# 2) Ladda testdata (YAML, HTML, JSON)
@pytest.fixture
def load_template():
    def _load(name: str) -> dict:
        p = Path(__file__).parent / "fixtures" / "templates" / f"{name}.yaml"
        return yaml.safe_load(p.read_text(encoding="utf-8"))
    return _load

@pytest.fixture
def load_html():
    def _load(name: str) -> str:
        p = Path(__file__).parent / "fixtures" / "html" / f"{name}.html"
        return p.read_text(encoding="utf-8")
    return _load

@pytest.fixture
def load_json():
    def _load(name: str) -> dict:
        p = Path(__file__).parent / "fixtures" / "data" / f"{name}.json"
        return json.loads(p.read_text(encoding="utf-8"))
    return _load

# 3) Falsk Redis
class FakeRedis:
    def __init__(self): self.store = {}
    async def get(self, k): return self.store.get(k)
    async def set(self, k, v, ex=None): self.store[k] = v
    async def delete(self, k): self.store.pop(k, None)
    async def incr(self, k, amt=1): self.store[k] = int(self.store.get(k, 0)) + amt

@pytest.fixture
async def redis_client():
    return FakeRedis()

# 4) Test-konfig
@pytest.fixture
def test_config():
    cfg_dir = Path(__file__).parent / "fixtures" / "config"
    return {
        "anti_bot": yaml.safe_load((cfg_dir / "anti_bot.yml").read_text(encoding="utf-8")),
        "perf": yaml.safe_load((cfg_dir / "performance-defaults.yml").read_text(encoding="utf-8")),
    }

# 5) Endpoints för syntetiska sajter
@pytest.fixture(scope="session")
def synthetic_hosts():
    return {
        "static": "http://localhost:8081",
        "scroll": "http://localhost:8082",
        "form":   "http://localhost:8083",
    }

# 6) Vänta på att syntetiska sajter startar i CI
@pytest.fixture(scope="session", autouse=True)
def _wait_for_synthetic_services(synthetic_hosts):
    import requests
    # Check if running in CI where docker is expected
    if os.environ.get("CI"):
        for name, base in synthetic_hosts.items():
            ok = False
            for _ in range(60):
                try:
                    r = requests.get(base, timeout=1.0)
                    if r.status_code in (200, 404):
                        ok = True
                        break
                except requests.RequestException:
                    time.sleep(1)
            if not ok:
                print(f"[WARN] Synthetic service '{name}' not ready at {base} (tests may fail)")
    yield