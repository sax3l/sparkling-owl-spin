import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  Search,
  Download,
  Filter,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  MoreHorizontal,
  Grid,
  List,
  BarChart3,
  FileJson,
  FileSpreadsheet,
  FileText,
  Calendar,
  Globe,
  TrendingUp,
  Database,
  Share
} from "lucide-react";
import { useState } from "react";

// Mock data
const mockDataSets = [
  {
    id: "ds_001",
    name: "E-commerce Products - example.com",
    description: "Product listings with prices and inventory",
    recordCount: 15420,
    lastUpdated: "2024-01-15 14:30:00",
    source: "example.com",
    template: "E-commerce Product Scraper", 
    status: "active",
    fields: ["title", "price", "description", "images", "stock", "rating"],
    size: "124.5 MB",
    format: "JSON"
  },
  {
    id: "ds_002",
    name: "News Articles - newsportal.com", 
    description: "Daily news articles with metadata",
    recordCount: 8950,
    lastUpdated: "2024-01-15 12:15:00",
    source: "newsportal.com",
    template: "Article Extractor",
    status: "active", 
    fields: ["headline", "content", "author", "publish_date", "category"],
    size: "89.2 MB",
    format: "JSON"
  },
  {
    id: "ds_003",
    name: "Real Estate Listings",
    description: "Property listings from multiple sources",
    recordCount: 3240,
    lastUpdated: "2024-01-15 10:45:00", 
    source: "multiple",
    template: "Real Estate Listings",
    status: "archived",
    fields: ["address", "price", "bedrooms", "bathrooms", "square_feet"],
    size: "45.8 MB",
    format: "CSV"
  }
];

const mockRecords = [
  {
    id: 1,
    title: "Wireless Bluetooth Headphones",
    price: "$89.99",
    description: "High-quality wireless headphones with noise cancellation",
    stock: 156,
    rating: 4.5,
    images: 8,
    lastSeen: "2024-01-15 14:30:00"
  },
  {
    id: 2,
    title: "Smartphone Case - Premium Leather",
    price: "$24.99", 
    description: "Genuine leather case for flagship smartphones",
    stock: 89,
    rating: 4.2,
    images: 5,
    lastSeen: "2024-01-15 14:25:00"
  },
  {
    id: 3,
    title: "USB-C Cable - Fast Charging", 
    price: "$12.99",
    description: "3ft USB-C cable with fast charging support",
    stock: 234,
    rating: 4.8,
    images: 3,
    lastSeen: "2024-01-15 14:20:00"
  }
];

