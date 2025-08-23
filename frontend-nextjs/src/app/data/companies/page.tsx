"use client";

import Layout from "@/components/Layout";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search,
  Filter,
  Building,
  Calendar,
  MapPin,
  Eye,
  Download,
  RefreshCw,
  BarChart3,
  TrendingUp,
  Database,
  Star,
  Settings,
  Plus,
  Edit,
  Trash2,
  Users,
  Globe,
  Phone,
  Mail,
  DollarSign,
  Briefcase,
  Award,
  CheckCircle,
  AlertTriangle,
  Clock
} from "lucide-react";
import { useState } from "react";

// Mock company data
const mockCompanies = [
  {
    id: "comp_001",
    name: "Tech Innovations AB",
    domain: "techinnovations.se",
    industry: "IT & Tech",
    size: "501-1000",
    employees: 750,
    founded: 2008,
    revenue: "150M SEK",
    location: "Stockholm, Sverige",
    headquarters: "Stockholm",
    description: "Ledande inom molnbaserade lösningar och AI-utveckling för svenska företag",
    website: "https://techinnovations.se",
    phone: "+46 8 123 45 67",
    email: "kontakt@techinnovations.se",
    ceo: "Anna Lindberg",
    keyPeople: ["Anna Lindberg (CEO)", "Erik Johansson (CTO)", "Maria Nilsson (CFO)"],
    technologies: ["React", "Node.js", "AWS", "Python", "Kubernetes"],
    certifications: ["ISO 27001", "GDPR Compliant", "SOC 2"],
    socialMedia: {
      linkedin: "company/tech-innovations-ab",
      twitter: "@techinnovations"
    },
    quality: 95,
    crawledAt: "2024-01-15 14:30:00",
    source: "allabolag.se",
    verified: true,
    publiclyTraded: false,
    status: "active"
  },
  {
    id: "comp_002",
    name: "Nordic Consulting Group",
    domain: "nordicconsulting.com",
    industry: "Consulting",
    size: "51-200",
    employees: 125,
    founded: 2015,
    revenue: "45M SEK",
    location: "Göteborg, Sverige",
    headquarters: "Göteborg",
    description: "Managementkonsulting för medelstora och stora företag i Norden",
    website: "https://nordicconsulting.com",
    phone: "+46 31 987 65 43",
    email: "hello@nordicconsulting.com",
    ceo: "Lars Andersson",
    keyPeople: ["Lars Andersson (CEO)", "Sofia Karlsson (COO)"],
    technologies: ["Salesforce", "Microsoft 365", "Power BI"],
    certifications: ["ISO 9001", "GDPR Compliant"],
    socialMedia: {
      linkedin: "company/nordic-consulting-group"
    },
    quality: 88,
    crawledAt: "2024-01-15 14:25:00",
    source: "linkedin.com",
    verified: true,
    publiclyTraded: false,
    status: "active"
  },
  {
    id: "comp_003",
    name: "Green Energy Solutions",
    domain: "greenenergy.se",
    industry: "Energy",
    size: "201-500",
    employees: 320,
    founded: 2012,
    revenue: "89M SEK",
    location: "Malmö, Sverige",
    headquarters: "Malmö",
    description: "Hållbara energilösningar för företag och kommuner",
    website: "https://greenenergy.se",
    phone: "+46 40 555 12 34",
    email: "info@greenenergy.se",
    ceo: "Emma Svensson",
    keyPeople: ["Emma Svensson (CEO)", "Mikael Lindqvist (CTO)", "Anna Petersson (Head of Sales)"],
    technologies: ["IoT", "Solar Tech", "Smart Grid", "Data Analytics"],
    certifications: ["ISO 14001", "B-Corp Certified", "GDPR Compliant"],
    socialMedia: {
      linkedin: "company/green-energy-solutions",
      twitter: "@greenenergyswe"
    },
    quality: 92,
    crawledAt: "2024-01-15 14:20:00",
    source: "allabolag.se",
    verified: true,
    publiclyTraded: true,
    status: "active"
  },
  {
    id: "comp_004",
    name: "Digital Marketing Pro",
    domain: "digitalmarketing.se",
    industry: "Marketing",
    size: "11-50",
    employees: 28,
    founded: 2020,
    revenue: "12M SEK",
    location: "Uppsala, Sverige",
    headquarters: "Uppsala",
    description: "Digital marknadsföring och e-handelslösningar för små och medelstora företag",
    website: "https://digitalmarketing.se",
    phone: "",
    email: "kontakt@digitalmarketing.se",
    ceo: "Johan Nilsson",
    keyPeople: ["Johan Nilsson (CEO)", "Sara Blomqvist (Head of Growth)"],
    technologies: ["Google Ads", "Facebook Ads", "Shopify", "WooCommerce"],
    certifications: ["Google Partner", "Facebook Marketing Partner"],
    socialMedia: {
      linkedin: "company/digital-marketing-pro",
      instagram: "@digitalmarketingpro"
    },
    quality: 76,
    crawledAt: "2024-01-15 14:15:00",
    source: "ratsit.se",
    verified: false,
    publiclyTraded: false,
    status: "needs_review"
  }
];

