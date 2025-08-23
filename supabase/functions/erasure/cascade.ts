import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

interface CascadeErasureConfig {
  user_id: string;
  request_id: string;
  erasure_type: 'anonymize' | 'delete' | 'tombstone';
  dry_run?: boolean;
}

interface CascadeResult {
  tables_processed: string[];
  total_records_affected: number;
  cascade_order: string[];
  errors: string[];
  execution_time_ms: number;
}

/**
 * Performs cascade deletion/anonymization across related tables
 * Ensures referential integrity and proper order of operations
 */
export async function cascade(config: CascadeErasureConfig): Promise<CascadeResult> {
  const startTime = Date.now();
  console.log(`Starting cascade erasure for user ${config.user_id}, type: ${config.erasure_type}`);
  
  const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
  const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
  const supabase = createClient(supabaseUrl, supabaseServiceKey);
  
  const result: CascadeResult = {
    tables_processed: [],
    total_records_affected: 0,
    cascade_order: [],
    errors: [],
    execution_time_ms: 0
  };

  // Define cascade order (leaf tables first, then parent tables)
  const cascadeOrder = [
    // Leaf tables (no dependencies)
    'audit_log_entries',
    'notification_history', 
    'dq_alert_events',
    'export_file_chunks',
    'crawl_result_attachments',
    
    // Level 2 tables (depend on leaf tables)
    'dq_metrics',
    'selector_drift_history',
    'crawl_results',
    'export_files',
    'job_executions',
    'privacy_requests',
    
    // Level 3 tables (depend on level 2)
    'export_requests',
    'jobs',
    'webhook_deliveries',
    'template_versions',
    
    // Level 4 tables (depend on level 3)
    'templates',
    'projects',
    'domain_policies',
    
    // Root tables (parent tables)
    'user_sessions',
    'user_preferences',
    'user_api_keys'
  ];

  result.cascade_order = cascadeOrder;

  try {
    // Process each table in cascade order
    for (const tableName of cascadeOrder) {
      try {
        const recordsAffected = await processTableCascade(
          supabase, 
          tableName, 
          config
        );
        
        if (recordsAffected > 0) {
          result.tables_processed.push(tableName);
          result.total_records_affected += recordsAffected;
          
          // Log cascade operation
          if (!config.dry_run) {
            await logCascadeOperation(supabase, {
              request_id: config.request_id,
              table_name: tableName,
              records_affected: recordsAffected,
              user_id: config.user_id,
              erasure_type: config.erasure_type
            });
          }
        }
        
      } catch (error) {
        const errorMsg = `Failed to process table ${tableName}: ${error.message}`;
        console.error(errorMsg);
        result.errors.push(errorMsg);
      }
    }

    // Verify cascade completion
    if (!config.dry_run) {
      await verifyCascadeCompletion(supabase, config.user_id, result);
    }

    result.execution_time_ms = Date.now() - startTime;
    console.log(`Cascade erasure completed in ${result.execution_time_ms}ms`);
    
    return result;

  } catch (error) {
    result.errors.push(`Cascade operation failed: ${error.message}`);
    result.execution_time_ms = Date.now() - startTime;
    throw error;
  }
}

async function processTableCascade(
  supabase: any, 
  tableName: string, 
  config: CascadeErasureConfig
): Promise<number> {
  
  // Check if table has user_id column
  const hasUserId = await checkTableHasColumn(supabase, tableName, 'user_id');
  if (!hasUserId) {
    console.log(`Skipping table ${tableName} - no user_id column`);
    return 0;
  }

  switch (config.erasure_type) {
    case 'delete':
      return await hardDeleteRecords(supabase, tableName, config);
    
    case 'anonymize': 
      return await anonymizeRecords(supabase, tableName, config);
    
    case 'tombstone':
      return await tombstoneRecords(supabase, tableName, config);
    
    default:
      throw new Error(`Unknown erasure type: ${config.erasure_type}`);
  }
}

