# 🚀 Revolutionary Ultimate Scraping System v4.0

**Den ultimata web scraping-plattformen med militär-grad stealth, AI-powered content extraction och production-ready arkitektur.**

## 🎯 Översikt

Revolutionary Ultimate Scraping System v4.0 är det mest avancerade web scraping-systemet som någonsin skapats. Det integrerar alla bästa tekniker från toppmodern forskning och open-source projekt för att lösa alla utmaningar inom modern web scraping.

### 🛡️ Anti-Bot Defense System

**Smart Triage Pipeline:**
1. **requests** → Standard HTTP requests
2. **cloudscraper** → CloudFlare IUAM bypass
3. **FlareSolverr** → Headless browser för Cloudflare Turnstile
4. **undetected-chromedriver** → Verklig Chrome med stealth
5. **azuretls-client** → TLS/JA3 fingerprinting spoofing

**CAPTCHA Solving:**
- 2captcha integration för reCAPTCHA v2/v3
- hCaptcha automatisk lösning
- Cloudflare Turnstile support
- NopeCHA extension support

### 📄 Content Extraction Pipeline

**Intelligent Content Processing:**
- **Trafilatura**: Best-in-class HTML content extraction med boilerplate removal
- **Apache Tika**: Universal parser för 1000+ filtyper (PDF, DOCX, XLSX, PPT, etc.)
- **PyMuPDF**: Advanced PDF processing med tabeller och layout detection
- **Microsoft Recognizers-Text**: Entity extraction (datum, belopp, mått) på svenska/engelska
- **RapidFuzz**: Fuzzy matching för content deduplication

### ⚙️ Intelligent Configuration System

**Per-Domain Policies (YAML):**
```yaml
domains:
  "example.se":
    engine: "cloudscraper"
    captcha: "2captcha" 
    rate_limit: 0.5
    min_quality: 0.5
```

**Quality Control:**
- Content quality scoring
- Duplicate detection
- Performance monitoring
- Error tracking & retry logic

## 🚀 Quick Start

### 1. Installation

```bash
# Klona repository
git clone <repository-url>
cd Main_crawler_project

# Automatisk installation
python setup_revolutionary_v4.py
```

Detta installerar automatiskt:
- ✅ Alla Python dependencies
- ✅ Docker services (FlareSolverr, Tika, PostgreSQL, Redis)
- ✅ Database schema
- ✅ Monitoring (Prometheus, Grafana)

### 2. Konfiguration

```bash
# Kopiera och redigera environment variables
cp .env.example .env
nano .env
```

Lägg till dina API-nycklar:
```bash
TWOCAPTCHA_API_KEY=your-2captcha-api-key
NOPECHA_API_KEY=your-nopecha-api-key
```

### 3. Användning

#### Basic Usage
```python
import asyncio
from revolutionary_scraper.revolutionary_ultimate_v4 import RevolutionaryUltimateSystem

async def main():
    async with RevolutionaryUltimateSystem() as scraper:
        # Scrapa en URL
        result = await scraper.scrape_url("https://example.com")
        
        if result.success:
            print(f"Title: {result.extracted_content.title}")
            print(f"Text: {result.extracted_content.text[:200]}...")
            print(f"Quality: {result.quality_score:.2f}")
        else:
            print(f"Error: {result.error}")

asyncio.run(main())
```

#### Batch Processing
```python
async with RevolutionaryUltimateSystem() as scraper:
    urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
    results = await scraper.scrape_urls(urls)
    
    for result in results:
        if result.success:
            print(f"✅ {result.task.url} - Quality: {result.quality_score:.2f}")
        else:
            print(f"❌ {result.task.url} - Error: {result.error}")
```

#### Advanced Configuration
```python
# Med custom policies
scraper.add_task(
    url="https://difficult-site.com",
    force_engine="undetected_chrome",
    priority=10,
    max_retries=5
)

results = await scraper.process_queue()
```

## 🔧 Konfiguration

### Domain Policies (crawl-policies.yml)

