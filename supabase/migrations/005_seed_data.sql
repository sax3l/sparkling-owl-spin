-- ECaDP Seed Data and Reference Values
-- Migration: 005_seed_data.sql
-- Description: Initial reference data, configuration values, and sample data
-- Date: 2025-01-22
-- Author: ECaDP Development Team

-- ===================================
-- SYSTEM ROLES AND PERMISSIONS
-- ===================================

-- Insert system roles
INSERT INTO user_roles (name, description, permissions, is_system_role) VALUES
('super_admin', 'System administrator with full access', 
 '["users:*", "tenants:*", "system:*", "data:*", "jobs:*", "proxies:*"]'::jsonb, true),
('tenant_admin', 'Tenant administrator with full tenant access', 
 '["users:read", "users:write", "data:*", "jobs:*", "proxies:read", "reports:read"]'::jsonb, true),
('data_manager', 'Manage data entities within tenant', 
 '["data:*", "jobs:read", "reports:read"]'::jsonb, true),
('data_viewer', 'Read-only access to data', 
 '["data:read", "reports:read"]'::jsonb, true),
('job_operator', 'Manage jobs and scraping operations', 
 '["jobs:*", "proxies:read", "data:read"]'::jsonb, true),
('api_client', 'Programmatic API access', 
 '["data:read", "data:write", "jobs:create"]'::jsonb, true)
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    permissions = EXCLUDED.permissions,
    updated_at = NOW();

-- ===================================
-- DEFAULT JOB QUEUES
-- ===================================

-- Insert default job queues
INSERT INTO job_queues (name, description, max_concurrent_jobs, max_retries, retry_delay_seconds, is_active) VALUES
('default', 'Default job queue for general tasks', 10, 3, 300, true),
('scraping', 'High-priority scraping operations', 20, 5, 60, true),
('data_processing', 'Data processing and enrichment', 5, 3, 120, true),
('exports', 'Data export operations', 3, 2, 180, true),
('maintenance', 'System maintenance and cleanup', 2, 1, 3600, true),
('priority', 'High priority tasks', 50, 3, 30, true),
('batch', 'Large batch operations', 2, 1, 900, true),
('api_requests', 'API-triggered operations', 15, 3, 60, true)
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    max_concurrent_jobs = EXCLUDED.max_concurrent_jobs,
    max_retries = EXCLUDED.max_retries,
    retry_delay_seconds = EXCLUDED.retry_delay_seconds,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- ===================================
-- DATA QUALITY RULES
-- ===================================

-- Insert standard data quality rules
INSERT INTO data_quality_rules (name, entity_type, field_name, rule_type, rule_expression, severity, description, is_active) VALUES

-- Person validation rules
('person_name_required', 'persons', 'full_name', 'required', '', 'critical', 'Person must have a full name', true),
('person_email_format', 'persons', 'email', 'format', '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', 'warning', 'Email must be in valid format', true),
('person_phone_format', 'persons', 'phone', 'format', '^(\+46|0)[0-9\-\s]+$', 'warning', 'Phone number must be in Swedish format', true),
('person_personal_number_format', 'persons', 'personal_number', 'format', '^[0-9]{6,8}-[0-9]{4}$', 'critical', 'Personal number must be in Swedish format (YYYYMMDD-XXXX)', true),

-- Company validation rules
('company_name_required', 'companies', 'name', 'required', '', 'critical', 'Company must have a name', true),
('company_org_number_format', 'companies', 'organization_number', 'format', '^[0-9]{6}-[0-9]{4}$', 'critical', 'Organization number must be in Swedish format (XXXXXX-XXXX)', true),
('company_employee_count_range', 'companies', 'employee_count', 'range', '{"min": 0, "max": 1000000}', 'warning', 'Employee count should be reasonable', true),

-- Vehicle validation rules
('vehicle_registration_required', 'vehicles', 'registration_number', 'required', '', 'critical', 'Vehicle must have registration number', true),
('vehicle_registration_format', 'vehicles', 'registration_number', 'format', '^[A-Z]{3}[0-9]{3}$|^[A-Z]{3}[0-9]{2}[A-Z]$', 'warning', 'Registration should be in Swedish format', true),
('vehicle_year_range', 'vehicles', 'year', 'range', '{"min": 1900, "max": 2030}', 'warning', 'Vehicle year should be reasonable', true),