const companyStats = {
  total: 18934,
  newToday: 67,
  activeCompanies: 16247,
  avgEmployees: 234,
  avgRevenue: "67M SEK",
  revenueGrowth: +12.4,
  sources: 12,
  qualityAvg: 89.1,
  verified: 14256
};

const industryStats = [
  { industry: "IT & Tech", count: 4567, percentage: 24.1, avgRevenue: "89M SEK" },
  { industry: "Finance", count: 3421, percentage: 18.1, avgRevenue: "156M SEK" },
  { industry: "Healthcare", count: 2890, percentage: 15.3, avgRevenue: "78M SEK" },
  { industry: "Manufacturing", count: 2456, percentage: 13.0, avgRevenue: "203M SEK" },
  { industry: "Retail", count: 2234, percentage: 11.8, avgRevenue: "45M SEK" },
  { industry: "Consulting", count: 1876, percentage: 9.9, avgRevenue: "34M SEK" },
  { industry: "Energy", count: 1490, percentage: 7.9, avgRevenue: "112M SEK" }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return "text-green-600 dark:text-green-400";
    case "inactive": return "text-gray-600 dark:text-gray-400";
    case "needs_review": return "text-yellow-600 dark:text-yellow-400";
    case "pending": return "text-blue-600 dark:text-blue-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "active": return CheckCircle;
    case "needs_review": return AlertTriangle;
    case "pending": return Clock;
    default: return Building;
  }
};

const getQualityColor = (quality: number) => {
  if (quality >= 90) return "text-green-600 dark:text-green-400";
  if (quality >= 80) return "text-blue-600 dark:text-blue-400";
  if (quality >= 70) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
};

const getSizeRange = (size: string) => {
  const ranges = {
    "1-10": "Mikroföretag",
    "11-50": "Litet företag",
    "51-200": "Medelstort företag",
    "201-500": "Större företag",
    "501-1000": "Stort företag",
    "1000+": "Storföretag"
  };
  return ranges[size as keyof typeof ranges] || size;
};

