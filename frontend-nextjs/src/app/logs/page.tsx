import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search,
  Filter,
  Activity,
  Calendar,
  Download,
  RefreshCw,
  Eye,
  AlertCircle,
  CheckCircle,
  Info,
  AlertTriangle,
  XCircle,
  Clock,
  Server,
  Database,
  Globe,
  Settings,
  Code,
  Bug,
  Zap
} from "lucide-react";
import { useState } from "react";

// Mock log data
const mockLogs = [
  {
    id: "log_001",
    timestamp: "2024-01-15 14:30:45.123",
    level: "INFO",
    service: "crawler-service",
    message: "Successfully crawled 1,247 pages from hemnet.se",
    source: "crawler.py:156",
    requestId: "req_a1b2c3d4",
    userId: "user_123",
    duration: 2450,
    status: "success",
    details: {
      pages_crawled: 1247,
      errors: 0,
      warnings: 3,
      data_extracted: "12.4MB"
    }
  },
  {
    id: "log_002", 
    timestamp: "2024-01-15 14:29:32.456",
    level: "WARN",
    service: "proxy-manager",
    message: "Proxy pool 'residential-1' is running low on available IPs (23% remaining)",
    source: "proxy_manager.py:89",
    requestId: "req_b5c6d7e8",
    userId: "system",
    duration: null,
    status: "warning",
    details: {
      pool_name: "residential-1",
      total_ips: 950,
      available_ips: 218,
      usage_percentage: 77
    }
  },
  {
    id: "log_003",
    timestamp: "2024-01-15 14:28:17.789",
    level: "ERROR",
    service: "data-extractor",
    message: "Failed to extract price information from 45 property listings",
    source: "extractor.py:234",
    requestId: "req_c9d0e1f2",
    userId: "user_456", 
    duration: 1200,
    status: "error",
    details: {
      failed_extractions: 45,
      total_attempts: 1247,
      success_rate: 96.4,
      error_type: "selector_not_found"
    }
  },
  {
    id: "log_004",
    timestamp: "2024-01-15 14:27:05.012",
    level: "DEBUG",
    service: "api-gateway",
    message: "API rate limit applied to user_789 - 98/100 requests in current window",
    source: "rate_limiter.py:45",
    requestId: "req_g3h4i5j6",
    userId: "user_789",
    duration: 12,
    status: "debug",
    details: {
      current_requests: 98,
      limit: 100,
      window: "1hour",
      reset_time: "2024-01-15 15:00:00"
    }
  },
  {
    id: "log_005",
    timestamp: "2024-01-15 14:26:48.345",
    level: "INFO",
    service: "export-service",
    message: "CSV export completed for dataset 'properties_stockholm' - 5,847 records",
    source: "export.py:178",
    requestId: "req_k7l8m9n0",
    userId: "user_234",
    duration: 3400,
    status: "success",
    details: {
      export_format: "CSV",
      record_count: 5847,
      file_size: "2.3MB",
      destination: "s3://exports/properties_stockholm_20240115.csv"
    }
  },
  {
    id: "log_006",
    timestamp: "2024-01-15 14:25:33.678",
    level: "FATAL",
    service: "database",
    message: "Database connection pool exhausted - unable to serve new requests",
    source: "db_pool.py:67",
    requestId: "req_p1q2r3s4",
    userId: "system",
    duration: null,
    status: "fatal",
    details: {
      pool_size: 50,
      active_connections: 50,
      pending_requests: 127,
      last_cleanup: "2024-01-15 14:20:00"
    }
  }
];

const logStats = {
  totalLogs: 2847392,
  logsToday: 127849,
  errorRate: 2.3,
  avgResponseTime: 145,
  topService: "crawler-service",
  alertsActive: 8
};

const serviceStats = [
  { service: "crawler-service", logs: 1248573, errors: 1247, warnings: 5834, success_rate: 99.1 },
  { service: "api-gateway", logs: 892456, errors: 2156, warnings: 3421, success_rate: 99.8 },
  { service: "data-extractor", logs: 456789, errors: 4523, warnings: 2198, success_rate: 98.5 },
  { service: "proxy-manager", logs: 189234, errors: 567, warnings: 1892, success_rate: 99.4 },
  { service: "export-service", logs: 60340, errors: 89, warnings: 234, success_rate: 99.9 }
];

