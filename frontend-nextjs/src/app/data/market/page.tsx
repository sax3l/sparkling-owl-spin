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
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  Eye,
  Download,
  RefreshCw,
  Calendar,
  MapPin,
  Target,
  Briefcase,
  DollarSign,
  Users,
  Building,
  Globe,
  Star,
  AlertTriangle,
  CheckCircle,
  Clock
} from "lucide-react";
import { useState } from "react";

// Mock market intelligence data
const marketOverview = {
  totalMarkets: 47,
  activeAnalyses: 23,
  completedReports: 156,
  trendScore: 87.3,
  competitiveIndex: 92.1,
  marketGrowth: 4.7
};

const marketSegments = [
  {
    id: "real_estate",
    name: "Fastigheter",
    icon: "🏠",
    totalListings: 42847,
    avgPrice: 4250000,
    priceChange: +3.2,
    marketShare: 34.2,
    activity: "Hög",
    trend: "up",
    reports: 12,
    lastUpdated: "2024-01-15 14:30:00"
  },
  {
    id: "vehicles",
    name: "Fordon", 
    icon: "🚗",
    totalListings: 28394,
    avgPrice: 285000,
    priceChange: +1.8,
    marketShare: 23.1,
    activity: "Medel",
    trend: "up",
    reports: 8,
    lastUpdated: "2024-01-15 14:25:00"
  },
  {
    id: "jobs",
    name: "Jobb",
    icon: "💼",
    totalListings: 67234,
    avgPrice: 45000,
    priceChange: +2.1,
    marketShare: 28.4,
    activity: "Hög",
    trend: "up", 
    reports: 15,
    lastUpdated: "2024-01-15 14:20:00"
  },
  {
    id: "retail",
    name: "Detaljhandel",
    icon: "🛍️",
    totalListings: 15674,
    avgPrice: 1250,
    priceChange: -0.8,
    marketShare: 14.3,
    activity: "Låg",
    trend: "down",
    reports: 6,
    lastUpdated: "2024-01-15 14:15:00"
  }
];

const competitorAnalysis = [
  {
    id: "comp_001",
    name: "MarketLeader AB",
    segment: "Fastigheter",
    marketShare: 23.4,
    shareChange: +1.2,
    strengths: ["Stark varumärke", "Bred täckning", "God kundeservice"],
    weaknesses: ["Höga priser", "Långsam innovation"],
    threatLevel: "Hög",
    status: "active"
  },
  {
    id: "comp_002", 
    name: "CompetitorCorp",
    segment: "Fordon",
    marketShare: 18.7,
    shareChange: -0.5,
    strengths: ["Teknisk innovation", "Låga priser"],
    weaknesses: ["Begränsad närvaro", "Kvalitetsproblem"],
    threatLevel: "Medel",
    status: "monitoring"
  },
  {
    id: "comp_003",
    name: "RivalInc",
    segment: "Jobb",
    marketShare: 15.2,
    shareChange: +2.8,
    strengths: ["Snabb tillväxt", "AI-teknik", "Mobil-first"],
    weaknesses: ["Ny aktör", "Begränsade resurser"],
    threatLevel: "Hög",
    status: "active"
  }
];

const marketTrends = [
  {
    id: "trend_001",
    title: "Ökad digitalisering av fastighetsmarknaden",
    category: "Technology",
    impact: "Hög",
    probability: 85,
    timeframe: "6 månader",
    description: "Virtual reality visningar och AI-drivna värderingar blir standard",
    sources: 12,
    confidence: 92
  },
  {
    id: "trend_002",
    title: "Elektrifiering av fordonssektorn accelererar",
    category: "Environmental",
    impact: "Hög", 
    probability: 92,
    timeframe: "12 månader",
    description: "EV-marknaden förväntas växa med 200% under nästa år",
    sources: 18,
    confidence: 88
  },
  {
    id: "trend_003",
    title: "Remote work förändrar jobbmarknaden",
    category: "Social",
    impact: "Medel",
    probability: 78,
    timeframe: "3 månader", 
    description: "Distansarbete blir permanent för 60% av kunskapsarbetare",
    sources: 24,
    confidence: 76
  }
];

