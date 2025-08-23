"use client";

import Layout from "@/components/Layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Search,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Target,
  Database,
  FileText,
  Settings,
  RefreshCw,
  Filter,
  Eye,
  BarChart3,
  PieChart,
  Activity
} from "lucide-react";
import { useState } from "react";

// Mock data quality metrics
const qualityMetrics = {
  overall: 87.3,
  completeness: 92.1,
  accuracy: 89.7,
  consistency: 85.3,
  timeliness: 91.8,
  validity: 86.9,
  uniqueness: 94.2
};

const mockQualityChecks = [
  {
    id: "check_001",
    name: "Vehicle Data Validation",
    source: "biluppgifter.se",
    status: "passed",
    score: 94.2,
    timestamp: "2024-01-15 14:35:00",
    recordsChecked: 12847,
    issues: 67,
    category: "accuracy",
    details: "Price format validation, VIN number format, year range checks"
  },
  {
    id: "check_002",
    name: "Business Directory Completeness",
    source: "hitta.se", 
    status: "warning",
    score: 78.1,
    timestamp: "2024-01-15 14:20:00",
    recordsChecked: 8934,
    issues: 1956,
    category: "completeness",
    details: "Missing phone numbers (15%), incomplete addresses (7%)"
  },
  {
    id: "check_003",
    name: "Price Format Consistency",
    source: "car.info",
    status: "passed",
    score: 96.8,
    timestamp: "2024-01-15 14:15:00",
    recordsChecked: 5623,
    issues: 18,
    category: "consistency", 
    details: "Currency format standardization, decimal places validation"
  },
  {
    id: "check_004",
    name: "Duplicate Detection",
    source: "blocket.se",
    status: "failed",
    score: 67.3,
    timestamp: "2024-01-15 14:10:00",
    recordsChecked: 3456,
    issues: 1129,
    category: "uniqueness",
    details: "32.7% duplicate entries found based on title and description similarity"
  },
  {
    id: "check_005",
    name: "Data Freshness Check",
    source: "marketplace.io",
    status: "passed", 
    score: 89.4,
    timestamp: "2024-01-15 14:05:00",
    recordsChecked: 7890,
    issues: 836,
    category: "timeliness",
    details: "10.6% of records older than 30 days, within acceptable limits"
  }
];

const mockDataSources = [
  {
    name: "biluppgifter.se",
    records: 12847,
    qualityScore: 94.2,
    lastCheck: "5 min ago",
    status: "healthy",
    issues: ["Minor price format inconsistencies"]
  },
  {
    name: "hitta.se", 
    records: 8934,
    qualityScore: 78.1,
    lastCheck: "12 min ago", 
    status: "warning",
    issues: ["Missing contact information", "Incomplete addresses"]
  },
  {
    name: "car.info",
    records: 5623,
    qualityScore: 96.8,
    lastCheck: "18 min ago",
    status: "healthy",
    issues: []
  },
  {
    name: "blocket.se",
    records: 3456,
    qualityScore: 67.3,
    lastCheck: "25 min ago",
    status: "critical",
    issues: ["High duplicate rate", "Inconsistent data format"]
  }
];

const mockIssues = [
  {
    id: "issue_001",
    type: "completeness",
    severity: "high",
    title: "Missing Required Fields",
    description: "15% of business records missing phone numbers",
    source: "hitta.se",
    affectedRecords: 1340,
    firstSeen: "2024-01-15 10:30:00",
    status: "open"
  },
  {
    id: "issue_002", 
    type: "uniqueness",
    severity: "critical",
    title: "High Duplicate Rate",
    description: "32.7% duplicate entries detected in product listings",
    source: "blocket.se", 
    affectedRecords: 1129,
    firstSeen: "2024-01-15 09:15:00",
    status: "investigating"
  },
  {
    id: "issue_003",
    type: "accuracy",
    severity: "medium", 
    title: "Invalid Price Format",
    description: "Price values contain non-numeric characters",
    source: "marketplace.io",
    affectedRecords: 234,
    firstSeen: "2024-01-15 11:45:00",
    status: "resolved"
  }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "passed": return "text-green-600 dark:text-green-400";
    case "warning": return "text-yellow-600 dark:text-yellow-400";
    case "failed": return "text-red-600 dark:text-red-400";
    case "healthy": return "text-green-600 dark:text-green-400";
    case "critical": return "text-red-600 dark:text-red-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "passed": return CheckCircle;
    case "warning": return AlertTriangle;
    case "failed": return XCircle;
    case "healthy": return CheckCircle;
    case "critical": return XCircle;
    default: return Clock;
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity) {
    case "critical": return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
    case "high": return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200";
    case "medium": return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
    case "low": return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    default: return "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200";
  }
};

