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
  Filter,
  BarChart3,
  PieChart,
  TrendingUp,
  TrendingDown,
  Eye,
  Download,
  RefreshCw,
  Calendar,
  Clock,
  Activity,
  Target,
  Zap,
  Database,
  Users,
  Globe,
  Star,
  AlertCircle,
  CheckCircle,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Plus
} from "lucide-react";
import { useState } from "react";

// Mock analytics data
const analyticsOverview = {
  totalSessions: 24672,
  sessionsGrowth: +12.4,
  avgSessionDuration: "4m 23s",
  durationChange: +8.7,
  bounceRate: 23.8,
  bounceChange: -4.2,
  conversionRate: 3.8,
  conversionChange: +15.3,
  totalPageviews: 89456,
  uniqueVisitors: 18934
};

const trafficSources = [
  { source: "Organic Search", visitors: 12847, percentage: 42.3, change: +5.8, color: "bg-green-500" },
  { source: "Direct", visitors: 8934, percentage: 29.4, change: +2.1, color: "bg-blue-500" },
  { source: "Social Media", visitors: 4672, percentage: 15.4, change: +18.7, color: "bg-purple-500" },
  { source: "Referral", visitors: 2843, percentage: 9.4, change: -3.4, color: "bg-orange-500" },
  { source: "Email", visitors: 1126, percentage: 3.7, change: +7.2, color: "bg-pink-500" }
];

const topPages = [
  { path: "/", title: "Startsida", views: 15847, uniqueViews: 12934, avgTime: "3m 45s", bounceRate: 18.3 },
  { path: "/data/properties", title: "Fastighetsdatabas", views: 12456, uniqueViews: 9823, avgTime: "6m 12s", bounceRate: 15.7 },
  { path: "/data/vehicles", title: "Fordonsdatabas", views: 8934, uniqueViews: 7234, avgTime: "4m 28s", bounceRate: 22.1 },
  { path: "/analytics", title: "Analytics", views: 6782, uniqueViews: 5489, avgTime: "8m 15s", bounceRate: 12.4 },
  { path: "/exports", title: "Dataexport", views: 4567, uniqueViews: 3892, avgTime: "2m 56s", bounceRate: 35.8 }
];

const userSegments = [
  { 
    name: "Power Users", 
    users: 2847, 
    percentage: 15.0, 
    avgSessions: 8.4, 
    conversionRate: 12.7,
    description: "Återkommande användare med hög aktivitet"
  },
  { 
    name: "Regular Users", 
    users: 8934, 
    percentage: 47.2, 
    avgSessions: 3.2, 
    conversionRate: 4.8,
    description: "Måttligt aktiva användare"
  },
  { 
    name: "New Users", 
    users: 5672, 
    percentage: 29.9, 
    avgSessions: 1.8, 
    conversionRate: 1.2,
    description: "Första besöket senaste månaden"
  },
  { 
    name: "At-Risk Users", 
    users: 1481, 
    percentage: 7.8, 
    avgSessions: 0.4, 
    conversionRate: 0.3,
    description: "Låg aktivitet, risk för churn"
  }
];

const conversionFunnels = [
  { step: "Landningssida", users: 18934, percentage: 100, dropRate: 0 },
  { step: "Registrering", users: 12847, percentage: 67.8, dropRate: -32.2 },
  { step: "Första sökning", users: 9823, percentage: 51.9, dropRate: -23.5 },
  { step: "Dataexport", users: 4567, percentage: 24.1, dropRate: -53.5 },
  { step: "Prenumeration", users: 726, percentage: 3.8, dropRate: -84.1 }
];

const realTimeMetrics = {
  activeUsers: 247,
  activeUsersTrend: +12,
  currentPageviews: 89,
  avgLoadTime: "1.2s",
  errorRate: 0.3,
  serverStatus: "healthy"
};

const devices = [
  { type: "Desktop", users: 11246, percentage: 59.4, change: +2.3 },
  { type: "Mobile", users: 6789, percentage: 35.8, change: +8.7 },
  { type: "Tablet", users: 899, percentage: 4.8, change: -1.2 }
];

