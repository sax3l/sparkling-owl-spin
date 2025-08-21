-- Enable required PostgreSQL extensions
-- This migration sets up all necessary extensions for the ECaDP platform

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full-text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- JSON operations
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- HTTP client for external API calls
CREATE EXTENSION IF NOT EXISTS "http";

-- Comments
COMMENT ON EXTENSION "uuid-ossp" IS 'UUID generation functions';
COMMENT ON EXTENSION "pg_trgm" IS 'Trigram matching for fuzzy text search';
COMMENT ON EXTENSION "pgcrypto" IS 'Cryptographic functions';
COMMENT ON EXTENSION "http" IS 'HTTP client for external requests';