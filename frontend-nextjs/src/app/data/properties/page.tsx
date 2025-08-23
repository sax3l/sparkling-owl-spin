'use client';

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Layout from "@/components/Layout";
import { 
  Search,
  Filter,
  Home,
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
  Bed,
  Bath,
  Square
} from "lucide-react";
import { useState } from "react";

// Mock property data
const mockProperties = [
  {
    id: "prop_001",
    address: "Östermalm 23, Stockholm",
    price: 8500000,
    currency: "SEK",
    pricePerSqm: 85000,
    rooms: 4,
    bedrooms: 3,
    bathrooms: 2,
    area: 100,
    type: "Lägenhet",
    yearBuilt: 1920,
    floor: 3,
    totalFloors: 5,
    balcony: true,
    elevator: true,
    parking: false,
    description: "Vacker sekelskiftesvåning med högt i tak och originaldetaljer",
    quality: 95,
    crawledAt: "2024-01-15 14:30:00",
    source: "hemnet.se",
    agent: "Svensk Fastighetsförmedling",
    images: 12,
    daysOnMarket: 14,
    viewings: 47,
    energyClass: "C"
  },
  {
    id: "prop_002",
    address: "Vasagatan 15, Göteborg",
    price: 4200000,
    currency: "SEK",
    pricePerSqm: 70000,
    rooms: 3,
    bedrooms: 2,
    bathrooms: 1,
    area: 60,
    type: "Lägenhet",
    yearBuilt: 1965,
    floor: 2,
    totalFloors: 4,
    balcony: true,
    elevator: false,
    parking: true,
    description: "Trivsam lägenhet med balkong och parkeringsplats",
    quality: 88,
    crawledAt: "2024-01-15 14:25:00",
    source: "booli.se",
    agent: "Mäklarhuset",
    images: 8,
    daysOnMarket: 7,
    viewings: 23,
    energyClass: "D"
  },
  {
    id: "prop_003",
    address: "Storgatan 42, Malmö",
    price: 3850000,
    currency: "SEK",
    pricePerSqm: 55000,
    rooms: 5,
    bedrooms: 4,
    bathrooms: 2,
    area: 70,
    type: "Lägenhet",
    yearBuilt: 2018,
    floor: 1,
    totalFloors: 6,
    balcony: true,
    elevator: true,
    parking: true,
    description: "Nybyggd lägenhet med moderna lösningar och god planlösning",
    quality: 96,
    crawledAt: "2024-01-15 14:20:00",
    source: "hemnet.se",
    agent: "Fastighetsbyrån",
    images: 15,
    daysOnMarket: 3,
    viewings: 18,
    energyClass: "A"
  },
  {
    id: "prop_004",
    address: "Kungsgatan 8, Uppsala",
    price: 2950000,
    currency: "SEK",
    pricePerSqm: 49000,
    rooms: 3,
    bedrooms: 2,
    bathrooms: 1,
    area: 60,
    type: "Lägenhet",
    yearBuilt: 1985,
    floor: 5,
    totalFloors: 8,
    balcony: false,
    elevator: true,
    parking: false,
    description: "Centralt belägen lägenhet med fin utsikt över staden",
    quality: 82,
    crawledAt: "2024-01-15 14:15:00",
    source: "booli.se",
    agent: "SkandiaMäklarna",
    images: 6,
    daysOnMarket: 21,
    viewings: 32,
    energyClass: "E"
  }
];

const propertyStats = {
  total: 45623,
  newToday: 127,
  avgPrice: 4850000,
  avgPricePerSqm: 68500,
  priceChange: +3.8,
  avgDaysOnMarket: 28,
  sources: 6,
  qualityAvg: 89.4
};

const regionStats = [
  { region: "Stockholm", count: 18934, avgPrice: 7850000, change: +4.2 },
  { region: "Göteborg", count: 12847, avgPrice: 4250000, change: +3.1 },
  { region: "Malmö", count: 8756, avgPrice: 3950000, change: +5.8 },
  { region: "Uppsala", count: 3421, avgPrice: 3450000, change: +2.7 },
  { region: "Linköping", count: 1665, avgPrice: 2850000, change: +1.9 }
];

