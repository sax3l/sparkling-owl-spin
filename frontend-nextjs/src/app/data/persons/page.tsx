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
  User,
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
  Phone,
  Mail,
  Building,
  Shield,
  CheckCircle,
  AlertTriangle,
  Clock
} from "lucide-react";
import { useState } from "react";

// Mock person data
const mockPersons = [
  {
    id: "pers_001",
    name: "Anna Andersson",
    email: "anna.andersson@email.com",
    phone: "+46 70 123 4567",
    age: 34,
    gender: "Kvinna",
    location: "Stockholm",
    company: "Tech Sweden AB",
    position: "Utvecklingschef",
    industry: "IT & Tech",
    experience: 12,
    education: "Civilingenjör",
    skills: ["Python", "React", "DevOps", "Agile"],
    linkedinUrl: "linkedin.com/in/annaandersson",
    gdprConsent: true,
    lastActivity: "2024-01-15 14:30:00",
    status: "active",
    quality: 95,
    source: "linkedin.com",
    profileViews: 247,
    connections: 892,
    verified: true
  },
  {
    id: "pers_002", 
    name: "Erik Johansson",
    email: "erik.j@company.se",
    phone: "+46 73 987 6543",
    age: 28,
    gender: "Man",
    location: "Göteborg",
    company: "Design Studio",
    position: "UX Designer",
    industry: "Design",
    experience: 6,
    education: "Kandidat Design",
    skills: ["Figma", "Sketch", "UX Research", "Prototyping"],
    linkedinUrl: "linkedin.com/in/erikjohansson",
    gdprConsent: true,
    lastActivity: "2024-01-15 13:45:00",
    status: "active",
    quality: 92,
    source: "indeed.se",
    profileViews: 156,
    connections: 431,
    verified: true
  },
  {
    id: "pers_003",
    name: "Maria Nilsson",
    email: "maria.nilsson@email.com",
    phone: "",
    age: 41,
    gender: "Kvinna", 
    location: "Malmö",
    company: "Marketing Pro",
    position: "Marknadschef",
    industry: "Marketing",
    experience: 18,
    education: "MBA",
    skills: ["Digital Marketing", "SEO", "Analytics", "Strategy"],
    linkedinUrl: "",
    gdprConsent: false,
    lastActivity: "2024-01-14 16:20:00",
    status: "incomplete",
    quality: 76,
    source: "xing.com",
    profileViews: 89,
    connections: 234,
    verified: false
  },
  {
    id: "pers_004",
    name: "David Larsson",
    email: "d.larsson@startup.com",
    phone: "+46 76 555 0123",
    age: 31,
    gender: "Man",
    location: "Uppsala",
    company: "StartupX",
    position: "CTO",
    industry: "Fintech",
    experience: 9,
    education: "Masterexamen IT",
    skills: ["Blockchain", "Node.js", "AWS", "Team Leadership"],
    linkedinUrl: "linkedin.com/in/davidlarsson",
    gdprConsent: true,
    lastActivity: "2024-01-15 11:15:00",
    status: "needs_review",
    quality: 88,
    source: "glassdoor.com",
    profileViews: 312,
    connections: 678,
    verified: true
  }
];

const personStats = {
  total: 28472,
  newToday: 89,
  activePersons: 24531,
  averageAge: 34.2,
  gdprCompliant: 26845,
  qualityAvg: 87.3,
  sources: 8,
  verified: 19234
};

const industryStats = [
  { industry: "IT & Tech", count: 8934, percentage: 31.4, avgAge: 32.1 },
  { industry: "Finance", count: 5672, percentage: 19.9, avgAge: 36.8 },
  { industry: "Healthcare", count: 4321, percentage: 15.2, avgAge: 38.4 },
  { industry: "Education", count: 3456, percentage: 12.1, avgAge: 41.2 },
  { industry: "Marketing", count: 2890, percentage: 10.1, avgAge: 35.6 },
  { industry: "Other", count: 3199, percentage: 11.2, avgAge: 37.3 }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return "text-green-600 dark:text-green-400";
    case "incomplete": return "text-yellow-600 dark:text-yellow-400";
    case "needs_review": return "text-orange-600 dark:text-orange-400";
    case "inactive": return "text-red-600 dark:text-red-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "active": return CheckCircle;
    case "incomplete": return Clock;
    case "needs_review": return AlertTriangle;
    default: return User;
  }
};

