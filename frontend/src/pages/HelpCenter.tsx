import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  HelpCircle,
  Book,
  FileText,
  Search,
  Settings,
  Play,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  Download,
  Star,
  Clock,
  Users,
  Zap,
  Shield,
  Database,
  Globe,
  Code,
  Terminal,
  Wrench,
  LifeBuoy,
  MessageCircle,
  Mail,
  Phone,
  Video,
  ChevronRight,
  Bookmark,
  Edit,
  Plus,
  Filter,
  Tag
} from 'lucide-react';

interface DocumentationItem {
  id: string;
  title: string;
  description: string;
  category: 'setup' | 'troubleshooting' | 'api' | 'best-practices' | 'security' | 'integration';
  type: 'guide' | 'runbook' | 'reference' | 'tutorial' | 'faq';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  lastUpdated: string;
  estimatedTime: string;
  popularity: number;
  tags: string[];
}

interface Runbook {
  id: string;
  title: string;
  description: string;
  category: 'incident' | 'maintenance' | 'deployment' | 'monitoring' | 'backup';
  severity: 'low' | 'medium' | 'high' | 'critical';
  steps: {
    id: string;
    title: string;
    description: string;
    command?: string;
    warning?: string;
    expectedOutput?: string;
  }[];
  prerequisites: string[];
  estimatedTime: string;
  lastUsed?: string;
  successRate: number;
}

interface SupportTicket {
  id: string;
  title: string;
  description: string;
  category: 'technical' | 'billing' | 'feature' | 'bug';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in_progress' | 'waiting' | 'resolved' | 'closed';
  createdAt: string;
  updatedAt: string;
  assignedTo?: string;
}

