-- ECaDP Initial Schema Migration
-- Migration: 001_initial_schema.sql
-- Description: Creates the foundational database schema for the ECaDP platform
-- Date: 2025-01-01
-- Author: ECaDP Development Team

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create custom types
CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
CREATE TYPE job_type AS ENUM ('crawl', 'scrape', 'export', 'analysis', 'cleanup');
CREATE TYPE data_quality_level AS ENUM ('poor', 'fair', 'good', 'excellent');
CREATE TYPE export_format AS ENUM ('csv', 'json', 'excel', 'xml');
CREATE TYPE proxy_status AS ENUM ('active', 'inactive', 'banned', 'testing');

-- Create core entities tables
CREATE TABLE IF NOT EXISTS persons (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    birth_date DATE,
    occupation TEXT,
    company_id UUID,
    address JSONB,
    social_media JSONB,
    data_quality data_quality_level DEFAULT 'fair',
    metadata JSONB DEFAULT '{}',
    source_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    organization_number TEXT UNIQUE,
    industry_code TEXT,
    industry_description TEXT,
    website TEXT,
    email TEXT,
    phone TEXT,
    address JSONB,
    founded_year INTEGER,
    employee_count INTEGER,
    revenue NUMERIC,
    description TEXT,
    data_quality data_quality_level DEFAULT 'fair',
    metadata JSONB DEFAULT '{}',
    source_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_number TEXT UNIQUE NOT NULL,
    vin TEXT UNIQUE,
    make TEXT,
    model TEXT,
    year INTEGER,
    color TEXT,
    fuel_type TEXT,
    engine_size TEXT,
    transmission TEXT,
    owner_id UUID,
    current_mileage INTEGER,
    inspection_date DATE,
    insurance_info JSONB,
    data_quality data_quality_level DEFAULT 'fair',
    metadata JSONB DEFAULT '{}',
    source_url TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create job management tables
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type job_type NOT NULL,
    status job_status DEFAULT 'pending',
    name TEXT NOT NULL,
    description TEXT,
    parameters JSONB DEFAULT '{}',
    progress INTEGER DEFAULT 0,
    result JSONB,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create proxy pool tables
CREATE TABLE IF NOT EXISTS proxies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    host TEXT NOT NULL,
    port INTEGER NOT NULL,
    protocol TEXT DEFAULT 'http',
    username TEXT,
    password TEXT,
    status proxy_status DEFAULT 'testing',
    country_code TEXT,
    city TEXT,
    provider TEXT,
    response_time_ms INTEGER,
    success_rate DECIMAL(5,2) DEFAULT 0.00,
    last_tested_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(host, port)
);

-- Create scraping templates table
CREATE TABLE IF NOT EXISTS scraping_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    domain TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    template_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create export jobs table
CREATE TABLE IF NOT EXISTS export_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    format export_format NOT NULL,
    entity_type TEXT NOT NULL,
    filters JSONB DEFAULT '{}',
    file_path TEXT,
    file_size BIGINT,
    record_count INTEGER,
    status job_status DEFAULT 'pending',
    created_by TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create data quality metrics table
CREATE TABLE IF NOT EXISTS data_quality_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value DECIMAL(5,2) NOT NULL,
    threshold_min DECIMAL(5,2),
    threshold_max DECIMAL(5,2),
    is_passing BOOLEAN DEFAULT true,
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    action TEXT NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by TEXT,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_persons_full_name ON persons USING GIN (full_name gin_trgm_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_persons_email ON persons (email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_persons_company_id ON persons (company_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_persons_data_quality ON persons (data_quality);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_persons_created_at ON persons (created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_name ON companies USING GIN (name gin_trgm_ops);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_org_number ON companies (organization_number);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_industry ON companies (industry_code);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_data_quality ON companies (data_quality);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vehicles_reg_number ON vehicles (registration_number);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vehicles_vin ON vehicles (vin);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vehicles_make_model ON vehicles (make, model);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vehicles_owner_id ON vehicles (owner_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_status ON jobs (status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_type ON jobs (type);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_jobs_created_at ON jobs (created_at);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proxies_status ON proxies (status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proxies_country ON proxies (country_code);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_proxies_success_rate ON proxies (success_rate);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_export_jobs_status ON export_jobs (status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_export_jobs_entity_type ON export_jobs (entity_type);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_data_quality_entity ON data_quality_metrics (entity_type, entity_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_data_quality_metric ON data_quality_metrics (metric_name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_table_record ON audit_logs (table_name, record_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_changed_at ON audit_logs (changed_at);

-- Add foreign key constraints
ALTER TABLE persons ADD CONSTRAINT fk_persons_company 
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL;

ALTER TABLE vehicles ADD CONSTRAINT fk_vehicles_owner 
    FOREIGN KEY (owner_id) REFERENCES persons(id) ON DELETE SET NULL;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_persons_updated_at BEFORE UPDATE ON persons 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companies_updated_at BEFORE UPDATE ON companies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proxies_updated_at BEFORE UPDATE ON proxies 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_scraping_templates_updated_at BEFORE UPDATE ON scraping_templates 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_export_jobs_updated_at BEFORE UPDATE ON export_jobs 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data
INSERT INTO scraping_templates (name, description, domain, template_data) VALUES
('person_profile_v1', 'Basic person profile scraping template', 'example.com', '{"selectors": {"name": ".profile-name", "email": ".contact-email"}}'),
('company_profile_v1', 'Basic company profile scraping template', 'company-site.com', '{"selectors": {"name": ".company-name", "website": ".company-url"}}'),
('vehicle_detail_v1', 'Basic vehicle detail scraping template', 'vehicle-registry.se', '{"selectors": {"reg_number": ".reg-no", "make": ".make"}}')
ON CONFLICT (name) DO NOTHING;

-- Create views for data quality reporting
CREATE OR REPLACE VIEW data_quality_summary AS
SELECT 
    'persons' as entity_type,
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
    END), 2) as avg_quality_score
FROM persons
UNION ALL
SELECT 
    'companies' as entity_type,
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
    END), 2) as avg_quality_score
FROM companies
UNION ALL
SELECT 
    'vehicles' as entity_type,
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
    END), 2) as avg_quality_score
FROM vehicles;

-- Grant permissions (adjust as needed for your security model)
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Comment the schema
COMMENT ON TABLE persons IS 'Stores information about individuals scraped from various sources';
COMMENT ON TABLE companies IS 'Stores information about companies and organizations';
COMMENT ON TABLE vehicles IS 'Stores information about vehicles and their registrations';
COMMENT ON TABLE jobs IS 'Tracks background jobs and their execution status';
COMMENT ON TABLE proxies IS 'Manages proxy pool for web scraping operations';
COMMENT ON TABLE scraping_templates IS 'Stores reusable scraping templates for different websites';
COMMENT ON TABLE export_jobs IS 'Tracks data export operations and their status';
COMMENT ON TABLE data_quality_metrics IS 'Stores data quality measurements for all entities';
COMMENT ON TABLE audit_logs IS 'Maintains audit trail of all data changes';

-- Migration complete
SELECT 'ECaDP Initial Schema Migration 001 completed successfully' as result;
