import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search,
  Globe,
  Map,
  ExternalLink,
  Download,
  Upload,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  FileText,
  Settings,
  Eye,
  Play,
  Filter
} from "lucide-react";
import { useState } from "react";

// Mock sitemap data
const mockSitemaps = [
  {
    id: "sitemap_001",
    domain: "biluppgifter.se",
    url: "https://biluppgifter.se/sitemap.xml",
    status: "active",
    lastCrawled: "2024-01-15 14:30:00",
    urlCount: 12847,
    validUrls: 12203,
    errorUrls: 644,
    size: "2.3 MB",
    format: "XML",
    lastModified: "2024-01-15 10:15:00",
    crawlFrequency: "daily"
  },
  {
    id: "sitemap_002", 
    domain: "hitta.se",
    url: "https://hitta.se/sitemap.xml",
    status: "processing",
    lastCrawled: "2024-01-15 13:45:00",
    urlCount: 34567,
    validUrls: 33892,
    errorUrls: 675,
    size: "5.7 MB",
    format: "XML",
    lastModified: "2024-01-15 08:30:00",
    crawlFrequency: "weekly"
  },
  {
    id: "sitemap_003",
    domain: "newsportal.com", 
    url: "https://newsportal.com/sitemap.xml",
    status: "failed",
    lastCrawled: "2024-01-15 11:20:00",
    urlCount: 0,
    validUrls: 0,
    errorUrls: 0,
    size: "N/A",
    format: "XML",
    lastModified: "N/A",
    crawlFrequency: "hourly",
    error: "404 Not Found - Sitemap does not exist"
  },
  {
    id: "sitemap_004",
    domain: "marketplace.io",
    url: "https://marketplace.io/sitemap.xml", 
    status: "active",
    lastCrawled: "2024-01-15 09:15:00",
    urlCount: 8934,
    validUrls: 8756,
    errorUrls: 178,
    size: "1.8 MB", 
    format: "XML",
    lastModified: "2024-01-15 07:00:00",
    crawlFrequency: "daily"
  }
];

const mockSitemapIndex = [
  {
    domain: "biluppgifter.se",
    sitemaps: [
      { url: "/sitemap-products.xml", urls: 8934, lastMod: "2024-01-15" },
      { url: "/sitemap-categories.xml", urls: 234, lastMod: "2024-01-14" },
      { url: "/sitemap-brands.xml", urls: 567, lastMod: "2024-01-13" },
      { url: "/sitemap-news.xml", urls: 3112, lastMod: "2024-01-15" }
    ]
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return "text-green-600 dark:text-green-400";
    case "processing": return "text-blue-600 dark:text-blue-400";
    case "failed": return "text-red-600 dark:text-red-400";
    case "pending": return "text-yellow-600 dark:text-yellow-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "active": return CheckCircle;
    case "processing": return RefreshCw;
    case "failed": return XCircle;
    case "pending": return Clock;
    default: return AlertTriangle;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "active": return "default";
    case "processing": return "secondary";
    case "failed": return "destructive";
    case "pending": return "outline";
    default: return "outline";
  }
};

