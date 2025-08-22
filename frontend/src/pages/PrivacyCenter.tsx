import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Shield,
  Lock,
  Eye,
  EyeOff,
  UserCheck,
  UserX,
  FileText,
  Download,
  Trash2,
  Search,
  Filter,
  CheckCircle,
  AlertTriangle,
  Clock,
  RefreshCw,
  Settings,
  Key,
  Database,
  Globe,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Users
} from 'lucide-react';

interface DataSubject {
  id: string;
  name: string;
  email: string;
  phone?: string;
  location?: string;
  registrationDate: string;
  lastActivity: string;
  consentStatus: 'granted' | 'withdrawn' | 'pending' | 'expired';
  dataCategories: string[];
  requests: {
    access: number;
    erasure: number;
    portability: number;
    rectification: number;
  };
  processingActivities: string[];
}

interface ConsentRecord {
  id: string;
  subjectId: string;
  subjectName: string;
  purpose: string;
  legalBasis: 'consent' | 'legitimate_interest' | 'contract' | 'legal_obligation';
  status: 'active' | 'withdrawn' | 'expired';
  grantedDate: string;
  withdrawnDate?: string;
  expiryDate?: string;
  source: string;
  dataCategories: string[];
}

interface PrivacyRequest {
  id: string;
  type: 'access' | 'erasure' | 'portability' | 'rectification' | 'restriction';
  subjectId: string;
  subjectName: string;
  subjectEmail: string;
  status: 'pending' | 'in_progress' | 'completed' | 'rejected';
  submittedDate: string;
  dueDate: string;
  completedDate?: string;
  assignedTo?: string;
  description: string;
  attachments: string[];
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

const PrivacyCenter = () => {
  const [activeTab, setActiveTab] = useState<'subjects' | 'consent' | 'requests' | 'compliance'>('subjects');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'withdrawn' | 'pending'>('all');

  // Mock data
  const [dataSubjects] = useState<DataSubject[]>([
    {
      id: 'subj_001',
      name: 'Anna Andersson',
      email: 'anna.andersson@example.com',
      phone: '+46701234567',
      location: 'Stockholm, Sverige',
      registrationDate: '2024-01-15T10:30:00Z',
      lastActivity: '2024-08-20T14:22:00Z',
      consentStatus: 'granted',
      dataCategories: ['personal_info', 'contact_data', 'usage_data'],
      requests: { access: 1, erasure: 0, portability: 0, rectification: 1 },
      processingActivities: ['marketing', 'analytics', 'service_delivery']
    },
    {
      id: 'subj_002',
      name: 'Erik Eriksson',
      email: 'erik.eriksson@example.com',
      phone: '+46709876543',
      location: 'Göteborg, Sverige',
      registrationDate: '2024-02-20T09:15:00Z',
      lastActivity: '2024-08-18T11:45:00Z',
      consentStatus: 'withdrawn',
      dataCategories: ['personal_info', 'contact_data'],
      requests: { access: 0, erasure: 1, portability: 0, rectification: 0 },
      processingActivities: ['service_delivery']
    }
  ]);

  const [consentRecords] = useState<ConsentRecord[]>([
    {
      id: 'consent_001',
      subjectId: 'subj_001',
      subjectName: 'Anna Andersson',
      purpose: 'Marknadsföring via e-post',
      legalBasis: 'consent',
      status: 'active',
      grantedDate: '2024-01-15T10:30:00Z',
      source: 'Website signup form',
      dataCategories: ['email', 'name', 'preferences']
    },
    {
      id: 'consent_002',
      subjectId: 'subj_002',
      subjectName: 'Erik Eriksson',
      purpose: 'Användningsanalys',
      legalBasis: 'consent',
      status: 'withdrawn',
      grantedDate: '2024-02-20T09:15:00Z',
      withdrawnDate: '2024-08-01T16:30:00Z',
      source: 'Mobile app',
      dataCategories: ['usage_data', 'device_info']
    }
  ]);

  const [privacyRequests] = useState<PrivacyRequest[]>([
    {
      id: 'req_001',
      type: 'access',
      subjectId: 'subj_001',
      subjectName: 'Anna Andersson',
      subjectEmail: 'anna.andersson@example.com',
      status: 'in_progress',
      submittedDate: '2024-08-18T14:30:00Z',
      dueDate: '2024-09-17T14:30:00Z',
      assignedTo: 'Maria Larsson',
      description: 'Begäran om all personlig data som lagras',
      attachments: ['identity_verification.pdf'],
      priority: 'medium'
    },
    {
      id: 'req_002',
      type: 'erasure',
      subjectId: 'subj_002',
      subjectName: 'Erik Eriksson',
      subjectEmail: 'erik.eriksson@example.com',
      status: 'completed',
      submittedDate: '2024-08-01T16:30:00Z',
      dueDate: '2024-08-31T16:30:00Z',
      completedDate: '2024-08-15T10:00:00Z',
      assignedTo: 'Johan Svensson',
      description: 'Radering av all personlig data',
      attachments: ['erasure_request.pdf', 'completion_certificate.pdf'],
      priority: 'high'
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'granted':
      case 'active':
      case 'completed':
        return 'bg-success/10 text-success border-success/20';
      case 'withdrawn':
      case 'rejected':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'pending':
      case 'in_progress':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'expired':
        return 'bg-muted/10 text-muted-foreground border-muted/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'granted':
      case 'active':
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'withdrawn':
      case 'rejected':
        return <UserX className="w-4 h-4" />;
      case 'pending':
      case 'in_progress':
        return <Clock className="w-4 h-4" />;
      case 'expired':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return 'bg-red-500/10 text-red-500 border-red-500/20';
      case 'high':
        return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
      case 'medium':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case 'low':
        return 'bg-green-500/10 text-green-500 border-green-500/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('sv-SE');
  };

  const formatDateTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('sv-SE');
  };

  const renderSubjectsTab = () => (
    <div className="space-y-6">
      {/* Controls */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button>
                <Users className="w-4 h-4 mr-2" />
                Lägg till person
              </Button>
              <Button variant="outline">
                <Download className="w-4 h-4 mr-2" />
                Exportera register
              </Button>
            </div>
            <div className="flex items-center space-x-2">
              <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Sök personer..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 w-64"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value as any)}
                className="px-3 py-2 border rounded-md"
              >
                <option value="all">Alla samtycken</option>
                <option value="active">Aktiva</option>
                <option value="withdrawn">Återkallade</option>
                <option value="pending">Väntande</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Data Subjects */}
      <div className="space-y-4">
        {dataSubjects.map((subject) => (
          <Card key={subject.id} className="border-sidebar-border">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <UserCheck className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">{subject.name}</h3>
                    <Badge className={getStatusColor(subject.consentStatus)}>
                      {getStatusIcon(subject.consentStatus)}
                      <span className="ml-1 capitalize">{subject.consentStatus}</span>
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                    <div>
                      <span className="text-muted-foreground block">E-post</span>
                      <span className="font-medium">{subject.email}</span>
                    </div>
                    {subject.phone && (
                      <div>
                        <span className="text-muted-foreground block">Telefon</span>
                        <span className="font-medium">{subject.phone}</span>
                      </div>
                    )}
                    {subject.location && (
                      <div>
                        <span className="text-muted-foreground block">Plats</span>
                        <span className="font-medium">{subject.location}</span>
                      </div>
                    )}
                    <div>
                      <span className="text-muted-foreground block">Registrerad</span>
                      <span className="font-medium">{formatDate(subject.registrationDate)}</span>
                    </div>
                  </div>

                  {/* Data Categories */}
                  <div className="mb-4">
                    <span className="text-muted-foreground text-sm block mb-2">Datakategorier:</span>
                    <div className="flex flex-wrap gap-2">
                      {subject.dataCategories.map((category, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {category.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Processing Activities */}
                  <div className="mb-4">
                    <span className="text-muted-foreground text-sm block mb-2">Behandlingsaktiviteter:</span>
                    <div className="flex flex-wrap gap-2">
                      {subject.processingActivities.map((activity, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {activity.replace('_', ' ')}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Request Summary */}
                  <div className="grid grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                      <span className="text-muted-foreground block">Åtkomst</span>
                      <span className="font-semibold">{subject.requests.access}</span>
                    </div>
                    <div className="text-center">
                      <span className="text-muted-foreground block">Radering</span>
                      <span className="font-semibold">{subject.requests.erasure}</span>
                    </div>
                    <div className="text-center">
                      <span className="text-muted-foreground block">Portabilitet</span>
                      <span className="font-semibold">{subject.requests.portability}</span>
                    </div>
                    <div className="text-center">
                      <span className="text-muted-foreground block">Rättelse</span>
                      <span className="font-semibold">{subject.requests.rectification}</span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderConsentTab = () => (
    <div className="space-y-6">
      {/* Consent Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Aktiva samtycken</p>
                <p className="text-2xl font-bold text-foreground">
                  {consentRecords.filter(c => c.status === 'active').length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Återkallade</p>
                <p className="text-2xl font-bold text-foreground">
                  {consentRecords.filter(c => c.status === 'withdrawn').length}
                </p>
              </div>
              <UserX className="w-8 h-8 text-destructive" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Utgångna</p>
                <p className="text-2xl font-bold text-foreground">
                  {consentRecords.filter(c => c.status === 'expired').length}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-warning" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Samtyckefrekvens</p>
                <p className="text-2xl font-bold text-foreground">
                  {((consentRecords.filter(c => c.status === 'active').length / consentRecords.length) * 100).toFixed(0)}%
                </p>
              </div>
              <Shield className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Consent Records */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Samtycken</CardTitle>
          <CardDescription>Detaljerad vy över alla samtyckesregistreringar</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {consentRecords.map((consent) => (
              <div key={consent.id} className="border border-sidebar-border rounded p-4">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <Lock className="w-5 h-5 text-primary" />
                    <div>
                      <h4 className="font-medium">{consent.purpose}</h4>
                      <p className="text-sm text-muted-foreground">{consent.subjectName}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className={getStatusColor(consent.status)}>
                      {getStatusIcon(consent.status)}
                      <span className="ml-1 capitalize">{consent.status}</span>
                    </Badge>
                    <Badge variant="outline">{consent.legalBasis.replace('_', ' ')}</Badge>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground block">Beviljat</span>
                    <span className="font-medium">{formatDate(consent.grantedDate)}</span>
                  </div>
                  {consent.withdrawnDate && (
                    <div>
                      <span className="text-muted-foreground block">Återkallat</span>
                      <span className="font-medium">{formatDate(consent.withdrawnDate)}</span>
                    </div>
                  )}
                  <div>
                    <span className="text-muted-foreground block">Källa</span>
                    <span className="font-medium">{consent.source}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground block">Kategorier</span>
                    <span className="font-medium">{consent.dataCategories.length} st</span>
                  </div>
                </div>

                {consent.dataCategories.length > 0 && (
                  <div className="mt-3">
                    <div className="flex flex-wrap gap-2">
                      {consent.dataCategories.map((category, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {category}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderRequestsTab = () => (
    <div className="space-y-6">
      {/* Request Controls */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <Button>
              <FileText className="w-4 h-4 mr-2" />
              Ny begäran
            </Button>
            <div className="flex items-center space-x-2">
              <Button variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Uppdatera
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Exportera rapport
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Privacy Requests */}
      <div className="space-y-4">
        {privacyRequests.map((request) => (
          <Card key={request.id} className="border-sidebar-border">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <FileText className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">
                      {request.type.charAt(0).toUpperCase() + request.type.slice(1)} Request
                    </h3>
                    <Badge className={getStatusColor(request.status)}>
                      {getStatusIcon(request.status)}
                      <span className="ml-1 capitalize">{request.status.replace('_', ' ')}</span>
                    </Badge>
                    <Badge className={getPriorityColor(request.priority)}>
                      {request.priority}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                    <div>
                      <span className="text-muted-foreground block">Begärande</span>
                      <span className="font-medium">{request.subjectName}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">E-post</span>
                      <span className="font-medium">{request.subjectEmail}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Inskickat</span>
                      <span className="font-medium">{formatDate(request.submittedDate)}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Förfallodatum</span>
                      <span className="font-medium">{formatDate(request.dueDate)}</span>
                    </div>
                  </div>

                  {request.assignedTo && (
                    <div className="mb-3">
                      <span className="text-muted-foreground text-sm block">Tilldelad till:</span>
                      <span className="font-medium">{request.assignedTo}</span>
                    </div>
                  )}

                  <div className="mb-4">
                    <span className="text-muted-foreground text-sm block mb-2">Beskrivning:</span>
                    <p className="text-sm">{request.description}</p>
                  </div>

                  {request.attachments.length > 0 && (
                    <div>
                      <span className="text-muted-foreground text-sm block mb-2">Bilagor:</span>
                      <div className="flex flex-wrap gap-2">
                        {request.attachments.map((attachment, index) => (
                          <Badge key={index} variant="outline" className="text-xs">
                            {attachment}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <Button size="sm">
                    <Eye className="w-4 h-4 mr-2" />
                    Hantera
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderComplianceTab = () => (
    <div className="space-y-6">
      {/* Compliance Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">GDPR Compliance</p>
                <p className="text-2xl font-bold text-success">98%</p>
              </div>
              <Shield className="w-8 h-8 text-success" />
            </div>
            <div className="mt-2">
              <Progress value={98} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Öppna begäranden</p>
                <p className="text-2xl font-bold text-warning">
                  {privacyRequests.filter(r => r.status !== 'completed' && r.status !== 'rejected').length}
                </p>
              </div>
              <Clock className="w-8 h-8 text-warning" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Genomsnittlig responstid</p>
                <p className="text-2xl font-bold text-primary">12 dagar</p>
              </div>
              <Calendar className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Compliance Checklist */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">GDPR Compliance Checklista</CardTitle>
          <CardDescription>Översikt över regelefterlevnad och nödvändiga åtgärder</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              { item: 'Samtyckehantering', status: 'completed', description: 'Tydligt och dokumenterat samtycke' },
              { item: 'Dataminimering', status: 'completed', description: 'Endast nödvändig data samlas in' },
              { item: 'Rätt till radering', status: 'completed', description: 'Automatiserad radering implementerad' },
              { item: 'Dataskyddsombud', status: 'completed', description: 'DPO tillsatt och kontaktuppgifter publicerade' },
              { item: 'Dataflödesanalys', status: 'in_progress', description: 'Kartläggning av alla dataflöden pågår' },
              { item: 'Konsekvensbedömning', status: 'pending', description: 'DPIA för nya behandlingar behövs' }
            ].map((check, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-sidebar-border rounded">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(check.status)}
                  <div>
                    <div className="font-medium">{check.item}</div>
                    <div className="text-sm text-muted-foreground">{check.description}</div>
                  </div>
                </div>
                <Badge className={getStatusColor(check.status)}>
                  {check.status.replace('_', ' ')}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risk Assessment */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Riskbedömning</CardTitle>
          <CardDescription>Aktuella risker och rekommenderade åtgärder</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[
              { risk: 'Överföringar till tredje land', level: 'medium', action: 'Implementera adequate safeguards' },
              { risk: 'Långvarig datalagring', level: 'low', action: 'Regelbunden granskning av lagringsperioder' },
              { risk: 'Manuell samtyckehantering', level: 'high', action: 'Automatisera samtyckeprocesser' }
            ].map((risk, index) => (
              <div key={index} className="flex items-center justify-between p-3 border border-sidebar-border rounded">
                <div>
                  <div className="font-medium">{risk.risk}</div>
                  <div className="text-sm text-muted-foreground">{risk.action}</div>
                </div>
                <Badge className={getPriorityColor(risk.level)}>
                  {risk.level}
                </Badge>
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
          <h1 className="text-3xl font-bold text-foreground">Privacy Center</h1>
          <p className="text-muted-foreground">GDPR-efterlevnad och integritetsskydd</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Compliance rapport
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="subjects">Registrerade</TabsTrigger>
          <TabsTrigger value="consent">Samtycken</TabsTrigger>
          <TabsTrigger value="requests">Begäranden</TabsTrigger>
          <TabsTrigger value="compliance">Efterlevnad</TabsTrigger>
        </TabsList>

        <TabsContent value="subjects" className="mt-6">
          {renderSubjectsTab()}
        </TabsContent>

        <TabsContent value="consent" className="mt-6">
          {renderConsentTab()}
        </TabsContent>

        <TabsContent value="requests" className="mt-6">
          {renderRequestsTab()}
        </TabsContent>

        <TabsContent value="compliance" className="mt-6">
          {renderComplianceTab()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PrivacyCenter;
