import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { 
  Code,
  Play,
  Save,
  Copy,
  Eye,
  Search,
  Target,
  Layers,
  CheckCircle,
  AlertCircle,
  Lightbulb,
  BookOpen,
  Zap,
  TreePine,
  MousePointer,
  TestTube,
  RefreshCw,
  Download,
  Upload
} from "lucide-react";
import { useState } from "react";

// Mock XPath analysis data
const mockAnalysisResults = [
  {
    xpath: "//div[@class='product-title']/h1/text()",
    matches: 1,
    confidence: 95,
    specificity: "high",
    robustness: "medium",
    suggestions: ["Consider using more specific attributes", "Add fallback selectors"],
    elements: [
      { text: "Wireless Bluetooth Headphones", tag: "h1", attributes: { class: "title main-title" } }
    ]
  },
  {
    xpath: "//span[contains(@class, 'price')]",
    matches: 3,
    confidence: 78,
    specificity: "medium", 
    robustness: "high",
    suggestions: ["Be more specific to avoid multiple matches", "Consider using CSS selector instead"],
    elements: [
      { text: "$89.99", tag: "span", attributes: { class: "price current-price" } },
      { text: "$129.99", tag: "span", attributes: { class: "price original-price" } },
      { text: "$89.99", tag: "span", attributes: { class: "price-display" } }
    ]
  }
];

const xpathTips = [
  {
    category: "Best Practices",
    tips: [
      "Use specific attributes when available (id, data-testid)",
      "Avoid using position-based selectors (e.g., [1], [2])",
      "Prefer contains() over exact matches for class names",
      "Use descendant axis (//) sparingly to improve performance"
    ]
  },
  {
    category: "Common Patterns",
    tips: [
      "Text content: //element/text()",
      "Attribute values: //element/@attribute",
      "Contains text: //element[contains(text(), 'value')]",
      "Multiple conditions: //element[@attr1 and @attr2]"
    ]
  },
  {
    category: "Troubleshooting",
    tips: [
      "Check for dynamic content loaded by JavaScript",
      "Verify element exists in actual DOM structure",
      "Consider namespaces for XML documents",
      "Test with different browser rendering engines"
    ]
  }
];