-- Custom business rules
('person_company_exists', 'persons', 'company_id', 'custom', 
 'company_id IS NULL OR EXISTS (SELECT 1 FROM companies WHERE companies.id = persons.company_id)', 
 'critical', 'Person company must exist if specified', true),
('vehicle_owner_exists', 'vehicles', 'owner_id', 'custom', 
 'owner_id IS NULL OR EXISTS (SELECT 1 FROM persons WHERE persons.id = vehicles.owner_id)', 
 'critical', 'Vehicle owner must exist if specified', true)

ON CONFLICT (name, entity_type, field_name) DO UPDATE SET
    rule_type = EXCLUDED.rule_type,
    rule_expression = EXCLUDED.rule_expression,
    severity = EXCLUDED.severity,
    description = EXCLUDED.description,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- ===================================
-- DATA RETENTION POLICIES
-- ===================================

-- Insert default retention policies
INSERT INTO data_retention_policies (name, entity_type, retention_days, action_type, conditions, is_active, description) VALUES
('audit_log_cleanup', 'audit_logs', 365, 'delete', '{}', true, 'Clean up audit logs older than 1 year'),
('job_history_cleanup', 'jobs', 90, 'delete', '{"status": ["completed", "failed"]}', true, 'Remove completed/failed jobs older than 90 days'),
('proxy_logs_cleanup', 'proxy_usage_logs', 30, 'delete', '{}', true, 'Clean up proxy usage logs older than 30 days'),
('gdpr_person_anonymization', 'persons', 2555, 'anonymize', '{"deleted_at": "IS NOT NULL"}', true, 'GDPR: Anonymize deleted persons after 7 years'),
('temp_extractions_cleanup', 'extraction_results', 7, 'delete', '{"status": "failed"}', true, 'Remove failed extractions older than 7 days'),
('system_metrics_cleanup', 'system_metrics', 90, 'delete', '{}', true, 'Clean up system metrics older than 90 days'),
('alert_history_cleanup', 'alert_history', 180, 'delete', '{}', true, 'Remove alert history older than 6 months')
ON CONFLICT (name) DO UPDATE SET
    entity_type = EXCLUDED.entity_type,
    retention_days = EXCLUDED.retention_days,
    action_type = EXCLUDED.action_type,
    conditions = EXCLUDED.conditions,
    is_active = EXCLUDED.is_active,
    description = EXCLUDED.description,
    updated_at = NOW();

-- ===================================
-- PROXY POOLS AND CONFIGURATIONS
-- ===================================

-- Insert default proxy pool
INSERT INTO proxy_pools (name, description, max_concurrent_uses, rotation_strategy, health_check_url, is_active) VALUES
('default', 'Default proxy pool for general scraping', 5, 'round_robin', 'https://httpbin.org/ip', true),
('premium', 'Premium proxies for sensitive operations', 3, 'least_used', 'https://httpbin.org/ip', true),
('residential', 'Residential IP proxies', 2, 'random', 'https://httpbin.org/ip', true),
('datacenter', 'Fast datacenter proxies', 10, 'round_robin', 'https://httpbin.org/ip', true)
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    max_concurrent_uses = EXCLUDED.max_concurrent_uses,
    rotation_strategy = EXCLUDED.rotation_strategy,
    health_check_url = EXCLUDED.health_check_url,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- ===================================
-- EXTRACTION TEMPLATES
-- ===================================

-- Insert sample extraction templates
INSERT INTO extraction_templates (name, description, selectors, validation_rules, is_active) VALUES
('swedish_company_basic', 'Basic Swedish company information extraction',
 '{
    "name": "h1.company-name, .company-title, h1",
    "organization_number": "[data-org-number], .org-number, .orgnr",
    "address": ".address, .company-address, address",
    "phone": "[data-phone], .phone, .tel, a[href^=\"tel:\"]",
    "email": "[data-email], .email, a[href^=\"mailto:\"]",
    "website": "[data-website], .website, a[href^=\"http\"]",
    "description": ".description, .company-description, .about"
  }'::jsonb,
 '{
    "name": {"required": true, "min_length": 2},
    "organization_number": {"format": "^[0-9]{6}-[0-9]{4}$"},
    "email": {"format": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"}
  }'::jsonb, true),

