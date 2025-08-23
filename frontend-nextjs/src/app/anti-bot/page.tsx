"use client";

import Layout from "@/components/Layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { 
  ShieldCheck,
  AlertTriangle,
  Bot,
  Activity,
  Clock,
  Settings,
  Plus,
  Search,
  BarChart3,
  Eye,
  Shield,
  Zap,
  Key
} from "lucide-react";

// Mock anti-bot policy data
const mockPolicies = [
  {
    id: "1",
    name: "E-commerce Standard",
    domain: "*.example-shop.com",
    status: "active",
    detectionRate: 94.2,
    blockedRequests: 1247,
    falsePositives: 3,
    lastUpdated: "2024-01-15 14:30:00",
    rules: [
      { type: "Rate Limiting", value: "10 req/min", enabled: true },
      { type: "User-Agent Filter", value: "Bot patterns", enabled: true },
      { type: "Javascript Challenge", value: "Required", enabled: true },
      { type: "CAPTCHA", value: "On suspicious", enabled: false }
    ]
  },
  {
    id: "2", 
    name: "News Portal Aggressive",
    domain: "news-site.com",
    status: "active",
    detectionRate: 97.8,
    blockedRequests: 892,
    falsePositives: 8,
    lastUpdated: "2024-01-15 14:25:15",
    rules: [
      { type: "Rate Limiting", value: "5 req/min", enabled: true },
      { type: "Fingerprinting", value: "Advanced", enabled: true },
      { type: "Behavioral Analysis", value: "ML-based", enabled: true },
      { type: "CAPTCHA", value: "Always", enabled: true }
    ]
  },
  {
    id: "3",
    name: "API Protection Basic",
    domain: "api.service.com",
    status: "warning",
    detectionRate: 89.1,
    blockedRequests: 456,
    falsePositives: 12,
    lastUpdated: "2024-01-15 14:20:00",
    rules: [
      { type: "API Key Validation", value: "Required", enabled: true },
      { type: "Rate Limiting", value: "100 req/min", enabled: true },
      { type: "IP Whitelist", value: "Trusted IPs", enabled: false },
      { type: "Request Signing", value: "HMAC-SHA256", enabled: true }
    ]
  }
];

const getStatusColor = (status: string) => {
  switch(status) {
    case "active": return "text-green-600 bg-green-100 dark:bg-green-900";
    case "warning": return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900";
    case "inactive": return "text-gray-600 bg-gray-100 dark:bg-gray-900";
    default: return "text-gray-600 bg-gray-100 dark:bg-gray-900";
  }
};

const getRuleTypeIcon = (type: string) => {
  switch(type) {
    case "Rate Limiting": return <Clock className="w-4 h-4" />;
    case "User-Agent Filter": return <Bot className="w-4 h-4" />;
    case "Javascript Challenge": return <Zap className="w-4 h-4" />;
    case "CAPTCHA": return <Shield className="w-4 h-4" />;
    case "Fingerprinting": return <Eye className="w-4 h-4" />;
    case "Behavioral Analysis": return <BarChart3 className="w-4 h-4" />;
    case "API Key Validation": return <Key className="w-4 h-4" />;
    case "IP Whitelist": return <ShieldCheck className="w-4 h-4" />;
    case "Request Signing": return <Settings className="w-4 h-4" />;
    default: return <Shield className="w-4 h-4" />;
  }
};

