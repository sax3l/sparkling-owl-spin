"use client";

import Layout from "@/components/Layout";
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
  RefreshCw,
  Eye,
  EyeOff,
  Target,
  Layers,
  MousePointer,
  CheckCircle,
  AlertCircle,
  Download,
  Upload,
  Wand2,
  BookOpen,
  Zap,
  TestTube
} from "lucide-react";
import { useState } from "react";

// Mock selector data
const mockSelectors = [
  {
    id: "sel_001",
    name: "Product Title",
    type: "xpath",
    selector: "//h1[@class='product-title']/text()",
    cssEquivalent: "h1.product-title",
    isValid: true,
    matchCount: 1,
    confidence: 95
  },
  {
    id: "sel_002", 
    name: "Price",
    type: "css",
    selector: ".price-current .value",
    xpathEquivalent: "//span[contains(@class, 'price-current')]//span[@class='value']",
    isValid: true,
    matchCount: 1,
    confidence: 98
  },
  {
    id: "sel_003",
    name: "Product Images",
    type: "xpath",
    selector: "//div[@class='gallery']//img/@src",
    cssEquivalent: ".gallery img",
    isValid: true,
    matchCount: 8,
    confidence: 89
  }
];

const selectorExamples = [
  {
    category: "E-commerce",
    examples: [
      { name: "Product Title", css: "h1.product-title", xpath: "//h1[@class='product-title']" },
      { name: "Price", css: ".price, .cost", xpath: "//span[contains(@class, 'price')]" },
      { name: "Stock Status", css: ".in-stock, .availability", xpath: "//div[contains(@class, 'stock')]" }
    ]
  },
  {
    category: "Content",
    examples: [
      { name: "Article Title", css: "h1, .title", xpath: "//h1 | //div[@class='title']" },
      { name: "Article Content", css: ".content, .article-body", xpath: "//div[contains(@class, 'content')]" },
      { name: "Author", css: ".author, .by-line", xpath: "//span[@class='author']" }
    ]
  }
];

