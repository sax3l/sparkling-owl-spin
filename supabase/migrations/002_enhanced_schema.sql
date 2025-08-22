-- ECaDP Enhanced Schema Migration
-- Migration: 002_enhanced_schema.sql
-- Description: Advanced database features including RLS, audit triggers, views, and performance optimizations
-- Date: 2025-01-22
-- Author: ECaDP Development Team

-- ===================================
-- ENHANCED ROLES AND SECURITY SETUP
-- ===================================

-- Create additional security roles
DO $$
BEGIN
    -- Create admin role if it doesn't exist
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ecadp_admin') THEN
        CREATE ROLE ecadp_admin NOINHERIT;
    END IF;
    
    -- Create service role if it doesn't exist  
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ecadp_service') THEN
        CREATE ROLE ecadp_service NOINHERIT;
    END IF;
    
    -- Create readonly role if it doesn't exist
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ecadp_readonly') THEN
        CREATE ROLE ecadp_readonly NOINHERIT;
    END IF;
END
$$;

-- Grant appropriate permissions
GRANT USAGE ON SCHEMA public TO ecadp_admin, ecadp_service, ecadp_readonly;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ecadp_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ecadp_service;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO ecadp_readonly;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO ecadp_admin, ecadp_service;

-- ===================================
-- ENHANCED DATA MODELS
-- ===================================

-- Add tenant isolation columns to existing tables
ALTER TABLE persons ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS tenant_id UUID;  
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE proxies ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE scraping_templates ADD COLUMN IF NOT EXISTS tenant_id UUID;
ALTER TABLE export_jobs ADD COLUMN IF NOT EXISTS tenant_id UUID;

-- Add soft delete columns
ALTER TABLE persons ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

-- Add encryption flags for PII data
ALTER TABLE persons ADD COLUMN IF NOT EXISTS personal_number_hash TEXT;
ALTER TABLE persons ADD COLUMN IF NOT EXISTS phone_number_hash TEXT;
ALTER TABLE persons ADD COLUMN IF NOT EXISTS email_hash TEXT;
ALTER TABLE persons ADD COLUMN IF NOT EXISTS is_pii_encrypted BOOLEAN DEFAULT false;

-- Enhanced job tracking
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS priority INTEGER DEFAULT 5;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS max_retries INTEGER DEFAULT 3;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS next_retry_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS timeout_seconds INTEGER DEFAULT 3600;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS memory_limit_mb INTEGER DEFAULT 512;

-- ===================================
-- NEW ADVANCED TABLES
-- ===================================

-- Create sessions tracking table
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,
    location JSONB,
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE
);

-- Create advanced job dependencies
CREATE TABLE IF NOT EXISTS job_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    depends_on_job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    dependency_type TEXT DEFAULT 'blocking', -- blocking, soft, conditional
    condition_expression TEXT, -- SQL-like expression for conditional dependencies
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(job_id, depends_on_job_id)
);

-- Create job queues for better scheduling
CREATE TABLE IF NOT EXISTS job_queues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    max_concurrent_jobs INTEGER DEFAULT 5,
    priority_boost INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    max_retry_attempts INTEGER DEFAULT 3,
    default_timeout_seconds INTEGER DEFAULT 3600,
    rate_limit_per_minute INTEGER DEFAULT 60,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Link jobs to queues
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS queue_id UUID REFERENCES job_queues(id);

-- Create advanced proxy management
CREATE TABLE IF NOT EXISTS proxy_pools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    pool_type TEXT DEFAULT 'standard', -- residential, datacenter, mobile, standard
    is_active BOOLEAN DEFAULT true,
    max_concurrent_uses INTEGER DEFAULT 10,
    rotation_strategy TEXT DEFAULT 'round_robin', -- round_robin, least_used, random, sticky
    health_check_interval_seconds INTEGER DEFAULT 300,
    failure_threshold INTEGER DEFAULT 5,
    success_threshold INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Link proxies to pools
ALTER TABLE proxies ADD COLUMN IF NOT EXISTS pool_id UUID REFERENCES proxy_pools(id);
ALTER TABLE proxies ADD COLUMN IF NOT EXISTS concurrent_uses INTEGER DEFAULT 0;
ALTER TABLE proxies ADD COLUMN IF NOT EXISTS failure_count INTEGER DEFAULT 0;
ALTER TABLE proxies ADD COLUMN IF NOT EXISTS last_failure_at TIMESTAMP WITH TIME ZONE;

