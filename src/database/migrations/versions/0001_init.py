"""
Database Migration - Initial Schema
===================================

Creates the initial database schema for the ECaDP platform including:
- User management tables
- Proxy pool management
- Job management and scheduling
- Template and extraction data
- Audit and logging tables
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Create initial schema"""
    
    # Enable required extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "btree_gin"')
    
    # Create enum types
    op.execute("""
        CREATE TYPE user_role AS ENUM ('admin', 'user', 'viewer');
        CREATE TYPE job_status AS ENUM ('pending', 'running', 'completed', 'failed', 'cancelled');
        CREATE TYPE proxy_status AS ENUM ('active', 'testing', 'failed', 'disabled');
        CREATE TYPE extraction_status AS ENUM ('pending', 'processing', 'completed', 'failed');
    """)
    
    # Users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', postgresql.ENUM('admin', 'user', 'viewer', name='user_role'), nullable=False, default='user'),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean, nullable=False, default=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # API Keys table
    op.create_table('api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False, unique=True),
        sa.Column('prefix', sa.String(20), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('permissions', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Proxy Pool table
    op.create_table('proxies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('host', sa.String(255), nullable=False),
        sa.Column('port', sa.Integer, nullable=False),
        sa.Column('protocol', sa.String(10), nullable=False, default='http'),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('password', sa.String(255), nullable=True),
        sa.Column('status', postgresql.ENUM('active', 'testing', 'failed', 'disabled', name='proxy_status'), nullable=False, default='testing'),
        sa.Column('quality_score', sa.Float, nullable=False, default=0.0),
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.Column('success_count', sa.Integer, nullable=False, default=0),
        sa.Column('failure_count', sa.Integer, nullable=False, default=0),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('country_code', sa.String(2), nullable=True),
        sa.Column('provider', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('host', 'port', 'protocol', name='unique_proxy_endpoint')
    )
    
    # Templates table
    op.create_table('templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('version', sa.String(20), nullable=False, default='1.0.0'),
        sa.Column('template_data', postgresql.JSONB, nullable=False),
        sa.Column('url_patterns', postgresql.ARRAY(sa.String), nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('is_public', sa.Boolean, nullable=False, default=False),
        sa.Column('usage_count', sa.Integer, nullable=False, default=0),
        sa.Column('success_rate', sa.Float, nullable=False, default=0.0),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Jobs table
    op.create_table('jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=False),  # crawl, scrape, backup, etc.
        sa.Column('status', postgresql.ENUM('pending', 'running', 'completed', 'failed', 'cancelled', name='job_status'), nullable=False, default='pending'),
        sa.Column('priority', sa.Integer, nullable=False, default=5),
        sa.Column('config', postgresql.JSONB, nullable=False),
        sa.Column('result', postgresql.JSONB, nullable=True),
        sa.Column('progress', sa.Float, nullable=False, default=0.0),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer, nullable=False, default=0),
        sa.Column('max_retries', sa.Integer, nullable=False, default=3),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Extractions table
    op.create_table('extractions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('templates.id', ondelete='SET NULL'), nullable=True),
        sa.Column('url', sa.Text, nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'processing', 'completed', 'failed', name='extraction_status'), nullable=False, default='pending'),
        sa.Column('extracted_data', postgresql.JSONB, nullable=True),
        sa.Column('raw_html', sa.Text, nullable=True),
        sa.Column('response_code', sa.Integer, nullable=True),
        sa.Column('response_time_ms', sa.Integer, nullable=True),
        sa.Column('proxy_used', sa.String(255), nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('extraction_time_ms', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Webhooks table
    op.create_table('webhooks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('url', sa.Text, nullable=False),
        sa.Column('secret', sa.String(255), nullable=True),
        sa.Column('events', postgresql.ARRAY(sa.String), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, default=True),
        sa.Column('success_count', sa.Integer, nullable=False, default=0),
        sa.Column('failure_count', sa.Integer, nullable=False, default=0),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_failure_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Webhook Deliveries table
    op.create_table('webhook_deliveries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('webhook_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('webhooks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('payload', postgresql.JSONB, nullable=False),
        sa.Column('response_code', sa.Integer, nullable=True),
        sa.Column('response_body', sa.Text, nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer, nullable=False, default=0),
        sa.Column('next_retry_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Audit Log table
    op.create_table('audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('changes', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # System Settings table
    op.create_table('system_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('key', sa.String(100), nullable=False, unique=True),
        sa.Column('value', postgresql.JSONB, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_encrypted', sa.Boolean, nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )

def downgrade():
    """Drop all tables and types"""
    
    # Drop tables in reverse order
    op.drop_table('system_settings')
    op.drop_table('audit_logs')
    op.drop_table('webhook_deliveries')
    op.drop_table('webhooks')
    op.drop_table('extractions')
    op.drop_table('jobs')
    op.drop_table('templates')
    op.drop_table('proxies')
    op.drop_table('api_keys')
    op.drop_table('users')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS extraction_status')
    op.execute('DROP TYPE IF EXISTS proxy_status')
    op.execute('DROP TYPE IF EXISTS job_status')
    op.execute('DROP TYPE IF EXISTS user_role')
