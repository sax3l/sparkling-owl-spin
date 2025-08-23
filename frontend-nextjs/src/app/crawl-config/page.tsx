"use client";

import Layout from "@/components/Layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { 
  Search,
  Globe,
  Settings,
  Code,
  FileText,
  Play,
  Save,
  Copy,
  Download,
  Upload,
  Zap,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Target,
  Network,
  Filter
} from "lucide-react";
import { useState } from "react";

// Mock crawl configurations
const mockCrawlConfigs = [
  {
    id: "config_001",
    name: "E-commerce Product Scraper",
    domain: "biluppgifter.se",
    template: "vehicle_listings.yaml",
    status: "active",
    lastUsed: "2024-01-15 14:30:00",
    jobsRun: 127,
    successRate: 96.8,
    selectors: {
      title: "h1.product-title",
      price: ".price-value",
      description: ".product-description",
      images: "img.product-image"
    },
    settings: {
      delay: 2000,
      concurrent: 5,
      retries: 3,
      respectRobots: true,
      userAgent: "ECaDP Bot 1.0"
    }
  },
  {
    id: "config_002",
    name: "Business Directory Crawler", 
    domain: "hitta.se",
    template: "business_listings.yaml",
    status: "active",
    lastUsed: "2024-01-15 12:15:00", 
    jobsRun: 89,
    successRate: 94.2,
    selectors: {
      name: ".company-name",
      address: ".address-info",
      phone: ".phone-number",
      website: ".website-link"
    },
    settings: {
      delay: 1500,
      concurrent: 3,
      retries: 2,
      respectRobots: true,
      userAgent: "ECaDP Business Bot 1.0"
    }
  },
  {
    id: "config_003",
    name: "News Article Extractor",
    domain: "newssite.com",
    template: "news_articles.yaml", 
    status: "draft",
    lastUsed: "Never",
    jobsRun: 0,
    successRate: 0,
    selectors: {
      headline: "h1.article-headline",
      author: ".author-name", 
      publishDate: ".publish-date",
      content: ".article-content"
    },
    settings: {
      delay: 3000,
      concurrent: 2,
      retries: 1,
      respectRobots: true,
      userAgent: "ECaDP News Bot 1.0"
    }
  }
];

const mockTemplates = [
  "vehicle_listings.yaml",
  "business_listings.yaml", 
  "news_articles.yaml",
  "real_estate.yaml",
  "product_catalog.yaml",
  "social_profiles.yaml",
  "job_postings.yaml"
];

