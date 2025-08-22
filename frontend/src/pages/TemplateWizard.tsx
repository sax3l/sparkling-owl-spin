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
  ChevronLeft, 
  ChevronRight, 
  Save, 
  Play, 
  Eye,
  FileText,
  Database,
  Code,
  Settings,
  CheckCircle,
  AlertTriangle,
  Plus,
  Trash2,
  Copy
} from 'lucide-react';

interface TemplateWizardProps {
  mode?: 'create' | 'edit';
  templateId?: string;
}

interface TemplateData {
  metadata: {
    name: string;
    version: string;
    description: string;
    tags: string[];
    author: string;
  };
  targetType: 'single' | 'list';
  structure: {
    listSelector?: string;
    detailUrlSelector?: string;
    detailUrlTemplate?: string;
    paginationSelector?: string;
  };
  listDetailConfig: {
    crawlMode: 'list_only' | 'list_detail' | 'detail_only';
    maxPages: number;
    followLinks: boolean;
  };
  fields: Array<{
    id: string;
    name: string;
    selector: string;
    type: 'text' | 'number' | 'url' | 'email' | 'date' | 'boolean';
    required: boolean;
    multiple: boolean;
    description?: string;
  }>;
  transformers: Array<{
    fieldId: string;
    type: 'regex' | 'format' | 'lookup' | 'calculation';
    config: Record<string, any>;
  }>;
  keys: {
    primaryKey: string[];
    uniqueKeys: string[][];
  };
  rendering: {
    mode: 'http' | 'js' | 'mobile';
    waitTime: number;
    viewport?: { width: number; height: number };
    userAgent?: string;
  };
  dqt: {
    rules: Array<{
      id: string;
      field: string;
      type: 'required' | 'format' | 'range' | 'custom';
      config: Record<string, any>;
      severity: 'error' | 'warning' | 'info';
    }>;
  };
}

