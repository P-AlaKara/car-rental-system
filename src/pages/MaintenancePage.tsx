import * as React from 'react'
import { fetchCars, toggleCarMaintenance, type Car } from '../lib/api'
import ImageCarousel from '../components/ImageCarousel'
import CarDetailModal from '../components/CarDetailModal'

const MaintenancePage: React.FC = () => {
  const [cars, setCars] = React.useState<Car[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [searchTerm, setSearchTerm] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState('all')
  const [viewMode, setViewMode] = React.useState<'grid' | 'table'>('table')
  const [selectedCar, setSelectedCar] = React.useState<Car | null>(null)
  const [isCarDetailModalOpen, setIsCarDetailModalOpen] = React.useState(false)
  const [selectedCarId, setSelectedCarId] = React.useState<number | null>(null)

  React.useEffect(() => {
    loadCars()
  }, [])

  const loadCars = async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('MaintenancePage: Loading cars...')
      const response = await fetchCars()
      console.log('MaintenancePage: Cars loaded:', response)
      setCars(response.data.data)
    } catch (err) {
      console.error('MaintenancePage: Error loading cars:', err)
      setError('Failed to load cars')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleMaintenance = async (carId: number) => {
    try {
      console.log('MaintenancePage: Toggling maintenance for car:', carId)
      await toggleCarMaintenance(carId)
      console.log('MaintenancePage: Maintenance toggle successful')
      
      // Refresh the cars list
      await loadCars()
      
      // Update selected car if it's currently open
      if (selectedCar && selectedCar.id === carId) {
        const updatedCar = cars.find(car => car.id === carId)
        if (updatedCar) {
          setSelectedCar(updatedCar)
        }
      }
    } catch (err) {
      console.error('MaintenancePage: Error toggling maintenance:', err)
      setError('Failed to update maintenance status')
    }
  }

  const openCarDetail = (car: Car) => {
    setSelectedCarId(car.id)
    setSelectedCar(car)
    setIsCarDetailModalOpen(true)
  }

  const closeCarDetail = () => {
    setSelectedCarId(null)
    setSelectedCar(null)
    setIsCarDetailModalOpen(false)
  }

  // Filter cars based on search and status
  const filteredCars = cars.filter(car => {
    const matchesSearch = searchTerm === '' || 
      car.make.toLowerCase().includes(searchTerm.toLowerCase()) ||
      car.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
      car.license_plate.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = statusFilter === 'all' || car.status === statusFilter

    return matchesSearch && matchesStatus
  })

  // Calculate car statistics
  const carStats = React.useMemo(() => {
    const total = cars.length
    const available = cars.filter(car => car.status === 'Available').length
    const underMaintenance = cars.filter(car => car.status === 'Under_maintenance').length
    const disabled = cars.filter(car => car.status === 'Disabled').length
    const serviceDue = cars.filter(car => 
      (car.current_odometer - car.last_service_odometer) >= car.service_threshold_km
    ).length

    return { total, available, underMaintenance, disabled, serviceDue }
  }, [cars])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
        <span className="ml-2 text-gray-600">Loading cars...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <button
          onClick={loadCars}
          className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Maintenance Management</h2>
          <p className="text-gray-600">Track vehicle maintenance and service schedules</p>
        </div>
      </div>

      {/* Car Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-900">{carStats.total}</div>
          <div className="text-sm text-gray-600">Total Cars</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">{carStats.available}</div>
          <div className="text-sm text-gray-600">Available</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-orange-600">{carStats.underMaintenance}</div>
          <div className="text-sm text-gray-600">Under Maintenance</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-red-600">{carStats.disabled}</div>
          <div className="text-sm text-gray-600">Disabled</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{carStats.serviceDue}</div>
          <div className="text-sm text-gray-600">Service Due</div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex flex-wrap gap-4 items-center justify-between">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Search cars by make, model, or license plate..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
              >
                <option value="all">All Status</option>
                <option value="Available">Available</option>
                <option value="Under_maintenance">Under Maintenance</option>
                <option value="Disabled">Disabled</option>
              </select>
            </div>
          </div>
          
          {/* View Mode Toggle */}
          <div className="flex border border-gray-300 rounded-lg">
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-2 text-sm font-medium rounded-l-lg transition-colors ${
                viewMode === 'table' 
                  ? 'bg-sky-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 6h18m-18 8h18m-18 4h18" />
              </svg>
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 text-sm font-medium rounded-r-lg transition-colors ${
                viewMode === 'grid' 
                  ? 'bg-sky-600 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Cars Display */}
      {viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCars.map((car) => {
            const kmSinceService = car.current_odometer - car.last_service_odometer
            const serviceDue = kmSinceService >= car.service_threshold_km
            
            return (
              <div 
                key={car.id} 
                className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => openCarDetail(car)}
              >
                {/* Car Image */}
                <div className="relative h-48 bg-gray-100">
                  <ImageCarousel
                    images={car.images || []}
                    alt={`${car.make} ${car.model}`}
                    className="h-full"
                  />
                  <div className="absolute top-3 right-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      car.status === 'Available' ? 'bg-green-100 text-green-800' :
                      car.status === 'Under_maintenance' ? 'bg-orange-100 text-orange-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {car.status.replace('_', ' ')}
                    </span>
                  </div>
                  {serviceDue && (
                    <div className="absolute top-3 left-3">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        Service Due
                      </span>
                    </div>
                  )}
                </div>
                
                {/* Car Details */}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg">{car.make} {car.model} ({car.year})</h3>
                      <p className="text-sm text-gray-600">{car.license_plate}</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Current Odometer:</span>
                      <span className="font-medium">{car.current_odometer.toLocaleString()} km</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Last Service:</span>
                      <span className="font-medium">{car.last_service_odometer.toLocaleString()} km</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-600">Service Status:</span>
                      {serviceDue ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Due ({kmSinceService.toLocaleString()} km)
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          OK ({(car.service_threshold_km - kmSinceService).toLocaleString()} km left)
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        openCarDetail(car)
                      }}
                      className="flex-1 px-3 py-2 text-sm bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors"
                    >
                      View Details
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleToggleMaintenance(car.id)
                      }}
                      className={`flex-1 px-3 py-2 text-sm rounded-lg transition-colors ${
                        car.status === 'Under_maintenance' 
                          ? 'bg-green-600 text-white hover:bg-green-700'
                          : 'bg-orange-600 text-white hover:bg-orange-700'
                      }`}
                    >
                      {car.status === 'Under_maintenance' ? 'Remove from Maintenance' : 'Put in Maintenance'}
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Cars Table */}
      {viewMode === 'table' && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vehicle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Odometer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service Due</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredCars.map((car) => {
                  const kmSinceService = car.current_odometer - car.last_service_odometer
                  const serviceDue = kmSinceService >= car.service_threshold_km
                  
                  return (
                    <tr 
                      key={car.id} 
                      className="hover:bg-gray-50 cursor-pointer"
                      onClick={() => openCarDetail(car)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="w-12 h-12 rounded-lg overflow-hidden mr-4">
                            <ImageCarousel
                              images={car.images || []}
                              alt={`${car.make} ${car.model}`}
                              className="w-full h-full"
                            />
                          </div>
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {car.make} {car.model} ({car.year})
                            </div>
                            <div className="text-sm text-gray-500">{car.license_plate}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          car.status === 'Available' ? 'bg-green-100 text-green-800' :
                          car.status === 'Under_maintenance' ? 'bg-orange-100 text-orange-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {car.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div>{car.current_odometer.toLocaleString()} km</div>
                        <div className="text-xs text-gray-500">
                          Last service: {car.last_service_odometer.toLocaleString()} km
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {serviceDue ? (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Service Due ({kmSinceService.toLocaleString()} km)
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            OK ({(car.service_threshold_km - kmSinceService).toLocaleString()} km remaining)
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex gap-2">
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              openCarDetail(car)
                            }}
                            className="text-sky-600 hover:text-sky-900"
                          >
                            View
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              handleToggleMaintenance(car.id)
                            }}
                            className={`${
                              car.status === 'Under_maintenance' 
                                ? 'text-green-600 hover:text-green-900'
                                : 'text-orange-600 hover:text-orange-900'
                            }`}
                          >
                            {car.status === 'Under_maintenance' ? 'Remove from Maintenance' : 'Put in Maintenance'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          
          {filteredCars.length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No cars found</h3>
              <p className="mt-1 text-sm text-gray-500">Try adjusting your search or filter criteria.</p>
            </div>
          )}
        </div>
      )}

      {/* Empty State for Grid View */}
      {viewMode === 'grid' && filteredCars.length === 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-12 shadow-sm text-center">
          <div className="text-gray-400 text-6xl mb-4">🔧</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No cars found</h3>
          <p className="text-gray-600 mb-4">
            Try adjusting your search or filter criteria to find more cars.
          </p>
        </div>
      )}

      {/* Car Detail Modal */}
      {selectedCarId && (
        <CarDetailModal
          carId={selectedCarId}
          isOpen={isCarDetailModalOpen}
          onClose={closeCarDetail}
          onCarUpdate={loadCars}
        />
      )}
    </div>
  )
}

export default MaintenancePage
