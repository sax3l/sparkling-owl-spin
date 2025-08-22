import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Play, 
  Pause, 
  Square, 
  Settings, 
  FileText, 
  Globe, 
  Clock, 
  Target,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';

const JobLauncher = () => {
  const [activeTab, setActiveTab] = useState('new');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Job Launcher</h1>
          <p className="text-muted-foreground">Create and manage crawling jobs</p>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="new">New Job</TabsTrigger>
          <TabsTrigger value="running">Running Jobs</TabsTrigger>
          <TabsTrigger value="history">Job History</TabsTrigger>
        </TabsList>

        <TabsContent value="new" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Job Configuration */}
            <div className="lg:col-span-2 space-y-6">
              <Card className="border-sidebar-border">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Settings className="w-5 h-5 text-primary" />
                    <span>Job Configuration</span>
                  </CardTitle>
                  <CardDescription>Configure your crawling job parameters</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="jobName">Job Name</Label>
                      <Input id="jobName" placeholder="e.g., biluppgifter_vehicles_2024" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="template">Template</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select template" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="biluppgifter">biluppgifter.se - Vehicles</SelectItem>
                          <SelectItem value="carinfo">car.info - Listings</SelectItem>
                          <SelectItem value="hitta">hitta.se - Business</SelectItem>
                          <SelectItem value="blocket">Blocket - Marketplace</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="startUrl">Start URL(s)</Label>
                    <Textarea 
                      id="startUrl" 
                      placeholder="https://biluppgifter.se/search&#10;https://car.info/listings"
                      rows={3}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="maxPages">Max Pages</Label>
                      <Input id="maxPages" type="number" placeholder="1000" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="delay">Delay (ms)</Label>
                      <Input id="delay" type="number" placeholder="2000" />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="concurrent">Concurrent</Label>
                      <Input id="concurrent" type="number" placeholder="3" />
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-sidebar-border">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Globe className="w-5 h-5 text-accent" />
                    <span>Proxy & Ethics Settings</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="proxyPool">Proxy Pool</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select proxy pool" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="residential">Residential Pool (847 active)</SelectItem>
                          <SelectItem value="datacenter">Datacenter Pool (234 active)</SelectItem>
                          <SelectItem value="mobile">Mobile Pool (156 active)</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="rotation">Rotation Strategy</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select rotation" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="round-robin">Round Robin</SelectItem>
                          <SelectItem value="random">Random</SelectItem>
                          <SelectItem value="sticky">Sticky Session</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 p-4 bg-success/5 border border-success/20 rounded-lg">
                    <CheckCircle2 className="w-5 h-5 text-success" />
                    <div>
                      <p className="text-sm font-medium text-success">Ethics Compliance Enabled</p>
                      <p className="text-xs text-muted-foreground">robots.txt respected, rate limits enforced</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Job Preview & Launch */}
            <div className="space-y-6">
              <Card className="border-sidebar-border">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Target className="w-5 h-5 text-warning" />
                    <span>Launch Control</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Estimated Duration</span>
                      <span className="text-foreground">2-4 hours</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Expected Records</span>
                      <span className="text-foreground">~15,000</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Resource Usage</span>
                      <Badge variant="secondary" className="bg-warning/10 text-warning border-warning/20">
                        Medium
                      </Badge>
                    </div>
                  </div>

                  <Button className="w-full bg-gradient-primary">
                    <Play className="w-4 h-4 mr-2" />
                    Launch Crawling Job
                  </Button>

                  <div className="pt-4 border-t border-sidebar-border">
                    <p className="text-xs text-muted-foreground">
                      This job will be queued and executed according to available resources and ethical guidelines.
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-sidebar-border">
                <CardHeader>
                  <CardTitle className="text-sm">Quick Templates</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {[
                    { name: 'Vehicle Registry', sites: 'biluppgifter.se', status: 'ready' },
                    { name: 'Business Directory', sites: 'hitta.se', status: 'ready' },
                    { name: 'Car Listings', sites: 'car.info', status: 'ready' },
                    { name: 'Marketplace Items', sites: 'blocket.se', status: 'maintenance' }
                  ].map((template, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-sidebar-accent">
                      <div>
                        <p className="text-sm font-medium text-foreground">{template.name}</p>
                        <p className="text-xs text-muted-foreground">{template.sites}</p>
                      </div>
                      <Badge 
                        variant="secondary" 
                        className={
                          template.status === 'ready' 
                            ? 'bg-success/10 text-success border-success/20'
                            : 'bg-warning/10 text-warning border-warning/20'
                        }
                      >
                        {template.status}
                      </Badge>
                    </div>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="running" className="space-y-6">
          <div className="grid grid-cols-1 gap-6">
            {[
              {
                id: 'job-001',
                name: 'biluppgifter_vehicles_daily',
                status: 'running',
                progress: 67,
                pages: '2,341 / 3,500',
                records: '15,623',
                runtime: '2h 14m',
                template: 'biluppgifter.se'
              },
              {
                id: 'job-002', 
                name: 'hitta_business_update',
                status: 'queued',
                progress: 0,
                pages: '0 / 1,200',
                records: '0',
                runtime: 'Waiting',
                template: 'hitta.se'
              },
              {
                id: 'job-003',
                name: 'car_listings_refresh',
                status: 'paused',
                progress: 23,
                pages: '456 / 2,000',
                records: '3,244',
                runtime: '45m (paused)',
                template: 'car.info'
              }
            ].map((job) => (
              <Card key={job.id} className="border-sidebar-border">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-semibold text-foreground">{job.name}</h3>
                      <p className="text-sm text-muted-foreground">Template: {job.template}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge 
                        variant="secondary"
                        className={
                          job.status === 'running' 
                            ? 'bg-success/10 text-success border-success/20'
                            : job.status === 'queued'
                            ? 'bg-primary/10 text-primary border-primary/20'
                            : 'bg-warning/10 text-warning border-warning/20'
                        }
                      >
                        {job.status}
                      </Badge>
                      <div className="flex space-x-1">
                        <Button size="sm" variant="outline">
                          {job.status === 'running' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </Button>
                        <Button size="sm" variant="outline">
                          <Square className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">Progress</span>
                        <span className="text-sm text-foreground">{job.progress}%</span>
                      </div>
                      <Progress value={job.progress} className="h-2" />
                    </div>

                    <div className="grid grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Pages</span>
                        <p className="font-medium text-foreground">{job.pages}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Records</span>
                        <p className="font-medium text-foreground">{job.records}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Runtime</span>
                        <p className="font-medium text-foreground">{job.runtime}</p>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Status</span>
                        <p className="font-medium text-foreground capitalize">{job.status}</p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="history" className="space-y-6">
          <div className="text-center py-12">
            <Clock className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Job History</h3>
            <p className="text-muted-foreground">Previous crawling jobs and their results will appear here</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default JobLauncher;