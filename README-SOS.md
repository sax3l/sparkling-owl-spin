# Sparkling Owl Spin (SOS) - Modern Webscraping Platform

En omfattande webscraping-plattform baserad på analys av moderna webscraping-verktyg som Octoparse, Firecrawl, Thunderbit, Browse AI, och Apify.

## ✨ Funktioner

### 🕷️ Crawler Engine
- **BFS/DFS crawling** - Breadth-first som standard, konfigurerbar djup-begränsning
- **Mall-baserat DSL** - YAML-mallar för återanvändbar konfiguration  
- **Statisk + JS-rendering** - HTTP för snabbhet, Playwright för dynamiskt innehåll
- **Politeness** - Respekterar robots.txt, konfigurerbar delay mellan requests

### 🌐 Anti-Bot & Proxies
- **Proxy pool** - Automatisk rotation av datacenter/residential proxies
- **Stealth browsing** - User-Agent rotation, headless-maskering
- **Rate limiting** - Per-host politeness för att undvika blockering
- **Session management** - Bibehåller cookies och kontext

### 📊 Data Processing  
- **Flexibel extraktion** - CSS selectors, XPath, regex post-processing
- **Strukturerad output** - JSON, CSV, BigQuery, Google Cloud Storage
- **Real-time monitoring** - Prometheus metrics, status tracking

### 🚀 Skalbarhet
- **Async arkitektur** - FastAPI backend, asynkron crawler workers
- **Docker-ready** - Container-baserad deployment
- **Databas-driven** - PostgreSQL för jobb/resultat, Supabase-kompatibel

### 🔧 Utvecklarverktyg
- **REST API** - Programmatisk åtkomst via OpenAPI/Swagger
- **CLI interface** - Kommandoradsverktyg för automation
- **Template system** - Visuellt mall-system för icke-utvecklare

## 🚀 Snabbstart

### Lokal utveckling

```bash
# 1. Klona och installera
git clone <repo>
cd Main_crawler_project
pip install -e .

# 2. Konfigurera miljö
cp .env.example .env
# Redigera .env med dina inställningar

# 3. Installera Playwright
make playwright-install

# 4. Starta databas
make db-up

# 5. Kör API i en terminal
make run-api

# 6. Kör worker i en annan terminal  
make run-worker
```

API finns nu på http://localhost:8080/docs

### Docker Compose (fullständigt system)

```bash
# Starta allt (API + Worker + DB)
make run-sos-system

# Visa loggar
make logs-sos

# Stoppa systemet
make stop-sos-system
```

## 📋 Användning

### Skapa crawling-mallar

```bash
# CLI: Skapa template från YAML
sos create-template "Min Mall" templates/min-mall.yaml

# Lista alla mallar  
sos list-templates

# Starta crawl-jobb
sos start-job 1 --output results.csv
```

### Via API

```bash
# Skapa template
curl -X POST http://localhost:8080/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Site",
    "yaml": "name: Test\nstart_urls:\n  - https://example.com\n..."
  }'

# Starta jobb
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{"template_id": 1}'

# Hämta resultat
curl http://localhost:8080/jobs/1/results
```

## 📝 Mall-DSL Format

SOS använder YAML-baserade mallar för att definiera crawling-beteende:

```yaml
name: "E-handel demo"
start_urls:
  - "https://shop.example.com/products"

# Länkföljning
follow:
  - selector: ".product-link"
    type: "detail" 
  - selector: ".pagination .next"
    type: "pagination"

# Data-extraktion
extract:
  - name: "title"
    selector: "h1.product-title"
    type: "text"
  - name: "price"
    selector: ".price"
    type: "text"
    regex: "([0-9,]+)"

# JavaScript-rendering
render:
  enabled: true

# Användar-aktioner
actions:
  scroll: true
  wait_ms: 2000

# Begränsningar
limits:
  max_pages: 500
  max_depth: 3

respect_robots: true
delay_ms: 1500
```

## 🔧 Konfiguration

### Miljövariabler (.env)