('person_profile_basic', 'Basic person profile extraction',
 '{
    "full_name": "h1.name, .person-name, .profile-name",
    "title": ".title, .job-title, .position",
    "company": ".company, .workplace, .employer",
    "email": ".email, a[href^=\"mailto:\"]",
    "phone": ".phone, a[href^=\"tel:\"]",
    "linkedin": "a[href*=\"linkedin.com\"]",
    "description": ".bio, .description, .about"
  }'::jsonb,
 '{
    "full_name": {"required": true, "min_length": 2},
    "email": {"format": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"}
  }'::jsonb, true),

('vehicle_registry', 'Vehicle registry information extraction',
 '{
    "registration_number": ".reg-number, [data-reg], .registration",
    "make": ".make, .brand, .manufacturer",
    "model": ".model, .car-model",
    "year": ".year, .model-year, [data-year]",
    "color": ".color, .car-color",
    "fuel_type": ".fuel, .fuel-type",
    "inspection_date": ".inspection, .besiktning",
    "owner_name": ".owner, .registered-owner"
  }'::jsonb,
 '{
    "registration_number": {"required": true, "format": "^[A-Z]{3}[0-9]{3}$|^[A-Z]{3}[0-9]{2}[A-Z]$"},
    "year": {"type": "integer", "min": 1900, "max": 2030}
  }'::jsonb, true)

ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    selectors = EXCLUDED.selectors,
    validation_rules = EXCLUDED.validation_rules,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- ===================================
-- GDPR DATA CATEGORIES
-- ===================================

-- Insert GDPR data categories
INSERT INTO gdpr_data_categories (name, description, legal_basis, retention_period_days, special_category) VALUES
('personal_identifiers', 'Basic personal identifiers (name, email, phone)', 'legitimate_interest', 2555, false),
('sensitive_personal', 'Personal numbers, financial information', 'explicit_consent', 2555, true),
('professional_data', 'Work-related information, job titles, company affiliation', 'legitimate_interest', 1825, false),
('behavioral_data', 'Website interactions, preferences, usage patterns', 'legitimate_interest', 365, false),
('technical_data', 'IP addresses, device information, cookies', 'legitimate_interest', 365, false),
('communication_data', 'Email communications, support tickets', 'contract_performance', 1095, false),
('financial_data', 'Payment information, billing data', 'contract_performance', 2555, true)
ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    legal_basis = EXCLUDED.legal_basis,
    retention_period_days = EXCLUDED.retention_period_days,
    special_category = EXCLUDED.special_category,
    updated_at = NOW();

-- ===================================
-- SYSTEM CONFIGURATION
-- ===================================

-- Insert system configuration values
INSERT INTO system_configuration (key, value, description, is_public) VALUES
('app_name', '"ECaDP - Enhanced Corporate and Data Platform"', 'Application display name', true),
('app_version', '"1.0.0"', 'Current application version', true),
('max_file_upload_size', '52428800', 'Maximum file upload size in bytes (50MB)', false),
('default_pagination_limit', '25', 'Default number of items per page', true),
('max_pagination_limit', '100', 'Maximum number of items per page', true),
('session_timeout_minutes', '480', 'User session timeout in minutes (8 hours)', false),
('password_min_length', '8', 'Minimum password length', true),
('password_require_special_chars', 'true', 'Require special characters in passwords', true),
('max_login_attempts', '5', 'Maximum failed login attempts before lockout', false),
('lockout_duration_minutes', '15', 'Account lockout duration in minutes', false),
('enable_audit_logging', 'true', 'Enable comprehensive audit logging', false),
('enable_data_encryption', 'true', 'Enable data encryption at rest', false),
('proxy_timeout_seconds', '30', 'Default proxy timeout in seconds', false),
('max_concurrent_jobs_per_tenant', '50', 'Maximum concurrent jobs per tenant', false),
('data_quality_check_interval_hours', '24', 'How often to run data quality checks', false),
('backup_retention_days', '30', 'How long to keep database backups', false),
('enable_rate_limiting', 'true', 'Enable API rate limiting', false),
('rate_limit_requests_per_minute', '60', 'API requests per minute per user', false),
('enable_captcha', 'false', 'Enable CAPTCHA for sensitive operations', true),
('maintenance_mode', 'false', 'Enable maintenance mode', false)
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    description = EXCLUDED.description,
    is_public = EXCLUDED.is_public,
    updated_at = NOW();

