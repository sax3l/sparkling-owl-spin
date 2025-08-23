'use client'

import Layout from '@/src/components/Layout'

export default function ProxiesPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Proxy Management
          </h1>
          <p className="text-gray-600">
            Hantera och övervaka dina proxy-servrar för optimal prestanda
          </p>
        </div>

        {/* Proxy Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">12</div>
                <div className="text-sm text-gray-600">Active Proxies</div>
              </div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">3</div>
                <div className="text-sm text-gray-600">Warning State</div>
              </div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">2</div>
                <div className="text-sm text-gray-600">Offline</div>
              </div>
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">847ms</div>
                <div className="text-sm text-gray-600">Avg Response</div>
              </div>
              <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            </div>
          </div>
        </div>

        {/* Add New Proxy */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Add New Proxy</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              placeholder="IP Address"
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="number"
              placeholder="Port"
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <select className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option>HTTP</option>
              <option>HTTPS</option>
              <option>SOCKS5</option>
            </select>
            <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors">
              Add Proxy
            </button>
          </div>
        </div>

        {/* Proxy List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Proxy Servers</h2>
            <div className="flex space-x-2">
              <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md text-sm transition-colors">
                Test All
              </button>
              <button className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-md text-sm transition-colors">
                Refresh Status
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    IP Address
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Port
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Response Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Check
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {[
                  { status: 'active', ip: '192.168.1.10', port: '8080', type: 'HTTP', response: '234ms', location: 'Stockholm', lastCheck: '2 min ago' },
                  { status: 'active', ip: '10.0.0.15', port: '3128', type: 'HTTPS', response: '567ms', location: 'Göteborg', lastCheck: '1 min ago' },
                  { status: 'warning', ip: '172.16.0.20', port: '1080', type: 'SOCKS5', response: '1.2s', location: 'Malmö', lastCheck: '5 min ago' },
                  { status: 'active', ip: '192.168.2.25', port: '8080', type: 'HTTP', response: '345ms', location: 'Uppsala', lastCheck: '3 min ago' },
                  { status: 'offline', ip: '10.1.1.30', port: '3128', type: 'HTTPS', response: 'Timeout', location: 'Linköping', lastCheck: '15 min ago' },
                  { status: 'active', ip: '172.20.0.35', port: '8080', type: 'HTTP', response: '456ms', location: 'Västerås', lastCheck: '1 min ago' },
                  { status: 'warning', ip: '192.168.3.40', port: '1080', type: 'SOCKS5', response: '1.5s', location: 'Örebro', lastCheck: '8 min ago' }
                ].map((proxy, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full mr-2 ${
                          proxy.status === 'active' ? 'bg-green-500' :
                          proxy.status === 'warning' ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}></div>
                        <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                          proxy.status === 'active' ? 'bg-green-100 text-green-800' :
                          proxy.status === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {proxy.status.charAt(0).toUpperCase() + proxy.status.slice(1)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      {proxy.ip}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {proxy.port}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                        {proxy.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {proxy.response}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {proxy.location}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {proxy.lastCheck}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-800 text-xs">Test</button>
                        <button className="text-yellow-600 hover:text-yellow-800 text-xs">Edit</button>
                        <button className="text-red-600 hover:text-red-800 text-xs">Remove</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Proxy Performance Chart */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Proxy Performance Over Time</h2>
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <div className="text-4xl text-gray-300 mb-2">📊</div>
              <div className="text-gray-500">Performance chart would appear here</div>
              <div className="text-sm text-gray-400">Showing response times and success rates</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
