import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw,
  RefreshCw, 
  Clock,
  AlertTriangle,
  CheckCircle,
  Activity,
  Zap,
  Database,
  Eye,
  MoreHorizontal,
  Filter,
  Search,
  Calendar,
  TrendingUp,
  Server
} from 'lucide-react';

interface JobStatus {
  id: string;
  name: string;
  type: 'crawl' | 'scrape' | 'analysis' | 'export';
  status: 'running' | 'queued' | 'completed' | 'failed' | 'paused';
  progress: number;
  startTime: string;
  estimatedCompletion?: string;
  itemsProcessed: number;
  totalItems: number;
  errorCount: number;
  source: string;
  template: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  owner: string;
  lastUpdate: string;
}

interface SystemMetrics {
  activeJobs: number;
  queuedJobs: number;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
  networkThroughput: number;
}

const JobControl = () => {
  const [activeTab, setActiveTab] = useState<'active' | 'queue' | 'history' | 'monitoring'>('active');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedJobs, setSelectedJobs] = useState<string[]>([]);

  const [systemMetrics] = useState<SystemMetrics>({
    activeJobs: 8,
    queuedJobs: 15,
    cpuUsage: 68,
    memoryUsage: 74,
    diskUsage: 45,
    networkThroughput: 125.7
  });

  const [jobs, setJobs] = useState<JobStatus[]>([
    {
      id: 'job_1001',
      name: 'Biluppgifter crawl - batch 1',
      type: 'crawl',
      status: 'running',
      progress: 65,
      startTime: '2024-08-21T09:30:00Z',
      estimatedCompletion: '2024-08-21T11:15:00Z',
      itemsProcessed: 3250,
      totalItems: 5000,
      errorCount: 23,
      source: 'Biluppgifter.se',
      template: 'vehicle_detail_v1',
      priority: 'high',
      owner: 'Anna Svensson',
      lastUpdate: '2024-08-21T10:45:00Z'
    },
    {
      id: 'job_1002',
      name: 'Hitta.se person scrape',
      type: 'scrape',
      status: 'running',
      progress: 23,
      startTime: '2024-08-21T08:15:00Z',
      estimatedCompletion: '2024-08-21T12:30:00Z',
      itemsProcessed: 1150,
      totalItems: 5000,
      errorCount: 8,
      source: 'Hitta.se',
      template: 'person_profile_v2',
      priority: 'normal',
      owner: 'Erik Johansson',
      lastUpdate: '2024-08-21T10:42:00Z'
    },
    {
      id: 'job_1003',
      name: 'Export till Excel - fordonsdata',
      type: 'export',
      status: 'queued',
      progress: 0,
      startTime: '2024-08-21T11:00:00Z',
      itemsProcessed: 0,
      totalItems: 12500,
      errorCount: 0,
      source: 'Datalager',
      template: 'vehicle_export_v1',
      priority: 'low',
      owner: 'Maria Andersson',
      lastUpdate: '2024-08-21T10:45:00Z'
    },
    {
      id: 'job_1004',
      name: 'Bolagsverket API sync',
      type: 'crawl',
      status: 'failed',
      progress: 15,
      startTime: '2024-08-21T06:00:00Z',
      itemsProcessed: 375,
      totalItems: 2500,
      errorCount: 156,
      source: 'Bolagsverket API',
      template: 'company_profile_v1',
      priority: 'urgent',
      owner: 'Johan Lindberg',
      lastUpdate: '2024-08-21T07:30:00Z'
    },
    {
      id: 'job_1005',
      name: 'Fastighetsdata analysis',
      type: 'analysis',
      status: 'completed',
      progress: 100,
      startTime: '2024-08-21T05:00:00Z',
      itemsProcessed: 8500,
      totalItems: 8500,
      errorCount: 12,
      source: 'Hemnet.se',
      template: 'property_analysis_v1',
      priority: 'normal',
      owner: 'Anna Svensson',
      lastUpdate: '2024-08-21T08:45:00Z'
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-success/10 text-success border-success/20';
      case 'queued':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'completed':
        return 'bg-primary/10 text-primary border-primary/20';
      case 'failed':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'paused':
        return 'bg-muted/10 text-muted-foreground border-muted/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'normal':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'low':
        return 'bg-gray-100 text-gray-700 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Activity className="w-4 h-4" />;
      case 'queued':
        return <Clock className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'crawl':
        return <Database className="w-4 h-4" />;
      case 'scrape':
        return <Zap className="w-4 h-4" />;
      case 'analysis':
        return <TrendingUp className="w-4 h-4" />;
      case 'export':
        return <Server className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getRelativeTime = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return `${Math.floor(diffMinutes / 1440)}d ago`;
  };

  const getEstimatedTimeRemaining = (job: JobStatus) => {
    if (job.status !== 'running' || job.progress === 0) return 'N/A';
    
    const elapsed = new Date().getTime() - new Date(job.startTime).getTime();
    const remaining = (elapsed / job.progress) * (100 - job.progress);
    const remainingMinutes = Math.floor(remaining / (1000 * 60));
    
    if (remainingMinutes < 60) return `${remainingMinutes}m`;
    return `${Math.floor(remainingMinutes / 60)}h ${remainingMinutes % 60}m`;
  };

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = !searchQuery || 
      job.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.source.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.template.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || job.status === statusFilter;
    const matchesType = !typeFilter || job.type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const toggleJobSelection = (jobId: string) => {
    setSelectedJobs(prev => 
      prev.includes(jobId) 
        ? prev.filter(id => id !== jobId)
        : [...prev, jobId]
    );
  };

  const renderSystemMonitoring = () => (
    <div className="space-y-6">
      {/* System Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">CPU Usage</p>
                <p className="text-2xl font-bold text-foreground">{systemMetrics.cpuUsage}%</p>
              </div>
              <div className="w-8 h-8 flex items-center justify-center">
                <Progress value={systemMetrics.cpuUsage} className="w-6 h-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Minne</p>
                <p className="text-2xl font-bold text-foreground">{systemMetrics.memoryUsage}%</p>
              </div>
              <div className="w-8 h-8 flex items-center justify-center">
                <Progress value={systemMetrics.memoryUsage} className="w-6 h-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Disk</p>
                <p className="text-2xl font-bold text-foreground">{systemMetrics.diskUsage}%</p>
              </div>
              <div className="w-8 h-8 flex items-center justify-center">
                <Progress value={systemMetrics.diskUsage} className="w-6 h-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Nätverk</p>
                <p className="text-2xl font-bold text-foreground">{systemMetrics.networkThroughput}</p>
                <p className="text-xs text-muted-foreground">MB/s</p>
              </div>
              <Activity className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-time Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="text-base">Systembelastning</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 bg-muted/20 rounded flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Realtidsdiagram för systemresurser</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="text-base">Jobbflöde</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 bg-muted/20 rounded flex items-center justify-center">
              <div className="text-center">
                <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Jobbstatistik över tid</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  const renderJobList = (jobsToShow: JobStatus[]) => (
    <div className="space-y-4">
      {jobsToShow.map((job) => (
        <Card key={job.id} className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={selectedJobs.includes(job.id)}
                  onChange={() => toggleJobSelection(job.id)}
                  className="rounded"
                />
                {getTypeIcon(job.type)}
                <div>
                  <h3 className="font-medium text-foreground">{job.name}</h3>
                  <p className="text-sm text-muted-foreground">{job.source} → {job.template}</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Badge className={getPriorityColor(job.priority)}>
                  {job.priority}
                </Badge>
                <Badge className={getStatusColor(job.status)}>
                  {getStatusIcon(job.status)}
                  <span className="ml-1">{job.status}</span>
                </Badge>
                <Button variant="ghost" size="sm">
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>
            </div>

            {job.status === 'running' && (
              <div className="mb-3">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-muted-foreground">Framsteg</span>
                  <span className="text-foreground">{job.progress}%</span>
                </div>
                <Progress value={job.progress} className="h-2" />
              </div>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground block">Items bearbetade</span>
                <span className="text-foreground font-medium">
                  {job.itemsProcessed.toLocaleString()} / {job.totalItems.toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground block">Fel</span>
                <span className={`font-medium ${job.errorCount > 0 ? 'text-destructive' : 'text-success'}`}>
                  {job.errorCount}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground block">Starttid</span>
                <span className="text-foreground">{getRelativeTime(job.startTime)}</span>
              </div>
              <div>
                <span className="text-muted-foreground block">
                  {job.status === 'running' ? 'ETA' : 'Senaste uppdatering'}
                </span>
                <span className="text-foreground">
                  {job.status === 'running' ? getEstimatedTimeRemaining(job) : getRelativeTime(job.lastUpdate)}
                </span>
              </div>
            </div>

            {job.status === 'running' && (
              <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-sidebar-border">
                <Button variant="outline" size="sm">
                  <Pause className="w-3 h-3 mr-1" />
                  Pausa
                </Button>
                <Button variant="outline" size="sm">
                  <Square className="w-3 h-3 mr-1" />
                  Stoppa
                </Button>
                <Button variant="outline" size="sm">
                  <Eye className="w-3 h-3 mr-1" />
                  Logs
                </Button>
              </div>
            )}

            {job.status === 'failed' && (
              <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-sidebar-border">
                <Button variant="outline" size="sm">
                  <RotateCcw className="w-3 h-3 mr-1" />
                  Försök igen
                </Button>
                <Button variant="outline" size="sm">
                  <Eye className="w-3 h-3 mr-1" />
                  Visa fel
                </Button>
              </div>
            )}

            {job.status === 'queued' && (
              <div className="flex items-center space-x-2 mt-3 pt-3 border-t border-sidebar-border">
                <Button variant="outline" size="sm">
                  <Play className="w-3 h-3 mr-1" />
                  Starta nu
                </Button>
                <Button variant="outline" size="sm">
                  <Square className="w-3 h-3 mr-1" />
                  Ta bort från kö
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Jobbkontroll</h1>
          <p className="text-muted-foreground">Övervaka och kontrollera pågående jobb och systemresurser</p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="bg-success/10 text-success">
            {systemMetrics.activeJobs} aktiva
          </Badge>
          <Badge variant="outline" className="bg-warning/10 text-warning">
            {systemMetrics.queuedJobs} i kö
          </Badge>
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Uppdatera
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="active">Aktiva jobb</TabsTrigger>
          <TabsTrigger value="queue">Kö</TabsTrigger>
          <TabsTrigger value="history">Historik</TabsTrigger>
          <TabsTrigger value="monitoring">Systemövervakning</TabsTrigger>
        </TabsList>

        {/* Filters for job lists */}
        {activeTab !== 'monitoring' && (
          <Card className="border-sidebar-border mt-4">
            <CardContent className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="search">Sök</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search"
                      placeholder="Sök jobb..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Status</Label>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Alla statusar" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Alla statusar</SelectItem>
                      <SelectItem value="running">Kör</SelectItem>
                      <SelectItem value="queued">I kö</SelectItem>
                      <SelectItem value="completed">Slutförd</SelectItem>
                      <SelectItem value="failed">Misslyckad</SelectItem>
                      <SelectItem value="paused">Pausad</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Typ</Label>
                  <Select value={typeFilter} onValueChange={setTypeFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="Alla typer" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Alla typer</SelectItem>
                      <SelectItem value="crawl">Crawl</SelectItem>
                      <SelectItem value="scrape">Scrape</SelectItem>
                      <SelectItem value="analysis">Analys</SelectItem>
                      <SelectItem value="export">Export</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {selectedJobs.length > 0 && (
                  <div className="space-y-2">
                    <Label>Valda jobb ({selectedJobs.length})</Label>
                    <div className="flex space-x-1">
                      <Button variant="outline" size="sm">
                        <Pause className="w-3 h-3" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Square className="w-3 h-3" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <RotateCcw className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        <TabsContent value="active" className="mt-6">
          {renderJobList(filteredJobs.filter(job => job.status === 'running'))}
        </TabsContent>

        <TabsContent value="queue" className="mt-6">
          {renderJobList(filteredJobs.filter(job => job.status === 'queued'))}
        </TabsContent>

        <TabsContent value="history" className="mt-6">
          {renderJobList(filteredJobs.filter(job => ['completed', 'failed', 'paused'].includes(job.status)))}
        </TabsContent>

        <TabsContent value="monitoring" className="mt-6">
          {renderSystemMonitoring()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default JobControl;
