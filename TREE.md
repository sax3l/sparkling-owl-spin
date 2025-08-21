# Complete Project File Structure

This document provides a comprehensive overview of the entire project structure, serving as a reference for developers and maintainers.

## Root Level
```
projektet/
├─ README.md                                # Start-här: översikt, snabbstart, arkitektur-figur, länkar
├─ TREE.md                                  # Denna fil – fullständig fil- och mappkarta (håll uppdaterad)
├─ LICENSE                                   # Licenspolicy
├─ CODE_OF_CONDUCT.md                        # Etik och community-regler
├─ CONTRIBUTING.md                           # Bidragsguide, commit-konventioner, PR-process
├─ SECURITY.md                               # Sårbarhetsrapportering, ansvarfullt avslöjande
├─ .gitignore                                # Ignorerade filer
├─ .dockerignore                             # Docker build-kontextfilter
├─ .editorconfig                             # Enhetlig formattering över editors
├─ .env.example                              # Exempel på miljövariabler (DB, Redis, S3, OAuth, HMAC, etc.)
├─ .envrc                                    # direnv-stöd (valfritt)
├─ Makefile                                  # Enkla kommandon: make up, make test, make lint, make seed, etc.
├─ pyproject.toml                            # Poetry/PDM (välj en) – beroenden, verktygskonfig
├─ requirements.txt                          # Lock/"export" för prod
├─ requirements_dev.txt                      # Dev-beroenden (pytest, mypy, ruff, bandit, black, GE/Soda)
├─ package.json                              # Rot-skript (formatter, lint-staged), ev. repo-verktyg
└─ VERSION                                   # En enkel versionsfil (CI läser denna)
```

## Configuration (globala, miljö & policies)
```
config/
├─ app_config.yml                         # Global app-konfig (crawler/scraper/proxy/scheduler)
├─ logging.yml                            # Loggstruktur (JSON), nivåer, handlers
├─ performance-defaults.yml               # Baseline-konfig (HTTP/Browser, caps, cache-TTL)
├─ proxies.yml                            # Källor (gratis/betal), regionpreferenser, prioritet
├─ anti_bot.yml                           # Header-profiler, delays, risknivåer, fallbackpolicy
├─ captcha.yml                            # (Valfritt) tredjeparts-CAPTCHA-tjänst (om juridiskt OK)
├─ export_targets.yml                     # Fördefinierade exporter (CSV/Excel/Sheets/BigQuery/ES/Snowflake)
├─ api.yml                                # API-limits, pagination defaults, webhooks (HMAC)
├─ auth.yml                               # OAuth2-klienter, API-nycklar (referenser till secrets)
├─ roles.yml                              # RBAC-roller (admin, analyst, operator)
├─ domain_policies/                       # Per-domän policys (robots, ToS-accept, caps)
│  ├─ example.com.yml
│  └─ ...
└─ env/
   ├─ development.yml
   ├─ staging.yml
   └─ production.yml
```

## Documentation (arkitektur, API, runbooks, lag/etik)
```
docs/
├─ architecture.md                        # Övergripande arkitektur, Figur 1, sekvensdiagram
├─ system_design_decisions.md             # ADRs (Architecture Decision Records)
├─ developer_guide.md                     # Lokal setup, kommandon, felsökning
├─ usage_guide.md                         # No-code UI, mallskapande, export – för icke-utvecklare
├─ database_schema.md                     # Relationsmodell, index, PK/FK, RLS, PII
├─ api_documentation.md                   # Länk/översikt till OpenAPI + GraphQL SDL
├─ openapi.yaml                           # Full REST-spec (server-url placeholders)
├─ graphql/
│  └─ schema.graphql                      # GraphQL SDL (typer, queries, mutations)
├─ postman/
│  └─ collection.json                     # Postman-samling av alla endpoints
├─ policies/
│  ├─ robots_tos_policy.md                # Robots/ToS-process, vad systemet gör automatiskt
│  ├─ gdpr_dpia_template.md               # DPIA-mall och checklista
│  ├─ s3_lifecycle_raw_html.json          # S3 Lifecycle policy (raw_html/)
│  ├─ s3_lifecycle_db_backups.json        # S3 Lifecycle policy (db_backups/)
│  ├─ s3_lifecycle_exports.json           # S3 Lifecycle policy (exports/)
│  ├─ backup_restore_policy.md            # Backups, WAL, återställningstest (drill)
│  ├─ retention_policy.md                 # TTL per tabell/filtyp
│  ├─ erasure_policy.md                   # Radering on-demand (person + relationer)
│  └─ provenance_lineage_policy.md        # Lineage-krav (käll-URL, mallversion, run_id)
├─ runbooks/                              # Incident- & driftkörböcker
│  ├─ 403_storm.md
│  ├─ 429_spike.md
│  ├─ layout_drift.md
│  ├─ proxy_drought.md
│  └─ restore_drill.md
├─ slo_sla.md                             # Mål & felbudget
├─ changelog.md                           # Versionslogg (synkad med release-taggar)
└─ lovable/
   └─ prompt.md                           # Lovable-initprompt
```

## Infrastructure & Deployment
Comprehensive Kubernetes, Terraform, and Docker configurations for production deployment.

## Source Code Structure
Complete Python application with modular architecture including crawlers, scrapers, anti-bot measures, and data processing pipelines.

## Testing Framework
Full test pyramid with unit, integration, and E2E tests including synthetic test sites.

## Observability & Monitoring
Prometheus, Grafana, and OpenTelemetry setup for comprehensive system monitoring.

## SDKs & APIs
Python and TypeScript SDKs for external integration, plus comprehensive OpenAPI and GraphQL specifications.

---

**Last Updated:** 2025-08-21  
**Total Files:** 456  
**Current Completion:** Dynamic (see scripts/complete_structure_analyzer.py)

This structure supports enterprise-grade web scraping with ethical compliance, scalability, and maintainability at its core.