export default function SitemapsPage() {
  const [activeTab, setActiveTab] = useState("sitemaps");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");

  const filteredSitemaps = mockSitemaps.filter(sitemap => {
    const matchesSearch = sitemap.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         sitemap.url.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || sitemap.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Sitemap Manager</h1>
          <p className="text-gray-600 dark:text-gray-400">Discover and manage website sitemaps for efficient crawling</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Import Sitemap
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh All
          </Button>
          <Button size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Add Sitemap
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Sitemaps</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {mockSitemaps.filter(s => s.status === "active").length}
                </p>
              </div>
              <Map className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total URLs</p>
                <p className="text-2xl font-bold">56.3K</p>
                <p className="text-xs text-gray-500">Discovered</p>
              </div>
              <Globe className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Valid URLs</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">54.9K</p>
                <p className="text-xs text-gray-500">97.5% success rate</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Processing</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">1</p>
                <p className="text-xs text-gray-500">in progress</p>
              </div>
              <RefreshCw className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="sitemaps">Sitemaps</TabsTrigger>
          <TabsTrigger value="discovery">URL Discovery</TabsTrigger>
          <TabsTrigger value="analysis">Analysis</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Sitemaps Tab */}
        <TabsContent value="sitemaps" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search sitemaps..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                  >
                    <option value="all">All Status</option>
                    <option value="active">Active</option>
                    <option value="processing">Processing</option>
                    <option value="failed">Failed</option>
                    <option value="pending">Pending</option>
                  </select>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sitemap List */}
          <div className="space-y-4">
            {filteredSitemaps.map((sitemap) => {
              const StatusIcon = getStatusIcon(sitemap.status);
              
              return (
                <Card key={sitemap.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <StatusIcon className={`h-5 w-5 ${getStatusColor(sitemap.status)}`} />
                        <div>
                          <h3 className="font-semibold text-lg">{sitemap.domain}</h3>
                          <div className="flex items-center gap-2">
                            <a 
                              href={sitemap.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:underline flex items-center gap-1"
                            >
                              {sitemap.url}
                              <ExternalLink className="h-3 w-3" />
                            </a>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={getStatusBadge(sitemap.status)}>
                          {sitemap.status}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {sitemap.format}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Total URLs</span>
                        <p className="font-medium">{sitemap.urlCount.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Valid URLs</span>
                        <p className="font-medium text-green-600">{sitemap.validUrls.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Errors</span>
                        <p className="font-medium text-red-600">{sitemap.errorUrls.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Size</span>
                        <p className="font-medium">{sitemap.size}</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-4">
                      <span>Last crawled: {sitemap.lastCrawled}</span>
                      <span>Last modified: {sitemap.lastModified}</span>
                      <span>Frequency: {sitemap.crawlFrequency}</span>
                    </div>

                    {sitemap.error && (
                      <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <div className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm">
                          <AlertTriangle className="h-4 w-4" />
                          <span>{sitemap.error}</span>
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2 pt-4 border-t">
                      <Button variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                      </Button>
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View URLs
                      </Button>
                      <Button variant="outline" size="sm">
                        <Play className="h-4 w-4 mr-2" />
                        Crawl Now
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Export
                      </Button>
                      <Button variant="outline" size="sm">
                        <Settings className="h-4 w-4 mr-2" />
                        Configure
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* URL Discovery Tab */}
        <TabsContent value="discovery" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Automatic Sitemap Discovery</CardTitle>
              <CardDescription>Discover sitemaps automatically from domains</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input 
                  placeholder="Enter domain (e.g., example.com)" 
                  className="flex-1"
                />
                <Button>
                  <Search className="h-4 w-4 mr-2" />
                  Discover
                </Button>
              </div>
              
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <p>Common sitemap locations that will be checked:</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>/sitemap.xml</li>
                  <li>/sitemap_index.xml</li>
                  <li>/robots.txt (for sitemap references)</li>
                  <li>/sitemap/</li>
                  <li>/sitemaps/</li>
                </ul>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Sitemap Index Analysis</CardTitle>
              <CardDescription>Analyze sitemap index files</CardDescription>
            </CardHeader>
            <CardContent>
              {mockSitemapIndex.map((index, idx) => (
                <div key={idx} className="space-y-3">
                  <h4 className="font-medium">{index.domain}</h4>
                  <div className="space-y-2">
                    {index.sitemaps.map((sitemap, sIdx) => (
                      <div key={sIdx} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-blue-600" />
                          <span className="font-medium">{sitemap.url}</span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                          <span>{sitemap.urls.toLocaleString()} URLs</span>
                          <span>Last: {sitemap.lastMod}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analysis Tab */}
        <TabsContent value="analysis" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>URL Distribution</CardTitle>
                <CardDescription>URLs by domain and type</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <span className="font-medium">biluppgifter.se</span>
                    <Badge>12.8K URLs</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <span className="font-medium">hitta.se</span>
                    <Badge>34.6K URLs</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <span className="font-medium">marketplace.io</span>
                    <Badge>8.9K URLs</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Crawl Status</CardTitle>
                <CardDescription>Overall crawling health</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Success Rate</span>
                    <span className="font-medium text-green-600">97.5%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Average Response Time</span>
                    <span className="font-medium">1.2s</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Total Errors</span>
                    <span className="font-medium text-red-600">1,497</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Last Updated</span>
                    <span className="font-medium">2 hours ago</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>URL Patterns</CardTitle>
                <CardDescription>Common URL structures found</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>/products/*</span>
                    <span className="font-medium">45,230 URLs</span>
                  </div>
                  <div className="flex justify-between">
                    <span>/categories/*</span>
                    <span className="font-medium">2,340 URLs</span>
                  </div>
                  <div className="flex justify-between">
                    <span>/news/*</span>
                    <span className="font-medium">5,670 URLs</span>
                  </div>
                  <div className="flex justify-between">
                    <span>/brands/*</span>
                    <span className="font-medium">1,120 URLs</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Error Analysis</CardTitle>
                <CardDescription>Types of errors encountered</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>404 Not Found</span>
                    <span className="font-medium text-red-600">892</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Timeout</span>
                    <span className="font-medium text-yellow-600">234</span>
                  </div>
                  <div className="flex justify-between">
                    <span>403 Forbidden</span>
                    <span className="font-medium text-red-600">156</span>
                  </div>
                  <div className="flex justify-between">
                    <span>500 Server Error</span>
                    <span className="font-medium text-red-600">89</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Sitemap Settings</CardTitle>
              <CardDescription>Configure sitemap discovery and processing</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Automatic Discovery</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Automatically discover sitemaps for new domains</p>
                  </div>
                  <Button variant="outline" size="sm">Toggle</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Validate URLs</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Check if URLs in sitemaps are accessible</p>
                  </div>
                  <Button variant="outline" size="sm">Toggle</Button>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Default Crawl Frequency</label>
                  <select className="w-full p-2 border rounded-lg bg-background">
                    <option>Hourly</option>
                    <option>Daily</option>
                    <option>Weekly</option>
                    <option>Monthly</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Max URLs per Sitemap</label>
                  <Input type="number" defaultValue="50000" />
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Request Timeout (seconds)</label>
                  <Input type="number" defaultValue="30" />
                </div>
              </div>

              <div className="pt-4 border-t">
                <Button>Save Settings</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
