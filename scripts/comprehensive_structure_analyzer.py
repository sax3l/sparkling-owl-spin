#!/usr/bin/env python3
"""
Comprehensive structure analyzer for the crawler project.
Analyzes the current project structure against the complete required structure.
Merges both specification structures intelligently to show full requirements.
"""

import os
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

def get_required_files() -> Dict[str, List[str]]:
    """Get the complete list of required files organized by category."""
    return {
        "root": [
            "README.md",
            "TREE.md",
            "CHANGELOG.md", 
            "CONTRIBUTING.md",
            "CODE_OF_CONDUCT.md", 
            "SECURITY.md",
            "LICENSE",
            ".gitignore",
            ".gitattributes",
            ".editorconfig", 
            ".dockerignore",
            ".pre-commit-config.yaml",
            ".env.example",
            ".envrc",
            "Makefile",
            "pyproject.toml",
            "requirements.txt", 
            "requirements_dev.txt",
            "package.json",
            "VERSION",
            "mypy.ini",
            "ruff.toml", 
            "pytest.ini",
            "CODEOWNERS"
        ],
        
        "config": [
            "config/app_config.yml",
            "config/logging.yml", 
            "config/performance-defaults.yml",
            "config/proxies.yml",
            "config/anti_bot.yml",
            "config/captcha.yml",
            "config/export_targets.yml",
            "config/api.yml",
            "config/auth.yml",
            "config/roles.yml",
            "config/feature_flags.yml",
            "config/domain_policies.yml",
            "config/rate_limits.yml", 
            "config/alerts_thresholds.yml",
            "config/domain_policies/example.com.yml",
            "config/env/development.yml",
            "config/env/staging.yml", 
            "config/env/production.yml"
        ],
        
        "docs": [
            "docs/architecture.md",
            "docs/system_design_decisions.md",
            "docs/developer_guide.md",
            "docs/usage_guide.md", 
            "docs/database_schema.md",
            "docs/api_documentation.md",
            "docs/openapi.yaml",
            "docs/graphql/schema.graphql",
            "docs/postman/collection.json",
            "docs/policies/robots_tos_policy.md",
            "docs/policies/gdpr_dpia_template.md",
            "docs/policies/s3_lifecycle_raw_html.json",
            "docs/policies/s3_lifecycle_db_backups.json",
            "docs/policies/s3_lifecycle_exports.json",
            "docs/policies/backup_restore_policy.md",
            "docs/policies/retention_policy.md",
            "docs/policies/erasure_policy.md",
            "docs/policies/provenance_lineage_policy.md",
            "docs/runbooks/403_storm.md",
            "docs/runbooks/429_spike.md",
            "docs/runbooks/layout_drift.md",
            "docs/runbooks/proxy_drought.md",
            "docs/runbooks/restore_drill.md",
            "docs/slo_sla.md",
            "docs/changelog.md",
            "docs/lovable/prompt.md",
            "docs/anti_bot_strategy.md",
            "docs/user_interface_design.md",
            "docs/graphql_guide.md", 
            "docs/observability.md",
            "docs/security.md",
            "docs/roadmap.md",
            "docs/risks.md",
            "docs/lovable_prompt.md",
            "docs/templates/dsl.md",
            "docs/templates/person_profile_v1.yml",
            "docs/templates/company_profile_v1.yml",
            "docs/templates/vehicle_detail_v3.yml",
            "docs/templates/shared_transforms.yml",
            "docs/templates/examples/example_list_page.yml",
            "docs/templates/examples/example_detail_page.yml",
            "docs/templates/examples/form_flow_example.yml",
            "docs/policies/rbac_policies.md",
            "docs/policies/privacy_retention_matrix.md",
            "docs/policies/dpia_template.md",
            "docs/policies/data_processing_agreement.md",
            "docs/policies/legal_checklist.md",
            "docs/runbooks/deletion_on_demand.md",
            "docs/runbooks/incident_comm_template.md",
            "docs/observability_assets/grafana/proxypool_dashboard.json",
            "docs/observability_assets/grafana/crawler_scraper_dashboard.json",
            "docs/observability_assets/grafana/database_dashboard.json",
            "docs/observability_assets/grafana/cost_dashboard.json",
            "docs/observability_assets/prometheus/alerts.yml",
            "docs/observability_assets/prometheus/recording_rules.yml"
        ],

        "docker": [
            "docker/Dockerfile.app",
            "docker/Dockerfile.worker", 
            "docker/Dockerfile.browser",
            "docker/Dockerfile.synthetic",
            "docker/entrypoint.sh",
            "docker/docker-compose.yml",
            "docker/docker-compose.dev.yml",
            "docker/docker-compose.synthetic.yml",
            "docker/dev/grafana/provisioning/README.md",
            "docker/dev/prometheus/prometheus.yml",
            "docker/Dockerfile",
            "docker/dev/Dockerfile",
            "docker/kafka-rabbitmq.yml",
            "docker/selenium-grid.yml",
            "docker/playwright-workers.yml",
            "docker/synthetic-sites/docker-compose.yml",
            "docker/synthetic-sites/sites/static-list/README.md",
            "docker/synthetic-sites/sites/js-infinite-scroll/README.md",
            "docker/synthetic-sites/sites/form-flow/README.md",
            "docker/synthetic-sites/sites/variable-dom/README.md",
            "docker/synthetic-sites/sites/captcha-lite/README.md",
            "docker/synthetic-sites/README.md",
            "docker/k8s/base/namespace.yaml",
            "docker/k8s/base/configmap.yaml",
            "docker/k8s/base/secrets.example.yaml",
            "docker/k8s/base/deployment-api.yaml",
            "docker/k8s/base/deployment-workers.yaml",
            "docker/k8s/base/deployment-proxypool.yaml",
            "docker/k8s/base/service-api.yaml",
            "docker/k8s/base/service-proxypool.yaml",
            "docker/k8s/base/ingress.yaml",
            "docker/k8s/base/hpa-api.yaml",
            "docker/k8s/base/hpa-workers.yaml",
            "docker/k8s/base/pdb-api.yaml",
            "docker/k8s/base/pdb-workers.yaml",
            "docker/k8s/base/cronjob-backup.yaml",
            "docker/k8s/base/cronjob-redis-snapshot.yaml",
            "docker/k8s/base/cronjob-retention.yaml",
            "docker/k8s/base/cronjob-erasure.yaml",
            "docker/k8s/base/cronjob-sbom.yaml",
            "docker/k8s/base/cronjob-cost-report.yaml",
            "docker/k8s/helm/Chart.yaml",
            "docker/k8s/helm/values.yaml",
            "docker/k8s/helm/templates/README.md"
        ],

        "iac": [
            "iac/terraform/modules/network/README.md",
            "iac/terraform/modules/eks/README.md", 
            "iac/terraform/modules/rds/README.md",
            "iac/terraform/modules/redis/README.md",
            "iac/terraform/modules/s3/README.md",
            "iac/terraform/envs/dev/README.md",
            "iac/terraform/envs/staging/README.md",
            "iac/terraform/envs/prod/README.md",
            "iac/terraform/README.md",
            "iac/k8s/namespaces/scraping.yaml",
            "iac/k8s/namespaces/data.yaml",
            "iac/k8s/namespaces/ops.yaml",
            "iac/k8s/secrets/external-secrets.yaml",
            "iac/k8s/configmaps/app-config.yaml",
            "iac/k8s/configmaps/anti-bot.yaml", 
            "iac/k8s/configmaps/performance-defaults.yaml",
            "iac/k8s/deployments/api.yaml",
            "iac/k8s/deployments/worker.yaml",
            "iac/k8s/deployments/browser-pool.yaml",
            "iac/k8s/deployments/proxy-pool.yaml",
            "iac/k8s/services/api-svc.yaml",
            "iac/k8s/services/proxy-api-svc.yaml",
            "iac/k8s/services/grafana-svc.yaml",
            "iac/k8s/ingress/api-ingress.yaml",
            "iac/k8s/ingress/grafana-ingress.yaml",
            "iac/k8s/hpa/api-hpa.yaml",
            "iac/k8s/hpa/worker-hpa.yaml",
            "iac/k8s/cronjobs/sql_backup.yaml",
            "iac/k8s/cronjobs/redis_snapshot_upload.yaml",
            "iac/k8s/cronjobs/retention_job.yaml", 
            "iac/k8s/cronjobs/erasure_worker.yaml",
            "iac/k8s/cronjobs/restore_drill.yaml",
            "iac/k8s/cronjobs/selector_regression.yaml",
            "iac/k8s/monitoring/prometheus-rules.yaml",
            "iac/k8s/monitoring/grafana-dashboards/scraping_overview.json",
            "iac/k8s/monitoring/grafana-dashboards/proxy_health.json",
            "iac/k8s/monitoring/grafana-dashboards/scheduler_queues.json",
            "iac/k8s/monitoring/grafana-dashboards/db_dq_metrics.json",
            "iac/k8s/monitoring/grafana-dashboards/cost_overview.json",
            "iac/k8s/monitoring/kustomization.yaml"
        ],
        
        "src_webapp": [
            "src/webapp/__init__.py",
            "src/webapp/app.py",
            "src/webapp/api.py",
            "src/webapp/graphql.py",
            "src/webapp/auth.py",
            "src/webapp/deps.py",
            "src/webapp/views.py",
            "src/webapp/websocket.py",
            "src/webapp/privacy_center.py",
            "src/webapp/schemas/jobs.py",
            "src/webapp/schemas/data.py",
            "src/webapp/schemas/templates.py",
            "src/webapp/schemas/proxies.py",
            "src/webapp/schemas/webhooks.py",
            "src/webapp/routers/jobs.py",
            "src/webapp/routers/data.py",
            "src/webapp/routers/templates.py",
            "src/webapp/routers/proxy.py",
            "src/webapp/routers/exports.py",
            "src/webapp/routers/privacy.py",
            "src/webapp/middlewares/logging.py",
            "src/webapp/middlewares/rate_limit.py",
            "src/webapp/services/webhook_dispatcher.py",
            "src/webapp/services/export_service.py",
            "src/webapp/services/auth_service.py",
            "src/webapp/static/README.md",
            "src/webapp/templates/README.md",
            "src/webapp/i18n/sv-SE.yml",
            "src/webapp/i18n/en-US.yml",
            "src/webapp/templates/base.html",
            "src/webapp/templates/dashboard.html",
            "src/webapp/templates/selector_tool.html",
            "src/webapp/templates/jobs.html",
            "src/webapp/templates/privacy.html",
            "src/webapp/templates/settings.html",
            "src/webapp/static/css/app.css",
            "src/webapp/static/js/selector_inject.js",
            "src/webapp/static/img/README.md"
        ],

        "src_crawler": [
            "src/crawler/__init__.py",
            "src/crawler/sitemap_generator.py",
            "src/crawler/template_detector.py",
            "src/crawler/link_extractors.py",
            "src/crawler/pagination.py",
            "src/crawler/infinite_scroll.py",
            "src/crawler/url_queue.py",
            "src/crawler/policy.py",
            "src/crawler/reporters.py",
            "src/crawler/keywords_search.py",
            "src/crawler/emitters.py"
        ],

        "src_scraper": [
            "src/scraper/__init__.py",
            "src/scraper/base_scraper.py",
            "src/scraper/http_scraper.py",
            "src/scraper/selenium_scraper.py",
            "src/scraper/form_flows.py",
            "src/scraper/template_extractor.py", 
            "src/scraper/template_runtime.py",
            "src/scraper/xpath_suggester.py",
            "src/scraper/regex_transformer.py",
            "src/scraper/login_handler.py",
            "src/scraper/image_downloader.py",
            "src/scraper/dsl/schema.py",
            "src/scraper/dsl/validators.py",
            "src/scraper/dsl/transformers.py",
            "src/scraper/dsl/cross_field.py",
            "src/scraper/dsl/examples/vehicle_detail_v3.yml",
            "src/scraper/dsl/examples/person_profile_v2.yml",
            "src/scraper/dsl/examples/company_profile_v2.yml",
            "src/scraper/adapters/http/client.py",
            "src/scraper/adapters/http/middlewares.py",
            "src/scraper/adapters/browser/driver.py",
            "src/scraper/adapters/browser/interactions.py"
        ],

        "src_exporters": [
            "src/exporters/__init__.py",
            "src/exporters/base.py",
            "src/exporters/csv_exporter.py",
            "src/exporters/json_exporter.py", 
            "src/exporters/excel_exporter.py",
            "src/exporters/sheets_exporter.py",
            "src/exporters/bigquery_exporter.py",
            "src/exporters/snowflake_exporter.py",
            "src/exporters/elastic_exporter.py",
            "src/exporters/google_sheets_exporter.py",
            "src/exporters/opensearch_exporter.py"
        ],

        "src_complete": [
            "src/__init__.py",
            "src/main.py",
            "src/settings.py",
            "src/proxy_pool/__init__.py",
            "src/proxy_pool/collector.py",
            "src/proxy_pool/validator.py",
            "src/proxy_pool/quality_filter.py", 
            "src/proxy_pool/rotator.py",
            "src/proxy_pool/manager.py",
            "src/proxy_pool/monitor.py",
            "src/proxy_pool/api/__init__.py",
            "src/proxy_pool/api/server.py",
            "src/anti_bot/__init__.py",
            "src/anti_bot/header_generator.py",
            "src/anti_bot/session_manager.py",
            "src/anti_bot/delay_strategy.py",
            "src/anti_bot/credential_manager.py",
            "src/anti_bot/fallback_strategy.py",
            "src/anti_bot/fingerprint_profiles/chrome.json",
            "src/anti_bot/fingerprint_profiles/firefox.json",
            "src/anti_bot/fingerprint_profiles/safari.json",
            "src/anti_bot/fingerprint_profiles/edge.json",
            "src/anti_bot/browser_stealth/__init__.py",
            "src/anti_bot/browser_stealth/stealth_browser.py",
            "src/anti_bot/browser_stealth/human_behavior.py",
            "src/anti_bot/browser_stealth/cloudflare_bypass.py",
            "src/anti_bot/browser_stealth/captcha_solver.py",
            "src/anti_bot/diagnostics/__init__.py",
            "src/anti_bot/diagnostics/diagnose_url.py",
            "src/database/__init__.py",
            "src/database/models.py",
            "src/database/manager.py",
            "src/database/seed/persons.json",
            "src/database/seed/companies.json",
            "src/database/seed/vehicles.json",
            "src/database/migrations/0001_init.sql",
            "src/database/migrations/0002_indexes.sql",
            "src/database/migrations/env.py",
            "src/database/migrations/alembic.ini",
            "src/database/migrations/versions/0001_init.py",
            "src/database/migrations/versions/0002_add_indexes.py",
            "src/database/migrations/versions/0003_template_versioning.py",
            "src/database/migrations/versions/0004_dq_tables.py",
            "src/database/schema.sql",
            "src/scheduler/__init__.py",
            "src/scheduler/scheduler.py",
            "src/scheduler/job_definitions.py",
            "src/scheduler/job_monitor.py",
            "src/scheduler/notifier.py",
            "src/scheduler/jobs/crawl_job.py",
            "src/scheduler/jobs/scrape_job.py",
            "src/scheduler/jobs/proxy_update_job.py",
            "src/scheduler/jobs/proxy_validate_job.py",
            "src/scheduler/jobs/retention_job.py",
            "src/scheduler/jobs/erasure_job.py",
            "src/scheduler/jobs/sql_backup_job.py",
            "src/scheduler/jobs/redis_snapshot_job.py",
            "src/scheduler/jobs/restore_drill_job.py",
            "src/scheduler/jobs/selector_regression_job.py",
            "src/scheduler/jobs/backup_job.py",
            "src/analysis/__init__.py",
            "src/analysis/data_quality.py",
            "src/analysis/similarity_analysis.py",
            "src/analysis/merinfo_analysis_tool.py",
            "src/analysis/reports/README.md",
            "src/plugins/__init__.py",
            "src/plugins/registry.yaml",
            "src/plugins/examples/extractor_example.py",
            "src/plugins/examples/export_example.py",
            "src/plugins/sample_extractor/__init__.py",
            "src/plugins/sample_extractor/plugin.py",
            "src/plugins/sample_extractor/README.md",
            "src/plugins/sample_export_target/__init__.py",
            "src/plugins/sample_export_target/plugin.py",
            "src/plugins/sample_export_target/README.md",
            "src/plugins/README.md",
            "src/utils/__init__.py",
            "src/utils/logger.py",
            "src/utils/user_agent_rotator.py",
            "src/utils/validators.py",
            "src/utils/export_utils.py",
            "src/utils/pattern_detector.py",
            "src/utils/hashing.py",
            "src/utils/cost_tracker.py",
            "src/utils/idempotency.py",
            "src/utils/hmac_utils.py",
            "src/utils/rate_limiter.py",
            "src/utils/pii_scanner.py",
            "src/utils/lineage.py",
            "src/utils/otel.py",
            "src/ml/__init__.py",
            "src/ml/template_classifier.py",
            "src/ml/selector_ranker.py",
            "src/ml/drift_detector.py",
            "src/ml/features/dom_features.py",
            "src/ml/features/text_features.py",
            "src/ml/pipelines/train_classifier.py",
            "src/ml/pipelines/train_ranker.py",
            "src/ml/pipelines/eval_report.py",
            "src/connectors/__init__.py",
            "src/connectors/bigquery_client.py",
            "src/connectors/snowflake_client.py",
            "src/connectors/opensearch_client.py",
            "src/connectors/google_sheets_client.py",
            "src/connectors/slack_webhook.py"
        ],

        "frontend": [
            "frontend/package.json",
            "frontend/tsconfig.json",
            "frontend/vite.config.ts",
            "frontend/postcss.config.js",
            "frontend/tailwind.config.js",
            "frontend/tailwind.config.ts",
            "frontend/pnpm-lock.yaml",
            "frontend/.env.example",
            "frontend/src/main.tsx",
            "frontend/src/App.tsx",
            "frontend/src/index.css",
            "frontend/src/api/http.ts",
            "frontend/src/api/rest.ts",
            "frontend/src/api/graphql.ts",
            "frontend/src/components/BrowserPanel.tsx",
            "frontend/src/components/SelectorOverlay.tsx",
            "frontend/src/components/JobDashboard.tsx",
            "frontend/src/components/ProxyHealth.tsx",
            "frontend/src/components/PolicyEditor.tsx",
            "frontend/src/components/PrivacyCenter.tsx",
            "frontend/src/components/SelectorPicker.tsx",
            "frontend/src/components/TemplateWizard.tsx",
            "frontend/src/components/DataPreview.tsx",
            "frontend/src/components/PolicyPanel.tsx",
            "frontend/src/components/PrivacyPanel.tsx",
            "frontend/src/components/ProxyDashboard.tsx",
            "frontend/src/components/Charts/ThroughputChart.tsx",
            "frontend/src/components/Charts/ErrorRateChart.tsx",
            "frontend/src/pages/Home.tsx",
            "frontend/src/pages/NewTemplateWizard.tsx",
            "frontend/src/pages/Jobs.tsx",
            "frontend/src/pages/Templates.tsx",
            "frontend/src/pages/Exports.tsx",
            "frontend/src/pages/Settings.tsx",
            "frontend/src/hooks/README.md",
            "frontend/src/store/README.md",
            "frontend/src/styles/README.md",
            "frontend/src/utils/README.md",
            "frontend/src/services/apiClient.ts",
            "frontend/src/services/jobsApi.ts",
            "frontend/src/services/templatesApi.ts",
            "frontend/src/services/dataApi.ts",
            "frontend/src/services/proxyApi.ts",
            "frontend/src/services/privacyApi.ts",
            "frontend/src/services/auth.ts",
            "frontend/public/index.html",
            "frontend/src/assets/README.md"
        ],

        "data": [
            "data/raw/html/.gitkeep",
            "data/raw/json/.gitkeep",
            "data/processed/.gitkeep",
            "data/exports/csv/.gitkeep",
            "data/exports/json/.gitkeep",
            "data/exports/excel/.gitkeep",
            "data/exports/google_sheets/.gitkeep",
            "data/images/.gitkeep",
            "data/templates/vehicle_detail/.gitkeep",
            "data/templates/person_profile/.gitkeep",
            "data/templates/company_profile/.gitkeep",
            "data/templates/.gitkeep"
        ],

        "scripts": [
            "scripts/init_db.py",
            "scripts/seed_data.py",
            "scripts/run_crawler.py",
            "scripts/run_scraper.py",
            "scripts/start_scheduler.py",
            "scripts/run_analysis.py",
            "scripts/diagnostic_tool.py",
            "scripts/backup.sh",
            "scripts/restore_drill.sh",
            "scripts/generate_sdk.sh",
            "scripts/backup_now.sh",
            "scripts/s3_sync.sh",
            "scripts/restore_integrity_check.py",
            "scripts/export_postman.py",
            "scripts/gen_openapi_client.sh",
            "scripts/perf_probe.py",
            "scripts/sbom_generate.sh",
            "scripts/cosign_sign.sh",
            "scripts/attestation_slsa.sh",
            "scripts/chaos/inject_network_latency.sh",
            "scripts/chaos/kill_worker_pod.sh",
            "scripts/chaos/readme.md"
        ],

        "tests_complete": [
            "tests/__init__.py",
            "tests/README.md",
            "tests/conftest.py",
            "tests/pytest.ini",
            "tests/unit/test_selectors.py",
            "tests/unit/test_transformers.py",
            "tests/unit/test_validators.py",
            "tests/unit/test_template_runtime.py",
            "tests/unit/test_header_generator.py",
            "tests/unit/test_db_manager.py",
            "tests/unit/test_utils.py",
            "tests/unit/test_regex_transformer.py",
            "tests/unit/test_delay_strategy.py",
            "tests/unit/test_lineage.py",
            "tests/unit/test_pii_scanner.py",
            "tests/unit/test_rate_limiter.py",
            "tests/integration/test_proxy_api.py",
            "tests/integration/test_crawler_queue.py",
            "tests/integration/test_scraper_http.py",
            "tests/integration/test_scraper_browser.py",
            "tests/integration/test_scheduler_jobs.py",
            "tests/integration/test_exports.py",
            "tests/integration/test_database.py",
            "tests/integration/test_migrations.py",
            "tests/integration/test_crawler_integration.py",
            "tests/integration/test_scraper_integration.py",
            "tests/integration/test_exporters.py",
            "tests/integration/test_privacy_center.py",
            "tests/e2e/test_static_pagination.py",
            "tests/e2e/test_infinite_scroll.py",
            "tests/e2e/test_form_flow_vin_regnr.py",
            "tests/e2e/test_layout_drift_resilience.py",
            "tests/e2e/test_privacy_erasure.py",
            "tests/e2e/playwright.config.ts",
            "tests/e2e/selectors.spec.ts",
            "tests/e2e/forms_flow.spec.ts",
            "tests/e2e/infinite_scroll.spec.ts",
            "tests/e2e/variable_dom.spec.ts",
            "tests/fixtures/golden_sets/vehicle_detail/.gitkeep",
            "tests/fixtures/golden_sets/person_profile/.gitkeep",
            "tests/fixtures/golden_sets/company_profile/.gitkeep",
            "tests/fixtures/html_samples/vehicle_detail/.gitkeep",
            "tests/fixtures/html_samples/person_profile/.gitkeep",
            "tests/fixtures/html_samples/company_profile/.gitkeep",
            "tests/fixtures/dsl/vehicle_detail_v3.yml",
            "tests/fixtures/dsl/person_profile_v2.yml",
            "tests/fixtures/dsl/company_profile_v2.yml",
            "tests/fixtures/html/vehicle_detail_1.html",
            "tests/fixtures/html/company_profile_1.html",
            "tests/fixtures/html/person_profile_1.html",
            "tests/fixtures/templates/vehicle_detail_v3.yml",
            "tests/fixtures/templates/company_profile_v1.yml",
            "tests/fixtures/templates/person_profile_v1.yml",
            "tests/fixtures/data/expected_outputs.json",
            "tests/synthetic_sites/Dockerfile",
            "tests/synthetic_sites/docker-compose.synthetic.yml",
            "tests/synthetic_sites/static_pagination/server.py",
            "tests/synthetic_sites/static_pagination/templates/.gitkeep",
            "tests/synthetic_sites/static_pagination/data.json",
            "tests/synthetic_sites/infinite_scroll/server.py",
            "tests/synthetic_sites/infinite_scroll/assets/.gitkeep",
            "tests/synthetic_sites/form_flow/server.py",
            "tests/synthetic_sites/form_flow/templates/.gitkeep",
            "tests/synthetic_sites/varied_dom/server.py",
            "tests/synthetic_sites/varied_dom/variants/.gitkeep",
            "tests/property_based/test_selectors_hypothesis.py",
            "tests/property_based/test_transformers_hypothesis.py",
            "tests/mutation/mutmut_config.toml",
            "tests/fuzz/test_fuzz_extractors.py",
            "tests/k6/crawl_throughput.js",
            "tests/k6/scrape_latency.js",
            "tests/chaos/test_worker_kill_recovery.py",
            "tests/chaos/test_proxy_pool_degradation.py",
            "tests/test_api.py",
            "tests/test_webapp.py",
            "tests/test_scheduler.py",
            "tests/test_anti_bot.py",
            "tests/test_proxy_pool.py",
            "tests/test_exports.py",
            "tests/test_template_drift.py"
        ],

        "observability": [
            "observability/prometheus/rules/scraping_alerts.yml",
            "observability/prometheus/rules/proxy_pool_alerts.yml",
            "observability/prometheus/rules/cost_budget_alerts.yml",
            "observability/prometheus/prometheus.yml",
            "observability/grafana/dashboards/scraping_overview.json",
            "observability/grafana/dashboards/proxy_health.json",
            "observability/grafana/dashboards/scheduler_queues.json",
            "observability/grafana/dashboards/db_dq_metrics.json",
            "observability/grafana/dashboards/cost_overview.json",
            "observability/otel/collector-config.yaml"
        ],

        "sdk": [
            "sdk/python/pyproject.toml",
            "sdk/python/README.md",
            "sdk/python/src/scraping_sdk/__init__.py",
            "sdk/python/src/scraping_sdk/client.py",
            "sdk/python/src/scraping_sdk/templates.py",
            "sdk/python/src/scraping_sdk/webhooks.py",
            "sdk/python/sdk_client/__init__.py",
            "sdk/python/sdk_client/client.py",
            "sdk/python/sdk_client/webhooks.py",
            "sdk/python/sdk_client/models.py",
            "sdk/python/sdk_client/idempotency.py",
            "sdk/python/sdk_client/retry.py",
            "sdk/python/tests/test_client.py",
            "sdk/typescript/package.json",
            "sdk/typescript/tsconfig.json",
            "sdk/typescript/README.md",
            "sdk/typescript/src/index.ts",
            "sdk/typescript/src/client.ts",
            "sdk/typescript/src/templates.ts",
            "sdk/typescript/src/webhooks.ts",
            "sdk/typescript/src/models.ts",
            "sdk/typescript/src/idempotency.ts",
            "sdk/typescript/src/retry.ts",
            "sdk/typescript/test/client.test.ts"
        ],

        "supabase": [
            "supabase/.env.example",
            "supabase/migrations/0001_init.sql",
            "supabase/migrations/0002_indexes.sql",
            "supabase/migrations/0003_rls_policies.sql",
            "supabase/migrations/0004_functions_triggers.sql",
            "supabase/migrations/0005_dq_metrics.sql",
            "supabase/migrations/0006_lineage_provenance.sql",
            "supabase/migrations/0007_erasure_cascade.sql",
            "supabase/seed/templates/vehicle_detail_v3.yml",
            "supabase/seed/templates/person_profile_v2.yml",
            "supabase/seed/templates/company_profile_v2.yml",
            "supabase/seed/demo_data.sql",
            "supabase/README.md"
        ],

        "api_clients": [
            "api_clients/openapi/python/.gitkeep",
            "api_clients/openapi/typescript/.gitkeep",
            "api_clients/postman/collection.json",
            "api_clients/README.md"
        ],

        "github_workflows": [
            ".github/workflows/01_lint_type.yml",
            ".github/workflows/02_unit_tests.yml",
            ".github/workflows/03_integration_tests.yml",
            ".github/workflows/04_e2e_tests.yml",
            ".github/workflows/05_security.yml",
            ".github/workflows/06_build_sbom_sign.yml",
            ".github/workflows/07_deploy_staging.yml",
            ".github/workflows/08_selector_regression.yml",
            ".github/workflows/09_canary_prod.yml",
            ".github/workflows/10_release_notes.yml",
            ".github/workflows/build_and_push.yml",
            ".github/workflows/security_sast.yml",
            ".github/workflows/dependency_review.yml",
            ".github/workflows/ci.yml",
            ".github/workflows/deploy_staging.yml",
            ".github/workflows/deploy_canary.yml",
            ".github/workflows/nightly_selector_regression.yml",
            ".github/workflows/sbom.yml",
            ".github/workflows/cosign_verify.yml",
            ".github/ISSUE_TEMPLATE.md",
            ".github/PULL_REQUEST_TEMPLATE.md"
        ],

        "examples": [
            "examples/crawl_example.md",
            "examples/scrape_vehicle_detail.md",
            "examples/export_to_sheets.md",
            "examples/api_usage.md",
            "examples/import_urls.csv",
            "examples/export_query_examples.md",
            "examples/api_calls.http"
        ],

        "notebooks": [
            "notebooks/data_exploration.ipynb",
            "notebooks/model_prototyping.ipynb"
        ],

        "legal": [
            "legal/README.md",
            "legal/robots_tos_checklist.md",
            "legal/privacy_policy_internal.md",
            "legal/data_processing_agreements/.gitkeep"
        ],

        "bin": [
            "bin/dev-up",
            "bin/dev-down", 
            "bin/gen-openapi-clients",
            "bin/fmt"
        ],

        "monitoring": [
            "monitoring/docker-compose.obsv.yml",
            "monitoring/alertmanager/.gitkeep",
            "monitoring/grafana/.gitkeep",
            "monitoring/loki/.gitkeep",
            "monitoring/otel-collector/.gitkeep",
            "monitoring/prometheus/.gitkeep",
            "monitoring/promtail/.gitkeep",
            "monitoring/tempo/.gitkeep",
            "monitoring/prometheus/prometheus.yml",
            "monitoring/grafana/provisioning/datasources/prometheus.yaml",
            "monitoring/grafana/provisioning/dashboards/proxypool_dashboard.json",
            "monitoring/grafana/provisioning/dashboards/crawler_scraper_dashboard.json",
            "monitoring/grafana/provisioning/dashboards/database_dashboard.json",
            "monitoring/grafana/provisioning/dashboards/cost_dashboard.json"
        ],

        "extension": [
            "extension/README.md",
            "extension/manifest.json",
            "extension/background.js",
            "extension/content_script.js",
            "extension/popup.html",
            "extension/popup.js",
            "extension/styles.css",
            "extension/icons/icon16.png",
            "extension/icons/icon48.png",
            "extension/icons/icon128.png"
        ],

        "infra": [
            "infra/terraform/README.md",
            "infra/terraform/envs/dev/backend.tf",
            "infra/terraform/envs/dev/main.tf",
            "infra/terraform/envs/dev/variables.tf",
            "infra/terraform/envs/dev/outputs.tf",
            "infra/terraform/envs/staging/main.tf",
            "infra/terraform/envs/prod/main.tf",
            "infra/terraform/modules/network/vpc.tf",
            "infra/terraform/modules/network/subnets.tf",
            "infra/terraform/modules/network/sg.tf",
            "infra/terraform/modules/eks/cluster.tf",
            "infra/terraform/modules/eks/nodegroups.tf",
            "infra/terraform/modules/eks/iam.tf",
            "infra/terraform/modules/rds/postgres.tf",
            "infra/terraform/modules/rds/parameter_groups.tf",
            "infra/terraform/modules/redis/elasticache.tf",
            "infra/terraform/modules/s3/buckets.tf",
            "infra/terraform/modules/s3/lifecycle.tf",
            "infra/terraform/modules/ecr/repos.tf",
            "infra/terraform/modules/iam/roles.tf",
            "infra/terraform/modules/iam/policies.tf",
            "infra/vault/policies/scraper.hcl",
            "infra/vault/policies/crawler.hcl",
            "infra/vault/policies/api.hcl",
            "infra/vault/policies/ci_cd.hcl",
            "infra/vault/kv_layout.md",
            "infra/vault/scripts/put_secrets_dev.sh",
            "infra/vault/scripts/rotate_database_password.sh"
        ],

        "clients": [
            "clients/postman_collection.json",
            "clients/insomnia/insomnia_export.yaml"
        ],

        "lovable": [
            "lovable/components_spec.md",
            "lovable/flows.md",
            "lovable/ui_blueprints.json"
        ],

        "ops": [
            "ops/backup/wal-g.yaml",
            "ops/backup/pgbackrest.conf",
            "ops/backup/verify_backup.sh",
            "ops/retention/retention_policy.yml",
            "ops/retention/retention_runner.py",
            "ops/erasure/erasure_worker.py",
            "ops/erasure/erasure_api.md",
            "ops/s3/lifecycle_raw_html.json",
            "ops/s3/lifecycle_db_backups.json",
            "ops/s3/lifecycle_exports.json"
        ],

        "generated": [
            "generated/python/openapi_client/.gitkeep",
            "generated/typescript/openapi_client/.gitkeep"
        ]
    }


