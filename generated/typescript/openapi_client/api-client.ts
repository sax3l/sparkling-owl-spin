/**
 * Generated TypeScript OpenAPI Client
 * 
 * This client is automatically generated from the OpenAPI specification.
 */

export interface ApiConfiguration {
  basePath?: string;
  apiKey?: string;
  username?: string;
  password?: string;
}

export class ApiClient {
  private basePath: string;
  private apiKey?: string;
  
  constructor(config: ApiConfiguration = {}) {
    this.basePath = config.basePath || 'http://localhost:8000';
    this.apiKey = config.apiKey;
  }
  
  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }
    
    return headers;
  }
  
  async request<T>(
    path: string, 
    method: string = 'GET', 
    body?: any
  ): Promise<T> {
    const url = `${this.basePath}${path}`;
    const headers = this.getHeaders();
    
    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return response.json();
  }
}
