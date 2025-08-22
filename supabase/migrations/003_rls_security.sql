-- ECaDP Row-Level Security and Multi-Tenant Setup
-- Migration: 003_rls_security.sql
-- Description: Comprehensive RLS policies for multi-tenant isolation and security
-- Date: 2025-01-22
-- Author: ECaDP Development Team

-- ===================================
-- ROW-LEVEL SECURITY SETUP
-- ===================================

-- Enable RLS on all sensitive tables
ALTER TABLE persons ENABLE ROW LEVEL SECURITY;
ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_dependencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraping_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE template_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE export_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE extraction_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_lineage ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE gdpr_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE proxy_usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_health_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_quality_metrics ENABLE ROW LEVEL SECURITY;

-- Keep certain tables without RLS for system-wide access
-- proxies, proxy_pools, job_queues, data_quality_rules, data_retention_policies, anonymization_templates

-- ===================================
-- TENANT ISOLATION POLICIES
-- ===================================

-- Helper function to get current tenant ID from JWT
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS UUID AS $$
BEGIN
    -- Try to get tenant_id from JWT claims
    RETURN COALESCE(
        current_setting('jwt.claims.tenant_id', true)::UUID,
        current_setting('app.current_tenant_id', true)::UUID
    );
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN COALESCE(
        current_setting('jwt.claims.role', true) = 'admin',
        current_setting('app.is_admin', true)::BOOLEAN,
        false
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Helper function to get current user ID
CREATE OR REPLACE FUNCTION get_current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN COALESCE(
        current_setting('jwt.claims.sub', true)::UUID,
        current_setting('app.current_user_id', true)::UUID
    );
EXCEPTION WHEN OTHERS THEN
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- PERSONS TABLE RLS POLICIES
-- ===================================

-- Persons: Select policy - tenant isolation with soft delete filter
CREATE POLICY persons_select_policy ON persons FOR SELECT
USING (
    (tenant_id = get_current_tenant_id() OR is_admin())
    AND deleted_at IS NULL
);

-- Persons: Insert policy - auto-set tenant_id
CREATE POLICY persons_insert_policy ON persons FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND deleted_at IS NULL
);

-- Persons: Update policy - tenant isolation, no changing tenant_id
CREATE POLICY persons_update_policy ON persons FOR UPDATE
USING (
    (tenant_id = get_current_tenant_id() OR is_admin())
    AND deleted_at IS NULL
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id) -- Prevent tenant_id changes
);

-- Persons: Delete policy - soft delete only, admin can hard delete
CREATE POLICY persons_delete_policy ON persons FOR DELETE
USING (
    tenant_id = get_current_tenant_id()
    AND (deleted_at IS NOT NULL OR is_admin()) -- Only delete already soft-deleted or if admin
);

-- ===================================
-- COMPANIES TABLE RLS POLICIES  
-- ===================================

CREATE POLICY companies_select_policy ON companies FOR SELECT
USING (
    (tenant_id = get_current_tenant_id() OR is_admin())
    AND deleted_at IS NULL
);

CREATE POLICY companies_insert_policy ON companies FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND deleted_at IS NULL
);

CREATE POLICY companies_update_policy ON companies FOR UPDATE
USING (
    (tenant_id = get_current_tenant_id() OR is_admin())
    AND deleted_at IS NULL
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

CREATE POLICY companies_delete_policy ON companies FOR DELETE
USING (
    tenant_id = get_current_tenant_id()
    AND (deleted_at IS NOT NULL OR is_admin())
);

-- ===================================
-- VEHICLES TABLE RLS POLICIES
-- ===================================

CREATE POLICY vehicles_select_policy ON vehicles FOR SELECT
USING (
    (tenant_id = get_current_tenant_id() OR is_admin())
    AND deleted_at IS NULL
);

CREATE POLICY vehicles_insert_policy ON vehicles FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND deleted_at IS NULL
);

CREATE POLICY vehicles_update_policy ON vehicles FOR UPDATE
USING (
    (tenant_id = get_current_tenant_id() OR is_admin())
    AND deleted_at IS NULL
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

CREATE POLICY vehicles_delete_policy ON vehicles FOR DELETE
USING (
    tenant_id = get_current_tenant_id()
    AND (deleted_at IS NOT NULL OR is_admin())
);

-- ===================================
-- JOBS TABLE RLS POLICIES
-- ===================================

-- Jobs: Users can see their own jobs and admin can see all
CREATE POLICY jobs_select_policy ON jobs FOR SELECT
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
);

CREATE POLICY jobs_insert_policy ON jobs FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
);

CREATE POLICY jobs_update_policy ON jobs FOR UPDATE
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

