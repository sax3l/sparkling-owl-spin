import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Checkbox } from '@/components/ui/checkbox';
import { Progress } from '@/components/ui/progress';
import { 
  Shield,
  Settings,
  Globe,
  Clock,
  Zap,
  Activity,
  AlertTriangle,
  CheckCircle,
  Play,
  Pause,
  Save,
  Copy,
  Edit,
  Trash2,
  Plus,
  Eye,
  RefreshCw,
  Target,
  Database,
  Network,
  Lock,
  User,
  FileText
} from 'lucide-react';

interface Policy {
  id: string;
  name: string;
  description: string;
  version: string;
  status: 'draft' | 'active' | 'deprecated';
  created: string;
  lastModified: string;
  appliedToJobs: number;
  rules: {
    domains: {
      include: string[];
      exclude: string[];
      subdomainsAllowed: boolean;
    };
    rateLimit: {
      requestsPerSecond: number;
      perHost: number;
      burstAllowed: number;
    };
    politeness: {
      delayBetweenRequests: number;
      respectRobotsTxt: boolean;
      respectCrawlDelay: boolean;
      maxConcurrentRequests: number;
    };
    rendering: {
      jsEnabled: boolean;
      waitForLoad: number;
      maxWaitTime: number;
      screenshotOnError: boolean;
    };
    headers: {
      userAgent: string;
      acceptLanguage: string;
      refererPolicy: 'no-referrer' | 'same-origin' | 'strict-origin';
      customHeaders: Record<string, string>;
    };
    consent: {
      checkCookieBanners: boolean;
      acceptCookies: boolean;
      gdprCompliant: boolean;
    };
    circuitBreaker: {
      errorThreshold: number;
      timeoutMs: number;
      retryAttempts: number;
      backoffStrategy: 'linear' | 'exponential';
    };
  };
}

interface PolicySimulation {
  estimatedThroughput: number;
  estimatedCompliance: number;
  potentialIssues: string[];
  recommendedChanges: string[];
}

