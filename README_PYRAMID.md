# 🦉 Sparkling-Owl-Spin - Pyramid Architecture

## Översikt

Sparkling-Owl-Spin är ett avancerat web scraping och penetrationstestning system byggt med pyramid-arkitektur. Systemet är designat för auktoriserad penetrationstestning och dataextrahering från egna system och godkända testmiljöer.

## ⚠️ Säkerhetsnotis

**ENDAST FÖR AUKTORISERAD ANVÄNDNING**
- Endast för penetrationstestning av egna servrar
- Endast godkända testmiljöer och auktoriserade mål
- All aktivitet loggas och övervakas
- Användaren ansvarar för att följa gällande lagar och etiska riktlinjer

## 🏗️ Pyramid Architecture

Systemet är organiserat i 6 lager enligt pyramid-arkitekturen:

### Layer 1: Core (Foundation)
**Plats:** `/core/`
- **Orchestrator** - Huvudkoordinator för alla komponenter
- **Config Manager** - Centraliserad konfigurationshantering
- **Security Controller** - Säkerhets- och auktoriseringskontroll
- **API Gateway** - REST API och webbinterface

### Layer 2: Engines (Specialization) 
**Plats:** `/engines/`
- **Scraping Engines** (`/engines/scraping/`)
  - Enhanced Scraping Framework (Scrapy, Playwright, BeautifulSoup)
- **Bypass Engines** (`/engines/bypass/`)
  - Cloudflare Bypass (FlareSolverr, CloudScraper, Undetected Chrome)
  - CAPTCHA Solver (2captcha, CapMonster, NopeCHA, Local OCR)
  - Undetected Browser Automation
- **Network Engines** (`/engines/network/`)
  - Proxy management och rotation
  - Rate limiting och throttling

### Layer 3: AI Agents (Intelligence)
**Plats:** `/ai_agents/`
- **CrewAI Integration** - Multi-agent orchestration
- **Specialized Agents**:
  - ScrapingSpecialist - Intelligent scraping strategies
  - SecurityAnalyst - Vulnerability assessment
  - DataScientist - Data analysis och insights
  - OSINTResearcher - Open source intelligence

### Layer 4: Data Processing (Information)
**Plats:** `/data_processing/`
- **Sources** (`/sources/`)
  - Swedish Data Sources (Blocket, Bytbil, Company Registry)
  - Custom data source adapters
- **Exporters** (`/exporters/`)
  - Multi-format export (JSON, CSV, XML, PDF)
  - Database integration

### Layer 5: API & Interfaces (Communication)
**Plats:** `/api/` och `/interfaces/`
- REST API endpoints
- Web UI (Next.js frontend)
- CLI interface
- External system integrations

### Layer 6: Configuration & Deployment (Environment)
**Plats:** `/config/`, `/docker/`, `/k8s/`
- Environment management
- Docker containers
- Kubernetes deployments
- CI/CD pipelines

## 🚀 Quick Start

### 1. Installation

```bash
# Klona repositoriet
git clone https://github.com/sax3l/sparkling-owl-spin.git
cd sparkling-owl-spin

# Installera dependencies
pip install -r requirements.txt
pip install -r requirements_backend.txt

# Eller använd setup script
python setup.py install
```

### 2. Konfiguration

```bash
# Kopiera konfigurationsmallar
cp config_template.py config/development/core.yml

# Redigera konfiguration för din miljö
# Lägg till API-nycklar för externa tjänster om nödvändigt
```

### 3. Starta systemet

```bash
# Starta med pyramid architecture
python main_pyramid.py

# Eller använd legacy main
python main.py
```

### 4. Verifiera installation

```bash
# Hälsokontroll
curl http://localhost:8000/health

# Systemstatus  
curl http://localhost:8000/status

# API dokumentation
open http://localhost:8000/docs
```

## 📡 API Usage

### Skapa Penetrationstestsession

```bash
curl -X POST http://localhost:8000/api/v1/security/pentest-sessions \
  -H "Content-Type: application/json" \
  -d '{
    "target_domains": ["example.com", "test.example.com"],
    "operator": "security_team",
    "purpose": "Security assessment",
    "duration_hours": 24
  }'
```

### Skapa Workflow

```bash
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Security Assessment",
    "type": "penetration_testing",
    "target_domains": ["test.example.com"],
    "steps": [
      {
        "name": "Cloudflare Bypass",
        "engine": "cloudflare_bypass",
        "parameters": {
          "target_url": "https://test.example.com",
          "method": "auto"
        }
      },
      {
        "name": "Vulnerability Scan",
        "engine": "ai_agents",
        "parameters": {
          "objective": "Assess security vulnerabilities",
          "tasks": ["security_assessment", "vulnerability_scan"]
        }
      }
    ]
  }'
```

### Kör Workflow

```bash
curl -X POST http://localhost:8000/api/v1/workflows/{workflow_id}/execute
```

## 🔧 Available Engines

### Scraping Engines
- **Scrapy** - Robust web scraping framework
- **Playwright** - Modern browser automation
- **BeautifulSoup** - HTML/XML parsing
- **Selenium** - Legacy browser automation

