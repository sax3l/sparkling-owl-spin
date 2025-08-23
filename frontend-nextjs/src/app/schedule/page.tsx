import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Calendar,
  Clock,
  Plus,
  Play,
  Pause,
  Edit,
  Trash2,
  RefreshCw,
  Settings,
  Bell,
  CheckCircle,
  AlertTriangle,
  XCircle,
  MoreHorizontal
} from "lucide-react";
import { useState } from "react";

// Mock schedule data
const mockSchedules = [
  {
    id: "sched_001",
    name: "Daily Product Sync",
    template: "E-commerce Product Scraper",
    domain: "example.com",
    frequency: "daily",
    time: "02:00",
    timezone: "UTC",
    status: "active",
    lastRun: "2024-01-15 02:00:00",
    nextRun: "2024-01-16 02:00:00",
    success: 98.5,
    enabled: true
  },
  {
    id: "sched_002",
    name: "Weekly News Aggregation",
    template: "News Article Extractor", 
    domain: "newsportal.com",
    frequency: "weekly",
    time: "06:00",
    timezone: "UTC",
    status: "active",
    lastRun: "2024-01-14 06:00:00",
    nextRun: "2024-01-21 06:00:00",
    success: 94.2,
    enabled: true
  },
  {
    id: "sched_003",
    name: "Real Estate Updates",
    template: "Real Estate Listings",
    domain: "realestate.com",
    frequency: "hourly",
    time: ":15",
    timezone: "EST",
    status: "paused",
    lastRun: "2024-01-15 13:15:00",
    nextRun: "Paused",
    success: 89.7,
    enabled: false
  },
  {
    id: "sched_004",
    name: "Social Media Monitor",
    template: "Social Media Profiles",
    domain: "socialmedia.com",
    frequency: "custom",
    time: "Every 4 hours",
    timezone: "PST",
    status: "error",
    lastRun: "2024-01-15 12:00:00",
    nextRun: "Error - check config",
    success: 76.3,
    enabled: true
  }
];

const frequencyOptions = [
  { value: "hourly", label: "Every Hour", description: "Runs at the specified minute of each hour" },
  { value: "daily", label: "Daily", description: "Runs once per day at specified time" },
  { value: "weekly", label: "Weekly", description: "Runs once per week on specified day and time" },
  { value: "monthly", label: "Monthly", description: "Runs once per month on specified date" },
  { value: "custom", label: "Custom Cron", description: "Define your own cron expression" }
];

const getStatusColor = (status: string) => {
  switch (status) {
    case "active": return "text-green-600 dark:text-green-400";
    case "paused": return "text-yellow-600 dark:text-yellow-400";
    case "error": return "text-red-600 dark:text-red-400";
    default: return "text-gray-600 dark:text-gray-400";
  }
};

const getStatusIcon = (status: string) => {
  switch (status) {
    case "active": return CheckCircle;
    case "paused": return Pause;
    case "error": return XCircle;
    default: return Clock;
  }
};

