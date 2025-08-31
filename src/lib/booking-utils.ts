import type { Booking, Car } from './types'
import { DEMO_BOOKINGS } from './demo-data'

// Check if a car is available for a given date range
export function isCarAvailable(
  carId: number, 
  startDate: string, 
  endDate: string, 
  excludeBookingId?: number
): boolean {
  const conflictingBookings = DEMO_BOOKINGS.filter(booking => {
    // Skip the booking we're updating (if any)
    if (excludeBookingId && booking.id === excludeBookingId) {
      return false
    }

    // Only check bookings for the same car
    if (booking.car_id !== carId) {
      return false
    }

    // Only check active bookings (not cancelled or completed)
    if (booking.status === 'cancelled' || booking.status === 'completed') {
      return false
    }

    // Check for date overlap
    const bookingStart = new Date(booking.start_date)
    const bookingEnd = new Date(booking.end_date)
    const requestedStart = new Date(startDate)
    const requestedEnd = new Date(endDate)

    // Check if there's any overlap
    return (
      (requestedStart <= bookingEnd && requestedEnd >= bookingStart) ||
      (bookingStart <= requestedEnd && bookingEnd >= requestedStart)
    )
  })

  return conflictingBookings.length === 0
}

// Get all available cars for a given date range
export function getAvailableCarsForPeriod(
  startDate: string, 
  endDate: string, 
  cars: Car[]
): Car[] {
  return cars.filter(car => {
    // First check if car is not under maintenance
    if (car.status === 'under_maintenance' || car.status === 'due_for_service') {
      return false
    }

    // Then check for booking conflicts
    return isCarAvailable(car.id, startDate, endDate)
  })
}

// Calculate rental duration in days
export function calculateRentalDuration(startDate: string, endDate: string): number {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

// Calculate total cost for a booking
export function calculateBookingCost(
  car: Car, 
  startDate: string, 
  endDate: string, 
  promoCode?: string
): number {
  const duration = calculateRentalDuration(startDate, endDate)
  let totalCost = Number(car.rental_rate_per_day) * duration

  // Apply promo code discount if provided
  if (promoCode) {
    const discount = getPromoCodeDiscount(promoCode)
    totalCost = totalCost * (1 - discount)
  }

  return Math.round(totalCost * 100) / 100 // Round to 2 decimal places
}

// Get promo code discount (placeholder for now)
export function getPromoCodeDiscount(promoCode: string): number {
  // This would typically query a database
  const promoCodes: Record<string, number> = {
    'WELCOME10': 0.10,
    'SUMMER20': 0.20,
    'LOYALTY15': 0.15
  }
  return promoCodes[promoCode.toUpperCase()] || 0
}

// Validate booking dates
export function validateBookingDates(startDate: string, endDate: string): {
  isValid: boolean
  error?: string
} {
  const start = new Date(startDate)
  const end = new Date(endDate)
  const now = new Date()

  // Check if dates are in the future
  if (start < now) {
    return { isValid: false, error: 'Start date must be in the future' }
  }

  if (end < now) {
    return { isValid: false, error: 'End date must be in the future' }
  }

  // Check if end date is after start date
  if (end <= start) {
    return { isValid: false, error: 'End date must be after start date' }
  }

  // Check if booking is not too far in the future (e.g., 1 year)
  const maxDate = new Date()
  maxDate.setFullYear(maxDate.getFullYear() + 1)
  if (end > maxDate) {
    return { isValid: false, error: 'Booking cannot be more than 1 year in advance' }
  }

  // Check minimum rental duration (e.g., 1 day)
  const duration = calculateRentalDuration(startDate, endDate)
  if (duration < 1) {
    return { isValid: false, error: 'Minimum rental duration is 1 day' }
  }

  return { isValid: true }
}

// Get booking conflicts for a car
export function getBookingConflicts(
  carId: number, 
  startDate: string, 
  endDate: string, 
  excludeBookingId?: number
): Booking[] {
  return DEMO_BOOKINGS.filter(booking => {
    if (excludeBookingId && booking.id === excludeBookingId) {
      return false
    }

    if (booking.car_id !== carId) {
      return false
    }

    if (booking.status === 'cancelled' || booking.status === 'completed') {
      return false
    }

    const bookingStart = new Date(booking.start_date)
    const bookingEnd = new Date(booking.end_date)
    const requestedStart = new Date(startDate)
    const requestedEnd = new Date(endDate)

    return (
      (requestedStart <= bookingEnd && requestedEnd >= bookingStart) ||
      (bookingStart <= requestedEnd && bookingEnd >= requestedStart)
    )
  })
}

// Check if a car is due for service
export function isCarDueForService(car: Car): boolean {
  const kmSinceService = car.current_odometer - car.last_service_odometer
  return kmSinceService >= car.service_threshold_km
}

// Get cars that are due for service
export function getCarsDueForService(cars: Car[]): Car[] {
  return cars.filter(car => isCarDueForService(car))
}

// Update car odometer and check service status
export function updateCarOdometer(
  car: Car, 
  newOdometer: number
): { updatedCar: Car; needsService: boolean } {
  const updatedCar = {
    ...car,
    current_odometer: newOdometer,
    updated_at: new Date().toISOString()
  }

  const needsService = isCarDueForService(updatedCar)

  if (needsService) {
    updatedCar.status = 'due_for_service'
  }

  return { updatedCar, needsService }
}
