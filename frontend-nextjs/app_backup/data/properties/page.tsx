'use client';

import React from 'react';
import Layout from '../../../src/components/Layout';

// Import our completed properties page component functionality
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { 
  Search,
  Filter,
  Home,
  MapPin,
  Calendar,
  TrendingUp,
  BarChart3,
  Users,
  DollarSign,
  AlertCircle,
  CheckCircle,
  Clock,
  Plus,
  Settings,
  Download,
  Edit
} from "lucide-react";

// Mock property data
const mockProperties = [
  {
    id: "1",
    address: "Storgatan 15, Stockholm",
    type: "Lägenhet",
    size: 85,
    rooms: 3,
    price: 6500000,
    pricePerSqm: 76470,
    listingDate: "2024-01-10",
    agent: "Maria Andersson",
    agency: "Hemnet Mäklare",
    description: "Fantastisk 3:a med balkong och öppen planlösning",
    status: "active",
    views: 1247,
    favorites: 89,
    quality: 95,
    crawledAt: "2024-01-15 14:30:00",
    source: "hemnet.se"
  },
  {
    id: "2", 
    address: "Östermalmsvägen 42, Göteborg",
    type: "Villa",
    size: 120,
    rooms: 5,
    price: 8900000,
    pricePerSqm: 74166,
    listingDate: "2024-01-08",
    agent: "Erik Johansson",
    agency: "SkandiaMäklarna",
    description: "Rymlig villa med trädgård i attraktivt område",
    status: "pending",
    views: 2156,
    favorites: 156,
    quality: 88,
    crawledAt: "2024-01-15 14:15:00",
    source: "booli.se"
  }
];

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
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Ny Fastighet
            </Button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Totalt Fastigheter</p>
                  <p className="text-2xl font-bold text-blue-600">{mockProperties.length.toLocaleString()}</p>
                </div>
                <Home className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Genomsnittspris</p>
                  <p className="text-2xl font-bold text-green-600">
                    {(mockProperties.reduce((acc, p) => acc + p.price, 0) / mockProperties.length / 1000000).toFixed(1)}M kr
                  </p>
                </div>
                <DollarSign className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Aktiva Annonser</p>
                  <p className="text-2xl font-bold text-orange-600">
                    {mockProperties.filter(p => p.status === 'active').length}
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Genomsnitt Visningar</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {Math.round(mockProperties.reduce((acc, p) => acc + p.views, 0) / mockProperties.length)}
                  </p>
                </div>
                <BarChart3 className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="properties">Fastigheter</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="settings">Inställningar</TabsTrigger>
          </TabsList>

          <TabsContent value="properties" className="space-y-6">
            {/* Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Filtrera Fastigheter</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col sm:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        placeholder="Sök fastigheter..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div className="w-full sm:w-48">
                    <select 
                      value={selectedRegion}
                      onChange={(e) => setSelectedRegion(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg bg-background"
                    >
                      <option value="all">All Regioner</option>
                      <option value="Stockholm">Stockholm</option>
                      <option value="Göteborg">Göteborg</option>
                      <option value="Malmö">Malmö</option>
                    </select>
                  </div>
                  <div className="w-full sm:w-48">
                    <select 
                      value={selectedType}
                      onChange={(e) => setSelectedType(e.target.value)}
                      className="w-full px-3 py-2 border rounded-lg bg-background"
                    >
                      <option value="all">All Typer</option>
                      <option value="Lägenhet">Lägenhet</option>
                      <option value="Villa">Villa</option>
                      <option value="Radhus">Radhus</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Property List */}
            <div className="grid grid-cols-1 gap-4">
              {filteredProperties.map((property) => (
                <Card key={property.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-lg">{property.address}</h3>
                          <Badge variant={property.status === 'active' ? 'default' : 'secondary'}>
                            {property.status === 'active' ? 'Aktiv' : 'Pending'}
                          </Badge>
                          <Badge variant="outline">{property.type}</Badge>
                        </div>
                        <p className="text-gray-600 dark:text-gray-400 mb-3">{property.description}</p>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-gray-500">Pris</p>
                            <p className="font-semibold text-green-600">{property.price.toLocaleString()} kr</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Storlek</p>
                            <p className="font-semibold">{property.size} m²</p>
                          </div>
                          <div>
                            <p className="text-gray-500">Rum</p>
                            <p className="font-semibold">{property.rooms} rum</p>
                          </div>
                          <div>
                            <p className="text-gray-500">kr/m²</p>
                            <p className="font-semibold text-blue-600">{property.pricePerSqm.toLocaleString()}</p>
                          </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                          <div className="text-center">
                            <p className="text-2xl font-bold text-blue-600">{property.views}</p>
                            <p className="text-xs text-gray-500">Visningar</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-red-600">{property.favorites}</p>
                            <p className="text-xs text-gray-500">Favoriter</p>
                          </div>
                          <div className="text-center">
                            <p className="text-2xl font-bold text-green-600">{property.quality}%</p>
                            <p className="text-xs text-gray-500">Kvalitet</p>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2 ml-4">
                        <Button size="sm" variant="outline">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button size="sm" variant="outline">
                          <Settings className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <span>{property.agent} - {property.agency}</span>
                      <span>Crawlad: {property.crawledAt} från {property.source}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Fastighetanalys</CardTitle>
                <CardDescription>Detaljerad marknadsanalys och trender</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Analytics-diagram kommer här</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Fastighetsinställningar</CardTitle>
                <CardDescription>Konfigurera datakällor och crawling-inställningar</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Aktiva Källor</label>
                    <div className="space-y-2">
                      <label className="flex items-center gap-2">
                        <input type="checkbox" defaultChecked />
                        <span>Hemnet.se</span>
                      </label>
                      <label className="flex items-center gap-2">
                        <input type="checkbox" defaultChecked />
                        <span>Booli.se</span>
                      </label>
                      <label className="flex items-center gap-2">
                        <input type="checkbox" />
                        <span>Vitahus.se</span>
                      </label>
                    </div>
                  </div>
                  <div className="pt-4">
                    <Button>Spara Inställningar</Button>
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
