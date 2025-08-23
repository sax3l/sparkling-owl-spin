"use client";

import Layout from "@/components/Layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { 
  Shield,
  Activity,
  AlertCircle,
  CheckCircle,
  Clock,
  Globe,
  Zap,
  Plus,
  Search,
  Settings,
  BarChart3,
  RefreshCw
} from "lucide-react";

// Mock proxy data
const mockProxies = [
  {
    id: "1",
    name: "US-East-001",
    ip: "192.168.1.100",
    port: 8080,
    location: "Virginia, USA",
    status: "active",
    responseTime: 125,
    uptime: 99.8,
    successRate: 98.5,
    lastChecked: "2024-01-15 14:30:00",
    provider: "ProxyProvider A",
    type: "HTTP"
  },
  {
    id: "2", 
    name: "EU-West-002",
    ip: "10.0.0.50",
    port: 3128,
    location: "Amsterdam, Netherlands",
    status: "warning",
    responseTime: 89,
    uptime: 97.2,
    successRate: 94.1,
    lastChecked: "2024-01-15 14:29:45",
    provider: "ProxyProvider B",
    type: "HTTPS"
  },
  {
    id: "3",
    name: "AS-South-003", 
    ip: "172.16.0.25",
    port: 8888,
    location: "Singapore",
    status: "error",
    responseTime: 0,
    uptime: 45.3,
    successRate: 67.8,
    lastChecked: "2024-01-15 14:15:20",
    provider: "ProxyProvider C",
    type: "SOCKS5"
  }
];

const getStatusColor = (status: string) => {
  switch(status) {
    case "active": return "text-green-600 bg-green-100 dark:bg-green-900";
    case "warning": return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900";
    case "error": return "text-red-600 bg-red-100 dark:bg-red-900";
    default: return "text-gray-600 bg-gray-100 dark:bg-gray-900";
  }
};

const getStatusIcon = (status: string) => {
  switch(status) {
    case "active": return <CheckCircle className="w-4 h-4" />;
    case "warning": return <AlertCircle className="w-4 h-4" />;
    case "error": return <AlertCircle className="w-4 h-4" />;
    default: return <Clock className="w-4 h-4" />;
  }
};

export default function ProxiesPage() {
  const [activeTab, setActiveTab] = useState("health");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");

  const filteredProxies = mockProxies.filter(proxy => {
    const matchesSearch = proxy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proxy.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         proxy.provider.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || proxy.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Proxy-hälsa</h1>
          <p className="text-gray-600 dark:text-gray-400">Övervaka och hantera proxy-servrar och deras prestanda</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Uppdatera Status
          </Button>
          <Button size="sm">
            <Plus className="w-4 h-4 mr-2" />
            Lägg till Proxy
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Aktiva Proxies</p>
                <p className="text-2xl font-bold text-green-600">
                  {mockProxies.filter(p => p.status === 'active').length}
                </p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Varningar</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {mockProxies.filter(p => p.status === 'warning').length}
                </p>
              </div>
              <AlertCircle className="w-8 h-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Fel</p>
                <p className="text-2xl font-bold text-red-600">
                  {mockProxies.filter(p => p.status === 'error').length}
                </p>
              </div>
              <AlertCircle className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Genomsnittlig Respons</p>
                <p className="text-2xl font-bold text-blue-600">
                  {Math.round(mockProxies.reduce((acc, p) => acc + p.responseTime, 0) / mockProxies.length)}ms
                </p>
              </div>
              <Zap className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="health">Hälsostatus</TabsTrigger>
          <TabsTrigger value="performance">Prestanda</TabsTrigger>
          <TabsTrigger value="config">Konfiguration</TabsTrigger>
          <TabsTrigger value="logs">Loggar</TabsTrigger>
        </TabsList>

        <TabsContent value="health" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Filtrera Proxies</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök proxies..."
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
                    <option value="all">All Status</option>
                    <option value="active">Aktiva</option>
                    <option value="warning">Varningar</option>
                    <option value="error">Fel</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Proxy List */}
          <div className="grid grid-cols-1 gap-4">
            {filteredProxies.map((proxy) => (
              <Card key={proxy.id}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <h3 className="font-semibold text-lg">{proxy.name}</h3>
                        <Badge className={getStatusColor(proxy.status)}>
                          {getStatusIcon(proxy.status)}
                          <span className="ml-1 capitalize">{proxy.status}</span>
                        </Badge>
                        <Badge variant="outline">{proxy.type}</Badge>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-600 dark:text-gray-400">Adress</p>
                          <p className="font-mono">{proxy.ip}:{proxy.port}</p>
                        </div>
                        <div>
                          <p className="text-gray-600 dark:text-gray-400">Plats</p>
                          <p className="flex items-center gap-1">
                            <Globe className="w-3 h-3" />
                            {proxy.location}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-600 dark:text-gray-400">Leverantör</p>
                          <p>{proxy.provider}</p>
                        </div>
                        <div>
                          <p className="text-gray-600 dark:text-gray-400">Senast kontrollerad</p>
                          <p className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {proxy.lastChecked}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-blue-600">{proxy.responseTime}ms</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">Responstid</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-green-600">{proxy.uptime}%</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">Drifttid</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-purple-600">{proxy.successRate}%</p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">Framgång</p>
                        </div>
                      </div>
                    </div>

                    <div className="flex gap-2 ml-4">
                      <Button size="sm" variant="outline">
                        <Settings className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Activity className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Prestandamätningar
              </CardTitle>
              <CardDescription>
                Detaljerad analys av proxy-prestanda över tid
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-center">
                <p className="text-gray-500">Prestandadiagram kommer här</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="config" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Proxy-konfiguration
              </CardTitle>
              <CardDescription>
                Hantera globala proxy-inställningar och konfiguration
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Timeout (ms)</label>
                  <Input defaultValue="30000" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Max Återförsök</label>
                  <Input defaultValue="3" />
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Hälsokontroll Intervall</label>
                  <select className="w-full px-3 py-2 border rounded-lg bg-background">
                    <option value="30">30 sekunder</option>
                    <option value="60">1 minut</option>
                    <option value="300">5 minuter</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Rotation Strategi</label>
                  <select className="w-full px-3 py-2 border rounded-lg bg-background">
                    <option value="round-robin">Round Robin</option>
                    <option value="random">Slumpmässig</option>
                    <option value="performance">Bästa Prestanda</option>
                  </select>
                </div>
              </div>
              <div className="pt-4">
                <Button>Spara Konfiguration</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="logs" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Proxy Loggar
              </CardTitle>
              <CardDescription>
                Senaste händelser och fel från proxy-servrar
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                <div className="flex items-center gap-3 p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                  <CheckCircle className="w-4 h-4 text-green-600" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">US-East-001 online</p>
                    <p className="text-xs text-gray-600">2024-01-15 14:30:00</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                  <AlertCircle className="w-4 h-4 text-yellow-600" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">EU-West-002 hög responstid</p>
                    <p className="text-xs text-gray-600">2024-01-15 14:25:30</p>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-3 bg-red-50 dark:bg-red-950 rounded-lg">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">AS-South-003 connection timeout</p>
                    <p className="text-xs text-gray-600">2024-01-15 14:15:20</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    </Layout>
  );
}