def scan_existing_files(root_path: Path) -> Set[str]:
    """Scan the project directory and return set of existing files."""
    existing_files = set()
    
    for item in root_path.rglob("*"):
        if item.is_file():
            # Get relative path from project root
            rel_path = item.relative_to(root_path)
            existing_files.add(str(rel_path).replace("\\", "/"))
    
    return existing_files

def analyze_structure(root_path: Path) -> Dict:
    """Analyze the current project structure against requirements."""
    required_files = get_required_files()
    existing_files = scan_existing_files(root_path)
    
    # Flatten required files
    all_required = set()
    for category_files in required_files.values():
        all_required.update(category_files)
    
    # Find missing files by category
    missing_by_category = {}
    existing_by_category = {}
    total_missing = 0
    
    for category, files in required_files.items():
        missing = [f for f in files if f not in existing_files]
        existing = [f for f in files if f in existing_files]
        missing_by_category[category] = missing
        existing_by_category[category] = existing
        total_missing += len(missing)
    
    # Calculate statistics
    total_required = len(all_required)
    total_existing = len([f for f in all_required if f in existing_files])
    completion_percentage = (total_existing / total_required) * 100 if total_required > 0 else 0
    
    return {
        "total_required": total_required,
        "total_existing": total_existing, 
        "total_missing": total_missing,
        "completion_percentage": completion_percentage,
        "missing_by_category": missing_by_category,
        "existing_by_category": existing_by_category,
        "existing_files": sorted(list(existing_files)),
        "required_files": all_required
    }

