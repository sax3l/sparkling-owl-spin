'use client';

import React from 'react';
import Layout from '../../src/components/Layout';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useState } from "react";
import { Target, Code, Play, Save, Eye } from "lucide-react";

export default function SelectorStudioPage() {
  const [selectedElement, setSelectedElement] = useState("div.product-card");
  const [generatedSelector, setGeneratedSelector] = useState("div.product-card .price");

  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Selector Studio</h1>
            <p className="text-gray-600 dark:text-gray-400">Visual selector builder och CSS/XPath generator</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Eye className="w-4 h-4 mr-2" />
              Preview
            </Button>
            <Button size="sm">
              <Save className="w-4 h-4 mr-2" />
              Spara Mall
            </Button>
          </div>
        </div>

        <Tabs defaultValue="builder" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="builder">Visual Builder</TabsTrigger>
            <TabsTrigger value="testing">Testning</TabsTrigger>
            <TabsTrigger value="library">Bibliotek</TabsTrigger>
          </TabsList>

          <TabsContent value="builder" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Element Inspector */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Element Inspector
                  </CardTitle>
                  <CardDescription>
                    Inspektera DOM-element och generera selektorer
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="p-3 border rounded-lg bg-blue-50 dark:bg-blue-950 border-blue-200">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary">div</Badge>
                        <Badge variant="outline">.product-card</Badge>
                        <Badge variant="outline">.featured</Badge>
                      </div>
                      <p className="text-sm text-gray-600">iPhone 15 Pro Max 256GB - Space Black</p>
                    </div>
                    <div className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary">span</Badge>
                        <Badge variant="outline">.price</Badge>
                      </div>
                      <p className="text-sm text-gray-600">12,995 kr</p>
                    </div>
                    <div className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary">a</Badge>
                        <Badge variant="outline">.btn</Badge>
                      </div>
                      <p className="text-sm text-gray-600">Visa produkt</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Selector Generator */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code className="w-5 h-5" />
                    Genererad Selektor
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-2 block">Strategy</label>
                    <select className="w-full px-3 py-2 border rounded-lg bg-background">
                      <option value="css">CSS Selector</option>
                      <option value="xpath">XPath</option>
                      <option value="data">Data Attributes</option>
                    </select>
                  </div>

                  <div>
                    <label className="text-sm font-medium mb-2 block">Genererad Selektor</label>
                    <Input 
                      value={generatedSelector}
                      onChange={(e) => setGeneratedSelector(e.target.value)}
                      className="font-mono text-sm"
                    />
                  </div>

                  <Button onClick={() => {}} className="w-full">
                    <Play className="w-4 h-4 mr-2" />
                    Testa Selektor
                  </Button>

                  <div className="p-3 rounded-lg border border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-sm font-medium text-green-600">✓ Hittade 3 element</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="testing" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Selektor Testning</CardTitle>
                <CardDescription>Testa dina selektorer mot live DOM</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Input placeholder="Test URL: https://example.com" />
                  <Input placeholder="CSS Selector eller XPath" className="font-mono" />
                  <Button>
                    <Play className="w-4 h-4 mr-2" />
                    Kör Test
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="library" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Sparade Selektorer</CardTitle>
                <CardDescription>Ditt bibliotek av testade selektorer</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-8 text-gray-500">
                  <Target className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Inga sparade selektorer än</p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
}