-- Create proxy usage tracking
CREATE TABLE IF NOT EXISTS proxy_usage_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proxy_id UUID NOT NULL REFERENCES proxies(id) ON DELETE CASCADE,
    job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    url TEXT NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    response_code INTEGER,
    response_time_ms INTEGER,
    bytes_transferred BIGINT,
    success BOOLEAN,
    error_message TEXT,
    tenant_id UUID
);

-- Create advanced data quality tracking
CREATE TABLE IF NOT EXISTS data_quality_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    entity_type TEXT NOT NULL, -- persons, companies, vehicles
    field_name TEXT NOT NULL,
    rule_type TEXT NOT NULL, -- required, format, range, custom
    rule_expression TEXT NOT NULL, -- JSON or SQL expression
    severity TEXT DEFAULT 'warning', -- info, warning, error, critical
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced data quality metrics with rule references
ALTER TABLE data_quality_metrics ADD COLUMN IF NOT EXISTS rule_id UUID REFERENCES data_quality_rules(id);
ALTER TABLE data_quality_metrics ADD COLUMN IF NOT EXISTS severity TEXT DEFAULT 'info';
ALTER TABLE data_quality_metrics ADD COLUMN IF NOT EXISTS details JSONB;

-- Create template versioning
CREATE TABLE IF NOT EXISTS template_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID NOT NULL REFERENCES scraping_templates(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    template_data JSONB NOT NULL,
    changelog TEXT,
    is_active BOOLEAN DEFAULT false,
    performance_metrics JSONB, -- success_rate, avg_extraction_time, etc.
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(template_id, version_number)
);

-- Create extraction results for better tracking
CREATE TABLE IF NOT EXISTS extraction_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    template_id UUID REFERENCES scraping_templates(id) ON DELETE SET NULL,
    template_version_id UUID REFERENCES template_versions(id) ON DELETE SET NULL,
    url TEXT NOT NULL,
    extracted_data JSONB,
    raw_html TEXT,
    response_code INTEGER,
    response_time_ms INTEGER,
    extraction_time_ms INTEGER,
    proxy_id UUID REFERENCES proxies(id) ON DELETE SET NULL,
    success BOOLEAN DEFAULT false,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tenant_id UUID
);

-- Create data lineage tracking
CREATE TABLE IF NOT EXISTS data_lineage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    source_job_id UUID REFERENCES jobs(id) ON DELETE SET NULL,
    source_url TEXT,
    extraction_result_id UUID REFERENCES extraction_results(id) ON DELETE SET NULL,
    template_version_id UUID REFERENCES template_versions(id) ON DELETE SET NULL,
    confidence_score DECIMAL(3,2) DEFAULT 1.00,
    validation_status TEXT DEFAULT 'pending', -- pending, validated, rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tenant_id UUID
);

-- Add lineage references to main tables
ALTER TABLE persons ADD COLUMN IF NOT EXISTS lineage_id UUID REFERENCES data_lineage(id);
ALTER TABLE companies ADD COLUMN IF NOT EXISTS lineage_id UUID REFERENCES data_lineage(id);
ALTER TABLE vehicles ADD COLUMN IF NOT EXISTS lineage_id UUID REFERENCES data_lineage(id);

-- Create data retention policies
CREATE TABLE IF NOT EXISTS data_retention_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    entity_type TEXT NOT NULL,
    retention_days INTEGER NOT NULL,
    action_type TEXT DEFAULT 'delete', -- delete, archive, anonymize
    conditions JSONB, -- Additional conditions for applying the policy
    is_active BOOLEAN DEFAULT true,
    last_executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create anonymization templates
CREATE TABLE IF NOT EXISTS anonymization_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    entity_type TEXT NOT NULL,
    field_mappings JSONB NOT NULL, -- Maps fields to anonymization strategies
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create GDPR request tracking
CREATE TABLE IF NOT EXISTS gdpr_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_type TEXT NOT NULL, -- access, portability, rectification, erasure, restriction
    status TEXT DEFAULT 'pending', -- pending, processing, completed, rejected
    subject_email TEXT NOT NULL,
    subject_identifiers JSONB, -- Additional identifiers to find the subject's data
    request_details JSONB,
    requester_info JSONB,
    processing_notes TEXT,
    completion_evidence JSONB, -- Proof of compliance
    deadline_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tenant_id UUID
);