const getTrendIcon = (change: number) => {
  return change > 0 ? TrendingUp : TrendingDown;
};

const getTrendColor = (change: number) => {
  return change > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400";
};

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [dateRange, setDateRange] = useState("30d");
  const [selectedMetric, setSelectedMetric] = useState("sessions");

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
          <p className="text-gray-600 dark:text-gray-400">Detaljerad användaranalys och prestanda</p>
        </div>
        <div className="flex gap-2">
          <select 
            className="px-3 py-2 border rounded-lg bg-background text-sm"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="1d">Senaste dagen</option>
            <option value="7d">Senaste 7 dagarna</option>
            <option value="30d">Senaste 30 dagarna</option>
            <option value="90d">Senaste 90 dagarna</option>
            <option value="1y">Senaste året</option>
          </select>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportera
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Uppdatera
          </Button>
        </div>
      </div>

      {/* Real-time Status */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium">Live: {realTimeMetrics.activeUsers} aktiva användare</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <span>Sidvisningar: {realTimeMetrics.currentPageviews}</span>
              <span>Laddningstid: {realTimeMetrics.avgLoadTime}</span>
              <span>Felfrekvens: {realTimeMetrics.errorRate}%</span>
              <Badge variant="outline" className="text-green-600">
                {realTimeMetrics.serverStatus}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Sessioner</p>
                <p className="text-2xl font-bold">{analyticsOverview.totalSessions.toLocaleString()}</p>
                <div className={`flex items-center gap-1 text-sm ${getTrendColor(analyticsOverview.sessionsGrowth)}`}>
                  {getTrendIcon(analyticsOverview.sessionsGrowth)({ className: "h-3 w-3" })}
                  <span>{analyticsOverview.sessionsGrowth > 0 ? '+' : ''}{analyticsOverview.sessionsGrowth}%</span>
                </div>
              </div>
              <Activity className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Sessionstid</p>
                <p className="text-2xl font-bold">{analyticsOverview.avgSessionDuration}</p>
                <div className={`flex items-center gap-1 text-sm ${getTrendColor(analyticsOverview.durationChange)}`}>
                  {getTrendIcon(analyticsOverview.durationChange)({ className: "h-3 w-3" })}
                  <span>{analyticsOverview.durationChange > 0 ? '+' : ''}{analyticsOverview.durationChange}%</span>
                </div>
              </div>
              <Clock className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Studsfrekvens</p>
                <p className="text-2xl font-bold">{analyticsOverview.bounceRate}%</p>
                <div className={`flex items-center gap-1 text-sm ${getTrendColor(-analyticsOverview.bounceChange)}`}>
                  {getTrendIcon(-analyticsOverview.bounceChange)({ className: "h-3 w-3" })}
                  <span>{analyticsOverview.bounceChange > 0 ? '' : '+'}{-analyticsOverview.bounceChange}%</span>
                </div>
              </div>
              <Target className="h-8 w-8 text-yellow-600 dark:text-yellow-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Konvertering</p>
                <p className="text-2xl font-bold">{analyticsOverview.conversionRate}%</p>
                <div className={`flex items-center gap-1 text-sm ${getTrendColor(analyticsOverview.conversionChange)}`}>
                  {getTrendIcon(analyticsOverview.conversionChange)({ className: "h-3 w-3" })}
                  <span>{analyticsOverview.conversionChange > 0 ? '+' : ''}{analyticsOverview.conversionChange}%</span>
                </div>
              </div>
              <Zap className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Översikt</TabsTrigger>
          <TabsTrigger value="traffic">Trafik</TabsTrigger>
          <TabsTrigger value="users">Användare</TabsTrigger>
          <TabsTrigger value="behavior">Beteende</TabsTrigger>
          <TabsTrigger value="conversions">Konvertering</TabsTrigger>
          <TabsTrigger value="realtime">Realtid</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Trafiköversikt</CardTitle>
                <CardDescription>Sidvisningar över tid</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📈 Trafikdiagram: {analyticsOverview.totalPageviews.toLocaleString()} sidvisningar
                </div>
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mt-4">
                  <span>Totalt: {analyticsOverview.totalPageviews.toLocaleString()}</span>
                  <span>Unika: {analyticsOverview.uniqueVisitors.toLocaleString()}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Toppkällor</CardTitle>
                <CardDescription>Trafik per källa</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {trafficSources.slice(0, 4).map((source, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-3 h-3 rounded ${source.color}`}></div>
                        <span className="font-medium">{source.source}</span>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{source.visitors.toLocaleString()}</p>
                        <p className={`text-xs ${getTrendColor(source.change)}`}>
                          {source.change > 0 ? '+' : ''}{source.change}%
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Populära sidor</CardTitle>
                <CardDescription>Mest besökta sidor</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {topPages.slice(0, 5).map((page, index) => (
                    <div key={index} className="flex items-center justify-between p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg">
                      <div>
                        <p className="font-medium text-sm">{page.title}</p>
                        <p className="text-xs text-gray-500">{page.path}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-semibold">{page.views.toLocaleString()}</p>
                        <p className="text-xs text-gray-500">{page.bounceRate}% studs</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Enhetsfördelning</CardTitle>
                <CardDescription>Användare per enhetstyp</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {devices.map((device, index) => (
                    <div key={index} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="font-medium">{device.type}</span>
                        <div className="text-right">
                          <span className="font-semibold">{device.percentage}%</span>
                          <span className={`text-xs ml-2 ${getTrendColor(device.change)}`}>
                            ({device.change > 0 ? '+' : ''}{device.change}%)
                          </span>
                        </div>
                      </div>
                      <Progress value={device.percentage} className="h-2" />
                      <p className="text-xs text-gray-500">{device.users.toLocaleString()} användare</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Traffic Tab */}
        <TabsContent value="traffic" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Trafikkällor</CardTitle>
                  <CardDescription>Detaljerad uppdelning av trafikdata</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {trafficSources.map((source, index) => (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            <div className={`w-4 h-4 rounded ${source.color}`}></div>
                            <h3 className="font-semibold">{source.source}</h3>
                          </div>
                          <Badge variant="outline">{source.percentage}%</Badge>
                        </div>
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">Besökare</p>
                            <p className="font-semibold text-lg">{source.visitors.toLocaleString()}</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Andel</p>
                            <p className="font-semibold text-lg">{source.percentage}%</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Förändring</p>
                            <div className={`flex items-center gap-1 ${getTrendColor(source.change)}`}>
                              {getTrendIcon(source.change)({ className: "h-4 w-4" })}
                              <span className="font-semibold">{source.change > 0 ? '+' : ''}{source.change}%</span>
                            </div>
                          </div>
                        </div>
                        <Progress value={source.percentage} className="mt-3" />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Geografisk fördelning</CardTitle>
                <CardDescription>Toppländer</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>🇸🇪 Sverige</span>
                    <span className="font-medium">68.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🇳🇴 Norge</span>
                    <span className="font-medium">12.3%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🇩🇰 Danmark</span>
                    <span className="font-medium">8.7%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🇫🇮 Finland</span>
                    <span className="font-medium">6.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>🇩🇪 Tyskland</span>
                    <span className="font-medium">4.4%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Användarsegment</CardTitle>
                <CardDescription>Uppdelning baserat på användarbeteende</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {userSegments.map((segment, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">{segment.name}</h3>
                        <Badge variant="outline">{segment.percentage}%</Badge>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{segment.description}</p>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Användare</p>
                          <p className="font-semibold">{segment.users.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Sessioner</p>
                          <p className="font-semibold">{segment.avgSessions}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Konvertering</p>
                          <p className="font-semibold">{segment.conversionRate}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Användarflöde</CardTitle>
                <CardDescription>Hur användare navigerar på plattformen</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  🌊 Flödesdiagram: Startsida → Sök → Resultat → Export
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Behavior Tab */}
        <TabsContent value="behavior" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Siddynamik</CardTitle>
                <CardDescription>Detaljerad sidanalys</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {topPages.map((page, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <h4 className="font-medium">{page.title}</h4>
                          <p className="text-sm text-gray-500">{page.path}</p>
                        </div>
                        <Button variant="outline" size="sm">
                          <Eye className="h-4 w-4 mr-1" />
                          Detaljer
                        </Button>
                      </div>
                      <div className="grid grid-cols-4 gap-4 text-sm">
                        <div>
                          <p className="text-gray-500">Sidvisningar</p>
                          <p className="font-semibold">{page.views.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Unika</p>
                          <p className="font-semibold">{page.uniqueViews.toLocaleString()}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Tid på sida</p>
                          <p className="font-semibold">{page.avgTime}</p>
                        </div>
                        <div>
                          <p className="text-gray-500">Studsfrekvens</p>
                          <p className="font-semibold">{page.bounceRate}%</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Interaktionsheatmap</CardTitle>
                <CardDescription>Populära sektioner och klick</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  🔥 Heatmap: Navigation (89%), Sökfält (76%), Export (34%)
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Conversions Tab */}
        <TabsContent value="conversions" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Konverteringsstratt</CardTitle>
              <CardDescription>Användarens väg från besök till konvertering</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {conversionFunnels.map((step, index) => (
                  <div key={index} className="relative">
                    <div className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                          {index + 1}
                        </div>
                        <div>
                          <h3 className="font-medium">{step.step}</h3>
                          {index > 0 && (
                            <p className="text-sm text-red-600 dark:text-red-400">
                              {step.dropRate}% drop-off
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold">{step.users.toLocaleString()}</p>
                        <p className="text-sm text-gray-500">{step.percentage}%</p>
                      </div>
                    </div>
                    <div className="mt-2 h-2 bg-gray-200 dark:bg-gray-700 rounded">
                      <div 
                        className="h-2 bg-blue-600 rounded" 
                        style={{ width: `${step.percentage}%` }}
                      ></div>
                    </div>
                    {index < conversionFunnels.length - 1 && (
                      <div className="flex justify-center mt-2">
                        <div className="w-0 h-0 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-400"></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Real-time Tab */}
        <TabsContent value="realtime" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6 text-center">
                <Users className="h-8 w-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {realTimeMetrics.activeUsers}
                </p>
                <p className="text-sm text-gray-500">Aktiva användare</p>
                <div className="flex items-center justify-center gap-1 mt-1">
                  <TrendingUp className="h-3 w-3 text-green-600" />
                  <span className="text-xs text-green-600">+{realTimeMetrics.activeUsersTrend}</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <Eye className="h-8 w-8 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
                <p className="text-2xl font-bold">{realTimeMetrics.currentPageviews}</p>
                <p className="text-sm text-gray-500">Sidvisningar/min</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <Zap className="h-8 w-8 text-yellow-600 dark:text-yellow-400 mx-auto mb-2" />
                <p className="text-2xl font-bold">{realTimeMetrics.avgLoadTime}</p>
                <p className="text-sm text-gray-500">Laddningstid</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6 text-center">
                <AlertCircle className="h-8 w-8 text-green-600 dark:text-green-400 mx-auto mb-2" />
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {realTimeMetrics.errorRate}%
                </p>
                <p className="text-sm text-gray-500">Felfrekvens</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Aktivitet i realtid</CardTitle>
                <CardDescription>Senaste 30 minuterna</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-48 flex items-center justify-center text-gray-500">
                  📊 Live aktivitetsdiagram
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Aktiva sidor</CardTitle>
                <CardDescription>Mest besökta just nu</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span>/</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="font-medium">47</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>/data/properties</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="font-medium">32</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>/analytics</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="font-medium">18</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span>/exports</span>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="font-medium">12</span>
                    </div>
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
