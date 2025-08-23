import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Bell,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Info,
  Mail,
  MessageSquare,
  Smartphone,
  Settings,
  Plus,
  Filter,
  Archive,
  Trash2,
  Eye,
  Clock,
  Shield,
  TrendingUp,
  Database,
  Globe
} from "lucide-react";
import { useState } from "react";

// Mock alerts data
const mockAlerts = [
  {
    id: "alert_001",
    type: "error",
    title: "Job Failure Alert",
    message: "Daily Product Sync failed after 3 retry attempts",
    timestamp: "2024-01-15 14:35:00",
    source: "Job Scheduler",
    severity: "high",
    status: "unread",
    details: {
      jobId: "job_12345",
      errorCode: "TIMEOUT_ERROR",
      retryCount: 3,
      domain: "example.com"
    }
  },
  {
    id: "alert_002", 
    type: "warning",
    title: "High Memory Usage",
    message: "System memory usage exceeded 85% threshold",
    timestamp: "2024-01-15 14:20:00",
    source: "System Monitor",
    severity: "medium",
    status: "read",
    details: {
      currentUsage: "87%",
      threshold: "85%",
      duration: "15 minutes"
    }
  },
  {
    id: "alert_003",
    type: "info",
    title: "Proxy Pool Updated",
    message: "Successfully added 15 new proxies to the active pool",
    timestamp: "2024-01-15 13:45:00",
    source: "Proxy Manager",
    severity: "low",
    status: "read",
    details: {
      newProxies: 15,
      totalActive: 234,
      successRate: "98.2%"
    }
  },
  {
    id: "alert_004",
    type: "success",
    title: "Scheduled Maintenance Complete",
    message: "Database maintenance completed successfully",
    timestamp: "2024-01-15 12:00:00",
    source: "Database Manager",
    severity: "low",
    status: "read",
    details: {
      duration: "45 minutes",
      optimizedTables: 12,
      spaceSaved: "2.3GB"
    }
  },
  {
    id: "alert_005",
    type: "error",
    title: "Rate Limit Exceeded",
    message: "API rate limit exceeded for socialmedia.com",
    timestamp: "2024-01-15 11:30:00",
    source: "Rate Limiter",
    severity: "high", 
    status: "unread",
    details: {
      domain: "socialmedia.com",
      requestCount: 1205,
      limit: 1000,
      resetTime: "2024-01-15 12:00:00"
    }
  }
];

const mockRules = [
  {
    id: "rule_001",
    name: "Job Failure Notification",
    condition: "job.status == 'failed' AND retryCount >= 3",
    action: "email + slack",
    enabled: true,
    severity: "high",
    category: "jobs"
  },
  {
    id: "rule_002",
    name: "System Resource Alert",
    condition: "cpu.usage > 90% OR memory.usage > 85%",
    action: "email",
    enabled: true,
    severity: "medium", 
    category: "system"
  },
  {
    id: "rule_003",
    name: "Proxy Health Check",
    condition: "proxy.successRate < 80% AND proxy.activeCount < 10",
    action: "email + webhook",
    enabled: false,
    severity: "medium",
    category: "proxy"
  },
  {
    id: "rule_004",
    name: "Data Quality Warning",
    condition: "extraction.errorRate > 15%",
    action: "slack",
    enabled: true,
    severity: "low",
    category: "data"
  }
];

const getAlertIcon = (type: string) => {
  switch (type) {
    case "error": return XCircle;
    case "warning": return AlertTriangle;
    case "info": return Info;
    case "success": return CheckCircle;
    default: return Bell;
  }
};

const getAlertColor = (type: string) => {
  switch (type) {
    case "error": return "text-red-600 dark:text-red-400 border-red-200 dark:border-red-800";
    case "warning": return "text-yellow-600 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800";
    case "info": return "text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-800";
    case "success": return "text-green-600 dark:text-green-400 border-green-200 dark:border-green-800";
    default: return "text-gray-600 dark:text-gray-400 border-gray-200 dark:border-gray-800";
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "high": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    case "medium": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    case "low": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
  }
};

