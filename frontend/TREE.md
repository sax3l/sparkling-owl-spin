# ECaDP - Fil- & Katalogstruktur

```
.
├── README.md                           # Projektöversikt och snabbstart
├── TREE.md                            # Denna fil - komplett filkarta
├── LICENSE                            # MIT licens
├── CODE_OF_CONDUCT.md                 # Uppförandekod
├── CONTRIBUTING.md                    # Bidragande-guide
├── SECURITY.md                        # Säkerhetsrapportering
├── VERSION                            # Semantisk versionsnummer
├── Makefile                           # Utvecklingskommandon
├── pyproject.toml                     # Python dependencies (Poetry)
├── requirements.txt                   # Python requirements
├── requirements-dev.txt               # Utvecklingsdependencies  
├── package.json                       # Node.js verktyg och lint
├── .gitignore                         # Git ignore-regler
├── .dockerignore                      # Docker ignore-regler
├── .editorconfig                      # Editor-konfiguration
├── .env.example                       # Miljövariabel-exempel
├── .envrc                             # direnv-konfiguration
│
├── config/                            # Konfigurationsfiler
│   ├── app_config.yml                 # Huvudapplikationskonfig
│   ├── logging.yml                    # Loggningskonfiguration
│   ├── performance-defaults.yml       # HTTP & Browser baseline
│   ├── proxies.yml                    # Proxy-källor och inställningar
│   ├── anti_bot.yml                   # Anti-bot strategier
│   ├── captcha.yml                    # CAPTCHA-lösare config
│   ├── export_targets.yml             # Export-destinationer
│   ├── api.yml                        # API-konfiguration
│   ├── auth.yml                       # Autentiseringsinställningar
│   ├── roles.yml                      # Rollbaserad åtkomstkontroll
│   ├── domain_policies/               # Per-domän policyer
│   │   └── example.com.yml            # Exempel domänpolicy
│   └── env/                           # Miljö-specifika inställningar
│       ├── development.yml
│       ├── staging.yml
│       └── production.yml
│
├── docs/                              # Dokumentation
│   ├── architecture.md                # Systemarkitektur + diagram
│   ├── system_design_decisions.md     # ADR-mall och beslut
│   ├── developer_guide.md             # Utvecklarguide
│   ├── usage_guide.md                 # Användarguide (no-code)
│   ├── database_schema.md             # DB-schema dokumentation
│   ├── api_documentation.md           # API-referens
│   ├── openapi.yaml                   # OpenAPI 3.0 specifikation
│   ├── graphql/
│   │   └── schema.graphql             # GraphQL SDL
│   ├── postman/
│   │   └── collection.json            # Postman test collection
│   ├── policies/                      # Policyer och riktlinjer
│   │   ├── robots_tos_policy.md       # robots.txt & ToS policy
│   │   ├── gdpr_dpia_template.md      # GDPR DPIA-mall
│   │   ├── s3_lifecycle_raw_html.json # S3 lifecycle för raw HTML
│   │   ├── s3_lifecycle_db_backups.json # S3 lifecycle för backups
│   │   ├── s3_lifecycle_exports.json  # S3 lifecycle för exports
│   │   ├── backup_restore_policy.md   # Backup & restore policy
│   │   ├── retention_policy.md        # Dataretention policy
│   │   ├── erasure_policy.md          # GDPR erasure policy
│   │   └── provenance_lineage_policy.md # Data provenance policy
│   ├── runbooks/                      # Drifthandböcker
│   │   ├── 403_storm.md               # Hantera 403-storm
│   │   ├── 429_spike.md               # Hantera rate-limiting
│   │   ├── layout_drift.md            # Hantera layout-förändringar
│   │   ├── proxy_drought.md           # Hantera proxy-brist
│   │   └── restore_drill.md           # Restore-övningshandbok
│   ├── slo_sla.md                     # SLO/SLA-definitioner
│   ├── changelog.md                   # Ändringslogg
│   └── lovable/
│       └── prompt.md                  # Master-prompt backup
│
├── docker/                            # Docker-konfiguration
│   ├── Dockerfile.app                 # Huvudapplikation
│   ├── Dockerfile.worker              # Background workers
│   ├── Dockerfile.browser             # Browser pool
│   ├── Dockerfile.synthetic           # Syntetiska test-sajter
│   ├── entrypoint.sh                  # Docker entrypoint script
│   ├── docker-compose.yml             # Produktionsdocker
│   ├── docker-compose.dev.yml         # Utvecklingsdocker
│   ├── docker-compose.synthetic.yml   # Syntetiska sajter
│   └── dev/                           # Utvecklingsverktyg
│       ├── grafana/
│       │   └── provisioning/
│       └── prometheus/
│           └── prometheus.yml
│
├── iac/                               # Infrastructure as Code
│   ├── terraform/                     # Terraform moduler
│   │   ├── modules/
│   │   │   ├── network/
│   │   │   ├── eks/
│   │   │   ├── rds/
│   │   │   ├── redis/
│   │   │   └── s3/
│   │   └── envs/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── prod/
│   └── k8s/                           # Kubernetes manifests
│       ├── namespaces/
│       │   ├── scraping.yaml
│       │   ├── data.yaml
│       │   └── ops.yaml
│       ├── secrets/
│       │   └── external-secrets.yaml
│       ├── configmaps/
│       │   ├── app-config.yaml
│       │   ├── anti-bot.yaml
│       │   └── performance-defaults.yaml
│       ├── deployments/
│       │   ├── api.yaml
│       │   ├── worker.yaml
│       │   ├── browser-pool.yaml
│       │   └── proxy-pool.yaml
│       ├── services/
│       │   ├── api-svc.yaml
│       │   ├── proxy-api-svc.yaml
│       │   └── grafana-svc.yaml
│       ├── ingress/
│       │   ├── api-ingress.yaml
│       │   └── grafana-ingress.yaml
│       ├── hpa/
│       │   ├── api-hpa.yaml
│       │   └── worker-hpa.yaml
│       ├── cronjobs/
│       │   ├── sql_backup.yaml
│       │   ├── redis_snapshot_upload.yaml
│       │   ├── retention_job.yaml
│       │   ├── erasure_worker.yaml
│       │   ├── restore_drill.yaml
│       │   └── selector_regression.yaml
│       └── monitoring/
│           ├── prometheus-rules.yaml
│           ├── kustomization.yaml
│           └── grafana-dashboards/
│
├── src/                               # Python källkod
│   ├── main.py                        # Huvudapplikation entrypoint
│   ├── settings.py                    # Pydantic Settings
│   ├── webapp/                        # FastAPI webbapplikation
│   │   ├── __init__.py
│   │   ├── app.py                     # FastAPI app init
│   │   ├── api.py                     # Router mounting
│   │   ├── graphql.py                 # GraphQL endpoint
│   │   ├── auth.py                    # Autentisering
│   │   ├── deps.py                    # Dependency injection
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py
│   │   │   ├── data.py
│   │   │   ├── templates.py
│   │   │   ├── proxies.py
│   │   │   └── webhooks.py
│   │   ├── routers/                   # API routers
│   │   │   ├── __init__.py
│   │   │   ├── jobs.py
│   │   │   ├── data.py
│   │   │   ├── templates.py
│   │   │   ├── proxy.py
│   │   │   ├── exports.py
│   │   │   └── privacy.py
│   │   ├── middlewares/               # Middleware
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   └── rate_limit.py
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── webhook_dispatcher.py
│   │   │   ├── export_service.py
│   │   │   └── auth_service.py
│   │   ├── static/                    # Statiska filer
│   │   └── templates/                 # Jinja templates
│   ├── crawler/                       # Crawling-logik
│   │   ├── __init__.py
│   │   ├── sitemap_generator.py       # Sitemap BFS/DFS
│   │   ├── template_detector.py       # Malldetektering
│   │   ├── link_extractors.py         # Länkextraktion
│   │   ├── pagination.py              # Paginering
│   │   ├── infinite_scroll.py         # Infinite scroll
│   │   ├── url_queue.py               # URL-kö
│   │   ├── policy.py                  # Policy enforcement
│   │   └── reporters.py               # Progress reporting
│   ├── scraper/                       # Scraping-logik
│   │   ├── __init__.py
│   │   ├── base_scraper.py            # Bas-scraper
│   │   ├── http_scraper.py            # HTTP-baserad scraper
│   │   ├── selenium_scraper.py        # Browser-baserad scraper
│   │   ├── form_flows.py              # Formulärflöden
│   │   ├── template_extractor.py      # Mall-extraktion
│   │   ├── template_runtime.py        # Mall-körmotor
│   │   ├── xpath_suggester.py         # XPath-förslag
│   │   ├── regex_transformer.py       # Regex-transformation
│   │   ├── login_handler.py           # Inloggningshantering
│   │   └── image_downloader.py        # Bildnedladdning
│   ├── dsl/                           # DSL för mallar
│   │   ├── __init__.py
│   │   ├── schema.py                  # Pydantic DSL-schema
│   │   ├── validators.py              # Datavalidering
│   │   ├── transformers.py            # Datatransformation
│   │   ├── cross_field.py             # Korsvalidering
│   │   └── examples/                  # Exempelmallar
│   │       ├── vehicle_detail_v3.yml
│   │       ├── person_profile_v2.yml
│   │       └── company_profile_v2.yml
│   ├── proxy_pool/                    # Proxy-hantering
│   │   ├── __init__.py
│   │   ├── collector.py               # Proxy-insamling
│   │   ├── validator.py               # Proxy-validering
│   │   ├── quality_filter.py          # Kvalitetsfiltrering
│   │   ├── rotator.py                 # Proxy-rotation
│   │   ├── manager.py                 # Proxy-hantering
│   │   ├── monitor.py                 # Proxy-övervakning
│   │   └── api/
│   │       └── server.py              # Proxy API server
│   ├── anti_bot/                      # Anti-bot hantering
│   │   ├── __init__.py
│   │   ├── header_generator.py        # Header-generering
│   │   ├── session_manager.py         # Sessionshantering
│   │   ├── delay_strategy.py          # Fördröjningsstrategier
│   │   ├── credential_manager.py      # Credential management
│   │   ├── fallback_strategy.py       # Fallback-strategier
│   │   ├── fingerprint_profiles/      # Browser fingerprints
│   │   │   ├── chrome.json
│   │   │   ├── firefox.json
│   │   │   ├── safari.json
│   │   │   └── edge.json
│   │   ├── browser_stealth/           # Browser stealth
│   │   │   ├── __init__.py
│   │   │   ├── stealth_browser.py
│   │   │   ├── human_behavior.py
│   │   │   ├── cloudflare_bypass.py
│   │   │   └── captcha_solver.py
│   │   └── diagnostics/
│   │       └── diagnose_url.py
│   ├── database/                      # Databashantering
│   │   ├── __init__.py
│   │   ├── models.py                  # SQLAlchemy modeller
│   │   ├── manager.py                 # CRUD operations
│   │   ├── seed/                      # Seed-data
│   │   │   ├── persons.json
│   │   │   ├── companies.json
│   │   │   └── vehicles.json
│   │   ├── migrations/                # Databasmigrationer
│   │   │   ├── 0001_init.sql
│   │   │   └── 0002_indexes.sql
│   │   └── schema.sql                 # DB-schema
│   ├── scheduler/                     # Job scheduler
│   │   ├── __init__.py
│   │   ├── scheduler.py               # APScheduler setup
│   │   ├── job_definitions.py         # Job-definitioner
│   │   ├── job_monitor.py             # Job-övervakning
│   │   ├── notifier.py                # Notifieringar
│   │   └── jobs/                      # Job implementations
│   │       ├── __init__.py
│   │       ├── crawl_job.py
│   │       ├── scrape_job.py
│   │       ├── proxy_validate_job.py
│   │       ├── retention_job.py
│   │       ├── erasure_job.py
│   │       ├── backup_job.py
│   │       └── restore_drill_job.py
│   ├── exporters/                     # Data export
│   │   ├── __init__.py
│   │   ├── csv_exporter.py
│   │   ├── json_exporter.py
│   │   ├── excel_exporter.py
│   │   ├── sheets_exporter.py
│   │   ├── bigquery_exporter.py
│   │   ├── snowflake_exporter.py
│   │   └── elastic_exporter.py
│   ├── analysis/                      # Dataanalys
│   │   ├── __init__.py
│   │   ├── data_quality.py            # Great Expectations integration
│   │   ├── similarity_analysis.py     # Similaritetsanalys
│   │   ├── merinfo_analysis_tool.py   # Merinfo-analys
│   │   └── reports/
│   │       └── README.md
│   ├── plugins/                       # Plugin-system
│   │   ├── registry.yaml              # Plugin-register
│   │   └── examples/
│   │       ├── extractor_example.py
│   │       └── export_example.py
│   └── utils/                         # Verktyg och hjälpfunktioner
│       ├── __init__.py
│       ├── logger.py                  # JSON logging
│       ├── user_agent_rotator.py      # User-Agent rotation
│       ├── validators.py              # Datavalidering
│       ├── export_utils.py            # Export hjälpfunktioner
│       ├── pattern_detector.py        # Mönsterigenkänning
│       └── hashing.py                 # Hashingfunktioner
│
├── frontend/                          # React frontend (integreras med src/)
│   ├── package.json                   # Frontend dependencies
│   ├── tsconfig.json                  # TypeScript config
│   ├── vite.config.ts                 # Vite config
│   ├── src/
│   │   ├── main.tsx                   # React entrypoint
│   │   ├── App.tsx                    # Huvudkomponent
│   │   ├── api/                       # API-klienter
│   │   │   ├── http.ts
│   │   │   ├── rest.ts
│   │   │   └── graphql.ts
│   │   ├── components/                # React komponenter
│   │   │   ├── BrowserPanel.tsx       # Inbyggd webbläsare
│   │   │   ├── SelectorOverlay.tsx    # Peka-och-extrahera
│   │   │   ├── JobDashboard.tsx       # Job-dashboard
│   │   │   ├── ProxyHealth.tsx        # Proxy-hälsa
│   │   │   ├── PolicyEditor.tsx       # Policy-editor
│   │   │   └── PrivacyCenter.tsx      # GDPR-center
│   │   └── pages/                     # Sidor
│   │       ├── Home.tsx
│   │       ├── NewTemplateWizard.tsx  # Mall-wizard
│   │       ├── Jobs.tsx
│   │       ├── Templates.tsx
│   │       ├── Exports.tsx
│   │       └── Settings.tsx
│   └── public/
│       └── index.html
│
├── data/                              # Datalagring
│   ├── raw/                           # Rådata
│   │   ├── html/
│   │   └── json/
│   ├── processed/                     # Processad data
│   ├── exports/                       # Exportdata
│   │   ├── csv/
│   │   ├── json/
│   │   ├── excel/
│   │   └── google_sheets/
│   ├── images/                        # Nedladdade bilder
│   └── templates/                     # Mall-specifik data
│       ├── vehicle_detail/
│       ├── person_profile/
│       └── company_profile/
│
├── scripts/                           # Utility scripts
│   ├── init_db.py                     # Databas-initialisering
│   ├── seed_data.py                   # Seed-data import
│   ├── run_crawler.py                 # Crawler launcher
│   ├── run_scraper.py                 # Scraper launcher
│   ├── start_scheduler.py             # Scheduler start
│   ├── run_analysis.py                # Analys launcher
│   ├── diagnostic_tool.py             # Diagnostikverktyg
│   ├── backup_now.sh                  # Manuell backup
│   ├── restore_drill.sh               # Restore-övning
│   ├── s3_sync.sh                     # S3-synkronisering
│   └── generate_sdk.sh                # SDK-generering
│
├── tests/                             # Testsvit
│   ├── README.md                      # Test-guide
│   ├── conftest.py                    # Pytest konfiguration
│   ├── unit/                          # Unit tests
│   │   ├── test_selectors.py
│   │   ├── test_transformers.py
│   │   ├── test_validators.py
│   │   ├── test_template_runtime.py
│   │   ├── test_header_generator.py
│   │   └── test_db_manager.py
│   ├── integration/                   # Integration tests
│   │   ├── test_proxy_api.py
│   │   ├── test_crawler_queue.py
│   │   ├── test_scraper_http.py
│   │   ├── test_scraper_browser.py
│   │   ├── test_scheduler_jobs.py
│   │   └── test_exporters.py
│   ├── e2e/                           # End-to-end tests
│   │   ├── test_static_pagination.py
│   │   ├── test_infinite_scroll.py
│   │   ├── test_form_flows.py
│   │   ├── test_layout_drift.py
│   │   └── test_privacy_erasure.py
│   ├── fixtures/                      # Test fixtures
│   │   ├── golden_sets/               # Golden datasets
│   │   ├── html_samples/              # HTML-exempel
│   │   └── dsl/                       # DSL-mallar för test
│   └── synthetic_sites/               # Syntetiska test-sajter
│       ├── static_pagination/
│       ├── infinite_scroll/
│       ├── form_flow/
│       ├── varied_dom/
│       ├── Dockerfile
│       └── docker-compose.synthetic.yml
│
├── observability/                     # Observability setup
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── rules/
│   │       ├── scraping_alerts.yml
│   │       ├── proxy_pool_alerts.yml
│   │       └── cost_budget_alerts.yml
│   ├── grafana/
│   │   └── dashboards/
│   │       ├── scraping_overview.json
│   │       ├── proxy_health.json
│   │       ├── scheduler_queues.json
│   │       ├── db_dq_metrics.json
│   │       └── cost_overview.json
│   └── otel/
│       └── collector-config.yaml
│
├── sdk/                               # SDK:er
│   ├── python/                        # Python SDK
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/
│   │       └── scraping_sdk/
│   │           ├── __init__.py
│   │           ├── client.py
│   │           ├── templates.py
│   │           └── webhooks.py
│   └── typescript/                    # TypeScript SDK
│       ├── package.json
│       ├── tsconfig.json
│       ├── README.md
│       └── src/
│           ├── index.ts
│           ├── client.ts
│           ├── templates.ts
│           └── webhooks.ts
│
├── supabase/                          # Supabase integration
│   ├── config.toml                    # Supabase konfiguration
│   ├── migrations/                    # Supabase migrationer
│   │   ├── 0001_init.sql
│   │   ├── 0002_indexes.sql
│   │   ├── 0003_rls_policies.sql
│   │   └── 0004_functions_triggers.sql
│   ├── seed/                          # Supabase seed
│   │   ├── templates/
│   │   │   ├── vehicle_detail_v3.yml
│   │   │   ├── person_profile_v2.yml
│   │   │   └── company_profile_v2.yml
│   │   └── demo_data.sql
│   └── README.md
│
├── api_clients/                       # Auto-genererade API-klienter
│   ├── openapi/
│   │   ├── python/                    # Python OpenAPI client
│   │   └── typescript/                # TypeScript OpenAPI client
│   ├── postman/
│   │   └── collection.json            # Postman collection
│   └── README.md
│
└── .github/                           # CI/CD workflows
    ├── workflows/
    │   ├── 01_lint_type.yml           # Linting & typechecking
    │   ├── 02_unit_tests.yml          # Unit tests
    │   ├── 03_integration_tests.yml   # Integration tests
    │   ├── 04_e2e_tests.yml           # End-to-end tests
    │   ├── 05_security.yml            # Security scanning
    │   ├── 06_build_sbom_sign.yml     # Build, SBOM, signing
    │   ├── 07_deploy_staging.yml      # Deploy to staging
    │   ├── 08_selector_regression.yml # Selector regression tests
    │   ├── 09_canary_prod.yml         # Canary deployment
    │   └── 10_release_notes.yml       # Release notes
    ├── ISSUE_TEMPLATE.md              # Issue-mall
    ├── PULL_REQUEST_TEMPLATE.md       # PR-mall
    └── CODEOWNERS                     # Code owners
```

## Totalt antal filer: ~200+

Detta är den kompletta filstrukturen för ECaDP-plattformen enligt specifikationen.