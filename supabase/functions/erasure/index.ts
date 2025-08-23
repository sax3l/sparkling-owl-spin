import { serve } from "https://deno.land/std@0.190.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface ErasureRequest {
  request_id: string;
  user_id: string;
  data_subject_id?: string;
  erasure_type: 'anonymize' | 'delete' | 'tombstone';
  reason?: string;
  tables?: string[];
  retention_override?: boolean;
}

interface ErasureResult {
  request_id: string;
  status: 'completed' | 'partial' | 'failed';
  affected_records: number;
  errors?: string[];
  completed_at: string;
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    const erasureRequest: ErasureRequest = await req.json()
    
    console.log(`Processing erasure request: ${erasureRequest.request_id}`)

    // Validate request
    if (!erasureRequest.request_id || !erasureRequest.user_id || !erasureRequest.erasure_type) {
      throw new Error('Missing required fields: request_id, user_id, or erasure_type')
    }

    // Start erasure transaction
    const result: ErasureResult = {
      request_id: erasureRequest.request_id,
      status: 'completed',
      affected_records: 0,
      errors: [],
      completed_at: new Date().toISOString()
    }

    // Define tables to process (with cascade order)
    const tablesToProcess = erasureRequest.tables || [
      'crawl_results',
      'job_executions', 
      'jobs',
      'templates',
      'export_requests',
      'dq_metrics',
      'audit_logs',
      'user_sessions',
      'user_preferences'
    ]

    // Process each table
    for (const table of tablesToProcess) {
      try {
        let recordsAffected = 0;

        switch (erasureRequest.erasure_type) {
          case 'delete':
            // Hard delete records
            const { count: deleteCount, error: deleteError } = await supabase
              .from(table)
              .delete({ count: 'exact' })
              .eq('user_id', erasureRequest.user_id)

            if (deleteError) throw deleteError
            recordsAffected = deleteCount || 0
            break

          case 'anonymize':
            // Anonymize PII fields
            const anonymizedData = getAnonymizedFields(table)
            const { count: updateCount, error: updateError } = await supabase
              .from(table)
              .update(anonymizedData, { count: 'exact' })
              .eq('user_id', erasureRequest.user_id)

            if (updateError) throw updateError
            recordsAffected = updateCount || 0
            break

          case 'tombstone':
            // Mark as deleted but keep structure
            const { count: tombstoneCount, error: tombstoneError } = await supabase
              .from(table)
              .update({ 
                is_deleted: true,
                deleted_at: new Date().toISOString(),
                deletion_reason: erasureRequest.reason || 'user_request'
              }, { count: 'exact' })
              .eq('user_id', erasureRequest.user_id)

            if (tombstoneError) throw tombstoneError
            recordsAffected = tombstoneCount || 0
            break
        }

        result.affected_records += recordsAffected

        // Log the operation
        await supabase
          .from('erasure_log')
          .insert({
            request_id: erasureRequest.request_id,
            table_name: table,
            erasure_type: erasureRequest.erasure_type,
            records_affected: recordsAffected,
            user_id: erasureRequest.user_id,
            completed_at: new Date().toISOString()
          })

      } catch (error) {
        console.error(`Error processing table ${table}:`, error)
        result.errors?.push(`${table}: ${error.message}`)
        result.status = 'partial'
      }
    }

    // Update main erasure request status
    await supabase
      .from('erasure_requests')
      .update({
        status: result.status,
        completed_at: result.completed_at,
        records_affected: result.affected_records,
        error_details: result.errors?.length ? result.errors.join('; ') : null
      })
      .eq('request_id', erasureRequest.request_id)

    // Send notification if configured
    if (result.status === 'completed') {
      console.log(`Erasure completed successfully for user ${erasureRequest.user_id}`)
    } else {
      console.warn(`Erasure partially failed for user ${erasureRequest.user_id}:`, result.errors)
    }

    return new Response(JSON.stringify({
      success: true,
      message: "Erasure request processed",
      result: result
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    })

  } catch (error) {
    console.error('Erasure function error:', error)
    
    return new Response(JSON.stringify({ 
      error: error.message,
      request_id: (await req.json().catch(() => ({})))?.request_id,
      timestamp: new Date().toISOString()
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    })
  }
})

function getAnonymizedFields(tableName: string): Record<string, any> {
  const commonAnonymization = {
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  switch (tableName) {
    case 'users':
      return {
        ...commonAnonymization,
        email: 'anonymized@domain.com',
        name: 'Anonymized User',
        phone: null,
        address: null
      }
    
    case 'crawl_results':
      return {
        ...commonAnonymization,
        payload: {
          anonymized: true,
          original_data_removed: new Date().toISOString()
        }
      }
    
    case 'templates':
      return {
        ...commonAnonymization,
        name: 'Anonymized Template',
        description: 'Template anonymized due to user request'
      }
    
    case 'jobs':
      return {
        ...commonAnonymization,
        name: 'Anonymized Job',
        config: {
          anonymized: true
        }
      }
    
    default:
      return commonAnonymization
  }
}