async function hardDeleteRecords(
  supabase: any, 
  tableName: string, 
  config: CascadeErasureConfig
): Promise<number> {
  
  if (config.dry_run) {
    const { count } = await supabase
      .from(tableName)
      .select('*', { count: 'exact', head: true })
      .eq('user_id', config.user_id);
    
    return count || 0;
  }

  const { count, error } = await supabase
    .from(tableName)
    .delete({ count: 'exact' })
    .eq('user_id', config.user_id);

  if (error) throw error;
  return count || 0;
}

async function anonymizeRecords(
  supabase: any, 
  tableName: string, 
  config: CascadeErasureConfig
): Promise<number> {
  
  const anonymizationMap = getTableAnonymizationMap(tableName);
  
  if (config.dry_run) {
    const { count } = await supabase
      .from(tableName)
      .select('*', { count: 'exact', head: true })
      .eq('user_id', config.user_id);
    
    return count || 0;
  }

  const { count, error } = await supabase
    .from(tableName)
    .update(anonymizationMap, { count: 'exact' })
    .eq('user_id', config.user_id);

  if (error) throw error;
  return count || 0;
}

async function tombstoneRecords(
  supabase: any, 
  tableName: string, 
  config: CascadeErasureConfig
): Promise<number> {
  
  const tombstoneData = {
    is_deleted: true,
    deleted_at: new Date().toISOString(),
    deleted_by: 'cascade_erasure',
    deletion_request_id: config.request_id
  };

  if (config.dry_run) {
    const { count } = await supabase
      .from(tableName)
      .select('*', { count: 'exact', head: true })
      .eq('user_id', config.user_id);
    
    return count || 0;
  }

  const { count, error } = await supabase
    .from(tableName)
    .update(tombstoneData, { count: 'exact' })
    .eq('user_id', config.user_id);

  if (error) throw error;
  return count || 0;
}

async function checkTableHasColumn(
  supabase: any, 
  tableName: string, 
  columnName: string
): Promise<boolean> {
  try {
    // Try a simple query to check if column exists
    await supabase
      .from(tableName)
      .select(columnName)
      .limit(1);
    
    return true;
  } catch {
    return false;
  }
}

function getTableAnonymizationMap(tableName: string): Record<string, any> {
  const baseAnonymization = {
    updated_at: new Date().toISOString(),
    anonymized_at: new Date().toISOString()
  };

  // Table-specific anonymization rules
  const tableSpecificMaps: Record<string, Record<string, any>> = {
    crawl_results: {
      ...baseAnonymization,
      payload: { anonymized: true, pii_removed: new Date().toISOString() },
      url: 'https://anonymized.domain.com/path'
    },
    
    templates: {
      ...baseAnonymization,
      name: 'Anonymized Template',
      description: 'Template anonymized per user request',
      selectors: { anonymized: true }
    },
    
    jobs: {
      ...baseAnonymization,
      name: 'Anonymized Job',
      config: { anonymized: true }
    },
    
    user_preferences: {
      ...baseAnonymization,
      email_notifications: false,
      data_export_settings: { anonymized: true }
    }
  };

  return tableSpecificMaps[tableName] || baseAnonymization;
}

async function logCascadeOperation(supabase: any, operation: {
  request_id: string;
  table_name: string;
  records_affected: number;
  user_id: string;
  erasure_type: string;
}) {
  await supabase
    .from('cascade_erasure_log')
    .insert({
      ...operation,
      completed_at: new Date().toISOString()
    });
}

async function verifyCascadeCompletion(
  supabase: any, 
  userId: string, 
  result: CascadeResult
) {
  // Verify no records remain for this user in processed tables
  for (const tableName of result.tables_processed) {
    try {
      const { count } = await supabase
        .from(tableName)
        .select('*', { count: 'exact', head: true })
        .eq('user_id', userId);

      if (count && count > 0) {
        result.errors.push(`Verification failed: ${count} records remain in ${tableName}`);
      }
    } catch (error) {
      result.errors.push(`Verification error for ${tableName}: ${error.message}`);
    }
  }
}