import { ScrapingAPI } from '../generated/api-client';

/**
 * TypeScript client example for the scraping platform
 */
class ScrapingClient {
    private apiClient: ScrapingAPI;

    constructor(apiKey: string, baseURL: string = 'http://localhost:8000') {
        this.apiClient = new ScrapingAPI({
            basePath: baseURL,
            apiKey: apiKey
        });
    }

    async startCrawl(url: string, template: string): Promise<any> {
        try {
            const result = await this.apiClient.startCrawl({
                url,
                template
            });
            return result.data;
        } catch (error) {
            console.error('Error starting crawl:', error);
            throw error;
        }
    }

    async getJobStatus(jobId: string): Promise<any> {
        try {
            const result = await this.apiClient.getJobStatus(jobId);
            return result.data;
        } catch (error) {
            console.error('Error getting job status:', error);
            throw error;
        }
    }
}

// Usage example
async function main() {
    const client = new ScrapingClient('your-api-key-here');
    
    try {
        const job = await client.startCrawl('https://example.com', 'company_profile_v1');
        console.log('Started job:', job);
        
        const status = await client.getJobStatus(job.id);
        console.log('Job status:', status);
    } catch (error) {
        console.error('Error:', error);
    }
}

if (require.main === module) {
    main();
}
