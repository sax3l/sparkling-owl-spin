-- ECaDP Advanced Business Logic and RPC Functions
-- Migration: 004_business_logic.sql
-- Description: Stored procedures, business rules, and advanced database functions
-- Date: 2025-01-22
-- Author: ECaDP Development Team

-- ===================================
-- BUSINESS LOGIC FUNCTIONS
-- ===================================

-- Function to get company employee count
CREATE OR REPLACE FUNCTION get_company_employee_count(company_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*) 
        FROM persons 
        WHERE company_id = get_company_employee_count.company_id 
        AND deleted_at IS NULL
        AND (tenant_id = get_current_tenant_id() OR is_admin())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get person's vehicle count
CREATE OR REPLACE FUNCTION get_person_vehicle_count(person_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*) 
        FROM vehicles 
        WHERE owner_id = get_person_vehicle_count.person_id 
        AND deleted_at IS NULL
        AND (tenant_id = get_current_tenant_id() OR is_admin())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to calculate extraction success rate for a template
CREATE OR REPLACE FUNCTION get_template_success_rate(template_id UUID, days INTEGER DEFAULT 30)
RETURNS DECIMAL(5,2) AS $$
DECLARE
    total_extractions INTEGER;
    successful_extractions INTEGER;
BEGIN
    SELECT 
        COUNT(*), 
        COUNT(CASE WHEN success = true THEN 1 END)
    INTO total_extractions, successful_extractions
    FROM extraction_results er
    WHERE er.template_id = get_template_success_rate.template_id
    AND er.created_at >= NOW() - INTERVAL '1 day' * days
    AND (er.tenant_id = get_current_tenant_id() OR is_admin());
    
    IF total_extractions = 0 THEN
        RETURN 0.00;
    END IF;
    
    RETURN (successful_extractions::DECIMAL / total_extractions::DECIMAL) * 100;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get next available proxy from a pool
