import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Activity,
  Globe,
  Database,
  TrendingUp,
  Server,
  Zap,
  Play,
  RotateCcw,
  FileText,
  Download
} from 'lucide-react';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Platform Overview</h1>
          <p className="text-muted-foreground">Monitor your ethical data collection operations</p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" size="sm">
            <RotateCcw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button size="sm" className="gradient-primary">
            <Play className="w-4 h-4 mr-2" />
            Quick Launch
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="border-sidebar-border">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">Active Crawlers</CardTitle>
              <Activity className="w-4 h-4 text-success" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">12</div>
            <div className="flex items-center space-x-2 mt-2">
              <Badge variant="secondary" className="bg-success/10 text-success border-success/20">
                +3 from yesterday
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">Data Points</CardTitle>
              <Database className="w-4 h-4 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">2.3M</div>
            <div className="flex items-center space-x-2 mt-2">
              <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                +15.2% growth
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">Proxy Pool</CardTitle>
              <Globe className="w-4 h-4 text-accent" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">847</div>
            <div className="flex items-center space-x-2 mt-2">
              <Badge variant="secondary" className="bg-accent/10 text-accent border-accent/20">
                98.3% healthy
              </Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
              <TrendingUp className="w-4 h-4 text-warning" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">94.7%</div>
            <div className="flex items-center space-x-2 mt-2">
              <Badge variant="secondary" className="bg-warning/10 text-warning border-warning/20">
                Target: 95%
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Status & Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="w-5 h-5 text-primary" />
              <span>System Status</span>
            </CardTitle>
            <CardDescription>Real-time platform health monitoring</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">API Server</span>
                <Badge className="bg-success/10 text-success border-success/20">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Database</span>
                <Badge className="bg-success/10 text-success border-success/20">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Proxy Manager</span>
                <Badge className="bg-success/10 text-success border-success/20">Active</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Queue Processing</span>
                <Badge className="bg-warning/10 text-warning border-warning/20">Busy</Badge>
              </div>
            </div>
            
            <div className="pt-4 border-t border-sidebar-border">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-foreground">CPU Usage</span>
                <span className="text-sm text-muted-foreground">34%</span>
              </div>
              <Progress value={34} className="h-2" />
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-foreground">Memory Usage</span>
                <span className="text-sm text-muted-foreground">67%</span>
              </div>
              <Progress value={67} className="h-2" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-accent" />
              <span>Recent Activity</span>
            </CardTitle>
            <CardDescription>Latest platform events and jobs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { time: '2m ago', action: 'Crawler job completed', target: 'biluppgifter.se', status: 'success' },
                { time: '5m ago', action: 'New proxy batch added', target: '50 proxies', status: 'info' },
                { time: '12m ago', action: 'Template updated', target: 'car_listings.yaml', status: 'info' },
                { time: '18m ago', action: 'Rate limit triggered', target: 'hitta.se', status: 'warning' },
                { time: '25m ago', action: 'Data export generated', target: 'vehicles_Q3.csv', status: 'success' },
              ].map((activity, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 rounded-lg bg-sidebar-accent">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-success' :
                    activity.status === 'warning' ? 'bg-warning' : 'bg-primary'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {activity.action}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {activity.target} • {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-warning" />
            <span>Quick Actions</span>
          </CardTitle>
          <CardDescription>Frequently used platform operations</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <Play className="w-6 h-6" />
              <span>Launch New Job</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <FileText className="w-6 h-6" />
              <span>Create Template</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <Download className="w-6 h-6" />
              <span>Export Data</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
