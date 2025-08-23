import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { 
  Play, 
  Pause, 
  StopCircle, 
  RefreshCw, 
  Search, 
  Filter,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  MoreHorizontal,
  Download,
  Eye
} from "lucide-react";
import { useState } from "react";

// Mock job data based on the live demo analysis
const mockJobs = [
  {
    id: "job_67890",
    domain: "example.com",
    template: "E-commerce Product Scraper",
    status: "running",
    progress: 75,
    proxyClass: "Premium Rotating",
    startTime: "2024-01-15 10:30:15",
    estimatedCompletion: "2024-01-15 11:45:20",
    itemsProcessed: 1250,
    totalItems: 1667,
    successRate: 98.2,
    errors: 23
  },
  {
    id: "job_67891",
    domain: "marketplace.io",
    template: "Product Catalog Crawler",
    status: "completed",
    progress: 100,
    proxyClass: "Standard Pool",
    startTime: "2024-01-15 09:15:30",
    completedTime: "2024-01-15 10:22:45",
    itemsProcessed: 2890,
    totalItems: 2890,
    successRate: 99.7,
    errors: 9
  },
  {
    id: "job_67892",
    domain: "retailsite.net",
    template: "Inventory Tracker",
    status: "failed",
    progress: 32,
    proxyClass: "Premium Rotating",
    startTime: "2024-01-15 08:45:00",
    failedTime: "2024-01-15 09:12:33",
    itemsProcessed: 567,
    totalItems: 1800,
    successRate: 85.3,
    errors: 145,
    errorMessage: "Rate limit exceeded. Proxy rotation insufficient."
  },
  {
    id: "job_67893",
    domain: "newsportal.com",
    template: "Article Extractor",
    status: "queued",
    progress: 0,
    proxyClass: "Standard Pool",
    queuePosition: 3,
    estimatedStart: "2024-01-15 11:50:00",
    itemsProcessed: 0,
    totalItems: 450
  }
];

const statusConfig = {
  running: { color: "blue", icon: Play, label: "Running" },
  completed: { color: "green", icon: CheckCircle, label: "Completed" },
  failed: { color: "red", icon: XCircle, label: "Failed" },
  queued: { color: "yellow", icon: Clock, label: "Queued" }
};

export default function JobsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");

  const filteredJobs = mockJobs.filter(job => {
    const matchesSearch = job.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.template.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || job.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: string) => {
    const config = statusConfig[status as keyof typeof statusConfig];
    const Icon = config.icon;
    return (
      <Badge variant={status === "completed" ? "default" : status === "failed" ? "destructive" : "secondary"} 
             className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {config.label}
      </Badge>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Job Management</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor and manage your crawling jobs</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm">
            <Play className="h-4 w-4 mr-2" />
            New Job
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Running</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {mockJobs.filter(j => j.status === "running").length}
                </p>
              </div>
              <Play className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {mockJobs.filter(j => j.status === "completed").length}
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
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Failed</p>
                <p className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {mockJobs.filter(j => j.status === "failed").length}
                </p>
              </div>
              <XCircle className="h-8 w-8 text-red-600 dark:text-red-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Queued</p>
                <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {mockJobs.filter(j => j.status === "queued").length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search jobs by domain, template, or ID..."
                  className="pl-10"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Tabs value={selectedStatus} onValueChange={setSelectedStatus} className="w-auto">
                <TabsList>
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="running">Running</TabsTrigger>
                  <TabsTrigger value="completed">Completed</TabsTrigger>
                  <TabsTrigger value="failed">Failed</TabsTrigger>
                  <TabsTrigger value="queued">Queued</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Jobs List */}
      <div className="space-y-4">
        {filteredJobs.map((job) => (
          <Card key={job.id} className="hover:shadow-md transition-shadow">
            <CardContent className="p-6">
              <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                {/* Job Info */}
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-lg">{job.domain}</h3>
                    {getStatusBadge(job.status)}
                    <Badge variant="outline" className="text-xs">
                      {job.id}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Template: <span className="font-medium">{job.template}</span>
                  </p>
                  
                  <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                    <span>Proxy: {job.proxyClass}</span>
                    {job.status === "running" && (
                      <>
                        <span>Started: {job.startTime}</span>
                        <span>ETA: {job.estimatedCompletion}</span>
                      </>
                    )}
                    {job.status === "completed" && (
                      <span>Completed: {job.completedTime}</span>
                    )}
                    {job.status === "failed" && (
                      <span>Failed: {job.failedTime}</span>
                    )}
                    {job.status === "queued" && (
                      <>
                        <span>Queue Position: #{job.queuePosition}</span>
                        <span>Est. Start: {job.estimatedStart}</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Progress and Stats */}
                <div className="lg:w-80 space-y-3">
                  {job.status !== "queued" && (
                    <div className="space-y-1">
                      <div className="flex justify-between text-sm">
                        <span>Progress</span>
                        <span>{job.progress}%</span>
                      </div>
                      <Progress value={job.progress} className="h-2" />
                      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
                        <span>{job.itemsProcessed.toLocaleString()} / {job.totalItems.toLocaleString()}</span>
                        <span>Success: {job.successRate}%</span>
                      </div>
                    </div>
                  )}

                  {job.errors && job.errors > 0 && (
                    <div className="flex items-center gap-2 text-xs text-red-600 dark:text-red-400">
                      <AlertCircle className="h-3 w-3" />
                      <span>{job.errors} errors</span>
                    </div>
                  )}

                  {job.status === "failed" && job.errorMessage && (
                    <p className="text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded">
                      {job.errorMessage}
                    </p>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {job.status === "running" && (
                    <>
                      <Button variant="outline" size="sm">
                        <Pause className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <StopCircle className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                  
                  {job.status === "completed" && (
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4" />
                    </Button>
                  )}

                  {job.status === "failed" && (
                    <Button variant="outline" size="sm">
                      <RefreshCw className="h-4 w-4" />
                    </Button>
                  )}

                  <Button variant="outline" size="sm">
                    <Eye className="h-4 w-4" />
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

      {filteredJobs.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-gray-400 dark:text-gray-600">
              <Search className="h-12 w-12 mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No jobs found</h3>
              <p>Try adjusting your search or filter criteria</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
