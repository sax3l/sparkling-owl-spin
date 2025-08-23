'use client';

import React from 'react';
import Layout from '../../src/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { BarChart3, TrendingUp, Users, Eye, Download, Calendar, Activity } from "lucide-react";

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState("overview");

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
            <select className="px-3 py-2 border rounded-lg bg-background text-sm">
              <option value="7d">Senaste 7 dagarna</option>
              <option value="30d">Senaste 30 dagarna</option>
              <option value="90d">Senaste 90 dagarna</option>
            </select>
            <Button variant="outline" size="sm">
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Sessions</p>
                  <p className="text-2xl font-bold text-blue-600">24,532</p>
                  <p className="text-sm text-green-600 flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3" />
                    +12.5%
                  </p>
                </div>
                <Users className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Page Views</p>
                  <p className="text-2xl font-bold text-green-600">156,789</p>
                  <p className="text-sm text-green-600 flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3" />
                    +8.3%
                  </p>
                </div>
                <Eye className="w-8 h-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Session Duration</p>
                  <p className="text-2xl font-bold text-purple-600">4m 32s</p>
                  <p className="text-sm text-red-600 flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 rotate-180" />
                    -2.1%
                  </p>
                </div>
                <Calendar className="w-8 h-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Bounce Rate</p>
                  <p className="text-2xl font-bold text-orange-600">34.2%</p>
                  <p className="text-sm text-green-600 flex items-center gap-1 mt-1">
                    <TrendingUp className="w-3 h-3 rotate-180" />
                    -5.7%
                  </p>
                </div>
                <Activity className="w-8 h-8 text-orange-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Översikt</TabsTrigger>
            <TabsTrigger value="users">Användare</TabsTrigger>
            <TabsTrigger value="conversion">Konvertering</TabsTrigger>
            <TabsTrigger value="realtime">Realtid</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Trafik Översikt</CardTitle>
                  <CardDescription>Besökare över tid</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-center">
                    <p className="text-gray-500">Trafikdiagram kommer här</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Top Sidor</CardTitle>
                  <CardDescription>Mest besökta sidor</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
                      <span className="font-medium">/data/properties</span>
                      <Badge>8,532 visningar</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                      <span className="font-medium">/selector-studio</span>
                      <Badge>6,234 visningar</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-purple-50 dark:bg-purple-950 rounded-lg">
                      <span className="font-medium">/analytics</span>
                      <Badge>4,123 visningar</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-orange-50 dark:bg-orange-950 rounded-lg">
                      <span className="font-medium">/proxies</span>
                      <Badge>3,456 visningar</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Geografisk Distribution</CardTitle>
                <CardDescription>Besökare per land</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-48 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">Världskarta med besöksdata kommer här</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Användarsegmentering</CardTitle>
                <CardDescription>Detaljerad användaranalys</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">68%</p>
                    <p className="text-sm text-gray-600">Nya besökare</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">32%</p>
                    <p className="text-sm text-gray-600">Återkommande</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 dark:bg-purple-950 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600">4.2</p>
                    <p className="text-sm text-gray-600">Sidor per session</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="conversion" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Konverteringstrattar</CardTitle>
                <CardDescription>Användarresa och konvertering</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                    <span>Landningsida</span>
                    <Badge>100% (10,000 användare)</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                    <span>Produktsida</span>
                    <Badge>75% (7,500 användare)</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                    <span>Registrering</span>
                    <Badge>45% (4,500 användare)</Badge>
                  </div>
                  <div className="flex items-center justify-between p-4 bg-purple-50 dark:bg-purple-950 rounded-lg">
                    <span>Aktiv användning</span>
                    <Badge>28% (2,800 användare)</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="realtime" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  Live Analytics
                </CardTitle>
                <CardDescription>Realtidsdata för aktiva användare</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="text-center p-6 bg-green-50 dark:bg-green-950 rounded-lg">
                    <p className="text-4xl font-bold text-green-600 mb-2">247</p>
                    <p className="text-gray-600">Aktiva användare nu</p>
                  </div>
                  <div className="text-center p-6 bg-blue-50 dark:bg-blue-950 rounded-lg">
                    <p className="text-4xl font-bold text-blue-600 mb-2">1,834</p>
                    <p className="text-gray-600">Sidvisningar senaste timmen</p>
                  </div>
                </div>
                
                <div className="mt-6">
                  <h4 className="font-medium mb-4">Aktiva sidor just nu</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-900 rounded">
                      <span>/data/properties</span>
                      <Badge>89 användare</Badge>
                    </div>
                    <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-900 rounded">
                      <span>/selector-studio</span>
                      <Badge>67 användare</Badge>
                    </div>
                    <div className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-900 rounded">
                      <span>/analytics</span>
                      <Badge>45 användare</Badge>
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