export default function AntiBotPage() {
  const [activeTab, setActiveTab] = useState("policies");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");

  const filteredPolicies = mockPolicies.filter(policy => {
    const matchesSearch = policy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         policy.domain.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || policy.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Anti-bot Policyer</h1>
          <p className="text-gray-600 dark:text-gray-400">Konfigurera och hantera bot-detection och skydd</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Activity className="w-4 h-4 mr-2" />
            Live Status
          </Button>
          <Button size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Ny Policy
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Aktiva Policyer</p>
                <p className="text-2xl font-bold text-green-600">
                  {mockPolicies.filter(p => p.status === 'active').length}
                </p>
              </div>
              <ShieldCheck className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Blockerade Requests</p>
                <p className="text-2xl font-bold text-red-600">
                  {mockPolicies.reduce((acc, p) => acc + p.blockedRequests, 0).toLocaleString()}
                </p>
              </div>
              <Bot className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Detection Rate</p>
                <p className="text-2xl font-bold text-blue-600">
                  {(mockPolicies.reduce((acc, p) => acc + p.detectionRate, 0) / mockPolicies.length).toFixed(1)}%
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Falska Positiva</p>
                <p className="text-2xl font-bold text-orange-600">
                  {mockPolicies.reduce((acc, p) => acc + p.falsePositives, 0)}
                </p>
              </div>
              <AlertTriangle className="w-8 h-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="policies">Policyer</TabsTrigger>
          <TabsTrigger value="detection">Detection</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="settings">Inställningar</TabsTrigger>
        </TabsList>

        <TabsContent value="policies" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Filtrera Policyer</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök policyer..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <div className="w-full sm:w-48">
                  <select 
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg bg-background"
                  >
                    <option value="all">Alla Status</option>
                    <option value="active">Aktiva</option>
                    <option value="warning">Varningar</option>
                    <option value="inactive">Inaktiva</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Policies List */}
          <div className="grid grid-cols-1 gap-6">
            {filteredPolicies.map((policy) => (
              <Card key={policy.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-3">
                        {policy.name}
                        <Badge className={getStatusColor(policy.status)}>
                          {policy.status}
                        </Badge>
                      </CardTitle>
                      <CardDescription className="mt-1">
                        Domain: <code className="text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                          {policy.domain}
                        </code>
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline">
                        <Settings className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Eye className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Stats */}
                    <div className="space-y-4">
                      <h4 className="font-medium text-sm text-gray-600 dark:text-gray-400">Prestanda</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Detection Rate</span>
                          <span className="font-bold text-blue-600">{policy.detectionRate}%</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Blockerade</span>
                          <span className="font-bold text-red-600">{policy.blockedRequests.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm">Falska Positiva</span>
                          <span className="font-bold text-orange-600">{policy.falsePositives}</span>
                        </div>
                      </div>
                    </div>

                    {/* Rules */}
                    <div className="lg:col-span-2">
                      <h4 className="font-medium text-sm text-gray-600 dark:text-gray-400 mb-4">Aktiva Regler</h4>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {policy.rules.map((rule, index) => (
                          <div
                            key={index}
                            className={`p-3 rounded-lg border ${
                              rule.enabled
                                ? "border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950"
                                : "border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900"
                            }`}
                          >
                            <div className="flex items-center gap-2 mb-1">
                              {getRuleTypeIcon(rule.type)}
                              <span className="font-medium text-sm">{rule.type}</span>
                              <Badge 
                                variant={rule.enabled ? "default" : "secondary"}
                                className="text-xs"
                              >
                                {rule.enabled ? "ON" : "OFF"}
                              </Badge>
                            </div>
                            <p className="text-xs text-gray-600 dark:text-gray-400">{rule.value}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t text-xs text-gray-600 dark:text-gray-400">
                    Senast uppdaterad: {policy.lastUpdated}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="detection" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                Real-time Detection
              </CardTitle>
              <CardDescription>
                Live övervakning av bot-aktivitet och detection
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">Real-time detection dashboard kommer här</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Detection Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-48 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Trend-diagram kommer här</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Top Threats
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-950 rounded-lg">
                    <span className="text-sm font-medium">Scrapy Bot</span>
                    <Badge variant="destructive">1,247 blocked</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-950 rounded-lg">
                    <span className="text-sm font-medium">Selenium Grid</span>
                    <Badge className="bg-orange-100 text-orange-800">892 blocked</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                    <span className="text-sm font-medium">Curl/Wget</span>
                    <Badge className="bg-yellow-100 text-yellow-800">456 blocked</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Globala Inställningar
              </CardTitle>
              <CardDescription>
                Konfigurera globala anti-bot inställningar
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Default Detection Level</label>
                  <select className="w-full px-3 py-2 border rounded-lg bg-background">
                    <option value="low">Låg (Mindre false positives)</option>
                    <option value="medium">Medium (Balanserad)</option>
                    <option value="high">Hög (Maximal skydd)</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Log Retention (dagar)</label>
                  <Input defaultValue="30" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Challenge Timeout (sekunder)</label>
                  <Input defaultValue="30" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Max Challenge Attempts</label>
                  <Input defaultValue="3" />
                </div>
              </div>
              <div className="pt-4">
                <Button>Spara Inställningar</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    </Layout>
  );
}