const getLevelColor = (level: string) => {
  switch (level) {
    case "DEBUG": return "text-gray-600 dark:text-gray-400";
    case "INFO": return "text-blue-600 dark:text-blue-400";
    case "WARN": return "text-yellow-600 dark:text-yellow-400";
    case "ERROR": return "text-red-600 dark:text-red-400";
    case "FATAL": return "text-red-800 dark:text-red-300";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getLevelIcon = (level: string) => {
  switch (level) {
    case "DEBUG": return Bug;
    case "INFO": return Info;
    case "WARN": return AlertTriangle;
    case "ERROR": return AlertCircle;
    case "FATAL": return XCircle;
    default: return Info;
  }
};

const getServiceIcon = (service: string) => {
  switch (service) {
    case "crawler-service": return Globe;
    case "api-gateway": return Code;
    case "data-extractor": return Database;
    case "proxy-manager": return Server;
    case "export-service": return Download;
    default: return Activity;
  }
};

const formatDuration = (duration: number | null) => {
  if (!duration) return "N/A";
  if (duration < 1000) return `${duration}ms`;
  return `${(duration / 1000).toFixed(2)}s`;
};

export default function LogsPage() {
  const [activeTab, setActiveTab] = useState("logs");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("all");
  const [selectedService, setSelectedService] = useState("all");

  const filteredLogs = mockLogs.filter(log => {
    const matchesSearch = 
      log.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.service.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.source.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.requestId.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLevel = selectedLevel === "all" || log.level === selectedLevel;
    const matchesService = selectedService === "all" || log.service === selectedService;
    return matchesSearch && matchesLevel && matchesService;
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Loggar</h1>
          <p className="text-gray-600 dark:text-gray-400">Systemloggar och felsökning i realtid</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportera loggar
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Uppdatera
          </Button>
          <Button size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Konfigurera
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Totalt loggar</p>
                <p className="text-2xl font-bold">{logStats.totalLogs.toLocaleString()}</p>
                <p className="text-xs text-gray-500">+{logStats.logsToday.toLocaleString()} idag</p>
              </div>
              <Activity className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Felfrekvens</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">{logStats.errorRate}%</p>
                <p className="text-xs text-gray-500">Senaste 24h</p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-600 dark:text-red-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Medelsvarstid</p>
                <p className="text-2xl font-bold">{logStats.avgResponseTime}ms</p>
                <p className="text-xs text-gray-500">Genomsnitt</p>
              </div>
              <Zap className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Aktiva larm</p>
                <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{logStats.alertsActive}</p>
                <p className="text-xs text-gray-500">Kräver åtgärd</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="logs">Loggar ({filteredLogs.length})</TabsTrigger>
          <TabsTrigger value="services">Tjänster</TabsTrigger>
          <TabsTrigger value="analytics">Analys</TabsTrigger>
          <TabsTrigger value="alerts">Larm</TabsTrigger>
          <TabsTrigger value="settings">Inställningar</TabsTrigger>
        </TabsList>

        {/* Logs Tab */}
        <TabsContent value="logs" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök i loggar efter meddelande, tjänst, källa eller request ID..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                  >
                    <option value="all">Alla nivåer</option>
                    <option value="DEBUG">Debug</option>
                    <option value="INFO">Info</option>
                    <option value="WARN">Varning</option>
                    <option value="ERROR">Fel</option>
                    <option value="FATAL">Fatalt</option>
                  </select>
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedService}
                    onChange={(e) => setSelectedService(e.target.value)}
                  >
                    <option value="all">Alla tjänster</option>
                    <option value="crawler-service">Crawler Service</option>
                    <option value="api-gateway">API Gateway</option>
                    <option value="data-extractor">Data Extractor</option>
                    <option value="proxy-manager">Proxy Manager</option>
                    <option value="export-service">Export Service</option>
                  </select>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Mer filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Log List */}
          <div className="space-y-2">
            {filteredLogs.map((log) => {
              const LevelIcon = getLevelIcon(log.level);
              const ServiceIcon = getServiceIcon(log.service);
              return (
                <Card key={log.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-4">
                      {/* Level Icon */}
                      <div className={`flex-shrink-0 ${getLevelColor(log.level)}`}>
                        <LevelIcon className="h-5 w-5" />
                      </div>

                      {/* Main Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className={`${getLevelColor(log.level)}`}>
                              {log.level}
                            </Badge>
                            <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                              <ServiceIcon className="h-4 w-4" />
                              <span>{log.service}</span>
                            </div>
                            <span className="text-xs text-gray-500">{log.timestamp}</span>
                          </div>
                          <Button variant="outline" size="sm">
                            <Eye className="h-4 w-4 mr-1" />
                            Detaljer
                          </Button>
                        </div>

                        <p className="text-gray-900 dark:text-white mb-2 font-medium">{log.message}</p>

                        <div className="flex flex-wrap gap-4 text-xs text-gray-600 dark:text-gray-400">
                          <span>Källa: {log.source}</span>
                          <span>Request ID: {log.requestId}</span>
                          <span>Användare: {log.userId}</span>
                          {log.duration && <span>Tid: {formatDuration(log.duration)}</span>}
                        </div>

                        {/* Details Preview */}
                        {log.details && (
                          <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <div className="flex flex-wrap gap-4 text-xs">
                              {Object.entries(log.details).map(([key, value]) => (
                                <span key={key} className="text-gray-600 dark:text-gray-400">
                                  <strong>{key.replace(/_/g, ' ')}:</strong> {String(value)}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {filteredLogs.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="text-gray-400 dark:text-gray-600">
                  <Activity className="h-12 w-12 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Inga loggar hittades</h3>
                  <p>Försök justera dina sökkriterier</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Services Tab */}
        <TabsContent value="services" className="space-y-4">
          <div className="space-y-4">
            {serviceStats.map((service, index) => {
              const ServiceIcon = getServiceIcon(service.service);
              return (
                <Card key={index} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <ServiceIcon className="h-6 w-6 text-blue-600" />
                        <div>
                          <h3 className="font-semibold text-lg">{service.service}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {service.logs.toLocaleString()} loggar totalt
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-8">
                        <div className="text-center">
                          <p className="text-sm text-gray-500">Framgång</p>
                          <p className="text-lg font-semibold text-green-600">{service.success_rate}%</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-500">Fel</p>
                          <p className="text-lg font-semibold text-red-600">{service.errors.toLocaleString()}</p>
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-gray-500">Varningar</p>
                          <p className="text-lg font-semibold text-yellow-600">{service.warnings.toLocaleString()}</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Loggvolym över tid</CardTitle>
                <CardDescription>Antal loggar per timme</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📊 Volymdiagram: Peak 14:30 med 23,456 loggar/h
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Felnivåfördelning</CardTitle>
                <CardDescription>Fördelning av loggnivåer</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>INFO</span>
                    <span className="font-medium text-blue-600">76.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>DEBUG</span>
                    <span className="font-medium text-gray-600">18.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>WARN</span>
                    <span className="font-medium text-yellow-600">3.1%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>ERROR</span>
                    <span className="font-medium text-red-600">2.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>FATAL</span>
                    <span className="font-medium text-red-800">0.1%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Vanligaste fel</CardTitle>
                <CardDescription>Mest frekventa felmeddelanden</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Connection timeout</span>
                    <span className="font-medium">1,247</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Rate limit exceeded</span>
                    <span className="font-medium">892</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Selector not found</span>
                    <span className="font-medium">567</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Database connection failed</span>
                    <span className="font-medium">234</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Prestanda</CardTitle>
                <CardDescription>Genomsnittlig svarstid per tjänst</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">API Gateway</span>
                    <span className="font-medium">45ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Data Extractor</span>
                    <span className="font-medium">234ms</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Crawler Service</span>
                    <span className="font-medium">1.2s</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Export Service</span>
                    <span className="font-medium">3.4s</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Aktiva larm</CardTitle>
              <CardDescription>Larm som kräver uppmärksamhet</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border border-red-200 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <XCircle className="h-5 w-5 text-red-600" />
                    <div>
                      <p className="font-medium text-red-800 dark:text-red-200">Database connection pool exhausted</p>
                      <p className="text-sm text-red-600 dark:text-red-300">Critical - Service degradation</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Åtgärda
                  </Button>
                </div>

                <div className="flex items-center justify-between p-4 border border-yellow-200 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    <div>
                      <p className="font-medium text-yellow-800 dark:text-yellow-200">High error rate in crawler-service</p>
                      <p className="text-sm text-yellow-600 dark:text-yellow-300">Warning - Error rate above 5%</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Undersök
                  </Button>
                </div>

                <div className="flex items-center justify-between p-4 border border-blue-200 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="flex items-center gap-3">
                    <Info className="h-5 w-5 text-blue-600" />
                    <div>
                      <p className="font-medium text-blue-800 dark:text-blue-200">Log retention policy will trigger cleanup</p>
                      <p className="text-sm text-blue-600 dark:text-blue-300">Info - Cleanup scheduled for tonight</p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    Visa
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Logginställningar</CardTitle>
              <CardDescription>Konfigurera loggning och retention</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="font-medium">Loggnivå</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>DEBUG</option>
                    <option>INFO</option>
                    <option>WARN</option>
                    <option>ERROR</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Retention period</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>7 dagar</option>
                    <option>30 dagar</option>
                    <option>90 dagar</option>
                    <option>1 år</option>
                  </select>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Realtidslarm</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Skicka larm direkt vid kritiska fel</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Strukturerad loggning</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">JSON-format för bättre parsning</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>
              </div>

              <div className="pt-4 border-t">
                <Button>Spara inställningar</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
