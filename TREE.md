# Project Tree (Canonical)

> Denna karta är den kanoniska källan för mapp-/filstruktur.  
> Uppdatera när nya moduler tillkommer. Se längst ner hur du autogenererar.

## Root
projektet/
├─ README.md
├─ TREE.md
├─ CHANGELOG.md
├─ CONTRIBUTING.md
├─ CODE_OF_CONDUCT.md
├─ SECURITY.md
├─ LICENSE
├─ .gitignore
├─ .gitattributes
├─ .editorconfig
├─ .dockerignore
├─ .pre-commit-config.yaml
├─ pyproject.toml
├─ setup.py
├─ requirements.txt
├─ requirements_dev.txt
├─ mypy.ini
├─ ruff.toml
├─ pytest.ini
├─ Makefile
├─ package.json
├─ .env.example
├─ .envrc
├─ VERSION
└─ CODEOWNERS

## Konfiguration (globala, miljö & policies)
config/
├─ app_config.yml
├─ logging.yml
├─ performance-defaults.yml
├─ proxies.yml
├─ anti_bot.yml
├─ captcha.yml
├─ export_targets.yml
├─ api.yml
├─ auth.yml
├─ roles.yml
├─ feature_flags.yml
├─ domain_policies.yml
├─ rate_limits.yml
├─ alerts_thresholds.yml
├─ domain_policies/
│  └─ example.com.yml
└─ env/
   ├─ development.yml
   ├─ staging.yml
   └─ production.yml

## Dokumentation (arkitektur, API, runbooks, lag/etik)
docs/
├─ architecture.md
├─ system_design_decisions.md
├─ developer_guide.md
├─ usage_guide.md
├─ database_schema.md
├─ api_documentation.md
├─ openapi.yaml
├─ graphql/
│  └─ schema.graphql
├─ postman/
│  └─ collection.json
├─ anti_bot_strategy.md
├─ user_interface_design.md
├─ graphql_guide.md
├─ observability.md
├─ security.md
├─ roadmap.md
├─ risks.md
├─ slo_sla.md
├─ changelog.md
├─ lovable/
│  └─ prompt.md
├─ templates/
│  ├─ dsl.md
│  ├─ shared_transforms.yml
│  ├─ person_profile_v1.yml
│  ├─ company_profile_v1.yml
│  ├─ vehicle_detail_v3.yml
│  └─ examples/
│     ├─ example_list_page.yml
│     ├─ example_detail_page.yml
│     └─ form_flow_example.yml
├─ policies/
│  ├─ robots_tos_policy.md
│  ├─ gdpr_dpia_template.md
│  ├─ backup_restore_policy.md
│  ├─ retention_policy.md
│  ├─ erasure_policy.md
│  ├─ provenance_lineage_policy.md
│  ├─ rbac_policies.md
│  ├─ privacy_retention_matrix.md
│  ├─ dpia_template.md
│  ├─ data_processing_agreement.md
│  └─ legal_checklist.md
├─ runbooks/
│  ├─ 403_storm.md
│  ├─ 429_spike.md
│  ├─ layout_drift.md
│  ├─ proxy_drought.md
│  ├─ restore_drill.md
│  ├─ deletion_on_demand.md
│  └─ incident_comm_template.md
└─ observability_assets/
   ├─ grafana/
   │  ├─ proxypool_dashboard.json
   │  ├─ crawler_scraper_dashboard.json
   │  ├─ database_dashboard.json
   │  └─ cost_dashboard.json
   └─ prometheus/
      ├─ alerts.yml
      └─ recording_rules.yml

