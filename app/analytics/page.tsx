'use client'

import Layout from '@/src/components/Layout'

export default function AnalyticsPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Användaranalys
          </h1>
          <p className="text-gray-600">
            Djupgående analys av dina crawl-operationer och datahantering
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center">
              <div className="flex-1">
                <div className="text-2xl font-bold text-gray-900">24,569</div>
                <div className="text-sm text-gray-600">Sidor crawlade idag</div>
                <div className="text-xs text-green-600 mt-1">↑ +12% från igår</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center">
              <div className="flex-1">
                <div className="text-2xl font-bold text-gray-900">97.8%</div>
                <div className="text-sm text-gray-600">Success Rate</div>
                <div className="text-xs text-green-600 mt-1">↑ +2.1% från förra veckan</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center">
              <div className="flex-1">
                <div className="text-2xl font-bold text-gray-900">1,247</div>
                <div className="text-sm text-gray-600">Aktiva Crawlers</div>
                <div className="text-xs text-blue-600 mt-1">15 schemalagda</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="flex items-center">
              <div className="flex-1">
                <div className="text-2xl font-bold text-gray-900">156 GB</div>
                <div className="text-sm text-gray-600">Data samlad</div>
                <div className="text-xs text-gray-600 mt-1">Denna månad</div>
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Crawl Activity (7 dagar)</h2>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl text-gray-300 mb-2">📊</div>
                <div className="text-gray-500">Chart visualization would appear here</div>
                <div className="text-sm text-gray-400">Showing crawl volume over time</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4">Success Rate Trend</h2>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <div className="text-4xl text-gray-300 mb-2">📈</div>
                <div className="text-gray-500">Success rate chart would appear here</div>
                <div className="text-sm text-gray-400">Tracking success rate over time</div>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Table */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Site Performance</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Site
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Pages Crawled
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Response Time
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Crawl
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {[
                  { site: 'hemnet.se', pages: '8,234', success: '98.5%', response: '1.2s', last: '2 min ago' },
                  { site: 'booli.se', pages: '5,678', success: '96.8%', response: '0.8s', last: '5 min ago' },
                  { site: 'svenskfast.se', pages: '3,456', success: '94.2%', response: '2.1s', last: '12 min ago' },
                  { site: 'lansfast.se', pages: '2,123', success: '97.9%', response: '1.5s', last: '8 min ago' },
                  { site: 'fastighetsbyran.se', pages: '4,567', success: '95.7%', response: '1.8s', last: '3 min ago' }
                ].map((site, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {site.site}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {site.pages}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        parseFloat(site.success) > 97 ? 'bg-green-100 text-green-800' :
                        parseFloat(site.success) > 95 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {site.success}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {site.response}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {site.last}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Data Quality Insights */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Data Quality Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">89%</div>
              <div className="text-sm text-gray-600">Complete Data Records</div>
              <div className="text-xs text-gray-500 mt-1">18,342 av 20,567 records</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">94%</div>
              <div className="text-sm text-gray-600">Data Accuracy</div>
              <div className="text-xs text-gray-500 mt-1">Baserat på validering</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">12h</div>
              <div className="text-sm text-gray-600">Avg Data Freshness</div>
              <div className="text-xs text-gray-500 mt-1">Senaste uppdatering</div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
