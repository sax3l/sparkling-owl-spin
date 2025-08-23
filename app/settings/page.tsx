'use client'

import Layout from '@/src/components/Layout'

export default function SettingsPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Systeminställningar
          </h1>
          <p className="text-gray-600">
            Konfigurera systemparametrar och användarinställningar
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Settings Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-lg font-semibold mb-4">Kategorier</h2>
              <nav className="space-y-2">
                {[
                  { name: 'General', active: true },
                  { name: 'Crawling', active: false },
                  { name: 'Database', active: false },
                  { name: 'Security', active: false },
                  { name: 'Notifications', active: false },
                  { name: 'Performance', active: false },
                  { name: 'API', active: false }
                ].map((item, index) => (
                  <button
                    key={index}
                    className={`w-full text-left px-3 py-2 rounded-md transition-colors ${
                      item.active 
                        ? 'bg-blue-100 text-blue-900 font-medium' 
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    {item.name}
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Settings Content */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-6">General Settings</h2>
              
              <div className="space-y-6">
                {/* System Information */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-medium mb-4">System Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-600">Version:</div>
                      <div className="font-medium">ECaDP v2.1.4</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Build:</div>
                      <div className="font-medium">2024.01.15.1432</div>
                    </div>
                    <div>
                      <div className="text-gray-600">Environment:</div>
                      <div className="font-medium">Production</div>
                    </div>
                    <div>
                      <div className="text-gray-600">License:</div>
                      <div className="font-medium">Enterprise</div>
                    </div>
                  </div>
                </div>

                {/* Application Settings */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-medium mb-4">Application Settings</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        System Name
                      </label>
                      <input
                        type="text"
                        value="ECaDP Production"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Default Timezone
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option>Europe/Stockholm</option>
                        <option>UTC</option>
                        <option>Europe/London</option>
                        <option>America/New_York</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Session Timeout (minutes)
                      </label>
                      <input
                        type="number"
                        value="30"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Language
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option>Svenska</option>
                        <option>English</option>
                        <option>Deutsch</option>
                        <option>Français</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Performance Settings */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-medium mb-4">Performance Settings</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium text-gray-700">
                          Max Concurrent Workers
                        </label>
                        <span className="text-sm text-gray-500">Current: 8</span>
                      </div>
                      <input
                        type="range"
                        min="1"
                        max="20"
                        value="8"
                        className="w-full"
                      />
                    </div>

                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-sm font-medium text-gray-700">
                          Memory Limit per Worker (MB)
                        </label>
                        <span className="text-sm text-gray-500">Current: 512MB</span>
                      </div>
                      <input
                        type="range"
                        min="256"
                        max="2048"
                        value="512"
                        className="w-full"
                      />
                    </div>

                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        id="auto-scaling"
                        checked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="auto-scaling" className="text-sm text-gray-700">
                        Enable automatic worker scaling
                      </label>
                    </div>
                  </div>
                </div>

                {/* Data Retention */}
                <div className="border-b pb-6">
                  <h3 className="text-lg font-medium mb-4">Data Retention</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Raw Data Retention (days)
                      </label>
                      <input
                        type="number"
                        value="90"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Log Files Retention (days)
                      </label>
                      <input
                        type="number"
                        value="30"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Analytics Data Retention (days)
                      </label>
                      <input
                        type="number"
                        value="365"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>

                {/* Backup Settings */}
                <div>
                  <h3 className="text-lg font-medium mb-4">Backup Settings</h3>
                  
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <input
                        type="checkbox"
                        id="auto-backup"
                        checked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="auto-backup" className="text-sm text-gray-700">
                        Enable automatic backups
                      </label>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Backup Schedule
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option>Daily at 02:00</option>
                        <option>Every 12 hours</option>
                        <option>Weekly</option>
                        <option>Custom</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Backup Location
                      </label>
                      <input
                        type="text"
                        value="/backup/ecadp"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Save Button */}
              <div className="flex justify-end space-x-3 mt-8 pt-6 border-t">
                <button className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-md transition-colors">
                  Reset to Default
                </button>
                <button className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md transition-colors">
                  Save Settings
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
