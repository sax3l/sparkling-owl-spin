'use client'

import Layout from '@/src/components/Layout'

export default function MonitoringPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            System Monitoring
          </h1>
          <p className="text-gray-600">
            Real-time systemövervakning och prestationsanalys
          </p>
        </div>

        {/* System Health Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-green-600">98.7%</div>
                <div className="text-sm text-gray-600">System Uptime</div>
                <div className="text-xs text-gray-500">Last 30 days</div>
              </div>
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-blue-600">67%</div>
                <div className="text-sm text-gray-600">CPU Usage</div>
                <div className="text-xs text-gray-500">Average</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-purple-600">8.2 GB</div>
                <div className="text-sm text-gray-600">Memory Usage</div>
                <div className="text-xs text-gray-500">of 16 GB</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-yellow-600">234 ms</div>
                <div className="text-sm text-gray-600">Response Time</div>
                <div className="text-xs text-gray-500">Average</div>
              </div>
            </div>
          </div>
        </div>

        {/* Active Services Status */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-6">Service Status</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { service: 'Web Crawler Engine', status: 'running', uptime: '15 days', load: 'Normal' },
              { service: 'Database Server', status: 'running', uptime: '30 days', load: 'Light' },
              { service: 'Proxy Manager', status: 'warning', uptime: '12 days', load: 'High' },
              { service: 'Data Export Service', status: 'running', uptime: '8 days', load: 'Normal' },
              { service: 'Authentication Service', status: 'running', uptime: '25 days', load: 'Light' },
              { service: 'API Gateway', status: 'running', uptime: '18 days', load: 'Normal' }
            ].map((service, index) => (
              <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">{service.service}</h3>
                  <div className={`w-3 h-3 rounded-full ${
                    service.status === 'running' ? 'bg-green-500' :
                    service.status === 'warning' ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}></div>
                </div>
                <div className="text-sm text-gray-600 space-y-1">
                  <div>Uptime: {service.uptime}</div>
                  <div>Load: {service.load}</div>
                  <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                    service.status === 'running' ? 'bg-green-100 text-green-800' :
                    service.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {service.status.charAt(0).toUpperCase() + service.status.slice(1)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">CPU & Memory Usage</h2>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl text-gray-300 mb-2">📊</div>
                <div className="text-gray-500">Resource usage chart</div>
                <div className="text-sm text-gray-400">Real-time system resources</div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Network Activity</h2>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl text-gray-300 mb-2">🌐</div>
                <div className="text-gray-500">Network traffic chart</div>
                <div className="text-sm text-gray-400">Inbound/Outbound data flow</div>
              </div>
            </div>
          </div>
        </div>

        {/* System Alerts */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Recent Alerts</h2>
          
          <div className="space-y-4">
            {[
              { time: '2024-01-15 14:35', level: 'warning', message: 'High CPU usage detected on crawler-node-3', resolved: false },
              { time: '2024-01-15 14:20', level: 'info', message: 'Database backup completed successfully', resolved: true },
              { time: '2024-01-15 13:45', level: 'error', message: 'Proxy server proxy-eu-2 is unresponsive', resolved: true },
              { time: '2024-01-15 13:30', level: 'warning', message: 'Memory usage above 85% threshold', resolved: false },
              { time: '2024-01-15 12:15', level: 'info', message: 'System maintenance window completed', resolved: true }
            ].map((alert, index) => (
              <div key={index} className={`border-l-4 p-4 rounded-r-lg ${
                alert.level === 'error' ? 'border-red-500 bg-red-50' :
                alert.level === 'warning' ? 'border-yellow-500 bg-yellow-50' :
                'border-blue-500 bg-blue-50'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      alert.level === 'error' ? 'bg-red-500' :
                      alert.level === 'warning' ? 'bg-yellow-500' :
                      'bg-blue-500'
                    }`}></div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">{alert.message}</div>
                      <div className="text-xs text-gray-600">{alert.time}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {alert.resolved ? (
                      <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                        Resolved
                      </span>
                    ) : (
                      <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">
                        Active
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-lg transition-colors">
              Restart Services
            </button>
            <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-3 rounded-lg transition-colors">
              Run Health Check
            </button>
            <button className="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-3 rounded-lg transition-colors">
              Clear Cache
            </button>
            <button className="bg-purple-500 hover:bg-purple-600 text-white px-4 py-3 rounded-lg transition-colors">
              Generate Report
            </button>
          </div>
        </div>
      </div>
    </Layout>
  )
}
