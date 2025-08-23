"use client";

import Layout from "@/components/Layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { 
  Download,
  Upload,
  FileText,
  Database,
  Settings,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
  Search,
  Filter,
  Plus,
  Eye,
  Trash2,
  Calendar,
  BarChart3,
  FileJson,
  FileSpreadsheet,
  Code,
  Globe
} from "lucide-react";
import { useState } from "react";

// Mock export data
const mockExports = [
  {
    id: "export_001",
    name: "vehicles_Q3_2024.csv",
    format: "CSV",
    size: "45.2 MB",
    records: 89432,
    status: "completed",
    progress: 100,
    createdAt: "2024-01-15 14:30:00",
    completedAt: "2024-01-15 14:32:15",
    downloadUrl: "/exports/vehicles_Q3_2024.csv",
    source: "biluppgifter.se",
    fields: ["make", "model", "year", "price", "mileage", "location"]
  },
  {
    id: "export_002",
    name: "business_directory.json",
    format: "JSON",
    size: "23.1 MB", 
    records: 34567,
    status: "processing",
    progress: 67,
    createdAt: "2024-01-15 13:45:00",
    completedAt: null,
    downloadUrl: null,
    source: "hitta.se",
    fields: ["name", "address", "phone", "website", "category"]
  },
  {
    id: "export_003",
    name: "car_listings_september.csv",
    format: "CSV",
    size: "67.8 MB",
    records: 123890,
    status: "completed",
    progress: 100,
    createdAt: "2024-01-13 09:15:00",
    completedAt: "2024-01-13 09:18:42",
    downloadUrl: "/exports/car_listings_september.csv",
    source: "blocket.se",
    fields: ["title", "price", "year", "mileage", "seller", "description"]
  },
  {
    id: "export_004",
    name: "real_estate_data.xml", 
    format: "XML",
    size: "12.3 MB",
    records: 8934,
    status: "failed",
    progress: 45,
    createdAt: "2024-01-15 11:20:00",
    completedAt: null,
    downloadUrl: null,
    source: "hemnet.se", 
    fields: ["address", "price", "rooms", "area", "type"],
    error: "Source unavailable - connection timeout"
  }
];

const exportFormats = [
  {
    name: "CSV",
    icon: FileSpreadsheet,
    description: "Comma-separated values for spreadsheet applications",
    extension: ".csv",
    features: ["Excel compatible", "Lightweight", "Universal support"]
  },
  {
    name: "JSON",
    icon: FileJson,
    description: "JavaScript Object Notation for APIs and applications",
    extension: ".json",
    features: ["Structured data", "API friendly", "Nested objects"]
  },
  {
    name: "XML",
    icon: Code,
    description: "Extensible Markup Language with schema validation",
    extension: ".xml", 
    features: ["Schema validation", "Hierarchical", "Standards compliant"]
  },
  {
    name: "Excel",
    icon: FileSpreadsheet,
    description: "Native Excel format with formatting and formulas",
    extension: ".xlsx",
    features: ["Rich formatting", "Multiple sheets", "Formulas support"]
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "completed": return "text-green-600 dark:text-green-400";
    case "processing": return "text-blue-600 dark:text-blue-400";
    case "failed": return "text-red-600 dark:text-red-400";
    case "queued": return "text-yellow-600 dark:text-yellow-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "completed": return CheckCircle;
    case "processing": return RefreshCw;
    case "failed": return XCircle;
    case "queued": return Clock;
    default: return Clock;
  }
};

const getStatusBadge = (status: string) => {
  switch (status) {
    case "completed": return "default";
    case "processing": return "secondary";
    case "failed": return "destructive";
    case "queued": return "outline";
    default: return "outline";
  }
};

const formatFileSize = (bytes: string) => {
  const size = parseFloat(bytes.replace(/[^\d.]/g, ''));
  const unit = bytes.replace(/[\d.\s]/g, '');
  return `${size} ${unit}`;
};

