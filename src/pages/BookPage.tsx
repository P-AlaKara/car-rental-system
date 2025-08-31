import * as React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import Footer from '../components/Footer'
import { bookingAPI, fleetAPI, buildImageUrl, type Car as APICar } from '../lib/api'
import { isAuthenticated, validateAndRefreshToken } from '../lib/auth'
import type { Car } from '../lib/types'

// Convert API Car to local Car type
function convertApiCarToLocalCar(apiCar: APICar): Car {
  return {
    ...apiCar,
    agency: apiCar.agency,
    rental_rate_per_day: Number(apiCar.rental_rate_per_day),
    category: apiCar.category
  }
}

function BookPage() {
  const { carId } = useParams<{ carId: string }>()
  const navigate = useNavigate()
  const [car, setCar] = React.useState<Car | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)
  
  const [formData, setFormData] = React.useState({
    startDate: '',
    endDate: '',
    pickupLocation: '',
    returnLocation: '',
    phoneNumber: '',
    driverEmail: '',
    driverFullname: '',
    licenseNumber: '',
    residentialArea: '',
    specialRequests: '',
    promoCode: ''
  })
  
  const [totalCost, setTotalCost] = React.useState(0)
  const [paymentFrequency, setPaymentFrequency] = React.useState<'3days' | 'weekly'>('weekly')
  const [isProcessing, setIsProcessing] = React.useState(false)

  // Fetch car data when component mounts
  React.useEffect(() => {
    const fetchCar = async () => {
      if (!carId) {
        setError('Car ID is required')
        return
      }

      try {
        setLoading(true)
        setError(null)
        const response = await fleetAPI.getCar(Number(carId))
        setCar(convertApiCarToLocalCar(response.data))
      } catch (e: any) {
        console.error('Error fetching car:', e)
        setError(e?.message || 'Failed to load car details')
      } finally {
        setLoading(false)
      }
    }

    fetchCar()
  }, [carId])

  // Calculate total cost when dates change
  React.useEffect(() => {
    if (formData.startDate && formData.endDate && car) {
      const start = new Date(formData.startDate)
      const end = new Date(formData.endDate)
      const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24))
      setTotalCost(days > 0 ? days * Number(car.rental_rate_per_day || 0) : 0)
    }
  }, [formData.startDate, formData.endDate, car])

  // Debug authentication status
  React.useEffect(() => {
    console.log('🔐 Current authentication status:', isAuthenticated() ? 'Authenticated' : 'Not authenticated')
    console.log('🔑 Token exists:', !!localStorage.getItem('am_token'))
    console.log('👤 User exists:', !!localStorage.getItem('am_user'))
  }, [])

  // Now we can have conditional returns after all hooks are called
  if (loading) {
    return (
      <main className="min-h-screen flex flex-col bg-white">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-semibold text-slate-900 mb-4">Loading car details...</h1>
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600 mx-auto"></div>
          </div>
        </div>
        <Footer />
      </main>
    )
  }

  if (error) {
    return (
      <main className="min-h-screen flex flex-col bg-white">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-semibold text-slate-900 mb-4">Error loading car</h1>
            <p className="text-red-600 mb-4">{error}</p>
            <button 
              onClick={() => navigate('/cars')}
              className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition"
            >
              Back to Cars
            </button>
          </div>
        </div>
        <Footer />
      </main>
    )
  }

  if (!car) {
    return (
      <main className="min-h-screen flex flex-col bg-white">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-semibold text-slate-900 mb-4">Car not found</h1>
            <p className="text-slate-600 mb-4">The requested car could not be found.</p>
            <button 
              onClick={() => navigate('/cars')}
              className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition"
            >
              Back to Cars
            </button>
          </div>
        </div>
        <Footer />
      </main>
    )
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Check if user is authenticated
    if (!isAuthenticated()) {
      alert('Please log in to book a vehicle. You will be redirected to the login page.')
      navigate('/login')
      return
    }
    
    // Validate and refresh token if needed
    const isValid = await validateAndRefreshToken()
    if (!isValid) {
      alert('Your session has expired. Please log in again.')
      navigate('/login')
      return
    }
    
    // Validate form
    if (!formData.startDate || !formData.endDate || !formData.pickupLocation || !formData.phoneNumber || 
        !formData.driverEmail || !formData.driverFullname || !formData.licenseNumber || !formData.residentialArea) {
      alert('Please fill in all required fields')
      return
    }
    
    // Check dates
    const start = new Date(formData.startDate)
    const end = new Date(formData.endDate)
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    if (start < today) {
      alert('Start date cannot be in the past')
      return
    }
    
    if (end <= start) {
      alert('End date must be after start date')
      return
    }
    
    // Submit booking directly
    try {
      setIsProcessing(true)
      
      // Compose API payload exactly as specified
      const payload = {
        car_id: Number(car.id),
        start_date: `${formData.startDate} 10:00:00`,
        end_date: `${formData.endDate} 10:00:00`,
        pickup_location: formData.pickupLocation,
        return_location: formData.returnLocation || formData.pickupLocation,
        driver_email: formData.driverEmail,
        driver_fullname: formData.driverFullname,
        license_number: formData.licenseNumber,
        residential_area: formData.residentialArea,
        special_requests: formData.specialRequests || undefined,
        total_cost: Number(totalCost),
        payment_frequency: paymentFrequency,
      }
      
      console.log('🚀 Submitting booking with payload:', payload)
      console.log('📞 API Endpoint: POST /book')
      console.log('🔐 Authentication status:', isAuthenticated() ? 'Authenticated' : 'Not authenticated')
      
      const response = await bookingAPI.createBooking(payload)
      console.log('✅ Booking created successfully:', response)
      
      alert('Booking confirmed! You will receive a confirmation email shortly.')
      navigate('/profile')
      
    } catch (e: any) {
      console.error('❌ Booking failed:', e)
      
      // Handle authentication errors specifically
      if (e?.message?.includes('Unauthenticated')) {
        alert('Your session has expired. Please log in again.')
        navigate('/login')
      } else {
        alert(e?.message || 'Booking failed')
      }
    } finally {
      setIsProcessing(false)
    }
  }





  const days = formData.startDate && formData.endDate ? 
    Math.ceil((new Date(formData.endDate).getTime() - new Date(formData.startDate).getTime()) / (1000 * 60 * 60 * 24)) : 0

  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Header />
      
      <div className="flex-1">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <button 
                onClick={() => navigate(`/car/${car.id}`)}
                className="text-sky-600 hover:text-sky-700 transition mb-4"
              >
                ← Back to Car Details
              </button>
              <h1 className="text-3xl font-semibold text-slate-900 mb-2">Book Your Rental</h1>
              <p className="text-slate-600">Complete the form below to book your vehicle</p>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
              {/* Booking Form */}
              <div className="lg:col-span-2">
                <form onSubmit={handleSubmit} className="space-y-6">
                  {/* Authentication Status Banner */}
                  {!isAuthenticated() && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <h3 className="text-sm font-medium text-yellow-800">
                            Authentication Required
                          </h3>
                          <div className="mt-2 text-sm text-yellow-700">
                            <p>You need to be logged in to book a vehicle.</p>
                            <button
                              type="button"
                              onClick={() => navigate('/login')}
                              className="mt-2 text-yellow-800 underline hover:text-yellow-900"
                            >
                              Click here to log in
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div className="bg-white border rounded-lg p-6">
                    <h2 className="text-xl font-semibold text-slate-900 mb-4">Rental Details</h2>
                    
                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label htmlFor="pickupDate" className="block text-sm font-medium text-slate-700 mb-2">
                          Pickup Date *
                        </label>
                        <input
                          type="date"
                          id="pickupDate"
                          name="startDate"
                          value={formData.startDate}
                          onChange={handleInputChange}
                          min={new Date().toISOString().split('T')[0]}
                          required
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        />
                      </div>
                      <div>
                        <label htmlFor="returnDate" className="block text-sm font-medium text-slate-700 mb-2">
                          Return Date *
                        </label>
                        <input
                          type="date"
                          id="returnDate"
                          name="endDate"
                          value={formData.endDate}
                          onChange={handleInputChange}
                          min={formData.startDate || new Date().toISOString().split('T')[0]}
                          required
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label htmlFor="pickupLocation" className="block text-sm font-medium text-slate-700 mb-2">
                          Pickup Location *
                        </label>
                        <select
                          id="pickupLocation"
                          name="pickupLocation"
                          value={formData.pickupLocation}
                          onChange={handleInputChange}
                          required
                          aria-label="Pickup Location"
                          title="Pickup Location"
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        >
                          <option value="">Select pickup location</option>
                          <option value="Melbourne CBD">Melbourne CBD</option>
                          <option value="Melbourne Airport">Melbourne Airport</option>
                          <option value="St Kilda">St Kilda</option>
                          <option value="Richmond">Richmond</option>
                          <option value="Brunswick">Brunswick</option>
                        </select>
                      </div>
                      <div>
                        <label htmlFor="returnLocation" className="block text-sm font-medium text-slate-700 mb-2">
                          Return Location
                        </label>
                        <select
                          id="returnLocation"
                          name="returnLocation"
                          value={formData.returnLocation}
                          onChange={handleInputChange}
                          aria-label="Return Location"
                          title="Return Location"
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        >
                          <option value="">Same as pickup</option>
                          <option value="Melbourne CBD">Melbourne CBD</option>
                          <option value="Melbourne Airport">Melbourne Airport</option>
                          <option value="St Kilda">St Kilda</option>
                          <option value="Richmond">Richmond</option>
                          <option value="Brunswick">Brunswick</option>
                        </select>
                      </div>
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Phone Number *
                      </label>
                      <input
                        type="tel"
                        name="phoneNumber"
                        value={formData.phoneNumber}
                        onChange={handleInputChange}
                        placeholder="+61 4XX XXX XXX"
                        required
                        aria-label="Phone Number"
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      />
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Driver Email *
                        </label>
                        <input
                          type="email"
                          name="driverEmail"
                          value={formData.driverEmail}
                          onChange={handleInputChange}
                          placeholder="driver@example.com"
                          required
                          aria-label="Driver Email"
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Driver Full Name *
                        </label>
                        <input
                          type="text"
                          name="driverFullname"
                          value={formData.driverFullname}
                          onChange={handleInputChange}
                          placeholder="John Doe"
                          required
                          aria-label="Driver Full Name"
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          License Number *
                        </label>
                        <input
                          type="text"
                          name="licenseNumber"
                          value={formData.licenseNumber}
                          onChange={handleInputChange}
                          placeholder="123456789"
                          required
                          aria-label="License Number"
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Residential Area *
                        </label>
                        <input
                          type="text"
                          name="residentialArea"
                          value={formData.residentialArea}
                          onChange={handleInputChange}
                          placeholder="Melbourne, VIC"
                          required
                          aria-label="Residential Area"
                          className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                        />
                      </div>
                    </div>

                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Promo Code
                      </label>
                      <input
                        type="text"
                        name="promoCode"
                        value={formData.promoCode}
                        onChange={handleInputChange}
                        placeholder="Enter promo code"
                        aria-label="Promo Code"
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">
                        Special Requests
                      </label>
                      <textarea
                        name="specialRequests"
                        value={formData.specialRequests}
                        onChange={handleInputChange}
                        rows={3}
                        placeholder="Any special requests or notes..."
                        aria-label="Special Requests"
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      />
                    </div>

                    <div>
                      <label htmlFor="paymentFrequency" className="block text-sm font-medium text-slate-700 mb-2">
                        Payment Frequency *
                      </label>
                      <select
                        id="paymentFrequency"
                        value={paymentFrequency}
                        onChange={(e) => setPaymentFrequency(e.target.value as '3days' | 'weekly')}
                        required
                        aria-label="Payment Frequency"
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      >
                        <option value="weekly">Weekly</option>
                        <option value="3days">Every 3 days</option>
                      </select>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isProcessing || !isAuthenticated()}
                    className="w-full py-3 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition font-medium disabled:bg-slate-400 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? (
                      <span className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing Booking...
                      </span>
                    ) : !isAuthenticated() ? (
                      'Please Log In to Book'
                    ) : (
                      'Confirm Booking'
                    )}
                  </button>
                </form>
              </div>

              {/* Booking Summary */}
              <div>
                <div className="bg-slate-50 border rounded-lg p-6 sticky top-4">
                  <h3 className="text-lg font-semibold text-slate-900 mb-4">Booking Summary</h3>
                  
                  <div className="space-y-3 mb-6">
                    <div className="flex gap-3">
                      <img 
                        src={
                          car.images && car.images.length > 0 
                            ? (typeof car.images[0] === 'string' 
                                ? buildImageUrl(car.images[0]) 
                                : buildImageUrl(car.images[0].image_url))
                            : '/images/cars/sedan-silver.png'
                        } 
                        alt={`${car.make} ${car.model}`}
                        className="w-16 h-12 object-cover rounded"
                      />
                      <div>
                        <p className="font-medium text-slate-900">
                          {car.year} {car.make} {car.model}
                        </p>
                        <p className="text-sm text-slate-600">
                          {typeof car.category === 'object' ? car.category.name : car.category}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2 text-sm">
                    {formData.startDate && formData.endDate && (
                      <>
                        <div className="flex justify-between">
                          <span>Duration:</span>
                          <span>{days} day{days !== 1 ? 's' : ''}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Rate per day:</span>
                          <span>${Number(car.rental_rate_per_day)}</span>
                        </div>
                        <hr className="my-2" />
                        <div className="flex justify-between font-semibold">
                          <span>Total:</span>
                          <span>${totalCost}</span>
                        </div>
                      </>
                    )}
                  </div>

                  {(!formData.startDate || !formData.endDate) && (
                    <p className="text-sm text-slate-500 mt-4">
                      Select dates to see pricing
                    </p>
                  )}

                  <div className="mt-6 p-3 bg-green-50 rounded-md">
                    <p className="text-xs text-green-700">
                      ✓ Free cancellation up to 24 hours before pickup
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}

export default BookPage