export default function CrawlConfigPage() {
  const [activeTab, setActiveTab] = useState("configurations");
  const [selectedConfig, setSelectedConfig] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  const filteredConfigs = mockCrawlConfigs.filter(config =>
    config.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    config.domain.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "text-green-600 dark:text-green-400";
      case "draft": return "text-yellow-600 dark:text-yellow-400";
      case "disabled": return "text-red-600 dark:text-red-400";
      default: return "text-gray-600 dark:text-gray-400";
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active": return "default";
      case "draft": return "secondary";
      case "disabled": return "destructive";
      default: return "outline";
    }
  };

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Crawl Configuration</h1>
          <p className="text-gray-600 dark:text-gray-400">Create and manage crawling configurations and templates</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Import Config
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export All
          </Button>
          <Button size="sm">
            <Settings className="h-4 w-4 mr-2" />
            New Configuration
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Configs</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {mockCrawlConfigs.filter(c => c.status === "active").length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Templates</p>
                <p className="text-2xl font-bold">{mockTemplates.length}</p>
                <p className="text-xs text-gray-500">Available</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Success Rate</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">95.4%</p>
                <p className="text-xs text-gray-500">Average</p>
              </div>
              <Target className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Jobs</p>
                <p className="text-2xl font-bold">216</p>
                <p className="text-xs text-gray-500">Executed</p>
              </div>
              <Zap className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="configurations">Configurations</TabsTrigger>
          <TabsTrigger value="builder">Configuration Builder</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="global-settings">Global Settings</TabsTrigger>
        </TabsList>

        {/* Configurations Tab */}
        <TabsContent value="configurations" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search configurations..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Configuration List */}
          <div className="space-y-4">
            {filteredConfigs.map((config) => (
              <Card key={config.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Globe className={`h-5 w-5 ${getStatusColor(config.status)}`} />
                      <div>
                        <h3 className="font-semibold text-lg">{config.name}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{config.domain}</p>
                      </div>
                    </div>
                    <Badge variant={getStatusBadge(config.status)}>
                      {config.status}
                    </Badge>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Template</span>
                      <p className="font-medium">{config.template}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Jobs Run</span>
                      <p className="font-medium">{config.jobsRun}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Success Rate</span>
                      <p className="font-medium text-green-600">{config.successRate}%</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Last Used</span>
                      <p className="font-medium">{config.lastUsed}</p>
                    </div>
                  </div>

                  {selectedConfig === config.id && (
                    <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <h4 className="font-medium mb-3">Configuration Details</h4>
                      
                      <div className="space-y-4">
                        <div>
                          <h5 className="font-medium mb-2">Selectors</h5>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            {Object.entries(config.selectors).map(([key, value]) => (
                              <div key={key} className="flex">
                                <span className="w-20 text-gray-500 capitalize">{key}:</span>
                                <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-xs flex-1">
                                  {value}
                                </code>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h5 className="font-medium mb-2">Settings</h5>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                            {Object.entries(config.settings).map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="text-gray-500 capitalize">{key.replace(/([A-Z])/g, ' $1')}:</span>
                                <span className="font-medium">{value.toString()}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  <div className="flex gap-2 pt-4 border-t">
                    <Button variant="outline" size="sm">
                      <Play className="h-4 w-4 mr-2" />
                      Run Job
                    </Button>
                    <Button variant="outline" size="sm">
                      <Code className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <Copy className="h-4 w-4 mr-2" />
                      Clone
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setSelectedConfig(selectedConfig === config.id ? null : config.id)}
                    >
                      {selectedConfig === config.id ? "Hide Details" : "Show Details"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Configuration Builder Tab */}
        <TabsContent value="builder" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configuration Builder</CardTitle>
              <CardDescription>Create a new crawling configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Settings */}
                <div className="space-y-4">
                  <h4 className="font-medium">Basic Configuration</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Configuration Name</label>
                      <Input placeholder="e.g., Product Catalog Scraper" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Target Domain</label>
                      <Input placeholder="example.com" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Base Template</label>
                      <select className="w-full p-2 border rounded-lg bg-background">
                        <option value="">Select template...</option>
                        {mockTemplates.map(template => (
                          <option key={template} value={template}>{template}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                {/* Crawl Settings */}
                <div className="space-y-4">
                  <h4 className="font-medium">Crawl Settings</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Delay (ms)</label>
                      <Input type="number" placeholder="2000" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Concurrent Requests</label>
                      <Input type="number" placeholder="5" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Retry Attempts</label>
                      <Input type="number" placeholder="3" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">User Agent</label>
                      <Input placeholder="ECaDP Bot 1.0" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Selectors Configuration */}
              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Data Selectors</h4>
                <div className="space-y-3">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Field Name</label>
                      <Input placeholder="title" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">CSS Selector</label>
                      <Input placeholder="h1.product-title" />
                    </div>
                  </div>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Add Selector
                  </Button>
                </div>
              </div>

              {/* Configuration Preview */}
              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Configuration Preview</h4>
                <Textarea 
                  className="font-mono text-sm h-40"
                  placeholder="# Configuration will be generated here..."
                  readOnly
                />
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button className="flex-1">
                  <Save className="h-4 w-4 mr-2" />
                  Save Configuration
                </Button>
                <Button variant="outline">Test Configuration</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {mockTemplates.map((template) => (
              <Card key={template} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-blue-600" />
                    <CardTitle className="text-lg">{template.replace('.yaml', '').replace('_', ' ')}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      <p>Template for {template.replace('.yaml', '').replace('_', ' ')} extraction</p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1">
                        <Code className="h-4 w-4 mr-2" />
                        Edit
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1">
                        <Copy className="h-4 w-4 mr-2" />
                        Clone
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Global Settings Tab */}
        <TabsContent value="global-settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Global Crawl Settings</CardTitle>
              <CardDescription>Default settings applied to all new configurations</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Rate Limiting</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Default Delay (ms)</label>
                      <Input type="number" defaultValue="2000" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Max Concurrent Requests</label>
                      <Input type="number" defaultValue="10" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Rate Limit per Domain</label>
                      <Input placeholder="100 requests/minute" />
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h4 className="font-medium">Error Handling</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Default Retry Count</label>
                      <Input type="number" defaultValue="3" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Timeout (seconds)</label>
                      <Input type="number" defaultValue="30" />
                    </div>
                    <div className="flex items-center gap-2">
                      <input type="checkbox" defaultChecked />
                      <label className="text-sm">Respect robots.txt</label>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">User Agents</h4>
                <Textarea 
                  className="h-32"
                  placeholder="ECaDP Bot 1.0&#10;Mozilla/5.0 (compatible; ECaDP/1.0)&#10;..."
                  defaultValue="ECaDP Bot 1.0&#10;Mozilla/5.0 (compatible; ECaDP/1.0)"
                />
              </div>

              <div className="flex gap-2 pt-4 border-t">
                <Button>Save Global Settings</Button>
                <Button variant="outline">Reset to Defaults</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    </Layout>
  );
}
