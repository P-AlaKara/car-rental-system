import * as React from 'react'
import type { Car } from '../lib/types'

const CarCard: React.FC<{ car: Car }> = ({ car }) => {
  const title = `${car.year} ${car.make} ${car.model}`
  return (
    <div className="flex flex-col overflow-hidden rounded-xl border bg-white transition-all hover:-translate-y-0.5 hover:shadow-lg">
      <img
        src={car.image_url || '/placeholder.svg'}
        alt={title}
        className="w-full h-44 object-cover bg-sky-50"
      />
      <div className="space-y-2 p-4">
        <div className="text-base font-semibold">{title}</div>
        <div className="flex flex-wrap gap-2 text-xs text-muted-foreground">
          <span className="rounded border px-2 py-0.5 bg-sky-50 text-sky-700">{car.agency}</span>
          <span className="rounded border px-2 py-0.5 bg-white">{car.category}</span>
          <span className="rounded border px-2 py-0.5">{car.transmission}</span>
          <span className="rounded border px-2 py-0.5">{car.fuel_type}</span>
          <span className="rounded border px-2 py-0.5">{car.seats} seats</span>
        </div>
        <div className="text-sm"><span className="font-semibold">${car.rental_rate_per_day.toLocaleString()}</span><span className="text-muted-foreground"> / day</span></div>
      </div>
      <div className="mt-auto p-4 pt-0">
        <div className="flex w-full items-center gap-2">
          <a href="/login" className="w-full inline-flex items-center justify-center rounded-md bg-sky-600 hover:bg-sky-700 h-9 text-white text-sm">View</a>
          <a href="/login" className="w-full inline-flex items-center justify-center rounded-md border bg-white hover:border-sky-300 h-9 text-sm">Book</a>
        </div>
      </div>
    </div>
  )
}

export default CarCard


