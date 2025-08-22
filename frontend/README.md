# ECaDP - Ethical Crawler & Data Platform

En etisk och regelefterlevande plattform för webb-crawling, mall-baserad web scraping, proxy/anti-bot-hantering, no-code UI, API (REST/GraphQL), DSL, SDK:er, observability, backup/restore och K8s-driftsjobb.

## Snabbstart

```bash
# Starta utvecklingsmiljö
make up

# Initiera databas och seeddata
make init
make seed

# Kör tester
make test
make e2e

# Bygg SDK:er
make gen-sdk
```

## Arkitektur

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   Backend API   │    │   Supabase DB   │
│   React/Vite    │───▶│   FastAPI       │───▶│   PostgreSQL    │
│                 │    │   Python 3.11+  │    │   Redis Cache   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Proxy Pool    │              │
         └─────────────▶│   Anti-Bot      │◀─────────────┘
                        │   Crawler       │
                        └─────────────────┘
```

## Etiska Riktlinjer

- **Följ robots.txt och ToS**: Systemet upprätthåller domänpolicyer tekniskt
- **Föredra officiella API:er**: Använd API:er när tillgängliga
- **Stealth endast inom policy**: Anti-bot-teknik följer lag och villkor
- **GDPR/PII-hantering**: Pseudonymisering, kryptering, radering på begäran

## Komponenter

- **No-Code UI**: Peka-och-extrahera interface för mallskapning
- **DSL Engine**: YAML-baserade extraktionsmallar
- **Proxy Pool**: Rotationshantering med kvalitetspoäng  
- **Scheduler**: Bakgrundsjobb för crawling, backup, retention
- **Observability**: Prometheus metrics + Grafana dashboards
- **SDK**: Python & TypeScript klienter med rate-limiting

## Utveckling

Se [docs/developer_guide.md](docs/developer_guide.md) för utvecklarinstruktioner.

För användare utan teknisk bakgrund: [docs/usage_guide.md](docs/usage_guide.md)

## Säkerhet

Rapportera säkerhetsproblem enligt [SECURITY.md](SECURITY.md).

## Teknisk Stack

### Backend
- **Python 3.11+** med FastAPI, SQLAlchemy 2, Pydantic v2
- **Supabase** (PostgreSQL + Redis cache)
- **Crawling**: httpx/aiohttp (HTTP), Playwright (browser)
- **Scheduler**: APScheduler för bakgrundsjobb
- **Observability**: Prometheus metrics + structured JSON logging

### Frontend  
- **React + Vite + TypeScript**
- **shadcn-ui + Tailwind CSS**
- **No-code UI**: Browser panel + selector overlay
- **Real-time**: WebSocket-baserad job monitoring

### DevOps
- **Docker** för containerisering
- **Kubernetes** för orkestrering  
- **GitHub Actions** för CI/CD
- **Grafana + Prometheus** för monitoring

## Licens

[LICENSE](LICENSE)
