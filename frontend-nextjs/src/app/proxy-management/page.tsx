import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Shield,
  Globe,
  Zap,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Plus,
  Settings,
  RefreshCw,
  BarChart3,
  Eye,
  Trash2,
  Edit,
  Play,
  Pause,
  MoreHorizontal,
  Search,
  Filter,
  TrendingUp,
  Activity,
  Wifi,
  WifiOff
} from "lucide-react";
import { useState } from "react";

// Mock proxy data
const mockProxies = [
  {
    id: "proxy_001",
    name: "Premium Rotating Pool",
    type: "residential",
    status: "active",
    health: 98,
    location: "Multiple",
    provider: "ProxyMesh",
    endpoints: 1000,
    successRate: 99.2,
    avgResponseTime: 245,
    totalRequests: 45820,
    failedRequests: 367,
    lastChecked: "2024-01-15 14:30:00",
    cost: 299,
    rateLimit: 1000
  },
  {
    id: "proxy_002", 
    name: "Standard Pool A",
    type: "datacenter",
    status: "active",
    health: 87,
    location: "US West",
    provider: "CloudProxy",
    endpoints: 50,
    successRate: 94.5,
    avgResponseTime: 156,
    totalRequests: 23400,
    failedRequests: 1287,
    lastChecked: "2024-01-15 14:25:00",
    cost: 49,
    rateLimit: 500
  },
  {
    id: "proxy_003",
    name: "EU Premium",
    type: "residential", 
    status: "warning",
    health: 73,
    location: "Europe",
    provider: "EuroProxy",
    endpoints: 200,
    successRate: 89.3,
    avgResponseTime: 312,
    totalRequests: 12890,
    failedRequests: 1378,
    lastChecked: "2024-01-15 14:20:00",
    cost: 159,
    rateLimit: 300
  },
  {
    id: "proxy_004",
    name: "Asian Network",
    type: "mobile",
    status: "inactive",
    health: 45,
    location: "Asia Pacific",
    provider: "MobileNet",
    endpoints: 75,
    successRate: 76.8,
    avgResponseTime: 456,
    totalRequests: 8950,
    failedRequests: 2076,
    lastChecked: "2024-01-15 13:45:00",
    cost: 199,
    rateLimit: 200
  }
];

