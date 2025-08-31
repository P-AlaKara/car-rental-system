import * as React from 'react'
import { getBookings, cancelBooking, confirmBooking, completeBooking, getBookingDetails } from '../lib/api'
import { getCurrentUser } from '../lib/auth'
import type { ApiBooking, BookingListResponse, BookingDetailResponse } from '../lib/api'
import type { Profile } from '../lib/types'

// Status badge component
const StatusBadge = ({ status, children }: { status: string; children: React.ReactNode }) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    cancelled: 'bg-red-100 text-red-800 border border-red-200',
    confirmed: 'bg-blue-100 text-blue-800 border border-blue-200',
    in_progress: 'bg-blue-100 text-blue-800 border border-blue-200',
    completed: 'bg-green-100 text-green-800 border border-green-200'
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800 border border-gray-200'}`}>
      {children}
    </span>
  )
}

// Booking Card component for grid view
const BookingCard = ({ 
  booking, 
  onViewDetails, 
  getActionButtons 
}: { 
  booking: ApiBooking
  onViewDetails: (booking: ApiBooking) => void
  getActionButtons: (booking: ApiBooking) => React.ReactNode
}) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div>
          <div className="text-lg font-semibold text-gray-900">#{booking.id}</div>
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
          <div className="text-sm font-medium text-gray-900">
            {booking.user.first_name} {booking.user.last_name}
          </div>
          <div className="text-sm text-gray-500">{booking.user.email}</div>
          <div className="text-xs text-gray-400">{booking.user.role}</div>
        </div>

        {/* Vehicle Info */}
        <div>
          <div className="text-sm font-medium text-gray-900">
            {booking.car.year} {booking.car.make} {booking.car.model}
          </div>
          <div className="text-sm text-gray-500">
            {booking.car.license_plate} • {booking.car.agency.name}
          </div>
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
            ${parseFloat(booking.total_cost).toLocaleString()}
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
          {getActionButtons(booking)}
        </div>
      </div>
    </div>
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
  const [actionLoading, setActionLoading] = React.useState<number | null>(null)
  const [currentUser, setCurrentUser] = React.useState<Profile | null>(null)
  const [viewMode, setViewMode] = React.useState<'table' | 'grid'>('table')

  // Get current user
  React.useEffect(() => {
    const user = getCurrentUser()
    setCurrentUser(user)
  }, [])

  // Fetch bookings
  const fetchBookings = React.useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      console.log('📅 Fetching bookings...')
      
      const response: BookingListResponse = await getBookings(0, 50) // Get more records
      console.log('📅 Bookings response:', response)
      
      if (response.status === 'success') {
        setBookings(response.data)
        console.log(`✅ Loaded ${response.data.length} bookings`)
      } else {
        throw new Error(response.message || 'Failed to fetch bookings')
      }
    } catch (err) {
      console.error('❌ Error fetching bookings:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch bookings')
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    fetchBookings()
  }, [fetchBookings])

  // Filter and sort bookings
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
          case 'status':
            // Custom status order: pending, confirmed, completed, cancelled
            const statusOrder = { pending: 1, confirmed: 2, in_progress: 2, completed: 3, cancelled: 4 }
            return (statusOrder[a.status as keyof typeof statusOrder] || 5) - (statusOrder[b.status as keyof typeof statusOrder] || 5)
          default:
            return 0
        }
      })
  }, [bookings, searchTerm, statusFilter, sortBy])

  // Calculate status counts
  const statusCounts = React.useMemo(() => {
    return bookings.reduce((acc, booking) => {
      acc[booking.status] = (acc[booking.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  }, [bookings])

  // Handle booking actions
  const handleCancelBooking = async (bookingId: number) => {
    if (!confirm('Are you sure you want to cancel this booking?')) return
    
    try {
      setActionLoading(bookingId)
      console.log(`❌ Cancelling booking ${bookingId}`)
      
      const response = await cancelBooking(bookingId)
      console.log('✅ Cancel response:', response)
      
      if (response.status === 'success') {
        await fetchBookings() // Refresh bookings
        alert('Booking cancelled successfully')
      } else {
        throw new Error(response.message || 'Failed to cancel booking')
      }
    } catch (err) {
      console.error('❌ Error cancelling booking:', err)
      alert(err instanceof Error ? err.message : 'Failed to cancel booking')
    } finally {
      setActionLoading(null)
    }
  }

  const handleConfirmBooking = async (bookingId: number) => {
    if (!confirm('Are you sure you want to confirm this booking? This will mark the car as booked.')) return
    
    try {
      setActionLoading(bookingId)
      console.log(`✅ Confirming booking ${bookingId}`)
      
      const response = await confirmBooking(bookingId)
      console.log('✅ Confirm response:', response)
      
      if (response.status === 'success') {
        await fetchBookings() // Refresh bookings
        alert('Booking confirmed successfully. Car is now confirmed and ready.')
      } else {
        throw new Error(response.message || 'Failed to confirm booking')
      }
    } catch (err) {
      console.error('❌ Error confirming booking:', err)
      alert(err instanceof Error ? err.message : 'Failed to confirm booking')
    } finally {
      setActionLoading(null)
    }
  }

  const handleCompleteBooking = async (bookingId: number) => {
    if (!confirm('Are you sure you want to complete this booking? This will make the car available again.')) return
    
    try {
      setActionLoading(bookingId)
      console.log(`🏁 Completing booking ${bookingId}`)
      
      const response = await completeBooking(bookingId)
      console.log('✅ Complete response:', response)
      
      if (response.status === 'success') {
        await fetchBookings() // Refresh bookings
        alert('Booking completed successfully. Car is now available.')
      } else {
        throw new Error(response.message || 'Failed to complete booking')
      }
    } catch (err) {
      console.error('❌ Error completing booking:', err)
      alert(err instanceof Error ? err.message : 'Failed to complete booking')
    } finally {
      setActionLoading(null)
    }
  }

  const openBookingDetail = async (booking: ApiBooking) => {
    try {
      console.log(`📄 Fetching details for booking ${booking.id}`)
      const response: BookingDetailResponse = await getBookingDetails(booking.id)
      
      if (response.status === 'success') {
        setSelectedBooking(response.data)
        setIsDetailModalOpen(true)
      } else {
        throw new Error(response.message || 'Failed to fetch booking details')
      }
    } catch (err) {
      console.error('❌ Error fetching booking details:', err)
      alert(err instanceof Error ? err.message : 'Failed to fetch booking details')
    }
  }

  const closeBookingDetail = () => {
    setSelectedBooking(null)
    setIsDetailModalOpen(false)
  }

  // Check if user can perform actions (only admin, not superAdmin)
  const canPerformActions = currentUser?.role === 'admin'

  // Get action buttons for a booking based on status and user role
  const getActionButtons = (booking: ApiBooking) => {
    const isActionInProgress = actionLoading === booking.id

    // SuperAdmin can only view bookings
    if (!canPerformActions) {
      return (
        <button
          onClick={() => openBookingDetail(booking)}
          className="text-sky-600 hover:text-sky-900 text-sm font-medium"
        >
          View
        </button>
      )
    }

    // Admin can perform actions based on booking status
    return (
      <div className="flex gap-2">
        <button
          onClick={() => openBookingDetail(booking)}
          className="text-sky-600 hover:text-sky-900 text-sm font-medium"
        >
          View
        </button>
        
        {booking.status === 'pending' && (
          <>
            <button
              onClick={() => handleConfirmBooking(booking.id)}
              disabled={isActionInProgress}
              className="text-green-600 hover:text-green-900 text-sm font-medium disabled:opacity-50"
            >
              {isActionInProgress ? 'Confirming...' : 'Confirm'}
            </button>
            <button
              onClick={() => handleCancelBooking(booking.id)}
              disabled={isActionInProgress}
              className="text-red-600 hover:text-red-900 text-sm font-medium disabled:opacity-50"
            >
              {isActionInProgress ? 'Cancelling...' : 'Cancel'}
            </button>
          </>
        )}
        
        {booking.status === 'confirmed' && (
          <button
            onClick={() => handleCompleteBooking(booking.id)}
            disabled={isActionInProgress}
            className="text-blue-600 hover:text-blue-900 text-sm font-medium disabled:opacity-50"
          >
            {isActionInProgress ? 'Completing...' : 'Complete'}
          </button>
        )}
      </div>
    )
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Bookings Management</h2>
            <p className="text-gray-600">Loading bookings...</p>
          </div>
        </div>
        <div className="flex justify-center items-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Bookings Management</h2>
            <p className="text-red-600">Error: {error}</p>
          </div>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="text-red-800">
              <h3 className="font-medium">Unable to load bookings</h3>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
          <button
            onClick={fetchBookings}
            className="mt-3 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 text-sm"
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
          <p className="text-gray-600">
            Manage all customer bookings and reservations
            {!canPerformActions && (
              <span className="ml-2 text-sm text-blue-600 font-medium">
                (View Only - SuperAdmin)
              </span>
            )}
          </p>
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
          <div className="text-2xl font-bold text-blue-600">{statusCounts.confirmed || 0}</div>
          <div className="text-sm text-gray-600">Confirmed</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">{statusCounts.completed || 0}</div>
          <div className="text-sm text-gray-600">Completed</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-red-600">{statusCounts.cancelled || 0}</div>
          <div className="text-sm text-gray-600">Cancelled</div>
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
              <option value="status">Status</option>
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
                {filteredBookings.map((booking) => (
                  <tr key={booking.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">#{booking.id}</div>
                      <div className="text-sm text-gray-500">
                        {new Date(booking.created_at).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {booking.user.first_name} {booking.user.last_name}
                        </div>
                        <div className="text-sm text-gray-500">{booking.user.email}</div>
                        <div className="text-xs text-gray-400">{booking.user.role}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {booking.car.year} {booking.car.make} {booking.car.model}
                        </div>
                        <div className="text-sm text-gray-500">
                          {booking.car.license_plate} • {booking.car.agency.name}
                        </div>
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
                      <div className="text-sm font-medium text-gray-900">
                        ${parseFloat(booking.total_cost).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium" onClick={(e) => e.stopPropagation()}>
                      {getActionButtons(booking)}
                    </td>
                  </tr>
                ))}
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
                getActionButtons={getActionButtons}
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
                  {canPerformActions && (
                    <>
                      {selectedBooking.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleConfirmBooking(selectedBooking.id)}
                            disabled={actionLoading === selectedBooking.id}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50"
                          >
                            {actionLoading === selectedBooking.id ? 'Confirming...' : 'Confirm Booking'}
                          </button>
                          <button
                            onClick={() => handleCancelBooking(selectedBooking.id)}
                            disabled={actionLoading === selectedBooking.id}
                            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 disabled:opacity-50"
                          >
                            {actionLoading === selectedBooking.id ? 'Cancelling...' : 'Cancel Booking'}
                          </button>
                        </>
                      )}
                      
                      {selectedBooking.status === 'confirmed' && (
                        <button
                          onClick={() => handleCompleteBooking(selectedBooking.id)}
                          disabled={actionLoading === selectedBooking.id}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                        >
                          {actionLoading === selectedBooking.id ? 'Completing...' : 'Complete Booking'}
                        </button>
                      )}
                    </>
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