```yaml
domains:
  # CloudFlare-skyddad sajt
  "protected.com":
    engine: "undetected_chrome"
    flare_solverr: true
    captcha: "2captcha"
    tls_fingerprint: "azuretls"
    rate_limit: 0.2
    timeout: 60
    
  # News website
  "*.news.se":
    engine: "playwright"
    extract_html: "trafilatura"
    extract_entities: true
    seed_mode: "katana"
    rate_limit: 2.0
    
  # PDF-heavy site
  "documents.gov.se":
    extract_pdf: "pdf-extract-kit"
    rate_limit: 0.3
    timeout: 120
```

### Engine Options
- **requests**: Standard HTTP (snabbast)
- **cloudscraper**: CloudFlare IUAM bypass
- **playwright**: Modern headless browser
- **undetected_chrome**: Stealth Chrome (bäst mot detektion)

### CAPTCHA Providers
- **2captcha**: Premium CAPTCHA solving service
- **nopecha**: Browser extension-baserad lösning
- **auto**: Automatisk val baserat på tillgängliga nycklar

## 🧪 Testing & Demo

### Kör Demo
```bash
# Interaktiv demo
python demo_revolutionary_v4.py --interactive

# Full automatisk demo
python demo_revolutionary_v4.py --full

# Testa specifik URL
python demo_revolutionary_v4.py --url https://example.com
```

### Test Suites
Demon testar:
- ✅ Basic functionality (HTTP, JSON, HTML)
- ✅ Anti-bot escalation (Cloudflare bypass)
- ✅ Content extraction (HTML, PDF, entities)
- ✅ Performance & concurrency
- ✅ Domain policies
- ✅ Quality scoring

## 📊 Monitoring & Metrics

### Services
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **FlareSolverr**: http://localhost:8191

### Key Metrics
```python
scraper.print_metrics()
```

Output:
```
🚀 Revolutionary Ultimate System Metrics
=====================================
📊 Tasks processed: 147
✅ Success rate: 94.6%
❌ Failure rate: 5.4%
🔄 Duplicate rate: 12.2%
⭐ Average quality: 0.73
⏱️  Average time per task: 2.34s
🌐 Unique domains: 15

🛡️ Methods used:
  • requests: 89
  • cloudscraper: 34
  • undetected_chrome: 24
```

## 🛡️ Advanced Features

### 1. TLS/JA3 Fingerprinting
För sajter som detekterar "fel" TLS-fingerprint:
```yaml
domains:
  "advanced-detection.com":
    tls_fingerprint: "azuretls"  # Spoofa Chrome TLS
```

### 2. Behavioral Simulation
```python
config.behavioral_simulation = True  # Simulera mänskligt beteende
```

### 3. Proxy Rotation
```yaml
domains:
  "rate-limited.com":
    proxy_rotation: true
    rate_limit: 0.1
```

### 4. Content Quality Scoring
Automatisk bedömning baserat på:
- Text length & word count
- Metadata completeness (title, author, date)
- Entity richness
- Structure (links, images, tables)

### 5. Entity Recognition
Extraherar automatiskt:
- 📅 Datum (svenska/engelska format)
- 💰 Belopp och valutor
- 📏 Mått och dimensioner
- 📞 Telefonnummer
- 📧 Email-adresser

## 🐳 Docker Services

### Start Services
```bash
# Alla core services
docker-compose -f docker-compose.revolutionary.yml up -d

# Med Selenium Grid
docker-compose -f docker-compose.revolutionary.yml --profile selenium up -d

# Med huvudapplikation
docker-compose -f docker-compose.revolutionary.yml --profile app up -d
```

### Service Ports
- **FlareSolverr**: 8191 (Cloudflare bypass)
- **Apache Tika**: 9998 (Content extraction)
- **PostgreSQL**: 5432 (Database)
- **Redis**: 6379 (Cache & queues)
- **Prometheus**: 9090 (Metrics)
- **Grafana**: 3000 (Dashboards)
- **Selenium Hub**: 4444 (Browser grid)

## 🔧 Troubleshooting

### Common Issues

