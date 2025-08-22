import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Download, 
  FileSpreadsheet, 
  Database, 
  Calendar,
  Filter,
  Settings
} from 'lucide-react';

const Exports = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Data Exports</h1>
          <p className="text-muted-foreground">Export and download your collected data</p>
        </div>
        <Button className="bg-gradient-primary">
          <Download className="w-4 h-4 mr-2" />
          Create Export
        </Button>
      </div>

      {/* Export Options */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileSpreadsheet className="w-5 h-5 text-success" />
              <span>CSV Export</span>
            </CardTitle>
            <CardDescription>Standard spreadsheet format</CardDescription>
          </CardHeader>
          <CardContent>
            <Button className="w-full bg-gradient-success">
              Export as CSV
            </Button>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-primary" />
              <span>JSON Export</span>
            </CardTitle>
            <CardDescription>Structured data format</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full">
              Export as JSON
            </Button>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="w-5 h-5 text-accent" />
              <span>Custom Export</span>
            </CardTitle>
            <CardDescription>Configure custom format</CardDescription>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="w-full">
              Configure Export
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Recent Exports */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle>Recent Exports</CardTitle>
          <CardDescription>Your latest data export jobs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              {
                name: 'vehicles_Q3_2024.csv',
                type: 'CSV',
                size: '45.2 MB',
                records: '89,432',
                status: 'completed',
                created: '2 hours ago'
              },
              {
                name: 'business_directory.json',
                type: 'JSON',
                size: '23.1 MB',
                records: '34,567',
                status: 'processing',
                created: '1 day ago'
              },
              {
                name: 'car_listings_september.csv',
                type: 'CSV',
                size: '67.8 MB',
                records: '123,890',
                status: 'completed',
                created: '3 days ago'
              }
            ].map((export_, index) => (
              <div key={index} className="flex items-center justify-between p-4 rounded-lg bg-sidebar-accent">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <FileSpreadsheet className="w-5 h-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium text-foreground">{export_.name}</p>
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                        <span>{export_.type}</span>
                        <span>{export_.size}</span>
                        <span>{export_.records} records</span>
                        <span>{export_.created}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge 
                    variant="secondary"
                    className={
                      export_.status === 'completed'
                        ? 'bg-success/10 text-success border-success/20'
                        : 'bg-warning/10 text-warning border-warning/20'
                    }
                  >
                    {export_.status}
                  </Badge>
                  <Button size="sm" variant="outline">
                    <Download className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Exports;