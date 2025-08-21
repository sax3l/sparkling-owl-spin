# ECaDP Test Framework 🧪

En komplett testsvit för ECaDP-plattformen designad för nybörjare och GitHub Copilot-integration.

## 📋 Översikt

Testframeworket är organiserat i tre nivåer:

1. **Unit-tester** - Snabba, isolerade tester av enskilda funktioner
2. **Integration-tester** - Tester av komponentinteraktion (databas, Redis, etc)
3. **E2E-tester** - End-to-end tester med riktiga webbläsare och syntetiska sajter

## 🚀 Snabbstart

### Förutsättningar

```bash
# Installera Python-beroenden
pip install -r requirements_dev.txt

# Installera Docker (för E2E-tester)
# Windows: Docker Desktop
# Linux: Docker Engine + Docker Compose
```

### Kör alla tester

```bash
# Enklaste sättet - kör allt
python scripts/run_tests.py

# Med detaljerad output
python scripts/run_tests.py --verbose

# Med code coverage
python scripts/run_tests.py --coverage
```

### Kör specifika testtyper

```bash
# Endast unit-tester (snabbast)
python scripts/run_tests.py --type unit

# Endast integration-tester  
python scripts/run_tests.py --type integration

# Endast E2E-tester
python scripts/run_tests.py --type e2e
```

## 🏗️ Teststruktur

```
tests/
├── pytest.ini              # Pytest-konfiguration och markers
├── conftest.py             # Delade fixtures och test-utilities
├── unit/                   # Unit-tester
│   ├── test_transformers.py    # DSL-transformationsfunktioner
│   ├── test_validators.py      # Datavalideringsfunktioner
│   └── test_header_generator.py # Anti-bot headers
├── integration/            # Integration-tester
│   ├── test_proxy_manager.py   # Proxy pool med Redis
│   ├── test_database.py       # Databasoperationer
│   └── test_scheduler.py      # Schemaläggning
├── e2e/                    # End-to-end tester
│   ├── test_e2e_static_list.py    # Statisk lista-scraping
│   ├── test_e2e_infinite_scroll.py # JavaScript infinite scroll
│   └── test_e2e_form_flow.py      # Formulärflöden
├── fixtures/               # Testdata och mock-filer
└── stubs/                  # Stub-implementationer
```

## 🎯 Test Markers

Använd pytest markers för att köra specifika testgrupper:

```bash
# Kör endast snabba tester
pytest -m "not slow"

# Kör endast databastester
pytest -m db

# Kör endast webbläsartester
pytest -m browser

# Kombinera markers
pytest -m "unit and not slow"
```

### Tillgängliga markers:

- `unit` - Unit-tester (snabba, isolerade)
- `integration` - Integration-tester
- `e2e` - End-to-end tester
- `db` - Kräver databas
- `browser` - Kräver webbläsare (Playwright)
- `slow` - Långsamma tester (>5 sekunder)

## 🐳 Syntetiska Test-tjänster

För E2E-tester använder vi Docker-baserade syntetiska webbsajter:

### Starta syntetiska tjänster

```bash
# Starta alla syntetiska tjänster
python scripts/start_synthetic_services.py

# Bygga om och starta
python scripts/start_synthetic_services.py --build

# Visa loggar
python scripts/start_synthetic_services.py --logs
```

### Tillgängliga tjänster

1. **Static List Service** (port 8081)
   - Simulerar traditionella lista-baserade sajter
   - Paginering, detaljsidor, robots.txt, sitemap
   - URL: http://localhost:8081/list

2. **Infinite Scroll Service** (port 8082)
   - JavaScript-driven infinite scroll
   - AJAX API, dynamisk innehållsladdning
   - URL: http://localhost:8082/scroll

3. **Form Flow Service** (port 8083)
   - Multi-step formulär med session management
   - CSRF-tokens, validering, komplex workflow
   - URL: http://localhost:8083/form

### Stoppa tjänster

```bash
docker compose -f docker/docker-compose.synthetic.yml down
```

## 🧪 Skriva nya tester

### Unit-test exempel

```python
import pytest
from src.utils.transformers import to_decimal

@pytest.mark.unit
@pytest.mark.parametrize("input_value,expected", [
    ("123.45", 123.45),
    ("123,45", 123.45),  # Svenska decimaler
    ("1 234,56", 1234.56),  # Tusentalsavgränsare
])
def test_to_decimal_conversion(input_value, expected):
    """Test decimal conversion with Swedish formats"""
    result = to_decimal(input_value)
    assert result == expected
```

### Integration-test exempel

```python
import pytest
from src.proxy_pool.manager import ProxyManager

@pytest.mark.integration
@pytest.mark.db
async def test_proxy_quality_tracking(redis_client):
    """Test proxy quality tracking with Redis"""
    manager = ProxyManager(redis_client)
    
    proxy = await manager.get_proxy()
    await manager.update_proxy_quality(proxy, success=True)
    
    quality = await manager.get_proxy_quality(proxy)
    assert quality > 0.5
```