-- Jobs: Delete policy - admin only
CREATE POLICY jobs_delete_policy ON jobs FOR DELETE
USING (is_admin());

-- ===================================
-- JOB DEPENDENCIES RLS POLICIES
-- ===================================

CREATE POLICY job_dependencies_select_policy ON job_dependencies FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM jobs j 
        WHERE j.id = job_dependencies.job_id 
        AND (j.tenant_id = get_current_tenant_id() OR is_admin())
    )
);

CREATE POLICY job_dependencies_insert_policy ON job_dependencies FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM jobs j 
        WHERE j.id = job_dependencies.job_id 
        AND j.tenant_id = get_current_tenant_id()
    )
);

-- ===================================
-- SCRAPING TEMPLATES RLS POLICIES
-- ===================================

-- Templates: Users can see their own templates and public ones
CREATE POLICY scraping_templates_select_policy ON scraping_templates FOR SELECT
USING (
    tenant_id = get_current_tenant_id()
    OR is_admin()
    OR (tenant_id IS NULL AND is_active = true) -- Public templates
);

CREATE POLICY scraping_templates_insert_policy ON scraping_templates FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
);

CREATE POLICY scraping_templates_update_policy ON scraping_templates FOR UPDATE
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

CREATE POLICY scraping_templates_delete_policy ON scraping_templates FOR DELETE
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
);

-- ===================================
-- TEMPLATE VERSIONS RLS POLICIES
-- ===================================

CREATE POLICY template_versions_select_policy ON template_versions FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM scraping_templates st 
        WHERE st.id = template_versions.template_id 
        AND (
            st.tenant_id = get_current_tenant_id()
            OR is_admin()
            OR (st.tenant_id IS NULL AND st.is_active = true)
        )
    )
);

CREATE POLICY template_versions_insert_policy ON template_versions FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM scraping_templates st 
        WHERE st.id = template_versions.template_id 
        AND st.tenant_id = get_current_tenant_id()
    )
);

-- ===================================
-- EXPORT JOBS RLS POLICIES
-- ===================================

CREATE POLICY export_jobs_select_policy ON export_jobs FOR SELECT
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
);

CREATE POLICY export_jobs_insert_policy ON export_jobs FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
);

CREATE POLICY export_jobs_update_policy ON export_jobs FOR UPDATE
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

-- ===================================
-- EXTRACTION RESULTS RLS POLICIES
-- ===================================

CREATE POLICY extraction_results_select_policy ON extraction_results FOR SELECT
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
);

CREATE POLICY extraction_results_insert_policy ON extraction_results FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
);

CREATE POLICY extraction_results_update_policy ON extraction_results FOR UPDATE
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

-- ===================================
-- DATA LINEAGE RLS POLICIES
-- ===================================

CREATE POLICY data_lineage_select_policy ON data_lineage FOR SELECT
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
);

CREATE POLICY data_lineage_insert_policy ON data_lineage FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
);

CREATE POLICY data_lineage_update_policy ON data_lineage FOR UPDATE
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

-- ===================================
-- USER SESSIONS RLS POLICIES
-- ===================================

-- Sessions: Users can only see their own sessions
CREATE POLICY user_sessions_select_policy ON user_sessions FOR SELECT
USING (
    user_id = get_current_user_id() OR is_admin()
);

CREATE POLICY user_sessions_insert_policy ON user_sessions FOR INSERT
WITH CHECK (
    user_id = get_current_user_id()
);

CREATE POLICY user_sessions_update_policy ON user_sessions FOR UPDATE
USING (
    user_id = get_current_user_id() OR is_admin()
)
WITH CHECK (
    user_id = get_current_user_id()
    AND (OLD.user_id = NEW.user_id)
);

CREATE POLICY user_sessions_delete_policy ON user_sessions FOR DELETE
USING (
    user_id = get_current_user_id() OR is_admin()
);

-- ===================================
-- GDPR REQUESTS RLS POLICIES
-- ===================================

-- GDPR requests: Users can see requests for their tenant
CREATE POLICY gdpr_requests_select_policy ON gdpr_requests FOR SELECT
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
);

CREATE POLICY gdpr_requests_insert_policy ON gdpr_requests FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
);

CREATE POLICY gdpr_requests_update_policy ON gdpr_requests FOR UPDATE
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
)
WITH CHECK (
    tenant_id = get_current_tenant_id()
    AND (OLD.tenant_id = NEW.tenant_id)
);

-- ===================================
-- PROXY USAGE LOGS RLS POLICIES
-- ===================================

CREATE POLICY proxy_usage_logs_select_policy ON proxy_usage_logs FOR SELECT
USING (
    tenant_id = get_current_tenant_id() OR is_admin()
);

