-- Define custom ENUM types for ECaDP platform
-- Job execution status
CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');

-- Data extraction methods
CREATE TYPE extraction_method AS ENUM ('http', 'selenium', 'playwright', 'api');

-- Proxy status
CREATE TYPE proxy_status AS ENUM ('active', 'inactive', 'failed', 'banned');

-- Data quality levels
CREATE TYPE data_quality_level AS ENUM ('excellent', 'good', 'fair', 'poor', 'unknown');

-- Scraping transport modes
CREATE TYPE transport_mode AS ENUM ('http', 'browser');

-- Anti-bot detection levels
CREATE TYPE detection_level AS ENUM ('none', 'low', 'medium', 'high', 'blocked');

-- Export formats
CREATE TYPE export_format AS ENUM ('csv', 'json', 'excel', 'xml', 'parquet');

-- Template statuses
CREATE TYPE template_status AS ENUM ('draft', 'active', 'deprecated', 'archived');

-- Address types
CREATE TYPE address_type AS ENUM ('home', 'work', 'billing', 'shipping', 'other');

-- Contact types
CREATE TYPE contact_type AS ENUM ('email', 'phone', 'fax', 'website', 'social');

-- Company role types
CREATE TYPE company_role AS ENUM ('owner', 'ceo', 'cfo', 'director', 'manager', 'employee', 'consultant');

-- Vehicle ownership types
CREATE TYPE ownership_type AS ENUM ('owner', 'lessee', 'previous_owner', 'registered_user');

-- Comments
COMMENT ON TYPE job_status IS 'Status of scraping and processing jobs';
COMMENT ON TYPE extraction_method IS 'Method used for data extraction';
COMMENT ON TYPE proxy_status IS 'Current status of proxy servers';
COMMENT ON TYPE data_quality_level IS 'Quality assessment levels for extracted data';
COMMENT ON TYPE transport_mode IS 'Transport protocol for web requests';
COMMENT ON TYPE detection_level IS 'Level of anti-bot detection encountered';
COMMENT ON TYPE export_format IS 'Supported data export formats';
COMMENT ON TYPE template_status IS 'Lifecycle status of extraction templates';
COMMENT ON TYPE address_type IS 'Classification of address records';
COMMENT ON TYPE contact_type IS 'Type of contact information';
COMMENT ON TYPE company_role IS 'Role type within a company';
COMMENT ON TYPE ownership_type IS 'Type of vehicle ownership relationship';