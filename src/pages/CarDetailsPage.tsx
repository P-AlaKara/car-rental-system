import * as React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import Footer from '../components/Footer'
import { fleetAPI, buildImageUrl } from '../lib/api'

function CarDetailsPage() {
  const { carId } = useParams<{ carId: string }>()
  const navigate = useNavigate()
  const [selectedImage, setSelectedImage] = React.useState(0)
  const [car, setCar] = React.useState<any | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    const id = Number(carId)
    if (!id) return
    ;(async () => {
      try {
        setLoading(true)
        setError(null)
        const resp = await fleetAPI.getCar(id)
        setCar(resp.data)
      } catch (e: any) {
        setError(e?.message || 'Failed to load car')
      } finally {
        setLoading(false)
      }
    })()
  }, [carId])

  if (loading) {
    return (
      <main className="min-h-screen flex flex-col bg-white">
        <Header />
        <div className="flex-1 flex items-center justify-center text-slate-600">Loading car...</div>
        <Footer />
      </main>
    )
  }

  if (error || !car) {
    return (
      <main className="min-h-screen flex flex-col bg-white">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-semibold text-slate-900 mb-2">Car not found</h1>
            {error && <p className="text-red-600 mb-4">{error}</p>}
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

  const images = (car.images && car.images.length > 0)
    ? car.images.map((img: any) => buildImageUrl(img.image_url) || '/images/cars/sedan-silver.png')
    : [
        '/images/cars/sedan-silver.png',
        '/images/cars/sedan-interior.png',
        '/images/cars/sedan-urban.png'
      ]

  const handleBooking = () => {
    navigate(`/book/${car.id}`)
  }

  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Header />
      
      <div className="flex-1">
        <div className="container mx-auto px-4 py-8">
          {/* Breadcrumb */}
          <nav className="mb-6">
            <button 
              onClick={() => navigate('/cars')}
              className="text-sky-600 hover:text-sky-700 transition"
            >
              ← Back to Cars
            </button>
          </nav>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Images */}
            <div className="space-y-4">
              <div className="aspect-video bg-slate-100 rounded-lg overflow-hidden">
                <img 
                  src={images[selectedImage]} 
                  alt={`${car.make} ${car.model}`}
                  className="w-full h-full object-cover"
                />
              </div>
              <div className="grid grid-cols-3 gap-2">
                {images.map((img: string, index: number) => (
                  <button
                    key={index}
                    onClick={() => setSelectedImage(index)}
                    aria-label={`Select image ${index + 1}`}
                    className={`aspect-video rounded-md overflow-hidden border-2 transition ${
                      selectedImage === index ? 'border-sky-500' : 'border-slate-200'
                    }`}
                  >
                    <img src={img} alt={`Car image ${index + 1}`} className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            </div>

            {/* Details */}
            <div className="space-y-6">
              <div>
                <h1 className="text-3xl font-semibold text-slate-900 mb-2">{car.year} {car.make} {car.model}</h1>
                <div className="flex items-center gap-2 mb-4">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${String(car.status).toLowerCase().includes('available') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>{String(car.status).toLowerCase().includes('available') ? 'Available' : 'Not Available'}</span>
                  <span className="px-2 py-1 rounded-full text-xs font-medium bg-sky-100 text-sky-800">
                    {car.category?.name || car.category || 'Category'}
                  </span>
                </div>
                <p className="text-3xl font-bold text-sky-600 mb-4">
                  ${Number(car.rental_rate_per_day).toLocaleString()}
                  <span className="text-lg text-slate-600 font-normal">/day</span>
                </p>
              </div>

              {/* Specifications */}
              <div className="bg-slate-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Specifications</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm text-slate-600">Year</span>
                    <p className="font-medium">{car.year}</p>
                  </div>
                  <div>
                    <span className="text-sm text-slate-600">Seats</span>
                    <p className="font-medium">{car.seats}</p>
                  </div>
                  <div>
                    <span className="text-sm text-slate-600">Transmission</span>
                    <p className="font-medium">{car.transmission}</p>
                  </div>
                  <div>
                    <span className="text-sm text-slate-600">Fuel Type</span>
                    <p className="font-medium">{car.fuel_type}</p>
                  </div>
                  <div>
                    <span className="text-sm text-slate-600">License Plate</span>
                    <p className="font-medium">{car.license_plate}</p>
                  </div>
                  <div>
                    <span className="text-sm text-slate-600">Agency</span>
                    <p className="font-medium">{car.agency?.name || '—'}</p>
                  </div>
                </div>
              </div>

              {/* Features */}
              <div>
                <h3 className="text-lg font-semibold text-slate-900 mb-4">Features</h3>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    'Air Conditioning',
                    'Bluetooth',
                    'GPS Navigation',
                    'Cruise Control',
                    'Power Steering',
                    'Central Locking'
                  ].map((feature) => (
                    <div key={feature} className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-sm text-slate-700">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Booking */}
              <div className="border-t pt-6">
                {car.status === 'available' ? (
                  <button
                    onClick={handleBooking}
                    className="w-full py-3 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition font-medium"
                  >
                    Book This Car
                  </button>
                ) : (
                  <button 
                    disabled
                    className="w-full py-3 bg-slate-300 text-slate-500 rounded-md cursor-not-allowed font-medium"
                  >
                    Currently Unavailable
                  </button>
                )}
                <p className="text-xs text-slate-500 mt-2 text-center">
                  Free cancellation up to 24 hours before pickup
                </p>
              </div>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-12 grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-sky-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="font-semibold text-slate-900 mb-2">Quality Assured</h4>
              <p className="text-sm text-slate-600">Regular maintenance and safety checks</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-sky-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="font-semibold text-slate-900 mb-2">24/7 Support</h4>
              <p className="text-sm text-slate-600">Round-the-clock assistance during your rental</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-sky-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h4 className="font-semibold text-slate-900 mb-2">Flexible Payment</h4>
              <p className="text-sm text-slate-600">Multiple payment options available</p>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}

export default CarDetailsPage
