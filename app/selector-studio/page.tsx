'use client'

import Layout from '@/src/components/Layout'

export default function SelectorStudioPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Selector Studio
          </h1>
          <p className="text-gray-600">
            Skapa och testa CSS-selektorer för dina crawl-operationer
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Selector Builder */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">CSS Selector Builder</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target URL
                </label>
                <input
                  type="url"
                  placeholder="https://example.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Selector
                </label>
                <textarea
                  placeholder="div.content > h2.title"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                />
              </div>

              <div className="flex space-x-3">
                <button className="flex-1 bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors">
                  Test Selector
                </button>
                <button className="flex-1 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors">
                  Save Selector
                </button>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t">
              <h3 className="text-lg font-medium mb-3">Quick Selectors</h3>
              <div className="grid grid-cols-2 gap-2">
                {[
                  'h1, h2, h3',
                  '.price, .cost',
                  'a[href]',
                  'img[src]',
                  '.description',
                  'table td'
                ].map((selector, index) => (
                  <button
                    key={index}
                    className="text-left px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-md text-sm transition-colors"
                  >
                    {selector}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Test Results */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Test Results</h2>
            
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center mb-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  <span className="text-sm font-medium text-green-800">5 elements found</span>
                </div>
                <div className="text-sm text-green-700">
                  Selector successfully matched elements on the page
                </div>
              </div>

              <div className="border rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-4 py-2 border-b">
                  <h4 className="font-medium text-gray-900">Matched Elements</h4>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {[
                    { element: 'h2.title', text: 'Fastighet i Stockholm', index: 0 },
                    { element: 'h2.title', text: 'Lägenhet i Göteborg', index: 1 },
                    { element: 'h2.title', text: 'Villa i Malmö', index: 2 },
                    { element: 'h2.title', text: 'Hus i Uppsala', index: 3 },
                    { element: 'h2.title', text: 'Radhus i Linköping', index: 4 }
                  ].map((match, index) => (
                    <div key={index} className="px-4 py-2 border-b last:border-b-0 hover:bg-gray-50">
                      <div className="text-sm font-medium text-gray-900">
                        Element {match.index + 1}: {match.element}
                      </div>
                      <div className="text-sm text-gray-600">
                        {match.text}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Saved Selectors */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Saved Selectors</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[
              { name: 'Property Titles', selector: 'h2.property-title', usage: '12 sites' },
              { name: 'Price Elements', selector: '.price, .cost, .amount', usage: '8 sites' },
              { name: 'Description Text', selector: '.description, .details p', usage: '15 sites' },
              { name: 'Image Sources', selector: 'img.property-image[src]', usage: '10 sites' },
              { name: 'Contact Info', selector: '.contact, .phone, .email', usage: '6 sites' },
              { name: 'Location Data', selector: '.address, .location', usage: '18 sites' }
            ].map((saved, index) => (
              <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="font-medium text-gray-900">{saved.name}</h3>
                  <span className="text-xs text-gray-500">{saved.usage}</span>
                </div>
                <div className="text-sm text-gray-600 mb-3 font-mono bg-gray-50 p-2 rounded">
                  {saved.selector}
                </div>
                <div className="flex space-x-2">
                  <button className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded hover:bg-blue-200 transition-colors">
                    Test
                  </button>
                  <button className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded hover:bg-green-200 transition-colors">
                    Use
                  </button>
                  <button className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded hover:bg-red-200 transition-colors">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  )
}
