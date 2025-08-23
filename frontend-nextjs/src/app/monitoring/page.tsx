import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  Cpu,
  Database,
  Globe,
  HardDrive,
  MemoryStick,
  Network,
  Server,
  Wifi,
  Zap,
  RefreshCw,
  Settings,
  Bell,
  Eye,
  TrendingUp,
  TrendingDown,
  Users,
  Shield,
  BarChart3
} from "lucide-react";
import { useState } from "react";

// Mock monitoring data
const systemMetrics = {
  status: "healthy",
  uptime: "15d 4h 32m",
  totalRequests: 2840567,
  activeJobs: 8,
  cpu: 34,
  memory: 67,
  disk: 45,
  network: 12.5
};

const services = [
  {
    name: "Web Scraping Engine",
    status: "healthy",
    uptime: "99.98%",
    responseTime: 245,
    requests: 125000,
    errors: 23,
    lastCheck: "30s ago"
  },
  {
    name: "Proxy Manager",
    status: "healthy",
    uptime: "99.95%",
    responseTime: 156,
    requests: 89000,
    errors: 12,
    lastCheck: "45s ago"
  },
  {
    name: "Data Pipeline",
    status: "warning",
    uptime: "98.76%",
    responseTime: 389,
    requests: 67000,
    errors: 145,
    lastCheck: "1m ago"
  },
  {
    name: "Authentication Service",
    status: "healthy",
    uptime: "99.99%",
    responseTime: 89,
    requests: 45000,
    errors: 3,
    lastCheck: "15s ago"
  }
];

const alerts = [
  {
    id: "alert_001",
    type: "warning",
    service: "Data Pipeline",
    message: "High response time detected (>300ms average)",
    timestamp: "2024-01-15 14:35:00",
    severity: "medium"
  },
  {
    id: "alert_002",
    type: "info",
    service: "Proxy Manager",
    message: "Proxy pool EU-West restored to full capacity",
    timestamp: "2024-01-15 14:20:00",
    severity: "low"
  },
  {
    id: "alert_003",
    type: "error",
    service: "Database",
    message: "Connection timeout spike in Asia region",
    timestamp: "2024-01-15 13:45:00",
    severity: "high"
  }
];

const performanceData = [
  { time: "14:00", cpu: 25, memory: 60, requests: 450 },
  { time: "14:05", cpu: 30, memory: 65, requests: 523 },
  { time: "14:10", cpu: 28, memory: 62, requests: 487 },
  { time: "14:15", cpu: 35, memory: 68, requests: 612 },
  { time: "14:20", cpu: 32, memory: 66, requests: 578 },
  { time: "14:25", cpu: 38, memory: 71, requests: 634 },
  { time: "14:30", cpu: 34, memory: 67, requests: 589 }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "healthy": return "text-green-600 dark:text-green-400";
    case "warning": return "text-yellow-600 dark:text-yellow-400";
    case "error": return "text-red-600 dark:text-red-400";
    case "critical": return "text-red-700 dark:text-red-300";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "healthy": return CheckCircle;
    case "warning": return AlertTriangle;
    case "error": return AlertTriangle;
    case "critical": return AlertTriangle;
    default: return Clock;
  }
};