### Bypass Engines
- **FlareSolverr** - Cloudflare bypass via proxy
- **CloudScraper** - Python Cloudflare solver
- **Undetected Chrome** - Stealth browser automation
- **curl-cffi** - Low-level HTTP client with TLS mimicking

### CAPTCHA Solvers
- **2captcha** - Premium CAPTCHA solving service
- **CapMonster** - Alternative CAPTCHA service
- **NopeCHA** - Modern CAPTCHA solver
- **Local OCR** - Offline CAPTCHA recognition

### AI Agents
- **CrewAI** - Multi-agent task orchestration
- **Langchain** - LLM application framework
- **LlamaIndex** - Data-augmented LLM applications

## 🇸🇪 Swedish Data Sources

### Blocket Integration
```python
# Söka fordon på Blocket
result = await swedish_data.search_blocket_vehicles(
    make="Volvo",
    model="V70", 
    year_min=2015,
    price_max=200000
)
```

### Bytbil Price Evaluation
```python
# Värdering via Bytbil
valuation = await swedish_data.get_bytbil_valuation(
    registration_number="ABC123",
    mileage=150000
)
```

## 🛡️ Säkerhetsfunktioner

### Domain Authorization
- Kräver explicit auktorisering för alla måldomäner
- DNS-verifiering eller filbaserad verifiering
- Tidsbegränsade auktoriseringar

### Penetration Testing Sessions
- Auditlogg för alla penetrationstestaktiviteter
- Sessionsbased åtkomstkontroll
- Automatisk session cleanup

### Rate Limiting
- Per-IP och per-endpoint begränsningar
- Automatisk blockering av misstänkta förfrågningar
- Anpassningsbara gränsvärden

### Request Monitoring
- Real-time övervakning av alla förfrågningar
- Säkerhetshändelse-loggning
- Automatisk hotdetektering

## 📊 Monitoring & Metrics

### System Metrics
```bash
curl http://localhost:8000/api/v1/metrics
```

### Engine Performance
```bash
curl http://localhost:8000/api/v1/metrics/engines
```

### Security Events
```bash
curl http://localhost:8000/api/v1/security/events
```

## 🔧 Konfiguration

### Environment Variables
```bash
# Core system
SPARKLING_ENV=development
LOG_LEVEL=INFO

# External APIs
OPENAI_API_KEY=your_openai_key
TWOCAPTCHA_API_KEY=your_2captcha_key
BLOCKET_API_KEY=your_blocket_key

# Security
SECURITY_LEVEL=medium
REQUIRE_DOMAIN_AUTHORIZATION=true
```

### Configuration Files
- `config/development/core.yml` - Core system settings
- `config/development/security.yml` - Security configuration  
- `config/development/api.yml` - API gateway settings
- `config/development/engines.yml` - Engine configurations

## 🚢 Deployment

### Docker
```bash
# Build image
docker build -t sparkling-owl-spin .

# Run container
docker run -p 8000:8000 sparkling-owl-spin
```

### Docker Compose
```bash
# Development environment
docker-compose up -d

# Production environment  
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes
```bash
# Deploy to cluster
kubectl apply -f k8s/
```

## 🧪 Testing

```bash
# Unit tests
pytest tests/

# Integration tests
pytest tests/integration/

# Engine tests
pytest tests/engines/

# Security tests
pytest tests/security/
```

## 📚 Documentation

- **API Reference**: http://localhost:8000/docs
- **Architecture Guide**: `/docs/architecture.md`
- **Security Guide**: `/docs/security.md`
- **Engine Development**: `/docs/engines.md`
- **Deployment Guide**: `/docs/deployment.md`

## 🤝 Contributing

1. Fork repositoriet
2. Skapa feature branch (`git checkout -b feature/amazing-feature`)
3. Commit ändringar (`git commit -m 'Add amazing feature'`)
4. Push till branch (`git push origin feature/amazing-feature`)
5. Skapa Pull Request

Se [CONTRIBUTING.md](CONTRIBUTING.md) för detaljerade riktlinjer.

## ⚖️ License

Detta projekt är licensierat under MIT License - se [LICENSE](LICENSE) filen för detaljer.

## 🙏 Acknowledgments

- **FlareSolverr** - Cloudflare bypass solution
- **CloudScraper** - Python Cloudflare solver
- **CrewAI** - Multi-agent AI framework
- **Scrapy** - Web scraping framework
- **Playwright** - Browser automation
- **Svenska utvecklargemenskapen** för inspiration och feedback

## ⚠️ Legal Disclaimer

Detta verktyg är utvecklat enbart för:
- Auktoriserad penetrationstestning av egna system
- Säkerhetsforskning i kontrollerade miljöer
- Dataextrahering från egna webbplatser

Användaren ansvarar fullt ut för att följa:
- Gällande lagar och förordningar
- Webbplatsers användarvillkor
- Etiska hacking-principer
- GDPR och andra dataskyddsregler

**Missbruk av detta verktyg kan vara olagligt. Använd ansvarsfullt.**
