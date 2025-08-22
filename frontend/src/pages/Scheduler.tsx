import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { 
  Clock,
  Calendar,
  Bell,
  Play,
  Pause,
  Square,
  Settings,
  Plus,
  Edit,
  Trash2,
  Copy,
  Activity,
  AlertTriangle,
  CheckCircle,
  Mail,
  Smartphone,
  Slack,
  Globe,
  Webhook,
  RefreshCw,
  Timer,
  Users,
  Target,
  Zap,
  FileText,
  Eye
} from 'lucide-react';

interface ScheduledJob {
  id: string;
  name: string;
  description: string;
  cronExpression: string;
  nextRun: string;
  lastRun?: string;
  status: 'active' | 'paused' | 'disabled';
  projectId: string;
  projectName: string;
  template: string;
  notifications: {
    onSuccess: boolean;
    onFailure: boolean;
    onTimeout: boolean;
    channels: string[];
  };
  retryPolicy: {
    enabled: boolean;
    maxAttempts: number;
    backoffStrategy: 'linear' | 'exponential';
    initialDelay: number;
  };
  timeouts: {
    jobTimeout: number;
    requestTimeout: number;
    queueTimeout: number;
  };
  executions: {
    total: number;
    successful: number;
    failed: number;
    lastSuccess?: string;
    lastFailure?: string;
  };
}

interface NotificationChannel {
  id: string;
  name: string;
  type: 'email' | 'slack' | 'webhook' | 'sms';
  config: Record<string, any>;
  status: 'active' | 'disabled' | 'error';
  lastUsed?: string;
}

interface Alert {
  id: string;
  type: 'success' | 'warning' | 'error' | 'info';
  title: string;
  message: string;
  timestamp: string;
  jobId?: string;
  read: boolean;
}