const HelpCenter = () => {
  const [activeTab, setActiveTab] = useState<'docs' | 'runbooks' | 'support' | 'contact'>('docs');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Mock documentation
  const [documentation] = useState<DocumentationItem[]>([
    {
      id: 'doc_001',
      title: 'Komma igång med ECaDP',
      description: 'Steg-för-steg guide för att sätta upp ditt första crawling-projekt',
      category: 'setup',
      type: 'tutorial',
      difficulty: 'beginner',
      lastUpdated: '2024-12-15T10:00:00Z',
      estimatedTime: '30 min',
      popularity: 95,
      tags: ['setup', 'getting-started', 'tutorial']
    },
    {
      id: 'doc_002',
      title: 'API Reference - GraphQL',
      description: 'Fullständig referens för ECaDPs GraphQL API',
      category: 'api',
      type: 'reference',
      difficulty: 'intermediate',
      lastUpdated: '2024-12-10T14:30:00Z',
      estimatedTime: '15 min',
      popularity: 78,
      tags: ['api', 'graphql', 'reference']
    },
    {
      id: 'doc_003',
      title: 'Felsökning av rate limit-problem',
      description: 'Hur man diagnostiserar och löser problem med hastighetsbegränsning',
      category: 'troubleshooting',
      type: 'guide',
      difficulty: 'intermediate',
      lastUpdated: '2024-12-08T09:15:00Z',
      estimatedTime: '20 min',
      popularity: 67,
      tags: ['troubleshooting', 'rate-limiting', 'debugging']
    },
    {
      id: 'doc_004',
      title: 'GDPR Compliance Best Practices',
      description: 'Säkerställ att dina crawling-projekt följer GDPR-reglerna',
      category: 'best-practices',
      type: 'guide',
      difficulty: 'advanced',
      lastUpdated: '2024-12-05T16:45:00Z',
      estimatedTime: '45 min',
      popularity: 89,
      tags: ['gdpr', 'compliance', 'privacy', 'legal']
    },
    {
      id: 'doc_005',
      title: 'Säkerhetsriktlinjer för produktion',
      description: 'Viktiga säkerhetsåtgärder för produktionsmiljöer',
      category: 'security',
      type: 'guide',
      difficulty: 'advanced',
      lastUpdated: '2024-12-01T11:20:00Z',
      estimatedTime: '60 min',
      popularity: 92,
      tags: ['security', 'production', 'best-practices']
    }
  ]);

  // Mock runbooks
  const [runbooks] = useState<Runbook[]>([
    {
      id: 'runbook_001',
      title: 'Incident: Hög CPU-användning i crawler',
      description: 'Steg för att diagnostisera och lösa hög CPU-användning',
      category: 'incident',
      severity: 'high',
      steps: [
        {
          id: 'step_1',
          title: 'Kontrollera systemstatus',
          description: 'Verifiera aktuell CPU-användning och systemlast',
          command: 'kubectl top pods -n ecadp-crawler',
          expectedOutput: 'Lista med poddar och deras resursanvändning'
        },
        {
          id: 'step_2',
          title: 'Identifiera problemjobbningar',
          description: 'Hitta jobb som använder mest CPU',
          command: 'kubectl logs -n ecadp-crawler -l app=crawler --tail=100',
          warning: 'Loggar kan vara stora, begränsa output med --tail'
        },
        {
          id: 'step_3',
          title: 'Pausa problematiska jobb',
          description: 'Tillfälligt pausa jobb med hög resursanvändning',
          command: 'curl -X POST /api/v1/jobs/{job_id}/pause',
          expectedOutput: '{"status": "paused", "job_id": "..."}'
        }
      ],
      prerequisites: ['kubectl access', 'API credentials', 'monitoring dashboard access'],
      estimatedTime: '15-30 min',
      lastUsed: '2024-12-10T08:30:00Z',
      successRate: 94
    },
    {
      id: 'runbook_002',
      title: 'Deployment: Rolling update av crawler-tjänster',
      description: 'Säker deployment av nya versioner utan avbrott',
      category: 'deployment',
      severity: 'medium',
      steps: [
        {
          id: 'step_1',
          title: 'Förbered deployment',
          description: 'Kontrollera att den nya versionen är testad',
          warning: 'Kör endast i underhållsfönster för kritiska uppdateringar'
        },
        {
          id: 'step_2',
          title: 'Kör rolling update',
          description: 'Uppdatera tjänster gradvis',
          command: 'kubectl rollout restart deployment/crawler -n ecadp',
          expectedOutput: 'deployment.apps/crawler restarted'
        },
        {
          id: 'step_3',
          title: 'Verifiera deployment',
          description: 'Kontrollera att alla poddar körs korrekt',
          command: 'kubectl rollout status deployment/crawler -n ecadp',
          expectedOutput: 'deployment "crawler" successfully rolled out'
        }
      ],
      prerequisites: ['kubectl access', 'tested image', 'backup plan'],
      estimatedTime: '45-60 min',
      successRate: 98
    }
  ]);

  // Mock support tickets
  const [supportTickets] = useState<SupportTicket[]>([
    {
      id: 'ticket_001',
      title: 'API rate limit för strikt för vårt användningsfall',
      description: 'Vi behöver crawla 10000+ sidor dagligen men träffar rate limit',
      category: 'technical',
      priority: 'medium',
      status: 'in_progress',
      createdAt: '2024-12-15T09:30:00Z',
      updatedAt: '2024-12-16T14:20:00Z',
      assignedTo: 'support@ecadp.com'
    },
    {
      id: 'ticket_002',
      title: 'Förfrågan om ny funktion: Batch export till S3',
      description: 'Skulle vilja kunna exportera stora datamängder direkt till S3',
      category: 'feature',
      priority: 'low',
      status: 'open',
      createdAt: '2024-12-14T16:45:00Z',
      updatedAt: '2024-12-14T16:45:00Z'
    }
  ]);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'setup':
        return <Settings className="w-4 h-4" />;
      case 'troubleshooting':
        return <Wrench className="w-4 h-4" />;
      case 'api':
        return <Code className="w-4 h-4" />;
      case 'best-practices':
        return <Star className="w-4 h-4" />;
      case 'security':
        return <Shield className="w-4 h-4" />;
      case 'integration':
        return <Zap className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'setup':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'troubleshooting':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'api':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'best-practices':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'security':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'integration':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'advanced':
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'waiting':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'closed':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('sv-SE');
  };

  const renderDocumentation = () => (
    <div className="space-y-6">
      {/* Search and Filters */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Sök i dokumentation..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline">
              <Filter className="w-4 h-4 mr-2" />
              Filter
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Popular Articles */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base flex items-center">
            <Star className="w-4 h-4 mr-2" />
            Populära artiklar
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {documentation
              .sort((a, b) => b.popularity - a.popularity)
              .slice(0, 4)
              .map((doc) => (
                <div key={doc.id} className="border rounded p-4 hover:bg-muted/50 cursor-pointer">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium">{doc.title}</h4>
                    <Badge className={getCategoryColor(doc.category)}>
                      {getCategoryIcon(doc.category)}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{doc.description}</p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{doc.estimatedTime}</span>
                    <Badge className={getDifficultyColor(doc.difficulty)}>
                      {doc.difficulty}
                    </Badge>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>

      {/* All Documentation */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Alla guider</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {documentation.map((doc) => (
              <div key={doc.id} className="border rounded p-4 hover:bg-muted/50 cursor-pointer">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium">{doc.title}</h4>
                      <Badge className={getCategoryColor(doc.category)}>
                        {getCategoryIcon(doc.category)}
                        <span className="ml-1">{doc.category}</span>
                      </Badge>
                      <Badge className={getDifficultyColor(doc.difficulty)}>
                        {doc.difficulty}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{doc.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {doc.estimatedTime}
                      </span>
                      <span>Uppdaterad {formatDate(doc.lastUpdated)}</span>
                      <span className="flex items-center">
                        <Star className="w-3 h-3 mr-1" />
                        {doc.popularity}% hittar detta användbart
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {doc.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          <Tag className="w-3 h-3 mr-1" />
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <Button variant="outline" size="sm">
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Bookmark className="w-4 h-4" />
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

  const renderRunbooks = () => (
    <div className="space-y-6">
      {/* Runbook Categories */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Runbook-kategorier</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <Button variant="outline" className="justify-start">
              <AlertTriangle className="w-4 h-4 mr-2" />
              Incidenter
            </Button>
            <Button variant="outline" className="justify-start">
              <Wrench className="w-4 h-4 mr-2" />
              Underhåll
            </Button>
            <Button variant="outline" className="justify-start">
              <Play className="w-4 h-4 mr-2" />
              Deployment
            </Button>
            <Button variant="outline" className="justify-start">
              <Database className="w-4 h-4 mr-2" />
              Backup
            </Button>
            <Button variant="outline" className="justify-start">
              <Shield className="w-4 h-4 mr-2" />
              Säkerhet
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Runbook List */}
      <div className="space-y-4">
        {runbooks.map((runbook) => (
          <Card key={runbook.id} className="border-sidebar-border">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="font-semibold text-lg">{runbook.title}</h3>
                    <Badge className={getSeverityColor(runbook.severity)}>
                      {runbook.severity}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground mb-4">{runbook.description}</p>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm mb-4">
                    <div>
                      <span className="text-muted-foreground">Kategori:</span>
                      <span className="ml-1 font-medium capitalize">{runbook.category}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Estimerad tid:</span>
                      <span className="ml-1 font-medium">{runbook.estimatedTime}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Framgångsgrad:</span>
                      <span className="ml-1 font-medium">{runbook.successRate}%</span>
                    </div>
                  </div>

                  {/* Prerequisites */}
                  <div className="mb-4">
                    <div className="text-sm font-medium text-muted-foreground mb-2">Förutsättningar:</div>
                    <div className="flex flex-wrap gap-1">
                      {runbook.prerequisites.map((prereq, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {prereq}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Steps Preview */}
                  <div className="bg-muted/50 border rounded p-3">
                    <div className="text-sm font-medium mb-2">{runbook.steps.length} steg:</div>
                    <div className="space-y-1">
                      {runbook.steps.slice(0, 3).map((step, index) => (
                        <div key={step.id} className="flex items-center text-xs text-muted-foreground">
                          <span className="w-4 h-4 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xs mr-2">
                            {index + 1}
                          </span>
                          {step.title}
                        </div>
                      ))}
                      {runbook.steps.length > 3 && (
                        <div className="text-xs text-muted-foreground ml-6">
                          +{runbook.steps.length - 3} fler steg...
                        </div>
                      )}
                    </div>
                  </div>

                  {runbook.lastUsed && (
                    <div className="mt-3 text-xs text-muted-foreground">
                      Senast använd: {formatDate(runbook.lastUsed)}
                    </div>
                  )}
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <Button>
                    <Play className="w-4 h-4 mr-2" />
                    Kör runbook
                  </Button>
                  <Button variant="outline" size="sm">
                    <ExternalLink className="w-4 h-4" />
                  </Button>
                  <Button variant="outline" size="sm">
                    <Edit className="w-4 h-4" />
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

  const renderSupport = () => (
    <div className="space-y-6">
      {/* New Ticket */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Skapa supportärende</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Nytt supportärende
          </Button>
        </CardContent>
      </Card>

      {/* Ticket Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-foreground">{supportTickets.filter(t => t.status === 'open').length}</div>
            <div className="text-sm text-muted-foreground">Öppna ärenden</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-warning">{supportTickets.filter(t => t.status === 'in_progress').length}</div>
            <div className="text-sm text-muted-foreground">Pågående</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-success">{supportTickets.filter(t => t.status === 'resolved').length}</div>
            <div className="text-sm text-muted-foreground">Lösta</div>
          </CardContent>
        </Card>
        <Card className="border-sidebar-border">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-foreground">24h</div>
            <div className="text-sm text-muted-foreground">Avg svarstid</div>
          </CardContent>
        </Card>
      </div>

      {/* Support Tickets */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Dina supportärenden</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {supportTickets.map((ticket) => (
              <div key={ticket.id} className="border rounded p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="font-medium">{ticket.title}</h4>
                      <Badge className={getStatusColor(ticket.status)}>
                        {ticket.status.replace('_', ' ')}
                      </Badge>
                      <Badge variant="outline" className="capitalize">
                        {ticket.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{ticket.description}</p>
                    <div className="flex items-center space-x-4 text-xs text-muted-foreground">
                      <span>Skapad: {formatDate(ticket.createdAt)}</span>
                      <span>Uppdaterad: {formatDate(ticket.updatedAt)}</span>
                      {ticket.assignedTo && (
                        <span>Tilldelad: {ticket.assignedTo}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex space-x-2 ml-4">
                    <Button variant="outline" size="sm">
                      <MessageCircle className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="w-4 h-4" />
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

  const renderContact = () => (
    <div className="space-y-6">
      {/* Contact Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-6 text-center">
            <Mail className="w-8 h-8 text-primary mx-auto mb-3" />
            <h3 className="font-semibold mb-2">E-post Support</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Få hjälp via e-post. Svarstid inom 24h.
            </p>
            <Button>
              <Mail className="w-4 h-4 mr-2" />
              support@ecadp.com
            </Button>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6 text-center">
            <MessageCircle className="w-8 h-8 text-primary mx-auto mb-3" />
            <h3 className="font-semibold mb-2">Live Chat</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Chatta med oss direkt. Tillgänglig 9-17 CET.
            </p>
            <Button>
              <MessageCircle className="w-4 h-4 mr-2" />
              Starta chat
            </Button>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6 text-center">
            <Phone className="w-8 h-8 text-primary mx-auto mb-3" />
            <h3 className="font-semibold mb-2">Telefonsupport</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Ring oss för akuta problem.
            </p>
            <Button>
              <Phone className="w-4 h-4 mr-2" />
              +46 8 123 456 78
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Community */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Community & Resurser</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded p-4">
              <div className="flex items-center space-x-3 mb-3">
                <Users className="w-5 h-5 text-primary" />
                <h4 className="font-medium">Community Forum</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Diskutera med andra användare och dela erfarenheter
              </p>
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4 mr-2" />
                Besök forum
              </Button>
            </div>

            <div className="border rounded p-4">
              <div className="flex items-center space-x-3 mb-3">
                <Video className="w-5 h-5 text-primary" />
                <h4 className="font-medium">Video Tutorials</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Lär dig genom steg-för-steg videor
              </p>
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4 mr-2" />
                YouTube-kanal
              </Button>
            </div>

            <div className="border rounded p-4">
              <div className="flex items-center space-x-3 mb-3">
                <Book className="w-5 h-5 text-primary" />
                <h4 className="font-medium">Utvecklardokumentation</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Teknisk dokumentation för utvecklare
              </p>
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4 mr-2" />
                docs.ecadp.com
              </Button>
            </div>

            <div className="border rounded p-4">
              <div className="flex items-center space-x-3 mb-3">
                <Terminal className="w-5 h-5 text-primary" />
                <h4 className="font-medium">GitHub Repository</h4>
              </div>
              <p className="text-sm text-muted-foreground mb-3">
                Källkod, issues och contributions
              </p>
              <Button variant="outline" size="sm">
                <ExternalLink className="w-4 h-4 mr-2" />
                GitHub
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* FAQ */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Vanliga frågor (FAQ)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="border rounded p-4">
              <h4 className="font-medium mb-2">Hur ökar jag rate limit för mitt konto?</h4>
              <p className="text-sm text-muted-foreground">
                Kontakta support med information om ditt användningsfall så hjälper vi dig att justera gränserna.
              </p>
            </div>
            <div className="border rounded p-4">
              <h4 className="font-medium mb-2">Kan jag exportera data i andra format än CSV?</h4>
              <p className="text-sm text-muted-foreground">
                Ja, vi stödjer JSON, Excel och kan även konfigurera direktintegration med din databas.
              </p>
            </div>
            <div className="border rounded p-4">
              <h4 className="font-medium mb-2">Hur fungerar GDPR-compliance i ECaDP?</h4>
              <p className="text-sm text-muted-foreground">
                ECaDP har inbyggda verktyg för att hantera GDPR-krav, inklusive rätten att bli glömd och dataportabilitet.
              </p>
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
          <h1 className="text-3xl font-bold text-foreground">Hjälp & Support</h1>
          <p className="text-muted-foreground">Dokumentation, runbooks och support</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Ladda ner PDF
          </Button>
          <Button variant="outline">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="docs">
            <Book className="w-4 h-4 mr-2" />
            Dokumentation
          </TabsTrigger>
          <TabsTrigger value="runbooks">
            <Terminal className="w-4 h-4 mr-2" />
            Runbooks
          </TabsTrigger>
          <TabsTrigger value="support">
            <LifeBuoy className="w-4 h-4 mr-2" />
            Support
          </TabsTrigger>
          <TabsTrigger value="contact">
            <MessageCircle className="w-4 h-4 mr-2" />
            Kontakt
          </TabsTrigger>
        </TabsList>

        <TabsContent value="docs" className="mt-6">
          {renderDocumentation()}
        </TabsContent>

        <TabsContent value="runbooks" className="mt-6">
          {renderRunbooks()}
        </TabsContent>

        <TabsContent value="support" className="mt-6">
          {renderSupport()}
        </TabsContent>

        <TabsContent value="contact" className="mt-6">
          {renderContact()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default HelpCenter;
