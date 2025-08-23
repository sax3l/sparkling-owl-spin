import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Key,
  Globe,
  Shield,
  Clock,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Copy,
  Eye,
  EyeOff,
  Trash2,
  Plus,
  Settings,
  Activity,
  BarChart3,
  Users,
  Lock,
  Unlock,
  RefreshCw,
  Code,
  FileText,
  Zap
} from "lucide-react";
import { useState } from "react";

// Mock API data
const mockApiKeys = [
  {
    id: "api_001",
    name: "Production API Key",
    key: "dcs_live_sk_1234567890abcdef",
    status: "active",
    permissions: ["read", "write", "admin"],
    lastUsed: "2024-01-15 14:30:00",
    requestCount: 15420,
    rateLimit: "1000/hour",
    createdAt: "2024-01-01",
    expiresAt: "2024-12-31"
  },
  {
    id: "api_002", 
    name: "Development Key",
    key: "dcs_test_sk_abcdef1234567890",
    status: "active",
    permissions: ["read", "write"],
    lastUsed: "2024-01-15 12:15:00",
    requestCount: 2847,
    rateLimit: "500/hour",
    createdAt: "2024-01-10",
    expiresAt: "2024-06-30"
  },
  {
    id: "api_003",
    name: "Analytics Integration",
    key: "dcs_analytics_sk_fedcba0987654321",
    status: "limited",
    permissions: ["read"],
    lastUsed: "2024-01-14 18:45:00",
    requestCount: 8765,
    rateLimit: "200/hour",
    createdAt: "2024-01-05",
    expiresAt: "2024-03-31"
  },
  {
    id: "api_004",
    name: "Legacy Integration",
    key: "dcs_legacy_sk_9876543210fedcba",
    status: "disabled",
    permissions: ["read"],
    lastUsed: "2024-01-10 09:20:00",
    requestCount: 150,
    rateLimit: "100/hour",
    createdAt: "2023-12-01",
    expiresAt: "2024-01-31"
  }
];

const mockEndpoints = [
  {
    path: "/api/v1/jobs",
    method: "GET",
    description: "List all crawling jobs",
    rateLimit: "100/min",
    requestCount: 8420,
    avgResponse: "145ms",
    successRate: "99.2%",
    auth: "API Key",
    status: "active"
  },
  {
    path: "/api/v1/jobs",
    method: "POST", 
    description: "Create a new crawling job",
    rateLimit: "20/min",
    requestCount: 1250,
    avgResponse: "234ms",
    successRate: "97.8%",
    auth: "API Key",
    status: "active"
  },
  {
    path: "/api/v1/templates",
    method: "GET",
    description: "Get crawling templates",
    rateLimit: "50/min",
    requestCount: 3420,
    avgResponse: "89ms",
    successRate: "99.8%",
    auth: "API Key",
    status: "active"
  },
  {
    path: "/api/v1/data/export",
    method: "POST",
    description: "Export crawled data",
    rateLimit: "10/min",
    requestCount: 650,
    avgResponse: "2.1s",
    successRate: "98.5%",
    auth: "API Key + OAuth",
    status: "active"
  },
  {
    path: "/api/v1/proxies",
    method: "GET",
    description: "Get proxy pool status",
    rateLimit: "30/min",
    requestCount: 2100,
    avgResponse: "67ms",
    successRate: "99.5%",
    auth: "API Key",
    status: "active"
  }
];

const mockWebhooks = [
  {
    id: "webhook_001",
    name: "Job Completion Webhook",
    url: "https://your-app.com/webhooks/job-completed",
    events: ["job.completed", "job.failed"],
    status: "active",
    lastTriggered: "2024-01-15 14:30:00",
    deliveryRate: "98.5%",
    retryAttempts: 3
  },
  {
    id: "webhook_002",
    name: "Data Export Notification",
    url: "https://analytics.company.com/data-webhook",
    events: ["data.exported"],
    status: "active",
    lastTriggered: "2024-01-15 12:15:00",
    deliveryRate: "99.2%",
    retryAttempts: 3
  },
  {
    id: "webhook_003",
    name: "Alert Notifications",
    url: "https://monitoring.company.com/alerts",
    events: ["alert.created", "system.error"],
    status: "disabled",
    lastTriggered: "2024-01-10 09:20:00",
    deliveryRate: "85.3%",
    retryAttempts: 5
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return "text-green-600 dark:text-green-400";
    case "limited": return "text-yellow-600 dark:text-yellow-400";  
    case "disabled": return "text-red-600 dark:text-red-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "active": return "default";
    case "limited": return "secondary";
    case "disabled": return "destructive";
    default: return "outline";
  }
};

