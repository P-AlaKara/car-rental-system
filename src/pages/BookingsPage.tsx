import * as React from 'react'
import { DEMO_BOOKINGS, DEMO_CARS, DEMO_USERS } from '../lib/demo-data'

// Status badge component
const StatusBadge = ({ status, children }: { status: string; children: React.ReactNode }) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-gray-100 text-gray-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
      {children}
    </span>
  )
}

// Booking Card component for grid view
const BookingCard = ({ 
  booking, 
  onViewDetails, 
  handleStatusUpdate 
}: { 
  booking: any
  onViewDetails: (booking: any) => void
  handleStatusUpdate: (bookingId: number, newStatus: string) => void
}) => {
  const user = DEMO_USERS.find(u => u.id === booking.user_id)
  const car = DEMO_CARS.find(c => c.id === booking.car_id)
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="text-lg font-semibold text-gray-900">#{booking.id.toString().slice(0, 8)}</div>
          <div className="text-sm text-gray-500">
            {new Date(booking.created_at).toLocaleDateString()}
          </div>
        </div>
        <StatusBadge status={booking.status}>
          {booking.status.replace('_', ' ')}
        </StatusBadge>
      </div>

      <div className="space-y-3 mb-4">
        {/* Customer Info */}
        <div>
          {user ? (
            <>
              <div className="text-sm font-medium text-gray-900">
                {user.first_name} {user.last_name}
              </div>
              <div className="text-sm text-gray-500">{user.email}</div>
            </>
          ) : (
            <div className="text-sm text-gray-500">User not found</div>
          )}
        </div>

        {/* Vehicle Info */}
        <div>
          {car ? (
            <>
              <div className="text-sm font-medium text-gray-900">
                {car.year} {car.make} {car.model}
              </div>
              <div className="text-sm text-gray-500">
                {typeof car.category === 'object' ? car.category.name : car.category} • {car.license_plate}
              </div>
            </>
          ) : (
            <div className="text-sm text-gray-500">Car not found</div>
          )}
        </div>

        {/* Duration */}
        <div>
          <div className="text-sm text-gray-900">
            {new Date(booking.start_date).toLocaleDateString()} - {new Date(booking.end_date).toLocaleDateString()}
          </div>
          <div className="text-sm text-gray-500">
            {Math.ceil((new Date(booking.end_date).getTime() - new Date(booking.start_date).getTime()) / (1000 * 60 * 60 * 24))} days
          </div>
        </div>

        {/* Total Cost */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <span className="text-sm text-gray-500">Total:</span>
          <span className="text-lg font-bold text-gray-900">
            ${booking.total_cost.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-3 border-t border-gray-200">
        <button
          onClick={() => onViewDetails(booking)}
          className="text-sky-600 hover:text-sky-900 text-sm font-medium"
        >
          View Details
        </button>
        <div className="flex items-center gap-2">
          {booking.status === 'pending' && (
            <>
              <button
                onClick={() => handleStatusUpdate(booking.id, 'confirmed')}
                className="text-green-600 hover:text-green-900 text-sm font-medium"
              >
                Confirm
              </button>
              <button
                onClick={() => handleStatusUpdate(booking.id, 'cancelled')}
                className="text-red-600 hover:text-red-900 text-sm font-medium"
              >
                Cancel
              </button>
            </>
          )}
          {booking.status === 'confirmed' && (
            <button
              onClick={() => handleStatusUpdate(booking.id, 'completed')}
              className="text-blue-600 hover:text-blue-900 text-sm font-medium"
            >
              Complete
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

const BookingsPage = () => {
  const [searchTerm, setSearchTerm] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState('all')
  const [sortBy, setSortBy] = React.useState('created_at')
  const [selectedBooking, setSelectedBooking] = React.useState<any>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = React.useState(false)
  const [viewMode, setViewMode] = React.useState<'table' | 'grid'>('table')

  const filteredBookings = React.useMemo(() => {
    return DEMO_BOOKINGS
      .filter(booking => {
        const user = DEMO_USERS.find(u => u.id === booking.user_id)
        const car = DEMO_CARS.find(c => c.id === booking.car_id)
        const searchText = `${user?.first_name} ${user?.last_name} ${car?.make} ${car?.model} ${booking.id}`.toLowerCase()
        
        const matchesSearch = searchTerm === '' || searchText.includes(searchTerm.toLowerCase())
        const matchesStatus = statusFilter === 'all' || booking.status === statusFilter
        
        return matchesSearch && matchesStatus
      })
      .sort((a, b) => {
        switch (sortBy) {
          case 'created_at':
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          case 'start_date':
            return new Date(a.start_date).getTime() - new Date(b.start_date).getTime()
          case 'total_cost':
            return b.total_cost - a.total_cost
          default:
            return 0
        }
      })
  }, [searchTerm, statusFilter, sortBy])

  const statusCounts = React.useMemo(() => {
    return DEMO_BOOKINGS.reduce((acc, booking) => {
      acc[booking.status] = (acc[booking.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [])

  const handleStatusUpdate = (bookingId: number, newStatus: string) => {
    console.log(`Updating booking ${bookingId} status to ${newStatus}`)
    // In a real app, this would make an API call
  }

  const openBookingDetail = (booking: any) => {
    setSelectedBooking(booking)
    setIsDetailModalOpen(true)
  }

  const closeBookingDetail = () => {
    setSelectedBooking(null)
    setIsDetailModalOpen(false)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Bookings Management</h2>
          <p className="text-gray-600">Manage all customer bookings and reservations</p>
        </div>
        <div className="flex items-center gap-3">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'table'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <svg className="w-4 h-4 mr-1.5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 6h18m-9 8h9m-9 4h9m-9-8h9m-9 4h9" />
              </svg>
              Table
            </button>
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                viewMode === 'grid'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <svg className="w-4 h-4 mr-1.5 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
              </svg>
              Grid
            </button>
          </div>
          <button className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700 transition-colors flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Booking
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-900">{DEMO_BOOKINGS.length}</div>
          <div className="text-sm text-gray-600">Total Bookings</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-yellow-600">{statusCounts.pending || 0}</div>
          <div className="text-sm text-gray-600">Pending</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">{statusCounts.confirmed || 0}</div>
          <div className="text-sm text-gray-600">Confirmed</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{statusCounts.in_progress || 0}</div>
          <div className="text-sm text-gray-600">In Progress</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-600">{statusCounts.completed || 0}</div>
          <div className="text-sm text-gray-600">Completed</div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search bookings, customers, or cars..."
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
              <option value="pending">Pending</option>
              <option value="confirmed">Confirmed</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
            >
              <option value="created_at">Latest</option>
              <option value="start_date">Start Date</option>
              <option value="total_cost">Price</option>
            </select>
          </div>
        </div>
      </div>

      {/* Bookings Table or Grid */}
      {viewMode === 'table' ? (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Booking ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Vehicle</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredBookings.map((booking) => {
                  const user = DEMO_USERS.find(u => u.id === booking.user_id)
                  const car = DEMO_CARS.find(c => c.id === booking.car_id)
                  
                  return (
                    <tr key={booking.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">#{booking.id.toString().slice(0, 8)}</div>
                        <div className="text-sm text-gray-500">{new Date(booking.created_at).toLocaleDateString()}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {user ? (
                          <div>
                            <div className="text-sm font-medium text-gray-900">{user.first_name} {user.last_name}</div>
                            <div className="text-sm text-gray-500">{user.email}</div>
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500">User not found</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {car ? (
                          <div>
                            <div className="text-sm font-medium text-gray-900">{car.year} {car.make} {car.model}</div>
                            <div className="text-sm text-gray-500">{typeof car.category === 'object' ? car.category.name : car.category} • {car.license_plate}</div>
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500">Car not found</div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {new Date(booking.start_date).toLocaleDateString()} - {new Date(booking.end_date).toLocaleDateString()}
                        </div>
                        <div className="text-sm text-gray-500">
                          {Math.ceil((new Date(booking.end_date).getTime() - new Date(booking.start_date).getTime()) / (1000 * 60 * 60 * 24))} days
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={booking.status}>
                          {booking.status.replace('_', ' ')}
                        </StatusBadge>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">${booking.total_cost.toLocaleString()}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <div className="flex gap-2">
                          <button
                            onClick={() => openBookingDetail(booking)}
                            className="text-sky-600 hover:text-sky-900"
                          >
                            View
                          </button>
                          {booking.status === 'pending' && (
                            <>
                              <button
                                onClick={() => handleStatusUpdate(booking.id, 'confirmed')}
                                className="text-green-600 hover:text-green-900"
                              >
                                Confirm
                              </button>
                              <button
                                onClick={() => handleStatusUpdate(booking.id, 'cancelled')}
                                className="text-red-600 hover:text-red-900"
                              >
                                Cancel
                              </button>
                            </>
                          )}
                          {booking.status === 'confirmed' && (
                            <button
                              onClick={() => handleStatusUpdate(booking.id, 'completed')}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              Complete
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          
          {filteredBookings.length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No bookings found</h3>
              <p className="mt-1 text-sm text-gray-500">Try adjusting your search or filter criteria.</p>
            </div>
          )}
        </div>
      ) : (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredBookings.map((booking) => (
              <BookingCard
                key={booking.id}
                booking={booking}
                onViewDetails={openBookingDetail}
                handleStatusUpdate={handleStatusUpdate}
              />
            ))}
          </div>
          
          {filteredBookings.length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No bookings found</h3>
              <p className="mt-1 text-sm text-gray-500">Try adjusting your search or filter criteria.</p>
            </div>
          )}
        </div>
      )}

      {/* Booking Detail Modal */}
      {isDetailModalOpen && selectedBooking && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Booking Details</h3>
                <button
                  onClick={closeBookingDetail}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {(() => {
                const user = DEMO_USERS.find(u => u.id === selectedBooking.user_id)
                const car = DEMO_CARS.find(c => c.id === selectedBooking.car_id)
                
                return (
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-3">Customer Information</h4>
                        <div className="space-y-2">
                          <div>
                            <span className="text-sm text-gray-500">Name:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {user ? `${user.first_name} ${user.last_name}` : 'User not found'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Email:</span>
                            <span className="ml-2 text-sm text-gray-900">{user?.email || 'N/A'}</span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Phone:</span>
                            <span className="ml-2 text-sm text-gray-900">{user?.phone || 'N/A'}</span>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-3">Vehicle Information</h4>
                        <div className="space-y-2">
                          <div>
                            <span className="text-sm text-gray-500">Vehicle:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {car ? `${car.year} ${car.make} ${car.model}` : 'Car not found'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Category:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {car ? (typeof car.category === 'object' ? car.category.name : car.category) : 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">License Plate:</span>
                            <span className="ml-2 text-sm text-gray-900">{car?.license_plate || 'N/A'}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Booking Details</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-sm text-gray-500">Booking ID:</span>
                          <span className="ml-2 text-sm text-gray-900">#{selectedBooking.id}</span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Status:</span>
                          <span className="ml-2">
                            <StatusBadge status={selectedBooking.status}>
                              {selectedBooking.status.replace('_', ' ')}
                            </StatusBadge>
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Start Date:</span>
                          <span className="ml-2 text-sm text-gray-900">
                            {new Date(selectedBooking.start_date).toLocaleDateString()}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">End Date:</span>
                          <span className="ml-2 text-sm text-gray-900">
                            {new Date(selectedBooking.end_date).toLocaleDateString()}
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Duration:</span>
                          <span className="ml-2 text-sm text-gray-900">
                            {Math.ceil((new Date(selectedBooking.end_date).getTime() - new Date(selectedBooking.start_date).getTime()) / (1000 * 60 * 60 * 24))} days
                          </span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Total Cost:</span>
                          <span className="ml-2 text-sm font-medium text-gray-900">
                            ${selectedBooking.total_cost.toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {selectedBooking.notes && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Notes</h4>
                        <p className="text-sm text-gray-600">{selectedBooking.notes}</p>
                      </div>
                    )}
                    
                    <div className="flex gap-3 pt-4 border-t border-gray-200">
                      {selectedBooking.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleStatusUpdate(selectedBooking.id, 'confirmed')}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                          >
                            Confirm Booking
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(selectedBooking.id, 'cancelled')}
                            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
                          >
                            Cancel Booking
                          </button>
                        </>
                      )}
                      {selectedBooking.status === 'confirmed' && (
                        <button
                          onClick={() => handleStatusUpdate(selectedBooking.id, 'completed')}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                        >
                          Complete Booking
                        </button>
                      )}
                      <button
                        onClick={closeBookingDetail}
                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                )
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BookingsPage
