import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  RefreshCw,
  Database,
  FileSpreadsheet,
  Target
} from 'lucide-react';

const DQPanel = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Data Quality Panel</h1>
          <p className="text-muted-foreground">Monitor and analyze data quality across all sources</p>
        </div>
        <Button variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Analysis
        </Button>
      </div>

      {/* Quality Score Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Overall Quality</p>
                <p className="text-3xl font-bold text-foreground">87.3%</p>
                <div className="flex items-center space-x-2 mt-2">
                  <TrendingUp className="w-4 h-4 text-success" />
                  <span className="text-sm text-success">+2.1% this week</span>
                </div>
              </div>
              <div className="w-16 h-16 rounded-full bg-gradient-success flex items-center justify-center">
                <BarChart3 className="w-8 h-8 text-success-foreground" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Valid Records</p>
                <p className="text-2xl font-bold text-foreground">2.1M</p>
                <Badge className="bg-success/10 text-success border-success/20 mt-2">
                  94.2% valid
                </Badge>
              </div>
              <CheckCircle2 className="w-8 h-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Data Issues</p>
                <p className="text-2xl font-bold text-foreground">142</p>
                <Badge className="bg-warning/10 text-warning border-warning/20 mt-2">
                  Requires attention
                </Badge>
              </div>
              <AlertTriangle className="w-8 h-8 text-warning" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Sources</p>
                <p className="text-2xl font-bold text-foreground">8</p>
                <Badge className="bg-primary/10 text-primary border-primary/20 mt-2">
                  Active sources
                </Badge>
              </div>
              <Database className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Quality Overview</TabsTrigger>
          <TabsTrigger value="sources">Source Analysis</TabsTrigger>
          <TabsTrigger value="issues">Data Issues</TabsTrigger>
          <TabsTrigger value="trends">Quality Trends</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Quality Metrics */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Target className="w-5 h-5 text-primary" />
                  <span>Quality Metrics</span>
                </CardTitle>
                <CardDescription>Key quality indicators across all data sources</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-foreground">Completeness</span>
                      <span className="text-sm text-foreground">92.1%</span>
                    </div>
                    <Progress value={92.1} className="h-2" />
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-foreground">Accuracy</span>
                      <span className="text-sm text-foreground">89.7%</span>
                    </div>
                    <Progress value={89.7} className="h-2" />
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-foreground">Consistency</span>
                      <span className="text-sm text-foreground">85.3%</span>
                    </div>
                    <Progress value={85.3} className="h-2" />
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-foreground">Timeliness</span>
                      <span className="text-sm text-foreground">91.8%</span>
                    </div>
                    <Progress value={91.8} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Recent Quality Checks */}
            <Card className="border-sidebar-border">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <CheckCircle2 className="w-5 h-5 text-success" />
                  <span>Recent Quality Checks</span>
                </CardTitle>
                <CardDescription>Latest automated quality assessments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    { 
                      check: 'Vehicle Data Validation', 
                      source: 'biluppgifter.se', 
                      status: 'passed', 
                      score: 94.2,
                      time: '5 min ago'
                    },
                    { 
                      check: 'Business Directory Completeness', 
                      source: 'hitta.se', 
                      status: 'warning', 
                      score: 78.1,
                      time: '12 min ago'
                    },
                    { 
                      check: 'Price Format Consistency', 
                      source: 'car.info', 
                      status: 'passed', 
                      score: 96.8,
                      time: '18 min ago'
                    },
                    { 
                      check: 'Duplicate Detection', 
                      source: 'blocket.se', 
                      status: 'failed', 
                      score: 67.3,
                      time: '25 min ago'
                    }
                  ].map((check, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-sidebar-accent">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <p className="text-sm font-medium text-foreground">{check.check}</p>
                          <Badge 
                            variant="secondary"
                            className={
                              check.status === 'passed' 
                                ? 'bg-success/10 text-success border-success/20'
                                : check.status === 'warning'
                                ? 'bg-warning/10 text-warning border-warning/20'
                                : 'bg-destructive/10 text-destructive border-destructive/20'
                            }
                          >
                            {check.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {check.source} • Score: {check.score}% • {check.time}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="sources" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { name: 'biluppgifter.se', records: '847K', quality: 94.2, status: 'excellent' },
              { name: 'hitta.se', records: '623K', quality: 78.1, status: 'good' },
              { name: 'car.info', records: '394K', quality: 96.8, status: 'excellent' },
              { name: 'blocket.se', records: '283K', quality: 67.3, status: 'needs_attention' }
            ].map((source, index) => (
              <Card key={index} className="border-sidebar-border">
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">{source.name}</CardTitle>
                  <CardDescription>{source.records} records</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-muted-foreground">Quality Score</span>
                        <span className="text-sm font-medium text-foreground">{source.quality}%</span>
                      </div>
                      <Progress value={source.quality} className="h-2" />
                    </div>
                    
                    <Badge 
                      variant="secondary"
                      className={
                        source.status === 'excellent'
                          ? 'bg-success/10 text-success border-success/20'
                          : source.status === 'good'
                          ? 'bg-primary/10 text-primary border-primary/20'
                          : 'bg-warning/10 text-warning border-warning/20'
                      }
                    >
                      {source.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="issues" className="space-y-6">
          <div className="grid grid-cols-1 gap-4">
            {[
              {
                type: 'Missing Values',
                description: 'Vehicle mileage field empty in 23% of records',
                source: 'biluppgifter.se',
                severity: 'medium',
                count: 67,
                suggested: 'Improve selector specificity'
              },
              {
                type: 'Format Inconsistency', 
                description: 'Phone numbers in multiple formats',
                source: 'hitta.se',
                severity: 'low',
                count: 45,
                suggested: 'Add normalization rules'
              },
              {
                type: 'Duplicate Records',
                description: 'Same vehicle listed multiple times',
                source: 'car.info',
                severity: 'high',
                count: 18,
                suggested: 'Implement deduplication'
              },
              {
                type: 'Invalid Data Type',
                description: 'Price field contains non-numeric values',
                source: 'blocket.se', 
                severity: 'high',
                count: 12,
                suggested: 'Update transformation rules'
              }
            ].map((issue, index) => (
              <Card key={index} className="border-sidebar-border">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-foreground">{issue.type}</h3>
                        <Badge 
                          variant="secondary"
                          className={
                            issue.severity === 'high'
                              ? 'bg-destructive/10 text-destructive border-destructive/20'
                              : issue.severity === 'medium'
                              ? 'bg-warning/10 text-warning border-warning/20'
                              : 'bg-primary/10 text-primary border-primary/20'
                          }
                        >
                          {issue.severity} severity
                        </Badge>
                        <Badge variant="secondary">
                          {issue.count} occurrences
                        </Badge>
                      </div>
                      <p className="text-muted-foreground mb-2">{issue.description}</p>
                      <div className="flex items-center space-x-4 text-sm">
                        <span className="text-muted-foreground">Source: <span className="text-foreground font-mono">{issue.source}</span></span>
                        <span className="text-muted-foreground">Suggestion: <span className="text-accent">{issue.suggested}</span></span>
                      </div>
                    </div>
                    <Button size="sm" variant="outline">
                      Fix Issue
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <div className="text-center py-12">
            <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">Quality Trends</h3>
            <p className="text-muted-foreground">Historical quality analysis and trends will be shown here</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DQPanel;