const getQualityColor = (quality: number) => {
  if (quality >= 95) return "text-green-600 dark:text-green-400";
  if (quality >= 90) return "text-blue-600 dark:text-blue-400";
  if (quality >= 80) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
};

const getEnergyClassColor = (energyClass: string) => {
  switch (energyClass) {
    case "A": return "text-green-600 dark:text-green-400";
    case "B": case "C": return "text-blue-600 dark:text-blue-400";
    case "D": case "E": return "text-yellow-600 dark:text-yellow-400";
    default: return "text-red-600 dark:text-red-400";
  }
};

const formatPrice = (price: number, currency: string) => {
  return new Intl.NumberFormat('sv-SE', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0
  }).format(price);
};

export default function PropertiesPage() {
  const [activeTab, setActiveTab] = useState("properties");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedRegion, setSelectedRegion] = useState("all");
  const [selectedType, setSelectedType] = useState("all");

  const filteredProperties = mockProperties.filter(property => {
    const matchesSearch = 
      property.address.toLowerCase().includes(searchTerm.toLowerCase()) ||
      property.agent.toLowerCase().includes(searchTerm.toLowerCase()) ||
      property.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRegion = selectedRegion === "all" || 
      property.address.includes(selectedRegion);
    const matchesType = selectedType === "all" || property.type === selectedType;
    return matchesSearch && matchesRegion && matchesType;
  });

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Fastigheter</h1>
          <p className="text-gray-600 dark:text-gray-400">Hantera fastighetsprofiler och marknadsdata</p>
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
            Lägg till fastighet
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Totalt fastigheter</p>
                <p className="text-2xl font-bold">{propertyStats.total.toLocaleString()}</p>
                <p className="text-xs text-gray-500">+{propertyStats.newToday} idag</p>
              </div>
              <Home className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Medelpris</p>
                <p className="text-2xl font-bold">{formatPrice(propertyStats.avgPrice, 'SEK')}</p>
                <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <TrendingUp className="h-3 w-3" />
                  <span className="text-xs">+{propertyStats.priceChange}%</span>
                </div>
              </div>
              <BarChart3 className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Pris per m²</p>
                <p className="text-2xl font-bold">{propertyStats.avgPricePerSqm.toLocaleString()}</p>
                <p className="text-xs text-gray-500">SEK/m²</p>
              </div>
              <Square className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Datakvalitet</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">{propertyStats.qualityAvg}%</p>
                <p className="text-xs text-gray-500">Genomsnitt</p>
              </div>
              <Star className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="properties">Fastigheter ({filteredProperties.length})</TabsTrigger>
          <TabsTrigger value="analytics">Analys</TabsTrigger>
          <TabsTrigger value="regions">Regioner</TabsTrigger>
          <TabsTrigger value="settings">Inställningar</TabsTrigger>
        </TabsList>

        {/* Properties Tab */}
        <TabsContent value="properties" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök fastigheter efter adress, mäklare eller beskrivning..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedRegion}
                    onChange={(e) => setSelectedRegion(e.target.value)}
                  >
                    <option value="all">Alla regioner</option>
                    <option value="Stockholm">Stockholm</option>
                    <option value="Göteborg">Göteborg</option>
                    <option value="Malmö">Malmö</option>
                    <option value="Uppsala">Uppsala</option>
                  </select>
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedType}
                    onChange={(e) => setSelectedType(e.target.value)}
                  >
                    <option value="all">Alla typer</option>
                    <option value="Lägenhet">Lägenhet</option>
                    <option value="Villa">Villa</option>
                    <option value="Radhus">Radhus</option>
                  </select>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Mer filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Property List */}
          <div className="space-y-4">
            {filteredProperties.map((property) => (
              <Card key={property.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row gap-6">
                    {/* Main Info */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-xl font-bold">{property.address}</h3>
                          <p className="text-lg font-semibold text-primary">
                            {formatPrice(property.price, property.currency)}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {property.pricePerSqm.toLocaleString()} SEK/m²
                          </p>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline" className={`${getQualityColor(property.quality)}`}>
                            Kvalitet: {property.quality}%
                          </Badge>
                          <Badge variant="outline" className={`${getEnergyClassColor(property.energyClass)} ml-2`}>
                            Energi: {property.energyClass}
                          </Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                        <div className="flex items-center gap-2">
                          <Home className="h-4 w-4 text-gray-400" />
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Rum</span>
                            <p className="font-medium">{property.rooms}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Bed className="h-4 w-4 text-gray-400" />
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Sovrum</span>
                            <p className="font-medium">{property.bedrooms}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Bath className="h-4 w-4 text-gray-400" />
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Badrum</span>
                            <p className="font-medium">{property.bathrooms}</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Square className="h-4 w-4 text-gray-400" />
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Yta</span>
                            <p className="font-medium">{property.area} m²</p>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Typ</span>
                          <p className="font-medium">{property.type}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Byggt</span>
                          <p className="font-medium">{property.yearBuilt}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Våning</span>
                          <p className="font-medium">{property.floor} av {property.totalFloors}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Bilder</span>
                          <p className="font-medium">{property.images} st</p>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 mb-4">
                        {property.balcony && (
                          <Badge variant="secondary">Balkong</Badge>
                        )}
                        {property.elevator && (
                          <Badge variant="secondary">Hiss</Badge>
                        )}
                        {property.parking && (
                          <Badge variant="secondary">Parkering</Badge>
                        )}
                      </div>

                      <p className="text-gray-700 dark:text-gray-300 mb-4">{property.description}</p>

                      <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {property.agent}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          Crawlad: {property.crawledAt}
                        </span>
                        <span>Källa: {property.source}</span>
                        <span>Marknaden: {property.daysOnMarket} dagar</span>
                        <span>Visningar: {property.viewings}</span>
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
            ))}
          </div>

          {filteredProperties.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="text-gray-400 dark:text-gray-600">
                  <Home className="h-12 w-12 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Inga fastigheter hittades</h3>
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
                <CardTitle>Prisutveckling</CardTitle>
                <CardDescription>Pristrend över tid</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📈 Prisdiagram: Medelpris {formatPrice(propertyStats.avgPrice, 'SEK')}, +{propertyStats.priceChange}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Regionfördelning</CardTitle>
                <CardDescription>Fastigheter per region</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {regionStats.slice(0, 5).map((region, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <span className="font-medium">{region.region}</span>
                      <div className="flex items-center gap-2">
                        <Badge>{region.count.toLocaleString()}</Badge>
                        <span className={`text-xs ${region.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {region.change > 0 ? '+' : ''}{region.change}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Säljhastighet</CardTitle>
                <CardDescription>Genomsnittlig tid på marknaden</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                    {propertyStats.avgDaysOnMarket} dagar
                  </p>
                  <p className="text-sm text-gray-500 mt-2">Genomsnittlig tid på marknaden</p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Energiklasser</CardTitle>
                <CardDescription>Fördelning av energiklasser</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>A-klass</span>
                    <span className="font-medium text-green-600">18.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>B-klass</span>
                    <span className="font-medium text-blue-600">24.7%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>C-klass</span>
                    <span className="font-medium text-blue-600">31.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>D-klass</span>
                    <span className="font-medium text-yellow-600">19.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>E-F-klass</span>
                    <span className="font-medium text-red-600">5.9%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Regions Tab */}
        <TabsContent value="regions" className="space-y-4">
          <div className="space-y-4">
            {regionStats.map((region, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <MapPin className="h-6 w-6 text-blue-600" />
                      <div>
                        <h3 className="font-semibold text-lg">{region.region}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {region.count.toLocaleString()} fastigheter
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <p className="font-medium">Medelpris</p>
                        <p className="text-lg font-semibold text-primary">
                          {formatPrice(region.avgPrice, 'SEK')}
                        </p>
                      </div>
                      
                      <div className="text-right">
                        <p className="font-medium">Förändring</p>
                        <div className={`flex items-center gap-1 ${region.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          <TrendingUp className="h-4 w-4" />
                          <span className="font-semibold">
                            {region.change > 0 ? '+' : ''}{region.change}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Fastighetsinställningar</CardTitle>
              <CardDescription>Konfigurera fastighetsdatahantering</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Automatisk prisvalidering</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Validera priser mot marknadsdata</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Bildanalys</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Analysera fastighetsbilder automatiskt</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Standardvaluta</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>SEK</option>
                    <option>EUR</option>
                    <option>USD</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="font-medium">Prisnotation</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>Svensk standard</option>
                    <option>Internationell standard</option>
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
