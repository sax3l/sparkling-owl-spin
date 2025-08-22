import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Shield, 
  Trash2, 
  Search,
  AlertTriangle,
  CheckCircle2,
  Clock
} from 'lucide-react';

const ErasureAdmin = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">GDPR Data Erasure</h1>
          <p className="text-muted-foreground">Manage data deletion requests and compliance</p>
        </div>
      </div>

      {/* GDPR Compliance Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Pending Requests</p>
                <p className="text-2xl font-bold text-foreground">3</p>
              </div>
              <Clock className="w-8 h-8 text-warning" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold text-foreground">47</p>
              </div>
              <CheckCircle2 className="w-8 h-8 text-success" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-sidebar-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Compliance Score</p>
                <p className="text-2xl font-bold text-foreground">98.7%</p>
              </div>
              <Shield className="w-8 h-8 text-primary" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Search & Erasure */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="w-5 h-5 text-primary" />
            <span>Data Subject Search</span>
          </CardTitle>
          <CardDescription>Search for and manage personal data across all sources</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="searchEmail">Email Address</Label>
              <Input id="searchEmail" placeholder="user@example.com" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="searchPhone">Phone Number</Label>
              <Input id="searchPhone" placeholder="+46 70 123 45 67" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="searchRegNum">Registration Number</Label>
              <Input id="searchRegNum" placeholder="ABC123" />
            </div>
          </div>
          
          <div className="flex space-x-2">
            <Button className="bg-gradient-primary">
              <Search className="w-4 h-4 mr-2" />
              Search Data
            </Button>
            <Button variant="outline">
              Advanced Search
            </Button>
          </div>

          <div className="mt-6 p-4 bg-warning/5 border border-warning/20 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-warning" />
              <p className="text-sm font-medium text-warning">Data Protection Notice</p>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              All data erasure requests are logged and audited in compliance with GDPR Article 17.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Recent Erasure Requests */}
      <Card className="border-sidebar-border">
        <CardHeader>
          <CardTitle>Recent Erasure Requests</CardTitle>
          <CardDescription>Latest data deletion requests and their status</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[
              {
                id: 'REQ-001',
                subject: 'user@example.com',
                type: 'Email-based',
                requestDate: '2024-08-20',
                status: 'pending',
                recordsFound: 5,
                sources: ['biluppgifter.se', 'hitta.se']
              },
              {
                id: 'REQ-002',
                subject: '+46701234567',
                type: 'Phone-based',
                requestDate: '2024-08-19',
                status: 'completed',
                recordsFound: 3,
                sources: ['car.info']
              },
              {
                id: 'REQ-003',
                subject: 'ABC123',
                type: 'Registration Number',
                requestDate: '2024-08-18',
                status: 'in_progress',
                recordsFound: 12,
                sources: ['biluppgifter.se', 'blocket.se']
              }
            ].map((request, index) => (
              <div key={index} className="flex items-center justify-between p-4 rounded-lg bg-sidebar-accent">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <p className="font-medium text-foreground">{request.id}</p>
                    <Badge 
                      variant="secondary"
                      className={
                        request.status === 'completed'
                          ? 'bg-success/10 text-success border-success/20'
                          : request.status === 'pending'
                          ? 'bg-warning/10 text-warning border-warning/20'
                          : 'bg-primary/10 text-primary border-primary/20'
                      }
                    >
                      {request.status.replace('_', ' ')}
                    </Badge>
                  </div>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <p>Subject: <span className="font-mono text-foreground">{request.subject}</span></p>
                    <p>Records Found: <span className="text-foreground">{request.recordsFound}</span> across {request.sources.length} sources</p>
                    <p>Requested: {request.requestDate}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <Button size="sm" variant="outline">
                    View Details
                  </Button>
                  {request.status === 'pending' && (
                    <Button size="sm" className="bg-gradient-danger">
                      <Trash2 className="w-4 h-4 mr-1" />
                      Process
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ErasureAdmin;