export default function MonitoringPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [autoRefresh, setAutoRefresh] = useState(true);

  const refreshData = () => {
    console.log("Refreshing monitoring data...");
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">System Monitoring</h1>
          <p className="text-gray-600 dark:text-gray-400">Real-time system health and performance metrics</p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant={autoRefresh ? "default" : "outline"} 
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            Auto Refresh
          </Button>
          <Button variant="outline" size="sm" onClick={refreshData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Bell className="h-4 w-4 mr-2" />
            Alerts
          </Button>
        </div>
      </div>

      {/* System Status Overview */}
      <Card className="border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
              <div>
                <h3 className="text-xl font-bold text-green-800 dark:text-green-200">System Healthy</h3>
                <p className="text-green-600 dark:text-green-400">All services operational</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-green-800 dark:text-green-200">{systemMetrics.uptime}</div>
              <div className="text-sm text-green-600 dark:text-green-400">System Uptime</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">CPU Usage</p>
                <p className="text-2xl font-bold">{systemMetrics.cpu}%</p>
                <Progress value={systemMetrics.cpu} className="mt-2 h-2" />
              </div>
              <Cpu className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Memory</p>
                <p className="text-2xl font-bold">{systemMetrics.memory}%</p>
                <Progress value={systemMetrics.memory} className="mt-2 h-2" />
              </div>
              <MemoryStick className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Disk Usage</p>
                <p className="text-2xl font-bold">{systemMetrics.disk}%</p>
                <Progress value={systemMetrics.disk} className="mt-2 h-2" />
              </div>
              <HardDrive className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Network I/O</p>
                <p className="text-2xl font-bold">{systemMetrics.network} MB/s</p>
                <div className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400 mt-1">
                  <TrendingUp className="h-3 w-3" />
                  Normal
                </div>
              </div>
              <Network className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="services">Services</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Active Jobs */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Active Jobs ({systemMetrics.activeJobs})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Array.from({ length: 3 }, (_, i) => (
                    <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
                      <div>
                        <p className="font-medium">Job #{1234 + i}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">example.com scraping</p>
                      </div>
                      <div className="text-right">
                        <Badge variant="default">Running</Badge>
                        <p className="text-xs text-gray-500 mt-1">75% complete</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Request Volume */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Request Volume (Last Hour)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-48 flex items-end justify-between gap-2">
                  {performanceData.map((data, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center gap-2">
                      <div className="relative w-full bg-gray-100 dark:bg-gray-800 rounded-t">
                        <div 
                          className="bg-blue-500 rounded-t transition-all duration-300"
                          style={{ height: `${(data.requests / 700) * 150}px` }}
                        />
                      </div>
                      <div className="text-xs text-center">
                        <div className="font-medium">{data.requests}</div>
                        <div className="text-gray-500">{data.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {systemMetrics.totalRequests.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Requests Today</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">99.2%</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Success Rate</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">245ms</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Avg Response Time</div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services" className="space-y-4">
          <div className="space-y-4">
            {services.map((service, index) => {
              const StatusIcon = getStatusIcon(service.status);
              return (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <StatusIcon className={`h-6 w-6 ${getStatusColor(service.status)}`} />
                        <div>
                          <h3 className="font-semibold text-lg">{service.name}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Last checked: {service.lastCheck}
                          </p>
                        </div>
                        <Badge variant={service.status === "healthy" ? "default" : "secondary"}>
                          {service.status}
                        </Badge>
                      </div>
                      
                      <div className="flex gap-8 text-sm">
                        <div className="text-center">
                          <div className="font-semibold text-green-600 dark:text-green-400">
                            {service.uptime}
                          </div>
                          <div className="text-xs text-gray-500">Uptime</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold">{service.responseTime}ms</div>
                          <div className="text-xs text-gray-500">Response Time</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-blue-600 dark:text-blue-400">
                            {service.requests.toLocaleString()}
                          </div>
                          <div className="text-xs text-gray-500">Requests</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-red-600 dark:text-red-400">
                            {service.errors}
                          </div>
                          <div className="text-xs text-gray-500">Errors</div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Settings className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>CPU & Memory Usage</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-600">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                    <p>Performance chart would be rendered here</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Request Throughput</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-600">
                  <div className="text-center">
                    <Activity className="h-12 w-12 mx-auto mb-2" />
                    <p>Throughput chart would be rendered here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-4">
          <div className="space-y-3">
            {alerts.map((alert) => {
              const severityColor = {
                high: "border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20",
                medium: "border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-900/20",
                low: "border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20"
              };

              const severityIcon = {
                high: AlertTriangle,
                medium: AlertTriangle,
                low: CheckCircle
              };

              const Icon = severityIcon[alert.severity as keyof typeof severityIcon];

              return (
                <Card key={alert.id} className={severityColor[alert.severity as keyof typeof severityColor]}>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-4">
                      <Icon className={`h-5 w-5 ${
                        alert.severity === "high" ? "text-red-600 dark:text-red-400" :
                        alert.severity === "medium" ? "text-yellow-600 dark:text-yellow-400" :
                        "text-blue-600 dark:text-blue-400"
                      }`} />
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h4 className="font-medium">{alert.service}</h4>
                          <Badge variant="outline" className="text-xs">
                            {alert.severity}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                          {alert.message}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                          {alert.timestamp}
                        </p>
                      </div>
                      <Button variant="outline" size="sm">
                        Acknowledge
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Logs</CardTitle>
              <CardDescription>Recent system activity and error logs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 font-mono text-sm">
                {[
                  "2024-01-15 14:35:22 [INFO] Job #1234 completed successfully",
                  "2024-01-15 14:35:15 [WARN] High response time on proxy pool EU-West",
                  "2024-01-15 14:35:08 [INFO] New job #1235 started",
                  "2024-01-15 14:35:01 [INFO] Proxy health check completed",
                  "2024-01-15 14:34:54 [ERROR] Connection timeout in region Asia-Pacific",
                  "2024-01-15 14:34:47 [INFO] Data pipeline processing batch #567",
                  "2024-01-15 14:34:40 [INFO] User authentication successful"
                ].map((log, index) => (
                  <div key={index} className={`p-2 rounded text-xs ${
                    log.includes("[ERROR]") ? "bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200" :
                    log.includes("[WARN]") ? "bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200" :
                    "bg-gray-50 dark:bg-gray-800"
                  }`}>
                    {log}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