## Docker & K8s
docker/
├─ Dockerfile.app
├─ Dockerfile.worker
├─ Dockerfile.browser
├─ Dockerfile.synthetic
├─ Dockerfile
├─ entrypoint.sh
├─ docker-compose.yml
├─ docker-compose.dev.yml
├─ docker-compose.synthetic.yml
├─ kafka-rabbitmq.yml
├─ selenium-grid.yml
├─ playwright-workers.yml
├─ synthetic-sites/
│  ├─ docker-compose.yml
│  ├─ README.md
│  └─ sites/
│     ├─ static-list/...
│     ├─ js-infinite-scroll/...
│     ├─ form-flow/...
│     ├─ variable-dom/...
│     └─ captcha-lite/...
└─ k8s/
   ├─ base/
   │  ├─ namespace.yaml
   │  ├─ configmap.yaml
   │  ├─ secrets.example.yaml
   │  ├─ deployment-api.yaml
   │  ├─ deployment-workers.yaml
   │  ├─ deployment-proxypool.yaml
   │  ├─ service-api.yaml
   │  ├─ service-proxypool.yaml
   │  ├─ ingress.yaml
   │  ├─ hpa-api.yaml
   │  ├─ hpa-workers.yaml
   │  ├─ pdb-api.yaml
   │  ├─ pdb-workers.yaml
   │  ├─ cronjob-backup.yaml
   │  ├─ cronjob-redis-snapshot.yaml
   │  ├─ cronjob-retention.yaml
   │  ├─ cronjob-erasure.yaml
   │  ├─ cronjob-sbom.yaml
   │  └─ cronjob-cost-report.yaml
   └─ helm/
      ├─ Chart.yaml
      ├─ values.yaml
      └─ templates/...

