# Snabbstart - SOS Installation & Test

## Steg 1: Installation

```bash
# Kopiera .env
Copy-Item .env.example .env

# Installera dependencies (om lokal utveckling)
pip install -e .
make playwright-install

# ELLER kör med Docker (rekommenderat)
make run-sos-system
```

## Steg 2: Verifiera installation

```bash
# Kontrollera att API är uppe
curl http://localhost:8080/healthz

# Öppna API docs
# Gå till: http://localhost:8080/docs
```

## Steg 3: Skapa din första template

```bash
# Skapa demo-templates
make sos-create-demo

# Lista templates
sos list-templates
```

## Steg 4: Starta en crawl

```bash
# Via CLI
sos start-job 1 --output test-results.csv

# Via API
curl -X POST http://localhost:8080/jobs -H "Content-Type: application/json" -d '{"template_id": 1}'
```

## Steg 5: Kontrollera resultat

```bash
# Via CLI - resultatet sparas som CSV/JSON
ls data/exports/

# Via API  
curl http://localhost:8080/jobs/1/results
```

## Felsökning

### Vanliga problem:

**Port upptagen:**
```bash
# Ändra port i .env
API_PORT=8081
```

**Playwright installation misslyckas:**
```bash
# Installera manuellt
python -m playwright install --with-deps chromium
```

**Databas anslutning misslyckas:**
```bash
# Starta bara databas först
make db-up
# Vänta 10 sekunder, sedan starta API
make run-api
```

**Worker startar inte:**
```bash
# Kontrollera loggar
make logs-sos

# Eller kör manuellt för debug
python -m sos.scheduler.scheduler
```

### Loggar och debugging:

```bash
# Docker logs
docker compose -f docker-compose.sos.yml logs -f sos-api
docker compose -f docker-compose.sos.yml logs -f sos-worker

# Lokal utveckling - sätt LOG_LEVEL=DEBUG i .env
```

## Nästa steg

1. **Skapa egna mallar** - Se `templates/README.md`
2. **Konfigurera proxies** - Lägg till PROXY_URLS i .env  
3. **Setup export** - Konfigurera BigQuery eller GCS
4. **Monitoring** - Kolla http://localhost:8080/metrics
5. **Scaling** - Kör flera worker-instanser

Full dokumentation i `README-SOS.md`
