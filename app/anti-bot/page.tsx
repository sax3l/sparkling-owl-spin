'use client'

import Layout from '@/src/components/Layout'

export default function AntiBotPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Anti-Bot Protection
          </h1>
          <p className="text-gray-600">
            Konfigurera och övervaka bot-skyddsmekanismer för dina crawl-operationer
          </p>
        </div>

        {/* Protection Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">Active</div>
                <div className="text-sm text-gray-600">Protection Status</div>
              </div>
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">847</div>
                <div className="text-sm text-gray-600">Requests Analyzed</div>
                <div className="text-xs text-gray-500">Last 24h</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">12</div>
                <div className="text-sm text-gray-600">Blocked Attempts</div>
                <div className="text-xs text-gray-500">This hour</div>
              </div>
            </div>
          </div>
        </div>

        {/* Protection Methods */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-6">Protection Methods</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">User-Agent Rotation</div>
                  <div className="text-sm text-gray-600">Rotate browser identities</div>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm text-green-700 font-medium">Enabled</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Request Delays</div>
                  <div className="text-sm text-gray-600">Random delays between requests</div>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm text-green-700 font-medium">2-8s range</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Header Spoofing</div>
                  <div className="text-sm text-gray-600">Mimic real browser headers</div>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm text-green-700 font-medium">Active</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">CAPTCHA Solving</div>
                  <div className="text-sm text-gray-600">Automated CAPTCHA handling</div>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></div>
                  <span className="text-sm text-yellow-700 font-medium">Manual</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">JavaScript Rendering</div>
                  <div className="text-sm text-gray-600">Handle dynamic content</div>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm text-green-700 font-medium">Enabled</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Behavioral Patterns</div>
                  <div className="text-sm text-gray-600">Simulate human-like behavior</div>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                  <span className="text-sm text-blue-700 font-medium">Learning</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Configuration */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-6">Configuration</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Request Delay Range (seconds)
                </label>
                <div className="flex space-x-2">
                  <input
                    type="number"
                    value="2"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="self-center text-gray-500">to</span>
                  <input
                    type="number"
                    value="8"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Concurrent Requests
                </label>
                <input
                  type="number"
                  value="5"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  User-Agent Strategy
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Random Rotation</option>
                  <option>Fixed Desktop</option>
                  <option>Mobile Only</option>
                  <option>Custom List</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CAPTCHA Service
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>2captcha</option>
                  <option>Anti-Captcha</option>
                  <option>Manual Solving</option>
                  <option>Disabled</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  JavaScript Timeout (ms)
                </label>
                <input
                  type="number"
                  value="30000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Retry Strategy
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>Exponential Backoff</option>
                  <option>Linear Backoff</option>
                  <option>Fixed Delay</option>
                  <option>No Retry</option>
                </select>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-md transition-colors">
              Reset to Default
            </button>
            <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors">
              Save Configuration
            </button>
          </div>
        </div>

        {/* Recent Activity Log */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Protection Activity</h2>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Event Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Target Site
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action Taken
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {[
                  { time: '14:32:15', type: 'CAPTCHA Detected', site: 'hemnet.se', action: 'Solving in progress', status: 'processing' },
                  { time: '14:31:42', type: 'Rate Limit', site: 'booli.se', action: 'Delay applied (5s)', status: 'resolved' },
                  { time: '14:30:18', type: 'Bot Challenge', site: 'svenskfast.se', action: 'JS execution', status: 'success' },
                  { time: '14:29:55', type: 'Proxy Rotation', site: 'lansfast.se', action: 'IP changed', status: 'success' },
                  { time: '14:28:33', type: 'User-Agent Rotate', site: 'fastighetsbyran.se', action: 'Chrome → Firefox', status: 'success' }
                ].map((activity, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.time}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {activity.type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.site}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.action}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        activity.status === 'success' ? 'bg-green-100 text-green-800' :
                        activity.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        activity.status === 'resolved' ? 'bg-blue-100 text-blue-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {activity.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </Layout>
  )
}
