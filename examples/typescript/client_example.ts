import { ScrapingAPI } from '../../generated/api-client';

/**
 * TypeScript client example for the revolutionary scraping platform
 */
class ScrapingClient {
    private apiClient: ScrapingAPI;

    constructor(apiKey?: string, baseURL: string = '/api') {
        this.apiClient = new ScrapingAPI(baseURL, apiKey);
    }

    async startCrawl(url: string): Promise<any> {
        try {
            const result = await this.apiClient.crawlUrl({
                url,
                extraction_rules: [
                    {
                        name: 'title',
                        method: 'css',
                        selector: 'h1, .title',
                        content_type: 'text',
                        required: true
                    },
                    {
                        name: 'links', 
                        method: 'css',
                        selector: 'a[href]',
                        content_type: 'links',
                        multiple: true
                    }
                ]
            });
            return result;
        } catch (error) {
            console.error('Error starting crawl:', error);
            throw error;
        }
    }

    async getDashboardData(): Promise<any> {
        try {
            const result = await this.apiClient.getDashboardData();
            return result;
        } catch (error) {
            console.error('Error getting dashboard data:', error);
            throw error;
        }
    }

    async getProxyStats(): Promise<any> {
        try {
            const result = await this.apiClient.getProxyStats();
            return result;
        } catch (error) {
            console.error('Error getting proxy stats:', error);
            throw error;
        }
    }
}

// Usage example
async function demo() {
    const client = new ScrapingClient();
    
    try {
        // Create API instance for health check
        const api = new ScrapingAPI();
        
        // Health check
        const health = await api.healthCheck();
        console.log('System health:', health);
        
        // Get dashboard data
        const dashboard = await client.getDashboardData();
        console.log('Dashboard:', dashboard);
        
        // Start a crawl
        const crawlResult = await client.startCrawl('https://example.com');
        console.log('Crawl result:', crawlResult);
        
    } catch (error) {
        console.error('Demo failed:', error);
    }
}

export { ScrapingClient, demo };
