import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { 
  Search, 
  Filter, 
  Download, 
  Trash2, 
  Eye, 
  Flag,
  Copy,
  Calendar,
  Database,
  FileSpreadsheet,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Grid,
  List,
  ExternalLink
} from 'lucide-react';

interface DataItem {
  id: string;
  templateName: string;
  templateVersion: string;
  status: 'validated' | 'quarantine' | 'tombstone';
  createdAt: string;
  preview: Record<string, any>;
  jobId: string;
  url: string;
}

const DataWarehouse = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSources, setSelectedSources] = useState<string[]>([]);
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>([]);
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>(['validated']);
  const [dateRange, setDateRange] = useState('24h');
  const [viewMode, setViewMode] = useState<'table' | 'cards'>('table');
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  const [selectedItem, setSelectedItem] = useState<DataItem | null>(null);
  const [sidebarTab, setSidebarTab] = useState<'lineage' | 'dq'>('lineage');

  // Mock data
  const [items, setItems] = useState<DataItem[]>([
    {
      id: 'it_123456',
      templateName: 'vehicle_detail_v1',
      templateVersion: 'v2.1',
      status: 'validated',
      createdAt: '2024-08-21T09:45:00Z',
      preview: {
        reg_number: 'ABC123',
        make: 'Volvo',
        model: 'XC90',
        year: 2022
      },
      jobId: 'job_901',
      url: 'https://biluppgifter.se/detalj/abc123'
    },
    {
      id: 'it_123457',
      templateName: 'vehicle_detail_v1',
      templateVersion: 'v2.1',
      status: 'quarantine',
      createdAt: '2024-08-21T09:30:00Z',
      preview: {
        reg_number: 'XYZ789',
        make: 'BMW',
        model: '',
        year: null
      },
      jobId: 'job_902',
      url: 'https://biluppgifter.se/detalj/xyz789'
    },
    {
      id: 'it_123458',
      templateName: 'owner_profile_v2',
      templateVersion: 'v1.3',
      status: 'validated',
      createdAt: '2024-08-21T09:15:00Z',
      preview: {
        name: 'Erik Andersson',
        address: 'Stockholm',
        phone: '+46701234567'
      },
      jobId: 'job_903',
      url: 'https://hitta.se/person/erik-andersson'
    }
  ]);

  const sources = ['Biluppgifter.se', 'Hitta.se', 'Bolagsverket', 'UC'];
  const templates = ['vehicle_detail_v1', 'owner_profile_v2', 'company_profile_v1'];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'validated':
        return 'bg-success/10 text-success border-success/20';
      case 'quarantine':
        return 'bg-warning/10 text-warning border-warning/20';
      case 'tombstone':
        return 'bg-muted/10 text-muted-foreground border-muted/20';
      default:
        return 'bg-muted/10 text-muted-foreground border-muted/20';
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

  const filteredItems = items.filter(item => {
    const matchesSearch = !searchQuery || 
      Object.values(item.preview).some(value => 
        String(value).toLowerCase().includes(searchQuery.toLowerCase())
      ) ||
      item.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.url.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesStatus = selectedStatuses.length === 0 || selectedStatuses.includes(item.status);
    const matchesTemplate = selectedTemplates.length === 0 || selectedTemplates.includes(item.templateName);
    
    return matchesSearch && matchesStatus && matchesTemplate;
  });

  const totalPages = Math.ceil(filteredItems.length / itemsPerPage);
  const paginatedItems = filteredItems.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const handleSelectItem = (itemId: string) => {
    setSelectedItems(prev => 
      prev.includes(itemId) 
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const handleSelectAll = () => {
    if (selectedItems.length === paginatedItems.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(paginatedItems.map(item => item.id));
    }
  };

  const renderTableView = () => (
    <div className="border border-sidebar-border rounded-lg">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="border-b border-sidebar-border bg-sidebar-accent">
            <tr>
              <th className="w-12 p-3">
                <Checkbox
                  checked={selectedItems.length === paginatedItems.length && paginatedItems.length > 0}
                  onCheckedChange={handleSelectAll}
                />
              </th>
              <th className="text-left p-3 font-medium text-foreground">ID</th>
              <th className="text-left p-3 font-medium text-foreground">Mall</th>
              <th className="text-left p-3 font-medium text-foreground">Förhandsvisning</th>
              <th className="text-left p-3 font-medium text-foreground">Status</th>
              <th className="text-left p-3 font-medium text-foreground">Skapad</th>
              <th className="w-12 p-3"></th>
            </tr>
          </thead>
          <tbody>
            {paginatedItems.map((item) => (
              <tr 
                key={item.id} 
                className="border-b border-sidebar-border hover:bg-sidebar-accent cursor-pointer"
                onClick={() => setSelectedItem(item)}
              >
                <td className="p-3" onClick={(e) => e.stopPropagation()}>
                  <Checkbox
                    checked={selectedItems.includes(item.id)}
                    onCheckedChange={() => handleSelectItem(item.id)}
                  />
                </td>
                <td className="p-3">
                  <div className="flex items-center space-x-2">
                    <code className="text-sm bg-muted px-2 py-1 rounded">{item.id}</code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(item.id);
                      }}
                    >
                      <Copy className="w-3 h-3" />
                    </Button>
                  </div>
                </td>
                <td className="p-3">
                  <div>
                    <span className="font-medium text-foreground">{item.templateName}</span>
                    <Badge variant="outline" className="ml-2 text-xs">
                      {item.templateVersion}
                    </Badge>
                  </div>
                </td>
                <td className="p-3">
                  <div className="space-y-1">
                    {Object.entries(item.preview).slice(0, 3).map(([key, value]) => (
                      <div key={key} className="text-sm">
                        <span className="text-muted-foreground">{key}:</span>
                        <span className="ml-1 text-foreground">
                          {value || <span className="text-muted-foreground italic">tom</span>}
                        </span>
                      </div>
                    ))}
                  </div>
                </td>
                <td className="p-3">
                  <Badge className={getStatusColor(item.status)}>
                    {item.status}
                  </Badge>
                </td>
                <td className="p-3">
                  <div className="text-sm">
                    <div className="text-foreground">{getRelativeTime(item.createdAt)}</div>
                    <div className="text-muted-foreground text-xs">
                      {new Date(item.createdAt).toLocaleString('sv-SE')}
                    </div>
                  </div>
                </td>
                <td className="p-3" onClick={(e) => e.stopPropagation()}>
                  <Button variant="ghost" size="sm">
                    <MoreHorizontal className="w-4 h-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderCardView = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {paginatedItems.map((item) => (
        <Card key={item.id} className="border-sidebar-border cursor-pointer hover:shadow-md" onClick={() => setSelectedItem(item)}>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <code className="text-sm bg-muted px-2 py-1 rounded">{item.id}</code>
                <Badge className={getStatusColor(item.status)}>
                  {item.status}
                </Badge>
              </div>
              <Checkbox
                checked={selectedItems.includes(item.id)}
                onCheckedChange={() => handleSelectItem(item.id)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div>
              <CardTitle className="text-base">{item.templateName}</CardTitle>
              <CardDescription>{item.templateVersion}</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 mb-4">
              {Object.entries(item.preview).slice(0, 3).map(([key, value]) => (
                <div key={key} className="text-sm">
                  <span className="text-muted-foreground">{key}:</span>
                  <span className="ml-1 text-foreground">
                    {value || <span className="text-muted-foreground italic">tom</span>}
                  </span>
                </div>
              ))}
            </div>
            <div className="text-xs text-muted-foreground">
              Skapad {getRelativeTime(item.createdAt)}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );

  const renderSidebar = () => {
    if (!selectedItem) return null;

    return (
      <div className="w-80 border-l border-sidebar-border bg-background">
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-foreground">Detaljer</h3>
            <Button variant="ghost" size="sm" onClick={() => setSelectedItem(null)}>
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>

          <Tabs value={sidebarTab} onValueChange={(value) => setSidebarTab(value as 'lineage' | 'dq')}>
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="lineage">Proveniens</TabsTrigger>
              <TabsTrigger value="dq">DQ</TabsTrigger>
            </TabsList>

            <TabsContent value="lineage" className="space-y-4 mt-4">
              <Card className="border-sidebar-border">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Härkomst</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <Label className="text-xs text-muted-foreground">Jobb</Label>
                    <p className="text-sm text-foreground">{selectedItem.jobId}</p>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">URL</Label>
                    <div className="flex items-center space-x-2">
                      <p className="text-sm text-foreground truncate flex-1">{selectedItem.url}</p>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(selectedItem.url, '_blank')}
                      >
                        <ExternalLink className="w-3 h-3" />
                      </Button>
                    </div>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Mall</Label>
                    <p className="text-sm text-foreground">{selectedItem.templateName} {selectedItem.templateVersion}</p>
                  </div>
                  <div>
                    <Label className="text-xs text-muted-foreground">Rendering</Label>
                    <p className="text-sm text-foreground">HTTP</p>
                  </div>
                </CardContent>
              </Card>

              <div className="space-y-2">
                <Button variant="outline" size="sm" className="w-full">
                  <Eye className="w-4 h-4 mr-2" />
                  Visa HTML snapshot
                </Button>
                <Button variant="outline" size="sm" className="w-full">
                  <Copy className="w-4 h-4 mr-2" />
                  Kopiera härkomst som JSON
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="dq" className="space-y-4 mt-4">
              <Card className="border-sidebar-border">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">Datakvalitet</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {selectedItem.status === 'validated' ? (
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-success rounded-full"></div>
                      <span className="text-sm text-success">Alla regler godkända</span>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-warning rounded-full"></div>
                        <span className="text-sm text-warning">DQ-problem upptäckta</span>
                      </div>
                      <div className="bg-warning/10 border border-warning/20 rounded p-2">
                        <p className="text-xs text-warning">missing_required_field: Fältet 'model' saknas</p>
                      </div>
                    </div>
                  )}
                  
                  <div>
                    <Label className="text-xs text-muted-foreground">Fälttäckning</Label>
                    <div className="flex items-center space-x-2 mt-1">
                      <div className="flex-1 bg-muted rounded-full h-2">
                        <div 
                          className="bg-success h-2 rounded-full" 
                          style={{ width: selectedItem.status === 'validated' ? '100%' : '75%' }}
                        ></div>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {selectedItem.status === 'validated' ? '100%' : '75%'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {selectedItem.status !== 'validated' && (
                <div className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full">
                    <Flag className="w-4 h-4 mr-2" />
                    Markera som validerad
                  </Button>
                  <Button variant="outline" size="sm" className="w-full">
                    <Search className="w-4 h-4 mr-2" />
                    Öppna liknande fel
                  </Button>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen">
      <div className="flex-1 space-y-6 p-6 overflow-auto">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Datalager</h1>
            <p className="text-muted-foreground">Extraherade dataposter och kvalitetskontroll</p>
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="outline" size="sm">
              <RefreshCw className="w-4 h-4 mr-2" />
              Uppdatera
            </Button>
            <Button variant="outline" size="sm" onClick={() => setViewMode(viewMode === 'table' ? 'cards' : 'table')}>
              {viewMode === 'table' ? <Grid className="w-4 h-4" /> : <List className="w-4 h-4" />}
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="border-sidebar-border">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="search">Sök</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="search"
                    placeholder="Sök i data, ID, URL..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Status</Label>
                <div className="flex flex-wrap gap-2">
                  {['validated', 'quarantine', 'tombstone'].map((status) => (
                    <div key={status} className="flex items-center space-x-2">
                      <Checkbox
                        id={status}
                        checked={selectedStatuses.includes(status)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setSelectedStatuses([...selectedStatuses, status]);
                          } else {
                            setSelectedStatuses(selectedStatuses.filter(s => s !== status));
                          }
                        }}
                      />
                      <Label htmlFor={status} className="text-sm">
                        {status}
                      </Label>
                    </div>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label>Mall</Label>
                <Select value={selectedTemplates[0] || ''} onValueChange={(value) => setSelectedTemplates(value ? [value] : [])}>
                  <SelectTrigger>
                    <SelectValue placeholder="Välj mall..." />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Alla mallar</SelectItem>
                    {templates.map((template) => (
                      <SelectItem key={template} value={template}>
                        {template}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Tidsintervall</Label>
                <Select value={dateRange} onValueChange={setDateRange}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="24h">Senaste 24h</SelectItem>
                    <SelectItem value="7d">Senaste 7 dagarna</SelectItem>
                    <SelectItem value="30d">Senaste 30 dagarna</SelectItem>
                    <SelectItem value="custom">Anpassat</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions toolbar */}
        {selectedItems.length > 0 && (
          <Card className="border-sidebar-border bg-primary/5">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-foreground">
                  {selectedItems.length} objekt valda
                </span>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Exportera urval
                  </Button>
                  <Button variant="outline" size="sm">
                    <Flag className="w-4 h-4 mr-2" />
                    Flagga/karantän
                  </Button>
                  <Button variant="outline" size="sm">
                    <Trash2 className="w-4 h-4 mr-2" />
                    Radera
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Visar {filteredItems.length} resultat
            </p>
            <div className="flex items-center space-x-2">
              <Label htmlFor="itemsPerPage" className="text-sm">Visa:</Label>
              <Select value={itemsPerPage.toString()} onValueChange={(value) => setItemsPerPage(parseInt(value))}>
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="25">25</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {viewMode === 'table' ? renderTableView() : renderCardView()}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">
                Sida {currentPage} av {totalPages}
              </p>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sidebar */}
      {renderSidebar()}
    </div>
  );
};

export default DataWarehouse;