export default function AlertsPage() {
  const [activeTab, setActiveTab] = useState("alerts");
  const [alerts, setAlerts] = useState(mockAlerts);
  const [rules, setRules] = useState(mockRules);
  const [selectedAlert, setSelectedAlert] = useState<string | null>(null);

  const markAsRead = (id: string) => {
    setAlerts(alerts.map(alert => 
      alert.id === id ? { ...alert, status: "read" } : alert
    ));
  };

  const deleteAlert = (id: string) => {
    setAlerts(alerts.filter(alert => alert.id !== id));
  };

  const toggleRule = (id: string) => {
    setRules(rules.map(rule => 
      rule.id === id ? { ...rule, enabled: !rule.enabled } : rule
    ));
  };

  const unreadCount = alerts.filter(alert => alert.status === "unread").length;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
            Alerts & Notifications
            {unreadCount > 0 && (
              <Badge variant="destructive" className="text-xs">
                {unreadCount} new
              </Badge>
            )}
          </h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor system alerts and manage notification rules</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <Archive className="h-4 w-4 mr-2" />
            Archive All
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Rule
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Unread Alerts</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">{unreadCount}</p>
              </div>
              <Bell className="h-8 w-8 text-red-600 dark:text-red-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">High Priority</p>
                <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {alerts.filter(a => a.severity === "high").length}
                </p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Rules</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {rules.filter(r => r.enabled).length}
                </p>
              </div>
              <Shield className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Today's Alerts</p>
                <p className="text-2xl font-bold">12</p>
                <p className="text-xs text-gray-500">↑ 25% from yesterday</p>
              </div>
              <TrendingUp className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="alerts">Recent Alerts</TabsTrigger>
          <TabsTrigger value="rules">Alert Rules</TabsTrigger>
          <TabsTrigger value="channels">Notification Channels</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Recent Alerts Tab */}
        <TabsContent value="alerts" className="space-y-4">
          {alerts.map((alert) => {
            const AlertIcon = getAlertIcon(alert.type);
            
            return (
              <Card key={alert.id} className={`${alert.status === "unread" ? "border-l-4 border-l-blue-500" : ""}`}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1">
                      <AlertIcon className={`h-5 w-5 mt-0.5 ${getAlertColor(alert.type).split(' ')[0]}`} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium">{alert.title}</h3>
                          <Badge className={getSeverityColor(alert.severity)}>
                            {alert.severity}
                          </Badge>
                          {alert.status === "unread" && (
                            <Badge variant="secondary" className="text-xs">New</Badge>
                          )}
                        </div>
                        
                        <p className="text-gray-600 dark:text-gray-400 mb-2">{alert.message}</p>
                        
                        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            {alert.timestamp}
                          </span>
                          <span>Source: {alert.source}</span>
                        </div>

                        {selectedAlert === alert.id && (
                          <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <h4 className="font-medium mb-2">Alert Details</h4>
                            <div className="space-y-1 text-sm">
                              {Object.entries(alert.details).map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                  <span className="capitalize">{key.replace(/([A-Z])/g, ' $1').toLowerCase()}:</span>
                                  <span className="font-medium">{value}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedAlert(selectedAlert === alert.id ? null : alert.id)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {alert.status === "unread" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => markAsRead(alert.id)}
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteAlert(alert.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </TabsContent>

        {/* Alert Rules Tab */}
        <TabsContent value="rules" className="space-y-4">
          <div className="space-y-4">
            {rules.map((rule) => (
              <Card key={rule.id}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-lg">{rule.name}</h3>
                        <Badge variant={rule.enabled ? "default" : "secondary"}>
                          {rule.enabled ? "Active" : "Disabled"}
                        </Badge>
                        <Badge className={getSeverityColor(rule.severity)}>
                          {rule.severity}
                        </Badge>
                      </div>
                      
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Condition: </span>
                          <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-xs">
                            {rule.condition}
                          </code>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Action: </span>
                          <span className="font-medium">{rule.action}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleRule(rule.id)}
                      >
                        {rule.enabled ? "Disable" : "Enable"}
                      </Button>
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Create New Rule */}
          <Card>
            <CardHeader>
              <CardTitle>Create New Alert Rule</CardTitle>
              <CardDescription>Define conditions and actions for automated alerts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Rule Name</label>
                  <Input placeholder="e.g., High CPU Usage Alert" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Category</label>
                  <select className="w-full p-2 border rounded-lg bg-background">
                    <option value="jobs">Jobs</option>
                    <option value="system">System</option>
                    <option value="proxy">Proxy</option>
                    <option value="data">Data Quality</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Severity</label>
                  <select className="w-full p-2 border rounded-lg bg-background">
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Notification Method</label>
                  <select className="w-full p-2 border rounded-lg bg-background">
                    <option value="email">Email</option>
                    <option value="slack">Slack</option>
                    <option value="webhook">Webhook</option>
                    <option value="email+slack">Email + Slack</option>
                  </select>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium">Condition</label>
                <Input placeholder="e.g., cpu.usage > 90% OR memory.usage > 85%" className="font-mono text-sm" />
              </div>

              <Button className="w-full">Create Alert Rule</Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notification Channels Tab */}
        <TabsContent value="channels" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Mail className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-lg">Email</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Status</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                  <div className="text-sm">
                    <p className="text-gray-600 dark:text-gray-400">Recipients: 3</p>
                    <p className="text-gray-600 dark:text-gray-400">Last sent: 2h ago</p>
                  </div>
                  <Button variant="outline" size="sm" className="w-full">
                    Configure
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-green-600" />
                  <CardTitle className="text-lg">Slack</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Status</span>
                    <Badge variant="secondary">Inactive</Badge>
                  </div>
                  <div className="text-sm">
                    <p className="text-gray-600 dark:text-gray-400">Not configured</p>
                  </div>
                  <Button variant="outline" size="sm" className="w-full">
                    Setup Slack
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center gap-2">
                  <Globe className="h-5 w-5 text-purple-600" />
                  <CardTitle className="text-lg">Webhook</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Status</span>
                    <Badge variant="default">Active</Badge>
                  </div>
                  <div className="text-sm">
                    <p className="text-gray-600 dark:text-gray-400">Endpoints: 2</p>
                    <p className="text-gray-600 dark:text-gray-400">Success rate: 98%</p>
                  </div>
                  <Button variant="outline" size="sm" className="w-full">
                    Configure
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Alert Settings</CardTitle>
              <CardDescription>Configure global alert behavior and preferences</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Enable Sound Notifications</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Play sound for high priority alerts</p>
                  </div>
                  <Button variant="outline" size="sm">Toggle</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Auto-archive Read Alerts</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Archive alerts after 7 days</p>
                  </div>
                  <Button variant="outline" size="sm">Toggle</Button>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Alert Retention Period</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>7 days</option>
                    <option>30 days</option>
                    <option>90 days</option>
                    <option>1 year</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Default Severity Filter</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>All severities</option>
                    <option>High and Medium</option>
                    <option>High only</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t">
                <Button>Save Settings</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
