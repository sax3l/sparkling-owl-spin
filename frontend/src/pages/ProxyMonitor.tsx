import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { 
  Globe, 
  Wifi, 
  WifiOff, 
  RefreshCw, 
  Plus, 
  Trash2,
  Activity,
  MapPin,
  Clock,
  Zap
} from 'lucide-react';

const ProxyMonitor = () => {
  const [activeTab, setActiveTab] = useState('pools');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Proxy Monitor</h1>
          <p className="text-muted-foreground">Manage and monitor proxy pools for ethical crawling</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Status
          </Button>
          <Button className="bg-gradient-primary">
            <Plus className="w-4 h-4 mr-2" />
            Add Proxies
          </Button>
        </div>
      </div>

      {/* Pool Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Proxies</p>
                <p className="text-3xl font-bold text-foreground">1,237</p>
                <div className="flex items-center space-x-2 mt-2">
                  <Activity className="w-4 h-4 text-primary" />
                  <span className="text-sm text-primary">847 active</span>
                </div>
              </div>
              <Globe className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className="text-2xl font-bold text-foreground">94.3%</p>
                <Badge className="bg-success/10 text-success border-success/20 mt-2">
                  Excellent
                </Badge>
              </div>
              <Wifi className="w-8 h-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Response</p>
                <p className="text-2xl font-bold text-foreground">1.2s</p>
                <Badge className="bg-success/10 text-success border-success/20 mt-2">
                  Fast
                </Badge>
              </div>
              <Zap className="w-8 h-8 text-accent" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Failed Proxies</p>
                <p className="text-2xl font-bold text-foreground">23</p>
                <Badge className="bg-warning/10 text-warning border-warning/20 mt-2">
                  Monitoring
                </Badge>
              </div>
              <WifiOff className="w-8 h-8 text-warning" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="pools">Proxy Pools</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="geography">Geographic Distribution</TabsTrigger>
          <TabsTrigger value="health">Health Check</TabsTrigger>
        </TabsList>

        <TabsContent value="pools" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Residential Pool */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-success rounded-full" />
                  <span>Residential Pool</span>
                </CardTitle>
                <CardDescription>High-quality residential IPs</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Active Proxies</span>
                    <span className="font-medium text-foreground">847 / 950</span>
                  </div>
                  <Progress value={89.2} className="h-2" />
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Success Rate</p>
                    <p className="font-semibold text-success">96.8%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Avg Speed</p>
                    <p className="font-semibold text-foreground">0.9s</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-sidebar-border">
                  <div className="flex justify-between items-center">
                    <Badge className="bg-success/10 text-success border-success/20">
                      Premium Tier
                    </Badge>
                    <Button size="sm" variant="outline">
                      Manage
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Datacenter Pool */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-primary rounded-full" />
                  <span>Datacenter Pool</span>
                </CardTitle>
                <CardDescription>Fast datacenter proxies</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Active Proxies</span>
                    <span className="font-medium text-foreground">234 / 300</span>
                  </div>
                  <Progress value={78} className="h-2" />
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Success Rate</p>
                    <p className="font-semibold text-primary">92.1%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Avg Speed</p>
                    <p className="font-semibold text-foreground">0.4s</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-sidebar-border">
                  <div className="flex justify-between items-center">
                    <Badge className="bg-primary/10 text-primary border-primary/20">
                      Standard Tier
                    </Badge>
                    <Button size="sm" variant="outline">
                      Manage
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Mobile Pool */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-accent rounded-full" />
                  <span>Mobile Pool</span>
                </CardTitle>
                <CardDescription>Mobile carrier IPs</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Active Proxies</span>
                    <span className="font-medium text-foreground">156 / 200</span>
                  </div>
                  <Progress value={78} className="h-2" />
                </div>

                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Success Rate</p>
                    <p className="font-semibold text-accent">89.7%</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Avg Speed</p>
                    <p className="font-semibold text-foreground">1.8s</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-sidebar-border">
                  <div className="flex justify-between items-center">
                    <Badge className="bg-accent/10 text-accent border-accent/20">
                      Specialty
                    </Badge>
                    <Button size="sm" variant="outline">
                      Manage
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Proxy Activity */}
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle>Recent Proxy Activity</CardTitle>
              <CardDescription>Latest proxy usage and status changes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { ip: '192.168.1.45', location: 'Stockholm, SE', status: 'active', speed: '0.8s', usage: '23 req/min' },
                  { ip: '10.0.0.123', location: 'London, UK', status: 'failed', speed: 'timeout', usage: '0 req/min' },
                  { ip: '172.16.0.89', location: 'Berlin, DE', status: 'active', speed: '1.2s', usage: '18 req/min' },
                  { ip: '198.51.100.42', location: 'Paris, FR', status: 'rotating', speed: '0.9s', usage: '31 req/min' },
                  { ip: '203.0.113.67', location: 'Amsterdam, NL', status: 'active', speed: '0.7s', usage: '27 req/min' }
                ].map((proxy, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-sidebar-accent">
                    <div className="flex items-center space-x-4">
                      <div className={`w-2 h-2 rounded-full ${
                        proxy.status === 'active' ? 'bg-success' :
                        proxy.status === 'failed' ? 'bg-destructive' : 'bg-warning'
                      }`} />
                      <div>
                        <p className="text-sm font-medium text-foreground font-mono">{proxy.ip}</p>
                        <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                          <span className="flex items-center space-x-1">
                            <MapPin className="w-3 h-3" />
                            <span>{proxy.location}</span>
                          </span>
                          <span className="flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>{proxy.speed}</span>
                          </span>
                          <span>{proxy.usage}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant="secondary"
                        className={
                          proxy.status === 'active' 
                            ? 'bg-success/10 text-success border-success/20'
                            : proxy.status === 'failed'
                            ? 'bg-destructive/10 text-destructive border-destructive/20'
                            : 'bg-warning/10 text-warning border-warning/20'
                        }
                      >
                        {proxy.status}
                      </Badge>
                      <Button size="sm" variant="ghost">
                        <Trash2 className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <div className="text-center py-12">
            <Activity className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Performance Analytics</h3>
            <p className="text-muted-foreground">Detailed proxy performance metrics and charts</p>
          </div>
        </TabsContent>

        <TabsContent value="geography" className="space-y-6">
          <div className="text-center py-12">
            <MapPin className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Geographic Distribution</h3>
            <p className="text-muted-foreground">Interactive map showing proxy locations worldwide</p>
          </div>
        </TabsContent>

        <TabsContent value="health" className="space-y-6">
          <div className="text-center py-12">
            <Wifi className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Health Monitoring</h3>
            <p className="text-muted-foreground">Automated health checks and diagnostics for all proxy pools</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ProxyMonitor;