const Scheduler = () => {
  const [activeTab, setActiveTab] = useState<'jobs' | 'notifications' | 'alerts' | 'config'>('jobs');
  const [selectedJob, setSelectedJob] = useState<ScheduledJob | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);

  // Mock data
  const [scheduledJobs] = useState<ScheduledJob[]>([
    {
      id: 'sched_001',
      name: 'Daglig produktuppdatering',
      description: 'Crawlar produktkatalog varje dag kl 06:00',
      cronExpression: '0 6 * * *',
      nextRun: '2024-12-19T06:00:00Z',
      lastRun: '2024-12-18T06:00:00Z',
      status: 'active',
      projectId: 'proj_001',
      projectName: 'E-commerce Monitor',
      template: 'product_catalog_v2',
      notifications: {
        onSuccess: true,
        onFailure: true,
        onTimeout: true,
        channels: ['email_ops', 'slack_alerts']
      },
      retryPolicy: {
        enabled: true,
        maxAttempts: 3,
        backoffStrategy: 'exponential',
        initialDelay: 300
      },
      timeouts: {
        jobTimeout: 3600,
        requestTimeout: 30,
        queueTimeout: 600
      },
      executions: {
        total: 45,
        successful: 42,
        failed: 3,
        lastSuccess: '2024-12-18T06:15:32Z',
        lastFailure: '2024-12-15T06:02:15Z'
      }
    },
    {
      id: 'sched_002',
      name: 'Veckotrendanalys',
      description: 'Samlar trenddata varje måndag',
      cronExpression: '0 8 * * 1',
      nextRun: '2024-12-23T08:00:00Z',
      lastRun: '2024-12-16T08:00:00Z',
      status: 'active',
      projectId: 'proj_002',
      projectName: 'Market Research',
      template: 'trend_analysis_v1',
      notifications: {
        onSuccess: false,
        onFailure: true,
        onTimeout: true,
        channels: ['email_team']
      },
      retryPolicy: {
        enabled: true,
        maxAttempts: 2,
        backoffStrategy: 'linear',
        initialDelay: 600
      },
      timeouts: {
        jobTimeout: 7200,
        requestTimeout: 45,
        queueTimeout: 900
      },
      executions: {
        total: 12,
        successful: 11,
        failed: 1,
        lastSuccess: '2024-12-16T08:45:21Z',
        lastFailure: '2024-11-25T08:15:33Z'
      }
    }
  ]);

  const [notificationChannels] = useState<NotificationChannel[]>([
    {
      id: 'email_ops',
      name: 'Operations Team Email',
      type: 'email',
      config: {
        recipients: ['ops@example.com', 'alerts@example.com'],
        subject: 'ECaDP Alert: {{type}} - {{job}}'
      },
      status: 'active',
      lastUsed: '2024-12-18T06:15:45Z'
    },
    {
      id: 'slack_alerts',
      name: 'Slack #crawler-alerts',
      type: 'slack',
      config: {
        webhook: 'https://hooks.slack.com/services/...',
        channel: '#crawler-alerts',
        username: 'ECaDP Bot'
      },
      status: 'active',
      lastUsed: '2024-12-18T06:15:48Z'
    },
    {
      id: 'webhook_monitoring',
      name: 'External Monitoring',
      type: 'webhook',
      config: {
        url: 'https://monitoring.example.com/webhook',
        method: 'POST',
        headers: {
          'Authorization': 'Bearer xxx'
        }
      },
      status: 'disabled'
    }
  ]);

  // Generate mock alerts
  useEffect(() => {
    const mockAlerts: Alert[] = [
      {
        id: 'alert_001',
        type: 'success',
        title: 'Schemalagt jobb slutfört',
        message: 'Daglig produktuppdatering slutfördes framgångsrikt (642 sidor crawlade)',
        timestamp: '2024-12-18T06:15:32Z',
        jobId: 'sched_001',
        read: false
      },
      {
        id: 'alert_002',
        type: 'warning',
        title: 'Jobb tog längre tid än förväntat',
        message: 'Veckotrendanalys tog 2.5h att slutföra (normalt 1.5h)',
        timestamp: '2024-12-16T10:30:15Z',
        jobId: 'sched_002',
        read: true
      },
      {
        id: 'alert_003',
        type: 'error',
        title: 'Schemalagt jobb misslyckades',
        message: 'Daglig produktuppdatering misslyckades efter 3 försök (timeout)',
        timestamp: '2024-12-15T06:02:15Z',
        jobId: 'sched_001',
        read: true
      }
    ];
    setAlerts(mockAlerts);
  }, []);

  const formatCron = (cronExpression: string) => {
    const descriptions: Record<string, string> = {
      '0 6 * * *': 'Varje dag kl 06:00',
      '0 8 * * 1': 'Varje måndag kl 08:00',
      '0 */6 * * *': 'Var 6:e timme',
      '0 0 1 * *': 'Första dagen varje månad'
    };
    return descriptions[cronExpression] || cronExpression;
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('sv-SE');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success/10 text-success border-success/20';
      case 'paused':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'disabled':
        return 'bg-muted/10 text-muted-foreground border-muted/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Play className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      case 'disabled':
        return <Square className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-destructive" />;
      default:
        return <Bell className="w-4 h-4 text-primary" />;
    }
  };

  const getChannelIcon = (type: string) => {
    switch (type) {
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'slack':
        return <Slack className="w-4 h-4" />;
      case 'sms':
        return <Smartphone className="w-4 h-4" />;
      case 'webhook':
        return <Webhook className="w-4 h-4" />;
      default:
        return <Bell className="w-4 h-4" />;
    }
  };

  const renderScheduledJobs = () => (
    <div className="space-y-6">
      {/* Controls */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Nytt schemalagt jobb
              </Button>
              <Button variant="outline">
                <Copy className="w-4 h-4 mr-2" />
                Klona befintligt
              </Button>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline">
                <RefreshCw className="w-4 h-4 mr-2" />
                Uppdatera status
              </Button>
              <Button variant="outline">
                <Calendar className="w-4 h-4 mr-2" />
                Visa kalender
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Job List */}
      <div className="space-y-4">
        {scheduledJobs.map((job) => (
          <Card key={job.id} className="border-sidebar-border">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <Clock className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">{job.name}</h3>
                    <Badge className={getStatusColor(job.status)}>
                      {getStatusIcon(job.status)}
                      <span className="ml-1 capitalize">{job.status}</span>
                    </Badge>
                  </div>

                  <p className="text-muted-foreground mb-4">{job.description}</p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                    <div>
                      <span className="text-muted-foreground block">Schema</span>
                      <span className="font-medium">{formatCron(job.cronExpression)}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Nästa körning</span>
                      <span className="font-medium">{formatDate(job.nextRun)}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Projekt</span>
                      <span className="font-medium">{job.projectName}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Framgångsgrad</span>
                      <span className="font-medium">
                        {Math.round((job.executions.successful / job.executions.total) * 100)}%
                      </span>
                    </div>
                  </div>

                  {/* Execution Stats */}
                  <div className="grid grid-cols-3 gap-4 text-xs">
                    <div className="text-center p-2 bg-success/5 border border-success/20 rounded">
                      <div className="font-semibold text-success">{job.executions.successful}</div>
                      <div className="text-muted-foreground">Lyckade</div>
                    </div>
                    <div className="text-center p-2 bg-destructive/5 border border-destructive/20 rounded">
                      <div className="font-semibold text-destructive">{job.executions.failed}</div>
                      <div className="text-muted-foreground">Misslyckade</div>
                    </div>
                    <div className="text-center p-2 bg-muted/5 border border-muted/20 rounded">
                      <div className="font-semibold">{job.executions.total}</div>
                      <div className="text-muted-foreground">Totalt</div>
                    </div>
                  </div>

                  {/* Quick Info */}
                  <div className="mt-4 flex items-center space-x-4 text-xs text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <Bell className="w-3 h-3" />
                      <span>{job.notifications.channels.length} notifikationer</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <RefreshCw className="w-3 h-3" />
                      <span>Max {job.retryPolicy.maxAttempts} försök</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Timer className="w-3 h-3" />
                      <span>{job.timeouts.jobTimeout}s timeout</span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <Button 
                    size="sm" 
                    variant={job.status === 'active' ? 'outline' : 'default'}
                  >
                    {job.status === 'active' ? (
                      <>
                        <Pause className="w-4 h-4 mr-2" />
                        Pausa
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Starta
                      </>
                    )}
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setSelectedJob(job)}
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Copy className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderNotifications = () => (
    <div className="space-y-6">
      {/* Channel Management */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Notifikationskanaler</CardTitle>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              Ny kanal
            </Button>
          </div>
          <CardDescription>
            Konfigurera hur notifikationer skickas för schemalagda jobb
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {notificationChannels.map((channel) => (
              <div key={channel.id} className="border border-sidebar-border rounded p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getChannelIcon(channel.type)}
                    <div>
                      <h4 className="font-medium">{channel.name}</h4>
                      <p className="text-sm text-muted-foreground capitalize">{channel.type}</p>
                    </div>
                    <Badge className={getStatusColor(channel.status)}>
                      {channel.status}
                    </Badge>
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      <Edit className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Zap className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
                {channel.lastUsed && (
                  <div className="mt-2 text-xs text-muted-foreground">
                    Senast använd: {formatDate(channel.lastUsed)}
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Global Notification Settings */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Globala notifikationsinställningar</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <Label>Aktivera notifikationer</Label>
              <p className="text-sm text-muted-foreground">Master-switch för alla notifikationer</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Sammanställ liknande alerts</Label>
              <p className="text-sm text-muted-foreground">Gruppera flera alerts av samma typ</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Nattläge (22:00-07:00)</Label>
              <p className="text-sm text-muted-foreground">Skicka endast kritiska alerts nattetid</p>
            </div>
            <Switch />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderAlerts = () => (
    <div className="space-y-6">
      {/* Alert Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-foreground">{alerts.filter(a => !a.read).length}</div>
            <div className="text-sm text-muted-foreground">Olästa alerts</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">{alerts.filter(a => a.type === 'success').length}</div>
            <div className="text-sm text-muted-foreground">Lyckade jobb</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-warning">{alerts.filter(a => a.type === 'warning').length}</div>
            <div className="text-sm text-muted-foreground">Varningar</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-destructive">{alerts.filter(a => a.type === 'error').length}</div>
            <div className="text-sm text-muted-foreground">Fel</div>
          </CardContent>
        </Card>
      </div>

      {/* Alert List */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Senaste alerts</CardTitle>
            <Button variant="outline" size="sm">
              Markera alla som lästa
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div 
                key={alert.id} 
                className={`border rounded p-4 ${alert.read ? 'opacity-60' : ''} ${
                  alert.type === 'error' ? 'border-destructive/20 bg-destructive/5' :
                  alert.type === 'warning' ? 'border-warning/20 bg-warning/5' :
                  alert.type === 'success' ? 'border-success/20 bg-success/5' :
                  'border-sidebar-border'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    {getAlertIcon(alert.type)}
                    <div className="flex-1">
                      <h4 className="font-medium">{alert.title}</h4>
                      <p className="text-sm text-muted-foreground mt-1">{alert.message}</p>
                      <div className="flex items-center space-x-2 mt-2 text-xs text-muted-foreground">
                        <span>{formatDate(alert.timestamp)}</span>
                        {alert.jobId && (
                          <Badge variant="outline" className="text-xs">
                            {scheduledJobs.find(j => j.id === alert.jobId)?.name || alert.jobId}
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                  {!alert.read && (
                    <Badge variant="secondary" className="text-xs">
                      Ny
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderConfig = () => (
    <div className="space-y-6">
      {/* Scheduler Configuration */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Scheduler-konfiguration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Max samtidiga jobb</Label>
              <Input type="number" defaultValue="5" />
            </div>
            <div className="space-y-2">
              <Label>Jobb-timeout (sekunder)</Label>
              <Input type="number" defaultValue="3600" />
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Retry-delay (sekunder)</Label>
              <Input type="number" defaultValue="300" />
            </div>
            <div className="space-y-2">
              <Label>Cleanup-intervall (timmar)</Label>
              <Input type="number" defaultValue="24" />
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Aktivera automatisk cleanup</Label>
              <p className="text-sm text-muted-foreground">Ta bort gamla jobb-loggar automatiskt</p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* Time Zone Settings */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Tidszon & Kalender</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Standard tidszon</Label>
            <Select defaultValue="europe/stockholm">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="europe/stockholm">Europe/Stockholm (CET/CEST)</SelectItem>
                <SelectItem value="utc">UTC</SelectItem>
                <SelectItem value="europe/london">Europe/London (GMT/BST)</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Respektera svenska helger</Label>
              <p className="text-sm text-muted-foreground">Pausa automatiskt under helger</p>
            </div>
            <Switch />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Sommartid-justering</Label>
              <p className="text-sm text-muted-foreground">Automatisk justering för DST</p>
            </div>
            <Switch defaultChecked />
          </div>
        </CardContent>
      </Card>

      {/* Monitoring Integration */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Monitoring & Logging</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Log-nivå för scheduler</Label>
            <Select defaultValue="info">
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="debug">Debug</SelectItem>
                <SelectItem value="info">Info</SelectItem>
                <SelectItem value="warn">Warning</SelectItem>
                <SelectItem value="error">Error</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Exportera metrics till Prometheus</Label>
              <p className="text-sm text-muted-foreground">Aktivera metrics-export</p>
            </div>
            <Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <Label>Detaljerad jobb-profiling</Label>
              <p className="text-sm text-muted-foreground">Spara utökad prestanda-data</p>
            </div>
            <Switch />
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Scheduler & Aviseringar</h1>
          <p className="text-muted-foreground">Hantera schemalagda jobb och notifikationer</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Calendar className="w-4 h-4 mr-2" />
            Visa kalender
          </Button>
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            Exportera schema
          </Button>
          <Button variant="outline">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="jobs">
            <Clock className="w-4 h-4 mr-2" />
            Schemalagda jobb
          </TabsTrigger>
          <TabsTrigger value="notifications">
            <Bell className="w-4 h-4 mr-2" />
            Notifikationer
          </TabsTrigger>
          <TabsTrigger value="alerts">
            <Activity className="w-4 h-4 mr-2" />
            Alerts ({alerts.filter(a => !a.read).length})
          </TabsTrigger>
          <TabsTrigger value="config">
            <Settings className="w-4 h-4 mr-2" />
            Konfiguration
          </TabsTrigger>
        </TabsList>

        <TabsContent value="jobs" className="mt-6">
          {renderScheduledJobs()}
        </TabsContent>

        <TabsContent value="notifications" className="mt-6">
          {renderNotifications()}
        </TabsContent>

        <TabsContent value="alerts" className="mt-6">
          {renderAlerts()}
        </TabsContent>

        <TabsContent value="config" className="mt-6">
          {renderConfig()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Scheduler;