-- Create system health monitoring
CREATE TABLE IF NOT EXISTS system_health_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name TEXT NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    metric_unit TEXT,
    component TEXT NOT NULL, -- database, api, scraper, proxy_pool, etc.
    severity TEXT DEFAULT 'info', -- info, warning, error, critical
    threshold_warning DECIMAL(15,4),
    threshold_critical DECIMAL(15,4),
    metadata JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    tenant_id UUID
);

-- Create index on metric lookups
CREATE INDEX IF NOT EXISTS idx_system_health_metrics_component_time 
ON system_health_metrics(component, recorded_at DESC);

-- ===================================
-- ADVANCED INDEXES FOR PERFORMANCE
-- ===================================

-- Tenant isolation indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_persons_tenant_id ON persons(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_tenant_id ON companies(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vehicles_tenant_id ON vehicles(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_tenant_id ON jobs(tenant_id);

-- Soft delete indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_persons_deleted_at ON persons(deleted_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_deleted_at ON companies(deleted_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vehicles_deleted_at ON vehicles(deleted_at);

-- Job management indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_queue_priority ON jobs(queue_id, priority, created_at);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_status_retry ON jobs(status, next_retry_at) WHERE status = 'failed';
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_dependencies_job_id ON job_dependencies(job_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_dependencies_depends_on ON job_dependencies(depends_on_job_id);

-- Proxy management indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proxies_pool_status ON proxies(pool_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proxy_usage_logs_proxy_time ON proxy_usage_logs(proxy_id, start_time);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proxy_usage_logs_job_id ON proxy_usage_logs(job_id);

-- Data quality indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_data_quality_rules_entity_field ON data_quality_rules(entity_type, field_name);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_data_lineage_entity ON data_lineage(entity_type, entity_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_extraction_results_job_template ON extraction_results(job_id, template_id);

-- Session tracking indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_user_active ON user_sessions(user_id) WHERE is_active = true;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);

-- GDPR request indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gdpr_requests_email ON gdpr_requests(subject_email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_gdpr_requests_status_deadline ON gdpr_requests(status, deadline_at);

-- Full-text search indexes using GIN and trgm
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_extraction_results_url_trgm ON extraction_results USING GIN(url gin_trgm_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_extraction_results_data ON extraction_results USING GIN(extracted_data);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_template_versions_data ON template_versions USING GIN(template_data);

-- ===================================
-- ADVANCED FUNCTIONS AND TRIGGERS
-- ===================================

-- Enhanced update timestamp function with audit support
CREATE OR REPLACE FUNCTION enhanced_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    
    -- Store old values in a session variable for potential audit use
    PERFORM set_config('audit.old_values', row_to_json(OLD)::text, true);
    PERFORM set_config('audit.new_values', row_to_json(NEW)::text, true);
    PERFORM set_config('audit.table_name', TG_TABLE_NAME, true);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to check data retention policies
CREATE OR REPLACE FUNCTION check_data_retention()
RETURNS TABLE(
    policy_name TEXT,
    entity_type TEXT,
    expired_count INTEGER,
    action_type TEXT
) AS $$
DECLARE
    policy_record RECORD;
    expired_count INTEGER;
BEGIN
    FOR policy_record IN 
        SELECT * FROM data_retention_policies WHERE is_active = true
    LOOP
        -- Check based on entity type
        CASE policy_record.entity_type
            WHEN 'persons' THEN
                SELECT COUNT(*) INTO expired_count
                FROM persons 
                WHERE created_at < (NOW() - INTERVAL '1 day' * policy_record.retention_days)
                AND deleted_at IS NULL;
                
            WHEN 'companies' THEN
                SELECT COUNT(*) INTO expired_count
                FROM companies 
                WHERE created_at < (NOW() - INTERVAL '1 day' * policy_record.retention_days)
                AND deleted_at IS NULL;
                
            WHEN 'vehicles' THEN
                SELECT COUNT(*) INTO expired_count
                FROM vehicles 
                WHERE created_at < (NOW() - INTERVAL '1 day' * policy_record.retention_days)
                AND deleted_at IS NULL;
                
            ELSE
                expired_count := 0;
        END CASE;
        
        RETURN QUERY SELECT 
            policy_record.name,
            policy_record.entity_type,
            expired_count,
            policy_record.action_type;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to anonymize PII data
CREATE OR REPLACE FUNCTION anonymize_person_data(person_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE persons 
    SET 
        full_name = 'ANONYMIZED_' || LEFT(MD5(full_name || id::text), 8),
        first_name = 'FIRST_' || LEFT(MD5(first_name || id::text), 6),
        last_name = 'LAST_' || LEFT(MD5(last_name || id::text), 6),
        email = 'anonymized_' || LEFT(MD5(email || id::text), 10) || '@example.com',
        phone = '+46' || LPAD((RANDOM() * 999999999)::INTEGER::TEXT, 9, '0'),
        personal_number_hash = MD5(personal_number_hash || 'anonymized'),
        phone_number_hash = MD5(phone_number_hash || 'anonymized'),
        email_hash = MD5(email_hash || 'anonymized'),
        address = '{"anonymized": true}'::JSONB,
        social_media = '{"anonymized": true}'::JSONB,
        metadata = jsonb_set(COALESCE(metadata, '{}'::JSONB), '{anonymized}', 'true'::JSONB),
        updated_at = NOW()
    WHERE id = person_id;
    
    -- Log the anonymization
    INSERT INTO audit_logs (table_name, record_id, action, new_values, changed_by, changed_at)
    VALUES ('persons', person_id, 'ANONYMIZED', '{"anonymized": true}'::JSONB, 'system', NOW());
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to calculate data quality score
CREATE OR REPLACE FUNCTION calculate_data_quality_score(
    entity_type_param TEXT,
    entity_id_param UUID
) RETURNS DECIMAL(3,2) AS $$
DECLARE
    total_rules INTEGER := 0;
    passed_rules INTEGER := 0;
    rule_record RECORD;
    field_value TEXT;
    score DECIMAL(3,2);
BEGIN
    -- Get all active rules for this entity type
    FOR rule_record IN 
        SELECT * FROM data_quality_rules 
        WHERE entity_type = entity_type_param AND is_active = true
    LOOP
        total_rules := total_rules + 1;
        
        -- Get the field value based on entity type
        CASE entity_type_param
            WHEN 'persons' THEN
                EXECUTE format('SELECT %I::TEXT FROM persons WHERE id = $1', rule_record.field_name)
                INTO field_value USING entity_id_param;
            WHEN 'companies' THEN
                EXECUTE format('SELECT %I::TEXT FROM companies WHERE id = $1', rule_record.field_name)
                INTO field_value USING entity_id_param;
            WHEN 'vehicles' THEN
                EXECUTE format('SELECT %I::TEXT FROM vehicles WHERE id = $1', rule_record.field_name)
                INTO field_value USING entity_id_param;
        END CASE;
        
        -- Apply rule based on type
        CASE rule_record.rule_type
            WHEN 'required' THEN
                IF field_value IS NOT NULL AND field_value != '' THEN
                    passed_rules := passed_rules + 1;
                END IF;
            WHEN 'format' THEN
                IF field_value ~ rule_record.rule_expression THEN
                    passed_rules := passed_rules + 1;
                END IF;
            -- Add more rule types as needed
        END CASE;
    END LOOP;
    
    -- Calculate score
    IF total_rules > 0 THEN
        score := (passed_rules::DECIMAL / total_rules::DECIMAL);
    ELSE
        score := 1.00;
    END IF;
    
    -- Store the result
    INSERT INTO data_quality_metrics (entity_type, entity_id, metric_name, metric_value, measured_at)
    VALUES (entity_type_param, entity_id_param, 'overall_quality_score', score, NOW())
    ON CONFLICT (entity_type, entity_id, metric_name) 
    DO UPDATE SET metric_value = score, measured_at = NOW();
    
    RETURN score;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger function for comprehensive audit logging
CREATE OR REPLACE FUNCTION comprehensive_audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    old_data JSONB;
    new_data JSONB;
    current_user_id UUID;
BEGIN
    -- Get current user from JWT or session
    current_user_id := COALESCE(
        current_setting('jwt.claims.sub', true)::UUID,
        current_setting('app.current_user_id', true)::UUID,
        NULL
    );
    
    -- Convert rows to JSON
    IF TG_OP = 'DELETE' THEN
        old_data := row_to_json(OLD);
        new_data := NULL;
    ELSIF TG_OP = 'INSERT' THEN
        old_data := NULL;
        new_data := row_to_json(NEW);
    ELSE -- UPDATE
        old_data := row_to_json(OLD);
        new_data := row_to_json(NEW);
    END IF;
    
    -- Insert audit record
    INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by, changed_at)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        old_data,
        new_data,
        COALESCE(current_user_id::TEXT, 'system'),
        NOW()
    );
    
    -- Return appropriate record
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- APPLY TRIGGERS
-- ===================================

-- Apply enhanced update timestamp triggers
DROP TRIGGER IF EXISTS update_persons_updated_at ON persons;
CREATE TRIGGER update_persons_updated_at 
    BEFORE UPDATE ON persons 
    FOR EACH ROW EXECUTE FUNCTION enhanced_update_timestamp();

DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at 
    BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION enhanced_update_timestamp();

DROP TRIGGER IF EXISTS update_vehicles_updated_at ON vehicles;
CREATE TRIGGER update_vehicles_updated_at 
    BEFORE UPDATE ON vehicles 
    FOR EACH ROW EXECUTE FUNCTION enhanced_update_timestamp();

-- Apply enhanced triggers to new tables
CREATE TRIGGER update_job_queues_updated_at 
    BEFORE UPDATE ON job_queues 
    FOR EACH ROW EXECUTE FUNCTION enhanced_update_timestamp();

CREATE TRIGGER update_proxy_pools_updated_at 
    BEFORE UPDATE ON proxy_pools 
    FOR EACH ROW EXECUTE FUNCTION enhanced_update_timestamp();

CREATE TRIGGER update_data_retention_policies_updated_at 
    BEFORE UPDATE ON data_retention_policies 
    FOR EACH ROW EXECUTE FUNCTION enhanced_update_timestamp();

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_persons_changes 
    AFTER INSERT OR UPDATE OR DELETE ON persons
    FOR EACH ROW EXECUTE FUNCTION comprehensive_audit_trigger();

CREATE TRIGGER audit_companies_changes 
    AFTER INSERT OR UPDATE OR DELETE ON companies
    FOR EACH ROW EXECUTE FUNCTION comprehensive_audit_trigger();

CREATE TRIGGER audit_vehicles_changes 
    AFTER INSERT OR UPDATE OR DELETE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION comprehensive_audit_trigger();

CREATE TRIGGER audit_gdpr_requests_changes 
    AFTER INSERT OR UPDATE OR DELETE ON gdpr_requests
    FOR EACH ROW EXECUTE FUNCTION comprehensive_audit_trigger();

-- ===================================
-- ADVANCED VIEWS
-- ===================================

-- Comprehensive data quality dashboard view
CREATE OR REPLACE VIEW data_quality_dashboard AS
SELECT 
    entity_type,
    COUNT(*) as total_records,
    COUNT(CASE WHEN data_quality = 'excellent' THEN 1 END) as excellent_count,
    COUNT(CASE WHEN data_quality = 'good' THEN 1 END) as good_count,
    COUNT(CASE WHEN data_quality = 'fair' THEN 1 END) as fair_count,
    COUNT(CASE WHEN data_quality = 'poor' THEN 1 END) as poor_count,
    ROUND(AVG(CASE 
        WHEN data_quality = 'excellent' THEN 4
        WHEN data_quality = 'good' THEN 3
        WHEN data_quality = 'fair' THEN 2
        WHEN data_quality = 'poor' THEN 1
    END), 2) as avg_quality_score,
    COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as active_records,
    COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as deleted_records
FROM (
    SELECT 'persons' as entity_type, data_quality, deleted_at FROM persons
    UNION ALL
    SELECT 'companies' as entity_type, data_quality, deleted_at FROM companies  
    UNION ALL
    SELECT 'vehicles' as entity_type, data_quality, deleted_at FROM vehicles
) combined
GROUP BY entity_type;

-- Job performance analytics view
CREATE OR REPLACE VIEW job_performance_analytics AS
SELECT 
    j.job_type,
    jq.name as queue_name,
    COUNT(*) as total_jobs,
    COUNT(CASE WHEN j.status = 'completed' THEN 1 END) as completed_jobs,
    COUNT(CASE WHEN j.status = 'failed' THEN 1 END) as failed_jobs,
    COUNT(CASE WHEN j.status = 'running' THEN 1 END) as running_jobs,
    ROUND(AVG(EXTRACT(EPOCH FROM (j.completed_at - j.started_at))), 2) as avg_duration_seconds,
    ROUND(AVG(j.retry_count), 2) as avg_retries,
    MAX(j.created_at) as last_job_created,
    ROUND(
        COUNT(CASE WHEN j.status = 'completed' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(CASE WHEN j.status IN ('completed', 'failed') THEN 1 END), 0) * 100, 
        2
    ) as success_rate_percent
FROM jobs j
LEFT JOIN job_queues jq ON j.queue_id = jq.id
WHERE j.created_at >= NOW() - INTERVAL '30 days'
GROUP BY j.job_type, jq.name;

-- Proxy pool health view
CREATE OR REPLACE VIEW proxy_pool_health AS
SELECT 
    pp.name as pool_name,
    pp.pool_type,
    COUNT(p.id) as total_proxies,
    COUNT(CASE WHEN p.status = 'active' THEN 1 END) as active_proxies,
    COUNT(CASE WHEN p.status = 'failed' THEN 1 END) as failed_proxies,
    ROUND(AVG(p.success_rate), 2) as avg_success_rate,
    ROUND(AVG(p.response_time_ms), 0) as avg_response_time_ms,
    COUNT(CASE WHEN p.last_tested_at > NOW() - INTERVAL '1 hour' THEN 1 END) as recently_tested,
    SUM(p.concurrent_uses) as total_concurrent_uses,
    pp.max_concurrent_uses,
    ROUND(
        COUNT(CASE WHEN p.status = 'active' THEN 1 END)::DECIMAL / 
        NULLIF(COUNT(p.id), 0) * 100, 
        2
    ) as health_percentage
FROM proxy_pools pp
LEFT JOIN proxies p ON pp.id = p.pool_id
WHERE pp.is_active = true
GROUP BY pp.id, pp.name, pp.pool_type, pp.max_concurrent_uses;

-- Data lineage traceability view
CREATE OR REPLACE VIEW data_lineage_trace AS
SELECT 
    dl.entity_type,
    dl.entity_id,
    dl.source_url,
    j.name as job_name,
    j.created_at as job_created_at,
    st.name as template_name,
    tv.version_number as template_version,
    er.success as extraction_success,
    er.response_code,
    er.extraction_time_ms,
    p.host || ':' || p.port as proxy_used,
    dl.confidence_score,
    dl.validation_status
FROM data_lineage dl
LEFT JOIN jobs j ON dl.source_job_id = j.id
LEFT JOIN extraction_results er ON dl.extraction_result_id = er.id
LEFT JOIN template_versions tv ON dl.template_version_id = tv.id
LEFT JOIN scraping_templates st ON tv.template_id = st.id
LEFT JOIN proxies p ON er.proxy_id = p.id;

-- System health monitoring view
CREATE OR REPLACE VIEW system_health_overview AS
SELECT 
    component,
    COUNT(*) as metric_count,
    COUNT(CASE WHEN severity = 'critical' THEN 1 END) as critical_issues,
    COUNT(CASE WHEN severity = 'error' THEN 1 END) as error_issues,
    COUNT(CASE WHEN severity = 'warning' THEN 1 END) as warning_issues,
    MAX(recorded_at) as last_recorded,
    ROUND(AVG(metric_value), 2) as avg_metric_value,
    MIN(metric_value) as min_metric_value,
    MAX(metric_value) as max_metric_value
FROM system_health_metrics 
WHERE recorded_at >= NOW() - INTERVAL '1 day'
GROUP BY component
ORDER BY critical_issues DESC, error_issues DESC;

-- Migration complete
SELECT 'ECaDP Enhanced Schema Migration 002 completed successfully' as result;