CREATE OR REPLACE FUNCTION get_next_proxy(pool_id UUID DEFAULT NULL)
RETURNS TABLE(
    proxy_id UUID,
    host TEXT,
    port INTEGER,
    protocol TEXT,
    username TEXT,
    password TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.host,
        p.port,
        p.protocol,
        p.username,
        p.password
    FROM proxies p
    LEFT JOIN proxy_pools pp ON p.pool_id = pp.id
    WHERE p.status = 'active'
    AND p.concurrent_uses < COALESCE(pp.max_concurrent_uses, 10)
    AND (pool_id IS NULL OR p.pool_id = get_next_proxy.pool_id)
    ORDER BY 
        p.concurrent_uses ASC,
        p.last_used_at ASC NULLS FIRST,
        RANDOM()
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to record proxy usage
CREATE OR REPLACE FUNCTION record_proxy_usage(
    proxy_id UUID,
    job_id UUID DEFAULT NULL,
    url TEXT DEFAULT NULL,
    success BOOLEAN DEFAULT NULL,
    response_code INTEGER DEFAULT NULL,
    response_time_ms INTEGER DEFAULT NULL,
    error_message TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Update proxy statistics
    UPDATE proxies 
    SET 
        last_used_at = NOW(),
        concurrent_uses = GREATEST(concurrent_uses - 1, 0),
        success_rate = CASE 
            WHEN success IS NOT NULL THEN
                (success_rate * (COALESCE(success_count, 0) + COALESCE(failure_count, 0)) + 
                 CASE WHEN success THEN 100 ELSE 0 END) / 
                (COALESCE(success_count, 0) + COALESCE(failure_count, 0) + 1)
            ELSE success_rate
        END,
        success_count = CASE WHEN success = true THEN COALESCE(success_count, 0) + 1 ELSE COALESCE(success_count, 0) END,
        failure_count = CASE WHEN success = false THEN COALESCE(failure_count, 0) + 1 ELSE COALESCE(failure_count, 0) END,
        response_time_ms = COALESCE(record_proxy_usage.response_time_ms, response_time_ms),
        last_success_at = CASE WHEN success = true THEN NOW() ELSE last_success_at END,
        last_failure_at = CASE WHEN success = false THEN NOW() ELSE last_failure_at END,
        failure_count = CASE WHEN success = false THEN COALESCE(failure_count, 0) + 1 ELSE failure_count END
    WHERE id = record_proxy_usage.proxy_id;
    
    -- Log usage if URL provided
    IF url IS NOT NULL THEN
        INSERT INTO proxy_usage_logs (
            proxy_id, job_id, url, end_time, response_code, 
            response_time_ms, success, error_message, tenant_id
        ) VALUES (
            record_proxy_usage.proxy_id,
            record_proxy_usage.job_id,
            record_proxy_usage.url,
            NOW(),
            record_proxy_usage.response_code,
            record_proxy_usage.response_time_ms,
            record_proxy_usage.success,
            record_proxy_usage.error_message,
            get_current_tenant_id()
        );
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to reserve a proxy for use
CREATE OR REPLACE FUNCTION reserve_proxy(proxy_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE proxies 
    SET concurrent_uses = concurrent_uses + 1
    WHERE id = reserve_proxy.proxy_id
    AND status = 'active';
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- JOB MANAGEMENT FUNCTIONS
-- ===================================

-- Function to check job dependencies before execution
CREATE OR REPLACE FUNCTION check_job_dependencies(job_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    blocking_deps INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO blocking_deps
    FROM job_dependencies jd
    JOIN jobs j ON jd.depends_on_job_id = j.id
    WHERE jd.job_id = check_job_dependencies.job_id
    AND jd.dependency_type = 'blocking'
    AND j.status NOT IN ('completed', 'failed', 'cancelled');
    
    RETURN blocking_deps = 0;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to queue a job with dependencies
CREATE OR REPLACE FUNCTION queue_job_with_dependencies(
    job_name TEXT,
    job_type TEXT,
    job_config JSONB DEFAULT '{}'::JSONB,
    queue_name TEXT DEFAULT 'default',
    depends_on_jobs UUID[] DEFAULT ARRAY[]::UUID[]
) RETURNS UUID AS $$
DECLARE
    new_job_id UUID;
    queue_id UUID;
    dep_job_id UUID;
BEGIN
    -- Get queue ID
    SELECT id INTO queue_id 
    FROM job_queues 
    WHERE name = queue_name AND is_active = true;
    
    IF queue_id IS NULL THEN
        RAISE EXCEPTION 'Queue % not found or inactive', queue_name;
    END IF;
    
    -- Create the job
    INSERT INTO jobs (name, job_type, parameters, queue_id, status, tenant_id)
    VALUES (
        job_name,
        job_type,
        job_config,
        queue_id,
        CASE WHEN array_length(depends_on_jobs, 1) > 0 THEN 'pending' ELSE 'queued' END,
        get_current_tenant_id()
    )
    RETURNING id INTO new_job_id;
    
    -- Add dependencies
    FOREACH dep_job_id IN ARRAY depends_on_jobs
    LOOP
        INSERT INTO job_dependencies (job_id, depends_on_job_id)
        VALUES (new_job_id, dep_job_id);
    END LOOP;
    
    RETURN new_job_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get next ready job from queue
CREATE OR REPLACE FUNCTION get_next_ready_job(queue_name TEXT DEFAULT NULL)
RETURNS TABLE(
    job_id UUID,
    job_name TEXT,
    job_type TEXT,
    parameters JSONB,
    priority INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        j.id,
        j.name,
        j.job_type,
        j.parameters,
        j.priority
    FROM jobs j
    LEFT JOIN job_queues jq ON j.queue_id = jq.id
    WHERE j.status = 'queued'
    AND (queue_name IS NULL OR jq.name = get_next_ready_job.queue_name)
    AND check_job_dependencies(j.id) = true
    AND (j.next_retry_at IS NULL OR j.next_retry_at <= NOW())
    AND (j.tenant_id = get_current_tenant_id() OR is_admin())
    ORDER BY j.priority DESC, j.created_at ASC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to update job status with progress
CREATE OR REPLACE FUNCTION update_job_status(
    job_id UUID,
    new_status TEXT,
    progress INTEGER DEFAULT NULL,
    result JSONB DEFAULT NULL,
    error_message TEXT DEFAULT NULL
) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE jobs 
    SET 
        status = new_status::job_status,
        progress = COALESCE(update_job_status.progress, progress),
        result = COALESCE(update_job_status.result, result),
        error_message = update_job_status.error_message,
        started_at = CASE WHEN new_status = 'running' AND started_at IS NULL THEN NOW() ELSE started_at END,
        completed_at = CASE WHEN new_status IN ('completed', 'failed', 'cancelled') THEN NOW() ELSE completed_at END,
        updated_at = NOW()
    WHERE id = update_job_status.job_id
    AND (tenant_id = get_current_tenant_id() OR is_admin());
    
    -- If job completed successfully, check for dependent jobs to release
    IF new_status = 'completed' AND FOUND THEN
        UPDATE jobs 
        SET status = 'queued'
        WHERE id IN (
            SELECT jd.job_id 
            FROM job_dependencies jd
            WHERE jd.depends_on_job_id = update_job_status.job_id
            AND check_job_dependencies(jd.job_id) = true
        );
    END IF;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- DATA QUALITY FUNCTIONS
-- ===================================

-- Function to run data quality checks on an entity
CREATE OR REPLACE FUNCTION run_data_quality_checks(
    entity_type TEXT,
    entity_id UUID
) RETURNS TABLE(
    rule_name TEXT,
    passed BOOLEAN,
    severity TEXT,
    details JSONB
) AS $$
DECLARE
    rule_record RECORD;
    field_value TEXT;
    check_result BOOLEAN;
    check_details JSONB;
BEGIN
    FOR rule_record IN 
        SELECT * FROM data_quality_rules 
        WHERE entity_type = run_data_quality_checks.entity_type 
        AND is_active = true
        ORDER BY severity DESC
    LOOP
        -- Get field value
        EXECUTE format(
            'SELECT %I::TEXT FROM %I WHERE id = $1 AND (tenant_id = $2 OR $3)',
            rule_record.field_name,
            entity_type
        ) INTO field_value 
        USING entity_id, get_current_tenant_id(), is_admin();
        
        check_result := false;
        check_details := '{}'::JSONB;
        
        -- Apply rule
        CASE rule_record.rule_type
            WHEN 'required' THEN
                check_result := (field_value IS NOT NULL AND field_value != '');
                check_details := jsonb_build_object(
                    'field_value', field_value,
                    'expected', 'non-empty value'
                );
                
            WHEN 'format' THEN
                check_result := (field_value ~ rule_record.rule_expression);
                check_details := jsonb_build_object(
                    'field_value', field_value,
                    'pattern', rule_record.rule_expression,
                    'matches', check_result
                );
                
            WHEN 'range' THEN
                BEGIN
                    DECLARE
                        num_value DECIMAL := field_value::DECIMAL;
                        range_config JSONB := rule_record.rule_expression::JSONB;
                    BEGIN
                        check_result := (
                            num_value >= COALESCE((range_config->>'min')::DECIMAL, num_value) AND
                            num_value <= COALESCE((range_config->>'max')::DECIMAL, num_value)
                        );
                        check_details := jsonb_build_object(
                            'field_value', num_value,
                            'min_allowed', range_config->>'min',
                            'max_allowed', range_config->>'max'
                        );
                    END;
                EXCEPTION WHEN OTHERS THEN
                    check_result := false;
                    check_details := jsonb_build_object('error', 'Invalid numeric value');
                END;
                
            WHEN 'custom' THEN
                -- Execute custom SQL expression
                BEGIN
                    EXECUTE format(
                        'SELECT (%s) FROM %I WHERE id = $1',
                        rule_record.rule_expression,
                        entity_type
                    ) INTO check_result USING entity_id;
                    
                    check_details := jsonb_build_object(
                        'custom_expression', rule_record.rule_expression,
                        'result', check_result
                    );
                EXCEPTION WHEN OTHERS THEN
                    check_result := false;
                    check_details := jsonb_build_object('error', SQLERRM);
                END;
        END CASE;
        
        -- Store result
        INSERT INTO data_quality_metrics (
            entity_type, entity_id, rule_id, metric_name, metric_value,
            is_passing, severity, details, measured_at
        ) VALUES (
            entity_type, entity_id, rule_record.id, rule_record.name,
            CASE WHEN check_result THEN 100 ELSE 0 END,
            check_result, rule_record.severity, check_details, NOW()
        ) ON CONFLICT (entity_type, entity_id, rule_id, metric_name) 
        DO UPDATE SET 
            metric_value = EXCLUDED.metric_value,
            is_passing = EXCLUDED.is_passing,
            details = EXCLUDED.details,
            measured_at = EXCLUDED.measured_at;
        
        RETURN QUERY SELECT 
            rule_record.name,
            check_result,
            rule_record.severity,
            check_details;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get data quality summary for an entity
CREATE OR REPLACE FUNCTION get_data_quality_summary(
    entity_type TEXT,
    entity_id UUID
) RETURNS TABLE(
    overall_score DECIMAL(5,2),
    total_rules INTEGER,
    passed_rules INTEGER,
    failed_rules INTEGER,
    critical_issues INTEGER,
    warnings INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ROUND(AVG(CASE WHEN is_passing THEN 100 ELSE 0 END), 2) as overall_score,
        COUNT(*)::INTEGER as total_rules,
        COUNT(CASE WHEN is_passing THEN 1 END)::INTEGER as passed_rules,
        COUNT(CASE WHEN NOT is_passing THEN 1 END)::INTEGER as failed_rules,
        COUNT(CASE WHEN NOT is_passing AND severity = 'critical' THEN 1 END)::INTEGER as critical_issues,
        COUNT(CASE WHEN NOT is_passing AND severity = 'warning' THEN 1 END)::INTEGER as warnings
    FROM data_quality_metrics dqm
    WHERE dqm.entity_type = get_data_quality_summary.entity_type
    AND dqm.entity_id = get_data_quality_summary.entity_id
    AND dqm.measured_at >= NOW() - INTERVAL '24 hours';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- SEARCH AND MATCHING FUNCTIONS
-- ===================================

-- Function for fuzzy person search
CREATE OR REPLACE FUNCTION search_persons(
    search_term TEXT,
    similarity_threshold DECIMAL DEFAULT 0.3
) RETURNS TABLE(
    person_id UUID,
    full_name TEXT,
    email TEXT,
    company_name TEXT,
    similarity_score DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.full_name,
        p.email,
        c.name as company_name,
        GREATEST(
            similarity(p.full_name, search_term),
            similarity(COALESCE(p.email, ''), search_term),
            similarity(COALESCE(c.name, ''), search_term)
        ) as similarity_score
    FROM persons p
    LEFT JOIN companies c ON p.company_id = c.id
    WHERE (p.tenant_id = get_current_tenant_id() OR is_admin())
    AND p.deleted_at IS NULL
    AND (
        p.full_name ILIKE '%' || search_term || '%'
        OR p.email ILIKE '%' || search_term || '%'
        OR c.name ILIKE '%' || search_term || '%'
        OR similarity(p.full_name, search_term) > similarity_threshold
        OR similarity(COALESCE(p.email, ''), search_term) > similarity_threshold
    )
    ORDER BY similarity_score DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function for duplicate detection
CREATE OR REPLACE FUNCTION find_potential_duplicates(
    entity_type TEXT,
    entity_id UUID DEFAULT NULL
) RETURNS TABLE(
    id1 UUID,
    id2 UUID,
    similarity_score DECIMAL,
    matching_fields TEXT[],
    confidence_level TEXT
) AS $$
BEGIN
    CASE entity_type
        WHEN 'persons' THEN
            RETURN QUERY
            SELECT 
                p1.id,
                p2.id,
                GREATEST(
                    similarity(p1.full_name, p2.full_name),
                    similarity(COALESCE(p1.email, ''), COALESCE(p2.email, '')),
                    similarity(COALESCE(p1.phone, ''), COALESCE(p2.phone, ''))
                ) as similarity_score,
                ARRAY_REMOVE(ARRAY[
                    CASE WHEN similarity(p1.full_name, p2.full_name) > 0.8 THEN 'name' END,
                    CASE WHEN similarity(COALESCE(p1.email, ''), COALESCE(p2.email, '')) > 0.9 THEN 'email' END,
                    CASE WHEN similarity(COALESCE(p1.phone, ''), COALESCE(p2.phone, '')) > 0.9 THEN 'phone' END,
                    CASE WHEN p1.personal_number_hash = p2.personal_number_hash AND p1.personal_number_hash IS NOT NULL THEN 'personal_number' END
                ], NULL) as matching_fields,
                CASE 
                    WHEN p1.personal_number_hash = p2.personal_number_hash AND p1.personal_number_hash IS NOT NULL THEN 'high'
                    WHEN similarity(COALESCE(p1.email, ''), COALESCE(p2.email, '')) > 0.95 THEN 'high'
                    WHEN similarity(p1.full_name, p2.full_name) > 0.9 THEN 'medium'
                    ELSE 'low'
                END as confidence_level
            FROM persons p1
            CROSS JOIN persons p2
            WHERE p1.id < p2.id  -- Avoid duplicate pairs
            AND (p1.tenant_id = get_current_tenant_id() OR is_admin())
            AND (p2.tenant_id = get_current_tenant_id() OR is_admin())
            AND p1.deleted_at IS NULL AND p2.deleted_at IS NULL
            AND (entity_id IS NULL OR p1.id = entity_id OR p2.id = entity_id)
            AND (
                similarity(p1.full_name, p2.full_name) > 0.7
                OR similarity(COALESCE(p1.email, ''), COALESCE(p2.email, '')) > 0.8
                OR similarity(COALESCE(p1.phone, ''), COALESCE(p2.phone, '')) > 0.8
                OR (p1.personal_number_hash = p2.personal_number_hash AND p1.personal_number_hash IS NOT NULL)
            )
            ORDER BY similarity_score DESC
            LIMIT 100;
            
        -- Add similar logic for companies and vehicles
        ELSE
            RAISE EXCEPTION 'Unsupported entity type: %', entity_type;
    END CASE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- ANALYTICS AND REPORTING FUNCTIONS
-- ===================================

-- Function for tenant analytics
CREATE OR REPLACE FUNCTION get_tenant_analytics(
    tenant_id UUID DEFAULT NULL,
    days INTEGER DEFAULT 30
) RETURNS TABLE(
    metric_name TEXT,
    metric_value BIGINT,
    change_percent DECIMAL
) AS $$
DECLARE
    target_tenant_id UUID;
    start_date TIMESTAMP;
    mid_date TIMESTAMP;
BEGIN
    target_tenant_id := COALESCE(tenant_id, get_current_tenant_id());
    start_date := NOW() - INTERVAL '1 day' * days;
    mid_date := NOW() - INTERVAL '1 day' * (days / 2);
    
    -- Total records
    RETURN QUERY
    SELECT 
        'total_persons'::TEXT,
        COUNT(*)::BIGINT,
        CASE WHEN COUNT(*) > 0 THEN
            (COUNT(CASE WHEN created_at >= mid_date THEN 1 END)::DECIMAL / 
             NULLIF(COUNT(CASE WHEN created_at < mid_date THEN 1 END), 0) - 1) * 100
        ELSE 0 END
    FROM persons 
    WHERE tenant_id = target_tenant_id 
    AND deleted_at IS NULL 
    AND created_at >= start_date;
    
    RETURN QUERY
    SELECT 
        'total_companies'::TEXT,
        COUNT(*)::BIGINT,
        CASE WHEN COUNT(*) > 0 THEN
            (COUNT(CASE WHEN created_at >= mid_date THEN 1 END)::DECIMAL / 
             NULLIF(COUNT(CASE WHEN created_at < mid_date THEN 1 END), 0) - 1) * 100
        ELSE 0 END
    FROM companies 
    WHERE tenant_id = target_tenant_id 
    AND deleted_at IS NULL 
    AND created_at >= start_date;
    
    RETURN QUERY
    SELECT 
        'total_vehicles'::TEXT,
        COUNT(*)::BIGINT,
        CASE WHEN COUNT(*) > 0 THEN
            (COUNT(CASE WHEN created_at >= mid_date THEN 1 END)::DECIMAL / 
             NULLIF(COUNT(CASE WHEN created_at < mid_date THEN 1 END), 0) - 1) * 100
        ELSE 0 END
    FROM vehicles 
    WHERE tenant_id = target_tenant_id 
    AND deleted_at IS NULL 
    AND created_at >= start_date;
    
    -- Job statistics
    RETURN QUERY
    SELECT 
        'jobs_completed'::TEXT,
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::BIGINT,
        0::DECIMAL
    FROM jobs 
    WHERE tenant_id = target_tenant_id 
    AND created_at >= start_date;
    
    RETURN QUERY
    SELECT 
        'jobs_failed'::TEXT,
        COUNT(CASE WHEN status = 'failed' THEN 1 END)::BIGINT,
        0::DECIMAL
    FROM jobs 
    WHERE tenant_id = target_tenant_id 
    AND created_at >= start_date;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- MAINTENANCE AND CLEANUP FUNCTIONS
-- ===================================

-- Function to clean up old data based on retention policies
CREATE OR REPLACE FUNCTION apply_retention_policies()
RETURNS TABLE(
    policy_name TEXT,
    entity_type TEXT,
    affected_records INTEGER,
    action_taken TEXT
) AS $$
DECLARE
    policy_record RECORD;
    affected_count INTEGER;
BEGIN
    FOR policy_record IN 
        SELECT * FROM data_retention_policies WHERE is_active = true
    LOOP
        affected_count := 0;
        
        CASE policy_record.action_type
            WHEN 'delete' THEN
                CASE policy_record.entity_type
                    WHEN 'persons' THEN
                        WITH deleted_persons AS (
                            DELETE FROM persons 
                            WHERE created_at < (NOW() - INTERVAL '1 day' * policy_record.retention_days)
                            AND deleted_at IS NOT NULL  -- Only hard delete already soft deleted
                            RETURNING id
                        )
                        SELECT COUNT(*) INTO affected_count FROM deleted_persons;
                        
                    WHEN 'audit_logs' THEN
                        WITH deleted_logs AS (
                            DELETE FROM audit_logs 
                            WHERE changed_at < (NOW() - INTERVAL '1 day' * policy_record.retention_days)
                            RETURNING id
                        )
                        SELECT COUNT(*) INTO affected_count FROM deleted_logs;
                END CASE;
                
            WHEN 'anonymize' THEN
                CASE policy_record.entity_type
                    WHEN 'persons' THEN
                        WITH anonymized_persons AS (
                            SELECT anonymize_person_data(id) as success
                            FROM persons 
                            WHERE created_at < (NOW() - INTERVAL '1 day' * policy_record.retention_days)
                            AND deleted_at IS NULL
                            AND NOT (metadata->>'anonymized')::BOOLEAN
                        )
                        SELECT COUNT(CASE WHEN success THEN 1 END) INTO affected_count FROM anonymized_persons;
                END CASE;
        END CASE;
        
        -- Update last executed timestamp
        UPDATE data_retention_policies 
        SET last_executed_at = NOW() 
        WHERE id = policy_record.id;
        
        RETURN QUERY SELECT 
            policy_record.name,
            policy_record.entity_type,
            affected_count,
            policy_record.action_type;
    END LOOP;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to cleanup orphaned records
CREATE OR REPLACE FUNCTION cleanup_orphaned_records()
RETURNS TABLE(
    table_name TEXT,
    orphaned_count INTEGER
) AS $$
DECLARE
    cleanup_count INTEGER;
BEGIN
    -- Clean up vehicles without owners
    WITH cleaned_vehicles AS (
        UPDATE vehicles 
        SET owner_id = NULL 
        WHERE owner_id IS NOT NULL 
        AND NOT EXISTS (
            SELECT 1 FROM persons 
            WHERE persons.id = vehicles.owner_id
        )
        RETURNING id
    )
    SELECT COUNT(*) INTO cleanup_count FROM cleaned_vehicles;
    
    RETURN QUERY SELECT 'vehicles'::TEXT, cleanup_count;
    
    -- Clean up persons without valid company references
    WITH cleaned_persons AS (
        UPDATE persons 
        SET company_id = NULL 
        WHERE company_id IS NOT NULL 
        AND NOT EXISTS (
            SELECT 1 FROM companies 
            WHERE companies.id = persons.company_id
        )
        RETURNING id
    )
    SELECT COUNT(*) INTO cleanup_count FROM cleaned_persons;
    
    RETURN QUERY SELECT 'persons'::TEXT, cleanup_count;
    
    -- Clean up job dependencies for non-existent jobs
    WITH cleaned_deps AS (
        DELETE FROM job_dependencies 
        WHERE NOT EXISTS (
            SELECT 1 FROM jobs WHERE jobs.id = job_dependencies.job_id
        )
        OR NOT EXISTS (
            SELECT 1 FROM jobs WHERE jobs.id = job_dependencies.depends_on_job_id
        )
        RETURNING id
    )
    SELECT COUNT(*) INTO cleanup_count FROM cleaned_deps;
    
    RETURN QUERY SELECT 'job_dependencies'::TEXT, cleanup_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ===================================
-- GRANT PERMISSIONS
-- ===================================

-- Grant execute permissions on business logic functions
GRANT EXECUTE ON FUNCTION get_company_employee_count(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_person_vehicle_count(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_template_success_rate(UUID, INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION get_next_proxy(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION record_proxy_usage(UUID, UUID, TEXT, BOOLEAN, INTEGER, INTEGER, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION reserve_proxy(UUID) TO authenticated;

GRANT EXECUTE ON FUNCTION check_job_dependencies(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION queue_job_with_dependencies(TEXT, TEXT, JSONB, TEXT, UUID[]) TO authenticated;
GRANT EXECUTE ON FUNCTION get_next_ready_job(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION update_job_status(UUID, TEXT, INTEGER, JSONB, TEXT) TO authenticated;

GRANT EXECUTE ON FUNCTION run_data_quality_checks(TEXT, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_data_quality_summary(TEXT, UUID) TO authenticated;

GRANT EXECUTE ON FUNCTION search_persons(TEXT, DECIMAL) TO authenticated;
GRANT EXECUTE ON FUNCTION find_potential_duplicates(TEXT, UUID) TO authenticated;

GRANT EXECUTE ON FUNCTION get_tenant_analytics(UUID, INTEGER) TO authenticated;

-- Admin-only functions
GRANT EXECUTE ON FUNCTION apply_retention_policies() TO ecadp_admin;
GRANT EXECUTE ON FUNCTION cleanup_orphaned_records() TO ecadp_admin;

-- Migration complete
SELECT 'ECaDP Business Logic Migration 004 completed successfully' as result;
