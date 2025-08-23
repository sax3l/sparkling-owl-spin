'use client'

import Layout from '@/src/components/Layout'

export default function VehiclesPage() {
  return (
    <Layout>
      <div className="container mx-auto p-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Fordonsdata
          </h1>
          <p className="text-gray-600">
            Hantera och visualisera fordonsdata från dina crawl-operationer
          </p>
        </div>

        {/* Vehicle Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">3,456</div>
                <div className="text-sm text-gray-600">Totalt fordon</div>
                <div className="text-xs text-gray-500">I databasen</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">91%</div>
                <div className="text-sm text-gray-600">Datacache</div>
                <div className="text-xs text-gray-500">Kvalitet</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">234</div>
                <div className="text-sm text-gray-600">Nya idag</div>
                <div className="text-xs text-gray-500">Registrerade</div>
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold text-gray-900">98.1%</div>
                <div className="text-sm text-gray-600">Success rate</div>
                <div className="text-xs text-gray-500">Senaste veckan</div>
              </div>
            </div>
          </div>
        </div>

        {/* Vehicle Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Filtrera fordon</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Märke
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Alla märken</option>
                <option>Volvo</option>
                <option>Saab</option>
                <option>BMW</option>
                <option>Mercedes-Benz</option>
                <option>Volkswagen</option>
                <option>Toyota</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Årsmodell
              </label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  placeholder="Från"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="number"
                  placeholder="Till"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Drivmedel
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Alla drivmedel</option>
                <option>Bensin</option>
                <option>Diesel</option>
                <option>El</option>
                <option>Hybrid</option>
                <option>Gas</option>
              </select>
            </div>

            <div className="flex items-end">
              <button className="w-full bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors">
                Sök
              </button>
            </div>
          </div>
        </div>

        {/* Vehicle List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold">Senaste fordon</h2>
            <button className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors">
              Exportera data
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Registreringsnummer
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Märke & Modell
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Årsmodell
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Drivmedel
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Ägare
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
                    reg: 'ABC123', 
                    make: 'Volvo XC90', 
                    year: '2022', 
                    fuel: 'Hybrid', 
                    owner: 'Anna Andersson', 
                    updated: '2024-01-15', 
                    status: 'Verified' 
                  },
                  { 
                    reg: 'XYZ789', 
                    make: 'BMW X5', 
                    year: '2021', 
                    fuel: 'Diesel', 
                    owner: 'Erik Eriksson', 
                    updated: '2024-01-15', 
                    status: 'Verified' 
                  },
                  { 
                    reg: 'DEF456', 
                    make: 'Tesla Model 3', 
                    year: '2023', 
                    fuel: 'El', 
                    owner: 'Maria Larsson', 
                    updated: '2024-01-14', 
                    status: 'Pending' 
                  },
                  { 
                    reg: 'GHI789', 
                    make: 'Mercedes GLC', 
                    year: '2020', 
                    fuel: 'Bensin', 
                    owner: 'Johan Johansson', 
                    updated: '2024-01-14', 
                    status: 'Verified' 
                  },
                  { 
                    reg: 'JKL012', 
                    make: 'Volkswagen ID.4', 
                    year: '2023', 
                    fuel: 'El', 
                    owner: 'Sara Nilsson', 
                    updated: '2024-01-13', 
                    status: 'Error' 
                  }
                ].map((vehicle, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {vehicle.reg}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {vehicle.make}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {vehicle.year}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <span className="bg-gray-100 px-2 py-1 rounded text-xs">
                        {vehicle.fuel}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {vehicle.owner}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {vehicle.updated}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        vehicle.status === 'Verified' ? 'bg-green-100 text-green-800' :
                        vehicle.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {vehicle.status}
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
              <span className="font-medium">3,456</span> resultat
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