export default function DataViewsPage() {
  const [activeTab, setActiveTab] = useState("datasets");
  const [viewMode, setViewMode] = useState("table");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedDataset, setSelectedDataset] = useState(mockDataSets[0]);

  const filteredDatasets = mockDataSets.filter(dataset => 
    dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    dataset.source.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const exportData = (format: string) => {
    console.log(`Exporting data as ${format}`);
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Data Views</h1>
          <p className="text-gray-600 dark:text-gray-400">Browse and analyze your crawled data</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <BarChart3 className="h-4 w-4 mr-2" />
            Analytics
          </Button>
          <Button size="sm">
            <Share className="h-4 w-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="datasets">Data Sets</TabsTrigger>
          <TabsTrigger value="records">Records</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="exports">Exports</TabsTrigger>
        </TabsList>

        {/* Data Sets Tab */}
        <TabsContent value="datasets" className="space-y-4">
          {/* Search and Filters */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <Input
                    placeholder="Search datasets by name or source..."
                    className="pl-10"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="outline" size="sm">
                    <Calendar className="h-4 w-4 mr-2" />
                    Date Range
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {mockDataSets.length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Datasets</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {mockDataSets.reduce((sum, ds) => sum + ds.recordCount, 0).toLocaleString()}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Records</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  259.5 MB
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Total Size</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {mockDataSets.filter(ds => ds.status === "active").length}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400">Active Sets</div>
              </CardContent>
            </Card>
          </div>

          {/* Datasets List */}
          <div className="space-y-4">
            {filteredDatasets.map((dataset) => (
              <Card key={dataset.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-3">
                        <Database className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                        <h3 className="font-semibold text-lg">{dataset.name}</h3>
                        <Badge variant={dataset.status === "active" ? "default" : "secondary"}>
                          {dataset.status}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {dataset.format}
                        </Badge>
                      </div>
                      
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {dataset.description}
                      </p>
                      
                      <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>Records: {dataset.recordCount.toLocaleString()}</span>
                        <span>Size: {dataset.size}</span>
                        <span>Source: {dataset.source}</span>
                        <span>Updated: {dataset.lastUpdated}</span>
                      </div>

                      <div className="flex flex-wrap gap-1 mt-2">
                        {dataset.fields.slice(0, 4).map((field) => (
                          <Badge key={field} variant="secondary" className="text-xs">
                            {field}
                          </Badge>
                        ))}
                        {dataset.fields.length > 4 && (
                          <Badge variant="secondary" className="text-xs">
                            +{dataset.fields.length - 4}
                          </Badge>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setSelectedDataset(dataset)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Records Tab */}
        <TabsContent value="records" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div>
                  <CardTitle>Data Records - {selectedDataset.name}</CardTitle>
                  <CardDescription>
                    {selectedDataset.recordCount.toLocaleString()} records from {selectedDataset.source}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setViewMode(viewMode === "table" ? "grid" : "table")}
                  >
                    {viewMode === "table" ? <Grid className="h-4 w-4" /> : <List className="h-4 w-4" />}
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {viewMode === "table" ? (
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Price</TableHead>
                        <TableHead>Stock</TableHead>
                        <TableHead>Rating</TableHead>
                        <TableHead>Images</TableHead>
                        <TableHead>Last Seen</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {mockRecords.map((record) => (
                        <TableRow key={record.id}>
                          <TableCell className="font-mono text-sm">{record.id}</TableCell>
                          <TableCell className="max-w-xs truncate">{record.title}</TableCell>
                          <TableCell className="font-semibold text-green-600">{record.price}</TableCell>
                          <TableCell>{record.stock}</TableCell>
                          <TableCell>⭐ {record.rating}</TableCell>
                          <TableCell>{record.images}</TableCell>
                          <TableCell className="text-xs text-gray-500">{record.lastSeen}</TableCell>
                          <TableCell>
                            <div className="flex gap-1">
                              <Button variant="ghost" size="sm">
                                <Eye className="h-3 w-3" />
                              </Button>
                              <Button variant="ghost" size="sm">
                                <Edit className="h-3 w-3" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {mockRecords.map((record) => (
                    <Card key={record.id}>
                      <CardContent className="p-4">
                        <div className="space-y-2">
                          <h4 className="font-medium line-clamp-2">{record.title}</h4>
                          <div className="flex items-center justify-between">
                            <span className="font-semibold text-green-600">{record.price}</span>
                            <span className="text-sm">⭐ {record.rating}</span>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                            {record.description}
                          </p>
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>Stock: {record.stock}</span>
                            <span>Images: {record.images}</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Data Growth
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-400 dark:text-gray-600">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto mb-2" />
                    <p>Analytics charts will be rendered here</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Sources Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {["example.com", "newsportal.com", "marketplace.io"].map((source) => (
                    <div key={source} className="flex items-center justify-between p-3 border rounded">
                      <span className="font-medium">{source}</span>
                      <Badge variant="secondary">
                        {Math.floor(Math.random() * 10000) + 1000} records
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Exports Tab */}
        <TabsContent value="exports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Export Data</CardTitle>
              <CardDescription>Choose format and download your data</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Button 
                  variant="outline" 
                  className="h-20 flex-col gap-2"
                  onClick={() => exportData("json")}
                >
                  <FileJson className="h-6 w-6" />
                  <span>JSON</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-20 flex-col gap-2"
                  onClick={() => exportData("csv")}
                >
                  <FileSpreadsheet className="h-6 w-6" />
                  <span>CSV</span>
                </Button>
                <Button 
                  variant="outline" 
                  className="h-20 flex-col gap-2"
                  onClick={() => exportData("xml")}
                >
                  <FileText className="h-6 w-6" />
                  <span>XML</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