## IaC (Terraform) & k8s manifests
iac/
├─ terraform/
│  ├─ README.md
│  ├─ envs/
│  │  ├─ dev/
│  │  │  ├─ backend.tf
│  │  │  ├─ main.tf
│  │  │  ├─ variables.tf
│  │  │  └─ outputs.tf
│  │  ├─ staging/...
│  │  └─ prod/...
│  └─ modules/
│     ├─ network/ (vpc.tf, subnets.tf, sg.tf)
│     ├─ eks/ (cluster.tf, nodegroups.tf, iam.tf)
│     ├─ rds/ (postgres.tf, parameter_groups.tf)
│     ├─ redis/ (elasticache.tf)
│     ├─ s3/ (buckets.tf, lifecycle.tf)
│     ├─ ecr/ (repos.tf)
│     └─ iam/ (roles.tf, policies.tf)
└─ k8s/
   ├─ namespaces/ (scraping.yaml, data.yaml, ops.yaml)
   ├─ secrets/external-secrets.yaml
   ├─ configmaps/ (app-config.yaml, anti-bot.yaml, performance-defaults.yaml)
   ├─ deployments/ (api.yaml, worker.yaml, browser-pool.yaml, proxy-pool.yaml)
   ├─ services/ (api-svc.yaml, proxy-api-svc.yaml, grafana-svc.yaml)
   ├─ ingress/ (api-ingress.yaml, grafana-ingress.yaml)
   ├─ hpa/ (api-hpa.yaml, worker-hpa.yaml)
   ├─ cronjobs/ (sql_backup.yaml, redis_snapshot_upload.yaml, retention_job.yaml, erasure_worker.yaml, restore_drill.yaml, selector_regression.yaml)
   └─ monitoring/ (prometheus-rules.yaml, grafana-dashboards/*.json, kustomization.yaml)

## Källkod (src)
src/
├─ __init__.py
├─ main.py
├─ settings.py
├─ webapp/
│  ├─ __init__.py
│  ├─ app.py
│  ├─ api.py
│  ├─ graphql.py
│  ├─ auth.py
│  ├─ deps.py
│  ├─ views.py
│  ├─ websocket.py
│  ├─ privacy_center.py
│  ├─ schemas/ (jobs.py, data.py, templates.py, proxies.py, webhooks.py)
│  ├─ routers/ (jobs.py, data.py, templates.py, proxy.py, exports.py, privacy.py)
│  ├─ middlewares/ (logging.py, rate_limit.py)
│  ├─ services/ (webhook_dispatcher.py, export_service.py, auth_service.py)
│  ├─ templates/ (base.html, dashboard.html, selector_tool.html, jobs.html, privacy.html, settings.html, README.md)
│  ├─ static/ (css/app.css, js/selector_inject.js, img/…)
│  └─ i18n/ (sv-SE.yml, en-US.yml)
├─ crawler/
│  ├─ __init__.py
│  ├─ sitemap_generator.py
│  ├─ template_detector.py
│  ├─ link_extractors.py
│  ├─ pagination.py
│  ├─ infinite_scroll.py
│  ├─ url_queue.py
│  ├─ policy.py
│  ├─ reporters.py
│  ├─ keywords_search.py
│  └─ emitters.py
├─ scraper/
│  ├─ __init__.py
│  ├─ base_scraper.py
│  ├─ http_scraper.py
│  ├─ selenium_scraper.py
│  ├─ form_flows.py
│  ├─ template_extractor.py
│  ├─ template_runtime.py
│  ├─ xpath_suggester.py
│  ├─ regex_transformer.py
│  ├─ login_handler.py
│  ├─ image_downloader.py
│  ├─ dsl/ (schema.py, validators.py, transformers.py, cross_field.py, examples/*.yml)
│  └─ adapters/
│     ├─ http/ (client.py, middlewares.py)
│     └─ browser/ (driver.py, interactions.py)
├─ proxy_pool/
│  ├─ __init__.py
│  ├─ collector.py
│  ├─ validator.py
│  ├─ quality_filter.py
│  ├─ rotator.py
│  ├─ manager.py
│  ├─ monitor.py
│  └─ api/ (__init__.py, server.py)
├─ anti_bot/
│  ├─ __init__.py
│  ├─ header_generator.py
│  ├─ session_manager.py
│  ├─ delay_strategy.py
│  ├─ credential_manager.py
│  ├─ fallback_strategy.py
│  ├─ fingerprint_profiles/ (chrome.json, firefox.json, safari.json, edge.json)
│  ├─ browser_stealth/ (__init__.py, stealth_browser.py, human_behavior.py, cloudflare_bypass.py, captcha_solver.py)
│  └─ diagnostics/ (__init__.py, diagnose_url.py)
├─ database/
│  ├─ __init__.py
│  ├─ models.py
│  ├─ manager.py
│  ├─ schema.sql
│  ├─ migrations/ (env.py, alembic.ini, versions/*.py, 0001_init.sql, 0002_indexes.sql)
│  └─ seed/ (persons.json, companies.json, vehicles.json)
├─ scheduler/
│  ├─ __init__.py
│  ├─ scheduler.py
│  ├─ job_definitions.py
│  ├─ job_monitor.py
│  ├─ notifier.py
│  └─ jobs/ (crawl_job.py, scrape_job.py, proxy_update_job.py, proxy_validate_job.py, retention_job.py, erasure_job.py, sql_backup_job.py, redis_snapshot_job.py, restore_drill_job.py, selector_regression_job.py, backup_job.py)
├─ exporters/
│  ├─ __init__.py
│  ├─ base.py
│  ├─ csv_exporter.py
│  ├─ json_exporter.py
│  ├─ excel_exporter.py
│  ├─ sheets_exporter.py
│  ├─ bigquery_exporter.py
│  ├─ snowflake_exporter.py
│  └─ elastic_exporter.py
├─ analysis/
│  ├─ __init__.py
│  ├─ data_quality.py
│  ├─ similarity_analysis.py
│  ├─ merinfo_analysis_tool.py
│  └─ reports/README.md
├─ plugins/
│  ├─ __init__.py
│  ├─ registry.yaml
│  └─ examples/ (extractor_example.py, export_example.py)
├─ connectors/
│  ├─ bigquery_client.py
│  ├─ snowflake_client.py
│  ├─ opensearch_client.py
│  ├─ google_sheets_client.py
│  └─ slack_webhook.py
└─ utils/
   ├─ __init__.py
   ├─ logger.py
   ├─ user_agent_rotator.py
   ├─ validators.py
   ├─ export_utils.py
   ├─ pattern_detector.py
   ├─ hashing.py
   ├─ cost_tracker.py
   ├─ idempotency.py
   ├─ hmac_utils.py
   ├─ rate_limiter.py
   ├─ pii_scanner.py
   └─ lineage.py

## Frontend (SPA)
frontend/
├─ package.json
├─ pnpm-lock.yaml
├─ tsconfig.json
├─ vite.config.ts
├─ tailwind.config.ts
├─ postcss.config.js
├─ .env.example
└─ src/
   ├─ main.tsx
   ├─ App.tsx
   ├─ index.css
   ├─ api/ (http.ts, rest.ts, graphql.ts)
   ├─ components/
   │  ├─ BrowserPanel.tsx
   │  ├─ SelectorOverlay.tsx
   │  ├─ SelectorPicker.tsx
   │  ├─ TemplateWizard.tsx
   │  ├─ JobDashboard.tsx
   │  ├─ ProxyDashboard.tsx
   │  ├─ DataPreview.tsx
   │  ├─ PolicyPanel.tsx
   │  ├─ PrivacyPanel.tsx
   │  └─ Charts/ (ThroughputChart.tsx, ErrorRateChart.tsx)
   ├─ pages/ (Home.tsx, Templates.tsx, Jobs.tsx, Exports.tsx, Settings.tsx, NewTemplateWizard.tsx)
   ├─ services/ (apiClient.ts, jobsApi.ts, templatesApi.ts, dataApi.ts, proxyApi.ts, privacyApi.ts, auth.ts)
   ├─ hooks/
   ├─ store/
   ├─ styles/
   ├─ utils/
   └─ assets/
      └─ README.md

## Data, artefakter & mallar
data/
├─ raw/html/.gitkeep
├─ raw/json/.gitkeep
├─ processed/.gitkeep
├─ exports/csv/.gitkeep
├─ exports/json/.gitkeep
├─ exports/excel/.gitkeep
├─ exports/google_sheets/.gitkeep
├─ images/.gitkeep
└─ templates/
   ├─ vehicle_detail/.gitkeep
   ├─ person_profile/.gitkeep
   ├─ company_profile/.gitkeep
   └─ .gitkeep

## Script & verktyg
scripts/
├─ init_db.py
├─ seed_data.py
├─ run_crawler.py
├─ run_scraper.py
├─ start_scheduler.py
├─ run_analysis.py
├─ diagnostic_tool.py
├─ backup_now.sh
├─ restore_drill.sh
├─ s3_sync.sh
├─ generate_sdk.sh
├─ export_postman.py
├─ gen_openapi_client.sh
├─ perf_probe.py
├─ sbom_generate.sh
├─ cosign_sign.sh
├─ attestation_slsa.sh
├─ comprehensive_structure_analyzer.py
└─ chaos/
   ├─ inject_network_latency.sh
   ├─ kill_worker_pod.sh
   └─ readme.md

## Tester (unit/integration/E2E/chaos/k6)
tests/
├─ README.md
├─ conftest.py
├─ unit/ (…)
├─ integration/ (…)
├─ e2e/
│  ├─ playwright.config.ts
│  ├─ selectors.spec.ts
│  ├─ forms_flow.spec.ts
│  ├─ infinite_scroll.spec.ts
│  └─ variable_dom.spec.ts
├─ fixtures/
│  ├─ golden_sets/{vehicle_detail,person_profile,company_profile}/.gitkeep
│  ├─ html_samples/{vehicle_detail,person_profile,company_profile}/.gitkeep
│  ├─ html/ (vehicle_detail_*.html, company_profile_*.html, person_profile_*.html)
│  ├─ templates/ (vehicle_detail_v3.yml, company_profile_v1.yml, person_profile_v1.yml)
│  ├─ dsl/ (vehicle_detail_v3.yml, person_profile_v2.yml, company_profile_v2.yml)
│  └─ data/expected_outputs.json
├─ property_based/ (test_selectors_hypothesis.py, test_transformers_hypothesis.py)
├─ mutation/mutmut_config.toml
├─ fuzz/test_fuzz_extractors.py
├─ k6/ (crawl_throughput.js, scrape_latency.js)
├─ chaos/ (test_worker_kill_recovery.py, test_proxy_pool_degradation.py)
├─ synthetic_sites/
│  ├─ Dockerfile
│  ├─ docker-compose.synthetic.yml
│  ├─ static_pagination/ (server.py, templates/.gitkeep, data.json)
│  ├─ infinite_scroll/ (server.py, assets/.gitkeep)
│  ├─ form_flow/ (server.py, templates/.gitkeep)
│  └─ varied_dom/ (server.py, variants/.gitkeep)
└─ test_*.py  # api, webapp, scheduler, anti_bot, proxy_pool, exports, template_drift

## Observability
observability/
├─ prometheus/
│  ├─ rules/ (scraping_alerts.yml, proxy_pool_alerts.yml, cost_budget_alerts.yml)
│  └─ prometheus.yml
├─ grafana/dashboards/
│  ├─ scraping_overview.json
│  ├─ proxy_health.json
│  ├─ scheduler_queues.json
│  ├─ db_dq_metrics.json
│  └─ cost_overview.json
└─ otel/collector-config.yaml

## SDKs
sdk/
├─ python/
│  ├─ pyproject.toml
│  ├─ README.md
│  ├─ src/scraping_sdk/ (__init__.py, client.py, templates.py, webhooks.py)
│  └─ sdk_client/ (__init__.py, client.py, webhooks.py, models.py, idempotency.py, retry.py)
└─ typescript/
   ├─ package.json
   ├─ tsconfig.json
   ├─ README.md
   └─ src/ (index.ts, client.ts, templates.ts, webhooks.ts, models.ts, idempotency.ts, retry.ts, test/client.test.ts)

## Supabase (valfritt)
supabase/
├─ .env.example
├─ migrations/ (0001_init.sql … 0007_erasure_cascade.sql)
├─ seed/templates/ (vehicle_detail_v3.yml, person_profile_v2.yml, company_profile_v2.yml)
└─ README.md

## API-klienter
api_clients/
├─ openapi/
│  ├─ python/.gitkeep
│  └─ typescript/.gitkeep
├─ postman/collection.json
└─ README.md

## Exempel & klienter
examples/
├─ crawl_example.md
├─ scrape_vehicle_detail.md
├─ export_to_sheets.md
├─ api_usage.md
├─ import_urls.csv
├─ export_query_examples.md
└─ api_calls.http

clients/
├─ postman_collection.json
└─ insomnia/insomnia_export.yaml

## Monitoring (lokal dev)
monitoring/
├─ docker-compose.obsv.yml
└─ grafana/provisioning/
   ├─ datasources/prometheus.yaml
   └─ dashboards/
      ├─ proxypool_dashboard.json
      ├─ crawler_scraper_dashboard.json
      ├─ database_dashboard.json
      └─ cost_dashboard.json

## Juridik & etik
legal/
├─ README.md
├─ robots_tos_checklist.md
├─ privacy_policy_internal.md
└─ data_processing_agreements/.gitkeep

## Bin
bin/
├─ dev-up
├─ dev-down
├─ gen-openapi-clients
└─ fmt

## Browser Extension
extension/
├─ README.md
├─ manifest.json
├─ background.js
├─ content_script.js
├─ popup.html
├─ popup.js
├─ styles.css
└─ icons/ (icon16.png, icon48.png, icon128.png)

## Ops – backup/retention/erasure
ops/
├─ backup/ (wal-g.yaml, pgbackrest.conf, verify_backup.sh)
├─ retention/ (retention_policy.yml, retention_runner.py)
├─ erasure/ (erasure_worker.py, erasure_api.md)
└─ s3/ (lifecycle_raw_html.json, lifecycle_db_backups.json, lifecycle_exports.json)

## Generated (klienter)
generated/
├─ python/openapi_client/.gitkeep
└─ typescript/openapi_client/.gitkeep

## GitHub (CI/CD)
.github/
└─ workflows/
   ├─ 01_lint_type.yml
   ├─ 02_unit_tests.yml
   ├─ 03_integration_tests.yml
   ├─ 04_e2e_tests.yml
   ├─ 05_security.yml
   ├─ 06_build_sbom_sign.yml
   ├─ 07_deploy_staging.yml
   ├─ 08_selector_regression.yml
   ├─ 09_canary_prod.yml
   ├─ 10_release_notes.yml
   ├─ ci.yml
   ├─ build_and_push.yml
   ├─ security_sast.yml
   ├─ dependency_review.yml
   ├─ deploy_staging.yml
   ├─ deploy_canary.yml
   ├─ nightly_selector_regression.yml
   ├─ sbom.yml
   └─ cosign_verify.yml

---

## Regenerera denna fil
- **Snabbt (UNIX):**
  ```bash
  tree -a -I 'node_modules|.venv|__pycache__|.git|dist|build|.pytest_cache|.mypy_cache' > TREE.md
