'use client'

import Layout from '@/src/components/Layout'

export default function PersonsPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Persondata
          </h1>
          <p className="text-gray-600">
            Hantera och visualisera persondata från dina crawl-operationer
          </p>
        </div>

        {/* Person Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">15,234</div>
                <div className="text-sm text-gray-600">Totalt personer</div>
                <div className="text-xs text-gray-500">I databasen</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">92%</div>
                <div className="text-sm text-gray-600">Datacache</div>
                <div className="text-xs text-gray-500">Kvalitet</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">523</div>
                <div className="text-sm text-gray-600">Nya idag</div>
                <div className="text-xs text-gray-500">Registrerade</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">95.2%</div>
                <div className="text-sm text-gray-600">Success rate</div>
                <div className="text-xs text-gray-500">Senaste veckan</div>
              </div>
            </div>
          </div>
        </div>

        {/* Person Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Filtrera personer</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Yrkeskategori
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Alla kategorier</option>
                <option>Ledning & Administration</option>
                <option>IT & Teknik</option>
                <option>Försäljning & Marknadsföring</option>
                <option>Ekonomi & Redovisning</option>
                <option>Personal & HR</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Företagsstorlek
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
                Stad/Ort
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

        {/* Person List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Senaste personer</h2>
            <div className="flex space-x-2">
              <button className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors">
                GDPR-export
              </button>
              <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors">
                Exportera data
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Namn
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Roll/Titel
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Företag
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Stad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Källa
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
                    name: 'Anna Lindström', 
                    title: 'VD', 
                    company: 'TechSolution AB', 
                    city: 'Stockholm', 
                    source: 'Allabolag.se', 
                    updated: '2024-01-15', 
                    status: 'Verified' 
                  },
                  { 
                    name: 'Erik Johansson', 
                    title: 'IT-Chef', 
                    company: 'Byggnordic Sverige AB', 
                    city: 'Göteborg', 
                    source: 'LinkedIn', 
                    updated: '2024-01-15', 
                    status: 'Verified' 
                  },
                  { 
                    name: 'Maria Andersson', 
                    title: 'Ekonomichef', 
                    company: 'Handel & Service HB', 
                    city: 'Malmö', 
                    source: 'Bolagsverket', 
                    updated: '2024-01-14', 
                    status: 'Pending' 
                  },
                  { 
                    name: 'Lars Nilsson', 
                    title: 'Säljchef', 
                    company: 'Transport Express AB', 
                    city: 'Uppsala', 
                    source: 'Företag.se', 
                    updated: '2024-01-14', 
                    status: 'Verified' 
                  },
                  { 
                    name: 'Sofia Karlsson', 
                    title: 'Produktionschef', 
                    company: 'IndustriMaker AB', 
                    city: 'Linköping', 
                    source: 'Proff.se', 
                    updated: '2024-01-13', 
                    status: 'Error' 
                  }
                ].map((person, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {person.name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="bg-blue-100 px-2 py-1 rounded text-xs">
                        {person.title}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {person.company}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {person.city}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="bg-purple-100 px-2 py-1 rounded text-xs">
                        {person.source}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {person.updated}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        person.status === 'Verified' ? 'bg-green-100 text-green-800' :
                        person.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {person.status}
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
              <span className="font-medium">15,234</span> resultat
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

          {/* GDPR Notice */}
          <div className="mt-6 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm text-blue-700">
                  <strong>GDPR-notering:</strong> All persondata hanteras enligt GDPR-bestämmelser. 
                  Kontaktpersoner kan begära utdrag eller radering av sina uppgifter.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
