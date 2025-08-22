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
  Plus, 
  Trash2, 
  Play, 
  Save, 
  BarChart3,
  Settings,
  Globe,
  Link,
  FileText,
  Clock,
  Target,
  Zap,
  AlertTriangle,
  CheckCircle,
  Eye
} from 'lucide-react';

interface CrawlPlan {
  metadata: {
    name: string;
    description: string;
    tags: string[];
  };
  startUrls: string[];
  linkRules: {
    include: string[];
    exclude: string[];
    maxDepth: number;
    domainScope: 'internal' | 'subdomains' | 'external';
    followCanonicals: boolean;
    followNoFollow: boolean;
  };
  pagination: {
    nextButtonSelector?: string;
    maxPages: number;
    queryParam?: {
      name: string;
      start: number;
      step: number;
      stop: number;
    };
    infiniteScroll?: {
      sentinelSelector: string;
      timeout: number;
    };
  };
  politeness: {
    globalConcurrency: number;
    perHostConcurrency: number;
    perHostDelay: number;
    rateLimit: {
      requestsPerSecond: number;
      perHost: number;
    };
    respectRobotsTxt: boolean;
    userAgent: string;
  };
  budgets: {
    maxPages: number;
    timebudget: number; // hours
    byteBudget: number; // GB
    dupeBudget: number; // percentage
  };
}

interface SimulationResult {
  estimatedPages: number;
  estimatedRuntime: number; // minutes
  urlSample: string[];
  filteredOut: number;
  warnings: string[];
}

