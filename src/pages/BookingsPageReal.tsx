import * as React from 'react'
import { bookingAPI, type ApiBooking } from '../lib/api'

// Status badge component
const StatusBadge = ({ status, children }: { status: string; children: React.ReactNode }) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-green-100 text-green-800',
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

const BookingsPageReal = () => {
  const [bookings, setBookings] = React.useState<ApiBooking[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [searchTerm, setSearchTerm] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState('all')
  const [sortBy, setSortBy] = React.useState('created_at')
  const [selectedBooking, setSelectedBooking] = React.useState<ApiBooking | null>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = React.useState(false)
  const [processingAction, setProcessingAction] = React.useState<{ id: number; action: string } | null>(null)

  // Fetch bookings on component mount
  React.useEffect(() => {
    fetchBookings()
  }, [])

  const fetchBookings = async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('📅 Fetching bookings...')
      
      const response = await bookingAPI.getBookings(0, 50) // Fetch more bookings
      console.log('📅 Bookings response:', response)
      
      if (response.status === 'success') {
        setBookings(response.data)
        console.log(`✅ Loaded ${response.data.length} bookings`)
      } else {
        throw new Error(response.message || 'Failed to fetch bookings')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch bookings'
      console.error('❌ Error fetching bookings:', errorMessage)
      setError(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const fetchBookingDetails = async (bookingId: number) => {
    try {
      console.log(`📅 Fetching details for booking ${bookingId}`)
      const response = await bookingAPI.getBookingDetails(bookingId)
      
      if (response.status === 'success') {
        setSelectedBooking(response.data)
        setIsDetailModalOpen(true)
        console.log('✅ Booking details loaded')
      } else {
        throw new Error(response.message || 'Failed to fetch booking details')
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch booking details'
      console.error('❌ Error fetching booking details:', errorMessage)
      alert(errorMessage)
    }
  }

  const handleStatusUpdate = async (bookingId: number, action: 'cancel' | 'complete') => {
    try {
      setProcessingAction({ id: bookingId, action })
      console.log(`🔄 ${action}ing booking ${bookingId}`)
      
      let response
      if (action === 'cancel') {
        response = await bookingAPI.cancelBooking(bookingId)
      } else {
        response = await bookingAPI.completeBooking(bookingId)
      }
      
      if (response.status === 'success') {
        console.log(`✅ Booking ${action}ed successfully`)
        
        // Update the booking in the list
        setBookings(prev => prev.map(booking => 
          booking.id === bookingId 
            ? { ...booking, status: response.data.status as ApiBooking['status'] }
            : booking
        ))
        
        // Update selected booking if it's open
        if (selectedBooking?.id === bookingId) {
          setSelectedBooking(prev => prev ? { ...prev, status: response.data.status as ApiBooking['status'] } : null)
        }
        
        // Show success message
        alert(`Booking ${action}ed successfully`)
      } else {
        throw new Error(response.message || `Failed to ${action} booking`)
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to ${action} booking`
      console.error(`❌ Error ${action}ing booking:`, errorMessage)
      alert(errorMessage)
    } finally {
      setProcessingAction(null)
    }
  }

  const filteredBookings = React.useMemo(() => {
    return bookings
      .filter(booking => {
        const searchText = `${booking.user.first_name} ${booking.user.last_name} ${booking.car.make} ${booking.car.model} ${booking.id}`.toLowerCase()
        
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
            return parseFloat(b.total_cost) - parseFloat(a.total_cost)
          default:
            return 0
        }
      })
  }, [bookings, searchTerm, statusFilter, sortBy])

  const statusCounts = React.useMemo(() => {
    return bookings.reduce((acc, booking) => {
      acc[booking.status] = (acc[booking.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [bookings])

  const openBookingDetail = (booking: ApiBooking) => {
    fetchBookingDetails(booking.id)
  }

  const closeBookingDetail = () => {
    setSelectedBooking(null)
    setIsDetailModalOpen(false)
  }

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
          <p className="text-slate-600 mt-4">Loading bookings...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <div className="text-red-600 text-lg mb-4">⚠️ Error Loading Bookings</div>
          <p className="text-slate-600 mb-4">{error}</p>
          <button 
            onClick={fetchBookings}
            className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Bookings Management</h2>
          <p className="text-gray-600">Manage all customer bookings and reservations</p>
        </div>
        <button
          onClick={fetchBookings}
          className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700 transition-colors flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-900">{bookings.length}</div>
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

      {/* Bookings Table */}
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
                const isProcessing = processingAction?.id === booking.id
                
                return (
                  <tr 
                    key={booking.id} 
                    className="hover:bg-gray-50 cursor-pointer"
                    onClick={() => openBookingDetail(booking)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">#{booking.id}</div>
                      <div className="text-sm text-gray-500">{new Date(booking.created_at).toLocaleDateString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{booking.user.first_name} {booking.user.last_name}</div>
                        <div className="text-sm text-gray-500">{booking.user.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{booking.car.year} {booking.car.make} {booking.car.model}</div>
                        <div className="text-sm text-gray-500">{booking.car.license_plate}</div>
                      </div>
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
                      <div className="text-sm font-medium text-gray-900">${parseFloat(booking.total_cost).toLocaleString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                        <button
                          onClick={() => openBookingDetail(booking)}
                          className="text-sky-600 hover:text-sky-900"
                        >
                          View
                        </button>
                        {booking.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleStatusUpdate(booking.id, 'complete')}
                              disabled={isProcessing}
                              className="text-green-600 hover:text-green-900 disabled:opacity-50"
                            >
                              {isProcessing && processingAction?.action === 'complete' ? 'Confirming...' : 'Confirm'}
                            </button>
                            <button
                              onClick={() => handleStatusUpdate(booking.id, 'cancel')}
                              disabled={isProcessing}
                              className="text-red-600 hover:text-red-900 disabled:opacity-50"
                            >
                              {isProcessing && processingAction?.action === 'cancel' ? 'Cancelling...' : 'Cancel'}
                            </button>
                          </>
                        )}
                        {booking.status === 'in_progress' && (
                          <button
                            onClick={() => handleStatusUpdate(booking.id, 'complete')}
                            disabled={isProcessing}
                            className="text-green-600 hover:text-green-900 disabled:opacity-50"
                          >
                            {isProcessing && processingAction?.action === 'complete' ? 'Completing...' : 'Complete'}
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
              
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Customer Information</h4>
                    <div className="space-y-2">
                      <div>
                        <span className="text-sm text-gray-500">Name:</span>
                        <span className="ml-2 text-sm text-gray-900">
                          {selectedBooking.user.first_name} {selectedBooking.user.last_name}
                        </span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-500">Email:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedBooking.user.email}</span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-500">Phone:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedBooking.user.phone || 'N/A'}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-3">Vehicle Information</h4>
                    <div className="space-y-2">
                      <div>
                        <span className="text-sm text-gray-500">Vehicle:</span>
                        <span className="ml-2 text-sm text-gray-900">
                          {selectedBooking.car.year} {selectedBooking.car.make} {selectedBooking.car.model}
                        </span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-500">License Plate:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedBooking.car.license_plate}</span>
                      </div>
                      <div>
                        <span className="text-sm text-gray-500">Agency:</span>
                        <span className="ml-2 text-sm text-gray-900">{selectedBooking.car.agency.name}</span>
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
                        ${parseFloat(selectedBooking.total_cost).toLocaleString()}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="flex gap-3 pt-4 border-t border-gray-200">
                  {selectedBooking.status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleStatusUpdate(selectedBooking.id, 'complete')}
                        disabled={!!processingAction}
                        className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                      >
                        {processingAction?.action === 'complete' ? 'Confirming...' : 'Confirm Booking'}
                      </button>
                      <button
                        onClick={() => handleStatusUpdate(selectedBooking.id, 'cancel')}
                        disabled={!!processingAction}
                        className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
                      >
                        {processingAction?.action === 'cancel' ? 'Cancelling...' : 'Cancel Booking'}
                      </button>
                    </>
                  )}
                  {selectedBooking.status === 'in_progress' && (
                    <button
                      onClick={() => handleStatusUpdate(selectedBooking.id, 'complete')}
                      disabled={!!processingAction}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                    >
                      {processingAction?.action === 'complete' ? 'Completing...' : 'Complete Booking'}
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
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default BookingsPageReal