export default function ExportsPage() {
  const [activeTab, setActiveTab] = useState("exports");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedFormat, setSelectedFormat] = useState("CSV");

  const filteredExports = mockExports.filter(exportItem =>
    exportItem.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    exportItem.source.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Data Exports</h1>
          <p className="text-gray-600 dark:text-gray-400">Export and download your collected data in various formats</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Import Data
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Export Settings
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Create Export
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Exports</p>
                <p className="text-2xl font-bold">{mockExports.length}</p>
              </div>
              <FileText className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {mockExports.filter(e => e.status === "completed").length}
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
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Records</p>
                <p className="text-2xl font-bold">256K</p>
                <p className="text-xs text-gray-500">Exported</p>
              </div>
              <Database className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Data Size</p>
                <p className="text-2xl font-bold">148MB</p>
                <p className="text-xs text-gray-500">Total exported</p>
              </div>
              <BarChart3 className="h-8 w-8 text-orange-600 dark:text-orange-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="exports">Recent Exports</TabsTrigger>
          <TabsTrigger value="create">Create Export</TabsTrigger>
          <TabsTrigger value="formats">Export Formats</TabsTrigger>
          <TabsTrigger value="scheduled">Scheduled Exports</TabsTrigger>
        </TabsList>

        {/* Recent Exports Tab */}
        <TabsContent value="exports" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search exports..."
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

          {/* Export List */}
          <div className="space-y-4">
            {filteredExports.map((exportItem) => {
              const StatusIcon = getStatusIcon(exportItem.status);
              const FormatIcon = exportItem.format === "JSON" ? FileJson : FileSpreadsheet;
              
              return (
                <Card key={exportItem.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <FormatIcon className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                        <div>
                          <h3 className="font-semibold text-lg">{exportItem.name}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Source: {exportItem.source}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant={getStatusBadge(exportItem.status)}>
                          <StatusIcon className="h-3 w-3 mr-1" />
                          {exportItem.status}
                        </Badge>
                        <Badge variant="outline">{exportItem.format}</Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Records</span>
                        <p className="font-medium">{exportItem.records.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Size</span>
                        <p className="font-medium">{exportItem.size}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Created</span>
                        <p className="font-medium">{exportItem.createdAt}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Completed</span>
                        <p className="font-medium">{exportItem.completedAt || "In progress"}</p>
                      </div>
                    </div>

                    {exportItem.status === "processing" && (
                      <div className="mb-4">
                        <div className="flex justify-between text-sm mb-1">
                          <span>Progress</span>
                          <span>{exportItem.progress}%</span>
                        </div>
                        <Progress value={exportItem.progress} className="h-2" />
                      </div>
                    )}

                    {exportItem.error && (
                      <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                        <div className="flex items-center gap-2 text-red-600 dark:text-red-400 text-sm">
                          <XCircle className="h-4 w-4" />
                          <span>{exportItem.error}</span>
                        </div>
                      </div>
                    )}

                    <div className="mb-4">
                      <h4 className="font-medium text-sm mb-2">Exported Fields:</h4>
                      <div className="flex flex-wrap gap-1">
                        {exportItem.fields.map((field, idx) => (
                          <Badge key={idx} variant="outline" className="text-xs">
                            {field}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    <div className="flex gap-2 pt-4 border-t">
                      {exportItem.status === "completed" && (
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        Preview
                      </Button>
                      {exportItem.status === "processing" && (
                        <Button variant="outline" size="sm">
                          <XCircle className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                      )}
                      {exportItem.status === "failed" && (
                        <Button variant="outline" size="sm">
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Retry
                        </Button>
                      )}
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Create Export Tab */}
        <TabsContent value="create" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Create New Export</CardTitle>
              <CardDescription>Export data from your crawled sources</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Export Configuration */}
                <div className="space-y-4">
                  <h4 className="font-medium">Export Configuration</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Export Name</label>
                      <Input placeholder="e.g., Monthly Vehicle Data Export" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Data Source</label>
                      <select className="w-full p-2 border rounded-lg bg-background">
                        <option>biluppgifter.se</option>
                        <option>hitta.se</option>
                        <option>blocket.se</option>
                        <option>hemnet.se</option>
                        <option>All sources</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Export Format</label>
                      <select 
                        className="w-full p-2 border rounded-lg bg-background"
                        value={selectedFormat}
                        onChange={(e) => setSelectedFormat(e.target.value)}
                      >
                        <option value="CSV">CSV - Comma Separated Values</option>
                        <option value="JSON">JSON - JavaScript Object Notation</option>
                        <option value="XML">XML - Extensible Markup Language</option>
                        <option value="Excel">Excel - Microsoft Excel Format</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Data Filters */}
                <div className="space-y-4">
                  <h4 className="font-medium">Data Filters</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Date Range</label>
                      <div className="grid grid-cols-2 gap-2">
                        <Input type="date" placeholder="Start date" />
                        <Input type="date" placeholder="End date" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Record Limit</label>
                      <Input type="number" placeholder="Max records (leave empty for all)" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Quality Threshold</label>
                      <select className="w-full p-2 border rounded-lg bg-background">
                        <option>All records</option>
                        <option>Quality score ≥ 90%</option>
                        <option>Quality score ≥ 80%</option>
                        <option>Quality score ≥ 70%</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Field Selection */}
              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Select Fields to Export</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                  {["title", "price", "make", "model", "year", "mileage", "location", "description", "images", "seller", "phone", "address"].map((field) => (
                    <div key={field} className="flex items-center space-x-2">
                      <input type="checkbox" defaultChecked className="rounded" />
                      <label className="text-sm capitalize">{field}</label>
                    </div>
                  ))}
                </div>
              </div>

              {/* Advanced Options */}
              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Advanced Options</h4>
                <div className="space-y-4">
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" />
                    <label className="text-sm">Include metadata (crawl date, source URL, etc.)</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" />
                    <label className="text-sm">Compress export file</label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <input type="checkbox" />
                    <label className="text-sm">Send notification email when complete</label>
                  </div>
                </div>
              </div>

              {/* Custom Filters */}
              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Custom Filters (Optional)</h4>
                <Textarea 
                  placeholder="Enter custom filter conditions (e.g., price > 100000 AND year > 2020)"
                  className="h-24"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button className="flex-1">
                  <Download className="h-4 w-4 mr-2" />
                  Create Export
                </Button>
                <Button variant="outline">
                  Save as Template
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Export Formats Tab */}
        <TabsContent value="formats" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {exportFormats.map((format) => {
              const FormatIcon = format.icon;
              return (
                <Card key={format.name} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-center gap-3">
                      <FormatIcon className="h-6 w-6 text-blue-600" />
                      <div>
                        <CardTitle className="text-lg">{format.name}</CardTitle>
                        <Badge variant="outline" className="text-xs">{format.extension}</Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{format.description}</p>
                    
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm">Features:</h4>
                      <ul className="space-y-1">
                        {format.features.map((feature, idx) => (
                          <li key={idx} className="text-sm flex items-center gap-2">
                            <CheckCircle className="h-3 w-3 text-green-600" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="pt-4">
                      <Button variant="outline" size="sm" className="w-full">
                        Use {format.name} Format
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Scheduled Exports Tab */}
        <TabsContent value="scheduled" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Scheduled Exports</CardTitle>
              <CardDescription>Automate regular data exports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-blue-600" />
                    <div>
                      <h4 className="font-medium">Weekly Vehicle Export</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Every Monday at 9:00 AM • CSV format
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="default">Active</Badge>
                    <Button variant="outline" size="sm">Configure</Button>
                  </div>
                </div>

                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-5 w-5 text-gray-400" />
                    <div>
                      <h4 className="font-medium">Monthly Business Directory</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        First day of month at 6:00 AM • JSON format
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">Paused</Badge>
                    <Button variant="outline" size="sm">Configure</Button>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t">
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Scheduled Export
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    </Layout>
  );
}
