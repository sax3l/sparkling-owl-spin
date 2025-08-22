import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Settings as SettingsIcon, 
  Database, 
  Shield, 
  Bell,
  Globe,
  Save
} from 'lucide-react';

const Settings = () => {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Settings</h1>
          <p className="text-muted-foreground">Configure platform settings and preferences</p>
        </div>
      </div>

      <Tabs defaultValue="general" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="database">Database</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <SettingsIcon className="w-5 h-5 text-primary" />
                <span>General Settings</span>
              </CardTitle>
              <CardDescription>Basic platform configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="platformName">Platform Name</Label>
                  <Input id="platformName" defaultValue="ECaDP Production" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="defaultDelay">Default Crawl Delay (ms)</Label>
                  <Input id="defaultDelay" type="number" defaultValue="2000" />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="enableLogging">Enable Debug Logging</Label>
                    <p className="text-sm text-muted-foreground">Log detailed crawling activities</p>
                  </div>
                  <Switch id="enableLogging" />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="autoBackup">Automatic Backups</Label>
                    <p className="text-sm text-muted-foreground">Daily automated data backups</p>
                  </div>
                  <Switch id="autoBackup" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="ethicsMode">Strict Ethics Mode</Label>
                    <p className="text-sm text-muted-foreground">Enhanced ethical compliance checks</p>
                  </div>
                  <Switch id="ethicsMode" defaultChecked />
                </div>
              </div>

              <Button className="bg-gradient-primary">
                <Save className="w-4 h-4 mr-2" />
                Save General Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="database" className="space-y-6">
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="w-5 h-5 text-accent" />
                <span>Database Configuration</span>
              </CardTitle>
              <CardDescription>Supabase and storage settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="supabaseUrl">Supabase URL</Label>
                  <Input id="supabaseUrl" defaultValue="https://your-project.supabase.co" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="supabaseKey">Supabase Anon Key</Label>
                  <Input id="supabaseKey" type="password" placeholder="••••••••••••••••" />
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="enableRLS">Row Level Security</Label>
                    <p className="text-sm text-muted-foreground">Enable RLS on all tables</p>
                  </div>
                  <Switch id="enableRLS" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="autoVacuum">Auto Vacuum</Label>
                    <p className="text-sm text-muted-foreground">Automatic database optimization</p>
                  </div>
                  <Switch id="autoVacuum" defaultChecked />
                </div>
              </div>

              <Button className="bg-gradient-primary">
                <Save className="w-4 h-4 mr-2" />
                Save Database Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-warning" />
                <span>Security Settings</span>
              </CardTitle>
              <CardDescription>Security and compliance configuration</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="apiKey">API Key</Label>
                  <div className="flex space-x-2">
                    <Input id="apiKey" type="password" placeholder="••••••••••••••••" className="flex-1" />
                    <Button variant="outline">Regenerate</Button>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="enableTwoFactor">Two-Factor Authentication</Label>
                    <p className="text-sm text-muted-foreground">Require 2FA for admin access</p>
                  </div>
                  <Switch id="enableTwoFactor" />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="auditLogging">Audit Logging</Label>
                    <p className="text-sm text-muted-foreground">Log all admin actions</p>
                  </div>
                  <Switch id="auditLogging" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="ipWhitelist">IP Whitelist</Label>
                    <p className="text-sm text-muted-foreground">Restrict access by IP address</p>
                  </div>
                  <Switch id="ipWhitelist" />
                </div>
              </div>

              <Button className="bg-gradient-primary">
                <Save className="w-4 h-4 mr-2" />
                Save Security Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-6">
          <Card className="border-sidebar-border">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="w-5 h-5 text-success" />
                <span>Notification Settings</span>
              </CardTitle>
              <CardDescription>Configure alerts and notifications</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="jobComplete">Job Completion</Label>
                    <p className="text-sm text-muted-foreground">Notify when crawling jobs finish</p>
                  </div>
                  <Switch id="jobComplete" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="jobFailed">Job Failures</Label>
                    <p className="text-sm text-muted-foreground">Alert on job failures</p>
                  </div>
                  <Switch id="jobFailed" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="proxyIssues">Proxy Issues</Label>
                    <p className="text-sm text-muted-foreground">Alert when proxies fail</p>
                  </div>
                  <Switch id="proxyIssues" defaultChecked />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label htmlFor="dataQuality">Data Quality Alerts</Label>
                    <p className="text-sm text-muted-foreground">Quality degradation warnings</p>
                  </div>
                  <Switch id="dataQuality" />
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="webhookUrl">Webhook URL</Label>
                  <Input id="webhookUrl" placeholder="https://your-webhook.com/ecadp" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="emailNotifications">Email Notifications</Label>
                  <Input id="emailNotifications" type="email" placeholder="admin@example.com" />
                </div>
              </div>

              <Button className="bg-gradient-primary">
                <Save className="w-4 h-4 mr-2" />
                Save Notification Settings
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Settings;