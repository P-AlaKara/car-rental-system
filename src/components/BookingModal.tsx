import * as React from 'react'
import type { Booking } from '../lib/types'
import { DEMO_CARS, DEMO_USERS } from '../lib/demo-data'
import { getBooking, updateBooking } from '../lib/auth'

interface BookingModalProps {
  booking: Booking
  onClose: () => void
  onStatusUpdate: (bookingId: number, newStatus: string) => void
  onPaymentUpdate: (bookingId: number, newPaymentStatus: string) => void
}

const BookingModal: React.FC<BookingModalProps> = ({ 
  booking, 
  onClose, 
  onStatusUpdate, 
  onPaymentUpdate 
}) => {
  const car = DEMO_CARS.find(c => c.id === booking.car_id)
  const user = DEMO_USERS.find(u => u.id === booking.user_id)
  const startDate = new Date(booking.start_date)
  const endDate = new Date(booking.end_date)
  const duration = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))

  const [licenseUrl, setLicenseUrl] = React.useState<string>(booking.driver_license_url || '')
  const [pickupPhotos, setPickupPhotos] = React.useState<string[]>(booking.pickup_photos || [])
  const [returnPhotos, setReturnPhotos] = React.useState<string[]>(booking.return_photos || [])
  const [bondAmount, setBondAmount] = React.useState<number>(booking.bond_amount || 0)
  const [week1Amount, setWeek1Amount] = React.useState<number>(booking.week1_amount || 0)
  const [pickupOdo, setPickupOdo] = React.useState<number>(booking.pickup_odometer || 0)
  const [returnOdo, setReturnOdo] = React.useState<number>(booking.return_odometer || 0)

  function persistPartial(update: Partial<Booking>) {
    updateBooking(booking.id, (b) => ({ ...b, ...update, updated_at: new Date().toISOString() }))
  }

  const getStatusColor = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800',
      payment_pending: 'bg-orange-100 text-orange-800',
      invoice_sent: 'bg-blue-100 text-blue-800',
      paid: 'bg-green-100 text-green-800',
      overdue: 'bg-red-100 text-red-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-xl">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Booking #{booking.id}</h2>
              <p className="text-sm text-gray-600 mt-1">
                Created on {new Date(booking.created_at).toLocaleDateString()} at {new Date(booking.created_at).toLocaleTimeString()}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              aria-label="Close modal"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Status and Payment Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Booking Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Current Status:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(booking.status)}`}>
                    {booking.status.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <label htmlFor="status-select" className="block text-sm font-medium text-gray-700 mb-2">
                    Update Status
                  </label>
                  <select
                    id="status-select"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                    value={booking.status}
                    onChange={(e) => onStatusUpdate(booking.id, e.target.value)}
                  >
                    <option value="pending">Pending</option>
                    <option value="confirmed">Confirmed</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Payment Status</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Payment Status:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(booking.payment_status)}`}>
                    {booking.payment_status.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <label htmlFor="payment-select" className="block text-sm font-medium text-gray-700 mb-2">
                    Update Payment Status
                  </label>
                  <select
                    id="payment-select"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                    value={booking.payment_status}
                    onChange={(e) => onPaymentUpdate(booking.id, e.target.value)}
                  >
                    <option value="pending">Pending</option>
                    <option value="invoice_sent">Invoice Sent</option>
                    <option value="paid">Paid</option>
                    <option value="overdue">Overdue</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Collection / Return (Handover) */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Collection & Return</h3>
            <div className="grid md:grid-cols-2 gap-6 text-sm">
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Collection (Pickup)</h4>
                <div>
                  <label className="block text-gray-700 mb-1">Driver License URL</label>
                  <input className="w-full border rounded px-3 py-2" placeholder="https://..." value={licenseUrl} onChange={(e)=>{ setLicenseUrl(e.target.value); persistPartial({ driver_license_url: e.target.value }) }} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-gray-700 mb-1">Pickup Odometer (km)</label>
                    <input type="number" title="Pickup odometer (kilometres)" placeholder="e.g. 28750" className="w-full border rounded px-3 py-2" value={pickupOdo} onChange={(e)=>{ const v=Number(e.target.value)||0; setPickupOdo(v); persistPartial({ pickup_odometer: v }) }} />
                  </div>
                  
                 </div>
                <div>
                  <label className="block text-gray-700 mb-1">Pickup Photos (comma-separated URLs)</label>
                  <input className="w-full border rounded px-3 py-2" placeholder="https://... , https://..." value={pickupPhotos.join(', ')} onChange={(e)=>{ const arr=e.target.value.split(',').map(s=>s.trim()).filter(Boolean); setPickupPhotos(arr); persistPartial({ pickup_photos: arr }) }} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-gray-700 mb-1">Bond Amount</label>
                    <input type="number" title="Bond amount" placeholder="e.g. 500" className="w-full border rounded px-3 py-2" value={bondAmount} onChange={(e)=>{ const v=Number(e.target.value)||0; setBondAmount(v); persistPartial({ bond_amount: v }) }} />
                  </div>
                  <div>
                    <label className="block text-gray-700 mb-1">Week 1 Amount</label>
                    <input type="number" title="Week 1 amount" placeholder="e.g. 300" className="w-full border rounded px-3 py-2" value={week1Amount} onChange={(e)=>{ const v=Number(e.target.value)||0; setWeek1Amount(v); persistPartial({ week1_amount: v }) }} />
                  </div>
                </div>
                <button className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700" onClick={()=>persistPartial({ collection_completed_at: new Date().toISOString() })}>Mark Collection Complete</button>
              </div>
              <div className="space-y-3">
                <h4 className="font-medium text-gray-900">Return (Drop-off)</h4>
                <div>
                  <label className="block text-gray-700 mb-1">Return Photos (comma-separated URLs)</label>
                  <input className="w-full border rounded px-3 py-2" placeholder="https://... , https://..." value={returnPhotos.join(', ')} onChange={(e)=>{ const arr=e.target.value.split(',').map(s=>s.trim()).filter(Boolean); setReturnPhotos(arr); persistPartial({ return_photos: arr }) }} />
                </div>
                <div>
                  <label className="block text-gray-700 mb-1">Return Odometer (km)</label>
                  <input type="number" title="Return odometer (kilometres)" placeholder="e.g. 29810" className="w-full border rounded px-3 py-2" value={returnOdo} onChange={(e)=>{ const v=Number(e.target.value)||0; setReturnOdo(v); persistPartial({ return_odometer: v }) }} />
                </div>
                <button className="px-4 py-2 bg-slate-600 text-white rounded hover:bg-slate-700" onClick={()=>persistPartial({ return_completed_at: new Date().toISOString() })}>Mark Return Complete</button>
              </div>
            </div>
          </div>

          {/* Customer Information */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Customer Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-12 h-12 bg-sky-100 rounded-full flex items-center justify-center">
                    <span className="text-sky-700 font-semibold text-lg">
                      {user?.first_name?.[0]}{user?.last_name?.[0]}
                    </span>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">
                      {user ? `${user.first_name} ${user.last_name}` : 'Unknown User'}
                    </h4>
                    <p className="text-sm text-gray-600">{user?.email || 'No email'}</p>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Phone:</span>
                    <span className="font-medium">{booking.phone_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Loyalty Points:</span>
                    <span className="font-medium">{user?.loyalty_points || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Member Since:</span>
                    <span className="font-medium">
                      {user ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              
            </div>
          </div>

          {/* Driver Details (Mock) */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Driver Details</h3>
            <div className="divide-y">
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">Full Name</span>
                <span className="font-medium text-gray-900">{user ? `${user.first_name?.toUpperCase()} ${user.last_name?.toUpperCase()}` : 'N/A'}</span>
              </div>
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">Address</span>
                <span className="font-medium text-gray-900 text-right">U 5 6 SYLVANWOOD CRES<br/>NARRE WARREN VIC 3805</span>
              </div>
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">DOB</span>
                <span className="font-medium text-gray-900">06 MAY 1997</span>
              </div>
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">Licence NO.</span>
                <span className="font-medium text-gray-900">054309446</span>
              </div>
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">Licence State/Country of issue</span>
                <span className="font-medium text-gray-900">VIC</span>
              </div>
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">Email address /CONTACT NO.</span>
                <span className="font-medium text-gray-900">{user?.email || '—'}{user?.phone ? ` / ${user.phone}` : ''}</span>
              </div>
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">STARTDATE</span>
                <span className="font-medium text-gray-900">{new Date(booking.start_date).toLocaleDateString('en-AU')}</span>
              </div>
              <div className="flex items-start justify-between py-3">
                <span className="text-gray-600">END DATES</span>
                <span className="font-medium text-gray-900">{booking.status === 'in_progress' || booking.status === 'confirmed' ? new Date(booking.end_date).toLocaleDateString('en-AU') : 'ONGOING'}</span>
              </div>
            </div>
          </div>

          {/* Vehicle Information */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Vehicle Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="flex items-start gap-4">
                <img 
                  src={car?.image_url || '/placeholder.svg'} 
                  alt={car?.make || 'Car'}
                  className="w-24 h-16 rounded-lg object-cover bg-gray-100"
                />
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 text-lg">
                    {car ? `${car.year} ${car.make} ${car.model}` : `Car ${booking.car_id}`}
                  </h4>
                  <div className="text-sm text-gray-600 space-y-1 mt-2">
                    <div>License: {car?.license_plate || 'N/A'}</div>
                    <div>Category: {typeof car?.category === 'object' ? car.category.name : car?.category}</div>
                    <div>Transmission: {car?.transmission}</div>
                    <div>Fuel Type: {car?.fuel_type}</div>
                    <div>Seats: {car?.seats}</div>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Vehicle Status</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Current Status:</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(car?.status || 'available')}`}>
                      {car?.status?.replace('_', ' ') || 'Available'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Odometer:</span>
                    <span className="font-medium">{car?.current_odometer?.toLocaleString()} km</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Daily Rate:</span>
                    <span className="font-medium">${car?.rental_rate_per_day}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Rental Details */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Rental Details</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Rental Period</h4>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <div className="text-sm text-gray-600">Pickup</div>
                      <div className="font-medium">{startDate.toLocaleDateString()}</div>
                      <div className="text-sm text-gray-500">{startDate.toLocaleTimeString()}</div>
                    </div>
                    <div className="text-gray-400">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Return</div>
                      <div className="font-medium">{endDate.toLocaleDateString()}</div>
                      <div className="text-sm text-gray-500">{endDate.toLocaleTimeString()}</div>
                    </div>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Duration:</span>
                    <span className="font-medium">{duration} day{duration !== 1 ? 's' : ''}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Pickup Location:</span>
                    <span className="font-medium">{booking.pickup_location}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Return Location:</span>
                    <span className="font-medium">{booking.return_location}</span>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Pricing & Extras</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Daily Rate:</span>
                    <span className="font-medium">${car?.rental_rate_per_day}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="font-medium">{duration} days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Subtotal:</span>
                    <span className="font-medium">${(Number(car?.rental_rate_per_day) || 0) * duration}</span>
                  </div>
                  {booking.promo_code && (
                    <div className="flex justify-between text-green-600">
                      <span>Promo Code ({booking.promo_code}):</span>
                      <span>-${((Number(car?.rental_rate_per_day) || 0) * duration * 0.1).toFixed(2)}</span>
                    </div>
                  )}
                  <div className="border-t pt-2">
                    <div className="flex justify-between font-semibold">
                      <span>Total:</span>
                      <span>${booking.total_cost.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Special Requests & Notes */}
          {(booking.special_requests || booking.admin_notes) && (
            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Additional Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {booking.special_requests && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Special Requests</h4>
                    <p className="text-sm text-gray-700 bg-yellow-50 p-3 rounded-lg">
                      {booking.special_requests}
                    </p>
                  </div>
                )}
                {booking.admin_notes && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Admin Notes</h4>
                    <p className="text-sm text-gray-700 bg-blue-50 p-3 rounded-lg">
                      {booking.admin_notes}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Close
            </button>
            <button className="px-6 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors" onClick={()=>{
              const existing = getBooking(booking.id) || booking
              persistPartial({ invoice_id: existing.invoice_id || `INV-${booking.id}`, invoice_status: 'sent', invoice_created_at: new Date().toISOString(), payment_status: 'invoice_sent' })
              onPaymentUpdate(booking.id, 'invoice_sent')
            }}>
              Create/Send Invoice
            </button>
            <button className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors" onClick={()=>{
              persistPartial({ invoice_status: 'paid', payment_status: 'paid' })
              onPaymentUpdate(booking.id, 'paid')
            }}>
              Mark Paid
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BookingModal