### E2E-test exempel

```python
import pytest
from playwright.async_api import Page

@pytest.mark.e2e
@pytest.mark.browser
async def test_form_submission(page: Page):
    """Test complete form submission workflow"""
    await page.goto("http://localhost:8083/form")
    
    await page.fill("#registration_number", "ABC123")
    await page.fill("#owner_name", "Test Testsson")
    await page.click("button[type=submit]")
    
    await page.wait_for_url("**/form/step1")
    assert "Steg 2/4" in await page.title()
```

## 🔧 Fixtures och Utilities

### Globala fixtures (conftest.py)

- `redis_client` - FakeRedis för tester
- `temp_database` - Tillfällig testdatabas  
- `sample_html` - Laddar HTML-filer från fixtures
- `mock_response` - HTTP-response mocks
- `synthetic_hosts` - URLs till syntetiska tjänster

### Använd fixtures

```python
def test_with_redis(redis_client):
    """Test som använder Redis-fixture"""
    redis_client.set("key", "value")
    assert redis_client.get("key") == b"value"

def test_with_html(sample_html):
    """Test som använder HTML-fixture"""
    soup = sample_html("vehicle_detail.html")
    assert soup.find("title") is not None
```

## 📊 Test Rapporter

### Coverage rapporter

```bash
# Generera HTML coverage-rapport
python scripts/run_tests.py --coverage

# Öppna rapport
open htmlcov/index.html  # macOS/Linux
start htmlcov/index.html # Windows
```

### JSON rapporter

Automatiska JSON-rapporter skapas för CI/CD:

- `test_results_unit.json`
- `test_results_integration.json`
- `test_results_e2e.json`

## 🤖 GitHub Copilot Integration

Testframeworket är designat för optimal GitHub Copilot-integration:

### Namnkonventioner

- Testfiler: `test_*.py`
- Testfunktioner: `test_*` eller `test_*_when_*`
- Klasser: `Test*` (PascalCase)

### Dokumentation

- Alla tester har docstrings som förklarar syfte
- "För nybörjare:"-kommentarer förklarar komplexa koncept
- Parametriserade tester med tydliga exempel

### Patterns för Copilot

```python
def test_vehicle_registration_validation():
    """
    Test: Validera svenska registreringsnummer
    
    För nybörjare: Svenska registreringsnummer har formatet
    ABC123 (3 bokstäver + 3 siffror) eller ABC12D.
    """
    # Given - Arrangera testdata
    valid_registrations = ["ABC123", "XYZ789", "DEF45G"]
    invalid_registrations = ["12ABC3", "ABCD12", "AB123"]
    
    # When & Then - Agera och verifiera
    for reg in valid_registrations:
        assert is_valid_registration(reg), f"{reg} ska vara giltigt"
    
    for reg in invalid_registrations:
        assert not is_valid_registration(reg), f"{reg} ska vara ogiltigt"
```

## 🚨 Felsökning

### Vanliga problem

**Unit-tester misslyckas:**
```bash
# Kontrollera import-sökvägar
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Windows
set PYTHONPATH=%PYTHONPATH%;%cd%\src
```

**Integration-tester hänger:**
```bash
# Kontrollera Redis-anslutning
redis-cli ping

# Eller använd embedded FakeRedis (standard i tester)
```

**E2E-tester startar inte:**
```bash
# Kontrollera Docker
docker --version
docker compose version

# Starta syntetiska tjänster manuellt
python scripts/start_synthetic_services.py --build
```

**Playwright installationsproblem:**
```bash
# Installera Playwright browsers
playwright install chromium

# Eller använd system-browser
pytest --browser-channel=chrome
```

### Debug-tips

```bash
# Kör med extra verbose output
pytest -vvv tests/unit/test_transformers.py

# Stoppa vid första fel och visa traceback
pytest -x --tb=long

# Kör endast ett specifikt test
pytest tests/unit/test_transformers.py::test_to_decimal_conversion

# Kör med live logging
pytest --log-cli-level=DEBUG
```

## 📚 Ytterligare resurser

- [Pytest dokumentation](https://docs.pytest.org/)
- [Playwright för Python](https://playwright.dev/python/)
- [Docker Compose guide](https://docs.docker.com/compose/)
- [GitHub Copilot best practices](https://docs.github.com/en/copilot)

## 🤝 Bidrag

När du lägger till nya tester:

1. Följ namnkonventioner och dokumentationsstandard
2. Lägg till lämpliga pytest markers
3. Inkludera "För nybörjare:"-kommentarer för komplexa koncept
4. Testa både success- och failure-scenarier
5. Använd parametriserade tester för multiple test cases

---

**Skapad för ECaDP-projektet med fokus på nybörjarvänlighet och GitHub Copilot-integration** 🚀
