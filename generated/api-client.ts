/**
 * Generated API Client for Revolutionary Web Scraping Platform
 * Beats all competitors with superior performance and reliability
 */

export interface ProxyConfig {
  id: string;
  host: string;
  port: number;
  type: string;
  location: string;
  success_rate: number;
  avg_response_time: number;
  cost_per_gb: number;
  quality_score: number;
}

export interface CrawlRequest {
  url: string;
  extraction_rules?: ExtractionRule[];
  anti_detection?: AntiDetectionConfig;
  proxy_requirements?: ProxyRequirements;
}

export interface ExtractionRule {
  name: string;
  method: string;
  selector: string;
  content_type: string;
  required?: boolean;
  multiple?: boolean;
  ai_prompt?: string;
}

export interface AntiDetectionConfig {
  use_residential_proxies?: boolean;
  randomize_user_agents?: boolean;
  simulate_human_behavior?: boolean;
  fingerprint_randomization?: boolean;
}

export interface ProxyRequirements {
  location?: string;
  quality?: string;
  max_cost_per_request?: number;
}

export interface CrawlResult {
  success: boolean;
  url: string;
  data: Record<string, any>;
  metadata: {
    extraction_time: number;
    confidence_score: number;
    methods_used: string[];
    proxy_location: string;
    anti_detection: boolean;
  };
  performance: {
    success_rate: number;
    avg_extraction_time: number;
    ai_accuracy: number;
    bypass_rate: number;
  };
}

export interface DashboardData {
  real_time_stats: {
    active_crawls: number;
    requests_per_minute: number;
    success_rate: number;
    avg_response_time: number;
    data_extracted_mb: number;
  };
  system_health: {
    cpu_usage: number;
    memory_usage: number;
    proxy_pool_health: number;
    ai_engine_status: string;
    cache_hit_rate: number;
  };
  performance_metrics: {
    pages_crawled_today: number;
    success_rate_24h: number;
    avg_extraction_time: number;
    cost_per_successful_request: number;
    anti_bot_bypass_rate: number;
  };
}

export class ScrapingAPI {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = '/api', apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    };

    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Proxy Management API
  async getOptimalProxy(requirements: ProxyRequirements = {}): Promise<ProxyConfig> {
    return this.request<ProxyConfig>('/proxy', {
      method: 'POST',
      body: JSON.stringify({
        action: 'get_optimal_proxy',
        ...requirements
      })
    });
  }

  async getProxyStats(): Promise<any> {
    return this.request('/proxy', {
      method: 'POST',
      body: JSON.stringify({ action: 'get_proxy_stats' })
    });
  }

  async proxyHealthCheck(): Promise<any> {
    return this.request('/proxy', {
      method: 'POST',
      body: JSON.stringify({ action: 'health_check' })
    });
  }

  // Crawler API
  async crawlUrl(request: CrawlRequest): Promise<CrawlResult> {
    return this.request<CrawlResult>('/crawler', {
      method: 'POST',
      body: JSON.stringify({
        action: 'crawl_url',
        ...request
      })
    });
  }

  async batchCrawl(urls: string[]): Promise<any> {
    return this.request('/crawler', {
      method: 'POST',
      body: JSON.stringify({
        action: 'batch_crawl',
        urls
      })
    });
  }

  async createExtractionTemplate(url: string, contentHints: string[]): Promise<any> {
    return this.request('/crawler', {
      method: 'POST',
      body: JSON.stringify({
        action: 'create_extraction_template',
        url,
        content_hints: contentHints
      })
    });
  }

  // Monitoring API
  async getDashboardData(): Promise<DashboardData> {
    return this.request<DashboardData>('/monitoring', {
      method: 'POST',
      body: JSON.stringify({ action: 'get_dashboard_data' })
    });
  }

  async getAlerts(): Promise<any> {
    return this.request('/monitoring', {
      method: 'POST',
      body: JSON.stringify({ action: 'get_alerts' })
    });
  }

  async exportData(format: 'json' | 'csv' = 'json'): Promise<any> {
    return this.request('/monitoring', {
      method: 'POST',
      body: JSON.stringify({
        action: 'export_data',
        format
      })
    });
  }

  // Health Check
  async healthCheck(): Promise<any> {
    return this.request('/health');
  }
}
