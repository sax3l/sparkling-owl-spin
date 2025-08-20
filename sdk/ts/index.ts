// TypeScript SDK for the ECaDP API

export class ECaDPClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(options: { baseUrl?: string; apiKey: string }) {
    this.baseUrl = options.baseUrl || 'http://localhost:8000/api/v1';
    this.apiKey = options.apiKey;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: object,
    headers?: HeadersInit,
    stream: boolean = false
  ): Promise<T | Response> {
    const defaultHeaders: HeadersInit = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json',
    };

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: { ...defaultHeaders, ...headers },
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({ message: response.statusText }));
      console.error(`API Error: ${response.status} - ${errorBody.message || JSON.stringify(errorBody)}`);
      throw new Error(`HTTP error! status: ${response.status}, detail: ${errorBody.message || JSON.stringify(errorBody)}`);
    }

    if (stream) {
      return response;
    }
    return response.json() as T;
  }

  async submitCrawlJob(payload: {
    seeds: string[];
    max_depth?: number;
    max_urls?: number;
    allow_domains: string[];
    disallow_patterns?: string[];
    policy?: object;
    caps?: object;
    tags?: string[];
  }): Promise<any> {
    const headers = { 'Idempotency-Key': crypto.randomUUID() };
    return this.request('POST', '/jobs/crawl', payload, headers);
  }

  async submitScrapeJob(payload: {
    template_id: string;
    template_version?: string;
    source: { sitemap_query?: { domain: string; pattern?: string; limit?: number; }; urls?: string[]; };
    policy?: object;
    caps?: object;
    export?: object;
    tags?: string[];
  }): Promise<any> {
    const headers = { 'Idempotency-Key': crypto.randomUUID() };
    return this.request('POST', '/jobs/scrape', payload, headers);
  }

  async getJobStatus(jobId: string): Promise<any> {
    return this.request('GET', `/jobs/${jobId}`);
  }

  async getDataStream(
    entityType: string,
    options?: {
      format?: 'csv' | 'ndjson' | 'json';
      compress?: boolean;
      filters?: object;
      sort_by?: string;
      fields?: string[];
      mask_pii?: boolean;
    }
  ): Promise<Response> {
    const params = new URLSearchParams();
    if (options?.format) params.append('format', options.format);
    if (options?.compress !== undefined) params.append('compress', String(options.compress));
    if (options?.filters) params.append('filters', JSON.stringify(options.filters));
    if (options?.sort_by) params.append('sort_by', options.sort_by);
    if (options?.fields) params.append('fields', options.fields.join(','));
    if (options?.mask_pii !== undefined) params.append('mask_pii', String(options.mask_pii));

    const headers: HeadersInit = {};
    if (options?.format === 'csv') headers['Accept'] = 'text/csv';
    else if (options?.format === 'ndjson') headers['Accept'] = 'application/x-ndjson';
    else if (options?.format === 'json') headers['Accept'] = 'application/json';

    return this.request<Response>('GET', `/data/${entityType}?${params.toString()}`, undefined, headers, true);
  }

  // TODO: Implement other SDK methods (templates, webhooks, proxy stats)
}