const Policies = () => {
  const [activeTab, setActiveTab] = useState<'list' | 'editor' | 'simulation' | 'applied'>('list');
  const [selectedPolicy, setSelectedPolicy] = useState<Policy | null>(null);
  const [simulation, setSimulation] = useState<PolicySimulation | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  // Mock policies data
  const [policies] = useState<Policy[]>([
    {
      id: 'policy_001',
      name: 'Standard Web Crawling',
      description: 'Grundläggande policy för etisk webb-crawling',
      version: 'v2.1',
      status: 'active',
      created: '2024-06-01T10:00:00Z',
      lastModified: '2024-08-15T14:30:00Z',
      appliedToJobs: 23,
      rules: {
        domains: {
          include: ['*.example.com', '*.test-site.se'],
          exclude: ['admin.*', '*.private.*'],
          subdomainsAllowed: true
        },
        rateLimit: {
          requestsPerSecond: 5,
          perHost: 2,
          burstAllowed: 10
        },
        politeness: {
          delayBetweenRequests: 1000,
          respectRobotsTxt: true,
          respectCrawlDelay: true,
          maxConcurrentRequests: 4
        },
        rendering: {
          jsEnabled: false,
          waitForLoad: 2000,
          maxWaitTime: 10000,
          screenshotOnError: false
        },
        headers: {
          userAgent: 'ECaDP-Crawler/1.0 (+https://ecadp.example.com/bot)',
          acceptLanguage: 'sv-SE,sv;q=0.9,en;q=0.8',
          refererPolicy: 'strict-origin',
          customHeaders: {}
        },
        consent: {
          checkCookieBanners: true,
          acceptCookies: false,
          gdprCompliant: true
        },
        circuitBreaker: {
          errorThreshold: 50,
          timeoutMs: 30000,
          retryAttempts: 3,
          backoffStrategy: 'exponential'
        }
      }
    },
    {
      id: 'policy_002',
      name: 'JS-Heavy Sites',
      description: 'Policy för siter som kräver JavaScript-rendering',
      version: 'v1.3',
      status: 'active',
      created: '2024-07-10T11:30:00Z',
      lastModified: '2024-08-10T09:15:00Z',
      appliedToJobs: 7,
      rules: {
        domains: {
          include: ['spa.example.com'],
          exclude: [],
          subdomainsAllowed: false
        },
        rateLimit: {
          requestsPerSecond: 2,
          perHost: 1,
          burstAllowed: 3
        },
        politeness: {
          delayBetweenRequests: 3000,
          respectRobotsTxt: true,
          respectCrawlDelay: true,
          maxConcurrentRequests: 2
        },
        rendering: {
          jsEnabled: true,
          waitForLoad: 5000,
          maxWaitTime: 30000,
          screenshotOnError: true
        },
        headers: {
          userAgent: 'ECaDP-Crawler/1.0 (+https://ecadp.example.com/bot)',
          acceptLanguage: 'sv-SE,sv;q=0.9,en;q=0.8',
          refererPolicy: 'same-origin',
          customHeaders: {}
        },
        consent: {
          checkCookieBanners: true,
          acceptCookies: true,
          gdprCompliant: true
        },
        circuitBreaker: {
          errorThreshold: 30,
          timeoutMs: 45000,
          retryAttempts: 2,
          backoffStrategy: 'linear'
        }
      }
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success/10 text-success border-success/20';
      case 'draft':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'deprecated':
        return 'bg-muted/10 text-muted-foreground border-muted/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4" />;
      case 'draft':
        return <Edit className="w-4 h-4" />;
      case 'deprecated':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleDateString('sv-SE');
  };

  const runSimulation = async () => {
    setIsSimulating(true);
    
    // Simulate policy analysis
    setTimeout(() => {
      setSimulation({
        estimatedThroughput: Math.floor(Math.random() * 50) + 10,
        estimatedCompliance: Math.floor(Math.random() * 20) + 80,
        potentialIssues: [
          'Rate limit kan vara för låg för stora sajter',
          'JS-rendering ökar resurskrävandet betydligt'
        ],
        recommendedChanges: [
          'Öka burst-allowance för bättre prestanda',
          'Implementera adaptiv delay baserat på server-respons'
        ]
      });
      setIsSimulating(false);
    }, 2000);
  };

  const renderPolicyList = () => (
    <div className="space-y-6">
      {/* Controls */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Ny policy
              </Button>
              <Button variant="outline">
                <Copy className="w-4 h-4 mr-2" />
                Klona befintlig
              </Button>
            </div>
            <Button variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Uppdatera status
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Policy Cards */}
      <div className="space-y-4">
        {policies.map((policy) => (
          <Card key={policy.id} className="border-sidebar-border">
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <Shield className="w-5 h-5 text-primary" />
                    <h3 className="font-semibold text-lg">{policy.name}</h3>
                    <Badge className={getStatusColor(policy.status)}>
                      {getStatusIcon(policy.status)}
                      <span className="ml-1 capitalize">{policy.status}</span>
                    </Badge>
                    <Badge variant="outline">{policy.version}</Badge>
                  </div>

                  <p className="text-muted-foreground mb-4">{policy.description}</p>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                    <div>
                      <span className="text-muted-foreground block">Skapad</span>
                      <span className="font-medium">{formatDate(policy.created)}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Senast ändrad</span>
                      <span className="font-medium">{formatDate(policy.lastModified)}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Tillämpade jobb</span>
                      <span className="font-medium">{policy.appliedToJobs}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground block">Rate limit</span>
                      <span className="font-medium">{policy.rules.rateLimit.requestsPerSecond} req/s</span>
                    </div>
                  </div>

                  {/* Quick Policy Preview */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                    <div className="flex items-center space-x-1">
                      <Globe className="w-3 h-3" />
                      <span>{policy.rules.domains.include.length} domäner</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Zap className="w-3 h-3" />
                      <span>{policy.rules.politeness.maxConcurrentRequests} samtidiga</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Lock className="w-3 h-3" />
                      <span>{policy.rules.consent.gdprCompliant ? 'GDPR' : 'Ej GDPR'}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Activity className="w-3 h-3" />
                      <span>{policy.rules.rendering.jsEnabled ? 'JS' : 'Ingen JS'}</span>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col space-y-2 ml-4">
                  <Button 
                    size="sm"
                    onClick={() => setSelectedPolicy(policy)}
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Redigera
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

  const renderPolicyEditor = () => (
    <div className="space-y-6">
      {selectedPolicy && (
        <>
          {/* Policy Metadata */}
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="text-base">Policy metadata</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Namn</Label>
                  <Input defaultValue={selectedPolicy.name} />
                </div>
                <div className="space-y-2">
                  <Label>Version</Label>
                  <Input defaultValue={selectedPolicy.version} />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Beskrivning</Label>
                <Textarea defaultValue={selectedPolicy.description} />
              </div>
            </CardContent>
          </Card>

          {/* Domain Rules */}
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="text-base">Domänregler</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Inkludera domäner</Label>
                  <Textarea 
                    placeholder="*.example.com&#10;specific-site.se"
                    defaultValue={selectedPolicy.rules.domains.include.join('\n')}
                    rows={4}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Exkludera domäner</Label>
                  <Textarea 
                    placeholder="admin.*&#10;private.*"
                    defaultValue={selectedPolicy.rules.domains.exclude.join('\n')}
                    rows={4}
                  />
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="subdomains"
                  defaultChecked={selectedPolicy.rules.domains.subdomainsAllowed}
                />
                <Label htmlFor="subdomains">Tillåt subdomäner</Label>
              </div>
            </CardContent>
          </Card>

          {/* Rate Limiting */}
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="text-base">Hastighetsbegränsning</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Requests per sekund</Label>
                  <Input 
                    type="number"
                    defaultValue={selectedPolicy.rules.rateLimit.requestsPerSecond}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Per värd</Label>
                  <Input 
                    type="number"
                    defaultValue={selectedPolicy.rules.rateLimit.perHost}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Burst tillåtet</Label>
                  <Input 
                    type="number"
                    defaultValue={selectedPolicy.rules.rateLimit.burstAllowed}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Politeness */}
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="text-base">Artighet & Respekt</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Delay mellan requests (ms)</Label>
                  <Input 
                    type="number"
                    defaultValue={selectedPolicy.rules.politeness.delayBetweenRequests}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Max samtidiga requests</Label>
                  <Input 
                    type="number"
                    defaultValue={selectedPolicy.rules.politeness.maxConcurrentRequests}
                  />
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="robots"
                    defaultChecked={selectedPolicy.rules.politeness.respectRobotsTxt}
                  />
                  <Label htmlFor="robots">Respektera robots.txt</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="crawldelay"
                    defaultChecked={selectedPolicy.rules.politeness.respectCrawlDelay}
                  />
                  <Label htmlFor="crawldelay">Respektera Crawl-Delay</Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Consent & GDPR */}
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="text-base">Samtycke & GDPR</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="cookiebanners"
                    defaultChecked={selectedPolicy.rules.consent.checkCookieBanners}
                  />
                  <Label htmlFor="cookiebanners">Kontrollera cookie-banners</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="acceptcookies"
                    defaultChecked={selectedPolicy.rules.consent.acceptCookies}
                  />
                  <Label htmlFor="acceptcookies">Acceptera cookies automatiskt</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox 
                    id="gdpr"
                    defaultChecked={selectedPolicy.rules.consent.gdprCompliant}
                  />
                  <Label htmlFor="gdpr">GDPR-kompatibel</Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Save Actions */}
          <Card className="border-sidebar-border">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex space-x-2">
                  <Button>
                    <Save className="w-4 h-4 mr-2" />
                    Spara utkast
                  </Button>
                  <Button variant="outline">
                    <Play className="w-4 h-4 mr-2" />
                    Publicera
                  </Button>
                </div>
                <Button variant="outline" onClick={() => setSelectedPolicy(null)}>
                  Avbryt
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );

  const renderSimulation = () => (
    <div className="space-y-6">
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Policy-simulering</CardTitle>
            <Button onClick={runSimulation} disabled={isSimulating}>
              {isSimulating ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Play className="w-4 h-4 mr-2" />
              )}
              {isSimulating ? 'Simulerar...' : 'Kör simulering'}
            </Button>
          </div>
          <CardDescription>
            Testa policy-inställningar innan tillämpning
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSimulating ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-center">
                <RefreshCw className="w-8 h-8 text-primary animate-spin mx-auto mb-2" />
                <p className="text-muted-foreground">Analyserar policy-påverkan...</p>
              </div>
            </div>
          ) : simulation ? (
            <div className="space-y-6">
              {/* Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="border-sidebar-border">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{simulation.estimatedThroughput}</div>
                    <div className="text-sm text-muted-foreground">Sidor/minut</div>
                  </CardContent>
                </Card>
                <Card className="border-sidebar-border">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{simulation.estimatedCompliance}%</div>
                    <div className="text-sm text-muted-foreground">Compliance-score</div>
                  </CardContent>
                </Card>
                <Card className="border-sidebar-border">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{simulation.potentialIssues.length}</div>
                    <div className="text-sm text-muted-foreground">Potentiella problem</div>
                  </CardContent>
                </Card>
              </div>

              {/* Issues & Recommendations */}
              {simulation.potentialIssues.length > 0 && (
                <Card className="border-sidebar-border border-warning">
                  <CardHeader>
                    <CardTitle className="text-base flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-2 text-warning" />
                      Potentiella problem
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {simulation.potentialIssues.map((issue, index) => (
                        <div key={index} className="text-sm text-warning bg-warning/10 p-2 rounded">
                          {issue}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {simulation.recommendedChanges.length > 0 && (
                <Card className="border-sidebar-border border-primary">
                  <CardHeader>
                    <CardTitle className="text-base flex items-center">
                      <Target className="w-4 h-4 mr-2 text-primary" />
                      Rekommendationer
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {simulation.recommendedChanges.map((change, index) => (
                        <div key={index} className="text-sm text-primary bg-primary/10 p-2 rounded">
                          {change}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <Shield className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">Kör simulering för att se policy-analys</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  const renderAppliedPolicies = () => (
    <div className="space-y-6">
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Tillämpade policyer</CardTitle>
          <CardDescription>Översikt över vilka jobb som använder vilka policyer</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {policies.filter(p => p.appliedToJobs > 0).map((policy) => (
              <div key={policy.id} className="border border-sidebar-border rounded p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <Shield className="w-5 h-5 text-primary" />
                    <h4 className="font-medium">{policy.name}</h4>
                    <Badge className={getStatusColor(policy.status)}>
                      {policy.status}
                    </Badge>
                  </div>
                  <Badge variant="outline">
                    {policy.appliedToJobs} aktiva jobb
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  Används för crawling med {policy.rules.rateLimit.requestsPerSecond} req/s rate limit
                </div>
                <div className="mt-3 flex space-x-2">
                  <Button variant="outline" size="sm">
                    <Eye className="w-4 h-4 mr-2" />
                    Visa jobb
                  </Button>
                  <Button variant="outline" size="sm">
                    <Pause className="w-4 h-4 mr-2" />
                    Pausa tillämpning
                  </Button>
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
          <h1 className="text-3xl font-bold text-foreground">Policies</h1>
          <p className="text-muted-foreground">Hantera crawling-policyer och compliance-regler</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <FileText className="w-4 h-4 mr-2" />
            Exportera policyer
          </Button>
          <Button variant="outline">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="list">Policyer</TabsTrigger>
          <TabsTrigger value="editor">Redigerare</TabsTrigger>
          <TabsTrigger value="simulation">Simulering</TabsTrigger>
          <TabsTrigger value="applied">Tillämpade</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-6">
          {renderPolicyList()}
        </TabsContent>

        <TabsContent value="editor" className="mt-6">
          {selectedPolicy ? renderPolicyEditor() : (
            <div className="text-center py-12">
              <Edit className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">Ingen policy vald</h3>
              <p className="text-muted-foreground">Välj en policy från listan eller skapa en ny</p>
            </div>
          )}
        </TabsContent>

        <TabsContent value="simulation" className="mt-6">
          {renderSimulation()}
        </TabsContent>

        <TabsContent value="applied" className="mt-6">
          {renderAppliedPolicies()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Policies;
