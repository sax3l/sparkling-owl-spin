import { createClient, SupabaseClient } from 'https://esm.sh/@supabase/supabase-js@2'

interface WebhookConfig {
  url: string;
  secret?: string;
  headers?: Record<string, string>;
  retry_attempts?: number;
  timeout_ms?: number;
}

interface JobWebhookPayload {
  event_type: 'job_created' | 'job_started' | 'job_completed' | 'job_failed';
  job_id: string;
  job_type: string;
  status: string;
  tenant_id: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export function createSupabaseClient(): SupabaseClient {
  const supabaseUrl = Deno.env.get('SUPABASE_URL');
  const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || Deno.env.get('SUPABASE_ANON_KEY');
  
  if (!supabaseUrl || !supabaseKey) {
    throw new Error('Missing Supabase environment variables');
  }

  return createClient(supabaseUrl, supabaseKey);
}

export async function sendWebhook(
  supabase: SupabaseClient,
  payload: JobWebhookPayload,
  config: WebhookConfig
): Promise<{ success: boolean; error?: string }> {
  const maxRetries = config.retry_attempts || 3;
  const timeout = config.timeout_ms || 5000;
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`Sending webhook (attempt ${attempt}/${maxRetries}) to ${config.url}`);
      
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        'User-Agent': 'ECaDP-Webhook/1.0',
        ...config.headers
      };

      // Add HMAC signature if secret is provided
      if (config.secret) {
        const signature = await generateHmacSignature(JSON.stringify(payload), config.secret);
        headers['X-Webhook-Signature'] = signature;
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(config.url, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        console.log(`Webhook sent successfully to ${config.url}`);
        
        // Log successful webhook delivery
        await logWebhookDelivery(supabase, {
          job_id: payload.job_id,
          webhook_url: config.url,
          status: 'success',
          response_code: response.status,
          attempt: attempt,
          timestamp: new Date().toISOString()
        });
        
        return { success: true };
      } else {
        const errorText = await response.text();
        console.error(`Webhook failed with status ${response.status}: ${errorText}`);
        
        if (attempt === maxRetries) {
          await logWebhookDelivery(supabase, {
            job_id: payload.job_id,
            webhook_url: config.url,
            status: 'failed',
            response_code: response.status,
            error_message: errorText,
            attempt: attempt,
            timestamp: new Date().toISOString()
          });
          
          return { success: false, error: `HTTP ${response.status}: ${errorText}` };
        }
      }
      
    } catch (error) {
      console.error(`Webhook attempt ${attempt} failed:`, error);
      
      if (attempt === maxRetries) {
        await logWebhookDelivery(supabase, {
          job_id: payload.job_id,
          webhook_url: config.url,
          status: 'failed',
          error_message: error.message,
          attempt: attempt,
          timestamp: new Date().toISOString()
        });
        
        return { success: false, error: error.message };
      }
      
      // Exponential backoff delay
      const delay = Math.min(1000 * Math.pow(2, attempt - 1), 10000);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  return { success: false, error: 'Max retries exceeded' };
}

export async function getWebhookConfigs(
  supabase: SupabaseClient, 
  tenantId: string, 
  eventType: string
): Promise<WebhookConfig[]> {
  try {
    const { data, error } = await supabase
      .from('webhook_configs')
      .select('*')
      .eq('tenant_id', tenantId)
      .eq('enabled', true)
      .contains('event_types', [eventType]);

    if (error) {
      console.error('Error fetching webhook configs:', error);
      return [];
    }

    return (data || []).map(config => ({
      url: config.webhook_url,
      secret: config.webhook_secret,
      headers: config.headers || {},
      retry_attempts: config.retry_attempts || 3,
      timeout_ms: config.timeout_ms || 5000
    }));
  } catch (error) {
    console.error('Error in getWebhookConfigs:', error);
    return [];
  }
}

async function generateHmacSignature(payload: string, secret: string): Promise<string> {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const signature = await crypto.subtle.sign('HMAC', key, encoder.encode(payload));
  const hashArray = Array.from(new Uint8Array(signature));
  return 'sha256=' + hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

async function logWebhookDelivery(
  supabase: SupabaseClient,
  log: {
    job_id: string;
    webhook_url: string;
    status: 'success' | 'failed';
    response_code?: number;
    error_message?: string;
    attempt: number;
    timestamp: string;
  }
): Promise<void> {
  try {
    const { error } = await supabase
      .from('webhook_deliveries')
      .insert([log]);

    if (error) {
      console.error('Error logging webhook delivery:', error);
    }
  } catch (error) {
    console.error('Error in logWebhookDelivery:', error);
  }
}

export const supabaseClient = createSupabaseClient;