def print_analysis(analysis: Dict) -> None:
    """Print detailed analysis results."""
    print("=" * 80)
    print("COMPREHENSIVE PROJECT STRUCTURE ANALYSIS")
    print("=" * 80)
    
    print(f"\nSTATISTICS:")
    print(f"Total required files: {analysis['total_required']}")
    print(f"Existing files: {analysis['total_existing']}")
    print(f"Missing files: {analysis['total_missing']}")
    print(f"Completion: {analysis['completion_percentage']:.1f}%")
    
    print(f"\nCOMPLETION BY CATEGORY:")
    for category in analysis['missing_by_category'].keys():
        total_in_category = len(analysis['missing_by_category'][category]) + len(analysis['existing_by_category'][category])
        existing_in_category = len(analysis['existing_by_category'][category])
        missing_in_category = len(analysis['missing_by_category'][category])
        category_percentage = (existing_in_category / total_in_category * 100) if total_in_category > 0 else 0
        
        print(f"  {category:20s}: {existing_in_category:3d}/{total_in_category:3d} ({category_percentage:5.1f}%) - {missing_in_category} missing")
    
    print(f"\nMISSING FILES BY CATEGORY:")
    for category, missing_files in analysis['missing_by_category'].items():
        if missing_files:
            print(f"\n{category.upper()} ({len(missing_files)} missing):")
            for file in sorted(missing_files)[:10]:  # Show first 10 per category
                print(f"  - {file}")
            if len(missing_files) > 10:
                print(f"  ... and {len(missing_files) - 10} more")
    
    print(f"\nTOP PRIORITY FILES TO CREATE (first 50):")
    all_missing = []
    for missing_files in analysis['missing_by_category'].values():
        all_missing.extend(missing_files)
    
    # Show top 50 missing files
    for i, file in enumerate(sorted(all_missing)[:50]):
        print(f"  {i+1:2d}. {file}")
    
    if len(all_missing) > 50:
        print(f"  ... and {len(all_missing) - 50} more files")

