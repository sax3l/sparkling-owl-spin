'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { 
  Activity,
  Database,
  Globe,
  TrendingUp,
  AlertCircle,
  Clock,
  Zap,
  Play,
  Wand2,
  Download
} from 'lucide-react'

interface Job {
  id: string
  name: string
  status: string
  progress: number
  runtime?: number
  pages_crawled?: number
  pages_failed?: number
  success_rate?: number
}

interface DashboardData {
  active_jobs: Record<string, Job>
  system_metrics: {
    cpu_usage: number
    memory_usage: number
    disk_usage: number
    active_jobs_count: number
  }
  performance_metrics: any
  recent_alerts: any[]
}

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [loading, setLoading] = useState(true)

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws')
    
    ws.onopen = () => {
      setIsConnected(true)
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('Real-time update:', data)
      
      // Handle different update types
      if (data.type === 'job_completed' || data.type === 'job_progress') {
        fetchDashboardData()
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      console.log('WebSocket disconnected')
    }
    
    return () => {
      ws.close()
    }
  }, [])

  // Fetch dashboard data
  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/monitoring/dashboard', {
        headers: {
          'Authorization': 'Bearer demo-token'
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setDashboardData(data)
      } else {
        console.error('Failed to fetch dashboard data')
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  // Initial data fetch
  useEffect(() => {
    fetchDashboardData()
    const interval = setInterval(fetchDashboardData, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const createNewJob = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify({
          name: 'Demo Scraping Job',
          template_id: 'demo-template',
          target_urls: ['https://example.com'],
          priority: 'normal',
          schedule_config: { immediate: true },
          proxy_config: { enabled: true }
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Job created:', result)
        fetchDashboardData()
      }
    } catch (error) {
      console.error('Error creating job:', error)
    }
  }

  const createTemplateWithWizard = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/templates/wizard?example_url=https://example.com', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer demo-token'
        },
        body: JSON.stringify({
          title: 'Sample Product Title',
          price: '$99.99',
          description: 'Product description text'
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        console.log('Template created:', result)
      }
    } catch (error) {
      console.error('Error creating template:', error)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading dashboard...</div>
      </div>
    )
  }

  const activeJobsArray = dashboardData ? Object.entries(dashboardData.active_jobs).map(([id, job]) => ({
    ...job,
    id
  })) : []

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Advanced Web Scraping Platform
              </h1>
              <p className="text-slate-300 text-lg">
                Enterprise-grade data extraction with AI-powered intelligence
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-emerald-400' : 'bg-red-400'}`}></div>
              <span className="text-slate-300 text-sm">
                {isConnected ? 'Real-time Connected' : 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Active Jobs</CardTitle>
              <Activity className="h-4 w-4 text-emerald-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {dashboardData?.system_metrics.active_jobs_count || 0}
              </div>
              <p className="text-xs text-slate-400">Currently running</p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">CPU Usage</CardTitle>
              <Database className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {dashboardData?.system_metrics.cpu_usage.toFixed(1) || 0}%
              </div>
              <Progress value={dashboardData?.system_metrics.cpu_usage || 0} className="mt-2" />
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Memory Usage</CardTitle>
              <TrendingUp className="h-4 w-4 text-emerald-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {dashboardData?.system_metrics.memory_usage.toFixed(1) || 0}%
              </div>
              <Progress value={dashboardData?.system_metrics.memory_usage || 0} className="mt-2" />
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-slate-200">Disk Usage</CardTitle>
              <Globe className="h-4 w-4 text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-white">
                {dashboardData?.system_metrics.disk_usage.toFixed(1) || 0}%
              </div>
              <Progress value={dashboardData?.system_metrics.disk_usage || 0} className="mt-2" />
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Active Jobs */}
          <div className="lg:col-span-2">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-slate-200">Active Scraping Jobs</CardTitle>
                <CardDescription className="text-slate-400">
                  Real-time monitoring of your data extraction tasks
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {activeJobsArray.length > 0 ? (
                    activeJobsArray.map((job) => (
                      <div key={job.id} className="p-4 rounded-lg bg-slate-700/30">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="font-medium text-white">{job.name}</h3>
                          <div className="flex items-center space-x-2">
                            <Badge 
                              variant={job.status === 'running' ? 'default' : 'secondary'}
                              className={job.status === 'running' ? 'bg-emerald-600' : 'bg-yellow-600'}
                            >
                              {job.status === 'running' ? <Zap className="w-3 h-3 mr-1" /> : <Clock className="w-3 h-3 mr-1" />}
                              {job.status}
                            </Badge>
                          </div>
                        </div>
                        <Progress value={job.progress || 0} className="mb-2" />
                        <div className="flex justify-between text-sm text-slate-400">
                          <span>{job.progress?.toFixed(1) || 0}% complete</span>
                          {job.runtime && <span>Runtime: {Math.floor(job.runtime / 60)}m {Math.floor(job.runtime % 60)}s</span>}
                        </div>
                        {job.success_rate !== undefined && (
                          <div className="text-sm text-slate-400 mt-1">
                            Success rate: {(job.success_rate * 100).toFixed(1)}%
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-slate-400 py-8">
                      No active jobs. Create a new job to get started.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Alerts */}
          <div>
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-slate-200">Recent Alerts</CardTitle>
                <CardDescription className="text-slate-400">
                  System notifications and warnings
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dashboardData?.recent_alerts?.length > 0 ? (
                    dashboardData.recent_alerts.slice(0, 5).map((alert, index) => (
                      <div key={index} className="flex items-start space-x-3">
                        <AlertCircle className={`h-4 w-4 mt-1 ${
                          alert.level === 'error' ? 'text-red-400' : 
                          alert.level === 'warning' ? 'text-yellow-400' : 'text-blue-400'
                        }`} />
                        <div>
                          <p className="text-sm font-medium text-white">{alert.title}</p>
                          <p className="text-xs text-slate-400">{alert.message}</p>
                          <p className="text-xs text-slate-500 mt-1">
                            {new Date(alert.timestamp).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center text-slate-400 py-4">
                      No recent alerts
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-slate-200">Quick Actions</CardTitle>
              <CardDescription className="text-slate-400">
                Get started with common scraping tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <Button 
                  onClick={createNewJob}
                  className="bg-emerald-600 hover:bg-emerald-700"
                >
                  <Play className="w-4 h-4 mr-2" />
                  Create New Job
                </Button>
                <Button 
                  onClick={createTemplateWithWizard}
                  variant="outline" 
                  className="border-slate-600 text-slate-200 hover:bg-slate-700"
                >
                  <Wand2 className="w-4 h-4 mr-2" />
                  Template Wizard
                </Button>
                <Button 
                  variant="outline" 
                  className="border-slate-600 text-slate-200 hover:bg-slate-700"
                >
                  <Globe className="w-4 h-4 mr-2" />
                  Proxy Manager
                </Button>
                <Button 
                  variant="outline" 
                  className="border-slate-600 text-slate-200 hover:bg-slate-700"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export Data
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