export default function XPathAnalysisPage() {
  const [activeTab, setActiveTab] = useState("analyzer");
  const [xpathInput, setXpathInput] = useState("//div[@class='product-title']/h1/text()");
  const [targetUrl, setTargetUrl] = useState("https://example.com/product/123");
  const [analysisResults, setAnalysisResults] = useState(mockAnalysisResults);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const analyzeXPath = async () => {
    setIsAnalyzing(true);
    // Mock analysis - in real app would call backend
    setTimeout(() => {
      setAnalysisResults(mockAnalysisResults);
      setIsAnalyzing(false);
    }, 1500);
  };

  const optimizeXPath = () => {
    // Mock optimization
    setXpathInput("//h1[@class='product-title']/text()");
  };

  const generateXPath = () => {
    // Mock generation
    setXpathInput("//div[contains(@class, 'product')]//h1[1]/text()");
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">XPath Analysis</h1>
          <p className="text-gray-600 dark:text-gray-400">Advanced XPath testing and optimization tools</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <BookOpen className="h-4 w-4 mr-2" />
            Documentation
          </Button>
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button size="sm">
            <Save className="h-4 w-4 mr-2" />
            Save Analysis
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="analyzer">Analyzer</TabsTrigger>
          <TabsTrigger value="builder">Builder</TabsTrigger>
          <TabsTrigger value="validator">Validator</TabsTrigger>
          <TabsTrigger value="optimizer">Optimizer</TabsTrigger>
          <TabsTrigger value="reference">Reference</TabsTrigger>
        </TabsList>

        {/* Analyzer Tab */}
        <TabsContent value="analyzer" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Input Panel */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    XPath Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Target URL */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Target URL</label>
                    <Input
                      placeholder="https://example.com/page"
                      value={targetUrl}
                      onChange={(e) => setTargetUrl(e.target.value)}
                    />
                  </div>

                  {/* XPath Input */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">XPath Expression</label>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm" onClick={generateXPath}>
                          <Zap className="h-3 w-3 mr-1" />
                          Generate
                        </Button>
                        <Button variant="ghost" size="sm" onClick={optimizeXPath}>
                          <Lightbulb className="h-3 w-3 mr-1" />
                          Optimize
                        </Button>
                      </div>
                    </div>
                    <Textarea
                      placeholder="Enter XPath expression..."
                      value={xpathInput}
                      onChange={(e) => setXpathInput(e.target.value)}
                      className="font-mono text-sm"
                      rows={3}
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button onClick={analyzeXPath} disabled={isAnalyzing} className="flex-1">
                      {isAnalyzing ? (
                        <>
                          <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <TestTube className="h-4 w-4 mr-2" />
                          Analyze
                        </>
                      )}
                    </Button>
                    <Button variant="outline">
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Tools */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Analysis Tools</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" size="sm" className="justify-start">
                      <MousePointer className="h-4 w-4 mr-2" />
                      Element Picker
                    </Button>
                    <Button variant="outline" size="sm" className="justify-start">
                      <TreePine className="h-4 w-4 mr-2" />
                      DOM Tree
                    </Button>
                    <Button variant="outline" size="sm" className="justify-start">
                      <Code className="h-4 w-4 mr-2" />
                      CSS to XPath
                    </Button>
                    <Button variant="outline" size="sm" className="justify-start">
                      <Search className="h-4 w-4 mr-2" />
                      XPath to CSS
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Results Panel */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5" />
                    Analysis Results
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {analysisResults.length > 0 ? (
                    <div className="space-y-4">
                      {analysisResults.map((result, index) => (
                        <div key={index} className="p-4 border rounded-lg space-y-3">
                          <div className="flex items-center justify-between">
                            <code className="text-sm font-mono bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                              {result.xpath}
                            </code>
                            <Badge variant={result.matches === 1 ? "default" : "secondary"}>
                              {result.matches} match{result.matches !== 1 ? 'es' : ''}
                            </Badge>
                          </div>

                          {/* Metrics */}
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div className="text-center">
                              <div className="font-semibold text-blue-600 dark:text-blue-400">
                                {result.confidence}%
                              </div>
                              <div className="text-xs text-gray-500">Confidence</div>
                            </div>
                            <div className="text-center">
                              <div className="font-semibold capitalize">{result.specificity}</div>
                              <div className="text-xs text-gray-500">Specificity</div>
                            </div>
                            <div className="text-center">
                              <div className="font-semibold capitalize">{result.robustness}</div>
                              <div className="text-xs text-gray-500">Robustness</div>
                            </div>
                          </div>

                          {/* Matched Elements */}
                          <div className="space-y-2">
                            <h5 className="text-sm font-medium">Matched Elements:</h5>
                            {result.elements.map((element, elemIndex) => (
                              <div key={elemIndex} className="p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm">
                                <div className="font-mono text-xs text-gray-600 dark:text-gray-400">
                                  &lt;{element.tag} class="{element.attributes.class}"&gt;
                                </div>
                                <div className="font-medium mt-1">{element.text}</div>
                              </div>
                            ))}
                          </div>

                          {/* Suggestions */}
                          {result.suggestions.length > 0 && (
                            <div className="space-y-1">
                              <h5 className="text-sm font-medium flex items-center gap-1">
                                <Lightbulb className="h-4 w-4 text-yellow-500" />
                                Suggestions:
                              </h5>
                              <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                                {result.suggestions.map((suggestion, suggIndex) => (
                                  <li key={suggIndex} className="flex items-start gap-2">
                                    <span className="text-xs">•</span>
                                    <span>{suggestion}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                      <TestTube className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>Enter an XPath expression and click "Analyze" to see results</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Builder Tab */}
        <TabsContent value="builder" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Interactive XPath Builder</CardTitle>
              <CardDescription>Build XPath expressions step by step</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Element Selection</h4>
                  <div className="space-y-3">
                    <div className="p-3 border rounded-lg">
                      <label className="text-sm font-medium">Tag Name</label>
                      <Input placeholder="div, span, h1..." className="mt-1" />
                    </div>
                    <div className="p-3 border rounded-lg">
                      <label className="text-sm font-medium">Attributes</label>
                      <div className="mt-1 space-y-2">
                        <Input placeholder="class=product-title" />
                        <Input placeholder="id=main-content" />
                      </div>
                    </div>
                    <div className="p-3 border rounded-lg">
                      <label className="text-sm font-medium">Text Content</label>
                      <Input placeholder="Contains text..." className="mt-1" />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-medium">Generated XPath</h4>
                  <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg">
                    <code className="text-sm font-mono">
                      //div[@class='product-title' and contains(text(), 'Product')]
                    </code>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    <p>This XPath will select div elements with class 'product-title' that contain the text 'Product'</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Validator Tab */}
        <TabsContent value="validator" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>XPath Validator</CardTitle>
              <CardDescription>Test XPath expressions against multiple URLs</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Test URLs (one per line)</label>
                    <Textarea
                      placeholder="https://example.com/product/1&#10;https://example.com/product/2&#10;https://example.com/product/3"
                      rows={6}
                      className="font-mono text-sm"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">XPath Expression</label>
                    <Textarea
                      placeholder="//h1[@class='product-title']/text()"
                      rows={6}
                      className="font-mono text-sm"
                    />
                  </div>
                </div>
                <Button className="w-full">
                  <TestTube className="h-4 w-4 mr-2" />
                  Validate Against All URLs
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Optimizer Tab */}
        <TabsContent value="optimizer" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>XPath Optimizer</CardTitle>
              <CardDescription>Optimize XPath expressions for better performance and reliability</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Original XPath</label>
                    <Textarea
                      placeholder="Enter your XPath expression..."
                      rows={4}
                      className="font-mono text-sm"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Optimized XPath</label>
                    <Textarea
                      value="//h1[@class='product-title'][1]/text()"
                      rows={4}
                      className="font-mono text-sm bg-green-50 dark:bg-green-900/20"
                      readOnly
                    />
                  </div>
                </div>

                <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <h4 className="font-medium text-blue-800 dark:text-blue-200 mb-2">
                    Optimization Suggestions:
                  </h4>
                  <ul className="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• Added position filter [1] to ensure single match</li>
                    <li>• Simplified descendant axis for better performance</li>
                    <li>• Used more specific attribute selector</li>
                  </ul>
                </div>

                <Button>
                  <Zap className="h-4 w-4 mr-2" />
                  Optimize XPath
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reference Tab */}
        <TabsContent value="reference" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {xpathTips.map((category) => (
              <Card key={category.category}>
                <CardHeader>
                  <CardTitle className="text-lg">{category.category}</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    {category.tips.map((tip, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-blue-500 mt-1">•</span>
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>XPath Syntax Reference</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div className="space-y-2">
                  <h5 className="font-medium">Basic Syntax</h5>
                  <div className="space-y-1 font-mono text-xs">
                    <div><span className="text-blue-600">//</span> - Select from anywhere</div>
                    <div><span className="text-blue-600">/</span> - Select from root</div>
                    <div><span className="text-blue-600">.</span> - Current node</div>
                    <div><span className="text-blue-600">..</span> - Parent node</div>
                    <div><span className="text-blue-600">@</span> - Select attribute</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <h5 className="font-medium">Functions</h5>
                  <div className="space-y-1 font-mono text-xs">
                    <div><span className="text-green-600">contains()</span> - Text contains</div>
                    <div><span className="text-green-600">text()</span> - Get text content</div>
                    <div><span className="text-green-600">position()</span> - Element position</div>
                    <div><span className="text-green-600">last()</span> - Last element</div>
                    <div><span className="text-green-600">count()</span> - Count elements</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