const TemplateWizard = ({ mode = 'create', templateId }: TemplateWizardProps) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [templateData, setTemplateData] = useState<TemplateData>({
    metadata: {
      name: '',
      version: 'v1.0',
      description: '',
      tags: [],
      author: ''
    },
    targetType: 'single',
    structure: {},
    listDetailConfig: {
      crawlMode: 'list_only',
      maxPages: 10,
      followLinks: false
    },
    fields: [],
    transformers: [],
    keys: {
      primaryKey: [],
      uniqueKeys: []
    },
    rendering: {
      mode: 'http',
      waitTime: 2000
    },
    dqt: {
      rules: []
    }
  });

  const steps = [
    { id: 1, name: 'Metadata', icon: FileText },
    { id: 2, name: 'Måltyp & struktur', icon: Database },
    { id: 3, name: 'Lista/Detalj', icon: Settings },
    { id: 4, name: 'Fält & Selektorer', icon: Code },
    { id: 5, name: 'Transformers', icon: Settings },
    { id: 6, name: 'Nycklar', icon: Database },
    { id: 7, name: 'Renderingsläge', icon: Eye },
    { id: 8, name: 'DQT', icon: CheckCircle },
    { id: 9, name: 'Förhandsvisa', icon: Play },
    { id: 10, name: 'Spara & Publicera', icon: Save }
  ];

  const updateTemplateData = (path: string, value: any) => {
    setTemplateData(prev => {
      const newData = { ...prev };
      const pathArray = path.split('.');
      let current: any = newData;
      
      for (let i = 0; i < pathArray.length - 1; i++) {
        current = current[pathArray[i]];
      }
      
      current[pathArray[pathArray.length - 1]] = value;
      return newData;
    });
  };

  const addField = () => {
    const newField = {
      id: `field_${Date.now()}`,
      name: '',
      selector: '',
      type: 'text' as const,
      required: false,
      multiple: false
    };
    
    setTemplateData(prev => ({
      ...prev,
      fields: [...prev.fields, newField]
    }));
  };

  const removeField = (fieldId: string) => {
    setTemplateData(prev => ({
      ...prev,
      fields: prev.fields.filter(f => f.id !== fieldId)
    }));
  };

  const updateField = (fieldId: string, updates: Partial<typeof templateData.fields[0]>) => {
    setTemplateData(prev => ({
      ...prev,
      fields: prev.fields.map(f => f.id === fieldId ? { ...f, ...updates } : f)
    }));
  };

  const addDQRule = () => {
    const newRule = {
      id: `rule_${Date.now()}`,
      field: '',
      type: 'required' as const,
      config: {},
      severity: 'error' as const
    };
    
    setTemplateData(prev => ({
      ...prev,
      dqt: {
        ...prev.dqt,
        rules: [...prev.dqt.rules, newRule]
      }
    }));
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1: // Metadata
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="templateName">Mallnamn *</Label>
                <Input
                  id="templateName"
                  value={templateData.metadata.name}
                  onChange={(e) => updateTemplateData('metadata.name', e.target.value)}
                  placeholder="t.ex. vehicle_detail_v1"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="templateVersion">Version</Label>
                <Input
                  id="templateVersion"
                  value={templateData.metadata.version}
                  onChange={(e) => updateTemplateData('metadata.version', e.target.value)}
                  placeholder="v1.0"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="templateDescription">Beskrivning</Label>
              <Textarea
                id="templateDescription"
                value={templateData.metadata.description}
                onChange={(e) => updateTemplateData('metadata.description', e.target.value)}
                placeholder="Beskriv vad denna mall extraherar och från vilken källa..."
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="templateAuthor">Författare</Label>
              <Input
                id="templateAuthor"
                value={templateData.metadata.author}
                onChange={(e) => updateTemplateData('metadata.author', e.target.value)}
                placeholder="Ditt namn"
              />
            </div>

            <div className="space-y-2">
              <Label>Taggar</Label>
              <div className="flex flex-wrap gap-2">
                {templateData.metadata.tags.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="cursor-pointer" 
                         onClick={() => {
                           const newTags = templateData.metadata.tags.filter((_, i) => i !== index);
                           updateTemplateData('metadata.tags', newTags);
                         }}>
                    {tag} ×
                  </Badge>
                ))}
                <Input
                  placeholder="Lägg till tagg..."
                  className="w-32"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      const value = e.currentTarget.value.trim();
                      if (value && !templateData.metadata.tags.includes(value)) {
                        updateTemplateData('metadata.tags', [...templateData.metadata.tags, value]);
                        e.currentTarget.value = '';
                      }
                    }
                  }}
                />
              </div>
            </div>
          </div>
        );

      case 2: // Måltyp & struktur
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <Label>Måltyp</Label>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card 
                  className={`cursor-pointer border-2 ${templateData.targetType === 'single' ? 'border-primary' : 'border-muted'}`}
                  onClick={() => updateTemplateData('targetType', 'single')}
                >
                  <CardHeader>
                    <CardTitle className="text-base">Enskild sida</CardTitle>
                    <CardDescription>Extrahera data från en specifik sida</CardDescription>
                  </CardHeader>
                </Card>
                
                <Card 
                  className={`cursor-pointer border-2 ${templateData.targetType === 'list' ? 'border-primary' : 'border-muted'}`}
                  onClick={() => updateTemplateData('targetType', 'list')}
                >
                  <CardHeader>
                    <CardTitle className="text-base">Lista med objekt</CardTitle>
                    <CardDescription>Extrahera från listsida med länkar till detaljer</CardDescription>
                  </CardHeader>
                </Card>
              </div>
            </div>

            {templateData.targetType === 'list' && (
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="listSelector">CSS-selektor för listobjekt *</Label>
                  <Input
                    id="listSelector"
                    value={templateData.structure.listSelector || ''}
                    onChange={(e) => updateTemplateData('structure.listSelector', e.target.value)}
                    placeholder="t.ex. .search-result, .product-item"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="detailUrlSelector">CSS-selektor för detaljlänk</Label>
                  <Input
                    id="detailUrlSelector"
                    value={templateData.structure.detailUrlSelector || ''}
                    onChange={(e) => updateTemplateData('structure.detailUrlSelector', e.target.value)}
                    placeholder="t.ex. a.detail-link, .title a"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="paginationSelector">CSS-selektor för nästa sida</Label>
                  <Input
                    id="paginationSelector"
                    value={templateData.structure.paginationSelector || ''}
                    onChange={(e) => updateTemplateData('structure.paginationSelector', e.target.value)}
                    placeholder="t.ex. .next-page, a[rel='next']"
                  />
                </div>
              </div>
            )}
          </div>
        );

      case 3: // Lista/Detalj
        return (
          <div className="space-y-6">
            <div className="space-y-4">
              <Label>Crawling-läge</Label>
              <div className="space-y-2">
                {[
                  { value: 'list_only', label: 'Endast lista', description: 'Extrahera data direkt från listsidan' },
                  { value: 'list_detail', label: 'Lista + detaljer', description: 'Följ länkar från lista till detaljsidor' },
                  { value: 'detail_only', label: 'Endast detaljer', description: 'Direkt till detaljsidor (kräver URL-lista)' }
                ].map((mode) => (
                  <Card 
                    key={mode.value}
                    className={`cursor-pointer border-2 ${templateData.listDetailConfig.crawlMode === mode.value ? 'border-primary' : 'border-muted'}`}
                    onClick={() => updateTemplateData('listDetailConfig.crawlMode', mode.value)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center space-x-3">
                        <div className={`w-4 h-4 rounded-full border-2 ${templateData.listDetailConfig.crawlMode === mode.value ? 'bg-primary border-primary' : 'border-muted'}`} />
                        <div>
                          <CardTitle className="text-base">{mode.label}</CardTitle>
                          <CardDescription>{mode.description}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                  </Card>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="maxPages">Max antal sidor</Label>
                <Input
                  id="maxPages"
                  type="number"
                  value={templateData.listDetailConfig.maxPages}
                  onChange={(e) => updateTemplateData('listDetailConfig.maxPages', parseInt(e.target.value) || 10)}
                  min="1"
                  max="1000"
                />
              </div>

              <div className="space-y-2">
                <Label>Följ länkar</Label>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="followLinks"
                    checked={templateData.listDetailConfig.followLinks}
                    onCheckedChange={(checked) => updateTemplateData('listDetailConfig.followLinks', checked)}
                  />
                  <Label htmlFor="followLinks">Följ externa länkar automatiskt</Label>
                </div>
              </div>
            </div>
          </div>
        );

      case 4: // Fält & Selektorer
        return (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Fält & Selektorer</h3>
              <Button onClick={addField}>
                <Plus className="w-4 h-4 mr-2" />
                Lägg till fält
              </Button>
            </div>

            <div className="space-y-4">
              {templateData.fields.map((field, index) => (
                <Card key={field.id} className="border-sidebar-border">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">Fält {index + 1}</CardTitle>
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => removeField(field.id)}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Fältnamn</Label>
                        <Input
                          value={field.name}
                          onChange={(e) => updateField(field.id, { name: e.target.value })}
                          placeholder="t.ex. reg_number, make, model"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>CSS-selektor</Label>
                        <Input
                          value={field.selector}
                          onChange={(e) => updateField(field.id, { selector: e.target.value })}
                          placeholder="t.ex. .reg-number, h1.title"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="space-y-2">
                        <Label>Datatyp</Label>
                        <Select value={field.type} onValueChange={(value) => updateField(field.id, { type: value as any })}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="text">Text</SelectItem>
                            <SelectItem value="number">Nummer</SelectItem>
                            <SelectItem value="url">URL</SelectItem>
                            <SelectItem value="email">E-post</SelectItem>
                            <SelectItem value="date">Datum</SelectItem>
                            <SelectItem value="boolean">Boolean</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Obligatoriskt</Label>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            checked={field.required}
                            onCheckedChange={(checked) => updateField(field.id, { required: checked as boolean })}
                          />
                          <Label>Krävs</Label>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label>Multipel</Label>
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            checked={field.multiple}
                            onCheckedChange={(checked) => updateField(field.id, { multiple: checked as boolean })}
                          />
                          <Label>Flera värden</Label>
                        </div>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label>Beskrivning</Label>
                      <Textarea
                        value={field.description || ''}
                        onChange={(e) => updateField(field.id, { description: e.target.value })}
                        placeholder="Beskriv vad detta fält innehåller..."
                        rows={2}
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}

              {templateData.fields.length === 0 && (
                <Card className="border-dashed border-2 border-muted">
                  <CardContent className="flex flex-col items-center justify-center py-8">
                    <Code className="w-8 h-8 text-muted-foreground mb-2" />
                    <p className="text-muted-foreground text-center">
                      Inga fält definierade än.<br />
                      Klicka på "Lägg till fält" för att börja.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        );

      case 9: // Förhandsvisa
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold mb-2">Förhandsvisa mall</h3>
              <p className="text-muted-foreground">
                Testa din mall mot en exempel-URL för att se resultatet
              </p>
            </div>

            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="text-base">Test-URL</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <Input
                  placeholder="Ange en URL att testa mallen mot..."
                  defaultValue="https://biluppgifter.se/detalj/abc123"
                />
                <Button className="w-full">
                  <Play className="w-4 h-4 mr-2" />
                  Kör test
                </Button>
              </CardContent>
            </Card>

            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="text-base">Mallöversikt</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Namn:</span>
                    <span className="ml-2 font-medium">{templateData.metadata.name || 'Namnlös mall'}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Version:</span>
                    <span className="ml-2 font-medium">{templateData.metadata.version}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Måltyp:</span>
                    <span className="ml-2 font-medium">{templateData.targetType}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Fält:</span>
                    <span className="ml-2 font-medium">{templateData.fields.length}</span>
                  </div>
                </div>

                {templateData.fields.length > 0 && (
                  <div>
                    <h4 className="font-medium mb-2">Fält:</h4>
                    <div className="space-y-1">
                      {templateData.fields.map((field) => (
                        <div key={field.id} className="flex items-center justify-between text-sm">
                          <span>{field.name}</span>
                          <Badge variant="outline">{field.type}</Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        );

      case 10: // Spara & Publicera
        return (
          <div className="space-y-6">
            <div className="text-center">
              <CheckCircle className="w-16 h-16 text-success mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Mall klar!</h3>
              <p className="text-muted-foreground">
                Din mall är nu redo att sparas och publiceras
              </p>
            </div>

            <Card className="border-sidebar-border">
              <CardContent className="p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <span>Validering</span>
                  <CheckCircle className="w-5 h-5 text-success" />
                </div>
                <div className="flex items-center justify-between">
                  <span>Schema-kontroll</span>
                  <CheckCircle className="w-5 h-5 text-success" />
                </div>
                <div className="flex items-center justify-between">
                  <span>Säkerhetsgranskning</span>
                  <CheckCircle className="w-5 h-5 text-success" />
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Button variant="outline" className="w-full">
                <Copy className="w-4 h-4 mr-2" />
                Spara som utkast
              </Button>
              <Button className="w-full">
                <Save className="w-4 h-4 mr-2" />
                Publicera mall
              </Button>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-8">
            <p className="text-muted-foreground">Steg {currentStep} implementeras snart...</p>
          </div>
        );
    }
  };

  const canGoNext = () => {
    switch (currentStep) {
      case 1:
        return templateData.metadata.name.trim() !== '';
      case 2:
        return templateData.targetType === 'single' || 
               (templateData.targetType === 'list' && templateData.structure.listSelector);
      case 4:
        return templateData.fields.length > 0;
      default:
        return true;
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            {mode === 'create' ? 'Skapa ny mall' : 'Redigera mall'}
          </h1>
          <p className="text-muted-foreground">
            Steg {currentStep} av {steps.length}: {steps[currentStep - 1]?.name}
          </p>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <Progress value={(currentStep / steps.length) * 100} className="h-2" />
          <div className="flex justify-between text-xs text-muted-foreground">
            {steps.map((step) => (
              <span 
                key={step.id} 
                className={currentStep >= step.id ? 'text-primary' : ''}
              >
                {step.name}
              </span>
            ))}
          </div>
        </div>

        {/* Content */}
        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            {renderStepContent()}
          </CardContent>
        </Card>

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Föregående
          </Button>

          <div className="flex items-center space-x-2">
            <Button variant="outline">
              <Save className="w-4 h-4 mr-2" />
              Spara utkast
            </Button>
            
            {currentStep < steps.length ? (
              <Button
                onClick={() => setCurrentStep(Math.min(steps.length, currentStep + 1))}
                disabled={!canGoNext()}
              >
                Nästa
                <ChevronRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button>
                <Save className="w-4 h-4 mr-2" />
                Slutför
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TemplateWizard;
