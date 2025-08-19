// TypeScript SDK for the ECaDP API

export class ECaDPClient {
  private baseUrl: string;
  private apiKey: string;

  constructor(options: { baseUrl?: string; apiKey: string }) {
    this.baseUrl = options.baseUrl || 'http://localhost:8000';
    this.apiKey = options.apiKey;
  }

  async submitCrawlJob(payload: { startUrl: string }): Promise<any> {
    const response = await fetch(`${this.baseUrl}/jobs/crawl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
        'Idempotency-Key': crypto.randomUUID(),
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error('Failed to submit job');
    }
    return response.json();
  }

  // TODO: Implement other SDK methods
}