CREATE POLICY proxy_usage_logs_insert_policy ON proxy_usage_logs FOR INSERT
WITH CHECK (
    tenant_id = get_current_tenant_id()
);

-- ===================================
-- SYSTEM HEALTH METRICS RLS POLICIES
-- ===================================

-- System health: Admin-only or service role
CREATE POLICY system_health_metrics_select_policy ON system_health_metrics FOR SELECT
USING (
    is_admin() 
    OR current_setting('jwt.claims.role', true) = 'service'
    OR tenant_id = get_current_tenant_id()
);

CREATE POLICY system_health_metrics_insert_policy ON system_health_metrics FOR INSERT
WITH CHECK (
    is_admin() 
    OR current_setting('jwt.claims.role', true) = 'service'
);

-- ===================================
-- DATA QUALITY METRICS RLS POLICIES
-- ===================================

-- Data quality metrics: Based on related entity access
CREATE POLICY data_quality_metrics_select_policy ON data_quality_metrics FOR SELECT
USING (
    is_admin()
    OR (
        entity_type = 'persons' 
        AND entity_id IN (
            SELECT id FROM persons 
            WHERE tenant_id = get_current_tenant_id() 
            AND deleted_at IS NULL
        )
    )
    OR (
        entity_type = 'companies'
        AND entity_id IN (
            SELECT id FROM companies 
            WHERE tenant_id = get_current_tenant_id() 
            AND deleted_at IS NULL
        )
    )
    OR (
        entity_type = 'vehicles'
        AND entity_id IN (
            SELECT id FROM vehicles 
            WHERE tenant_id = get_current_tenant_id() 
            AND deleted_at IS NULL
        )
    )
);

-- ===================================
-- DEFAULT TENANT ASSIGNMENT FUNCTIONS
-- ===================================

-- Function to automatically set tenant_id on insert
CREATE OR REPLACE FUNCTION auto_set_tenant_id()
RETURNS TRIGGER AS $$
BEGIN
    -- Only set tenant_id if not already provided
    IF NEW.tenant_id IS NULL THEN
        NEW.tenant_id := get_current_tenant_id();
    END IF;
    
    -- Validate that tenant_id matches current user's tenant
    IF NEW.tenant_id != get_current_tenant_id() AND NOT is_admin() THEN
        RAISE EXCEPTION 'Access denied: Cannot create records for different tenant';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Apply auto tenant assignment triggers
CREATE TRIGGER auto_set_tenant_id_persons 
    BEFORE INSERT ON persons 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

CREATE TRIGGER auto_set_tenant_id_companies 
    BEFORE INSERT ON companies 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

CREATE TRIGGER auto_set_tenant_id_vehicles 
    BEFORE INSERT ON vehicles 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

CREATE TRIGGER auto_set_tenant_id_jobs 
    BEFORE INSERT ON jobs 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

CREATE TRIGGER auto_set_tenant_id_export_jobs 
    BEFORE INSERT ON export_jobs 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

CREATE TRIGGER auto_set_tenant_id_extraction_results 
    BEFORE INSERT ON extraction_results 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

CREATE TRIGGER auto_set_tenant_id_data_lineage 
    BEFORE INSERT ON data_lineage 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

CREATE TRIGGER auto_set_tenant_id_gdpr_requests 
    BEFORE INSERT ON gdpr_requests 
    FOR EACH ROW EXECUTE FUNCTION auto_set_tenant_id();

-- ===================================
-- SOFT DELETE FUNCTIONS
-- ===================================

