import * as React from 'react'
import type { Car } from '../lib/types'
import { buildImageUrl } from '../lib/api'

const CarCard: React.FC<{ car: Car }> = ({ car }) => {
  const title = `${car.year} ${car.make} ${car.model}`
  const imagePath = (car as any).images?.[0]?.image_url || (car as any).image_url
  const [imageError, setImageError] = React.useState(false)
  const [imageSrc, setImageSrc] = React.useState(() => buildImageUrl(imagePath))
  
  const category = (car as any).category?.name || (car as any).category
  const agency = (car as any).agency?.name || (car as any).agency
  
  const handleImageError = () => {
    console.warn('🖼️ Image failed to load:', imageSrc)
    setImageError(true)
    setImageSrc('/images/cars/sedan-silver.png')
  }

  return (
    <div className="flex flex-col overflow-hidden rounded-xl border bg-white transition-all hover:-translate-y-0.5 hover:shadow-lg">
      <div className="relative w-full h-44 bg-sky-50">
        {!imageError ? (
          <img
            src={imageSrc}
            alt={title}
            className="w-full h-44 object-cover"
            onError={handleImageError}
            onLoad={() => console.log('🖼️ Image loaded successfully:', imageSrc)}
          />
        ) : (
          <div className="w-full h-44 flex items-center justify-center bg-sky-100">
            <div className="text-center text-sky-600">
              <div className="text-2xl mb-2">🚗</div>
              <div className="text-sm font-medium">{title}</div>
            </div>
          </div>
        )}
      </div>
      <div className="space-y-2 p-4">
        <div className="text-base font-semibold">{title}</div>
        <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
          <span className="rounded border px-2 py-0.5 bg-sky-50 text-sky-700">{agency}</span>
          <span className="rounded border px-2 py-0.5 bg-white">{category}</span>
          <span className="rounded border px-2 py-0.5">{car.transmission}</span>
          <span className="rounded border px-2 py-0.5">{car.fuel_type}</span>
          <span className="rounded border px-2 py-0.5">{car.seats} seats</span>
        </div>
        <div className="text-sm"><span className="font-semibold">${Number((car as any).rental_rate_per_day).toLocaleString()}</span><span className="text-muted-foreground"> / day</span></div>
      </div>
      <div className="mt-auto p-4 pt-0">
        <div className="flex w-full items-center gap-2">
          <a href={`/car/${car.id}`} className="w-full inline-flex items-center justify-center rounded-md bg-sky-600 hover:bg-sky-700 h-9 text-white text-sm">View</a>
          <a href={`/book/${car.id}`} className="w-full inline-flex items-center justify-center rounded-md border bg-white hover:border-sky-300 h-9 text-sm">Book</a>
        </div>
      </div>
    </div>
  )
}

export default CarCard


