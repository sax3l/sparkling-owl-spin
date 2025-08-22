import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Shield,
  Activity,
  User,
  Settings,
  Database,
  Lock,
  Eye,
  Download,
  Filter,
  Search,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Play,
  Pause,
  Edit,
  Trash2,
  FileText,
  Globe,
  Users,
  Key,
  RefreshCw,
  Archive,
  ExternalLink,
  Server,
  Network,
  Zap
} from 'lucide-react';

interface AuditEvent {
  id: string;
  timestamp: string;
  category: 'auth' | 'data' | 'system' | 'job' | 'admin' | 'api' | 'security';
  action: string;
  resource: string;
  user: {
    id: string;
    name: string;
    email: string;
    role: string;
  };
  details: Record<string, any>;
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'success' | 'failure' | 'warning';
  ipAddress: string;
  userAgent?: string;
  sessionId: string;
  changes?: {
    before?: any;
    after?: any;
    fields?: string[];
  };
}

interface SecurityEvent {
  id: string;
  timestamp: string;
  type: 'login_failure' | 'suspicious_activity' | 'privilege_escalation' | 'data_access' | 'policy_violation';
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  user?: {
    id: string;
    name: string;
    email: string;
  };
  ipAddress: string;
  location?: string;
  resolved: boolean;
  assignedTo?: string;
}

