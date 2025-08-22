import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { 
  Plus, 
  Search, 
  Settings, 
  Play, 
  Pause, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Globe,
  Eye,
  MoreHorizontal,
  Activity,
  TrendingUp,
  Zap,
  Database,
  Calendar,
  ExternalLink
} from 'lucide-react';

interface Source {
  id: string;
  name: string;
  url: string;
  type: 'web' | 'api' | 'feed';
  status: 'active' | 'paused' | 'error' | 'unknown';
  templates: string[];
  lastCrawl: string;
  nextCrawl: string;
  totalItems: number;
  errorRate: number;
  description?: string;
}

interface Project {
  id: string;
  name: string;
  description: string;
  sources: string[];
  templates: string[];
  status: 'active' | 'completed' | 'paused';
  createdAt: string;
  lastActivity: string;
  totalItems: number;
}

const SourcesProjects = () => {
  const [activeTab, setActiveTab] = useState<'sources' | 'projects'>('sources');
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [selectedItem, setSelectedItem] = useState<Source | Project | null>(null);
  const [showNewSourceDialog, setShowNewSourceDialog] = useState(false);
  const [showNewProjectDialog, setShowNewProjectDialog] = useState(false);

  // Mock data for sources
  const [sources, setSources] = useState<Source[]>([
    {
      id: 'src_001',
      name: 'Biluppgifter.se',
      url: 'https://biluppgifter.se',
      type: 'web',
      status: 'active',
      templates: ['vehicle_detail_v1', 'vehicle_list_v1'],
      lastCrawl: '2024-08-21T09:45:00Z',
      nextCrawl: '2024-08-21T15:45:00Z',
      totalItems: 15420,
      errorRate: 2.1,
      description: 'Svenska fordonsregisterdata'
    },
    {
      id: 'src_002',
      name: 'Hitta.se Personer',
      url: 'https://hitta.se',
      type: 'web',
      status: 'active',
      templates: ['person_profile_v1', 'person_profile_v2'],
      lastCrawl: '2024-08-21T08:30:00Z',
      nextCrawl: '2024-08-21T14:30:00Z',
      totalItems: 8934,
      errorRate: 1.5,
      description: 'Personuppgifter och kontaktinformation'
    },
    {
      id: 'src_003',
      name: 'Bolagsverket API',
      url: 'https://api.bolagsverket.se',
      type: 'api',
      status: 'error',
      templates: ['company_profile_v1'],
      lastCrawl: '2024-08-21T06:15:00Z',
      nextCrawl: '2024-08-21T12:15:00Z',
      totalItems: 3421,
      errorRate: 15.2,
      description: 'Företagsinformation från Bolagsverket'
    }
  ]);

  // Mock data for projects
  const [projects, setProjects] = useState<Project[]>([
    {
      id: 'proj_001',
      name: 'Fordonsanalys Q3 2024',
      description: 'Omfattande analys av fordonsmarknaden för Q3 2024',
      sources: ['src_001', 'src_002'],
      templates: ['vehicle_detail_v1', 'owner_profile_v1'],
      status: 'active',
      createdAt: '2024-08-01T10:00:00Z',
      lastActivity: '2024-08-21T09:45:00Z',
      totalItems: 24354
    },
    {
      id: 'proj_002',
      name: 'Företagsmappning Stockholm',
      description: 'Kartläggning av företag i Stockholmsområdet',
      sources: ['src_003'],
      templates: ['company_profile_v1'],
      status: 'paused',
      createdAt: '2024-07-15T14:30:00Z',
      lastActivity: '2024-08-20T16:20:00Z',
      totalItems: 3421
    }
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-success/10 text-success border-success/20';
      case 'paused':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'error':
        return 'bg-destructive/10 text-destructive border-destructive/20';
      case 'completed':
        return 'bg-primary/10 text-primary border-primary/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4" />;
      case 'paused':
        return <Pause className="w-4 h-4" />;
      case 'error':
        return <AlertTriangle className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
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

  const renderSourceCard = (source: Source) => (
    <Card key={source.id} className="border-sidebar-border cursor-pointer hover:shadow-md" onClick={() => setSelectedItem(source)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {source.type === 'web' && <Globe className="w-4 h-4 text-muted-foreground" />}
            {source.type === 'api' && <Zap className="w-4 h-4 text-muted-foreground" />}
            {source.type === 'feed' && <Database className="w-4 h-4 text-muted-foreground" />}
            <CardTitle className="text-base">{source.name}</CardTitle>
          </div>
          <Badge className={getStatusColor(source.status)}>
            {getStatusIcon(source.status)}
            <span className="ml-1">{source.status}</span>
          </Badge>
        </div>
        <CardDescription>{source.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">URL:</span>
            <span className="text-foreground truncate max-w-48">{source.url}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Senaste crawl:</span>
            <span className="text-foreground">{getRelativeTime(source.lastCrawl)}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Totalt items:</span>
            <span className="text-foreground">{source.totalItems.toLocaleString()}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Felfrekvens:</span>
            <span className={`${source.errorRate > 10 ? 'text-destructive' : source.errorRate > 5 ? 'text-warning' : 'text-success'}`}>
              {source.errorRate}%
            </span>
          </div>
          <div className="flex flex-wrap gap-1 mt-2">
            {source.templates.map((template) => (
              <Badge key={template} variant="outline" className="text-xs">
                {template}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderProjectCard = (project: Project) => (
    <Card key={project.id} className="border-sidebar-border cursor-pointer hover:shadow-md" onClick={() => setSelectedItem(project)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">{project.name}</CardTitle>
          <Badge className={getStatusColor(project.status)}>
            {getStatusIcon(project.status)}
            <span className="ml-1">{project.status}</span>
          </Badge>
        </div>
        <CardDescription>{project.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Källor:</span>
            <span className="text-foreground">{project.sources.length}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Skapad:</span>
            <span className="text-foreground">{getRelativeTime(project.createdAt)}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Senaste aktivitet:</span>
            <span className="text-foreground">{getRelativeTime(project.lastActivity)}</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Totalt items:</span>
            <span className="text-foreground">{project.totalItems.toLocaleString()}</span>
          </div>
          <div className="flex flex-wrap gap-1 mt-2">
            {project.templates.map((template) => (
              <Badge key={template} variant="outline" className="text-xs">
                {template}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const renderDetailPanel = () => {
    if (!selectedItem) return null;

    const isSource = 'url' in selectedItem;
    const item = selectedItem as Source | Project;

    return (
      <div className="w-80 border-l border-sidebar-border bg-background">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground">
              {isSource ? 'Källdetaljer' : 'Projektdetaljer'}
            </h3>
            <Button variant="ghost" size="sm" onClick={() => setSelectedItem(null)}>
              ×
            </Button>
          </div>

          <div className="space-y-4">
            <div>
              <Label className="text-xs text-muted-foreground">Namn</Label>
              <p className="text-sm text-foreground">{item.name}</p>
            </div>

            {isSource && (
              <>
                <div>
                  <Label className="text-xs text-muted-foreground">URL</Label>
                  <div className="flex items-center space-x-2">
                    <p className="text-sm text-foreground truncate flex-1">{(item as Source).url}</p>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => window.open((item as Source).url, '_blank')}
                    >
                      <ExternalLink className="w-3 h-3" />
                    </Button>
                  </div>
                </div>

                <div>
                  <Label className="text-xs text-muted-foreground">Typ</Label>
                  <p className="text-sm text-foreground capitalize">{(item as Source).type}</p>
                </div>

                <div>
                  <Label className="text-xs text-muted-foreground">Nästa crawl</Label>
                  <p className="text-sm text-foreground">
                    {new Date((item as Source).nextCrawl).toLocaleString('sv-SE')}
                  </p>
                </div>
              </>
            )}

            {!isSource && (
              <>
                <div>
                  <Label className="text-xs text-muted-foreground">Beskrivning</Label>
                  <p className="text-sm text-foreground">{(item as Project).description}</p>
                </div>

                <div>
                  <Label className="text-xs text-muted-foreground">Källor</Label>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {(item as Project).sources.map((sourceId) => {
                      const source = sources.find(s => s.id === sourceId);
                      return (
                        <Badge key={sourceId} variant="outline" className="text-xs">
                          {source?.name || sourceId}
                        </Badge>
                      );
                    })}
                  </div>
                </div>
              </>
            )}

            <div>
              <Label className="text-xs text-muted-foreground">Mallar</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {('templates' in item ? item.templates : []).map((template) => (
                  <Badge key={template} variant="outline" className="text-xs">
                    {template}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="border-t border-sidebar-border pt-4 space-y-2">
              {isSource ? (
                <>
                  <Button variant="outline" size="sm" className="w-full">
                    <Play className="w-4 h-4 mr-2" />
                    Kör crawl nu
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    <Settings className="w-4 h-4 mr-2" />
                    Redigera källa
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    <Activity className="w-4 h-4 mr-2" />
                    Visa diagnostik
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="outline" size="sm" className="w-full">
                    <Play className="w-4 h-4 mr-2" />
                    Starta projekt
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    <Settings className="w-4 h-4 mr-2" />
                    Redigera projekt
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    <TrendingUp className="w-4 h-4 mr-2" />
                    Visa statistik
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const filteredSources = sources.filter(source => {
    const matchesSearch = !searchQuery || 
      source.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      source.url.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || source.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const filteredProjects = projects.filter(project => {
    const matchesSearch = !searchQuery || 
      project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = !statusFilter || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="flex h-screen">
      <div className="flex-1 space-y-6 p-6 overflow-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Källor & Projekt</h1>
            <p className="text-muted-foreground">Hantera datakällor och crawling-projekt</p>
          </div>
          <div className="flex items-center space-x-3">
            {activeTab === 'sources' ? (
              <Button onClick={() => setShowNewSourceDialog(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Ny källa
              </Button>
            ) : (
              <Button onClick={() => setShowNewProjectDialog(true)}>
                <Plus className="w-4 h-4 mr-2" />
                Nytt projekt
              </Button>
            )}
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'sources' | 'projects')}>
          <TabsList>
            <TabsTrigger value="sources">Källor</TabsTrigger>
            <TabsTrigger value="projects">Projekt</TabsTrigger>
          </TabsList>

          {/* Filters */}
          <Card className="border-sidebar-border mt-4">
            <CardContent className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="search">Sök</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="search"
                      placeholder={activeTab === 'sources' ? 'Sök källor...' : 'Sök projekt...'}
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                </div>

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
                      <SelectItem value="error">Fel</SelectItem>
                      {activeTab === 'projects' && (
                        <SelectItem value="completed">Slutförd</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Typ</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Alla typer" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">Alla typer</SelectItem>
                      {activeTab === 'sources' ? (
                        <>
                          <SelectItem value="web">Webb</SelectItem>
                          <SelectItem value="api">API</SelectItem>
                          <SelectItem value="feed">Feed</SelectItem>
                        </>
                      ) : (
                        <>
                          <SelectItem value="research">Forskning</SelectItem>
                          <SelectItem value="monitoring">Övervakning</SelectItem>
                          <SelectItem value="analysis">Analys</SelectItem>
                        </>
                      )}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <TabsContent value="sources">
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
              {filteredSources.map(renderSourceCard)}
            </div>
          </TabsContent>

          <TabsContent value="projects">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {filteredProjects.map(renderProjectCard)}
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Detail panel */}
      {renderDetailPanel()}
    </div>
  );
};

export default SourcesProjects;