const getTrendIcon = (trend: string) => {
  return trend === "up" ? TrendingUp : TrendingDown;
};

const getTrendColor = (trend: string) => {
  return trend === "up" ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400";
};

const getActivityColor = (activity: string) => {
  switch (activity) {
    case "Hög": return "text-green-600 dark:text-green-400";
    case "Medel": return "text-yellow-600 dark:text-yellow-400";
    case "Låg": return "text-red-600 dark:text-red-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getThreatColor = (level: string) => {
  switch (level) {
    case "Hög": return "text-red-600 dark:text-red-400";
    case "Medel": return "text-yellow-600 dark:text-yellow-400";
    case "Låg": return "text-green-600 dark:text-green-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const formatPrice = (price: number, segment: string) => {
  if (segment === "Fastigheter") {
    return new Intl.NumberFormat('sv-SE', {
      style: 'currency',
      currency: 'SEK',
      minimumFractionDigits: 0
    }).format(price);
  } else if (segment === "Jobb") {
    return new Intl.NumberFormat('sv-SE', {
      style: 'currency',
      currency: 'SEK',
      minimumFractionDigits: 0
    }).format(price) + "/mån";
  } else {
    return new Intl.NumberFormat('sv-SE', {
      style: 'currency',
      currency: 'SEK',
      minimumFractionDigits: 0
    }).format(price);
  }
};

export default function MarketIntelligencePage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedSegment, setSelectedSegment] = useState("all");

  const filteredSegments = marketSegments.filter(segment => {
    const matchesSearch = segment.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSegment = selectedSegment === "all" || segment.id === selectedSegment;
    return matchesSearch && matchesSegment;
  });

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Market Intelligence</h1>
          <p className="text-gray-600 dark:text-gray-400">Marknadsanalys och konkurrensinformation</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportera rapport
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Uppdatera data
          </Button>
          <Button size="sm">
            <Target className="h-4 w-4 mr-2" />
            Ny analys
          </Button>
        </div>
      </div>

      {/* Market Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <Globe className="h-6 w-6 text-blue-600 dark:text-blue-400 mx-auto mb-2" />
              <p className="text-2xl font-bold">{marketOverview.totalMarkets}</p>
              <p className="text-xs text-gray-500">Marknader</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <BarChart3 className="h-6 w-6 text-green-600 dark:text-green-400 mx-auto mb-2" />
              <p className="text-2xl font-bold">{marketOverview.activeAnalyses}</p>
              <p className="text-xs text-gray-500">Aktiva analyser</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <CheckCircle className="h-6 w-6 text-purple-600 dark:text-purple-400 mx-auto mb-2" />
              <p className="text-2xl font-bold">{marketOverview.completedReports}</p>
              <p className="text-xs text-gray-500">Rapporter</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{marketOverview.trendScore}%</p>
              <p className="text-xs text-gray-500">Trend Score</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <Target className="h-6 w-6 text-orange-600 dark:text-orange-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">{marketOverview.competitiveIndex}%</p>
              <p className="text-xs text-gray-500">Konkurrensindex</p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <TrendingUp className="h-6 w-6 text-green-600 dark:text-green-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">+{marketOverview.marketGrowth}%</p>
              <p className="text-xs text-gray-500">Tillväxt</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Översikt</TabsTrigger>
          <TabsTrigger value="segments">Segment ({filteredSegments.length})</TabsTrigger>
          <TabsTrigger value="competitors">Konkurrenter</TabsTrigger>
          <TabsTrigger value="trends">Trender</TabsTrigger>
          <TabsTrigger value="reports">Rapporter</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Marknadssegment</CardTitle>
                <CardDescription>Prestanda per segment idag</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {marketSegments.slice(0, 4).map((segment) => {
                    const TrendIcon = getTrendIcon(segment.trend);
                    return (
                      <div key={segment.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-3">
                          <span className="text-xl">{segment.icon}</span>
                          <div>
                            <p className="font-medium">{segment.name}</p>
                            <p className="text-sm text-gray-500">{segment.totalListings.toLocaleString()} annonser</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`flex items-center gap-1 ${getTrendColor(segment.trend)}`}>
                            <TrendIcon className="h-4 w-4" />
                            <span className="font-medium">{segment.priceChange > 0 ? '+' : ''}{segment.priceChange}%</span>
                          </div>
                          <p className="text-sm text-gray-500">{segment.marketShare}% marknadsandel</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Toppkonkurrenter</CardTitle>
                <CardDescription>Högst hotbetyg denna vecka</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {competitorAnalysis.slice(0, 3).map((competitor) => (
                    <div key={competitor.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div>
                        <p className="font-medium">{competitor.name}</p>
                        <p className="text-sm text-gray-500">{competitor.segment}</p>
                      </div>
                      <div className="text-right">
                        <Badge className={`${getThreatColor(competitor.threatLevel)}`}>
                          {competitor.threatLevel}
                        </Badge>
                        <p className="text-sm text-gray-500 mt-1">{competitor.marketShare}%</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Aktuella trender</CardTitle>
                <CardDescription>Högst sannolikhet att påverka marknaden</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {marketTrends.slice(0, 3).map((trend) => (
                    <div key={trend.id} className="p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-sm">{trend.title}</h4>
                        <Badge variant="outline">{trend.impact}</Badge>
                      </div>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>Sannolikhet: {trend.probability}%</span>
                        <span>{trend.timeframe}</span>
                      </div>
                      <Progress value={trend.probability} className="h-1 mt-2" />
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Marknadsaktivitet</CardTitle>
                <CardDescription>Aktivitetsnivå per segment</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📊 Aktivitetsdiagram: Genomsnittlig aktivitet {marketOverview.trendScore}%
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Segments Tab */}
        <TabsContent value="segments" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök marknadssegment..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedSegment}
                    onChange={(e) => setSelectedSegment(e.target.value)}
                  >
                    <option value="all">Alla segment</option>
                    {marketSegments.map(segment => (
                      <option key={segment.id} value={segment.id}>{segment.name}</option>
                    ))}
                  </select>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Avancerat filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Segment List */}
          <div className="space-y-4">
            {filteredSegments.map((segment) => {
              const TrendIcon = getTrendIcon(segment.trend);
              return (
                <Card key={segment.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row gap-6">
                      {/* Main Info */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-3">
                            <span className="text-2xl">{segment.icon}</span>
                            <div>
                              <h3 className="text-xl font-bold">{segment.name}</h3>
                              <p className="text-sm text-gray-500">
                                {segment.totalListings.toLocaleString()} annonser
                              </p>
                            </div>
                          </div>
                          <Badge className={`${getActivityColor(segment.activity)}`}>
                            {segment.activity} aktivitet
                          </Badge>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Medelpris</p>
                            <p className="font-semibold">{formatPrice(segment.avgPrice, segment.name)}</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Prisförändring</p>
                            <div className={`flex items-center gap-1 ${getTrendColor(segment.trend)}`}>
                              <TrendIcon className="h-4 w-4" />
                              <span className="font-semibold">
                                {segment.priceChange > 0 ? '+' : ''}{segment.priceChange}%
                              </span>
                            </div>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Marknadsandel</p>
                            <p className="font-semibold">{segment.marketShare}%</p>
                          </div>
                          <div>
                            <p className="text-sm text-gray-500 dark:text-gray-400">Rapporter</p>
                            <p className="font-semibold">{segment.reports} st</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                          <span className="flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            Uppdaterad: {segment.lastUpdated}
                          </span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex flex-row lg:flex-col gap-2 lg:w-32">
                        <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                          <Eye className="h-4 w-4 mr-2" />
                          Visa detaljer
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                          <BarChart3 className="h-4 w-4 mr-2" />
                          Analys
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                          <Download className="h-4 w-4 mr-2" />
                          Rapport
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        {/* Competitors Tab */}
        <TabsContent value="competitors" className="space-y-4">
          <div className="space-y-4">
            {competitorAnalysis.map((competitor) => (
              <Card key={competitor.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row gap-6">
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-bold">{competitor.name}</h3>
                          <p className="text-gray-600 dark:text-gray-400">{competitor.segment}</p>
                        </div>
                        <div className="text-right">
                          <Badge className={`${getThreatColor(competitor.threatLevel)}`}>
                            Hotbetyg: {competitor.threatLevel}
                          </Badge>
                          <p className="text-sm text-gray-500 mt-1">
                            {competitor.status === "active" ? "Aktiv övervakning" : "Passiv övervakning"}
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-4">
                        <div>
                          <h4 className="font-medium text-green-600 dark:text-green-400 mb-2">Styrkor</h4>
                          <ul className="space-y-1">
                            {competitor.strengths.map((strength, index) => (
                              <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                                <CheckCircle className="h-3 w-3 text-green-600" />
                                {strength}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="font-medium text-red-600 dark:text-red-400 mb-2">Svagheter</h4>
                          <ul className="space-y-1">
                            {competitor.weaknesses.map((weakness, index) => (
                              <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                                <AlertTriangle className="h-3 w-3 text-red-600" />
                                {weakness}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>

                      <div className="flex items-center gap-4 text-sm">
                        <span>Marknadsandel: <strong>{competitor.marketShare}%</strong></span>
                        <span className={competitor.shareChange > 0 ? "text-red-600" : "text-green-600"}>
                          Förändring: {competitor.shareChange > 0 ? '+' : ''}{competitor.shareChange}%
                        </span>
                      </div>
                    </div>

                    <div className="flex flex-row lg:flex-col gap-2 lg:w-32">
                      <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                        <Eye className="h-4 w-4 mr-2" />
                        Visa profil
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                        <BarChart3 className="h-4 w-4 mr-2" />
                        Jämför
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                        <Target className="h-4 w-4 mr-2" />
                        Övervaka
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          <div className="space-y-4">
            {marketTrends.map((trend) => (
              <Card key={trend.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row gap-6">
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-xl font-bold">{trend.title}</h3>
                          <p className="text-gray-600 dark:text-gray-400 mt-2">{trend.description}</p>
                        </div>
                        <Badge variant="outline">{trend.category}</Badge>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Sannolikhet</p>
                          <div className="flex items-center gap-2">
                            <p className="font-semibold text-lg">{trend.probability}%</p>
                            <Progress value={trend.probability} className="flex-1 h-2" />
                          </div>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Påverkan</p>
                          <Badge className={trend.impact === "Hög" ? "text-red-600" : "text-yellow-600"}>
                            {trend.impact}
                          </Badge>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Tidsram</p>
                          <p className="font-semibold">{trend.timeframe}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500 dark:text-gray-400">Förtroende</p>
                          <p className="font-semibold text-blue-600 dark:text-blue-400">{trend.confidence}%</p>
                        </div>
                      </div>

                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        Baserat på {trend.sources} källor
                      </div>
                    </div>

                    <div className="flex flex-row lg:flex-col gap-2 lg:w-32">
                      <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                        <Eye className="h-4 w-4 mr-2" />
                        Detaljer
                      </Button>
                      <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                        <Download className="h-4 w-4 mr-2" />
                        Rapport
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Marknadsrapporter</CardTitle>
              <CardDescription>Genererade analyser och rapporter</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Inga rapporter tillgängliga</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Skapa din första marknadsanalysrapport för att komma igång
                </p>
                <Button>
                  <Target className="h-4 w-4 mr-2" />
                  Skapa rapport
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
