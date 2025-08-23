'use client'

import Layout from '@/src/components/Layout'

export default function CompaniesPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Företagsdata
          </h1>
          <p className="text-gray-600">
            Hantera och visualisera företagsdata från dina crawl-operationer
          </p>
        </div>

        {/* Company Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">2,845</div>
                <div className="text-sm text-gray-600">Totalt företag</div>
                <div className="text-xs text-gray-500">I databasen</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">94%</div>
                <div className="text-sm text-gray-600">Datacache</div>
                <div className="text-xs text-gray-500">Kvalitet</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">187</div>
                <div className="text-sm text-gray-600">Nya idag</div>
                <div className="text-xs text-gray-500">Registrerade</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">96.7%</div>
                <div className="text-sm text-gray-600">Success rate</div>
                <div className="text-xs text-gray-500">Senaste veckan</div>
              </div>
            </div>
          </div>
        </div>

        {/* Company Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Filtrera företag</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Bransch
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Alla branscher</option>
                <option>IT & Teknik</option>
                <option>Bygg & Anläggning</option>
                <option>Handel</option>
                <option>Transport</option>
                <option>Tillverkning</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Antal anställda
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Alla storlekar</option>
                <option>1-10</option>
                <option>11-50</option>
                <option>51-250</option>
                <option>250+</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stad/Kommun
              </label>
              <input
                type="text"
                placeholder="T.ex. Stockholm"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-end">
              <button className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors">
                Sök
              </button>
            </div>
          </div>
        </div>

        {/* Company List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Senaste företag</h2>
            <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors">
              Exportera data
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Företagsnamn
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Org.nummer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Bransch
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Stad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Anställda
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Senast uppdaterad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {[
                  { 
                    name: 'TechSolution AB', 
                    orgNr: '556123-4567', 
                    industry: 'IT & Teknik', 
                    city: 'Stockholm', 
                    employees: '25-50', 
                    updated: '2024-01-15', 
                    status: 'Verified' 
                  },
                  { 
                    name: 'Byggnordic Sverige AB', 
                    orgNr: '556234-5678', 
                    industry: 'Bygg & Anläggning', 
                    city: 'Göteborg', 
                    employees: '100-250', 
                    updated: '2024-01-15', 
                    status: 'Verified' 
                  },
                  { 
                    name: 'Handel & Service HB', 
                    orgNr: '969345-6789', 
                    industry: 'Handel', 
                    city: 'Malmö', 
                    employees: '5-10', 
                    updated: '2024-01-14', 
                    status: 'Pending' 
                  },
                  { 
                    name: 'Transport Express AB', 
                    orgNr: '556456-7890', 
                    industry: 'Transport', 
                    city: 'Uppsala', 
                    employees: '50-100', 
                    updated: '2024-01-14', 
                    status: 'Verified' 
                  },
                  { 
                    name: 'IndustriMaker AB', 
                    orgNr: '556567-8901', 
                    industry: 'Tillverkning', 
                    city: 'Linköping', 
                    employees: '250+', 
                    updated: '2024-01-13', 
                    status: 'Error' 
                  }
                ].map((company, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {company.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500">
                      {company.orgNr}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                        {company.industry}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {company.city}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {company.employees}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {company.updated}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        company.status === 'Verified' ? 'bg-green-100 text-green-800' :
                        company.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {company.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex items-center justify-between mt-6">
            <div className="text-sm text-gray-700">
              Visar <span className="font-medium">1</span> till <span className="font-medium">5</span> av{' '}
              <span className="font-medium">2,845</span> resultat
            </div>
            <div className="flex space-x-2">
              <button className="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                Föregående
              </button>
              <button className="px-3 py-1 bg-blue-500 text-white rounded-md text-sm">
                1
              </button>
              <button className="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                2
              </button>
              <button className="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                3
              </button>
              <button className="px-3 py-1 border border-gray-300 rounded-md text-sm hover:bg-gray-50">
                Nästa
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