const AuditLog = () => {
  const [activeTab, setActiveTab] = useState<'events' | 'security' | 'compliance' | 'reports'>('events');
  const [filters, setFilters] = useState({
    category: 'all',
    severity: 'all',
    dateRange: '7d',
    user: 'all'
  });
  const [searchTerm, setSearchTerm] = useState('');

  // Mock audit events
  const [auditEvents] = useState<AuditEvent[]>([
    {
      id: 'audit_001',
      timestamp: '2024-12-18T14:30:25Z',
      category: 'job',
      action: 'job_started',
      resource: 'crawl_job_prod_001',
      user: {
        id: 'user_001',
        name: 'Anna Andersson',
        email: 'anna@example.com',
        role: 'operator'
      },
      details: {
        jobName: 'Daglig produktuppdatering',
        projectId: 'proj_001',
        scheduledBy: 'scheduler',
        estimatedDuration: '45m'
      },
      severity: 'low',
      status: 'success',
      ipAddress: '192.168.1.100',
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      sessionId: 'sess_12345'
    },
    {
      id: 'audit_002',
      timestamp: '2024-12-18T13:45:12Z',
      category: 'admin',
      action: 'user_role_changed',
      resource: 'user_management',
      user: {
        id: 'user_admin',
        name: 'Erik Svensson',
        email: 'erik@example.com',
        role: 'admin'
      },
      details: {
        targetUser: 'maja@example.com',
        previousRole: 'viewer',
        newRole: 'operator',
        reason: 'Promoted to operator role for Q1 project'
      },
      severity: 'medium',
      status: 'success',
      ipAddress: '192.168.1.101',
      sessionId: 'sess_67890',
      changes: {
        before: { role: 'viewer', permissions: ['read'] },
        after: { role: 'operator', permissions: ['read', 'execute', 'create'] },
        fields: ['role', 'permissions']
      }
    },
    {
      id: 'audit_003',
      timestamp: '2024-12-18T12:15:33Z',
      category: 'security',
      action: 'failed_login_attempt',
      resource: 'authentication',
      user: {
        id: 'unknown',
        name: 'Unknown',
        email: 'test@hacker.com',
        role: 'none'
      },
      details: {
        attemptedEmail: 'admin@example.com',
        failureReason: 'Invalid password',
        consecutiveFailures: 3,
        sourceCountry: 'Unknown'
      },
      severity: 'high',
      status: 'failure',
      ipAddress: '45.123.456.789',
      sessionId: 'sess_unknown'
    },
    {
      id: 'audit_004',
      timestamp: '2024-12-18T11:30:45Z',
      category: 'data',
      action: 'data_export',
      resource: 'export_service',
      user: {
        id: 'user_002',
        name: 'Maja Karlsson',
        email: 'maja@example.com',
        role: 'analyst'
      },
      details: {
        exportType: 'csv',
        recordCount: 15420,
        projectId: 'proj_002',
        fileSize: '2.3MB',
        retentionPeriod: '30 days'
      },
      severity: 'medium',
      status: 'success',
      ipAddress: '192.168.1.102',
      sessionId: 'sess_13579'
    },
    {
      id: 'audit_005',
      timestamp: '2024-12-18T10:00:12Z',
      category: 'system',
      action: 'configuration_updated',
      resource: 'system_config',
      user: {
        id: 'user_admin',
        name: 'Erik Svensson',
        email: 'erik@example.com',
        role: 'admin'
      },
      details: {
        configSection: 'rate_limiting',
        component: 'crawler_engine',
        previousValue: '5 req/s',
        newValue: '7 req/s'
      },
      severity: 'medium',
      status: 'success',
      ipAddress: '192.168.1.101',
      sessionId: 'sess_67890',
      changes: {
        before: { maxRequestsPerSecond: 5 },
        after: { maxRequestsPerSecond: 7 },
        fields: ['maxRequestsPerSecond']
      }
    }
  ]);

  // Mock security events
  const [securityEvents] = useState<SecurityEvent[]>([
    {
      id: 'sec_001',
      timestamp: '2024-12-18T12:15:33Z',
      type: 'login_failure',
      description: 'Flera misslyckade inloggningsförsök från samma IP-adress',
      severity: 'high',
      user: {
        id: 'unknown',
        name: 'Unknown',
        email: 'test@hacker.com'
      },
      ipAddress: '45.123.456.789',
      location: 'Unknown',
      resolved: false
    },
    {
      id: 'sec_002',
      timestamp: '2024-12-18T09:30:15Z',
      type: 'suspicious_activity',
      description: 'Ovanligt stort antal API-anrop under kort tid',
      severity: 'medium',
      user: {
        id: 'user_003',
        name: 'Lars Pettersson',
        email: 'lars@example.com'
      },
      ipAddress: '192.168.1.103',
      location: 'Stockholm, Sweden',
      resolved: true,
      assignedTo: 'security@example.com'
    }
  ]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'auth':
        return <Lock className="w-4 h-4" />;
      case 'data':
        return <Database className="w-4 h-4" />;
      case 'system':
        return <Server className="w-4 h-4" />;
      case 'job':
        return <Play className="w-4 h-4" />;
      case 'admin':
        return <Settings className="w-4 h-4" />;
      case 'api':
        return <Network className="w-4 h-4" />;
      case 'security':
        return <Shield className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'auth':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'data':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'system':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'job':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'admin':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'api':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'security':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-success" />;
      case 'failure':
        return <XCircle className="w-4 h-4 text-destructive" />;
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-warning" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('sv-SE');
  };

  const renderAuditEvents = () => (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="space-y-2">
              <Label>Kategori</Label>
              <Select value={filters.category} onValueChange={(value) => setFilters({...filters, category: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alla kategorier</SelectItem>
                  <SelectItem value="auth">Autentisering</SelectItem>
                  <SelectItem value="data">Data</SelectItem>
                  <SelectItem value="system">System</SelectItem>
                  <SelectItem value="job">Jobb</SelectItem>
                  <SelectItem value="admin">Administration</SelectItem>
                  <SelectItem value="api">API</SelectItem>
                  <SelectItem value="security">Säkerhet</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Allvarlighetsgrad</Label>
              <Select value={filters.severity} onValueChange={(value) => setFilters({...filters, severity: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Alla nivåer</SelectItem>
                  <SelectItem value="critical">Kritisk</SelectItem>
                  <SelectItem value="high">Hög</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Låg</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Tidsperiod</Label>
              <Select value={filters.dateRange} onValueChange={(value) => setFilters({...filters, dateRange: value})}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1h">Senaste timmen</SelectItem>
                  <SelectItem value="24h">Senaste 24h</SelectItem>
                  <SelectItem value="7d">Senaste 7 dagarna</SelectItem>
                  <SelectItem value="30d">Senaste 30 dagarna</SelectItem>
                  <SelectItem value="custom">Anpassat</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Sök</Label>
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Sök i händelser..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div className="flex items-end space-x-2">
              <Button variant="outline">
                <Filter className="w-4 h-4 mr-2" />
                Filtrera
              </Button>
              <Button variant="outline">
                <Download className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Event List */}
      <div className="space-y-3">
        {auditEvents.map((event) => (
          <Card key={event.id} className="border-sidebar-border">
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="flex flex-col items-center space-y-1">
                    {getStatusIcon(event.status)}
                    <div className="w-px h-8 bg-sidebar-border"></div>
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge className={getCategoryColor(event.category)}>
                        {getCategoryIcon(event.category)}
                        <span className="ml-1 capitalize">{event.category}</span>
                      </Badge>
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {formatDate(event.timestamp)}
                      </span>
                    </div>

                    <h4 className="font-medium mb-1">{event.action.replace(/_/g, ' ')}</h4>
                    <p className="text-sm text-muted-foreground mb-2">
                      Resurs: {event.resource}
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Användare:</span>
                        <div className="font-medium">{event.user.name}</div>
                        <div className="text-xs text-muted-foreground">{event.user.email}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">IP-adress:</span>
                        <div className="font-medium">{event.ipAddress}</div>
                        {event.userAgent && (
                          <div className="text-xs text-muted-foreground truncate max-w-40">
                            {event.userAgent.split(' ')[0]}
                          </div>
                        )}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Session ID:</span>
                        <div className="font-medium font-mono text-xs">{event.sessionId}</div>
                      </div>
                    </div>

                    {/* Event Details */}
                    {Object.keys(event.details).length > 0 && (
                      <div className="mt-3 p-3 bg-muted/50 rounded border">
                        <div className="text-xs font-medium text-muted-foreground mb-2">Detaljer:</div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                          {Object.entries(event.details).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-muted-foreground">{key}:</span>
                              <span className="ml-1 font-medium">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Changes */}
                    {event.changes && (
                      <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
                        <div className="text-xs font-medium text-blue-800 mb-2">Ändringar:</div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          {event.changes.before && (
                            <div>
                              <div className="text-muted-foreground mb-1">Före:</div>
                              <pre className="bg-white p-2 rounded border text-xs overflow-x-auto">
                                {JSON.stringify(event.changes.before, null, 2)}
                              </pre>
                            </div>
                          )}
                          {event.changes.after && (
                            <div>
                              <div className="text-muted-foreground mb-1">Efter:</div>
                              <pre className="bg-white p-2 rounded border text-xs overflow-x-auto">
                                {JSON.stringify(event.changes.after, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex space-x-2 ml-4">
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderSecurityEvents = () => (
    <div className="space-y-6">
      {/* Security Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-destructive">{securityEvents.filter(e => e.severity === 'critical' || e.severity === 'high').length}</div>
            <div className="text-sm text-muted-foreground">Kritiska hotelser</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-warning">{securityEvents.filter(e => !e.resolved).length}</div>
            <div className="text-sm text-muted-foreground">Olösta händelser</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-foreground">{securityEvents.length}</div>
            <div className="text-sm text-muted-foreground">Total händelser</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">{Math.round((securityEvents.filter(e => e.resolved).length / securityEvents.length) * 100)}%</div>
            <div className="text-sm text-muted-foreground">Lösta händelser</div>
          </CardContent>
        </Card>
      </div>

      {/* Security Events List */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Säkerhetshändelser</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {securityEvents.map((event) => (
              <div 
                key={event.id} 
                className={`border rounded p-4 ${
                  event.severity === 'critical' ? 'border-destructive bg-destructive/5' :
                  event.severity === 'high' ? 'border-orange-500 bg-orange-50' :
                  'border-sidebar-border'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Badge className={getSeverityColor(event.severity)}>
                        {event.severity}
                      </Badge>
                      <Badge variant="outline">
                        {event.type.replace(/_/g, ' ')}
                      </Badge>
                      {event.resolved ? (
                        <Badge className="bg-success/10 text-success border-success/20">
                          Löst
                        </Badge>
                      ) : (
                        <Badge className="bg-destructive/10 text-destructive border-destructive/20">
                          Olöst
                        </Badge>
                      )}
                    </div>

                    <h4 className="font-medium mb-2">{event.description}</h4>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Tidpunkt:</span>
                        <div className="font-medium">{formatDate(event.timestamp)}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">IP-adress:</span>
                        <div className="font-medium">{event.ipAddress}</div>
                        {event.location && (
                          <div className="text-xs text-muted-foreground">{event.location}</div>
                        )}
                      </div>
                      <div>
                        <span className="text-muted-foreground">Användare:</span>
                        {event.user ? (
                          <div>
                            <div className="font-medium">{event.user.name}</div>
                            <div className="text-xs text-muted-foreground">{event.user.email}</div>
                          </div>
                        ) : (
                          <div className="text-muted-foreground">Okänd</div>
                        )}
                      </div>
                    </div>

                    {event.assignedTo && (
                      <div className="mt-2 text-sm">
                        <span className="text-muted-foreground">Tilldelad till:</span>
                        <span className="ml-1 font-medium">{event.assignedTo}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col space-y-2 ml-4">
                    {!event.resolved && (
                      <Button size="sm">
                        Markera som löst
                      </Button>
                    )}
                    <Button variant="outline" size="sm">
                      <Eye className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Users className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderCompliance = () => (
    <div className="space-y-6">
      {/* Compliance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">98%</div>
            <div className="text-sm text-muted-foreground">GDPR Compliance</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">95%</div>
            <div className="text-sm text-muted-foreground">Audit Coverage</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-foreground">30</div>
            <div className="text-sm text-muted-foreground">Dagar retention</div>
          </CardContent>
        </Card>
      </div>

      {/* Compliance Checks */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Compliance-kontroller</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-success" />
                <div>
                  <div className="font-medium">GDPR Article 30 - Behandlingsregister</div>
                  <div className="text-sm text-muted-foreground">Alla databehandlingar dokumenterade</div>
                </div>
              </div>
              <Badge className="bg-success/10 text-success border-success/20">
                Uppfyllt
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-success" />
                <div>
                  <div className="font-medium">Rättighetsutövning</div>
                  <div className="text-sm text-muted-foreground">Alla förfrågningar hanterade inom 30 dagar</div>
                </div>
              </div>
              <Badge className="bg-success/10 text-success border-success/20">
                Uppfyllt
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-5 h-5 text-warning" />
                <div>
                  <div className="font-medium">Datakvalitetskontroller</div>
                  <div className="text-sm text-muted-foreground">2 projekt saknar automatiska kvalitetskontroller</div>
                </div>
              </div>
              <Badge className="bg-warning/10 text-warning border-warning/20">
                Åtgärd krävs
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-5 h-5 text-success" />
                <div>
                  <div className="font-medium">Säkerhetsloggning</div>
                  <div className="text-sm text-muted-foreground">Alla säkerhetshändelser loggade och övervakade</div>
                </div>
              </div>
              <Badge className="bg-success/10 text-success border-success/20">
                Uppfyllt
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Retention */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Datalagring & Retention</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Audit logs retention</Label>
                <Select defaultValue="365d">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30d">30 dagar</SelectItem>
                    <SelectItem value="90d">90 dagar</SelectItem>
                    <SelectItem value="365d">1 år</SelectItem>
                    <SelectItem value="2y">2 år</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Crawlad data retention</Label>
                <Select defaultValue="90d">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30d">30 dagar</SelectItem>
                    <SelectItem value="90d">90 dagar</SelectItem>
                    <SelectItem value="365d">1 år</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Automatisk arkivering</Label>
                <p className="text-sm text-muted-foreground">Flytta gamla data till arkivlagring</p>
              </div>
              <Checkbox defaultChecked />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderReports = () => (
    <div className="space-y-6">
      {/* Report Generation */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Generera audit-rapport</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Rapporttyp</Label>
              <Select defaultValue="full">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="full">Fullständig audit-rapport</SelectItem>
                  <SelectItem value="security">Säkerhetsrapport</SelectItem>
                  <SelectItem value="compliance">Compliance-rapport</SelectItem>
                  <SelectItem value="user_activity">Användaraktivitet</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Tidsperiod</Label>
              <Select defaultValue="30d">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">Senaste 7 dagarna</SelectItem>
                  <SelectItem value="30d">Senaste 30 dagarna</SelectItem>
                  <SelectItem value="90d">Senaste 90 dagarna</SelectItem>
                  <SelectItem value="365d">Senaste året</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button>
              <FileText className="w-4 h-4 mr-2" />
              Generera rapport
            </Button>
            <Button variant="outline">
              <Download className="w-4 h-4 mr-2" />
              Ladda ner som PDF
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Scheduled Reports */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Schemalagda rapporter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-primary" />
                <div>
                  <div className="font-medium">Veckovis säkerhetsrapport</div>
                  <div className="text-sm text-muted-foreground">Varje måndag kl 08:00</div>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Pause className="w-4 h-4" />
                </Button>
              </div>
            </div>

            <div className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center space-x-3">
                <Calendar className="w-5 h-5 text-primary" />
                <div>
                  <div className="font-medium">Månatlig compliance-rapport</div>
                  <div className="text-sm text-muted-foreground">Första vardagen varje månad</div>
                </div>
              </div>
              <div className="flex space-x-2">
                <Button variant="outline" size="sm">
                  <Edit className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Pause className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Audit & Händelseloggar</h1>
          <p className="text-muted-foreground">Spåra och övervaka alla systemhändelser</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Archive className="w-4 h-4 mr-2" />
            Arkivera gamla loggar
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Exportera
          </Button>
          <Button variant="outline">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="events">
            <Activity className="w-4 h-4 mr-2" />
            Audit Events
          </TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="w-4 h-4 mr-2" />
            Säkerhetshändelser
          </TabsTrigger>
          <TabsTrigger value="compliance">
            <CheckCircle className="w-4 h-4 mr-2" />
            Compliance
          </TabsTrigger>
          <TabsTrigger value="reports">
            <FileText className="w-4 h-4 mr-2" />
            Rapporter
          </TabsTrigger>
        </TabsList>

        <TabsContent value="events" className="mt-6">
          {renderAuditEvents()}
        </TabsContent>

        <TabsContent value="security" className="mt-6">
          {renderSecurityEvents()}
        </TabsContent>

        <TabsContent value="compliance" className="mt-6">
          {renderCompliance()}
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          {renderReports()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AuditLog;