export default function SelectorStudioPage() {
  const [activeTab, setActiveTab] = useState("builder");
  const [selectorType, setSelectorType] = useState("css");
  const [currentSelector, setCurrentSelector] = useState("");
  const [testUrl, setTestUrl] = useState("https://example.com/product/test-item");
  const [isPreviewMode, setIsPreviewMode] = useState(false);
  const [selectedSelectors, setSelectedSelectors] = useState(mockSelectors);

  const generateSelector = () => {
    // Mock auto-generation
    if (selectorType === "css") {
      setCurrentSelector(".auto-generated-selector");
    } else {
      setCurrentSelector("//div[@class='auto-generated-selector']");
    }
  };

  const testSelector = () => {
    // Mock testing - would actually test against live URL
    console.log(`Testing ${selectorType} selector: ${currentSelector} on ${testUrl}`);
  };

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Selector Studio</h1>
          <p className="text-gray-600 dark:text-gray-400">Build and test CSS selectors and XPath expressions</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <BookOpen className="h-4 w-4 mr-2" />
            Guide
          </Button>
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button size="sm">
            <Save className="h-4 w-4 mr-2" />
            Save Set
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="builder">Builder</TabsTrigger>
          <TabsTrigger value="tester">Tester</TabsTrigger>
          <TabsTrigger value="library">Library</TabsTrigger>
          <TabsTrigger value="examples">Examples</TabsTrigger>
        </TabsList>

        {/* Builder Tab */}
        <TabsContent value="builder" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Panel - Builder */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Selector Builder
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Selector Type Toggle */}
                  <Tabs value={selectorType} onValueChange={setSelectorType}>
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="css">CSS Selector</TabsTrigger>
                      <TabsTrigger value="xpath">XPath</TabsTrigger>
                    </TabsList>
                  </Tabs>

                  {/* Target URL */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Target URL</label>
                    <div className="flex gap-2">
                      <Input
                        placeholder="https://example.com/page"
                        value={testUrl}
                        onChange={(e) => setTestUrl(e.target.value)}
                        className="flex-1"
                      />
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  {/* Selector Input */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <label className="text-sm font-medium">
                        {selectorType === "css" ? "CSS Selector" : "XPath Expression"}
                      </label>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={generateSelector}
                        className="text-xs"
                      >
                        <Wand2 className="h-3 w-3 mr-1" />
                        Auto-generate
                      </Button>
                    </div>
                    <Textarea
                      placeholder={
                        selectorType === "css" 
                          ? "Enter CSS selector (e.g., .class-name, #id, tag[attribute])"
                          : "Enter XPath expression (e.g., //div[@class='example'], //h1/text())"
                      }
                      value={currentSelector}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setCurrentSelector(e.target.value)}
                      className="font-mono text-sm"
                      rows={3}
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button onClick={testSelector} className="flex-1">
                      <TestTube className="h-4 w-4 mr-2" />
                      Test Selector
                    </Button>
                    <Button variant="outline">
                      <Copy className="h-4 w-4" />
                    </Button>
                    <Button variant="outline">
                      <Save className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Validation Results */}
                  {currentSelector && (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                      <div className="flex items-center gap-2 text-green-700 dark:text-green-400">
                        <CheckCircle className="h-4 w-4" />
                        <span className="font-medium">Valid selector</span>
                      </div>
                      <div className="text-sm text-green-600 dark:text-green-500 mt-1">
                        Found 3 matches with 95% confidence
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Quick Tools */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Quick Tools</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <Button variant="outline" size="sm" className="justify-start">
                      <MousePointer className="h-4 w-4 mr-2" />
                      Element Picker
                    </Button>
                    <Button variant="outline" size="sm" className="justify-start">
                      <Layers className="h-4 w-4 mr-2" />
                      DOM Inspector
                    </Button>
                    <Button variant="outline" size="sm" className="justify-start">
                      <Code className="h-4 w-4 mr-2" />
                      Convert to XPath
                    </Button>
                    <Button variant="outline" size="sm" className="justify-start">
                      <Zap className="h-4 w-4 mr-2" />
                      Optimize Selector
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Right Panel - Preview */}
            <div className="space-y-4">
              <Card className="h-[600px]">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <Eye className="h-5 w-5" />
                      Live Preview
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setIsPreviewMode(!isPreviewMode)}
                      >
                        {isPreviewMode ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                      </Button>
                      <Button variant="ghost" size="sm">
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="h-full">
                  <div className="border rounded-lg h-full bg-white dark:bg-gray-950 overflow-hidden">
                    {isPreviewMode ? (
                      <iframe
                        src={testUrl}
                        className="w-full h-full"
                        sandbox="allow-scripts allow-same-origin"
                        title="Preview"
                      />
                    ) : (
                      <div className="h-full flex items-center justify-center text-gray-500 dark:text-gray-400">
                        <div className="text-center">
                          <Eye className="h-12 w-12 mx-auto mb-2 opacity-50" />
                          <p>Click preview to load target page</p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Tester Tab */}
        <TabsContent value="tester" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Batch Selector Testing</CardTitle>
              <CardDescription>Test multiple selectors against your target pages</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {selectedSelectors.map((selector) => (
                  <div key={selector.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="font-medium">{selector.name}</h4>
                        <Badge variant={selector.type === "css" ? "default" : "secondary"}>
                          {selector.type.toUpperCase()}
                        </Badge>
                        {selector.isValid ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        )}
                      </div>
                      <code className="text-sm text-gray-600 dark:text-gray-400 font-mono">
                        {selector.selector}
                      </code>
                      <div className="flex gap-4 text-xs text-gray-500 mt-2">
                        <span>Matches: {selector.matchCount}</span>
                        <span>Confidence: {selector.confidence}%</span>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Play className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Copy className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Library Tab */}
        <TabsContent value="library" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockSelectors.map((selector) => (
              <Card key={selector.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{selector.name}</CardTitle>
                    <Badge variant={selector.type === "css" ? "default" : "secondary"}>
                      {selector.type.toUpperCase()}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="font-mono text-sm p-2 bg-gray-100 dark:bg-gray-800 rounded">
                    {selector.selector}
                  </div>
                  <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                    <span>{selector.matchCount} matches</span>
                    <span>{selector.confidence}% confidence</span>
                  </div>
                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" className="flex-1">
                      <Play className="h-3 w-3 mr-1" />
                      Test
                    </Button>
                    <Button size="sm" variant="outline">
                      <Copy className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Examples Tab */}
        <TabsContent value="examples" className="space-y-4">
          {selectorExamples.map((category) => (
            <Card key={category.category}>
              <CardHeader>
                <CardTitle>{category.category} Selectors</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {category.examples.map((example, index) => (
                    <div key={index} className="border rounded-lg p-4 space-y-2">
                      <h4 className="font-medium">{example.name}</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <div className="text-xs text-gray-500 mb-1">CSS Selector</div>
                          <code className="text-sm bg-gray-100 dark:bg-gray-800 p-2 rounded block">
                            {example.css}
                          </code>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500 mb-1">XPath</div>
                          <code className="text-sm bg-gray-100 dark:bg-gray-800 p-2 rounded block">
                            {example.xpath}
                          </code>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline">
                          <Copy className="h-3 w-3 mr-1" />
                          Copy CSS
                        </Button>
                        <Button size="sm" variant="outline">
                          <Copy className="h-3 w-3 mr-1" />
                          Copy XPath
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>
    </div>
    </Layout>
  );
}
