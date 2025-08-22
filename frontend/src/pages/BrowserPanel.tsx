import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  MousePointer2,
  Monitor,
  Smartphone,
  Tablet,
  RefreshCw,
  ArrowLeft,
  ArrowRight,
  Home,
  Crosshair,
  Eye,
  Code,
  Copy,
  Download,
  Settings,
  Target,
  Layers,
  Search,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  ZoomIn,
  ZoomOut,
  CheckCircle
} from 'lucide-react';

interface DOMElement {
  tag: string;
  id?: string;
  classes: string[];
  text?: string;
  attributes: Record<string, string>;
  children: DOMElement[];
  xpath: string;
  cssSelector: string;
  rect: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

interface SelectorRule {
  type: 'css' | 'xpath';
  selector: string;
  field: string;
  extractionType: 'text' | 'attribute' | 'html';
  attribute?: string;
  required: boolean;
  multiple: boolean;
}

const BrowserPanel = () => {
  const [currentUrl, setCurrentUrl] = useState('https://biluppgifter.se/search?q=volvo');
  const [urlInput, setUrlInput] = useState(currentUrl);
  const [activeTab, setActiveTab] = useState<'browser' | 'selector' | 'rules' | 'preview'>('browser');
  const [viewportSize, setViewportSize] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [isSelecting, setIsSelecting] = useState(false);
  const [selectedElement, setSelectedElement] = useState<DOMElement | null>(null);
  const [hoveredElement, setHoveredElement] = useState<DOMElement | null>(null);
  const [selectorRules, setSelectorRules] = useState<SelectorRule[]>([
    {
      type: 'css',
      selector: '.vehicle-card h3',
      field: 'vehicle_title',
      extractionType: 'text',
      required: true,
      multiple: true
    },
    {
      type: 'css',
      selector: '.vehicle-card .price',
      field: 'price',
      extractionType: 'text',
      required: false,
      multiple: true
    }
  ]);
  const [zoomLevel, setZoomLevel] = useState(100);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Mock DOM structure - in real app this would come from the browser engine
  const mockDOMTree: DOMElement = {
    tag: 'html',
    classes: [],
    attributes: {},
    children: [
      {
        tag: 'body',
        classes: ['page-search'],
        attributes: {},
        children: [
          {
            tag: 'div',
            classes: ['container'],
            attributes: {},
            children: [
              {
                tag: 'div',
                classes: ['vehicle-card'],
                attributes: { 'data-vehicle-id': '12345' },
                children: [
                  {
                    tag: 'h3',
                    classes: ['title'],
                    text: 'Volvo XC90 2022',
                    attributes: {},
                    children: [],
                    xpath: '/html/body/div/div[1]/h3',
                    cssSelector: '.vehicle-card h3',
                    rect: { x: 20, y: 50, width: 200, height: 24 }
                  },
                  {
                    tag: 'span',
                    classes: ['price'],
                    text: '450 000 kr',
                    attributes: {},
                    children: [],
                    xpath: '/html/body/div/div[1]/span',
                    cssSelector: '.vehicle-card .price',
                    rect: { x: 20, y: 80, width: 100, height: 18 }
                  }
                ],
                xpath: '/html/body/div/div[1]',
                cssSelector: '.vehicle-card',
                rect: { x: 10, y: 40, width: 220, height: 120 }
              }
            ],
            xpath: '/html/body/div',
            cssSelector: '.container',
            rect: { x: 0, y: 30, width: 800, height: 600 }
          }
        ],
        xpath: '/html/body',
        cssSelector: 'body',
        rect: { x: 0, y: 0, width: 800, height: 800 }
      }
    ],
    xpath: '/html',
    cssSelector: 'html',
    rect: { x: 0, y: 0, width: 800, height: 800 }
  };

  const getViewportDimensions = () => {
    switch (viewportSize) {
      case 'mobile':
        return { width: 375, height: 667 };
      case 'tablet':
        return { width: 768, height: 1024 };
      case 'desktop':
        return { width: 1200, height: 800 };
      default:
        return { width: 1200, height: 800 };
    }
  };

  const handleNavigate = () => {
    setCurrentUrl(urlInput);
  };

  const handleElementClick = (element: DOMElement) => {
    if (isSelecting) {
      setSelectedElement(element);
      setIsSelecting(false);
    }
  };

  const generateSelector = (element: DOMElement) => {
    // Generate CSS selector
    let cssSelector = element.tag;
    if (element.id) {
      cssSelector = `#${element.id}`;
    } else if (element.classes.length > 0) {
      cssSelector = `${element.tag}.${element.classes.join('.')}`;
    }
    return cssSelector;
  };

  const addSelectorRule = () => {
    if (selectedElement) {
      const newRule: SelectorRule = {
        type: 'css',
        selector: generateSelector(selectedElement),
        field: `field_${selectorRules.length + 1}`,
        extractionType: 'text',
        required: false,
        multiple: false
      };
      setSelectorRules([...selectorRules, newRule]);
    }
  };

  const updateSelectorRule = (index: number, updates: Partial<SelectorRule>) => {
    const updated = [...selectorRules];
    updated[index] = { ...updated[index], ...updates };
    setSelectorRules(updated);
  };

  const deleteSelectorRule = (index: number) => {
    setSelectorRules(selectorRules.filter((_, i) => i !== index));
  };

  const renderDOMTreeNode = (node: DOMElement, depth: number = 0) => {
    const [isExpanded, setIsExpanded] = useState(depth < 2);
    const hasChildren = node.children.length > 0;
    
    return (
      <div key={node.xpath} className="text-sm">
        <div 
          className={`flex items-center space-x-1 py-1 px-2 rounded cursor-pointer hover:bg-muted/50 ${
            selectedElement?.xpath === node.xpath ? 'bg-primary/20' : ''
          } ${hoveredElement?.xpath === node.xpath ? 'bg-muted/30' : ''}`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          onClick={() => handleElementClick(node)}
          onMouseEnter={() => setHoveredElement(node)}
          onMouseLeave={() => setHoveredElement(null)}
        >
          {hasChildren && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setIsExpanded(!isExpanded);
              }}
              className="w-4 h-4 flex items-center justify-center"
            >
              {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
            </button>
          )}
          {!hasChildren && <div className="w-4" />}
          
          <span className="text-blue-600">&lt;</span>
          <span className="text-blue-600 font-medium">{node.tag}</span>
          
          {node.id && (
            <>
              <span className="text-green-600">id</span>
              <span className="text-orange-600">=</span>
              <span className="text-red-600">"{node.id}"</span>
            </>
          )}
          
          {node.classes.length > 0 && (
            <>
              <span className="text-green-600">class</span>
              <span className="text-orange-600">=</span>
              <span className="text-red-600">"{node.classes.join(' ')}"</span>
            </>
          )}
          
          <span className="text-blue-600">&gt;</span>
          
          {node.text && (
            <span className="text-gray-800 max-w-32 truncate">{node.text}</span>
          )}
        </div>
        
        {hasChildren && isExpanded && (
          <div>
            {node.children.map(child => renderDOMTreeNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  const renderBrowserTab = () => (
    <div className="space-y-4">
      {/* Browser Controls */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" disabled>
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm" disabled>
              <ArrowRight className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm">
              <Home className="w-4 h-4" />
            </Button>
            
            <div className="flex-1 flex items-center space-x-2">
              <Input
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleNavigate()}
                className="flex-1"
                placeholder="Ange URL..."
              />
              <Button onClick={handleNavigate}>
                <ExternalLink className="w-4 h-4" />
              </Button>
            </div>

            {/* Viewport Controls */}
            <div className="flex items-center space-x-1 border-l pl-2">
              <Button
                variant={viewportSize === 'desktop' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewportSize('desktop')}
              >
                <Monitor className="w-4 h-4" />
              </Button>
              <Button
                variant={viewportSize === 'tablet' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewportSize('tablet')}
              >
                <Tablet className="w-4 h-4" />
              </Button>
              <Button
                variant={viewportSize === 'mobile' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewportSize('mobile')}
              >
                <Smartphone className="w-4 h-4" />
              </Button>
            </div>

            {/* Zoom Controls */}
            <div className="flex items-center space-x-1 border-l pl-2">
              <Button variant="outline" size="sm" onClick={() => setZoomLevel(Math.max(50, zoomLevel - 10))}>
                <ZoomOut className="w-4 h-4" />
              </Button>
              <span className="text-sm text-muted-foreground px-2">{zoomLevel}%</span>
              <Button variant="outline" size="sm" onClick={() => setZoomLevel(Math.min(200, zoomLevel + 10))}>
                <ZoomIn className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Browser Viewport */}
      <Card className="border-sidebar-border">
        <CardContent className="p-0">
          <div className="flex justify-center bg-muted/20 p-4">
            <div 
              className="bg-white border shadow-lg relative overflow-hidden"
              style={{
                width: getViewportDimensions().width,
                height: getViewportDimensions().height,
                transform: `scale(${zoomLevel / 100})`,
                transformOrigin: 'top center'
              }}
            >
              {/* Mock Browser Content */}
              <div className="p-4 space-y-4">
                <div className="flex items-center justify-between border-b pb-2">
                  <h1 className="text-xl font-bold">Biluppgifter.se</h1>
                  <div className="flex items-center space-x-2">
                    <Input placeholder="Sök fordon..." className="w-48" />
                    <Button size="sm"><Search className="w-4 h-4" /></Button>
                  </div>
                </div>
                
                {/* Mock Vehicle Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[1, 2, 3, 4, 5, 6].map((i) => (
                    <div 
                      key={i}
                      className={`vehicle-card border rounded p-4 cursor-pointer hover:shadow-md ${
                        selectedElement?.cssSelector === '.vehicle-card' ? 'ring-2 ring-primary' : ''
                      } ${hoveredElement?.cssSelector === '.vehicle-card' ? 'bg-blue-50' : ''}`}
                      onClick={() => handleElementClick(mockDOMTree.children[0].children[0].children[0])}
                    >
                      <div className="w-full h-32 bg-gray-200 rounded mb-2"></div>
                      <h3 
                        className={`title font-medium mb-1 ${
                          selectedElement?.cssSelector === '.vehicle-card h3' ? 'bg-yellow-200' : ''
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleElementClick(mockDOMTree.children[0].children[0].children[0].children[0]);
                        }}
                      >
                        Volvo XC90 202{i}
                      </h3>
                      <p className="text-sm text-gray-600 mb-2">Automatisk, Diesel, 5 dörrar</p>
                      <span 
                        className={`price text-lg font-bold text-green-600 ${
                          selectedElement?.cssSelector === '.vehicle-card .price' ? 'bg-yellow-200' : ''
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleElementClick(mockDOMTree.children[0].children[0].children[0].children[1]);
                        }}
                      >
                        {450 + i * 25} 000 kr
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Selection Overlay */}
              {isSelecting && (
                <div className="absolute inset-0 bg-blue-500/10 cursor-crosshair flex items-center justify-center">
                  <div className="bg-white border shadow-lg rounded p-4">
                    <div className="flex items-center space-x-2">
                      <Target className="w-5 h-5 text-primary" />
                      <span>Klicka på element för att välja</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSelectorTab = () => (
    <div className="space-y-4">
      {/* Selection Controls */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">Element Selector</CardTitle>
          <CardDescription>Välj element i browsern för att skapa extraktionsregler</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <Button
              variant={isSelecting ? 'default' : 'outline'}
              onClick={() => setIsSelecting(!isSelecting)}
            >
              <Crosshair className="w-4 h-4 mr-2" />
              {isSelecting ? 'Avbryt val' : 'Välj element'}
            </Button>
            {selectedElement && (
              <Button onClick={addSelectorRule} variant="outline">
                <Target className="w-4 h-4 mr-2" />
                Lägg till regel
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Selected Element Info */}
      {selectedElement && (
        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="text-base">Valt element</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div>
                <span className="text-sm text-muted-foreground">Tag:</span>
                <Badge variant="outline" className="ml-2">{selectedElement.tag}</Badge>
              </div>
              
              {selectedElement.classes.length > 0 && (
                <div>
                  <span className="text-sm text-muted-foreground">Klasser:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {selectedElement.classes.map((cls, i) => (
                      <Badge key={i} variant="secondary" className="text-xs">{cls}</Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedElement.text && (
                <div>
                  <span className="text-sm text-muted-foreground">Text:</span>
                  <span className="ml-2 font-mono text-sm">{selectedElement.text}</span>
                </div>
              )}
              
              <div>
                <span className="text-sm text-muted-foreground">CSS Selector:</span>
                <div className="flex items-center space-x-2 mt-1">
                  <code className="bg-muted p-1 rounded text-sm flex-1">{selectedElement.cssSelector}</code>
                  <Button variant="outline" size="sm">
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              
              <div>
                <span className="text-sm text-muted-foreground">XPath:</span>
                <div className="flex items-center space-x-2 mt-1">
                  <code className="bg-muted p-1 rounded text-sm flex-1">{selectedElement.xpath}</code>
                  <Button variant="outline" size="sm">
                    <Copy className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* DOM Tree */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="text-base">DOM-träd</CardTitle>
          <CardDescription>Navigera genom sidans struktur</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="bg-muted/20 rounded p-3 max-h-96 overflow-y-auto font-mono text-sm">
            {renderDOMTreeNode(mockDOMTree)}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderRulesTab = () => (
    <div className="space-y-4">
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Extraktionsregler</CardTitle>
              <CardDescription>Definiera hur data ska extraheras från sidan</CardDescription>
            </div>
            <Button onClick={() => setSelectorRules([...selectorRules, {
              type: 'css',
              selector: '',
              field: `field_${selectorRules.length + 1}`,
              extractionType: 'text',
              required: false,
              multiple: false
            }])}>
              Lägg till regel
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {selectorRules.map((rule, index) => (
              <Card key={index} className="border-muted">
                <CardContent className="p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="text-sm text-muted-foreground">Fältnamn</label>
                      <Input
                        value={rule.field}
                        onChange={(e) => updateSelectorRule(index, { field: e.target.value })}
                        placeholder="Fältnamn"
                      />
                    </div>
                    
                    <div>
                      <label className="text-sm text-muted-foreground">Selector typ</label>
                      <select
                        value={rule.type}
                        onChange={(e) => updateSelectorRule(index, { type: e.target.value as 'css' | 'xpath' })}
                        className="w-full p-2 border rounded"
                      >
                        <option value="css">CSS Selector</option>
                        <option value="xpath">XPath</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="text-sm text-muted-foreground">Extraktionstyp</label>
                      <select
                        value={rule.extractionType}
                        onChange={(e) => updateSelectorRule(index, { extractionType: e.target.value as any })}
                        className="w-full p-2 border rounded"
                      >
                        <option value="text">Text</option>
                        <option value="attribute">Attribut</option>
                        <option value="html">HTML</option>
                      </select>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <label className="text-sm text-muted-foreground">Selector</label>
                    <div className="flex items-center space-x-2">
                      <Input
                        value={rule.selector}
                        onChange={(e) => updateSelectorRule(index, { selector: e.target.value })}
                        placeholder="CSS selector eller XPath"
                        className="flex-1 font-mono"
                      />
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => deleteSelectorRule(index)}>
                        ×
                      </Button>
                    </div>
                  </div>
                  
                  {rule.extractionType === 'attribute' && (
                    <div className="mt-2">
                      <label className="text-sm text-muted-foreground">Attribut</label>
                      <Input
                        value={rule.attribute || ''}
                        onChange={(e) => updateSelectorRule(index, { attribute: e.target.value })}
                        placeholder="href, src, data-id, etc."
                      />
                    </div>
                  )}
                  
                  <div className="flex items-center space-x-4 mt-4">
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={rule.required}
                        onChange={(e) => updateSelectorRule(index, { required: e.target.checked })}
                      />
                      <span className="text-sm">Obligatorisk</span>
                    </label>
                    <label className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={rule.multiple}
                        onChange={(e) => updateSelectorRule(index, { multiple: e.target.checked })}
                      />
                      <span className="text-sm">Flera värden</span>
                    </label>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderPreviewTab = () => (
    <div className="space-y-4">
      <Card className="border-sidebar-border">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">Extraktionsförhandsvisning</CardTitle>
              <CardDescription>Testkör extraktionsreglerna på aktuell sida</CardDescription>
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" size="sm">
                <RefreshCw className="w-4 h-4 mr-2" />
                Uppdatera
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Exportera
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Extraction Results */}
            <div className="border rounded">
              <div className="bg-muted/20 p-3 border-b">
                <h4 className="font-medium">Extraherad data (3 items)</h4>
              </div>
              <div className="p-3">
                <div className="space-y-3">
                  {[
                    { vehicle_title: 'Volvo XC90 2021', price: '450 000 kr' },
                    { vehicle_title: 'Volvo XC90 2022', price: '475 000 kr' },
                    { vehicle_title: 'Volvo XC90 2023', price: '500 000 kr' }
                  ].map((item, index) => (
                    <Card key={index} className="border-muted">
                      <CardContent className="p-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                          {Object.entries(item).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-muted-foreground">{key}:</span>
                              <span className="ml-2 font-medium">{value}</span>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>

            {/* Rule Results */}
            <div className="space-y-2">
              <h4 className="font-medium">Regelresultat</h4>
              {selectorRules.map((rule, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded">
                  <div className="flex items-center space-x-3">
                    <Badge variant="outline">{rule.field}</Badge>
                    <code className="text-sm bg-muted px-2 py-1 rounded">{rule.selector}</code>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant="secondary" className="text-xs">3 matches</Badge>
                    <CheckCircle className="w-4 h-4 text-success" />
                  </div>
                </div>
              ))}
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
          <h1 className="text-3xl font-bold text-foreground">Browser Panel</h1>
          <p className="text-muted-foreground">Interaktiv browser för att skapa och testa selectors</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="browser">Browser</TabsTrigger>
          <TabsTrigger value="selector">Selector</TabsTrigger>
          <TabsTrigger value="rules">Regler</TabsTrigger>
          <TabsTrigger value="preview">Förhandsvisning</TabsTrigger>
        </TabsList>

        <TabsContent value="browser" className="mt-6">
          {renderBrowserTab()}
        </TabsContent>

        <TabsContent value="selector" className="mt-6">
          {renderSelectorTab()}
        </TabsContent>

        <TabsContent value="rules" className="mt-6">
          {renderRulesTab()}
        </TabsContent>

        <TabsContent value="preview" className="mt-6">
          {renderPreviewTab()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BrowserPanel;
