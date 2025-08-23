import { serve } from "https://deno.land/std@0.190.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

interface DQMetrics {
  completeness: number;
  validity: number;
  consistency: number;
  uniqueness: number;
  freshness: number;
  drift_score: number;
}

interface DQRecomputeRequest {
  template_id?: string;
  job_id?: string;
  force_recalculate?: boolean;
  metric_types?: string[];
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders })
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const supabaseAnonKey = Deno.env.get('SUPABASE_ANON_KEY')!
    const supabase = createClient(supabaseUrl, supabaseAnonKey)

    const { template_id, job_id, force_recalculate = false, metric_types = [] }: DQRecomputeRequest = 
      await req.json()

    console.log(`DQ Recompute request: template_id=${template_id}, job_id=${job_id}`)

    // Get data to analyze
    let query = supabase.from('crawl_results')
    if (template_id) {
      query = query.eq('template_id', template_id)
    }
    if (job_id) {
      query = query.eq('job_id', job_id)
    }

    const { data: crawlResults, error: fetchError } = await query
      .select('*')
      .order('created_at', { ascending: false })
      .limit(1000)

    if (fetchError) {
      throw new Error(`Failed to fetch crawl results: ${fetchError.message}`)
    }

    // Calculate DQ metrics
    const dqMetrics = calculateDataQualityMetrics(crawlResults || [])

    // Store updated metrics
    const { error: updateError } = await supabase
      .from('dq_metrics')
      .upsert({
        template_id: template_id || null,
        job_id: job_id || null,
        completeness: dqMetrics.completeness,
        validity: dqMetrics.validity,
        consistency: dqMetrics.consistency,
        uniqueness: dqMetrics.uniqueness,
        freshness: dqMetrics.freshness,
        drift_score: dqMetrics.drift_score,
        computed_at: new Date().toISOString(),
        record_count: crawlResults?.length || 0
      })

    if (updateError) {
      throw new Error(`Failed to update DQ metrics: ${updateError.message}`)
    }

    // Log the recomputation
    await supabase
      .from('dq_recompute_log')
      .insert({
        template_id: template_id || null,
        job_id: job_id || null,
        metrics_calculated: Object.keys(dqMetrics),
        record_count: crawlResults?.length || 0,
        triggered_by: 'api_request'
      })

    const data = {
      success: true,
      message: "Data quality metrics successfully recomputed",
      metrics: dqMetrics,
      records_analyzed: crawlResults?.length || 0,
      timestamp: new Date().toISOString()
    }

    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 200,
    })
  } catch (error) {
    console.error('DQ Recompute error:', error)
    return new Response(JSON.stringify({ 
      error: error.message,
      timestamp: new Date().toISOString()
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400,
    })
  }
})

function calculateDataQualityMetrics(results: any[]): DQMetrics {
  if (!results.length) {
    return {
      completeness: 0,
      validity: 0,
      consistency: 0,
      uniqueness: 0,
      freshness: 0,
      drift_score: 0
    }
  }

  // Completeness: percentage of non-null required fields
  const completenessScores = results.map(result => {
    const payload = result.payload || {}
    const requiredFields = ['title', 'url', 'extracted_at']
    const nonNullFields = requiredFields.filter(field => 
      payload[field] !== null && payload[field] !== undefined && payload[field] !== ''
    )
    return nonNullFields.length / requiredFields.length
  })
  const completeness = completenessScores.reduce((sum, score) => sum + score, 0) / results.length

  // Validity: percentage of records with valid data formats
  const validityScores = results.map(result => {
    const payload = result.payload || {}
    let validFields = 0
    let totalFields = 0

    // URL validation
    if (payload.url) {
      totalFields++
      try {
        new URL(payload.url)
        validFields++
      } catch {}
    }

    // Date validation
    if (payload.extracted_at) {
      totalFields++
      if (!isNaN(Date.parse(payload.extracted_at))) {
        validFields++
      }
    }

    return totalFields > 0 ? validFields / totalFields : 1
  })
  const validity = validityScores.reduce((sum, score) => sum + score, 0) / results.length

  // Consistency: similarity in data formats across records
  const urlFormats = new Set(results.map(r => getUrlFormat(r.payload?.url)))
  const consistency = Math.max(0, 1 - (urlFormats.size - 1) / Math.max(1, results.length / 10))

  // Uniqueness: percentage of unique records
  const uniqueKeys = new Set(results.map(r => `${r.payload?.url}-${r.payload?.title}`))
  const uniqueness = uniqueKeys.size / results.length

  // Freshness: percentage of recent records (last 24 hours)
  const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
  const recentRecords = results.filter(r => new Date(r.created_at) > oneDayAgo)
  const freshness = recentRecords.length / results.length

  // Drift score: consistency of extraction patterns (simplified)
  const avgFieldCount = results.reduce((sum, r) => {
    return sum + Object.keys(r.payload || {}).length
  }, 0) / results.length
  
  const fieldCountVariance = results.reduce((sum, r) => {
    const fieldCount = Object.keys(r.payload || {}).length
    return sum + Math.pow(fieldCount - avgFieldCount, 2)
  }, 0) / results.length
  
  const drift_score = Math.max(0, 100 - (fieldCountVariance * 10))

  return {
    completeness: Math.round(completeness * 100) / 100,
    validity: Math.round(validity * 100) / 100,
    consistency: Math.round(consistency * 100) / 100,
    uniqueness: Math.round(uniqueness * 100) / 100,
    freshness: Math.round(freshness * 100) / 100,
    drift_score: Math.round(drift_score * 100) / 100
  }
}

function getUrlFormat(url: string): string {
  if (!url) return 'empty'
  try {
    const parsed = new URL(url)
    return `${parsed.protocol}//${parsed.hostname}`
  } catch {
    return 'invalid'
  }
}