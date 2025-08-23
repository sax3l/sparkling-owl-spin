import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { 
  User,
  Shield,
  Bell,
  Palette,
  Database,
  Globe,
  Key,
  Mail,
  Phone,
  Camera,
  Save,
  RefreshCw,
  Download,
  Upload,
  Trash2,
  AlertTriangle,
  CheckCircle,
  Moon,
  Sun,
  Monitor,
  Languages,
  Clock,
  Lock,
  Eye,
  EyeOff
} from "lucide-react";
import { useState } from "react";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState("profile");
  const [darkMode, setDarkMode] = useState(true);
  const [showApiKey, setShowApiKey] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(false);

  const saveSettings = () => {
    console.log("Settings saved");
  };

  const exportSettings = () => {
    console.log("Exporting settings");
  };

  const importSettings = () => {
    console.log("Importing settings");
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Settings</h1>
          <p className="text-gray-600 dark:text-gray-400">Manage your account and application preferences</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={importSettings}>
            <Upload className="h-4 w-4 mr-2" />
            Import
          </Button>
          <Button variant="outline" size="sm" onClick={exportSettings}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button size="sm" onClick={saveSettings}>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="appearance">Appearance</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Profile Information
              </CardTitle>
              <CardDescription>Update your personal information and contact details</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Profile Picture */}
              <div className="flex items-center gap-6">
                <div className="relative">
                  <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold">
                    JD
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full p-0"
                  >
                    <Camera className="h-3 w-3" />
                  </Button>
                </div>
                <div>
                  <h3 className="font-medium">Profile Picture</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Click to upload a new picture. JPG, PNG or GIF (max 2MB)
                  </p>
                </div>
              </div>

              {/* Personal Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">First Name</label>
                  <Input defaultValue="John" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Last Name</label>
                  <Input defaultValue="Doe" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Email Address</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input className="pl-10" defaultValue="john.doe@example.com" />
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Phone Number</label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                    <Input className="pl-10" defaultValue="+1 (555) 123-4567" />
                  </div>
                </div>
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium">Company</label>
                  <Input defaultValue="Acme Corporation" />
                </div>
                <div className="space-y-2 md:col-span-2">
                  <label className="text-sm font-medium">Bio</label>
                  <Textarea 
                    placeholder="Tell us about yourself..."
                    defaultValue="Web scraping enthusiast and data analyst with 5+ years of experience."
                    rows={3}
                  />
                </div>
              </div>

              {/* Account Status */}
              <div className="p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
                  <span className="font-medium text-green-800 dark:text-green-200">Account Verified</span>
                </div>
                <p className="text-sm text-green-600 dark:text-green-400">
                  Your email address has been verified. You have access to all premium features.
                </p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Password & Authentication
              </CardTitle>
              <CardDescription>Manage your login credentials and security settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Current Password</label>
                  <Input type="password" placeholder="Enter current password" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">New Password</label>
                  <Input type="password" placeholder="Enter new password" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Confirm Password</label>
                  <Input type="password" placeholder="Confirm new password" />
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Two-Factor Authentication</h4>
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <p className="font-medium">Authenticator App</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Use an authenticator app to generate verification codes
                    </p>
                  </div>
                  <Badge variant="secondary">Not Enabled</Badge>
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Login Sessions</h4>
                <div className="space-y-3">
                  {[
                    { device: "Chrome on Windows", location: "New York, NY", lastActive: "Current session", current: true },
                    { device: "Safari on iPhone", location: "New York, NY", lastActive: "2 hours ago", current: false },
                    { device: "Firefox on Linux", location: "San Francisco, CA", lastActive: "1 day ago", current: false }
                  ].map((session, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <p className="font-medium">{session.device}</p>
                          {session.current && (
                            <Badge variant="default" className="text-xs">Current</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {session.location} • {session.lastActive}
                        </p>
                      </div>
                      {!session.current && (
                        <Button variant="outline" size="sm">
                          Revoke
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="h-5 w-5" />
                Notification Preferences
              </CardTitle>
              <CardDescription>Choose what notifications you want to receive and how</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-medium">Email Notifications</h4>
                {[
                  { label: "Job Completion", description: "Get notified when crawling jobs finish", enabled: true },
                  { label: "Job Failures", description: "Receive alerts when jobs fail or encounter errors", enabled: true },
                  { label: "System Updates", description: "News about new features and updates", enabled: false },
                  { label: "Weekly Reports", description: "Summary of your account activity", enabled: true }
                ].map((notification, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{notification.label}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{notification.description}</p>
                    </div>
                    <input 
                      type="checkbox" 
                      defaultChecked={notification.enabled}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                  </div>
                ))}
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Push Notifications</h4>
                {[
                  { label: "Browser Notifications", description: "Show notifications in your browser", enabled: false },
                  { label: "Mobile App", description: "Push notifications to your mobile device", enabled: false }
                ].map((notification, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">{notification.label}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{notification.description}</p>
                    </div>
                    <input 
                      type="checkbox" 
                      defaultChecked={notification.enabled}
                      className="w-4 h-4 text-blue-600 rounded"
                    />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Tab */}
        <TabsContent value="appearance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Appearance & Theme
              </CardTitle>
              <CardDescription>Customize how the application looks and feels</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-medium">Theme</h4>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { value: "light", icon: Sun, label: "Light", active: false },
                    { value: "dark", icon: Moon, label: "Dark", active: true },
                    { value: "system", icon: Monitor, label: "System", active: false }
                  ].map((theme) => {
                    const Icon = theme.icon;
                    return (
                      <button
                        key={theme.value}
                        className={`p-4 border-2 rounded-lg flex flex-col items-center gap-2 transition-colors ${
                          theme.active 
                            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20" 
                            : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                        }`}
                      >
                        <Icon className="h-6 w-6" />
                        <span className="text-sm font-medium">{theme.label}</span>
                      </button>
                    );
                  })}
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Language</h4>
                <div className="flex items-center gap-3">
                  <Languages className="h-4 w-4 text-gray-400" />
                  <select className="flex-1 p-2 border rounded-lg bg-background">
                    <option value="en">English</option>
                    <option value="sv">Svenska</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                  </select>
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Timezone</h4>
                <div className="flex items-center gap-3">
                  <Clock className="h-4 w-4 text-gray-400" />
                  <select className="flex-1 p-2 border rounded-lg bg-background">
                    <option value="UTC">UTC (Coordinated Universal Time)</option>
                    <option value="EST">EST (Eastern Standard Time)</option>
                    <option value="PST">PST (Pacific Standard Time)</option>
                    <option value="CET">CET (Central European Time)</option>
                  </select>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* API Tab */}
        <TabsContent value="api" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                API Configuration
              </CardTitle>
              <CardDescription>Manage API keys and integration settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-medium">API Keys</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex-1">
                      <p className="font-medium">Primary API Key</p>
                      <div className="flex items-center gap-2 mt-1">
                        <code className="text-sm bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded font-mono">
                          {showApiKey ? "sk_live_1234567890abcdef..." : "sk_live_••••••••••••••••"}
                        </code>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowApiKey(!showApiKey)}
                        >
                          {showApiKey ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        </Button>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Created on Jan 1, 2024 • Last used 2 hours ago
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                
                <Button>Generate New API Key</Button>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Rate Limits</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-3 border rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">1,000</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Requests/hour</div>
                  </div>
                  <div className="p-3 border rounded-lg text-center">
                    <div className="text-2xl font-bold text-green-600 dark:text-green-400">10,000</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Requests/day</div>
                  </div>
                  <div className="p-3 border rounded-lg text-center">
                    <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">100,000</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Requests/month</div>
                  </div>
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Webhook URLs</h4>
                <div className="space-y-3">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Job Completion Webhook</label>
                    <Input placeholder="https://your-app.com/webhooks/job-complete" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Error Notification Webhook</label>
                    <Input placeholder="https://your-app.com/webhooks/errors" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Advanced Tab */}
        <TabsContent value="advanced" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Advanced Settings
              </CardTitle>
              <CardDescription>Advanced configuration options for power users</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <h4 className="font-medium">Data Retention</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Job History (days)</label>
                    <Input defaultValue="30" type="number" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Log Retention (days)</label>
                    <Input defaultValue="7" type="number" />
                  </div>
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Performance</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Max Concurrent Jobs</label>
                    <Input defaultValue="5" type="number" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Request Timeout (seconds)</label>
                    <Input defaultValue="30" type="number" />
                  </div>
                </div>
              </div>

              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Data Export</h4>
                <div className="space-y-3">
                  <Button variant="outline" className="justify-start">
                    <Download className="h-4 w-4 mr-2" />
                    Export Account Data
                  </Button>
                  <Button variant="outline" className="justify-start">
                    <Download className="h-4 w-4 mr-2" />
                    Export Configuration
                  </Button>
                </div>
              </div>

              <div className="border-t pt-6">
                <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertTriangle className="h-4 w-4 text-red-600 dark:text-red-400" />
                    <span className="font-medium text-red-800 dark:text-red-200">Danger Zone</span>
                  </div>
                  <p className="text-sm text-red-600 dark:text-red-400 mb-4">
                    These actions are permanent and cannot be undone.
                  </p>
                  <div className="space-y-2">
                    <Button variant="destructive" size="sm">
                      Delete All Data
                    </Button>
                    <Button variant="destructive" size="sm">
                      Delete Account
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
