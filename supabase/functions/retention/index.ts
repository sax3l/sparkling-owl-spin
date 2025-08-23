import { serve } from "https://deno.land/std@0.190.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface RetentionPolicy {
  table_name: string;
  retention_days: number;
  date_column: string;
  conditions?: Record<string, any>;
}

interface RetentionRequest {
  policies?: RetentionPolicy[];
  dry_run?: boolean;
}

const DEFAULT_RETENTION_POLICIES: RetentionPolicy[] = [
  { table_name: 'crawl_results', retention_days: 90, date_column: 'created_at' },
  { table_name: 'scrape_results', retention_days: 365, date_column: 'created_at' },
  { table_name: 'exports', retention_days: 30, date_column: 'created_at' },
  { table_name: 'audit_logs', retention_days: 180, date_column: 'created_at' },
  { table_name: 'job_executions', retention_days: 60, date_column: 'created_at' },
  { table_name: 'error_logs', retention_days: 30, date_column: 'created_at' },
  { table_name: 'privacy_requests', retention_days: 1095, date_column: 'created_at' }, // 3 years for compliance
];

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
    )

    const requestBody: RetentionRequest = req.method === 'POST' 
      ? await req.json() 
      : {};

    const policies = requestBody.policies || DEFAULT_RETENTION_POLICIES;
    const dryRun = requestBody.dry_run ?? false;

    console.log(`Starting retention enforcement for ${policies.length} policies (dry run: ${dryRun})`);

    const results = [];

    for (const policy of policies) {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - policy.retention_days);
      const cutoffISOString = cutoffDate.toISOString();

      console.log(`Processing policy for ${policy.table_name}, retaining data newer than ${cutoffISOString}`);

      try {
        // Build query with conditions
        let query = supabaseClient
          .from(policy.table_name)
          .select('id', { count: 'exact', head: true })
          .lt(policy.date_column, cutoffISOString);

        // Apply additional conditions if specified
        if (policy.conditions) {
          for (const [key, value] of Object.entries(policy.conditions)) {
            query = query.eq(key, value);
          }
        }

        // Get count of records that would be deleted
        const countResult = await query;
        
        if (countResult.error) {
          console.error(`Error counting records for ${policy.table_name}:`, countResult.error);
          results.push({
            table_name: policy.table_name,
            status: 'error',
            error: countResult.error.message,
            records_affected: 0,
            dry_run: dryRun
          });
          continue;
        }

        const recordsToDelete = countResult.count || 0;

        if (recordsToDelete === 0) {
          console.log(`No records to delete for ${policy.table_name}`);
          results.push({
            table_name: policy.table_name,
            status: 'success',
            records_affected: 0,
            message: 'No records to delete',
            dry_run: dryRun
          });
          continue;
        }

        if (dryRun) {
          console.log(`DRY RUN: Would delete ${recordsToDelete} records from ${policy.table_name}`);
          results.push({
            table_name: policy.table_name,
            status: 'dry_run',
            records_affected: recordsToDelete,
            message: `Would delete ${recordsToDelete} records`,
            dry_run: true
          });
        } else {
          // Perform actual deletion in batches to avoid timeouts
          const batchSize = 1000;
          let totalDeleted = 0;

          while (totalDeleted < recordsToDelete) {
            let deleteQuery = supabaseClient
              .from(policy.table_name)
              .delete()
              .lt(policy.date_column, cutoffISOString)
              .limit(batchSize);

            // Apply additional conditions if specified
            if (policy.conditions) {
              for (const [key, value] of Object.entries(policy.conditions)) {
                deleteQuery = deleteQuery.eq(key, value);
              }
            }

            const deleteResult = await deleteQuery;

            if (deleteResult.error) {
              console.error(`Error deleting records from ${policy.table_name}:`, deleteResult.error);
              results.push({
                table_name: policy.table_name,
                status: 'error',
                error: deleteResult.error.message,
                records_affected: totalDeleted,
                dry_run: false
              });
              break;
            }

            // Estimate deleted records (Supabase doesn't return count for delete)
            const batchDeleted = Math.min(batchSize, recordsToDelete - totalDeleted);
            totalDeleted += batchDeleted;

            console.log(`Deleted batch of ${batchDeleted} records from ${policy.table_name} (total: ${totalDeleted})`);

            // Break if we've deleted fewer than batch size (indicates no more records)
            if (batchDeleted < batchSize) {
              break;
            }

            // Add small delay between batches to avoid overwhelming the database
            await new Promise(resolve => setTimeout(resolve, 100));
          }

          console.log(`Completed deletion of ${totalDeleted} records from ${policy.table_name}`);
          results.push({
            table_name: policy.table_name,
            status: 'success',
            records_affected: totalDeleted,
            message: `Successfully deleted ${totalDeleted} records`,
            dry_run: false
          });
        }
      } catch (error) {
        console.error(`Unexpected error processing ${policy.table_name}:`, error);
        results.push({
          table_name: policy.table_name,
          status: 'error',
          error: error.message,
          records_affected: 0,
          dry_run: dryRun
        });
      }
    }

    const summary = {
      timestamp: new Date().toISOString(),
      dry_run: dryRun,
      policies_processed: policies.length,
      total_records_affected: results.reduce((sum, r) => sum + r.records_affected, 0),
      errors: results.filter(r => r.status === 'error').length,
      results: results
    };

    console.log('Retention enforcement completed:', summary);

    return new Response(JSON.stringify(summary), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    })
  } catch (error) {
    console.error('Retention function error:', error);
    return new Response(JSON.stringify({ 
      error: error.message,
      timestamp: new Date().toISOString()
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    })
  }
})