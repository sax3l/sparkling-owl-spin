import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  BarChart3,
  TrendingUp,
  TrendingDown,
  Download,
  RefreshCw,
  Calendar,
  Filter,
  Share,
  Eye,
  Activity,
  Clock,
  Target,
  Zap,
  DollarSign,
  Globe,
  Users,
  Database,
  AlertCircle,
  CheckCircle
} from "lucide-react";
import { useState } from "react";

// Mock analytics data
const mockMetrics = {
  totalJobs: 2847,
  successRate: 94.8,
  avgResponseTime: 2.3,
  dataPoints: 1250000,
  totalCost: 1847,
  activeProxies: 12,
  monthlyGrowth: 23.5,
  errorRate: 5.2
};

const mockChartData = [
  { date: "2024-01-01", jobs: 45, success: 42, errors: 3 },
  { date: "2024-01-02", jobs: 52, success: 48, errors: 4 },
  { date: "2024-01-03", jobs: 38, success: 36, errors: 2 },
  { date: "2024-01-04", jobs: 67, success: 63, errors: 4 },
  { date: "2024-01-05", jobs: 58, success: 55, errors: 3 },
  { date: "2024-01-06", jobs: 73, success: 69, errors: 4 },
  { date: "2024-01-07", jobs: 61, success: 58, errors: 3 }
];

const topDomains = [
  { domain: "example.com", jobs: 456, success: 98.2, dataPoints: 125000 },
  { domain: "marketplace.io", jobs: 324, success: 96.8, dataPoints: 89000 },
  { domain: "newsportal.com", jobs: 289, success: 94.1, dataPoints: 67000 },
  { domain: "retailsite.net", jobs: 198, success: 91.5, dataPoints: 45000 },
  { domain: "socialmedia.com", jobs: 167, success: 89.7, dataPoints: 38000 }
];

const recentReports = [
  {
    id: "report_001",
    name: "Monthly Performance Summary",
    type: "performance",
    generated: "2024-01-15 09:00:00",
    status: "completed",
    size: "2.4 MB"
  },
  {
    id: "report_002",
    name: "Cost Analysis - Q1 2024",
    type: "cost",
    generated: "2024-01-14 16:30:00", 
    status: "completed",
    size: "1.8 MB"
  },
  {
    id: "report_003",
    name: "Domain Health Report",
    type: "health",
    generated: "2024-01-14 08:15:00",
    status: "completed",
    size: "3.1 MB"
  }
];