const getMethodColor = (method: string) => {
  switch (method) {
    case "GET": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    case "POST": return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
    case "PUT": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    case "DELETE": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
  }
};

export default function ApiManagementPage() {
  const [activeTab, setActiveTab] = useState("keys");
  const [apiKeys, setApiKeys] = useState(mockApiKeys);
  const [showKey, setShowKey] = useState<string | null>(null);

  const toggleKeyVisibility = (keyId: string) => {
    setShowKey(showKey === keyId ? null : keyId);
  };

  const regenerateKey = (keyId: string) => {
    // Mock regeneration
    setApiKeys(apiKeys.map(key => 
      key.id === keyId 
        ? { ...key, key: `dcs_${key.key.split('_')[1]}_sk_${Math.random().toString(36).substr(2, 16)}` }
        : key
    ));
  };

  const toggleKeyStatus = (keyId: string) => {
    setApiKeys(apiKeys.map(key => 
      key.id === keyId 
        ? { ...key, status: key.status === "active" ? "disabled" : "active" }
        : key
    ));
  };

  const deleteKey = (keyId: string) => {
    setApiKeys(apiKeys.filter(key => key.id !== keyId));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">API Management</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage API keys, endpoints, and integrations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            Documentation
          </Button>
          <Button variant="outline" size="sm">
            <Activity className="h-4 w-4 mr-2" />
            Monitor
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Create API Key
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Keys</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {apiKeys.filter(k => k.status === "active").length}
                </p>
              </div>
              <Key className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">API Requests</p>
                <p className="text-2xl font-bold">127.5K</p>
                <p className="text-xs text-gray-500">today</p>
              </div>
              <BarChart3 className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Success Rate</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">98.7%</p>
                <p className="text-xs text-gray-500">last 24h</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Response</p>
                <p className="text-2xl font-bold">156ms</p>
                <p className="text-xs text-gray-500">↓ 12% improvement</p>
              </div>
              <Zap className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="keys">API Keys</TabsTrigger>
          <TabsTrigger value="endpoints">Endpoints</TabsTrigger>
          <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* API Keys Tab */}
        <TabsContent value="keys" className="space-y-4">
          {apiKeys.map((apiKey) => (
            <Card key={apiKey.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Key className={`h-5 w-5 ${getStatusColor(apiKey.status)}`} />
                    <div>
                      <h3 className="font-semibold text-lg">{apiKey.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Created: {apiKey.createdAt} • Expires: {apiKey.expiresAt}
                      </p>
                    </div>
                  </div>
                  <Badge variant={getStatusBadge(apiKey.status)}>
                    {apiKey.status}
                  </Badge>
                </div>

                <div className="space-y-4">
                  {/* API Key Display */}
                  <div className="flex items-center gap-2 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <code className="flex-1 font-mono text-sm">
                      {showKey === apiKey.id ? apiKey.key : "•".repeat(32)}
                    </code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => toggleKeyVisibility(apiKey.id)}
                    >
                      {showKey === apiKey.id ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Key Details */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Permissions</span>
                      <div className="flex gap-1 mt-1">
                        {apiKey.permissions.map((perm) => (
                          <Badge key={perm} variant="outline" className="text-xs">
                            {perm}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Requests</span>
                      <p className="font-medium">{apiKey.requestCount.toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Rate Limit</span>
                      <p className="font-medium">{apiKey.rateLimit}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Last Used</span>
                      <p className="font-medium">{apiKey.lastUsed}</p>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-2 border-t">
                    <Button variant="outline" size="sm">
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => regenerateKey(apiKey.id)}
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Regenerate
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => toggleKeyStatus(apiKey.id)}
                    >
                      {apiKey.status === "active" ? (
                        <><Lock className="h-4 w-4 mr-2" />Disable</>
                      ) : (
                        <><Unlock className="h-4 w-4 mr-2" />Enable</>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteKey(apiKey.id)}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {/* Create New API Key */}
          <Card>
            <CardHeader>
              <CardTitle>Create New API Key</CardTitle>
              <CardDescription>Generate a new API key with specific permissions</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Key Name</label>
                  <Input placeholder="e.g., Production Integration" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Expires</label>
                  <select className="w-full p-2 border rounded-lg bg-background">
                    <option>Never</option>
                    <option>30 days</option>
                    <option>90 days</option>
                    <option>1 year</option>
                  </select>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Permissions</label>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">Read</Button>
                  <Button variant="outline" size="sm">Write</Button>
                  <Button variant="outline" size="sm">Admin</Button>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Rate Limit (requests/hour)</label>
                <Input type="number" placeholder="1000" />
              </div>

              <Button className="w-full">Generate API Key</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Endpoints Tab */}
        <TabsContent value="endpoints" className="space-y-4">
          <div className="space-y-4">
            {mockEndpoints.map((endpoint, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Badge className={getMethodColor(endpoint.method)}>
                        {endpoint.method}
                      </Badge>
                      <div>
                        <code className="font-mono text-sm font-medium">{endpoint.path}</code>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{endpoint.description}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm">
                      <div className="text-center">
                        <p className="font-medium">{endpoint.requestCount.toLocaleString()}</p>
                        <p className="text-gray-500">Requests</p>
                      </div>
                      <div className="text-center">
                        <p className="font-medium">{endpoint.avgResponse}</p>
                        <p className="text-gray-500">Avg Response</p>
                      </div>
                      <div className="text-center">
                        <p className="font-medium text-green-600">{endpoint.successRate}</p>
                        <p className="text-gray-500">Success</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between mt-3 pt-3 border-t">
                    <div className="flex items-center gap-4 text-sm">
                      <span>Rate Limit: <span className="font-medium">{endpoint.rateLimit}</span></span>
                      <span>Auth: <span className="font-medium">{endpoint.auth}</span></span>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Code className="h-4 w-4 mr-2" />
                        Docs
                      </Button>
                      <Button variant="outline" size="sm">
                        <Activity className="h-4 w-4 mr-2" />
                        Monitor
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Webhooks Tab */}
        <TabsContent value="webhooks" className="space-y-4">
          {mockWebhooks.map((webhook) => (
            <Card key={webhook.id}>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Globe className={`h-5 w-5 ${getStatusColor(webhook.status)}`} />
                    <div>
                      <h3 className="font-semibold text-lg">{webhook.name}</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{webhook.url}</p>
                    </div>
                  </div>
                  <Badge variant={getStatusBadge(webhook.status)}>
                    {webhook.status}
                  </Badge>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Events</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {webhook.events.map((event, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          {event}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Last Triggered</span>
                    <p className="font-medium">{webhook.lastTriggered}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Delivery Rate</span>
                    <p className="font-medium text-green-600">{webhook.deliveryRate}</p>
                  </div>
                  <div>
                    <span className="text-gray-500 dark:text-gray-400">Retry Attempts</span>
                    <p className="font-medium">{webhook.retryAttempts}</p>
                  </div>
                </div>

                <div className="flex gap-2 pt-3 border-t">
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure
                  </Button>
                  <Button variant="outline" size="sm">
                    Test
                  </Button>
                  <Button variant="outline" size="sm">
                    <Activity className="h-4 w-4 mr-2" />
                    Logs
                  </Button>
                  <Button variant="outline" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}

          <Card>
            <CardHeader>
              <CardTitle>Create New Webhook</CardTitle>
              <CardDescription>Set up webhook notifications for events</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Webhook Name</label>
                <Input placeholder="e.g., Job Status Notifications" />
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Endpoint URL</label>
                <Input placeholder="https://your-app.com/webhook" />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Events</label>
                <div className="flex flex-wrap gap-2">
                  {["job.completed", "job.failed", "data.exported", "alert.created", "system.error"].map((event) => (
                    <Button key={event} variant="outline" size="sm">
                      {event}
                    </Button>
                  ))}
                </div>
              </div>

              <Button className="w-full">Create Webhook</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Request Volume</CardTitle>
                <CardDescription>API requests over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📊 Chart: API requests per hour
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Response Times</CardTitle>
                <CardDescription>Average response times by endpoint</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📈 Chart: Response time trends
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Error Rates</CardTitle>
                <CardDescription>HTTP status codes distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📉 Chart: Error rate trends
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Consumers</CardTitle>
                <CardDescription>Most active API key usage</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {apiKeys.slice(0, 3).map((key, idx) => (
                    <div key={key.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                      <span className="font-medium">{key.name}</span>
                      <Badge>{key.requestCount.toLocaleString()} req</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