-- ===================================
-- SAMPLE TENANTS (Development Only)
-- ===================================

-- Insert sample tenants for development/testing
INSERT INTO tenant_configurations (tenant_id, name, settings, subscription_tier, is_active) 
SELECT 
    gen_random_uuid(),
    'Demo Corporation',
    '{
        "features": ["basic_scraping", "data_export", "api_access"],
        "limits": {
            "max_users": 10,
            "max_jobs_per_day": 1000,
            "max_storage_gb": 5
        },
        "branding": {
            "logo_url": null,
            "primary_color": "#2563eb",
            "company_name": "Demo Corporation"
        }
    }'::jsonb,
    'professional',
    true
WHERE NOT EXISTS (SELECT 1 FROM tenant_configurations WHERE name = 'Demo Corporation');

-- ===================================
-- HEALTH CHECK AND MONITORING SETUP
-- ===================================

-- Insert system health metrics configuration
INSERT INTO system_metrics (metric_name, metric_value, metric_unit, category, threshold_warning, threshold_critical) VALUES
('database_connections', 0, 'count', 'database', 80, 95),
('active_jobs', 0, 'count', 'jobs', 100, 200),
('failed_jobs_per_hour', 0, 'count', 'jobs', 10, 25),
('proxy_success_rate', 100, 'percentage', 'proxies', 85, 70),
('api_response_time_ms', 0, 'milliseconds', 'performance', 2000, 5000),
('storage_used_gb', 0, 'gigabytes', 'storage', 80, 95),
('memory_usage_percent', 0, 'percentage', 'system', 85, 95),
('cpu_usage_percent', 0, 'percentage', 'system', 80, 90),
('error_rate_percent', 0, 'percentage', 'errors', 5, 10)
ON CONFLICT (metric_name) DO UPDATE SET
    category = EXCLUDED.category,
    threshold_warning = EXCLUDED.threshold_warning,
    threshold_critical = EXCLUDED.threshold_critical,
    updated_at = NOW();

-- ===================================
-- EXPORT TARGET CONFIGURATIONS
-- ===================================

-- Insert default export configurations
INSERT INTO export_targets (name, target_type, configuration, is_active, description) VALUES
('local_json', 'file', 
 '{"format": "json", "path": "/data/exports/", "compression": "gzip"}'::jsonb, 
 true, 'Local JSON file export with compression'),
('local_csv', 'file', 
 '{"format": "csv", "path": "/data/exports/", "delimiter": ",", "include_headers": true}'::jsonb, 
 true, 'Local CSV file export'),
('local_excel', 'file', 
 '{"format": "xlsx", "path": "/data/exports/", "include_formatting": true}'::jsonb, 
 true, 'Local Excel file export'),
('webhook_json', 'webhook', 
 '{"format": "json", "method": "POST", "headers": {"Content-Type": "application/json"}}'::jsonb, 
 true, 'JSON webhook delivery'),
('email_csv', 'email', 
 '{"format": "csv", "subject": "ECaDP Data Export", "compress": true}'::jsonb, 
 true, 'CSV export via email')
ON CONFLICT (name) DO UPDATE SET
    target_type = EXCLUDED.target_type,
    configuration = EXCLUDED.configuration,
    is_active = EXCLUDED.is_active,
    description = EXCLUDED.description,
    updated_at = NOW();

-- ===================================
-- NOTIFICATION TEMPLATES
-- ===================================