const getQualityColor = (score: number) => {
  if (score >= 90) return "text-green-600 dark:text-green-400";
  if (score >= 70) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
};

export default function DataQualityPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [searchTerm, setSearchTerm] = useState("");

  const filteredChecks = mockQualityChecks.filter(check =>
    check.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    check.source.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Data Quality Panel</h1>
          <p className="text-gray-600 dark:text-gray-400">Monitor and analyze data quality across all sources</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Configure Rules
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Analysis
          </Button>
          <Button size="sm">
            <Target className="h-4 w-4 mr-2" />
            Run Quality Check
          </Button>
        </div>
      </div>

      {/* Overall Quality Score */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-2">Overall Data Quality</h3>
              <div className="flex items-center gap-4">
                <div className="text-4xl font-bold text-primary">{qualityMetrics.overall}%</div>
                <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-sm">+2.1% this week</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">2.1M</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Records analyzed</div>
              <div className="text-sm text-green-600 dark:text-green-400">94.2% valid</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quality Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
        {Object.entries(qualityMetrics).filter(([key]) => key !== "overall").map(([key, value]) => (
          <Card key={key}>
            <CardContent className="p-4">
              <div className="text-center">
                <div className={`text-2xl font-bold ${getQualityColor(value)}`}>{value}%</div>
                <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                  {key}
                </div>
                <Progress value={value} className="mt-2 h-2" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Quality Overview</TabsTrigger>
          <TabsTrigger value="checks">Recent Checks</TabsTrigger>
          <TabsTrigger value="sources">Source Analysis</TabsTrigger>
          <TabsTrigger value="issues">Data Issues</TabsTrigger>
          <TabsTrigger value="trends">Quality Trends</TabsTrigger>
        </TabsList>

        {/* Quality Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Quality Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Excellent (90-100%)</span>
                    <div className="flex items-center gap-2">
                      <Progress value={35} className="w-20 h-2" />
                      <span className="text-sm font-medium">35%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Good (80-89%)</span>
                    <div className="flex items-center gap-2">
                      <Progress value={42} className="w-20 h-2" />
                      <span className="text-sm font-medium">42%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Fair (70-79%)</span>
                    <div className="flex items-center gap-2">
                      <Progress value={18} className="w-20 h-2" />
                      <span className="text-sm font-medium">18%</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Poor (&lt;70%)</span>
                    <div className="flex items-center gap-2">
                      <Progress value={5} className="w-20 h-2" />
                      <span className="text-sm font-medium">5%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  Issue Categories
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Completeness Issues</span>
                    <Badge variant="secondary">42%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Accuracy Issues</span>
                    <Badge variant="secondary">28%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Consistency Issues</span>
                    <Badge variant="secondary">18%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Uniqueness Issues</span>
                    <Badge variant="secondary">12%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Quality Alerts
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 p-2 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <XCircle className="h-4 w-4 text-red-600" />
                    <span className="text-sm">High duplicate rate detected</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <span className="text-sm">Completeness below threshold</span>
                  </div>
                  <div className="flex items-center gap-2 p-2 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm">Data validation improved</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Quality Targets</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Overall Target</span>
                      <span>90%</span>
                    </div>
                    <Progress value={87.3} className="h-2" />
                    <div className="text-xs text-gray-500 mt-1">87.3% / 90% target</div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Completeness Target</span>
                      <span>95%</span>
                    </div>
                    <Progress value={92.1} className="h-2" />
                    <div className="text-xs text-gray-500 mt-1">92.1% / 95% target</div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Accuracy Target</span>
                      <span>95%</span>
                    </div>
                    <Progress value={89.7} className="h-2" />
                    <div className="text-xs text-gray-500 mt-1">89.7% / 95% target</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Recent Checks Tab */}
        <TabsContent value="checks" className="space-y-4">
          {/* Search */}
          <Card>
            <CardContent className="p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search quality checks..."
                  className="pl-10"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </CardContent>
          </Card>

          {/* Quality Checks */}
          <div className="space-y-4">
            {filteredChecks.map((check) => {
              const StatusIcon = getStatusIcon(check.status);
              
              return (
                <Card key={check.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <StatusIcon className={`h-5 w-5 ${getStatusColor(check.status)}`} />
                        <div>
                          <h3 className="font-semibold text-lg">{check.name}</h3>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Source: {check.source}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`text-2xl font-bold ${getQualityColor(check.score)}`}>
                          {check.score}%
                        </div>
                        <Badge variant="outline" className="text-xs capitalize">
                          {check.category}
                        </Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mb-4">
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Records Checked</span>
                        <p className="font-medium">{check.recordsChecked.toLocaleString()}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Issues Found</span>
                        <p className="font-medium text-red-600">{check.issues}</p>
                      </div>
                      <div>
                        <span className="text-gray-500 dark:text-gray-400">Completed</span>
                        <p className="font-medium">{check.timestamp}</p>
                      </div>
                    </div>

                    <div className="mb-4 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <p className="text-sm">{check.details}</p>
                    </div>

                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                      <Button variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Re-run Check
                      </Button>
                      <Button variant="outline" size="sm">
                        <FileText className="h-4 w-4 mr-2" />
                        Export Report
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Source Analysis Tab */}
        <TabsContent value="sources" className="space-y-4">
          <div className="space-y-4">
            {mockDataSources.map((source, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <Database className={`h-5 w-5 ${getStatusColor(source.status)}`} />
                      <div>
                        <h3 className="font-semibold text-lg">{source.name}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {source.records.toLocaleString()} records • Last check: {source.lastCheck}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-2xl font-bold ${getQualityColor(source.qualityScore)}`}>
                        {source.qualityScore}%
                      </div>
                      <Badge variant={source.status === "healthy" ? "default" : source.status === "warning" ? "secondary" : "destructive"}>
                        {source.status}
                      </Badge>
                    </div>
                  </div>

                  {source.issues.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm">Issues:</h4>
                      {source.issues.map((issue, idx) => (
                        <div key={idx} className="flex items-center gap-2 text-sm">
                          <AlertTriangle className="h-3 w-3 text-yellow-600" />
                          <span>{issue}</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {source.issues.length === 0 && (
                    <div className="flex items-center gap-2 text-sm text-green-600">
                      <CheckCircle className="h-3 w-3" />
                      <span>No issues detected</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Data Issues Tab */}
        <TabsContent value="issues" className="space-y-4">
          <div className="space-y-4">
            {mockIssues.map((issue) => (
              <Card key={issue.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <AlertTriangle className="h-5 w-5 text-red-600" />
                      <div>
                        <h3 className="font-semibold text-lg">{issue.title}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">Source: {issue.source}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getSeverityColor(issue.severity)}>
                        {issue.severity}
                      </Badge>
                      <Badge variant="outline" className="capitalize">
                        {issue.type}
                      </Badge>
                    </div>
                  </div>

                  <p className="text-gray-700 dark:text-gray-300 mb-4">{issue.description}</p>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mb-4">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Affected Records</span>
                      <p className="font-medium text-red-600">{issue.affectedRecords.toLocaleString()}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">First Seen</span>
                      <p className="font-medium">{issue.firstSeen}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Status</span>
                      <Badge variant="outline" className="capitalize text-xs">
                        {issue.status}
                      </Badge>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Eye className="h-4 w-4 mr-2" />
                      View Records
                    </Button>
                    <Button variant="outline" size="sm">
                      Assign
                    </Button>
                    <Button variant="outline" size="sm">
                      Mark Resolved
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Quality Trends Tab */}
        <TabsContent value="trends" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Quality Score Trend</CardTitle>
                <CardDescription>Overall data quality over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📈 Quality trend chart (87.3% current, +2.1% improvement)
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Issue Resolution Rate</CardTitle>
                <CardDescription>How quickly issues are being resolved</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📊 Resolution rate chart (avg 2.3 days)
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Source Quality Comparison</CardTitle>
                <CardDescription>Quality scores by data source</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mockDataSources.map((source, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <span className="text-sm">{source.name}</span>
                      <div className="flex items-center gap-2">
                        <Progress value={source.qualityScore} className="w-20 h-2" />
                        <span className={`text-sm font-medium ${getQualityColor(source.qualityScore)}`}>
                          {source.qualityScore}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Monthly Quality Metrics</CardTitle>
                <CardDescription>Key metrics performance this month</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Records Processed</span>
                    <span className="font-medium">2.1M</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Quality Checks Run</span>
                    <span className="font-medium">1,247</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Issues Identified</span>
                    <span className="font-medium">342</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Issues Resolved</span>
                    <span className="font-medium text-green-600">318</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
    </Layout>
  );
}
