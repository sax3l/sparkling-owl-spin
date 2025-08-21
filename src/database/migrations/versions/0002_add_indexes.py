"""
Database Migration - Indexes and Performance
============================================

Creates indexes and performance optimizations for the ECaDP platform:
- Primary and foreign key indexes
- Search and filtering indexes
- Performance optimization indexes
- Partial indexes for specific use cases
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '0002_add_indexes'
down_revision = '0001_init'
branch_labels = None
depends_on = None

def upgrade():
    """Create indexes for performance optimization"""
    
    # Users table indexes
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])
    op.create_index('ix_users_created_at', 'users', ['created_at'])
    op.create_index('ix_users_last_login_at', 'users', ['last_login_at'])
    
    # API Keys table indexes
    op.create_index('ix_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('ix_api_keys_key_hash', 'api_keys', ['key_hash'])
    op.create_index('ix_api_keys_prefix', 'api_keys', ['prefix'])
    op.create_index('ix_api_keys_is_active', 'api_keys', ['is_active'])
    op.create_index('ix_api_keys_expires_at', 'api_keys', ['expires_at'])
    op.create_index('ix_api_keys_last_used_at', 'api_keys', ['last_used_at'])
    
    # Partial index for active API keys
    op.create_index('ix_api_keys_active_user', 'api_keys', ['user_id'], 
                   postgresql_where=sa.text('is_active = true'))
    
    # Proxies table indexes
    op.create_index('ix_proxies_host_port', 'proxies', ['host', 'port'])
    op.create_index('ix_proxies_status', 'proxies', ['status'])
    op.create_index('ix_proxies_quality_score', 'proxies', ['quality_score'])
    op.create_index('ix_proxies_response_time_ms', 'proxies', ['response_time_ms'])
    op.create_index('ix_proxies_last_used_at', 'proxies', ['last_used_at'])
    op.create_index('ix_proxies_last_success_at', 'proxies', ['last_success_at'])
    op.create_index('ix_proxies_country_code', 'proxies', ['country_code'])
    op.create_index('ix_proxies_provider', 'proxies', ['provider'])
    op.create_index('ix_proxies_created_at', 'proxies', ['created_at'])
    
    # Partial indexes for active and high-quality proxies
    op.create_index('ix_proxies_active_quality', 'proxies', ['quality_score'], 
                   postgresql_where=sa.text('status = \'active\''))
    op.create_index('ix_proxies_high_quality', 'proxies', ['last_used_at'], 
                   postgresql_where=sa.text('quality_score > 0.7 AND status = \'active\''))
    
    # Composite index for proxy selection
    op.create_index('ix_proxies_selection', 'proxies', 
                   ['status', 'quality_score', 'last_used_at'])
    
    # Templates table indexes
    op.create_index('ix_templates_user_id', 'templates', ['user_id'])
    op.create_index('ix_templates_name', 'templates', ['name'])
    op.create_index('ix_templates_version', 'templates', ['version'])
    op.create_index('ix_templates_is_active', 'templates', ['is_active'])
    op.create_index('ix_templates_is_public', 'templates', ['is_public'])
    op.create_index('ix_templates_usage_count', 'templates', ['usage_count'])
    op.create_index('ix_templates_success_rate', 'templates', ['success_rate'])
    op.create_index('ix_templates_last_used_at', 'templates', ['last_used_at'])
    op.create_index('ix_templates_created_at', 'templates', ['created_at'])
    
    # GIN index for URL patterns array search
    op.create_index('ix_templates_url_patterns_gin', 'templates', ['url_patterns'], 
                   postgresql_using='gin')
    
    # GIN index for template data JSONB search
    op.create_index('ix_templates_template_data_gin', 'templates', ['template_data'], 
                   postgresql_using='gin')
    
    # Partial index for active public templates
    op.create_index('ix_templates_active_public', 'templates', ['success_rate'], 
                   postgresql_where=sa.text('is_active = true AND is_public = true'))
    
    # Jobs table indexes
    op.create_index('ix_jobs_user_id', 'jobs', ['user_id'])
    op.create_index('ix_jobs_job_type', 'jobs', ['job_type'])
    op.create_index('ix_jobs_status', 'jobs', ['status'])
    op.create_index('ix_jobs_priority', 'jobs', ['priority'])
    op.create_index('ix_jobs_started_at', 'jobs', ['started_at'])
    op.create_index('ix_jobs_completed_at', 'jobs', ['completed_at'])
    op.create_index('ix_jobs_scheduled_at', 'jobs', ['scheduled_at'])
    op.create_index('ix_jobs_created_at', 'jobs', ['created_at'])
    op.create_index('ix_jobs_retry_count', 'jobs', ['retry_count'])
    
    # Composite indexes for job management
    op.create_index('ix_jobs_status_priority', 'jobs', ['status', 'priority'])
    op.create_index('ix_jobs_user_status', 'jobs', ['user_id', 'status'])
    op.create_index('ix_jobs_type_status', 'jobs', ['job_type', 'status'])
    
    # Partial indexes for pending and running jobs
    op.create_index('ix_jobs_pending_priority', 'jobs', ['priority'], 
                   postgresql_where=sa.text('status = \'pending\''))
    op.create_index('ix_jobs_running_started', 'jobs', ['started_at'], 
                   postgresql_where=sa.text('status = \'running\''))
    
    # GIN index for job config JSONB
    op.create_index('ix_jobs_config_gin', 'jobs', ['config'], 
                   postgresql_using='gin')
    
    # Extractions table indexes
    op.create_index('ix_extractions_job_id', 'extractions', ['job_id'])
    op.create_index('ix_extractions_template_id', 'extractions', ['template_id'])
    op.create_index('ix_extractions_status', 'extractions', ['status'])
    op.create_index('ix_extractions_response_code', 'extractions', ['response_code'])
    op.create_index('ix_extractions_response_time_ms', 'extractions', ['response_time_ms'])
    op.create_index('ix_extractions_extraction_time_ms', 'extractions', ['extraction_time_ms'])
    op.create_index('ix_extractions_created_at', 'extractions', ['created_at'])
    
    # URL indexing for extractions (using hash for long URLs)
    op.execute('CREATE INDEX ix_extractions_url_hash ON extractions USING hash (url)')
    
    # Text search index for URLs using trigrams
    op.create_index('ix_extractions_url_trgm', 'extractions', ['url'], 
                   postgresql_using='gin', postgresql_ops={'url': 'gin_trgm_ops'})
    
    # GIN index for extracted data JSONB
    op.create_index('ix_extractions_data_gin', 'extractions', ['extracted_data'], 
                   postgresql_using='gin')
    
    # Composite indexes for extraction analysis
    op.create_index('ix_extractions_job_status', 'extractions', ['job_id', 'status'])
    op.create_index('ix_extractions_template_status', 'extractions', ['template_id', 'status'])
    
    # Webhooks table indexes
    op.create_index('ix_webhooks_user_id', 'webhooks', ['user_id'])
    op.create_index('ix_webhooks_is_active', 'webhooks', ['is_active'])
    op.create_index('ix_webhooks_last_success_at', 'webhooks', ['last_success_at'])
    op.create_index('ix_webhooks_last_failure_at', 'webhooks', ['last_failure_at'])
    op.create_index('ix_webhooks_created_at', 'webhooks', ['created_at'])
    
    # GIN index for events array
    op.create_index('ix_webhooks_events_gin', 'webhooks', ['events'], 
                   postgresql_using='gin')
    
    # Webhook Deliveries table indexes
    op.create_index('ix_webhook_deliveries_webhook_id', 'webhook_deliveries', ['webhook_id'])
    op.create_index('ix_webhook_deliveries_event_type', 'webhook_deliveries', ['event_type'])
    op.create_index('ix_webhook_deliveries_response_code', 'webhook_deliveries', ['response_code'])
    op.create_index('ix_webhook_deliveries_delivered_at', 'webhook_deliveries', ['delivered_at'])
    op.create_index('ix_webhook_deliveries_retry_count', 'webhook_deliveries', ['retry_count'])
    op.create_index('ix_webhook_deliveries_next_retry_at', 'webhook_deliveries', ['next_retry_at'])
    op.create_index('ix_webhook_deliveries_created_at', 'webhook_deliveries', ['created_at'])
    
    # Composite index for retry processing
    op.create_index('ix_webhook_deliveries_retry', 'webhook_deliveries', 
                   ['next_retry_at', 'retry_count'], 
                   postgresql_where=sa.text('delivered_at IS NULL'))
    
    # GIN index for payload JSONB
    op.create_index('ix_webhook_deliveries_payload_gin', 'webhook_deliveries', ['payload'], 
                   postgresql_using='gin')
    
    # Audit Logs table indexes
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_resource_type', 'audit_logs', ['resource_type'])
    op.create_index('ix_audit_logs_resource_id', 'audit_logs', ['resource_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    
    # Composite indexes for audit trail analysis
    op.create_index('ix_audit_logs_user_action', 'audit_logs', ['user_id', 'action'])
    op.create_index('ix_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('ix_audit_logs_user_time', 'audit_logs', ['user_id', 'created_at'])
    
    # GIN index for changes JSONB
    op.create_index('ix_audit_logs_changes_gin', 'audit_logs', ['changes'], 
                   postgresql_using='gin')
    
    # System Settings table indexes
    op.create_index('ix_system_settings_key', 'system_settings', ['key'])
    op.create_index('ix_system_settings_is_encrypted', 'system_settings', ['is_encrypted'])
    op.create_index('ix_system_settings_created_at', 'system_settings', ['created_at'])
    
    # GIN index for value JSONB
    op.create_index('ix_system_settings_value_gin', 'system_settings', ['value'], 
                   postgresql_using='gin')
    
    # Create function for updating updated_at timestamp
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Create triggers for updated_at columns
    tables_with_updated_at = [
        'users', 'api_keys', 'proxies', 'templates', 
        'jobs', 'extractions', 'webhooks', 'system_settings'
    ]
    
    for table in tables_with_updated_at:
        op.execute(f"""
            CREATE TRIGGER update_{table}_updated_at 
            BEFORE UPDATE ON {table} 
            FOR EACH ROW 
            EXECUTE FUNCTION update_updated_at_column();
        """)

def downgrade():
    """Drop indexes and triggers"""
    
    # Drop triggers
    tables_with_updated_at = [
        'users', 'api_keys', 'proxies', 'templates', 
        'jobs', 'extractions', 'webhooks', 'system_settings'
    ]
    
    for table in tables_with_updated_at:
        op.execute(f'DROP TRIGGER IF EXISTS update_{table}_updated_at ON {table}')
    
    # Drop function
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column()')
    
    # Drop indexes (SQLAlchemy will handle this automatically when dropping tables)
    # But we'll explicitly drop some custom indexes
    
    # Custom indexes that need explicit dropping
    op.drop_index('ix_extractions_url_hash')
    
    # Note: Most indexes will be dropped automatically when tables are dropped
    # This is just for indexes that might need special handling
