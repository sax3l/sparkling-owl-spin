import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Code, 
  Play, 
  Copy,
  Terminal,
  Book,
  Zap
} from 'lucide-react';

const APIExplorer = () => {
  const [selectedEndpoint, setSelectedEndpoint] = useState('GET /api/jobs');

  const endpoints = [
    { method: 'GET', path: '/api/jobs', description: 'List all crawling jobs' },
    { method: 'POST', path: '/api/jobs', description: 'Create a new crawling job' },
    { method: 'GET', path: '/api/jobs/{id}', description: 'Get job details' },
    { method: 'DELETE', path: '/api/jobs/{id}', description: 'Cancel a job' },
    { method: 'GET', path: '/api/templates', description: 'List extraction templates' },
    { method: 'POST', path: '/api/templates', description: 'Create new template' },
    { method: 'GET', path: '/api/proxies', description: 'Get proxy pool status' },
    { method: 'GET', path: '/api/data/export', description: 'Export collected data' },
  ];

  const sampleResponse = `{
  "jobs": [
    {
      "id": "job-001",
      "name": "biluppgifter_vehicles_daily",
      "status": "running",
      "progress": 67.3,
      "pages_crawled": 2341,
      "records_extracted": 15623,
      "started_at": "2024-08-21T08:30:00Z",
      "template": "biluppgifter.se",
      "proxy_pool": "residential"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 10
}`;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">API Explorer</h1>
          <p className="text-muted-foreground">Test and explore the ECaDP REST API</p>
        </div>
      </div>

      <Tabs defaultValue="explorer" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="explorer">API Explorer</TabsTrigger>
          <TabsTrigger value="docs">Documentation</TabsTrigger>
          <TabsTrigger value="auth">Authentication</TabsTrigger>
        </TabsList>

        <TabsContent value="explorer" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Request Builder */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Terminal className="w-5 h-5 text-primary" />
                  <span>API Request</span>
                </CardTitle>
                <CardDescription>Build and test API requests</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Endpoint Selector */}
                <div className="space-y-2">
                  <Label>Endpoint</Label>
                  <div className="space-y-2">
                    {endpoints.slice(0, 4).map((endpoint, index) => (
                      <div 
                        key={index}
                        className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                          selectedEndpoint === `${endpoint.method} ${endpoint.path}`
                            ? 'border-primary bg-primary/5'
                            : 'border-sidebar-border hover:bg-sidebar-accent'
                        }`}
                        onClick={() => setSelectedEndpoint(`${endpoint.method} ${endpoint.path}`)}
                      >
                        <div className="flex items-center space-x-3">
                          <Badge 
                            variant="secondary"
                            className={
                              endpoint.method === 'GET' 
                                ? 'bg-success/10 text-success border-success/20'
                                : endpoint.method === 'POST'
                                ? 'bg-primary/10 text-primary border-primary/20'
                                : 'bg-destructive/10 text-destructive border-destructive/20'
                            }
                          >
                            {endpoint.method}
                          </Badge>
                          <div className="flex-1">
                            <p className="font-mono text-sm text-foreground">{endpoint.path}</p>
                            <p className="text-xs text-muted-foreground">{endpoint.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Headers */}
                <div className="space-y-2">
                  <Label>Headers</Label>
                  <div className="space-y-2">
                    <Input placeholder="Authorization: Bearer your-token" />
                    <Input placeholder="Content-Type: application/json" />
                  </div>
                </div>

                {/* Request Body */}
                <div className="space-y-2">
                  <Label>Request Body (JSON)</Label>
                  <Textarea 
                    placeholder='{\n  "name": "test_job",\n  "template": "biluppgifter.se",\n  "max_pages": 100\n}'
                    className="font-mono text-sm"
                    rows={6}
                  />
                </div>

                <Button className="w-full bg-gradient-primary">
                  <Play className="w-4 h-4 mr-2" />
                  Send Request
                </Button>
              </CardContent>
            </Card>

            {/* Response */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Code className="w-5 h-5 text-accent" />
                  <span>Response</span>
                </CardTitle>
                <CardDescription>API response and status</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Status */}
                <div className="flex items-center justify-between">
                  <Label>Status</Label>
                  <Badge className="bg-success/10 text-success border-success/20">
                    200 OK
                  </Badge>
                </div>

                {/* Response Headers */}
                <div className="space-y-2">
                  <Label>Response Headers</Label>
                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <pre className="text-xs text-muted-foreground">
{`Content-Type: application/json
X-Rate-Limit: 1000
X-Rate-Remaining: 999
Response-Time: 142ms`}
                    </pre>
                  </div>
                </div>

                {/* Response Body */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Response Body</Label>
                    <Button size="sm" variant="ghost">
                      <Copy className="w-3 h-3" />
                    </Button>
                  </div>
                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <pre className="text-xs text-foreground overflow-x-auto">
                      {sampleResponse}
                    </pre>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="docs" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* API Overview */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Book className="w-5 h-5 text-primary" />
                  <span>API Overview</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <h4 className="font-semibold text-foreground mb-2">Base URL</h4>
                    <code className="text-sm text-primary">https://api.ecadp.example.com</code>
                  </div>
                  
                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <h4 className="font-semibold text-foreground mb-2">Authentication</h4>
                    <p className="text-sm text-muted-foreground">Bearer token required for all endpoints</p>
                  </div>
                  
                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <h4 className="font-semibold text-foreground mb-2">Rate Limits</h4>
                    <p className="text-sm text-muted-foreground">1000 requests per hour per API key</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Endpoints List */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle>Available Endpoints</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {endpoints.map((endpoint, index) => (
                    <div key={index} className="flex items-center space-x-3 p-2 rounded-lg hover:bg-sidebar-accent">
                      <Badge 
                        variant="secondary"
                        className={
                          endpoint.method === 'GET' 
                            ? 'bg-success/10 text-success border-success/20'
                            : endpoint.method === 'POST'
                            ? 'bg-primary/10 text-primary border-primary/20'
                            : 'bg-destructive/10 text-destructive border-destructive/20'
                        }
                      >
                        {endpoint.method}
                      </Badge>
                      <div className="flex-1">
                        <p className="font-mono text-sm text-foreground">{endpoint.path}</p>
                        <p className="text-xs text-muted-foreground">{endpoint.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="auth" className="space-y-6">
          <div className="text-center py-12">
            <Zap className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">API Authentication</h3>
            <p className="text-muted-foreground">Manage API keys and authentication settings</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default APIExplorer;