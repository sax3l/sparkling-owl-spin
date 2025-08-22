import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  FileText, 
  Code, 
  Play, 
  Save, 
  Copy, 
  Edit,
  Trash2,
  Plus,
  Eye
} from 'lucide-react';

const TemplateBuilder = () => {
  const [activeTab, setActiveTab] = useState('builder');

const yamlTemplate = `# ECaDP Template - biluppgifter.se
name: "Vehicle Registry Scraper"
version: "1.2.0"
target_domain: "biluppgifter.se"

# Ethical constraints
ethics:
  respect_robots_txt: true
  rate_limit: 2000  # ms between requests
  max_concurrent: 3

# Entry points and navigation
navigation:
  start_urls:
    - "https://biluppgifter.se/search"
  pagination:
    selector: ".pagination .next"
    max_pages: 500

# Data extraction rules
extraction:
  vehicle:
    selectors:
      reg_number: ".reg-number"
      make: ".vehicle-make"
      model: ".vehicle-model"
      year: ".vehicle-year"
      mileage: ".mileage"
      price: ".price"
    
    transformations:
      price: 
        - regex: "[^0-9]"
        - cast: "integer"
      
      year:
        - cast: "integer"
        - validate: "range(1900, 2025)"

# Output configuration  
output:
  format: "json"
  batch_size: 100
  destination: "supabase.vehicles"`;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Template Builder</h1>
          <p className="text-muted-foreground">Create and manage extraction templates</p>
        </div>
        <Button className="bg-gradient-primary">
          <Plus className="w-4 h-4 mr-2" />
          New Template
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="builder">Template Builder</TabsTrigger>
          <TabsTrigger value="library">Template Library</TabsTrigger>
          <TabsTrigger value="test">Test & Preview</TabsTrigger>
        </TabsList>

        <TabsContent value="builder" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Template Editor */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Code className="w-5 h-5 text-primary" />
                  <span>YAML Editor</span>
                </CardTitle>
                <CardDescription>Define your extraction template using our DSL</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="templateName">Template Name</Label>
                      <Input id="templateName" placeholder="Vehicle Registry Scraper" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="domain">Target Domain</Label>
                      <Input id="domain" placeholder="biluppgifter.se" />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="yaml">Template YAML</Label>
                    <Textarea 
                      id="yaml"
                      value={yamlTemplate}
                      className="font-mono text-sm min-h-[400px]"
                      readOnly
                    />
                  </div>

                  <div className="flex space-x-2">
                    <Button className="bg-gradient-primary flex-1">
                      <Save className="w-4 h-4 mr-2" />
                      Save Template
                    </Button>
                    <Button variant="outline">
                      <Play className="w-4 h-4 mr-2" />
                      Test
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Template Documentation */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <FileText className="w-5 h-5 text-accent" />
                  <span>Template Guide</span>
                </CardTitle>
                <CardDescription>DSL syntax and best practices</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <h4 className="text-sm font-semibold text-foreground mb-2">Basic Structure</h4>
                    <code className="text-xs text-muted-foreground">
                      name: "Template Name"<br/>
                      target_domain: "example.com"<br/>
                      ethics: &lbrace;...&rbrace;<br/>
                      navigation: &lbrace;...&rbrace;<br/>
                      extraction: &lbrace;...&rbrace;
                    </code>
                  </div>

                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <h4 className="text-sm font-semibold text-foreground mb-2">Selectors</h4>
                    <code className="text-xs text-muted-foreground">
                      selectors:<br/>
                      {"  "}title: ".post-title"<br/>
                      {"  "}price: "[data-price]"<br/>
                      {"  "}link: "a.item-link @href"
                    </code>
                  </div>

                  <div className="p-3 bg-sidebar-accent rounded-lg">
                    <h4 className="text-sm font-semibold text-foreground mb-2">Transformations</h4>
                    <code className="text-xs text-muted-foreground">
                      transformations:<br/>
                      {"  "}price:<br/>
                      {"    "}- regex: "[^0-9]"<br/>
                      {"    "}- cast: "integer"
                    </code>
                  </div>

                  <div className="p-3 bg-primary/5 border border-primary/20 rounded-lg">
                    <h4 className="text-sm font-semibold text-primary mb-2">Pro Tips</h4>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      <li>• Use CSS selectors for precise targeting</li>
                      <li>• Always set rate_limit ≥ 1000ms</li>
                      <li>• Test selectors in browser DevTools first</li>
                      <li>• Validate data with transformations</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="library" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                name: 'biluppgifter.se - Vehicles',
                description: 'Extract vehicle registration data',
                domain: 'biluppgifter.se',
                version: '1.2.0',
                status: 'active',
                lastUsed: '2 hours ago'
              },
              {
                name: 'hitta.se - Business',
                description: 'Business directory listings',
                domain: 'hitta.se', 
                version: '1.0.3',
                status: 'active',
                lastUsed: '1 day ago'
              },
              {
                name: 'car.info - Listings',
                description: 'Car marketplace listings',
                domain: 'car.info',
                version: '0.9.1',
                status: 'beta',
                lastUsed: '3 days ago'
              },
              {
                name: 'blocket.se - Marketplace',
                description: 'General marketplace items',
                domain: 'blocket.se',
                version: '1.1.0',
                status: 'maintenance',
                lastUsed: '1 week ago'
              }
            ].map((template, index) => (
              <Card key={index} className="border-sidebar-border">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="text-base">{template.name}</CardTitle>
                      <CardDescription className="text-sm">{template.description}</CardDescription>
                    </div>
                    <Badge 
                      variant="secondary"
                      className={
                        template.status === 'active'
                          ? 'bg-success/10 text-success border-success/20'
                          : template.status === 'beta'
                          ? 'bg-primary/10 text-primary border-primary/20'
                          : 'bg-warning/10 text-warning border-warning/20'
                      }
                    >
                      {template.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Version</span>
                        <span className="text-foreground font-mono">{template.version}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Domain</span>
                        <span className="text-foreground font-mono text-xs">{template.domain}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Last Used</span>
                        <span className="text-foreground">{template.lastUsed}</span>
                      </div>
                    </div>

                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline" className="flex-1">
                        <Edit className="w-3 h-3 mr-1" />
                        Edit
                      </Button>
                      <Button size="sm" variant="outline">
                        <Copy className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Eye className="w-3 h-3" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="test" className="space-y-6">
          <div className="text-center py-12">
            <Play className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Template Testing</h3>
            <p className="text-muted-foreground">Test your templates against live websites safely</p>
            <Button className="mt-4 bg-gradient-primary">
              <Play className="w-4 h-4 mr-2" />
              Run Test
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TemplateBuilder;