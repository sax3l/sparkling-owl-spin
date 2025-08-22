import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  Calendar, 
  Clock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Users,
  Target,
  BarChart3,
  Activity,
  Settings,
  Plus,
  FileText,
  Database
} from 'lucide-react';

interface ProjectMetrics {
  totalProjects: number;
  activeProjects: number;
  completedToday: number;
  totalDataPoints: number;
  successRate: number;
  avgProcessingTime: number;
}

interface ProjectItem {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed' | 'error';
  progress: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
  owner: string;
  startDate: string;
  estimatedCompletion: string;
  dataCollected: number;
  targetData: number;
  sources: string[];
  lastActivity: string;
}

const ProjectManagement = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'projects' | 'analytics'>('overview');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [priorityFilter, setPriorityFilter] = useState<string>('');

  const [metrics] = useState<ProjectMetrics>({
    totalProjects: 12,
    activeProjects: 8,
    completedToday: 3,
    totalDataPoints: 2847391,
    successRate: 94.2,
    avgProcessingTime: 145
  });

  const [projects] = useState<ProjectItem[]>([
    {
      id: 'proj_001',
      name: 'Fordonsanalys Q3 2024',
      description: 'Omfattande analys av fordonsmarknaden för Q3 2024',
      status: 'active',
      progress: 75,
      priority: 'high',
      owner: 'Anna Svensson',
      startDate: '2024-08-01',
      estimatedCompletion: '2024-08-30',
      dataCollected: 45230,
      targetData: 60000,
      sources: ['Biluppgifter.se', 'Hitta.se'],
      lastActivity: '2024-08-21T09:45:00Z'
    },
    {
      id: 'proj_002',
      name: 'Företagsmappning Stockholm',
      description: 'Kartläggning av företag i Stockholmsområdet',
      status: 'paused',
      progress: 45,
      priority: 'medium',
      owner: 'Erik Johansson',
      startDate: '2024-07-15',
      estimatedCompletion: '2024-09-15',
      dataCollected: 23100,
      targetData: 50000,
      sources: ['Bolagsverket'],
      lastActivity: '2024-08-20T16:20:00Z'
    },
    {
      id: 'proj_003',
      name: 'Kontaktdatabas Q3',
      description: 'Uppdatering av kontaktdatabas för Q3',
      status: 'completed',
      progress: 100,
      priority: 'low',
      owner: 'Maria Andersson',
      startDate: '2024-07-01',
      estimatedCompletion: '2024-08-15',
      dataCollected: 12500,
      targetData: 12500,
      sources: ['Hitta.se'],
      lastActivity: '2024-08-15T14:30:00Z'
    },
    {
      id: 'proj_004',
      name: 'Fastighetsanalys',
      description: 'Datainhämtning för fastighetsmarknadsanalys',
      status: 'error',
      progress: 15,
      priority: 'critical',
      owner: 'Johan Lindberg',
      startDate: '2024-08-10',
      estimatedCompletion: '2024-09-30',
      dataCollected: 1250,
      targetData: 25000,
      sources: ['Hemnet.se', 'Booli.se'],
      lastActivity: '2024-08-21T06:15:00Z'
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success/10 text-success border-success/20';
      case 'paused':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'completed':
        return 'bg-primary/10 text-primary border-primary/20';
      case 'error':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'high':
        return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'medium':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'low':
        return 'bg-muted/10 text-muted-foreground border-muted/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Play className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getRelativeTime = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffMinutes < 60) return `${diffMinutes}m ago`;
    if (diffMinutes < 1440) return `${Math.floor(diffMinutes / 60)}h ago`;
    return `${Math.floor(diffMinutes / 1440)}d ago`;
  };

  const filteredProjects = projects.filter(project => {
    const matchesStatus = !statusFilter || project.status === statusFilter;
    const matchesPriority = !priorityFilter || project.priority === priorityFilter;
    return matchesStatus && matchesPriority;
  });

  const renderOverview = () => (
    <div className="space-y-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Totalt projekt</p>
                <p className="text-2xl font-bold text-foreground">{metrics.totalProjects}</p>
              </div>
              <FileText className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Aktiva projekt</p>
                <p className="text-2xl font-bold text-foreground">{metrics.activeProjects}</p>
              </div>
              <Activity className="w-8 h-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Slutförda idag</p>
                <p className="text-2xl font-bold text-foreground">{metrics.completedToday}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Framgångsgrad</p>
                <p className="text-2xl font-bold text-foreground">{metrics.successRate}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-success" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Projects */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle>Senaste projektaktivitet</CardTitle>
          <CardDescription>Översikt av pågående och senaste projekt</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {projects.slice(0, 5).map((project) => (
              <div key={project.id} className="flex items-center justify-between p-3 border border-sidebar-border rounded">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(project.status)}
                  <div>
                    <p className="font-medium text-foreground">{project.name}</p>
                    <p className="text-sm text-muted-foreground">{project.owner}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-foreground">{project.progress}%</p>
                    <p className="text-xs text-muted-foreground">{getRelativeTime(project.lastActivity)}</p>
                  </div>
                  <Progress value={project.progress} className="w-20" />
                  <Badge className={getStatusColor(project.status)}>
                    {project.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Performance Chart Placeholder */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle>Projektprestanda</CardTitle>
          <CardDescription>Datainhämtning och framsteg över tid</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-muted/20 rounded flex items-center justify-center">
            <div className="text-center">
              <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-muted-foreground">Prestandadiagram kommer här</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderProjects = () => (
    <div className="space-y-6">
      {/* Filters */}
      <Card className="border-sidebar-border">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Status</Label>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Alla statusar" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Alla statusar</SelectItem>
                  <SelectItem value="active">Aktiv</SelectItem>
                  <SelectItem value="paused">Pausad</SelectItem>
                  <SelectItem value="completed">Slutförd</SelectItem>
                  <SelectItem value="error">Fel</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Prioritet</Label>
              <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Alla prioriteter" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Alla prioriteter</SelectItem>
                  <SelectItem value="critical">Kritisk</SelectItem>
                  <SelectItem value="high">Hög</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Låg</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Ägare</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Alla ägare" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Alla ägare</SelectItem>
                  <SelectItem value="anna">Anna Svensson</SelectItem>
                  <SelectItem value="erik">Erik Johansson</SelectItem>
                  <SelectItem value="maria">Maria Andersson</SelectItem>
                  <SelectItem value="johan">Johan Lindberg</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Project List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {filteredProjects.map((project) => (
          <Card key={project.id} className="border-sidebar-border">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CardTitle className="text-base">{project.name}</CardTitle>
                  <Badge className={getPriorityColor(project.priority)}>
                    {project.priority}
                  </Badge>
                </div>
                <Badge className={getStatusColor(project.status)}>
                  {getStatusIcon(project.status)}
                  <span className="ml-1">{project.status}</span>
                </Badge>
              </div>
              <CardDescription>{project.description}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Framsteg</span>
                  <span className="text-foreground font-medium">{project.progress}%</span>
                </div>
                <Progress value={project.progress} className="h-2" />
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground block">Ägare</span>
                  <span className="text-foreground">{project.owner}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Slutförs</span>
                  <span className="text-foreground">
                    {new Date(project.estimatedCompletion).toLocaleDateString('sv-SE')}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground block">Data samlade</span>
                  <span className="text-foreground">{project.dataCollected.toLocaleString()}</span>
                </div>
                <div>
                  <span className="text-muted-foreground block">Mål</span>
                  <span className="text-foreground">{project.targetData.toLocaleString()}</span>
                </div>
              </div>

              <div>
                <span className="text-muted-foreground text-sm block mb-1">Källor</span>
                <div className="flex flex-wrap gap-1">
                  {project.sources.map((source) => (
                    <Badge key={source} variant="outline" className="text-xs">
                      {source}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-sidebar-border">
                <span className="text-xs text-muted-foreground">
                  Senaste aktivitet: {getRelativeTime(project.lastActivity)}
                </span>
                <div className="flex space-x-1">
                  {project.status === 'active' ? (
                    <Button variant="outline" size="sm">
                      <Pause className="w-3 h-3" />
                    </Button>
                  ) : project.status === 'paused' ? (
                    <Button variant="outline" size="sm">
                      <Play className="w-3 h-3" />
                    </Button>
                  ) : null}
                  <Button variant="outline" size="sm">
                    <Settings className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <Card className="border-sidebar-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Datapunkter totalt</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-foreground">{metrics.totalDataPoints.toLocaleString()}</p>
            <p className="text-sm text-muted-foreground mt-1">Sedan projektstart</p>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Genomsnittlig processtid</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-foreground">{metrics.avgProcessingTime}s</p>
            <p className="text-sm text-muted-foreground mt-1">Per datapunkt</p>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Felfrekvens</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-foreground">{(100 - metrics.successRate).toFixed(1)}%</p>
            <p className="text-sm text-muted-foreground mt-1">Av totala försök</p>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="text-base">Datainhämtning över tid</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 bg-muted/20 rounded flex items-center justify-center">
              <div className="text-center">
                <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Tidsseriesdiagram kommer här</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="text-base">Projektstatus fördelning</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 bg-muted/20 rounded flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-muted-foreground">Cirkeldiagram kommer här</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Projektstyrning</h1>
          <p className="text-muted-foreground">Hantera och övervaka datainsamlingsprojekt</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Nytt projekt
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
        <TabsList>
          <TabsTrigger value="overview">Översikt</TabsTrigger>
          <TabsTrigger value="projects">Projekt</TabsTrigger>
          <TabsTrigger value="analytics">Analys</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="mt-6">
          {renderOverview()}
        </TabsContent>

        <TabsContent value="projects" className="mt-6">
          {renderProjects()}
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          {renderAnalytics()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ProjectManagement;