-- Function for soft deleting persons with cascade to related data
CREATE OR REPLACE FUNCTION soft_delete_person(person_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Verify access
    IF NOT EXISTS (
        SELECT 1 FROM persons 
        WHERE id = person_id 
        AND (tenant_id = get_current_tenant_id() OR is_admin())
        AND deleted_at IS NULL
    ) THEN
        RAISE EXCEPTION 'Person not found or access denied';
    END IF;
    
    -- Soft delete the person
    UPDATE persons 
    SET deleted_at = NOW() 
    WHERE id = person_id;
    
    -- Optionally soft delete related vehicles
    UPDATE vehicles 
    SET deleted_at = NOW() 
    WHERE owner_id = person_id AND deleted_at IS NULL;
    
    -- Log the action
    INSERT INTO audit_logs (table_name, record_id, action, changed_by, changed_at)
    VALUES ('persons', person_id, 'SOFT_DELETE', get_current_user_id()::TEXT, NOW());
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function for soft deleting companies with cascade
CREATE OR REPLACE FUNCTION soft_delete_company(company_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    -- Verify access
    IF NOT EXISTS (
        SELECT 1 FROM companies 
        WHERE id = company_id 
        AND (tenant_id = get_current_tenant_id() OR is_admin())
        AND deleted_at IS NULL
    ) THEN
        RAISE EXCEPTION 'Company not found or access denied';
    END IF;
    
    -- Soft delete the company
    UPDATE companies 
    SET deleted_at = NOW() 
    WHERE id = company_id;
    
    -- Optionally handle related persons (set company_id to NULL or leave as is)
    -- UPDATE persons SET company_id = NULL WHERE company_id = company_id;
    
    -- Log the action
    INSERT INTO audit_logs (table_name, record_id, action, changed_by, changed_at)
    VALUES ('companies', company_id, 'SOFT_DELETE', get_current_user_id()::TEXT, NOW());
    
    RETURN true;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- TENANT-AWARE VIEWS
-- ===================================

-- Create tenant-aware views that automatically filter by current tenant
CREATE OR REPLACE VIEW tenant_persons AS
SELECT * FROM persons 
WHERE tenant_id = get_current_tenant_id() 
AND deleted_at IS NULL;

CREATE OR REPLACE VIEW tenant_companies AS
SELECT * FROM companies 
WHERE tenant_id = get_current_tenant_id() 
AND deleted_at IS NULL;

CREATE OR REPLACE VIEW tenant_vehicles AS
SELECT * FROM vehicles 
WHERE tenant_id = get_current_tenant_id() 
AND deleted_at IS NULL;

CREATE OR REPLACE VIEW tenant_jobs AS
SELECT * FROM jobs 
WHERE tenant_id = get_current_tenant_id();

-- ===================================
-- SECURITY VALIDATION FUNCTIONS
-- ===================================

-- Function to validate RLS is working correctly
CREATE OR REPLACE FUNCTION test_rls_isolation()
RETURNS TABLE(
    test_name TEXT,
    passed BOOLEAN,
    message TEXT
) AS $$
DECLARE
    test_tenant_id UUID := gen_random_uuid();
    other_tenant_id UUID := gen_random_uuid();
    test_person_id UUID;
BEGIN
    -- Test 1: Create person with specific tenant_id
    BEGIN
        PERFORM set_config('app.current_tenant_id', test_tenant_id::TEXT, true);
        
        INSERT INTO persons (full_name, tenant_id) 
        VALUES ('Test Person', test_tenant_id) 
        RETURNING id INTO test_person_id;
        
        RETURN QUERY SELECT 
            'Tenant assignment'::TEXT, 
            true, 
            'Person created with correct tenant_id'::TEXT;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT 
            'Tenant assignment'::TEXT, 
            false, 
            SQLERRM::TEXT;
    END;
    
    -- Test 2: Try to access person from different tenant
    BEGIN
        PERFORM set_config('app.current_tenant_id', other_tenant_id::TEXT, true);
        
        IF EXISTS (SELECT 1 FROM persons WHERE id = test_person_id) THEN
            RETURN QUERY SELECT 
                'Tenant isolation'::TEXT, 
                false, 
                'Should not be able to see person from different tenant'::TEXT;
        ELSE
            RETURN QUERY SELECT 
                'Tenant isolation'::TEXT, 
                true, 
                'Correctly isolated tenant data'::TEXT;
        END IF;
    EXCEPTION WHEN OTHERS THEN
        RETURN QUERY SELECT 
            'Tenant isolation'::TEXT, 
            false, 
            SQLERRM::TEXT;
    END;
    
    -- Clean up test data
    PERFORM set_config('app.is_admin', 'true', true);
    DELETE FROM persons WHERE id = test_person_id;
    PERFORM set_config('app.is_admin', 'false', true);
    
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- GRANT PERMISSIONS TO ROLES
-- ===================================

-- Grant execute permissions on security functions
GRANT EXECUTE ON FUNCTION get_current_tenant_id() TO authenticated;
GRANT EXECUTE ON FUNCTION is_admin() TO authenticated;
GRANT EXECUTE ON FUNCTION get_current_user_id() TO authenticated;
GRANT EXECUTE ON FUNCTION soft_delete_person(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION soft_delete_company(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION test_rls_isolation() TO ecadp_admin;

-- Grant view access
GRANT SELECT ON tenant_persons TO authenticated;
GRANT SELECT ON tenant_companies TO authenticated;
GRANT SELECT ON tenant_vehicles TO authenticated;
GRANT SELECT ON tenant_jobs TO authenticated;

-- Migration complete
SELECT 'ECaDP RLS Security Migration 003 completed successfully' as result;