const CrawlPlanStudio = () => {
  const [activeTab, setActiveTab] = useState<'plan' | 'simulation' | 'policy'>('plan');
  const [plan, setPlan] = useState<CrawlPlan>({
    metadata: {
      name: '',
      description: '',
      tags: []
    },
    startUrls: [''],
    linkRules: {
      include: [],
      exclude: [],
      maxDepth: 3,
      domainScope: 'internal',
      followCanonicals: true,
      followNoFollow: false
    },
    pagination: {
      maxPages: 50
    },
    politeness: {
      globalConcurrency: 16,
      perHostConcurrency: 2,
      perHostDelay: 1000,
      rateLimit: {
        requestsPerSecond: 10,
        perHost: 2
      },
      respectRobotsTxt: true,
      userAgent: 'ECaDP-Crawler/1.0'
    },
    budgets: {
      maxPages: 10000,
      timebudget: 2,
      byteBudget: 5,
      dupeBudget: 20
    }
  });

  const [simulation, setSimulation] = useState<SimulationResult>({
    estimatedPages: 0,
    estimatedRuntime: 0,
    urlSample: [],
    filteredOut: 0,
    warnings: []
  });

  const [isSimulating, setIsSimulating] = useState(false);

  const updatePlan = (path: string, value: any) => {
    setPlan(prev => {
      const newPlan = { ...prev };
      const pathArray = path.split('.');
      let current: any = newPlan;
      
      for (let i = 0; i < pathArray.length - 1; i++) {
        current = current[pathArray[i]];
      }
      
      current[pathArray[pathArray.length - 1]] = value;
      return newPlan;
    });
  };

  const addStartUrl = () => {
    setPlan(prev => ({
      ...prev,
      startUrls: [...prev.startUrls, '']
    }));
  };

  const updateStartUrl = (index: number, url: string) => {
    setPlan(prev => ({
      ...prev,
      startUrls: prev.startUrls.map((u, i) => i === index ? url : u)
    }));
  };

  const removeStartUrl = (index: number) => {
    setPlan(prev => ({
      ...prev,
      startUrls: prev.startUrls.filter((_, i) => i !== index)
    }));
  };

  const addRule = (type: 'include' | 'exclude') => {
    setPlan(prev => ({
      ...prev,
      linkRules: {
        ...prev.linkRules,
        [type]: [...prev.linkRules[type], '']
      }
    }));
  };

  const updateRule = (type: 'include' | 'exclude', index: number, value: string) => {
    setPlan(prev => ({
      ...prev,
      linkRules: {
        ...prev.linkRules,
        [type]: prev.linkRules[type].map((rule, i) => i === index ? value : rule)
      }
    }));
  };

  const removeRule = (type: 'include' | 'exclude', index: number) => {
    setPlan(prev => ({
      ...prev,
      linkRules: {
        ...prev.linkRules,
        [type]: prev.linkRules[type].filter((_, i) => i !== index)
      }
    }));
  };

  const runSimulation = async () => {
    setIsSimulating(true);
    
    // Simulate API call
    setTimeout(() => {
      setSimulation({
        estimatedPages: Math.floor(Math.random() * 5000) + 500,
        estimatedRuntime: Math.floor(Math.random() * 120) + 30,
        urlSample: [
          'https://example.com/page/1',
          'https://example.com/page/2',
          'https://example.com/category/cars',
          'https://example.com/detail/abc123'
        ],
        filteredOut: Math.floor(Math.random() * 200),
        warnings: [
          'Robots.txt disallows /admin/* paths',
          'High pagination depth detected'
        ]
      });
      setIsSimulating(false);
    }, 2000);
  };

  const renderPlanConfiguration = () => (
    <div className="space-y-6">
      {/* Metadata */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Planmetadata</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="planName">Plannamn *</Label>
              <Input
                id="planName"
                value={plan.metadata.name}
                onChange={(e) => updatePlan('metadata.name', e.target.value)}
                placeholder="t.ex. biluppgifter-crawl-2024"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="planDescription">Beskrivning</Label>
              <Input
                id="planDescription"
                value={plan.metadata.description}
                onChange={(e) => updatePlan('metadata.description', e.target.value)}
                placeholder="Kort beskrivning av crawlplanen..."
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Start URLs */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Start-URLs</CardTitle>
            <Button variant="outline" size="sm" onClick={addStartUrl}>
              <Plus className="w-4 h-4 mr-2" />
              Lägg till URL
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {plan.startUrls.map((url, index) => (
            <div key={index} className="flex items-center space-x-2">
              <Input
                value={url}
                onChange={(e) => updateStartUrl(index, e.target.value)}
                placeholder="https://example.com/start"
                className="flex-1"
              />
              {plan.startUrls.length > 1 && (
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => removeStartUrl(index)}
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Link Rules */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Länkregler</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Include Rules */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Inkludera (regex)</Label>
                <Button variant="outline" size="sm" onClick={() => addRule('include')}>
                  <Plus className="w-3 h-3" />
                </Button>
              </div>
              {plan.linkRules.include.map((rule, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    value={rule}
                    onChange={(e) => updateRule('include', index, e.target.value)}
                    placeholder=".*\/products\/.*"
                    className="flex-1 font-mono text-sm"
                  />
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => removeRule('include', index)}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              ))}
            </div>

            {/* Exclude Rules */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Exkludera (regex)</Label>
                <Button variant="outline" size="sm" onClick={() => addRule('exclude')}>
                  <Plus className="w-3 h-3" />
                </Button>
              </div>
              {plan.linkRules.exclude.map((rule, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Input
                    value={rule}
                    onChange={(e) => updateRule('exclude', index, e.target.value)}
                    placeholder=".*\/admin\/.*"
                    className="flex-1 font-mono text-sm"
                  />
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => removeRule('exclude', index)}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Max djup</Label>
              <Input
                type="number"
                value={plan.linkRules.maxDepth}
                onChange={(e) => updatePlan('linkRules.maxDepth', parseInt(e.target.value) || 3)}
                min="1"
                max="10"
              />
            </div>
            <div className="space-y-2">
              <Label>Domänscope</Label>
              <Select value={plan.linkRules.domainScope} onValueChange={(value) => updatePlan('linkRules.domainScope', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="internal">Endast samma domän</SelectItem>
                  <SelectItem value="subdomains">Subdomäner OK</SelectItem>
                  <SelectItem value="external">Externa tillåtna</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Canonicals & NoFollow</Label>
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="followCanonicals"
                    checked={plan.linkRules.followCanonicals}
                    onCheckedChange={(checked) => updatePlan('linkRules.followCanonicals', checked)}
                  />
                  <Label htmlFor="followCanonicals" className="text-sm">Följ canonicals</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="followNoFollow"
                    checked={plan.linkRules.followNoFollow}
                    onCheckedChange={(checked) => updatePlan('linkRules.followNoFollow', checked)}
                  />
                  <Label htmlFor="followNoFollow" className="text-sm">Följ nofollow</Label>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pagination */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Paginering</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Nästa-knapp selektor</Label>
              <Input
                value={plan.pagination.nextButtonSelector || ''}
                onChange={(e) => updatePlan('pagination.nextButtonSelector', e.target.value)}
                placeholder="a.next, .pagination .next"
                className="font-mono text-sm"
              />
            </div>
            <div className="space-y-2">
              <Label>Max sidor</Label>
              <Input
                type="number"
                value={plan.pagination.maxPages}
                onChange={(e) => updatePlan('pagination.maxPages', parseInt(e.target.value) || 50)}
                min="1"
                max="1000"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Politeness */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Politeness & Samtidighet</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Global samtidighet</Label>
              <Input
                type="number"
                value={plan.politeness.globalConcurrency}
                onChange={(e) => updatePlan('politeness.globalConcurrency', parseInt(e.target.value) || 16)}
                min="1"
                max="100"
              />
            </div>
            <div className="space-y-2">
              <Label>Per värd samtidighet</Label>
              <Input
                type="number"
                value={plan.politeness.perHostConcurrency}
                onChange={(e) => updatePlan('politeness.perHostConcurrency', parseInt(e.target.value) || 2)}
                min="1"
                max="10"
              />
            </div>
            <div className="space-y-2">
              <Label>Delay per värd (ms)</Label>
              <Input
                type="number"
                value={plan.politeness.perHostDelay}
                onChange={(e) => updatePlan('politeness.perHostDelay', parseInt(e.target.value) || 1000)}
                min="0"
                max="10000"
              />
            </div>
            <div className="space-y-2">
              <Label>Rate limit (req/s)</Label>
              <Input
                type="number"
                value={plan.politeness.rateLimit.requestsPerSecond}
                onChange={(e) => updatePlan('politeness.rateLimit.requestsPerSecond', parseInt(e.target.value) || 10)}
                min="1"
                max="100"
              />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="respectRobotsTxt"
                checked={plan.politeness.respectRobotsTxt}
                onCheckedChange={(checked) => updatePlan('politeness.respectRobotsTxt', checked)}
              />
              <Label htmlFor="respectRobotsTxt">Respektera robots.txt</Label>
            </div>
            <div className="space-y-2 flex-1">
              <Label>User Agent</Label>
              <Input
                value={plan.politeness.userAgent}
                onChange={(e) => updatePlan('politeness.userAgent', e.target.value)}
                placeholder="ECaDP-Crawler/1.0"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Budgets */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Budgetar & Stopp</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Max sidor</Label>
              <Input
                type="number"
                value={plan.budgets.maxPages}
                onChange={(e) => updatePlan('budgets.maxPages', parseInt(e.target.value) || 10000)}
                min="1"
              />
            </div>
            <div className="space-y-2">
              <Label>Tidsbudget (timmar)</Label>
              <Input
                type="number"
                value={plan.budgets.timebudget}
                onChange={(e) => updatePlan('budgets.timebudget', parseInt(e.target.value) || 2)}
                min="0.5"
                step="0.5"
              />
            </div>
            <div className="space-y-2">
              <Label>Byte-budget (GB)</Label>
              <Input
                type="number"
                value={plan.budgets.byteBudget}
                onChange={(e) => updatePlan('budgets.byteBudget', parseInt(e.target.value) || 5)}
                min="1"
              />
            </div>
            <div className="space-y-2">
              <Label>Dupe-budget (%)</Label>
              <Input
                type="number"
                value={plan.budgets.dupeBudget}
                onChange={(e) => updatePlan('budgets.dupeBudget', parseInt(e.target.value) || 20)}
                min="1"
                max="100"
              />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSimulation = () => (
    <div className="space-y-6">
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Simulering</CardTitle>
            <Button onClick={runSimulation} disabled={isSimulating}>
              {isSimulating ? (
                <Settings className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Play className="w-4 h-4 mr-2" />
              )}
              {isSimulating ? 'Simulerar...' : 'Kör simulering'}
            </Button>
          </div>
          <CardDescription>
            Uppskatta omfattning och runtime innan crawling
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isSimulating ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-center">
                <Settings className="w-8 h-8 text-primary animate-spin mx-auto mb-2" />
                <p className="text-muted-foreground">Analyserar URL-struktur...</p>
              </div>
            </div>
          ) : simulation.estimatedPages > 0 ? (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="border-sidebar-border">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{simulation.estimatedPages.toLocaleString()}</div>
                    <div className="text-sm text-muted-foreground">Estimerade sidor</div>
                  </CardContent>
                </Card>
                <Card className="border-sidebar-border">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{Math.floor(simulation.estimatedRuntime / 60)}h {simulation.estimatedRuntime % 60}m</div>
                    <div className="text-sm text-muted-foreground">Estimerad runtime</div>
                  </CardContent>
                </Card>
                <Card className="border-sidebar-border">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{simulation.filteredOut}</div>
                    <div className="text-sm text-muted-foreground">Filtrerade URLs</div>
                  </CardContent>
                </Card>
                <Card className="border-sidebar-border">
                  <CardContent className="p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{simulation.warnings.length}</div>
                    <div className="text-sm text-muted-foreground">Varningar</div>
                  </CardContent>
                </Card>
              </div>

              {/* URL Sample */}
              <Card className="border-sidebar-border">
                <CardHeader>
                  <CardTitle className="text-base">URL-exempel</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {simulation.urlSample.map((url, index) => (
                      <div key={index} className="font-mono text-sm bg-muted/50 p-2 rounded">
                        {url}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Warnings */}
              {simulation.warnings.length > 0 && (
                <Card className="border-sidebar-border border-warning">
                  <CardHeader>
                    <CardTitle className="text-base flex items-center">
                      <AlertTriangle className="w-4 h-4 mr-2 text-warning" />
                      Varningar
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {simulation.warnings.map((warning, index) => (
                        <div key={index} className="text-sm text-warning bg-warning/10 p-2 rounded">
                          {warning}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <div className="text-center py-8">
              <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">Kör simulering för att se estimat</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );

  const renderPolicyPanel = () => (
    <div className="space-y-6">
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Policy-sammanfattning</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label className="text-sm font-medium">Robots.txt status</Label>
              <div className="mt-1">
                <Badge className="bg-success/10 text-success">
                  <CheckCircle className="w-3 h-3 mr-1" />
                  Respekteras
                </Badge>
              </div>
            </div>
            <div>
              <Label className="text-sm font-medium">Rate limiting</Label>
              <div className="mt-1">
                <Badge className="bg-primary/10 text-primary">
                  {plan.politeness.rateLimit.requestsPerSecond} req/s
                </Badge>
              </div>
            </div>
          </div>

          <div>
            <Label className="text-sm font-medium">Estimerad kostnad</Label>
            <div className="mt-1 text-sm text-muted-foreground">
              Baserat på {simulation.estimatedPages} sidor × ~2KB = {((simulation.estimatedPages * 2) / 1024).toFixed(1)} MB transfer
            </div>
          </div>

          <div>
            <Label className="text-sm font-medium">Resursutnyttjande</Label>
            <div className="mt-1 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>CPU (estimat)</span>
                <span>~25%</span>
              </div>
              <Progress value={25} className="h-2" />
              <div className="flex items-center justify-between text-sm">
                <span>Nätverk</span>
                <span>~{plan.politeness.rateLimit.requestsPerSecond * 2}KB/s</span>
              </div>
              <Progress value={40} className="h-2" />
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
          <h1 className="text-3xl font-bold text-foreground">Crawl Plan Studio</h1>
          <p className="text-muted-foreground">Definiera och simulera crawling-strategier</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Save className="w-4 h-4 mr-2" />
            Spara plan
          </Button>
          <Button>
            <Play className="w-4 h-4 mr-2" />
            Kör som jobb
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="plan">Plankonfiguration</TabsTrigger>
          <TabsTrigger value="simulation">Simulering</TabsTrigger>
          <TabsTrigger value="policy">Policy & Kostnad</TabsTrigger>
        </TabsList>

        <TabsContent value="plan" className="mt-6">
          {renderPlanConfiguration()}
        </TabsContent>

        <TabsContent value="simulation" className="mt-6">
          {renderSimulation()}
        </TabsContent>

        <TabsContent value="policy" className="mt-6">
          {renderPolicyPanel()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CrawlPlanStudio;
