import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Database, 
  Globe, 
  Play, 
  Settings, 
  FileText,
  ArrowRight,
  ArrowLeft,
  X,
  Eye,
  EyeOff,
  TestTube,
  CheckSquare,
  Server,
  Docker
} from 'lucide-react';

interface PreflightCheck {
  name: string;
  status: 'pending' | 'success' | 'warning' | 'error';
  version?: string;
  message?: string;
}

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
}

const OnboardingWizard = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [dbTesting, setDbTesting] = useState(false);
  const [dbTestResult, setDbTestResult] = useState<any>(null);
  const [syntheticStatus, setSyntheticStatus] = useState<any>(null);

  // Preflight checks state
  const [preflightChecks, setPreflightChecks] = useState<PreflightCheck[]>([
    { name: 'Python ≥ 3.11', status: 'pending' },
    { name: 'Docker + Docker Compose', status: 'pending' },
    { name: 'Node.js LTS + npm', status: 'pending' },
    { name: 'MySQL Client Libraries', status: 'pending' }
  ]);

  // Form state
  const [formData, setFormData] = useState({
    // Organization
    orgName: '',
    notifyEmail: '',
    consentToNotifications: false,
    
    // Database
    dbType: 'mysql',
    dbHost: '127.0.0.1',
    dbPort: '3306',
    dbName: 'crawler',
    dbUser: 'root',
    dbPassword: '',
    dbSSL: false,
    dbSSLMode: 'DISABLED',
    dbCharset: 'utf8mb4',
    dbCollation: 'utf8mb4_0900_ai_ci',
    dbTimezone: 'Europe/Stockholm',
    dbPoolSize: 10,
    dbIdleTimeout: 300,
    dbAutoMigrations: true,
    dbSavePasswordSecurely: true,
    
    // Synthetic sites
    syntheticEnabled: true,
    syntheticPorts: {
      static: 8081,
      infiniteScroll: 8082,
      formFlow: 8083
    },
    syntheticNetwork: 'bridge',
    syntheticAutoFix: true,
    
    // First project
    projectName: 'Mitt första projekt',
    startUrl: 'https://example.com',
    renderingPolicy: 'auto',
    respectRobots: true,
    rateLimit: 1.5,
    geography: 'SE',
    createCrawlPlan: false,
    nextSelector: '',
    
    // Default policies
    acceptLanguage: 'sv-SE,sv;q=0.9,en;q=0.7',
    userAgentProfile: 'desktop_chrome',
    politenessDelay: 2000,
    consentStrategy: 'auto',
    dataRetention: 90,
    criticalAlerts: true
  });

  const steps: OnboardingStep[] = [
    { id: 'preflight', title: 'Förutsättningskontroll', description: 'Kontrollerar systemkrav', completed: false },
    { id: 'organization', title: 'Organisationsuppgifter', description: 'Företagsinformation och kontakt', completed: false },
    { id: 'database', title: 'Databasanslutning', description: 'Konfigurera MySQL-anslutning', completed: false },
    { id: 'synthetic', title: 'Syntetiska testsajter', description: 'Docker-baserade testmiljöer', completed: false },
    { id: 'project', title: 'Första projektet', description: 'Skapa din första datakälla', completed: false },
    { id: 'policies', title: 'Standardpolicies', description: 'Konfigurera standardinställningar', completed: false },
    { id: 'summary', title: 'Sammandrag', description: 'Granska och slutför', completed: false }
  ];

  // Run preflight checks on mount
  useEffect(() => {
    runPreflightChecks();
  }, []);

  const runPreflightChecks = async () => {
    const checks = [...preflightChecks];
    
    for (let i = 0; i < checks.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      switch (i) {
        case 0: // Python
          checks[i] = { name: 'Python ≥ 3.11', status: 'success', version: '3.11.5' };
          break;
        case 1: // Docker
          checks[i] = { name: 'Docker + Docker Compose', status: 'success', version: 'Docker 24.0.6, Compose v2.21.0' };
          break;
        case 2: // Node.js
          checks[i] = { name: 'Node.js LTS + npm', status: 'success', version: 'v18.17.1, npm 9.6.7' };
          break;
        case 3: // MySQL
          checks[i] = { name: 'MySQL Client Libraries', status: 'success', version: 'mysqlclient 2.2.0' };
          break;
      }
      
      setPreflightChecks([...checks]);
    }
  };

  const testDatabaseConnection = async () => {
    setDbTesting(true);
    setDbTestResult(null);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setDbTestResult({
        success: true,
        serverVersion: 'MySQL 8.0.34',
        timezone: 'Europe/Stockholm',
        canMigrate: true,
        needsDbCreate: false
      });
    } catch (error) {
      setDbTestResult({
        success: false,
        error: 'ECONNREFUSED',
        message: 'Kontrollera host/port och att MySQL kör.'
      });
    } finally {
      setDbTesting(false);
    }
  };

  const startSyntheticSites = async () => {
    setIsLoading(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setSyntheticStatus({
        sites: [
          { name: 'Statisk lista', port: formData.syntheticPorts.static, status: 'healthy', url: `http://localhost:${formData.syntheticPorts.static}` },
          { name: 'Oändlig scroll', port: formData.syntheticPorts.infiniteScroll, status: 'healthy', url: `http://localhost:${formData.syntheticPorts.infiniteScroll}` },
          { name: 'Formflöde', port: formData.syntheticPorts.formFlow, status: 'healthy', url: `http://localhost:${formData.syntheticPorts.formFlow}` }
        ]
      });
    } finally {
      setIsLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: // Preflight
        return preflightChecks.every(check => check.status === 'success');
      case 1: // Organization
        return formData.orgName.length > 0;
      case 2: // Database
        return dbTestResult?.success || false;
      case 3: // Synthetic
        return !formData.syntheticEnabled || syntheticStatus;
      case 4: // Project
        return formData.projectName.length > 0 && formData.startUrl.length > 0;
      default:
        return true;
    }
  };

  const renderPreflightStep = () => (
    <Card className="border-sidebar-border">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <CheckSquare className="w-5 h-5 text-primary" />
          <span>Systemkrav</span>
        </CardTitle>
        <CardDescription>Kontrollerar att alla nödvändiga komponenter är installerade</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {preflightChecks.map((check, index) => (
          <div key={index} className="flex items-center justify-between p-3 rounded-lg border border-sidebar-border">
            <div className="flex items-center space-x-3">
              {check.status === 'pending' && <Clock className="w-4 h-4 text-muted-foreground animate-spin" />}
              {check.status === 'success' && <CheckCircle className="w-4 h-4 text-success" />}
              {check.status === 'warning' && <AlertTriangle className="w-4 h-4 text-warning" />}
              {check.status === 'error' && <X className="w-4 h-4 text-destructive" />}
              <div>
                <p className="font-medium text-foreground">{check.name}</p>
                {check.version && <p className="text-sm text-muted-foreground">{check.version}</p>}
              </div>
            </div>
            {check.status === 'success' && (
              <Badge className="bg-success/10 text-success border-success/20">OK</Badge>
            )}
          </div>
        ))}
        
        {preflightChecks.every(check => check.status === 'success') && (
          <div className="mt-6 p-4 rounded-lg bg-success/10 border border-success/20">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-success" />
              <p className="text-success font-medium">Alla systemkrav uppfyllda!</p>
            </div>
            <p className="text-sm text-success/80 mt-1">Du kan fortsätta med konfigurationen.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );

  const renderOrganizationStep = () => (
    <Card className="border-sidebar-border">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-primary" />
          <span>Organisationsuppgifter</span>
        </CardTitle>
        <CardDescription>Grundläggande information om din organisation</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="orgName">Organisationsnamn *</Label>
          <Input
            id="orgName"
            value={formData.orgName}
            onChange={(e) => setFormData({ ...formData, orgName: e.target.value })}
            placeholder="Ditt företag AB"
            maxLength={80}
            required
          />
          {!formData.orgName && (
            <p className="text-sm text-destructive">Ange organisationsnamn</p>
          )}
        </div>

        <div className="space-y-2">
          <Label htmlFor="notifyEmail">E-post för aviseringar</Label>
          <Input
            id="notifyEmail"
            type="email"
            value={formData.notifyEmail}
            onChange={(e) => setFormData({ ...formData, notifyEmail: e.target.value })}
            placeholder="driftansvarig@företag.se"
          />
          <p className="text-sm text-muted-foreground">
            E-posten används för driftlarm (misslyckade jobb, låg proxyhälsa).
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="consentToNotifications"
            checked={formData.consentToNotifications}
            onCheckedChange={(checked) => 
              setFormData({ ...formData, consentToNotifications: checked as boolean })
            }
          />
          <Label htmlFor="consentToNotifications">Samtycke till aviseringar</Label>
        </div>
      </CardContent>
    </Card>
  );

  const renderDatabaseStep = () => (
    <Card className="border-sidebar-border">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Database className="w-5 h-5 text-primary" />
          <span>Databasanslutning</span>
        </CardTitle>
        <CardDescription>Konfigurera MySQL-anslutning för datalagring</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="dbHost">Host</Label>
            <Input
              id="dbHost"
              value={formData.dbHost}
              onChange={(e) => setFormData({ ...formData, dbHost: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="dbPort">Port</Label>
            <Input
              id="dbPort"
              type="number"
              value={formData.dbPort}
              onChange={(e) => setFormData({ ...formData, dbPort: e.target.value })}
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="dbName">Databas</Label>
            <Input
              id="dbName"
              value={formData.dbName}
              onChange={(e) => setFormData({ ...formData, dbName: e.target.value })}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="dbUser">Användare</Label>
            <Input
              id="dbUser"
              value={formData.dbUser}
              onChange={(e) => setFormData({ ...formData, dbUser: e.target.value })}
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="dbPassword">Lösenord</Label>
          <div className="relative">
            <Input
              id="dbPassword"
              type={showPassword ? "text" : "password"}
              value={formData.dbPassword}
              onChange={(e) => setFormData({ ...formData, dbPassword: e.target.value })}
            />
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="absolute right-0 top-0 h-full px-3"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </Button>
          </div>
        </div>

        <Accordion type="single" collapsible>
          <AccordionItem value="advanced">
            <AccordionTrigger>Avancerade inställningar</AccordionTrigger>
            <AccordionContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="dbCharset">Teckenuppsättning</Label>
                  <Input
                    id="dbCharset"
                    value={formData.dbCharset}
                    onChange={(e) => setFormData({ ...formData, dbCharset: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dbTimezone">Tidszon</Label>
                  <Input
                    id="dbTimezone"
                    value={formData.dbTimezone}
                    onChange={(e) => setFormData({ ...formData, dbTimezone: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="dbAutoMigrations"
                  checked={formData.dbAutoMigrations}
                  onCheckedChange={(checked) => 
                    setFormData({ ...formData, dbAutoMigrations: checked as boolean })
                  }
                />
                <Label htmlFor="dbAutoMigrations">Automatiska migrationer</Label>
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="dbSavePasswordSecurely"
                  checked={formData.dbSavePasswordSecurely}
                  onCheckedChange={(checked) => 
                    setFormData({ ...formData, dbSavePasswordSecurely: checked as boolean })
                  }
                />
                <Label htmlFor="dbSavePasswordSecurely">Spara lösenord säkert</Label>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={testDatabaseConnection}
            disabled={dbTesting}
          >
            {dbTesting && <Clock className="w-4 h-4 mr-2 animate-spin" />}
            <TestTube className="w-4 h-4 mr-2" />
            Testa databasanslutning
          </Button>
          
          {dbTestResult && (
            <div className={`flex items-center space-x-2 ${
              dbTestResult.success ? 'text-success' : 'text-destructive'
            }`}>
              {dbTestResult.success ? (
                <CheckCircle className="w-4 h-4" />
              ) : (
                <X className="w-4 h-4" />
              )}
              <span className="text-sm">
                {dbTestResult.success 
                  ? `${dbTestResult.serverVersion} upptäckt. Migration redo.`
                  : dbTestResult.message
                }
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );

  const renderSyntheticStep = () => (
    <Card className="border-sidebar-border">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Docker className="w-5 h-5 text-primary" />
          <span>Syntetiska testsajter</span>
        </CardTitle>
        <CardDescription>Docker-baserade testmiljöer för att öva crawling</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex items-center space-x-2">
          <Checkbox
            id="syntheticEnabled"
            checked={formData.syntheticEnabled}
            onCheckedChange={(checked) => 
              setFormData({ ...formData, syntheticEnabled: checked as boolean })
            }
          />
          <Label htmlFor="syntheticEnabled">Starta syntetiska testsajter i Docker</Label>
        </div>

        {formData.syntheticEnabled && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="staticPort">Statisk lista (port)</Label>
                <Input
                  id="staticPort"
                  type="number"
                  value={formData.syntheticPorts.static}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    syntheticPorts: { 
                      ...formData.syntheticPorts, 
                      static: parseInt(e.target.value) 
                    } 
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="scrollPort">Oändlig scroll (port)</Label>
                <Input
                  id="scrollPort"
                  type="number"
                  value={formData.syntheticPorts.infiniteScroll}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    syntheticPorts: { 
                      ...formData.syntheticPorts, 
                      infiniteScroll: parseInt(e.target.value) 
                    } 
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="formPort">Formflöde (port)</Label>
                <Input
                  id="formPort"
                  type="number"
                  value={formData.syntheticPorts.formFlow}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    syntheticPorts: { 
                      ...formData.syntheticPorts, 
                      formFlow: parseInt(e.target.value) 
                    } 
                  })}
                />
              </div>
            </div>

            <Button
              onClick={startSyntheticSites}
              disabled={isLoading}
              className="bg-gradient-primary"
            >
              {isLoading && <Clock className="w-4 h-4 mr-2 animate-spin" />}
              <Play className="w-4 h-4 mr-2" />
              Starta testsajter
            </Button>

            {syntheticStatus && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                {syntheticStatus.sites.map((site: any, index: number) => (
                  <Card key={index} className="border-sidebar-border">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-foreground">{site.name}</h4>
                        <Badge className="bg-success/10 text-success border-success/20">
                          {site.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">Port: {site.port}</p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(site.url, '_blank')}
                      >
                        <Globe className="w-4 h-4 mr-2" />
                        Öppna
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );

  const renderProjectStep = () => (
    <Card className="border-sidebar-border">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <FileText className="w-5 h-5 text-primary" />
          <span>Första projektet</span>
        </CardTitle>
        <CardDescription>Skapa din första datakälla för crawling</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="projectName">Projektnamn *</Label>
          <Input
            id="projectName"
            value={formData.projectName}
            onChange={(e) => setFormData({ ...formData, projectName: e.target.value })}
            placeholder="Mitt första projekt"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="startUrl">Start-URL *</Label>
          <Input
            id="startUrl"
            type="url"
            value={formData.startUrl}
            onChange={(e) => setFormData({ ...formData, startUrl: e.target.value })}
            placeholder="https://example.com"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="renderingPolicy">Renderingspolicy</Label>
            <Select
              value={formData.renderingPolicy}
              onValueChange={(value) => setFormData({ ...formData, renderingPolicy: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto</SelectItem>
                <SelectItem value="http">HTTP</SelectItem>
                <SelectItem value="browser">Browser</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="geography">Geografi</Label>
            <Select
              value={formData.geography}
              onValueChange={(value) => setFormData({ ...formData, geography: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="SE">Sverige (SE)</SelectItem>
                <SelectItem value="NO">Norge (NO)</SelectItem>
                <SelectItem value="DK">Danmark (DK)</SelectItem>
                <SelectItem value="FI">Finland (FI)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="rateLimit">Rate limit (RPS)</Label>
          <Input
            id="rateLimit"
            type="number"
            step="0.1"
            value={formData.rateLimit}
            onChange={(e) => setFormData({ ...formData, rateLimit: parseFloat(e.target.value) })}
          />
        </div>

        <div className="flex items-center space-x-2">
          <Checkbox
            id="respectRobots"
            checked={formData.respectRobots}
            onCheckedChange={(checked) => 
              setFormData({ ...formData, respectRobots: checked as boolean })
            }
          />
          <Label htmlFor="respectRobots">Respektera robots.txt (rekommenderat)</Label>
        </div>
      </CardContent>
    </Card>
  );

  const renderSummaryStep = () => (
    <Card className="border-sidebar-border">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <CheckCircle className="w-5 h-5 text-primary" />
          <span>Sammandrag</span>
        </CardTitle>
        <CardDescription>Granska dina inställningar innan du slutför</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-foreground mb-2">Organisation</h4>
              <p className="text-sm text-muted-foreground">Namn: {formData.orgName}</p>
              {formData.notifyEmail && (
                <p className="text-sm text-muted-foreground">E-post: {formData.notifyEmail}</p>
              )}
            </div>

            <div>
              <h4 className="font-medium text-foreground mb-2">Databas</h4>
              <p className="text-sm text-muted-foreground">
                {formData.dbHost}:{formData.dbPort}/{formData.dbName}
              </p>
              <p className="text-sm text-muted-foreground">Användare: {formData.dbUser}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-foreground mb-2">Första projektet</h4>
              <p className="text-sm text-muted-foreground">Namn: {formData.projectName}</p>
              <p className="text-sm text-muted-foreground">URL: {formData.startUrl}</p>
              <p className="text-sm text-muted-foreground">Rendering: {formData.renderingPolicy}</p>
            </div>

            {formData.syntheticEnabled && (
              <div>
                <h4 className="font-medium text-foreground mb-2">Testsajter</h4>
                <p className="text-sm text-muted-foreground">
                  Portar: {formData.syntheticPorts.static}, {formData.syntheticPorts.infiniteScroll}, {formData.syntheticPorts.formFlow}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="bg-success/10 border border-success/20 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-success" />
            <p className="text-success font-medium">Allt klart för slutförande!</p>
          </div>
          <p className="text-sm text-success/80 mt-1">
            Dina inställningar kommer att sparas och systemet konfigureras automatiskt.
          </p>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Onboarding Guide</h1>
          <p className="text-muted-foreground">Kom igång med ECaDP genom att följa dessa steg</p>
        </div>
      </div>

      {/* Progress indicator */}
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                index === currentStep 
                  ? 'bg-primary text-primary-foreground'
                  : index < currentStep 
                    ? 'bg-success text-success-foreground'
                    : 'bg-muted text-muted-foreground'
              }`}>
                {index < currentStep ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  index + 1
                )}
              </div>
              {index < steps.length - 1 && (
                <div className={`w-12 h-0.5 mx-2 ${
                  index < currentStep ? 'bg-success' : 'bg-muted'
                }`} />
              )}
            </div>
          ))}
        </div>
        <div>
          <h2 className="text-xl font-semibold text-foreground">{steps[currentStep].title}</h2>
          <p className="text-sm text-muted-foreground">{steps[currentStep].description}</p>
        </div>
      </div>

      {/* Step content */}
      <div className="min-h-[500px]">
        {currentStep === 0 && renderPreflightStep()}
        {currentStep === 1 && renderOrganizationStep()}
        {currentStep === 2 && renderDatabaseStep()}
        {currentStep === 3 && renderSyntheticStep()}
        {currentStep === 4 && renderProjectStep()}
        {currentStep === 5 && renderProjectStep()} {/* Placeholder for policies */}
        {currentStep === 6 && renderSummaryStep()}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 0}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Tillbaka
        </Button>
        
        <div className="flex items-center space-x-4">
          {currentStep < steps.length - 1 ? (
            <Button
              onClick={nextStep}
              disabled={!canProceed()}
            >
              Nästa
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={() => window.location.href = '/'}
              disabled={!canProceed()}
              className="bg-gradient-primary"
            >
              Slutför
              <CheckCircle className="w-4 h-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
};

export default OnboardingWizard;