export default function AnalyticsReportsPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [dateRange, setDateRange] = useState("7d");

  const generateReport = (type: string) => {
    console.log(`Generating ${type} report`);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics & Reports</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor performance and generate detailed reports</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Calendar className="h-4 w-4 mr-2" />
            Date Range
          </Button>
          <Button size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Jobs</p>
                <p className="text-2xl font-bold">{mockMetrics.totalJobs.toLocaleString()}</p>
                <div className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400">
                  <TrendingUp className="h-3 w-3" />
                  +{mockMetrics.monthlyGrowth}%
                </div>
              </div>
              <Activity className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Success Rate</p>
                <p className="text-2xl font-bold">{mockMetrics.successRate}%</p>
                <Progress value={mockMetrics.successRate} className="mt-2 h-2" />
              </div>
              <Target className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Response</p>
                <p className="text-2xl font-bold">{mockMetrics.avgResponseTime}s</p>
                <div className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400">
                  <TrendingDown className="h-3 w-3" />
                  -12% faster
                </div>
              </div>
              <Zap className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Monthly Cost</p>
                <p className="text-2xl font-bold">${mockMetrics.totalCost}</p>
                <div className="flex items-center gap-1 text-sm text-red-600 dark:text-red-400">
                  <TrendingUp className="h-3 w-3" />
                  +8.3%
                </div>
              </div>
              <DollarSign className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="domains">Domains</TabsTrigger>
          <TabsTrigger value="costs">Costs</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Job Trends Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Job Trends (Last 7 Days)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-end justify-between gap-2 p-4">
                  {mockChartData.map((data, index) => (
                    <div key={index} className="flex-1 flex flex-col items-center gap-2">
                      <div className="relative w-full bg-gray-100 dark:bg-gray-800 rounded-t">
                        <div 
                          className="bg-blue-500 rounded-t transition-all duration-300"
                          style={{ height: `${(data.jobs / 80) * 200}px` }}
                        />
                        <div 
                          className="bg-green-500 rounded-t absolute bottom-0 w-full transition-all duration-300"
                          style={{ height: `${(data.success / 80) * 200}px` }}
                        />
                      </div>
                      <div className="text-xs text-center">
                        <div className="font-medium">{data.jobs}</div>
                        <div className="text-gray-500">
                          {new Date(data.date).toLocaleDateString('en-US', { weekday: 'short' })}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="flex justify-center gap-4 mt-4 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-blue-500 rounded" />
                    <span>Total Jobs</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded" />
                    <span>Successful</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Health */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  System Health
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  {[
                    { label: "API Response Time", value: 98, status: "excellent" },
                    { label: "Proxy Pool Health", value: 85, status: "good" },
                    { label: "Database Performance", value: 92, status: "excellent" },
                    { label: "Error Rate", value: 15, status: "warning" }
                  ].map((metric, index) => (
                    <div key={index} className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>{metric.label}</span>
                        <span className={
                          metric.status === "excellent" ? "text-green-600 dark:text-green-400" :
                          metric.status === "good" ? "text-blue-600 dark:text-blue-400" :
                          "text-yellow-600 dark:text-yellow-400"
                        }>
                          {metric.value}%
                        </span>
                      </div>
                      <Progress 
                        value={metric.value} 
                        className="h-2" 
                      />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { time: "14:30", type: "job_completed", message: "E-commerce scraping job completed successfully", domain: "example.com" },
                  { time: "14:25", type: "error", message: "Rate limit exceeded on proxy pool EU-West", domain: "retailsite.net" },
                  { time: "14:20", type: "job_started", message: "New product catalog crawl initiated", domain: "marketplace.io" },
                  { time: "14:15", type: "proxy_health", message: "Proxy pool Asia-Pacific restored to full capacity", domain: null },
                  { time: "14:10", type: "job_completed", message: "News article extraction completed", domain: "newsportal.com" }
                ].map((activity, index) => (
                  <div key={index} className="flex items-center gap-4 p-3 border rounded-lg">
                    <div className="flex-shrink-0">
                      {activity.type === "job_completed" && <CheckCircle className="h-4 w-4 text-green-600" />}
                      {activity.type === "error" && <AlertCircle className="h-4 w-4 text-red-600" />}
                      {activity.type === "job_started" && <Activity className="h-4 w-4 text-blue-600" />}
                      {activity.type === "proxy_health" && <Globe className="h-4 w-4 text-purple-600" />}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">{activity.message}</p>
                      {activity.domain && (
                        <p className="text-xs text-gray-500 dark:text-gray-400">{activity.domain}</p>
                      )}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {activity.time}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Response Time Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-600">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                    <p>Response time histogram would be rendered here</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Success Rate Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-600">
                  <div className="text-center">
                    <TrendingUp className="h-12 w-12 mx-auto mb-2" />
                    <p>Success rate trend chart would be rendered here</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Domains Tab */}
        <TabsContent value="domains" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Top Performing Domains
              </CardTitle>
              <CardDescription>Domain statistics and performance metrics</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topDomains.map((domain, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="font-medium text-lg">{domain.domain}</span>
                        <Badge variant={domain.success > 95 ? "default" : "secondary"}>
                          {domain.success}% success
                        </Badge>
                      </div>
                      <div className="flex gap-6 text-sm text-gray-600 dark:text-gray-400">
                        <span>{domain.jobs} jobs</span>
                        <span>{domain.dataPoints.toLocaleString()} data points</span>
                      </div>
                      <Progress value={domain.success} className="mt-2 h-2" />
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <BarChart3 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Generate Reports */}
            <Card>
              <CardHeader>
                <CardTitle>Generate New Report</CardTitle>
                <CardDescription>Create detailed reports for analysis</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-3">
                  {[
                    { type: "performance", label: "Performance Report", description: "Detailed job performance analysis", icon: BarChart3 },
                    { type: "cost", label: "Cost Analysis", description: "Resource usage and cost breakdown", icon: DollarSign },
                    { type: "health", label: "System Health Report", description: "Infrastructure and proxy health", icon: Activity },
                    { type: "custom", label: "Custom Report", description: "Configure your own metrics", icon: Target }
                  ].map((report) => {
                    const Icon = report.icon;
                    return (
                      <div key={report.type} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <Icon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                          <div>
                            <p className="font-medium">{report.label}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-400">{report.description}</p>
                          </div>
                        </div>
                        <Button size="sm" onClick={() => generateReport(report.type)}>
                          Generate
                        </Button>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Recent Reports */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Reports</CardTitle>
                <CardDescription>Previously generated reports</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentReports.map((report) => (
                    <div key={report.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <p className="font-medium">{report.name}</p>
                        <div className="flex gap-4 text-sm text-gray-600 dark:text-gray-400 mt-1">
                          <span>{report.generated}</span>
                          <span>{report.size}</span>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Share className="h-4 w-4" />
                        </Button>
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