def analyze_current_structure(project_root: Path) -> Tuple[Set[str], Set[str], Dict[str, int]]:
    """Analyze current project structure and return existing files, missing files, and stats."""
    all_expected = set()
    expected_by_category = get_required_files()
    
    # Flatten all expected files
    for category, files in expected_by_category.items():
        all_expected.update(files)
    
    # Find existing files
    existing_files = set()
    for file_path in all_expected:
        full_path = project_root / file_path
        if full_path.exists():
            existing_files.add(file_path)
    
    # Calculate missing files
    missing_files = all_expected - existing_files
    
    # Calculate stats by category
    category_stats = {}
    for category, files in expected_by_category.items():
        expected_count = len(files)
        existing_count = len([f for f in files if f in existing_files])
        missing_count = expected_count - existing_count
        category_stats[category] = {
            'expected': expected_count,
            'existing': existing_count,
            'missing': missing_count,
            'completion': (existing_count / expected_count * 100) if expected_count > 0 else 0
        }
    
    return existing_files, missing_files, category_stats


def print_analysis_report(existing_files: Set[str], missing_files: Set[str], category_stats: Dict[str, Dict]):
    """Print comprehensive analysis report."""
    total_expected = len(existing_files) + len(missing_files)
    total_existing = len(existing_files)
    overall_completion = (total_existing / total_expected * 100) if total_expected > 0 else 0
    
    print("=" * 80)
    print("COMPLETE PROJECT STRUCTURE ANALYSIS")
    print("=" * 80)
    print(f"📊 OVERALL PROGRESS: {total_existing}/{total_expected} files ({overall_completion:.1f}% complete)")
    print(f"✅ Existing files: {total_existing}")
    print(f"❌ Missing files: {len(missing_files)}")
    print()
    
    print("📋 COMPLETION BY CATEGORY:")
    print("-" * 80)
    for category, stats in sorted(category_stats.items()):
        completion = stats['completion']
        status_icon = "✅" if completion == 100 else "🟡" if completion >= 50 else "❌"
        print(f"{status_icon} {category:20} {stats['existing']:3d}/{stats['expected']:3d} ({completion:5.1f}%)")
    print()
    
    # Show categories with missing files
    print("🔍 MISSING FILES BY CATEGORY:")
    print("-" * 80)
    expected_by_category = get_expected_files()
    for category, files in sorted(expected_by_category.items()):
        missing_in_category = [f for f in files if f in missing_files]
        if missing_in_category:
            print(f"\n{category.upper()} ({len(missing_in_category)} missing):")
            for file_path in sorted(missing_in_category)[:5]:  # Show first 5
                print(f"  ❌ {file_path}")
            if len(missing_in_category) > 5:
                print(f"  ... and {len(missing_in_category) - 5} more")


def main():
    """Main function."""
    # Get project root (one level up from scripts directory)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print(f"Analyzing comprehensive project structure in: {project_root}")
    
    # Run analysis
    analysis = analyze_structure(project_root)
    
    # Print results
    print_analysis(analysis)
    
    # Save detailed results
    output_file = script_dir / "comprehensive_structure_analysis.json"
    with open(output_file, 'w') as f:
        # Convert sets to lists for JSON serialization
        json_analysis = analysis.copy()
        json_analysis['required_files'] = list(analysis['required_files'])
        json.dump(json_analysis, f, indent=2, default=str)
    
    print(f"\nDetailed analysis saved to: {output_file}")

if __name__ == "__main__":
    main()