export default function SchedulePage() {
  const [activeTab, setActiveTab] = useState("schedules");
  const [schedules, setSchedules] = useState(mockSchedules);

  const toggleSchedule = (id: string) => {
    setSchedules(schedules.map(schedule => 
      schedule.id === id 
        ? { ...schedule, enabled: !schedule.enabled, status: schedule.enabled ? "paused" : "active" }
        : schedule
    ));
  };

  const deleteSchedule = (id: string) => {
    setSchedules(schedules.filter(schedule => schedule.id !== id));
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Job Scheduler</h1>
          <p className="text-gray-600 dark:text-gray-400">Automate your crawling jobs with flexible scheduling</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Schedule
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Schedules</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {schedules.filter(s => s.status === "active").length}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Next Run</p>
                <p className="text-lg font-bold">16:00 UTC</p>
                <p className="text-xs text-gray-500">in 2h 15m</p>
              </div>
              <Clock className="h-8 w-8 text-blue-600 dark:text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Today's Jobs</p>
                <p className="text-2xl font-bold">24</p>
                <p className="text-xs text-gray-500">18 completed</p>
              </div>
              <Calendar className="h-8 w-8 text-purple-600 dark:text-purple-400" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Avg Success</p>
                <p className="text-2xl font-bold">94.8%</p>
                <p className="text-xs text-gray-500">last 30 days</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="schedules">Active Schedules</TabsTrigger>
          <TabsTrigger value="create">Create Schedule</TabsTrigger>
          <TabsTrigger value="history">Execution History</TabsTrigger>
          <TabsTrigger value="templates">Schedule Templates</TabsTrigger>
        </TabsList>

        {/* Active Schedules Tab */}
        <TabsContent value="schedules" className="space-y-4">
          {schedules.map((schedule) => {
            const StatusIcon = getStatusIcon(schedule.status);
            
            return (
              <Card key={schedule.id}>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <StatusIcon className={`h-6 w-6 ${getStatusColor(schedule.status)}`} />
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="font-semibold text-lg">{schedule.name}</h3>
                          <Badge variant={schedule.status === "active" ? "default" : "secondary"}>
                            {schedule.status}
                          </Badge>
                          {!schedule.enabled && (
                            <Badge variant="outline" className="text-xs">Disabled</Badge>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Template</span>
                            <p className="font-medium">{schedule.template}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Domain</span>
                            <p className="font-medium">{schedule.domain}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Frequency</span>
                            <p className="font-medium capitalize">{schedule.frequency}</p>
                          </div>
                          <div>
                            <span className="text-gray-500 dark:text-gray-400">Time</span>
                            <p className="font-medium">{schedule.time} {schedule.timezone}</p>
                          </div>
                        </div>

                        <div className="flex gap-6 text-sm text-gray-600 dark:text-gray-400 mt-3">
                          <span>Last run: {schedule.lastRun}</span>
                          <span>Next run: {schedule.nextRun}</span>
                          <span>Success rate: {schedule.success}%</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => toggleSchedule(schedule.id)}
                      >
                        {schedule.enabled ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                      </Button>
                      <Button variant="outline" size="sm">
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <Bell className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => deleteSchedule(schedule.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </TabsContent>

        {/* Create Schedule Tab */}
        <TabsContent value="create" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Create New Schedule</CardTitle>
              <CardDescription>Set up automated crawling jobs</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Information */}
                <div className="space-y-4">
                  <h4 className="font-medium">Basic Information</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Schedule Name</label>
                      <Input placeholder="e.g., Daily Product Updates" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Template</label>
                      <select className="w-full p-2 border rounded-lg bg-background">
                        <option>E-commerce Product Scraper</option>
                        <option>News Article Extractor</option>
                        <option>Real Estate Listings</option>
                        <option>Social Media Profiles</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Target Domain</label>
                      <Input placeholder="example.com" />
                    </div>
                  </div>
                </div>

                {/* Timing Configuration */}
                <div className="space-y-4">
                  <h4 className="font-medium">Timing Configuration</h4>
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Frequency</label>
                      <select className="w-full p-2 border rounded-lg bg-background">
                        {frequencyOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Time</label>
                      <Input type="time" defaultValue="02:00" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Timezone</label>
                      <select className="w-full p-2 border rounded-lg bg-background">
                        <option>UTC</option>
                        <option>EST</option>
                        <option>PST</option>
                        <option>CET</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              {/* Advanced Options */}
              <div className="border-t pt-6">
                <h4 className="font-medium mb-4">Advanced Options</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Max Runtime (minutes)</label>
                    <Input type="number" defaultValue="60" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Retry Attempts</label>
                    <Input type="number" defaultValue="3" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Notification Email</label>
                    <Input type="email" placeholder="your@email.com" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Priority</label>
                    <select className="w-full p-2 border rounded-lg bg-background">
                      <option>Normal</option>
                      <option>High</option>
                      <option>Low</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button className="flex-1">Create Schedule</Button>
                <Button variant="outline">Save as Draft</Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Execution History</CardTitle>
              <CardDescription>Recent scheduled job executions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { name: "Daily Product Sync", time: "2024-01-15 02:00:00", status: "completed", duration: "12m 34s" },
                  { name: "Weekly News Aggregation", time: "2024-01-14 06:00:00", status: "completed", duration: "8m 12s" },
                  { name: "Real Estate Updates", time: "2024-01-14 13:15:00", status: "failed", duration: "2m 45s" },
                  { name: "Social Media Monitor", time: "2024-01-14 12:00:00", status: "completed", duration: "15m 23s" }
                ].map((execution, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div>
                      <p className="font-medium">{execution.name}</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{execution.time}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-sm">{execution.duration}</span>
                      <Badge variant={execution.status === "completed" ? "default" : "destructive"}>
                        {execution.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {frequencyOptions.map((template) => (
              <Card key={template.value}>
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">{template.label}</CardTitle>
                  <CardDescription className="text-sm">{template.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">
                    Use Template
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