const getQualityColor = (quality: number) => {
  if (quality >= 90) return "text-green-600 dark:text-green-400";
  if (quality >= 80) return "text-blue-600 dark:text-blue-400";
  if (quality >= 70) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
};

export default function PersonsPage() {
  const [activeTab, setActiveTab] = useState("persons");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const [selectedIndustry, setSelectedIndustry] = useState("all");

  const filteredPersons = mockPersons.filter(person => {
    const matchesSearch = 
      person.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      person.position.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || person.status === selectedStatus;
    const matchesIndustry = selectedIndustry === "all" || person.industry === selectedIndustry;
    return matchesSearch && matchesStatus && matchesIndustry;
  });

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Personer</h1>
          <p className="text-gray-600 dark:text-gray-400">Hantera personprofiler och professionella data</p>
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
            Lägg till person
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Totalt personer</p>
                <p className="text-2xl font-bold">{personStats.total.toLocaleString()}</p>
                <p className="text-xs text-gray-500">+{personStats.newToday} idag</p>
              </div>
              <User className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Aktiva profiler</p>
                <p className="text-2xl font-bold">{personStats.activePersons.toLocaleString()}</p>
                <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <CheckCircle className="h-3 w-3" />
                  <span className="text-xs">86.2%</span>
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
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">GDPR-godkända</p>
                <p className="text-2xl font-bold">{personStats.gdprCompliant.toLocaleString()}</p>
                <p className="text-xs text-gray-500">94.3%</p>
              </div>
              <Shield className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Datakvalitet</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{personStats.qualityAvg}%</p>
                <p className="text-xs text-gray-500">Genomsnitt</p>
              </div>
              <Star className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="persons">Personer ({filteredPersons.length})</TabsTrigger>
          <TabsTrigger value="analytics">Analys</TabsTrigger>
          <TabsTrigger value="industries">Branscher</TabsTrigger>
          <TabsTrigger value="gdpr">GDPR</TabsTrigger>
          <TabsTrigger value="settings">Inställningar</TabsTrigger>
        </TabsList>

        {/* Persons Tab */}
        <TabsContent value="persons" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök personer efter namn, företag, position eller e-post..."
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
                    <option value="all">Alla status</option>
                    <option value="active">Aktiv</option>
                    <option value="incomplete">Ofullständig</option>
                    <option value="needs_review">Behöver granskning</option>
                  </select>
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedIndustry}
                    onChange={(e) => setSelectedIndustry(e.target.value)}
                  >
                    <option value="all">Alla branscher</option>
                    <option value="IT & Tech">IT & Tech</option>
                    <option value="Finance">Finans</option>
                    <option value="Healthcare">Hälsovård</option>
                    <option value="Education">Utbildning</option>
                    <option value="Marketing">Marknadsföring</option>
                  </select>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Mer filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Person List */}
          <div className="space-y-4">
            {filteredPersons.map((person) => {
              const StatusIcon = getStatusIcon(person.status);
              return (
                <Card key={person.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex flex-col lg:flex-row gap-6">
                      {/* Main Info */}
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                              <User className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div>
                              <h3 className="text-xl font-bold flex items-center gap-2">
                                {person.name}
                                {person.verified && (
                                  <CheckCircle className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                                )}
                              </h3>
                              <p className="text-gray-600 dark:text-gray-400">{person.position} at {person.company}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge variant="outline" className={`${getStatusColor(person.status)}`}>
                              <StatusIcon className="h-3 w-3 mr-1" />
                              {person.status}
                            </Badge>
                            <Badge variant="outline" className={`${getQualityColor(person.quality)} ml-2`}>
                              Kvalitet: {person.quality}%
                            </Badge>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                          <div className="flex items-center gap-2">
                            <Mail className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">E-post</span>
                              <p className="font-medium truncate">{person.email || "Inte tillgänglig"}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Phone className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Telefon</span>
                              <p className="font-medium">{person.phone || "Inte tillgänglig"}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Plats</span>
                              <p className="font-medium">{person.location}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Building className="h-4 w-4 text-gray-400" />
                            <div>
                              <span className="text-gray-500 dark:text-gray-400">Bransch</span>
                              <p className="font-medium">{person.industry}</p>
                            </div>
                          </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Ålder</span>
                            <p className="font-medium">{person.age} år</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Erfarenhet</span>
                            <p className="font-medium">{person.experience} år</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Utbildning</span>
                            <p className="font-medium">{person.education}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Kontakter</span>
                            <p className="font-medium">{person.connections.toLocaleString()}</p>
                          </div>
                        </div>

                        <div className="mb-4">
                          <span className="text-sm text-gray-500 dark:text-gray-400">Färdigheter:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {person.skills.slice(0, 4).map((skill, index) => (
                              <Badge key={index} variant="secondary" className="text-xs">
                                {skill}
                              </Badge>
                            ))}
                            {person.skills.length > 4 && (
                              <Badge variant="secondary" className="text-xs">
                                +{person.skills.length - 4}
                              </Badge>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2 mb-4">
                          <Shield className={`h-4 w-4 ${person.gdprConsent ? 'text-green-600' : 'text-red-600'}`} />
                          <span className={`text-sm ${person.gdprConsent ? 'text-green-600' : 'text-red-600'}`}>
                            {person.gdprConsent ? 'GDPR-godkänd' : 'GDPR-godkännande saknas'}
                          </span>
                        </div>

                        <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            Senast aktiv: {person.lastActivity}
                          </span>
                          <span>Källa: {person.source}</span>
                          <span>Profilvisningar: {person.profileViews}</span>
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

          {filteredPersons.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="text-gray-400 dark:text-gray-600">
                  <User className="h-12 w-12 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Inga personer hittades</h3>
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
                <CardTitle>Åldersfördelning</CardTitle>
                <CardDescription>Genomsnittlig ålder: {personStats.averageAge} år</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📊 Åldersdiagram: Vanligaste åldern 28-35 år (34.2%)
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Geografisk fördelning</CardTitle>
                <CardDescription>Personer per region</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Stockholm</span>
                    <span className="font-medium">12,847</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Göteborg</span>
                    <span className="font-medium">8,234</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Malmö</span>
                    <span className="font-medium">4,567</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Uppsala</span>
                    <span className="font-medium">1,923</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Övrigt</span>
                    <span className="font-medium">901</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Erfarenhetsnivåer</CardTitle>
                <CardDescription>Fördelning av yrkeserfaenhet</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>0-2 år</span>
                    <span className="font-medium">15.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>3-5 år</span>
                    <span className="font-medium">28.7%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>6-10 år</span>
                    <span className="font-medium">31.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>11-15 år</span>
                    <span className="font-medium">17.9%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>16+ år</span>
                    <span className="font-medium">6.8%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Datakvalitet per källa</CardTitle>
                <CardDescription>Genomsnittlig kvalitet per källa</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>LinkedIn</span>
                    <span className="font-medium text-green-600">94.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Indeed</span>
                    <span className="font-medium text-blue-600">89.7%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Glassdoor</span>
                    <span className="font-medium text-yellow-600">82.1%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Xing</span>
                    <span className="font-medium text-red-600">71.3%</span>
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
                      <Building className="h-6 w-6 text-blue-600" />
                      <div>
                        <h3 className="font-semibold text-lg">{industry.industry}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {industry.count.toLocaleString()} personer ({industry.percentage}%)
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className="font-medium">Genomsnittlig ålder</p>
                      <p className="text-lg font-semibold text-primary">{industry.avgAge} år</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* GDPR Tab */}
        <TabsContent value="gdpr" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>GDPR-status</CardTitle>
                <CardDescription>Genomsnitt över alla profiler</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Godkänd lagring</span>
                    <Badge className="text-green-600">94.3%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Väntar på godkännande</span>
                    <Badge className="text-yellow-600">3.2%</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Nekad lagring</span>
                    <Badge className="text-red-600">2.5%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Databehandling</CardTitle>
                <CardDescription>Känslig information</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span>Personuppgifter</span>
                    <span className="font-medium">Krypterad</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Kontaktuppgifter</span>
                    <span className="font-medium">Anonymiserad</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Beteendedata</span>
                    <span className="font-medium">Aggregerad</span>
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
              <CardTitle>Personinställningar</CardTitle>
              <CardDescription>Konfigurera persondatahantering</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">GDPR-kontroll</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Automatisk GDPR-kompabilitetscheck</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Dubblettdetektering</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Identifiera och slå ihop dubblettprofiler</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Dataretention</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>12 månader</option>
                    <option>24 månader</option>
                    <option>36 månader</option>
                    <option>Permanent</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Kvalitets minimum</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>70%</option>
                    <option>80%</option>
                    <option>90%</option>
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