-- Create notification templates table and insert templates
DO $$ 
BEGIN
    -- Create table if it doesn't exist
    CREATE TABLE IF NOT EXISTS notification_templates (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL CHECK (type IN ('email', 'webhook', 'sms')),
        subject TEXT,
        template TEXT NOT NULL,
        variables JSONB DEFAULT '{}'::JSONB,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Insert templates
    INSERT INTO notification_templates (name, type, subject, template, variables) VALUES
    ('job_completed', 'email', 'Job Completed Successfully', 
     'Your job "{{job_name}}" has completed successfully.\n\nJob Details:\n- ID: {{job_id}}\n- Started: {{started_at}}\n- Completed: {{completed_at}}\n- Duration: {{duration}}\n- Results: {{result_count}} records processed\n\nBest regards,\nECaDP Team',
     '["job_name", "job_id", "started_at", "completed_at", "duration", "result_count"]'::jsonb),
    
    ('job_failed', 'email', 'Job Failed - Action Required',
     'Your job "{{job_name}}" has failed.\n\nJob Details:\n- ID: {{job_id}}\n- Started: {{started_at}}\n- Failed: {{failed_at}}\n- Error: {{error_message}}\n\nPlease review the job configuration and try again.\n\nBest regards,\nECaDP Team',
     '["job_name", "job_id", "started_at", "failed_at", "error_message"]'::jsonb),
    
    ('data_quality_alert', 'email', 'Data Quality Issues Detected',
     'Data quality issues have been detected in your {{entity_type}} data.\n\nSummary:\n- Total Records Checked: {{total_records}}\n- Issues Found: {{issues_count}}\n- Critical Issues: {{critical_count}}\n- Warnings: {{warning_count}}\n\nPlease review and address these issues in your ECaDP dashboard.\n\nBest regards,\nECaDP Team',
     '["entity_type", "total_records", "issues_count", "critical_count", "warning_count"]'::jsonb),
    
    ('export_ready', 'email', 'Data Export Ready for Download',
     'Your data export is ready for download.\n\nExport Details:\n- Export ID: {{export_id}}\n- Format: {{format}}\n- Records: {{record_count}}\n- File Size: {{file_size}}\n- Download URL: {{download_url}}\n\nThis download link will expire in 24 hours.\n\nBest regards,\nECaDP Team',
     '["export_id", "format", "record_count", "file_size", "download_url"]'::jsonb)
    
    ON CONFLICT (name) DO UPDATE SET
        type = EXCLUDED.type,
        subject = EXCLUDED.subject,
        template = EXCLUDED.template,
        variables = EXCLUDED.variables,
        updated_at = NOW();

EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not create notification templates: %', SQLERRM;
END $$;

-- ===================================
-- FINALIZATION AND VERIFICATION
-- ===================================

-- Update statistics for better query planning
ANALYZE;

-- Verify seed data
DO $$
DECLARE
    roles_count INTEGER;
    queues_count INTEGER;
    rules_count INTEGER;
    templates_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO roles_count FROM user_roles WHERE is_system_role = true;
    SELECT COUNT(*) INTO queues_count FROM job_queues WHERE is_active = true;
    SELECT COUNT(*) INTO rules_count FROM data_quality_rules WHERE is_active = true;
    SELECT COUNT(*) INTO templates_count FROM extraction_templates WHERE is_active = true;
    
    RAISE NOTICE 'Seed data verification:';
    RAISE NOTICE '- System roles: %', roles_count;
    RAISE NOTICE '- Active job queues: %', queues_count;
    RAISE NOTICE '- Data quality rules: %', rules_count;
    RAISE NOTICE '- Extraction templates: %', templates_count;
    
    IF roles_count < 6 OR queues_count < 8 OR rules_count < 10 OR templates_count < 3 THEN
        RAISE WARNING 'Some seed data may not have been inserted correctly';
    ELSE
        RAISE NOTICE 'All seed data inserted successfully!';
    END IF;
END $$;

-- Migration complete
SELECT 'ECaDP Seed Data Migration 005 completed successfully' as result;
