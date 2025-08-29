import * as React from 'react'
import { fleetAPI, type Car } from '../lib/api'

interface CarDetailModalProps {
  carId: number
  isOpen: boolean
  onClose: () => void
  onCarUpdate?: () => void
}

const CarDetailModal: React.FC<CarDetailModalProps> = ({ carId, isOpen, onClose, onCarUpdate }) => {
  const [car, setCar] = React.useState<Car | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string>('')
  const [currentImageIndex, setCurrentImageIndex] = React.useState(0)
  const [fullScreenImage, setFullScreenImage] = React.useState<string | null>(null)
  const [uploadingImages, setUploadingImages] = React.useState(false)
  const [selectedFiles, setSelectedFiles] = React.useState<File[]>([])

  React.useEffect(() => {
    if (isOpen && carId) {
      loadCarDetails()
    }
  }, [isOpen, carId])

  const loadCarDetails = async () => {
    try {
      setLoading(true)
      setError('')
      console.log('🚗 Loading car details for ID:', carId)
      
      const response = await fleetAPI.getCar(carId)
      console.log('✅ Car details loaded:', response.data)
      setCar(response.data)
      setCurrentImageIndex(0)
    } catch (err: any) {
      console.error('❌ Failed to load car details:', err)
      setError(err.message || 'Failed to load car details')
    } finally {
      setLoading(false)
    }
  }

  const handleAddImages = async () => {
    if (selectedFiles.length === 0 || !car) return

    try {
      setUploadingImages(true)
      console.log('📸 Uploading images for car:', car.id)
      
      await fleetAPI.addCarImages(car.id, selectedFiles)
      console.log('✅ Images uploaded successfully')
      
      // Reload car details to get updated images
      await loadCarDetails()
      setSelectedFiles([])
      
      // Clear the file input
      const fileInput = document.getElementById('add-images-input') as HTMLInputElement
      if (fileInput) fileInput.value = ''
      
      if (onCarUpdate) onCarUpdate()
    } catch (err: any) {
      console.error('❌ Failed to upload images:', err)
      setError(err.message || 'Failed to upload images')
    } finally {
      setUploadingImages(false)
    }
  }

  const handleDeleteImage = async (imageId: number) => {
    if (!car || !window.confirm('Are you sure you want to delete this image?')) return

    try {
      console.log('🗑️ Deleting image:', imageId)
      await fleetAPI.deleteCarImage(imageId)
      console.log('✅ Image deleted successfully')
      
      // Reload car details to get updated images
      await loadCarDetails()
      
      if (onCarUpdate) onCarUpdate()
    } catch (err: any) {
      console.error('❌ Failed to delete image:', err)
      setError(err.message || 'Failed to delete image')
    }
  }

  const nextImage = () => {
    if (car && car.images.length > 1) {
      setCurrentImageIndex((prev) => (prev + 1) % car.images.length)
    }
  }

  const prevImage = () => {
    if (car && car.images.length > 1) {
      setCurrentImageIndex((prev) => (prev - 1 + car.images.length) % car.images.length)
    }
  }

  if (!isOpen) return null

  return (
    <>
      {/* Main Modal */}
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-xl">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-semibold text-gray-900">
                {loading ? 'Loading...' : car ? `${car.year} ${car.make} ${car.model}` : 'Car Details'}
              </h3>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <div className="flex items-center gap-2 text-red-800">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  {error}
                </div>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-sky-600"></div>
                <span className="ml-2 text-gray-600">Loading car details...</span>
              </div>
            )}

            {/* Car Details */}
            {car && !loading && (
              <div className="space-y-6">
                {/* Images Section */}
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Images ({car.images.length})</h4>
                  
                  {car.images.length > 0 ? (
                    <div className="space-y-4">
                      {/* Main Image Display */}
                      <div className="relative">
                        <img
                          src={car.images[currentImageIndex]?.image_url}
                          alt={`${car.make} ${car.model} - Image ${currentImageIndex + 1}`}
                          className="w-full h-64 object-cover rounded-lg border border-gray-300 cursor-pointer"
                          onClick={() => setFullScreenImage(car.images[currentImageIndex]?.image_url)}
                        />
                        
                        {/* Navigation Arrows */}
                        {car.images.length > 1 && (
                          <>
                            <button
                              onClick={prevImage}
                              className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-opacity"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                              </svg>
                            </button>
                            <button
                              onClick={nextImage}
                              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-70 transition-opacity"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                              </svg>
                            </button>
                          </>
                        )}
                        
                        {/* Image Counter */}
                        {car.images.length > 1 && (
                          <div className="absolute bottom-2 right-2 bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                            {currentImageIndex + 1} / {car.images.length}
                          </div>
                        )}
                        
                        {/* Delete Current Image Button */}
                        <button
                          onClick={() => handleDeleteImage(car.images[currentImageIndex].id)}
                          className="absolute top-2 right-2 bg-red-500 text-white p-2 rounded-full hover:bg-red-600 transition-colors"
                          title="Delete this image"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                      
                      {/* Thumbnail Navigation */}
                      {car.images.length > 1 && (
                        <div className="flex gap-2 overflow-x-auto pb-2">
                          {car.images.map((image, index) => (
                            <button
                              key={image.id}
                              onClick={() => setCurrentImageIndex(index)}
                              className={`flex-shrink-0 w-16 h-16 rounded-lg border-2 overflow-hidden ${
                                index === currentImageIndex ? 'border-sky-500' : 'border-gray-300'
                              }`}
                            >
                              <img
                                src={image.image_url}
                                alt={`Thumbnail ${index + 1}`}
                                className="w-full h-full object-cover"
                              />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      No images available for this car
                    </div>
                  )}
                  
                  {/* Add Images Section */}
                  <div className="mt-6 p-4 border border-gray-200 rounded-lg">
                    <h5 className="font-medium text-gray-900 mb-3">Add More Images</h5>
                    <div className="space-y-3">
                      <input
                        id="add-images-input"
                        type="file"
                        accept="image/*"
                        multiple
                        onChange={(e) => setSelectedFiles(Array.from(e.target.files || []))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      />
                      
                      {selectedFiles.length > 0 && (
                        <div>
                          <p className="text-sm text-gray-600 mb-2">{selectedFiles.length} file(s) selected</p>
                          <div className="flex gap-2">
                            <button
                              onClick={handleAddImages}
                              disabled={uploadingImages}
                              className="px-4 py-2 bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors disabled:opacity-50"
                            >
                              {uploadingImages ? 'Uploading...' : 'Upload Images'}
                            </button>
                            <button
                              onClick={() => {
                                setSelectedFiles([])
                                const fileInput = document.getElementById('add-images-input') as HTMLInputElement
                                if (fileInput) fileInput.value = ''
                              }}
                              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                            >
                              Cancel
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Car Information */}
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Vehicle Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Make & Model</label>
                        <p className="mt-1 text-sm text-gray-900">{car.make} {car.model} ({car.year})</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">License Plate</label>
                        <p className="mt-1 text-sm text-gray-900">{car.license_plate}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Category</label>
                        <p className="mt-1 text-sm text-gray-900">{car.category?.name || 'Unknown'}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Status</label>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          car.status === 'Available' ? 'bg-green-100 text-green-800' :
                          car.status === 'Under_maintenance' ? 'bg-orange-100 text-orange-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {car.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Transmission & Fuel</label>
                        <p className="mt-1 text-sm text-gray-900">{car.transmission} • {car.fuel_type}</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Seats</label>
                        <p className="mt-1 text-sm text-gray-900">{car.seats} passengers</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">Daily Rate</label>
                        <p className="mt-1 text-sm text-gray-900">${car.rental_rate_per_day}/day</p>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">VIN</label>
                        <p className="mt-1 text-sm text-gray-900 font-mono">{car.vin}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Maintenance Information */}
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Maintenance Information</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Current Odometer</label>
                      <p className="mt-1 text-sm text-gray-900">{car.current_odometer?.toLocaleString() || 0} km</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Last Service</label>
                      <p className="mt-1 text-sm text-gray-900">{car.last_service_odometer?.toLocaleString() || 0} km</p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Service Threshold</label>
                      <p className="mt-1 text-sm text-gray-900">{car.service_threshold_km?.toLocaleString() || 0} km</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700">Insurance Expiry</label>
                    <p className="mt-1 text-sm text-gray-900">{car.insurance_expiry_date}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Close Button */}
            <div className="flex justify-end mt-6 pt-4 border-t">
              <button
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Full Screen Image Modal */}
      {fullScreenImage && (
        <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-[60]">
          <div className="relative max-w-full max-h-full p-4">
            <img
              src={fullScreenImage}
              alt="Full screen view"
              className="max-w-full max-h-full object-contain"
            />
            <button
              onClick={() => setFullScreenImage(null)}
              className="absolute top-6 right-6 bg-white bg-opacity-20 text-white p-3 rounded-full hover:bg-opacity-30 transition-opacity"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      )}
    </>
  )
}

export default CarDetailModal
