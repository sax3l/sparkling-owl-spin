import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  Clock,
  Activity,
  Database,
  FileText,
  TrendingUp,
  Eye,
  Download,
  Settings,
  Zap
} from 'lucide-react';

interface JobDetails {
  id: string;
  name: string;
  status: 'running' | 'paused' | 'completed' | 'failed' | 'stopping';
  startTime: string;
  endTime?: string;
  progress: {
    current: number;
    total: number;
    percentage: number;
  };
  stats: {
    pagesProcessed: number;
    itemsExtracted: number;
    errorsCount: number;
    duplicatesSkipped: number;
    avgResponseTime: number;
    throughput: number; // pages per minute
  };
  source: {
    name: string;
    url: string;
    template: string;
  };
  currentUrl?: string;
  recentActivity: Array<{
    timestamp: string;
    type: 'info' | 'warning' | 'error';
    message: string;
    url?: string;
  }>;
}

interface LiveMetrics {
  cpu: number;
  memory: number;
  network: number;
  queueSize: number;
  activeWorkers: number;
}

const JobDetailsConsole = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'logs' | 'metrics' | 'data'>('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  // Mock job data - in real app this would come from API/WebSocket
  const [jobDetails] = useState<JobDetails>({
    id: 'job_1001',
    name: 'Biluppgifter crawl - batch 1',
    status: 'running',
    startTime: '2024-08-21T09:30:00Z',
    progress: {
      current: 3250,
      total: 5000,
      percentage: 65
    },
    stats: {
      pagesProcessed: 3250,
      itemsExtracted: 2845,
      errorsCount: 23,
      duplicatesSkipped: 156,
      avgResponseTime: 1.2,
      throughput: 45
    },
    source: {
      name: 'Biluppgifter.se',
      url: 'https://biluppgifter.se',
      template: 'vehicle_detail_v1'
    },
    currentUrl: 'https://biluppgifter.se/search?page=65',
    recentActivity: [
      {
        timestamp: '2024-08-21T10:45:12Z',
        type: 'info',
        message: 'Extraherade 15 fordon från listsida',
        url: 'https://biluppgifter.se/search?page=65'
      },
      {
        timestamp: '2024-08-21T10:45:08Z',
        type: 'warning',
        message: 'Rate limit träffad, väntar 2s',
        url: 'https://biluppgifter.se/detail/abc123'
      },
      {
        timestamp: '2024-08-21T10:45:05Z',
        type: 'error',
        message: 'Timeout vid hämtning av detaljsida',
        url: 'https://biluppgifter.se/detail/xyz789'
      },
      {
        timestamp: '2024-08-21T10:45:01Z',
        type: 'info',
        message: 'Följer paginering till nästa sida',
        url: 'https://biluppgifter.se/search?page=64'
      }
    ]
  });

  const [liveMetrics] = useState<LiveMetrics>({
    cpu: 68,
    memory: 74,
    network: 125,
    queueSize: 234,
    activeWorkers: 8
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-success/10 text-success border-success/20';
      case 'paused':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'completed':
        return 'bg-primary/10 text-primary border-primary/20';
      case 'failed':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'stopping':
        return 'bg-muted/10 text-muted-foreground border-muted/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Activity className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4" />;
      case 'stopping':
        return <Square className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getLogTypeColor = (type: string) => {
    switch (type) {
      case 'info':
        return 'text-primary';
      case 'warning':
        return 'text-warning';
      case 'error':
        return 'text-destructive';
      default:
        return 'text-muted-foreground';
    }
  };

  const formatDuration = (startTime: string, endTime?: string) => {
    const start = new Date(startTime);
    const end = endTime ? new Date(endTime) : new Date();
    const diffMs = end.getTime() - start.getTime();
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMinutes / 60);
    
    if (diffHours > 0) {
      return `${diffHours}h ${diffMinutes % 60}m`;
    }
    return `${diffMinutes}m`;
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('sv-SE');
  };

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Job Header */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Database className="w-6 h-6 text-primary" />
              <div>
                <CardTitle className="text-xl">{jobDetails.name}</CardTitle>
                <CardDescription>
                  {jobDetails.source.name} → {jobDetails.source.template}
                </CardDescription>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <Badge className={getStatusColor(jobDetails.status)}>
                {getStatusIcon(jobDetails.status)}
                <span className="ml-1 capitalize">{jobDetails.status}</span>
              </Badge>
              <div className="flex space-x-1">
                {jobDetails.status === 'running' && (
                  <>
                    <Button variant="outline" size="sm">
                      <Pause className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Square className="w-4 h-4" />
                    </Button>
                  </>
                )}
                <Button variant="outline" size="sm">
                  <RefreshCw className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Progress */}
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Framsteg</span>
                <span className="text-foreground font-medium">
                  {jobDetails.progress.current.toLocaleString()} / {jobDetails.progress.total.toLocaleString()} 
                  ({jobDetails.progress.percentage}%)
                </span>
              </div>
              <Progress value={jobDetails.progress.percentage} className="h-3" />
            </div>

            {/* Key Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground block">Starttid</span>
                <span className="text-foreground font-medium">
                  {formatTime(jobDetails.startTime)}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground block">Körtid</span>
                <span className="text-foreground font-medium">
                  {formatDuration(jobDetails.startTime, jobDetails.endTime)}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground block">Aktuell URL</span>
                <span className="text-foreground font-medium truncate block">
                  {jobDetails.currentUrl || 'N/A'}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground block">Genomströmning</span>
                <span className="text-foreground font-medium">
                  {jobDetails.stats.throughput} sidor/min
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Sidor bearbetade</p>
                <p className="text-2xl font-bold text-foreground">
                  {jobDetails.stats.pagesProcessed.toLocaleString()}
                </p>
              </div>
              <FileText className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Items extraherade</p>
                <p className="text-2xl font-bold text-foreground">
                  {jobDetails.stats.itemsExtracted.toLocaleString()}
                </p>
              </div>
              <Database className="w-8 h-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Fel</p>
                <p className="text-2xl font-bold text-foreground">
                  {jobDetails.stats.errorsCount}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-destructive" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg svarstid</p>
                <p className="text-2xl font-bold text-foreground">
                  {jobDetails.stats.avgResponseTime}s
                </p>
              </div>
              <Clock className="w-8 h-8 text-warning" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Senaste aktivitet</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {jobDetails.recentActivity.slice(0, 8).map((activity, index) => (
              <div key={index} className="flex items-start space-x-3 p-2 border border-sidebar-border rounded">
                <div className="flex-shrink-0 text-xs text-muted-foreground mt-1">
                  {formatTime(activity.timestamp)}
                </div>
                <div className="flex-1">
                  <div className={`text-sm ${getLogTypeColor(activity.type)}`}>
                    {activity.message}
                  </div>
                  {activity.url && (
                    <div className="text-xs text-muted-foreground font-mono mt-1 truncate">
                      {activity.url}
                    </div>
                  )}
                </div>
                <Badge variant={activity.type === 'error' ? 'destructive' : activity.type === 'warning' ? 'secondary' : 'outline'} className="text-xs">
                  {activity.type}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderLogs = () => (
    <div className="space-y-4">
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Live Logs</CardTitle>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Exportera
              </Button>
              <Button variant="outline" size="sm">
                <RefreshCw className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="bg-black text-green-400 font-mono text-sm p-4 rounded max-h-96 overflow-y-auto">
            {jobDetails.recentActivity.map((activity, index) => (
              <div key={index} className="mb-1">
                <span className="text-gray-500">[{formatTime(activity.timestamp)}]</span>
                <span className={`ml-2 ${
                  activity.type === 'error' ? 'text-red-400' : 
                  activity.type === 'warning' ? 'text-yellow-400' : 
                  'text-green-400'
                }`}>
                  {activity.type.toUpperCase()}
                </span>
                <span className="ml-2">{activity.message}</span>
                {activity.url && (
                  <div className="text-blue-400 ml-8">{activity.url}</div>
                )}
              </div>
            ))}
            <div className="text-green-400 animate-pulse">█</div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderMetrics = () => (
    <div className="space-y-6">
      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">CPU Användning</span>
              <span className="text-sm text-muted-foreground">{liveMetrics.cpu}%</span>
            </div>
            <Progress value={liveMetrics.cpu} className="h-2" />
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Minne</span>
              <span className="text-sm text-muted-foreground">{liveMetrics.memory}%</span>
            </div>
            <Progress value={liveMetrics.memory} className="h-2" />
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Nätverk</span>
              <span className="text-sm text-muted-foreground">{liveMetrics.network} KB/s</span>
            </div>
            <Progress value={Math.min(100, (liveMetrics.network / 500) * 100)} className="h-2" />
          </CardContent>
        </Card>
      </div>

      {/* Worker Status */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Worker Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Aktiva workers</span>
                <span className="text-sm font-medium">{liveMetrics.activeWorkers}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Kö-storlek</span>
                <span className="text-sm font-medium">{liveMetrics.queueSize}</span>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Genomsnittlig latens</span>
                <span className="text-sm font-medium">{jobDetails.stats.avgResponseTime}s</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Duplicates skippade</span>
                <span className="text-sm font-medium">{jobDetails.stats.duplicatesSkipped}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Chart Placeholder */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Prestanda över tid</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-muted/20 rounded flex items-center justify-center">
            <div className="text-center">
              <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">Realtidsdiagram för genomströmning och latens</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderData = () => (
    <div className="space-y-4">
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Senast extraherad data</CardTitle>
            <Button variant="outline" size="sm">
              <Eye className="w-4 h-4 mr-2" />
              Visa alla
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {/* Sample extracted data */}
            {[
              { id: 'it_123456', reg_number: 'ABC123', make: 'Volvo', model: 'XC90', year: 2022 },
              { id: 'it_123457', reg_number: 'DEF456', make: 'BMW', model: 'X5', year: 2021 },
              { id: 'it_123458', reg_number: 'GHI789', make: 'Audi', model: 'Q7', year: 2023 }
            ].map((item, index) => (
              <div key={index} className="border border-sidebar-border rounded p-3">
                <div className="flex items-center justify-between mb-2">
                  <Badge variant="outline">{item.id}</Badge>
                  <span className="text-xs text-muted-foreground">
                    {formatTime(new Date(Date.now() - index * 30000).toISOString())}
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Reg:</span>
                    <span className="ml-1 font-mono">{item.reg_number}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Märke:</span>
                    <span className="ml-1">{item.make}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Modell:</span>
                    <span className="ml-1">{item.model}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">År:</span>
                    <span className="ml-1">{item.year}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Jobbdetaljer</h1>
          <p className="text-muted-foreground">Live-övervakning av pågående jobb</p>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="autoRefresh"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            <label htmlFor="autoRefresh" className="text-sm text-muted-foreground">
              Auto-uppdatera
            </label>
          </div>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="overview">Översikt</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="metrics">Metrics</TabsTrigger>
          <TabsTrigger value="data">Data</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          {renderOverview()}
        </TabsContent>

        <TabsContent value="logs" className="mt-6">
          {renderLogs()}
        </TabsContent>

        <TabsContent value="metrics" className="mt-6">
          {renderMetrics()}
        </TabsContent>

        <TabsContent value="data" className="mt-6">
          {renderData()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default JobDetailsConsole;
