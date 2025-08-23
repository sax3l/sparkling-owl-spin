'use client'

import Layout from '@/src/components/Layout'

export default function ExportPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Data Export
          </h1>
          <p className="text-gray-600">
            Exportera och ladda ner dina crawl-data i olika format
          </p>
        </div>

        {/* Export Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">156</div>
                <div className="text-sm text-gray-600">Total Exports</div>
                <div className="text-xs text-gray-500">This month</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">2.3 GB</div>
                <div className="text-sm text-gray-600">Data Exported</div>
                <div className="text-xs text-gray-500">This month</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">12</div>
                <div className="text-sm text-gray-600">Scheduled Exports</div>
                <div className="text-xs text-gray-500">Active</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">97.8%</div>
                <div className="text-sm text-gray-600">Success Rate</div>
                <div className="text-xs text-gray-500">Last 30 days</div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Export */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-6">Quick Export</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Source
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>All Data</option>
                  <option>Properties</option>
                  <option>Vehicles</option>
                  <option>Companies</option>
                  <option>Persons</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Date Range
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <input
                    type="date"
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="date"
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Export Format
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>CSV</option>
                  <option>JSON</option>
                  <option>Excel (XLSX)</option>
                  <option>XML</option>
                  <option>Parquet</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Columns to Include
                </label>
                <div className="space-y-2 max-h-32 overflow-y-auto border rounded-md p-3">
                  {['ID', 'URL', 'Title', 'Price', 'Location', 'Description', 'Images', 'Created Date', 'Modified Date'].map((column, index) => (
                    <label key={index} className="flex items-center">
                      <input
                        type="checkbox"
                        defaultChecked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded mr-2"
                      />
                      <span className="text-sm text-gray-700">{column}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Compression
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                  <option>None</option>
                  <option>ZIP</option>
                  <option>GZIP</option>
                  <option>BZIP2</option>
                </select>
              </div>

              <button className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-3 rounded-md transition-colors">
                Start Export
              </button>
            </div>
          </div>
        </div>

        {/* Scheduled Exports */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Scheduled Exports</h2>
            <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors">
              Create Schedule
            </button>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Data Source
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Format
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Schedule
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Run
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {[
                  { name: 'Daily Properties Report', source: 'Properties', format: 'CSV', schedule: 'Daily 06:00', lastRun: '2024-01-15 06:00', status: 'success' },
                  { name: 'Weekly Vehicle Data', source: 'Vehicles', format: 'JSON', schedule: 'Weekly Mon 08:00', lastRun: '2024-01-14 08:00', status: 'success' },
                  { name: 'Monthly Full Export', source: 'All Data', format: 'Excel', schedule: 'Monthly 1st 02:00', lastRun: '2024-01-01 02:00', status: 'success' },
                  { name: 'Company Analytics', source: 'Companies', format: 'XML', schedule: 'Daily 18:00', lastRun: '2024-01-15 18:00', status: 'running' }
                ].map((schedule, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {schedule.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {schedule.source}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                        {schedule.format}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {schedule.schedule}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {schedule.lastRun}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        schedule.status === 'success' ? 'bg-green-100 text-green-800' :
                        schedule.status === 'running' ? 'bg-blue-100 text-blue-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {schedule.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <div className="flex space-x-2">
                        <button className="text-blue-600 hover:text-blue-800 text-xs">Edit</button>
                        <button className="text-green-600 hover:text-green-800 text-xs">Run Now</button>
                        <button className="text-red-600 hover:text-red-800 text-xs">Delete</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Exports */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-6">Recent Exports</h2>
          
          <div className="space-y-4">
            {[
              { name: 'properties_2024-01-15.csv', size: '245 MB', time: '2024-01-15 14:32', status: 'completed', download: true },
              { name: 'vehicles_weekly.json', size: '87 MB', time: '2024-01-15 14:15', status: 'completed', download: true },
              { name: 'companies_export.xlsx', size: '156 MB', time: '2024-01-15 13:45', status: 'processing', download: false },
              { name: 'analytics_data.xml', size: '312 MB', time: '2024-01-15 12:30', status: 'failed', download: false },
              { name: 'full_backup.zip', size: '2.1 GB', time: '2024-01-15 11:00', status: 'completed', download: true }
            ].map((exportItem, index) => (
              <div key={index} className="flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-shadow">
                <div className="flex-1">
                  <div className="font-medium text-gray-900">{exportItem.name}</div>
                  <div className="text-sm text-gray-600">
                    {exportItem.size} • {exportItem.time}
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    exportItem.status === 'completed' ? 'bg-green-100 text-green-800' :
                    exportItem.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {exportItem.status}
                  </span>
                  {exportItem.download && (
                    <button className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-xs transition-colors">
                      Download
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}