**1. FlareSolverr not starting**
```bash
# Check Docker
docker logs revolutionary_flaresolverr

# Restart service
docker-compose -f docker-compose.revolutionary.yml restart flaresolverr
```

**2. CAPTCHA solving fails**
- Kontrollera API-nycklar i .env
- Verifiera 2captcha/NopeCHA saldo
- Testa med mindre svåra CAPTCHAs först

**3. Low quality scores**
```yaml
# Sänk quality threshold
domains:
  "problematic-site.com":
    min_quality: 0.1
```

**4. Rate limiting issues**
```yaml
# Sänk rate limit
domains:
  "strict-site.com":
    rate_limit: 0.1
    retry_delay: 10.0
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

async with RevolutionaryUltimateSystem(config_path="debug-config.yml") as scraper:
    result = await scraper.scrape_url("https://problematic-site.com")
```

## 📚 API Reference

### RevolutionaryUltimateSystem

```python
class RevolutionaryUltimateSystem:
    async def scrape_url(self, url: str, **kwargs) -> ScrapingTaskResult
    async def scrape_urls(self, urls: List[str], **kwargs) -> List[ScrapingTaskResult]
    async def process_queue(self, max_concurrent: int = None) -> List[ScrapingTaskResult]
    def add_task(self, url: str, **kwargs) -> str
    def get_metrics(self) -> Dict[str, Any]
    def print_metrics(self) -> None
```

### ScrapingTaskResult

```python
@dataclass
class ScrapingTaskResult:
    success: bool
    scraping_result: Optional[ScrapingResult]     # Anti-bot result
    extracted_content: Optional[ExtractedContent] # Content extraction result
    quality_score: float                          # Content quality (0-1)
    total_time: float                            # Processing time
    error: Optional[str]                         # Error message if failed
```

### ExtractedContent

```python
@dataclass
class ExtractedContent:
    title: Optional[str]           # Page title
    text: Optional[str]           # Clean text content
    author: Optional[str]         # Author if detected
    date: Optional[str]           # Published date
    entities: List[EntityResult]  # Extracted entities
    links: List[Dict]             # Found links
    images: List[Dict]            # Found images
    tables: List[Dict]            # Extracted tables
    quality_score: float          # Content quality score
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements_dev.txt

# Run tests
pytest tests/

# Code formatting
black revolutionary_scraper/
flake8 revolutionary_scraper/

# Type checking
mypy revolutionary_scraper/
```

### Adding New Anti-Bot Methods
1. Extend `AntiDetectionMethod` enum
2. Implement method in `RevolutionaryAntiBotSystem`
3. Add configuration options
4. Update tests

### Adding New Extraction Methods
1. Extend `ExtractionMethod` enum
2. Implement in `RevolutionaryContentExtractor`
3. Add quality scoring logic
4. Update tests

## 📄 License

MIT License - Se LICENSE fil för detaljer.

## 🙏 Acknowledgments

Detta system integrerar och bygger vidare på fantastiska open-source projekt:

**Anti-Bot Defense:**
- [cloudscraper](https://github.com/VeNoMouS/cloudscraper) - CloudFlare bypass
- [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) - Headless Cloudflare solver  
- [undetected-chromedriver](https://github.com/ultrafunkamsterdam/undetected-chromedriver) - Stealth automation
- [2captcha-python](https://github.com/2captcha/2captcha-python) - CAPTCHA solving

**Content Extraction:**
- [trafilatura](https://github.com/adbar/trafilatura) - HTML content extraction
- [Apache Tika](https://tika.apache.org/) - Universal content parser
- [recognizers-text](https://github.com/Microsoft/Recognizers-Text) - Entity recognition
- [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) - Fuzzy string matching

**Infrastructure:**
- [Docker](https://docker.com) - Containerization
- [PostgreSQL](https://postgresql.org) - Database
- [Redis](https://redis.io) - Caching & queues
- [Prometheus](https://prometheus.io) - Metrics
- [Grafana](https://grafana.com) - Monitoring

---

**🚀 Happy Scraping! Bygg ansvarigt och respektera robots.txt 🤖**
