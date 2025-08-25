#!/usr/bin/env python3
"""
Detailed comparison between actual and ideal project structure
Based on Projektbeskrivning.txt Chapter 24.1
"""

import os
from pathlib import Path

def check_ideal_vs_actual():
    """Compare ideal structure from Chapter 24.1 with actual implementation"""
    
    project_root = Path(os.getcwd())
    
    # Define the ideal structure from Chapter 24.1
    ideal_structure = {
        # Root files
        "README.md": "Root documentation",
        "LICENSE": "License file", 
        "CODE_OF_CONDUCT.md": "Code of conduct",
        "SECURITY.md": "Security policy",
        ".gitignore": "Git ignore rules",
        ".editorconfig": "Editor configuration",
        ".env.example": "Environment template",
        "pyproject.toml": "Python project config",
        "requirements.txt": "Python dependencies",
        "requirements_dev.txt": "Development dependencies",
        "Makefile": "Build automation",
        
        # Config structure
        "config/app_config.yml": "Main app configuration",
        "config/logging.yml": "Logging configuration", 
        "config/anti_bot.yml": "Anti-bot settings",
        "config/proxies.yml": "Proxy configuration",
        "config/performance-defaults.yml": "Performance settings",
        "config/env/development.yml": "Development environment",
        "config/env/staging.yml": "Staging environment",
        "config/env/production.yml": "Production environment",
        
        # Supabase structure
        "supabase/migrations/0001_extensions.sql": "Database extensions",
        "supabase/migrations/0002_types.sql": "Custom types",
        "supabase/migrations/0003_core.sql": "Core tables",
        "supabase/migrations/0004_rls.sql": "Row level security",
        "supabase/migrations/0005_rpc.sql": "Remote procedure calls",
        "supabase/migrations/0006_cron.sql": "Scheduled jobs",
        "supabase/migrations/0007_triggers.sql": "Database triggers",
        "supabase/migrations/0008_preview.sql": "Preview features",
        "supabase/functions/jobs_webhook/index.ts": "Job webhook handler",
        "supabase/functions/retention/index.ts": "Data retention handler",
        "supabase/functions/erasure/index.ts": "Data erasure handler",
        "supabase/types/database-types.ts": "TypeScript database types",
        
        # Core Python modules
        "src/__init__.py": "Main package init",
        "src/utils/__init__.py": "Utils package init",
        "src/utils/logger.py": "Logging utilities",
        "src/utils/user_agent_rotator.py": "User agent rotation",
        "src/utils/validators.py": "Data validators",
        "src/utils/export_utils.py": "Export utilities",
        "src/utils/pattern_detector.py": "Pattern detection",
        
        # Proxy pool module
        "src/proxy_pool/__init__.py": "Proxy pool package",
        "src/proxy_pool/collector.py": "Proxy collector",
        "src/proxy_pool/validator.py": "Proxy validator",
        "src/proxy_pool/quality_filter.py": "Quality filtering",
        "src/proxy_pool/monitor.py": "Proxy monitoring",
        "src/proxy_pool/manager.py": "Proxy management",
        "src/proxy_pool/rotator.py": "Proxy rotation",
        "src/proxy_pool/api/__init__.py": "Proxy API package",
        "src/proxy_pool/api/server.py": "Proxy API server",
        
        # Anti-bot module
        "src/anti_bot/__init__.py": "Anti-bot package",
        "src/anti_bot/header_generator.py": "HTTP header generation",
        "src/anti_bot/session_manager.py": "Session management",
        "src/anti_bot/delay_strategy.py": "Delay strategies",
        "src/anti_bot/credential_manager.py": "Credential management",
        "src/anti_bot/diagnostics/__init__.py": "Diagnostics package",
        "src/anti_bot/diagnostics/diagnose_url.py": "URL diagnostics",
        "src/anti_bot/fallback_strategy.py": "Fallback strategies",
        "src/anti_bot/browser_stealth/__init__.py": "Browser stealth package",
        "src/anti_bot/browser_stealth/stealth_browser.py": "Stealth browser",
        "src/anti_bot/browser_stealth/human_behavior.py": "Human behavior simulation",
        "src/anti_bot/browser_stealth/cloudflare_bypass.py": "Cloudflare bypass",
        "src/anti_bot/browser_stealth/captcha_solver.py": "CAPTCHA solving",
        
        # Crawler module
        "src/crawler/__init__.py": "Crawler package",
        "src/crawler/sitemap_generator.py": "Sitemap generation",
        "src/crawler/template_detector.py": "Template detection",
        "src/crawler/url_queue.py": "URL queue management",
        "src/crawler/keywords_search.py": "Keyword search",
        
        # Scraper module
        "src/scraper/__init__.py": "Scraper package",
        "src/scraper/base_scraper.py": "Base scraper class",
        "src/scraper/http_scraper.py": "HTTP scraper",
        "src/scraper/selenium_scraper.py": "Selenium scraper",
        "src/scraper/template_extractor.py": "Template extraction",
        "src/scraper/xpath_suggester.py": "XPath suggestions",
        "src/scraper/regex_transformer.py": "Regex transformations",
        "src/scraper/login_handler.py": "Login handling",
        "src/scraper/image_downloader.py": "Image downloading",
        "src/scraper/dsl/__init__.py": "DSL package",
        "src/scraper/dsl/schema.py": "DSL schema definitions",
        "src/scraper/dsl/transformers.py": "Data transformers",
        "src/scraper/template_runtime.py": "Template runtime",
        
        # Database module
        "src/database/__init__.py": "Database package",
        "src/database/models.py": "Database models",
        "src/database/schema.sql": "Database schema",
        "src/database/manager.py": "Database manager",
        "src/database/seed/persons.json": "Person seed data",
        "src/database/seed/companies.json": "Company seed data",
        "src/database/seed/vehicles.json": "Vehicle seed data",
        
        # Scheduler module
        "src/scheduler/__init__.py": "Scheduler package",
        "src/scheduler/job_definitions.py": "Job definitions",
        "src/scheduler/scheduler.py": "Main scheduler",
        "src/scheduler/job_monitor.py": "Job monitoring",
        "src/scheduler/notifier.py": "Notifications",
        "src/scheduler/jobs/retention_job.py": "Retention job",
        "src/scheduler/jobs/dq_job.py": "Data quality job",
        "src/scheduler/jobs/backup_sql_job.py": "Backup job",
        "src/scheduler/jobs/redis_snapshot_job.py": "Redis snapshot job",
        "src/scheduler/jobs/erasure_worker.py": "Data erasure worker",
        
        # Web application module
        "src/webapp/__init__.py": "Web app package",
        "src/webapp/app.py": "Main web application",
        "src/webapp/api.py": "API endpoints",
        "src/webapp/auth.py": "Authentication",
        "src/webapp/views.py": "Web views",
        
        # Analysis module
        "src/analysis/__init__.py": "Analysis package",
        "src/analysis/data_quality.py": "Data quality analysis",
        "src/analysis/similarity_analysis.py": "Similarity analysis",
        
        # Frontend structure
        "frontend/package.json": "Frontend dependencies",
        "frontend/vite.config.ts": "Vite configuration",
        "frontend/tsconfig.json": "TypeScript configuration",
        "frontend/src/main.tsx": "Frontend entry point",
        "frontend/src/App.tsx": "Main App component",
        "frontend/src/api/client.ts": "API client",
        "frontend/src/api/types.ts": "TypeScript types",
        
        # SDK structure
        "sdk/python/pyproject.toml": "Python SDK config",
        "sdk/python/scrape_sdk.py": "Python SDK",
        "sdk/ts/package.json": "TypeScript SDK config",
        "sdk/ts/index.ts": "TypeScript SDK",
        
        # Scripts
        "scripts/init_db.py": "Database initialization",
        "scripts/seed_data.py": "Data seeding",
        "scripts/start_scheduler.py": "Scheduler startup",
        "scripts/run_crawler.py": "Crawler runner",
        "scripts/run_scraper.py": "Scraper runner", 
        "scripts/run_analysis.py": "Analysis runner",
        "scripts/diagnostic_tool.py": "Diagnostic tool",
        
        # Docker structure
        "docker/Dockerfile": "Main Dockerfile",
        "docker/docker-compose.yml": "Docker composition",
        "docker/entrypoint.sh": "Container entry point",
        
        # Testing structure (implied)
        "tests/__init__.py": "Test package",
        "tests/unit/__init__.py": "Unit tests",
        "tests/integration/__init__.py": "Integration tests",
        "tests/conftest.py": "Test configuration",
        
        # Kubernetes
        "k8s/helm/Chart.yaml": "Helm chart definition",
    }
    
    print("🔍 DETAILED COMPARISON: IDEAL vs ACTUAL STRUCTURE")
    print("=" * 80)
    
    # Check each file
    missing_files = []
    existing_files = []
    
    for file_path, description in ideal_structure.items():
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size if full_path.is_file() else "DIR"
            existing_files.append((file_path, description, size))
            print(f"✅ {file_path:<50} ({size} bytes)")
        else:
            missing_files.append((file_path, description))
            print(f"❌ {file_path:<50} MISSING")
    
    print(f"\n📊 SUMMARY:")
    print(f"✅ Existing files: {len(existing_files)}")
    print(f"❌ Missing files: {len(missing_files)}")
    print(f"📈 Completion: {len(existing_files)/(len(existing_files)+len(missing_files))*100:.1f}%")
    
    print(f"\n🚨 TOP PRIORITY MISSING FILES:")
    critical_missing = [
        f for f, desc in missing_files 
        if any(keyword in f for keyword in [
            'migrations/', 'scheduler/', 'analysis/', 'proxy_pool/', 
            'anti_bot/', 'helm/', 'tests/unit', 'tests/integration'
        ])
    ]
    
    for i, file_path in enumerate(critical_missing[:15], 1):
        print(f"   {i:2d}. {file_path}")
    
    return {
        'existing': existing_files,
        'missing': missing_files,
        'completion_percentage': len(existing_files)/(len(existing_files)+len(missing_files))*100
    }

if __name__ == "__main__":
    check_ideal_vs_actual()
