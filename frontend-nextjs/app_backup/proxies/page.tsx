'use client';

import React from 'react';
import Layout from '../../src/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { Shield, CheckCircle, AlertCircle, Clock, Plus, RefreshCw, Activity, Globe, Zap } from "lucide-react";

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
    provider: "ProxyProvider A"
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
    provider: "ProxyProvider B"
  }
];

export default function ProxiesPage() {
  const [activeTab, setActiveTab] = useState("health");

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Proxy-hälsa</h1>
            <p className="text-gray-600 dark:text-gray-400">Övervaka och hantera proxy-servrar</p>
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
                  <p className="text-2xl font-bold text-green-600">1</p>
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
                  <p className="text-2xl font-bold text-yellow-600">1</p>
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
                  <p className="text-2xl font-bold text-red-600">0</p>
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
                  <p className="text-2xl font-bold text-blue-600">107ms</p>
                </div>
                <Zap className="w-8 h-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="health">Hälsostatus</TabsTrigger>
            <TabsTrigger value="performance">Prestanda</TabsTrigger>
            <TabsTrigger value="config">Konfiguration</TabsTrigger>
          </TabsList>

          <TabsContent value="health" className="space-y-6">
            {/* Proxy List */}
            <div className="grid grid-cols-1 gap-4">
              {mockProxies.map((proxy) => (
                <Card key={proxy.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <h3 className="font-semibold text-lg">{proxy.name}</h3>
                          <Badge className={
                            proxy.status === 'active' 
                              ? "text-green-600 bg-green-100 dark:bg-green-900"
                              : "text-yellow-600 bg-yellow-100 dark:bg-yellow-900"
                          }>
                            {proxy.status === 'active' ? (
                              <><CheckCircle className="w-3 h-3 mr-1" />Aktiv</>
                            ) : (
                              <><AlertCircle className="w-3 h-3 mr-1" />Varning</>
                            )}
                          </Badge>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
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
                            <p className="text-2xl font-bold text-purple-600">98.5%</p>
                            <p className="text-xs text-gray-600 dark:text-gray-400">Framgång</p>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2 ml-4">
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
                <CardTitle>Prestandamätningar</CardTitle>
                <CardDescription>Detaljerad analys av proxy-prestanda över tid</CardDescription>
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
                <CardTitle>Proxy-konfiguration</CardTitle>
                <CardDescription>Hantera globala proxy-inställningar</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Rotation Strategi</label>
                    <select className="w-full px-3 py-2 border rounded-lg bg-background">
                      <option value="round-robin">Round Robin</option>
                      <option value="random">Slumpmässig</option>
                      <option value="performance">Bästa Prestanda</option>
                    </select>
                  </div>
                  <Button>Spara Konfiguration</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
