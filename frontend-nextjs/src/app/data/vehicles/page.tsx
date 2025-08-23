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
  Car,
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
  Trash2
} from "lucide-react";
import { useState } from "react";

// Mock vehicle data
const mockVehicles = [
  {
    id: "veh_001",
    make: "Volvo",
    model: "XC90",
    year: 2020,
    price: 450000,
    currency: "SEK",
    mileage: 45000,
    fuel: "Hybrid",
    transmission: "Automatic",
    color: "Svart",
    location: "Stockholm",
    dealer: "Volvo Stockholm",
    images: 8,
    description: "Välvårdad Volvo XC90 med fullservicehistorik",
    quality: 95,
    crawledAt: "2024-01-15 14:30:00",
    source: "biluppgifter.se",
    vin: "YV1******1234567",
    bodyType: "SUV",
    doors: 5,
    seats: 7
  },
  {
    id: "veh_002",
    make: "BMW",
    model: "320d",
    year: 2019,
    price: 295000,
    currency: "SEK", 
    mileage: 78000,
    fuel: "Diesel",
    transmission: "Automatic",
    color: "Vit",
    location: "Göteborg",
    dealer: "BMW Göteborg",
    images: 12,
    description: "BMW 320d med M-Sport paket och panoramatak",
    quality: 92,
    crawledAt: "2024-01-15 14:25:00",
    source: "blocket.se",
    vin: "WBA******7890123",
    bodyType: "Sedan",
    doors: 4,
    seats: 5
  },
  {
    id: "veh_003",
    make: "Tesla",
    model: "Model 3",
    year: 2022,
    price: 395000,
    currency: "SEK",
    mileage: 25000,
    fuel: "Electric",
    transmission: "Automatic",
    color: "Blå",
    location: "Malmö",
    dealer: "Tesla Center Malmö",
    images: 6,
    description: "Tesla Model 3 Long Range med autopilot",
    quality: 98,
    crawledAt: "2024-01-15 14:20:00",
    source: "biluppgifter.se",
    vin: "5YJ******4567890",
    bodyType: "Sedan", 
    doors: 4,
    seats: 5
  },
  {
    id: "veh_004",
    make: "Audi",
    model: "Q5",
    year: 2018,
    price: 285000,
    currency: "SEK",
    mileage: 95000,
    fuel: "Diesel",
    transmission: "Automatic", 
    color: "Grå",
    location: "Uppsala",
    dealer: "Audi Uppsala",
    images: 10,
    description: "Audi Q5 quattro med S-line utrustning",
    quality: 87,
    crawledAt: "2024-01-15 14:15:00",
    source: "car.info",
    vin: "WAU******2345678",
    bodyType: "SUV",
    doors: 5,
    seats: 5
  }
];

const vehicleStats = {
  total: 12847,
  newToday: 234,
  avgPrice: 325000,
  priceChange: +2.3,
  sources: 4,
  qualityAvg: 92.1
};

const makeStats = [
  { make: "Volvo", count: 2847, avgPrice: 285000, change: +1.2 },
  { make: "BMW", count: 2134, avgPrice: 315000, change: +2.8 },
  { make: "Audi", count: 1923, avgPrice: 295000, change: -0.5 },
  { make: "Mercedes", count: 1756, avgPrice: 345000, change: +3.1 },
  { make: "Tesla", count: 892, avgPrice: 425000, change: +5.2 },
  { make: "Volkswagen", count: 1845, avgPrice: 225000, change: +0.8 }
];

const getQualityColor = (quality: number) => {
  if (quality >= 95) return "text-green-600 dark:text-green-400";
  if (quality >= 90) return "text-blue-600 dark:text-blue-400";
  if (quality >= 80) return "text-yellow-600 dark:text-yellow-400";
  return "text-red-600 dark:text-red-400";
};

const formatPrice = (price: number, currency: string) => {
  return new Intl.NumberFormat('sv-SE', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0
  }).format(price);
};

const formatMileage = (mileage: number) => {
  return new Intl.NumberFormat('sv-SE').format(mileage) + ' mil';
};