export default function CompaniesPage() {
  const [activeTab, setActiveTab] = useState("companies");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedIndustry, setSelectedIndustry] = useState("all");
  const [selectedSize, setSelectedSize] = useState("all");

  const filteredCompanies = mockCompanies.filter(company => {
    const matchesSearch = 
      company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.domain.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      company.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesIndustry = selectedIndustry === "all" || company.industry === selectedIndustry;
    const matchesSize = selectedSize === "all" || company.size === selectedSize;
    return matchesSearch && matchesIndustry && matchesSize;
  });

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Företag</h1>
          <p className="text-gray-600 dark:text-gray-400">Hantera företagsprofiler och marknadsdata</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportera
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Uppdatera
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Lägg till företag
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Totalt företag</p>
                <p className="text-2xl font-bold">{companyStats.total.toLocaleString()}</p>
                <p className="text-xs text-gray-500">+{companyStats.newToday} idag</p>
              </div>
              <Building className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Aktiva företag</p>
                <p className="text-2xl font-bold">{companyStats.activeCompanies.toLocaleString()}</p>
                <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <CheckCircle className="h-3 w-3" />
                  <span className="text-xs">85.8%</span>
                </div>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Medelomsättning</p>
                <p className="text-2xl font-bold">{companyStats.avgRevenue}</p>
                <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <TrendingUp className="h-3 w-3" />
                  <span className="text-xs">+{companyStats.revenueGrowth}%</span>
                </div>
              </div>
              <DollarSign className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Datakvalitet</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{companyStats.qualityAvg}%</p>
                <p className="text-xs text-gray-500">Genomsnitt</p>
              </div>
              <Star className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="companies">Företag ({filteredCompanies.length})</TabsTrigger>
          <TabsTrigger value="analytics">Analys</TabsTrigger>
          <TabsTrigger value="industries">Branscher</TabsTrigger>
          <TabsTrigger value="verification">Verifiering</TabsTrigger>
          <TabsTrigger value="settings">Inställningar</TabsTrigger>
        </TabsList>

        {/* Companies Tab */}
        <TabsContent value="companies" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök företag efter namn, domän, beskrivning eller plats..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedIndustry}
                    onChange={(e) => setSelectedIndustry(e.target.value)}
                  >
                    <option value="all">Alla branscher</option>
                    <option value="IT & Tech">IT & Tech</option>
                    <option value="Consulting">Consulting</option>
                    <option value="Energy">Energi</option>
                    <option value="Marketing">Marknadsföring</option>
                    <option value="Finance">Finans</option>
                    <option value="Healthcare">Hälsovård</option>
                  </select>
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedSize}
                    onChange={(e) => setSelectedSize(e.target.value)}
                  >
                    <option value="all">Alla storlekar</option>
                    <option value="1-10">1-10 anställda</option>
                    <option value="11-50">11-50 anställda</option>
                    <option value="51-200">51-200 anställda</option>
                    <option value="201-500">201-500 anställda</option>
                    <option value="501-1000">501-1000 anställda</option>
                    <option value="1000+">1000+ anställda</option>
                  </select>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Mer filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Company List */}
          <div className="space-y-4">
            {filteredCompanies.map((company) => {
              const StatusIcon = getStatusIcon(company.status);
              return (
                <Card key={company.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row gap-6">
                      {/* Main Info */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                              <Building className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div>
                              <h3 className="text-xl font-bold flex items-center gap-2">
                                {company.name}
                                {company.verified && (
                                  <CheckCircle className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                                )}
                              </h3>
                              <p className="text-gray-600 dark:text-gray-400">{company.domain}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge variant="outline" className={`${getStatusColor(company.status)}`}>
                              <StatusIcon className="h-3 w-3 mr-1" />
                              {company.status}
                            </Badge>
                            <Badge variant="outline" className={`${getQualityColor(company.quality)} ml-2`}>
                              Kvalitet: {company.quality}%
                            </Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                          <div className="flex items-center gap-2">
                            <Briefcase className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Bransch</span>
                              <p className="font-medium">{company.industry}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Anställda</span>
                              <p className="font-medium">{company.employees.toLocaleString()}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <DollarSign className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Omsättning</span>
                              <p className="font-medium">{company.revenue}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Grundad</span>
                              <p className="font-medium">{company.founded}</p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Plats</span>
                              <p className="font-medium">{company.location}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">VD</span>
                              <p className="font-medium">{company.ceo}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Building className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Storlek</span>
                              <p className="font-medium">{getSizeRange(company.size)}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Globe className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Börsnoterad</span>
                              <p className="font-medium">{company.publiclyTraded ? "Ja" : "Nej"}</p>
                            </div>
                          </div>
                        </div>

                        <p className="text-gray-700 dark:text-gray-300 mb-4">{company.description}</p>

                        <div className="mb-4">
                          <span className="text-sm text-gray-500 dark:text-gray-400">Teknologier:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {company.technologies.slice(0, 6).map((tech, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {tech}
                              </Badge>
                            ))}
                            {company.technologies.length > 6 && (
                              <Badge variant="secondary" className="text-xs">
                                +{company.technologies.length - 6}
                              </Badge>
                            )}
                          </div>
                        </div>

                        <div className="mb-4">
                          <span className="text-sm text-gray-500 dark:text-gray-400">Certifieringar:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {company.certifications.map((cert, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                <Award className="h-3 w-3 mr-1" />
                                {cert}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                          {company.email && (
                            <span className="flex items-center gap-1">
                              <Mail className="h-3 w-3" />
                              {company.email}
                            </span>
                          )}
                          {company.phone && (
                            <span className="flex items-center gap-1">
                              <Phone className="h-3 w-3" />
                              {company.phone}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            Crawlad: {company.crawledAt}
                          </span>
                          <span>Källa: {company.source}</span>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex flex-row lg:flex-col gap-2 lg:w-32">
                        <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                          <Eye className="h-4 w-4 mr-2" />
                          Visa
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                          <Edit className="h-4 w-4 mr-2" />
                          Redigera
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1 lg:w-full">
                          <Trash2 className="h-4 w-4 mr-2" />
                          Ta bort
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          {filteredCompanies.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="text-gray-400 dark:text-gray-600">
                  <Building className="h-12 w-12 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Inga företag hittades</h3>
                  <p>Försök justera dina sökkriterier</p>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Storleksfördelning</CardTitle>
                <CardDescription>Företag per anställdstorlek</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📊 Storleksdiagram: Mest vanligt 51-200 anställda (28.4%)
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Geografisk fördelning</CardTitle>
                <CardDescription>Företag per region</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Stockholm</span>
                    <span className="font-medium">7,234</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Göteborg</span>
                    <span className="font-medium">4,567</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Malmö</span>
                    <span className="font-medium">2,890</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Uppsala</span>
                    <span className="font-medium">1,456</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Övriga</span>
                    <span className="font-medium">2,787</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Omsättningstrender</CardTitle>
                <CardDescription>Genomsnittsomsättning per bransch</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📈 Omsättningsdiagram: +{companyStats.revenueGrowth}% tillväxt YoY
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Grundningsår</CardTitle>
                <CardDescription>Ålder på företagen</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>2020-2024</span>
                    <span className="font-medium">18.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>2015-2019</span>
                    <span className="font-medium">24.7%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>2010-2014</span>
                    <span className="font-medium">21.3%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>2000-2009</span>
                    <span className="font-medium">19.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Före 2000</span>
                    <span className="font-medium">15.8%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Industries Tab */}
        <TabsContent value="industries" className="space-y-4">
          <div className="space-y-4">
            {industryStats.map((industry, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Briefcase className="h-6 w-6 text-blue-600" />
                      <div>
                        <h3 className="font-semibold text-lg">{industry.industry}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {industry.count.toLocaleString()} företag ({industry.percentage}%)
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="font-medium">Genomsnittsomsättning</p>
                      <p className="text-lg font-semibold text-primary">{industry.avgRevenue}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Verification Tab */}
        <TabsContent value="verification" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Verifieringsstatus</CardTitle>
                <CardDescription>Företagsdata verifiering</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Verifierade företag</span>
                    <Badge className="text-green-600">75.3%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Väntar på verifiering</span>
                    <Badge className="text-yellow-600">18.2%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Verifiering misslyckad</span>
                    <Badge className="text-red-600">6.5%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Verifieringsmetoder</CardTitle>
                <CardDescription>Olika verifieringstyper</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Bolagsverket</span>
                    <span className="font-medium">Automatisk</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Allabolag.se</span>
                    <span className="font-medium">API-baserad</span>
                  </div>
                  <div className="flex justify-between">
                    <span>LinkedIn</span>
                    <span className="font-medium">Social verifiering</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Manuell kontroll</span>
                    <span className="font-medium">Kvalitetssäkring</span>
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
              <CardTitle>Företagsinställningar</CardTitle>
              <CardDescription>Konfigurera företagsdatahantering</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Automatisk verifiering</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Verifiera företagsdata mot Bolagsverket</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Dubblettdetektering</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Identifiera och slå ihop dubblettföretag</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Kvalitetsminimum</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>70%</option>
                    <option>80%</option>
                    <option>90%</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Uppdateringsfrekvens</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>Dagligen</option>
                    <option>Veckovis</option>
                    <option>Månadsvis</option>
                  </select>
                </div>
              </div>

              <div className="pt-4 border-t">
                <Button>Spara inställningar</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    </Layout>
  );
}