const getStatusIcon = (status: string) => {
  switch (status) {
    case "active": return CheckCircle;
    case "warning": return AlertTriangle;
    case "inactive": return XCircle;
    default: return Clock;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return "text-green-600 dark:text-green-400";
    case "warning": return "text-yellow-600 dark:text-yellow-400";
    case "inactive": return "text-red-600 dark:text-red-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getTypeIcon = (type: string) => {
  switch (type) {
    case "residential": return Shield;
    case "datacenter": return Globe;
    case "mobile": return Wifi;
    default: return Globe;
  }
};

export default function ProxyManagementPage() {
  const [activeTab, setActiveTab] = useState("pools");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");

  const filteredProxies = mockProxies.filter(proxy => {
    const matchesSearch = proxy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proxy.provider.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proxy.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || proxy.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const toggleProxyStatus = (proxyId: string) => {
    console.log(`Toggle status for proxy ${proxyId}`);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Proxy Management</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage and monitor your proxy infrastructure</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh All
          </Button>
          <Button variant="outline" size="sm">
            <BarChart3 className="h-4 w-4 mr-2" />
            Analytics
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Pool
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Pools</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {mockProxies.filter(p => p.status === "active").length}
                </p>
              </div>
              <Shield className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Endpoints</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {mockProxies.reduce((sum, p) => sum + p.endpoints, 0).toLocaleString()}
                </p>
              </div>
              <Globe className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Success Rate</p>
                <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  {Math.round(mockProxies.reduce((sum, p) => sum + p.successRate, 0) / mockProxies.length)}%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Monthly Cost</p>
                <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  ${mockProxies.reduce((sum, p) => sum + p.cost, 0)}
                </p>
              </div>
              <Activity className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="pools">Proxy Pools</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          <TabsTrigger value="configuration">Configuration</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Proxy Pools Tab */}
        <TabsContent value="pools" className="space-y-4">
          {/* Search and Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search proxy pools..."
                    className="pl-10"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="flex gap-2">
                  <Tabs value={selectedStatus} onValueChange={setSelectedStatus}>
                    <TabsList>
                      <TabsTrigger value="all">All</TabsTrigger>
                      <TabsTrigger value="active">Active</TabsTrigger>
                      <TabsTrigger value="warning">Warning</TabsTrigger>
                      <TabsTrigger value="inactive">Inactive</TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Proxy Pool Cards */}
          <div className="space-y-4">
            {filteredProxies.map((proxy) => {
              const StatusIcon = getStatusIcon(proxy.status);
              const TypeIcon = getTypeIcon(proxy.type);
              
              return (
                <Card key={proxy.id} className="hover:shadow-lg transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex flex-col xl:flex-row xl:items-center gap-6">
                      {/* Pool Info */}
                      <div className="flex-1 space-y-3">
                        <div className="flex items-center gap-3">
                          <TypeIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                          <h3 className="font-semibold text-lg">{proxy.name}</h3>
                          <Badge variant={proxy.status === "active" ? "default" : "secondary"} className="flex items-center gap-1">
                            <StatusIcon className="h-3 w-3" />
                            {proxy.status}
                          </Badge>
                          <Badge variant="outline" className="capitalize">
                            {proxy.type}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Provider</span>
                            <p className="font-medium">{proxy.provider}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Location</span>
                            <p className="font-medium">{proxy.location}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Endpoints</span>
                            <p className="font-medium">{proxy.endpoints.toLocaleString()}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Rate Limit</span>
                            <p className="font-medium">{proxy.rateLimit}/min</p>
                          </div>
                        </div>
                      </div>

                      {/* Health and Performance */}
                      <div className="xl:w-80 space-y-4">
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span>Health Score</span>
                            <span className={getStatusColor(proxy.status)}>{proxy.health}%</span>
                          </div>
                          <Progress value={proxy.health} className="h-2" />
                        </div>

                        <div className="grid grid-cols-3 gap-4 text-center text-sm">
                          <div>
                            <div className="font-semibold text-green-600 dark:text-green-400">
                              {proxy.successRate}%
                            </div>
                            <div className="text-xs text-gray-500">Success Rate</div>
                          </div>
                          <div>
                            <div className="font-semibold">{proxy.avgResponseTime}ms</div>
                            <div className="text-xs text-gray-500">Avg Response</div>
                          </div>
                          <div>
                            <div className="font-semibold text-blue-600 dark:text-blue-400">
                              ${proxy.cost}
                            </div>
                            <div className="text-xs text-gray-500">Monthly Cost</div>
                          </div>
                        </div>

                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          <div>Requests: {proxy.totalRequests.toLocaleString()}</div>
                          <div>Failed: {proxy.failedRequests.toLocaleString()}</div>
                          <div>Last checked: {proxy.lastChecked}</div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex xl:flex-col gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => toggleProxyStatus(proxy.id)}
                        >
                          {proxy.status === "active" ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                        </Button>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Settings className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Real-time Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockProxies.slice(0, 3).map((proxy) => (
                    <div key={proxy.id} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${
                          proxy.status === "active" ? "bg-green-500" : 
                          proxy.status === "warning" ? "bg-yellow-500" : "bg-red-500"
                        }`} />
                        <span className="font-medium">{proxy.name}</span>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <span>{proxy.health}%</span>
                        <span>{proxy.avgResponseTime}ms</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" />
                  Health Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded">
                    <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                    <div className="flex-1">
                      <p className="font-medium text-sm">EU Premium - High Response Time</p>
                      <p className="text-xs text-yellow-600 dark:text-yellow-500">
                        Average response time increased to 312ms
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded">
                    <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                    <div className="flex-1">
                      <p className="font-medium text-sm">Asian Network - Degraded Performance</p>
                      <p className="text-xs text-red-600 dark:text-red-500">
                        Success rate dropped below 80%
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Configuration Tab */}
        <TabsContent value="configuration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Global Proxy Settings</CardTitle>
              <CardDescription>Configure default settings for all proxy pools</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Connection Settings</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <label className="text-sm">Default Timeout</label>
                      <Input className="w-24" defaultValue="30" />
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm">Max Retries</label>
                      <Input className="w-24" defaultValue="3" />
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm">Connection Pool Size</label>
                      <Input className="w-24" defaultValue="100" />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-medium">Health Check Settings</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <label className="text-sm">Check Interval (minutes)</label>
                      <Input className="w-24" defaultValue="5" />
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm">Health Threshold (%)</label>
                      <Input className="w-24" defaultValue="80" />
                    </div>
                    <div className="flex items-center justify-between">
                      <label className="text-sm">Alert Threshold (%)</label>
                      <Input className="w-24" defaultValue="70" />
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex gap-2 pt-4 border-t">
                <Button>Save Configuration</Button>
                <Button variant="outline">Reset to Defaults</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Usage Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-600">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                    <p>Usage analytics chart</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Cost Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mockProxies.map((proxy) => (
                    <div key={proxy.id} className="flex items-center justify-between p-3 border rounded">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded-full ${
                          proxy.type === "residential" ? "bg-blue-500" :
                          proxy.type === "datacenter" ? "bg-green-500" : "bg-purple-500"
                        }`} />
                        <span className="font-medium">{proxy.name}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">${proxy.cost}</div>
                        <div className="text-xs text-gray-500">
                          ${(proxy.cost / proxy.totalRequests * 1000).toFixed(3)}/1k req
                        </div>
                      </div>
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