export default function VehiclesPage() {
  const [activeTab, setActiveTab] = useState("vehicles");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedMake, setSelectedMake] = useState("all");

  const filteredVehicles = mockVehicles.filter(vehicle => {
    const matchesSearch = 
      vehicle.make.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesMake = selectedMake === "all" || vehicle.make === selectedMake;
    return matchesSearch && matchesMake;
  });

  return (
    <Layout>
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Fordon</h1>
          <p className="text-gray-600 dark:text-gray-400">Hantera fordonsprofiler och marknadsdata</p>
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
            Lägg till fordon
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Totalt fordon</p>
                <p className="text-2xl font-bold">{vehicleStats.total.toLocaleString()}</p>
                <p className="text-xs text-gray-500">+{vehicleStats.newToday} idag</p>
              </div>
              <Car className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Medelpris</p>
                <p className="text-2xl font-bold">{formatPrice(vehicleStats.avgPrice, 'SEK')}</p>
                <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                  <TrendingUp className="h-3 w-3" />
                  <span className="text-xs">+{vehicleStats.priceChange}%</span>
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
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Datakvalitet</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">{vehicleStats.qualityAvg}%</p>
                <p className="text-xs text-gray-500">Genomsnitt</p>
              </div>
              <Star className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Datakällor</p>
                <p className="text-2xl font-bold">{vehicleStats.sources}</p>
                <p className="text-xs text-gray-500">Aktiva källor</p>
              </div>
              <Database className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="vehicles">Fordon ({filteredVehicles.length})</TabsTrigger>
          <TabsTrigger value="analytics">Analys</TabsTrigger>
          <TabsTrigger value="brands">Märken</TabsTrigger>
          <TabsTrigger value="settings">Inställningar</TabsTrigger>
        </TabsList>

        {/* Vehicles Tab */}
        <TabsContent value="vehicles" className="space-y-4">
          {/* Search and Filter */}
          <Card>
            <CardContent className="p-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Sök fordon efter märke, modell eller plats..."
                      className="pl-10"
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select 
                    className="px-3 py-2 border rounded-lg bg-background text-sm"
                    value={selectedMake}
                    onChange={(e) => setSelectedMake(e.target.value)}
                  >
                    <option value="all">Alla märken</option>
                    <option value="Volvo">Volvo</option>
                    <option value="BMW">BMW</option>
                    <option value="Audi">Audi</option>
                    <option value="Tesla">Tesla</option>
                    <option value="Mercedes">Mercedes</option>
                  </select>
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Vehicle List */}
          <div className="space-y-4">
            {filteredVehicles.map((vehicle) => (
              <Card key={vehicle.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row gap-6">
                    {/* Main Info */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-xl font-bold">{vehicle.make} {vehicle.model}</h3>
                          <p className="text-lg font-semibold text-primary">
                            {formatPrice(vehicle.price, vehicle.currency)}
                          </p>
                        </div>
                        <div className="text-right">
                          <Badge variant="outline" className={`${getQualityColor(vehicle.quality)}`}>
                            Kvalitet: {vehicle.quality}%
                          </Badge>
                          <p className="text-sm text-gray-500 mt-1">
                            {vehicle.images} bilder
                          </p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">År</span>
                          <p className="font-medium">{vehicle.year}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Miltalet</span>
                          <p className="font-medium">{formatMileage(vehicle.mileage)}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Bränsle</span>
                          <p className="font-medium">{vehicle.fuel}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Växellåda</span>
                          <p className="font-medium">{vehicle.transmission}</p>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Färg</span>
                          <p className="font-medium">{vehicle.color}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Karosseri</span>
                          <p className="font-medium">{vehicle.bodyType}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Dörrar</span>
                          <p className="font-medium">{vehicle.doors}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">Säten</span>
                          <p className="font-medium">{vehicle.seats}</p>
                        </div>
                      </div>

                      <p className="text-gray-700 dark:text-gray-300 mb-4">{vehicle.description}</p>

                      <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3 w-3" />
                          {vehicle.location} • {vehicle.dealer}
                        </span>
                        <span className="flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          Crawlad: {vehicle.crawledAt}
                        </span>
                        <span>Källa: {vehicle.source}</span>
                        <span>VIN: {vehicle.vin}</span>
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

          {filteredVehicles.length === 0 && (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="text-gray-400 dark:text-gray-600">
                  <Car className="h-12 w-12 mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Inga fordon hittades</h3>
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
                <CardTitle>Prisanalys</CardTitle>
                <CardDescription>Prisutveckling över tid</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center text-gray-500">
                  📈 Prisdiagram: Medelpris {formatPrice(vehicleStats.avgPrice, 'SEK')}, +{vehicleStats.priceChange}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Märkesfördelning</CardTitle>
                <CardDescription>Antal fordon per märke</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {makeStats.slice(0, 5).map((make, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <span className="font-medium">{make.make}</span>
                      <div className="flex items-center gap-2">
                        <Badge>{make.count.toLocaleString()}</Badge>
                        <span className={`text-xs ${make.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {make.change > 0 ? '+' : ''}{make.change}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Geografisk fördelning</CardTitle>
                <CardDescription>Fordon per region</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Stockholm</span>
                    <span className="font-medium">4,234</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Göteborg</span>
                    <span className="font-medium">3,567</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Malmö</span>
                    <span className="font-medium">2,890</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Uppsala</span>
                    <span className="font-medium">1,456</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Kvalitetsanalys</CardTitle>
                <CardDescription>Datakvalitet per källa</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>biluppgifter.se</span>
                    <span className="font-medium text-green-600">96.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>blocket.se</span>
                    <span className="font-medium text-green-600">92.1%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>car.info</span>
                    <span className="font-medium text-yellow-600">87.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>hemnet.se</span>
                    <span className="font-medium text-red-600">67.3%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Brands Tab */}
        <TabsContent value="brands" className="space-y-4">
          <div className="space-y-4">
            {makeStats.map((make, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <Car className="h-6 w-6 text-blue-600" />
                      <div>
                        <h3 className="font-semibold text-lg">{make.make}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {make.count.toLocaleString()} fordon
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <p className="font-medium">Medelpris</p>
                        <p className="text-lg font-semibold text-primary">
                          {formatPrice(make.avgPrice, 'SEK')}
                        </p>
                      </div>
                      
                      <div className="text-right">
                        <p className="font-medium">Förändring</p>
                        <div className={`flex items-center gap-1 ${make.change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          <TrendingUp className="h-4 w-4" />
                          <span className="font-semibold">
                            {make.change > 0 ? '+' : ''}{make.change}%
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
              <CardTitle>Fordonsinställningar</CardTitle>
              <CardDescription>Konfigurera fordonsdatahantering</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Automatisk kvalitetskontroll</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Validera fordonsinformation automatiskt</p>
                  </div>
                  <Button variant="outline" size="sm">Aktivera</Button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">VIN-validering</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Kontrollera VIN-nummer format</p>
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
                  <label className="font-medium">Prisformat</label>
                  <select className="w-full p-2 border rounded-lg bg-background max-w-xs">
                    <option>Svensk standard</option>
                    <option>Europeisk standard</option>
                    <option>Amerikansk standard</option>
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