```bash
# Databas
DB_URL=postgresql+asyncpg://user:pass@localhost/sos

# Crawler inställningar  
CRAWL_MAX_CONCURRENCY=5
CRAWL_DEFAULT_DELAY_MS=1000
CRAWL_RESPECT_ROBOTS=true

# Proxy pool (komma-separerade URLs)
PROXY_URLS=http://proxy1:8080,http://proxy2:8080

# Export destinationer
BQ_DATASET=my_dataset
BQ_TABLE=scraped_data  
GCS_BUCKET=my-scraping-bucket

# Google Cloud autentisering
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Proxies

SOS stödjer proxy pools för att undvika blockering:

```bash
# Testa en proxy
sos test-proxy http://proxy.example.com:8080

# I .env, lägg till flera proxies:
PROXY_URLS=http://proxy1:8080,http://proxy2:8080,http://proxy3:8080
```

## 📊 Monitoring & Observability

### Prometheus Metrics

```
http://localhost:8080/metrics
```

Viktiga metrics:
- `sos_pages_crawled_total` - Antal crawlade sidor
- `sos_requests_blocked_total` - Blockerade requests
- `sos_job_duration_seconds` - Jobblängd

### Health Checks

```
http://localhost:8080/healthz  # Application health
http://localhost:8080/livez    # Liveness probe
```

## 🏗️ Arkitektur

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Web UI    │    │  REST API    │    │   Worker    │
│ (Frontend)  │◄──►│ (FastAPI)    │◄──►│ (Scheduler) │
└─────────────┘    └──────────────┘    └─────────────┘
                          │                     │
                          ▼                     ▼
                   ┌─────────────┐    ┌─────────────┐
                   │ PostgreSQL  │    │ Crawler     │
                   │ (Jobs/Data) │    │ (Playwright)│
                   └─────────────┘    └─────────────┘
                          │                     │
                          ▼                     ▼
                   ┌─────────────┐    ┌─────────────┐
                   │ Exporters   │    │ Proxy Pool  │
                   │(CSV/BQ/GCS) │    │ (Anti-bot)  │
                   └─────────────┘    └─────────────┘
```

## 🔍 Jämförelse med andra verktyg

| Funktion | SOS | Octoparse | Firecrawl | Apify | Browse AI |
|----------|-----|-----------|-----------|-------|-----------|
| **Open Source** | ✅ | ❌ | ✅ | SDK ✅ | ❌ |
| **Self-hosted** | ✅ | ❌ | ✅ | ❌ | ❌ |  
| **JS Rendering** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Proxy Support** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **CAPTCHA Solving** | Plugin | ❌ | ❌ | Plugin | ✅ |
| **API Access** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Template System** | ✅ | ✅ | ❌ | Code | ✅ |
| **Cost** | Hosting | $75+ | $19+ | $49+ | $19+ |

## 🚧 Utveckling & Bidrag

### Projektstruktur

```
src/sos/
├── api/           # FastAPI router & endpoints
├── core/          # Konfiguration & loggning  
├── crawler/       # Crawling engine & DSL
├── db/            # SQLAlchemy modeller & CRUD
├── exporters/     # CSV, BigQuery, GCS exporters
├── proxy/         # Proxy pool management
├── scheduler/     # Background job processor
└── schemas/       # Pydantic datamodeller
```

### Lägg till nya funktioner

1. **Ny exporter**: Skapa `src/sos/exporters/my_exporter.py`
2. **Ny crawler-strategi**: Utöka `src/sos/crawler/engine.py` 
3. **Ny mall-typ**: Utöka DSL i `src/sos/crawler/template_dsl.py`

### Tester

```bash
# Kör tester (när implementerade)
make test

# Kör linting
make lint

# Formattera kod  
make fmt
```

## 📜 Licens

MIT License - Se LICENSE fil för detaljer.

## 🤝 Erkännanden

Byggt baserat på analys av:
- Octoparse (visuell mall-byggare)
- Firecrawl (LLM-integrerad crawling)  
- Thunderbit (AI-driven extraktion)
- Browse AI (RPA-baserad automation)
- Apify (utvecklar-centrerad plattform)
- Screaming Frog (SEO-fokuserad crawling)

SOS kombinerar det bästa från varje verktyg i en öppen, självhostbar lösning.
