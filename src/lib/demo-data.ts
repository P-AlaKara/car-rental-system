import type { Car, Booking, Profile, UsageLog, ServiceRecord, AgencyLocation, Agency } from './types'

// Agency Location Data
export const AGENCY_LOCATIONS: AgencyLocation[] = [
  {
    id: 'Aurora motors',
    name: 'Aurora Motors - Dandenong',
    address: 'Unit 2/11 Burrows Avenue',
    city: 'Dandenong',
    state: 'VIC',
    postcode: '3175',
    phone: '0420 759 910',
    email: 'smartrentals1@gmail.com'
  },
  {
    id: 'Smart',
    name: 'Smart Rentals - Melbourne CBD',
    address: '123 Collins Street',
    city: 'Melbourne',
    state: 'VIC',
    postcode: '3000',
    phone: '0420 759 911',
    email: 'melbourne@auroramotors.com'
  },
  {
    id: 'JNK',
    name: 'JNK Rentals - Southbank',
    address: '456 Southbank Boulevard',
    city: 'Southbank',
    state: 'VIC',
    postcode: '3006',
    phone: '0420 759 912',
    email: 'southbank@auroramotors.com'
  }
]

// Enhanced Demo Cars with Realistic Data
export const DEMO_CARS: Car[] = [
  {
    id: 101,
    make: 'Toyota',
    model: 'Corolla',
    year: 2022,
    license_plate: 'ABC-123',
    agency: 'Aurora motors',
    category: 'Sedan',
    transmission: 'Automatic',
    fuel_type: 'Petrol',
    seats: 5,
    rental_rate_per_day: 89,
    status: 'available',
    current_odometer: 15420,
    last_service_odometer: 12000,
    service_threshold_km: 5000,
    image_url: '/images/cars/sedan-white.png',
    created_at: '2024-01-15T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  },
  {
    id: 102,
    make: 'Honda',
    model: 'Civic',
    year: 2023,
    license_plate: 'XYZ-789',
    agency: 'Aurora motors',
    category: 'Sedan',
    transmission: 'CVT',
    fuel_type: 'Hybrid',
    seats: 5,
    rental_rate_per_day: 95,
    status: 'booked',
    current_odometer: 8900,
    last_service_odometer: 5000,
    service_threshold_km: 5000,
    image_url: '/images/cars/sedan-silver.png',
    created_at: '2024-02-10T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  },
  {
    id: 103,
    make: 'Hyundai',
    model: 'Tucson',
    year: 2021,
    license_plate: 'DEF-456',
    agency: 'Smart',
    category: 'SUV',
    transmission: 'Automatic',
    fuel_type: 'Petrol',
    seats: 5,
    rental_rate_per_day: 110,
    status: 'in_use',
    current_odometer: 28750,
    last_service_odometer: 25000,
    service_threshold_km: 5000,
    image_url: '/images/cars/suv-blue.png',
    created_at: '2024-01-20T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  },
  {
    id: 104,
    make: 'Kia',
    model: 'Sportage',
    year: 2022,
    license_plate: 'GHI-789',
    agency: 'Smart',
    category: 'SUV',
    transmission: 'Automatic',
    fuel_type: 'Diesel',
    seats: 5,
    rental_rate_per_day: 115,
    status: 'under_maintenance',
    current_odometer: 32100,
    last_service_odometer: 30000,
    service_threshold_km: 5000,
    image_url: '/images/cars/suv-black.png',
    created_at: '2024-03-05T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  },
  {
    id: 105,
    make: 'Toyota',
    model: 'Hilux',
    year: 2021,
    license_plate: 'JKL-012',
    agency: 'JNK',
    category: 'Van',
    transmission: 'Manual',
    fuel_type: 'Diesel',
    seats: 5,
    rental_rate_per_day: 125,
    status: 'available',
    current_odometer: 18900,
    last_service_odometer: 15000,
    service_threshold_km: 5000,
    image_url: '/images/cars/van-white.png',
    created_at: '2024-01-10T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  },
  {
    id: 106,
    make: 'Tesla',
    model: 'Model 3',
    year: 2023,
    license_plate: 'MNO-345',
    agency: 'Aurora motors',
    category: 'Electric',
    transmission: 'Automatic',
    fuel_type: 'Electric',
    seats: 5,
    rental_rate_per_day: 150,
    status: 'available',
    current_odometer: 12300,
    last_service_odometer: 10000,
    service_threshold_km: 10000,
    image_url: '/images/cars/sedan-white.png',
    created_at: '2024-04-15T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  }
]

// Demo Users
export const DEMO_USERS: Profile[] = [
  {
    id: 1,
    email: 'admin@auroramotors.com',
    first_name: 'Admin',
    last_name: 'User',
    phone: '+61420123456',
    role: 'admin',
    loyalty_points: 0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  },
  {
    id: 2,
    email: 'john.doe@example.com',
    first_name: 'John',
    last_name: 'Doe',
    phone: '+61420987654',
    role: 'customer',
    loyalty_points: 250,
    created_at: '2024-02-15T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  },
  {
    id: 3,
    email: 'jane.smith@example.com',
    first_name: 'Jane',
    last_name: 'Smith',
    phone: '+61420111222',
    role: 'customer',
    loyalty_points: 120,
    created_at: '2024-03-10T00:00:00Z',
    updated_at: '2024-08-19T00:00:00Z'
  }
]

// Demo Bookings with Various Statuses
export const DEMO_BOOKINGS: Booking[] = [
  {
    id: 1001,
    user_id: 2,
    car_id: 102,
    start_date: '2024-08-20T09:00:00Z',
    end_date: '2024-08-22T17:00:00Z',
    pickup_location: 'Dandenong VIC',
    return_location: 'Dandenong VIC',
    special_requests: 'GPS and child seat required',
    phone_number: '+61420987654',
    status: 'confirmed',
    payment_status: 'paid',
    total_cost: 190,
    pickup_odometer: 8900,
    fuel_level_pickup: 85,
    created_at: '2024-08-18T10:30:00Z',
    updated_at: '2024-08-19T14:00:00Z'
  },
  {
    id: 1002,
    user_id: 3,
    car_id: 103,
    start_date: '2024-08-19T08:00:00Z',
    end_date: '2024-08-21T18:00:00Z',
    pickup_location: 'Melbourne VIC',
    return_location: 'Melbourne VIC',
    phone_number: '+61420111222',
    status: 'in_progress',
    payment_status: 'paid',
    total_cost: 220,
    pickup_odometer: 28750,
    fuel_level_pickup: 90,
    pickup_photo_url: '/images/pickup-photos/booking-1002.jpg',
    created_at: '2024-08-17T15:45:00Z',
    updated_at: '2024-08-19T08:00:00Z'
  },
  {
    id: 1003,
    user_id: 2,
    car_id: 101,
    start_date: '2024-08-25T10:00:00Z',
    end_date: '2024-08-27T16:00:00Z',
    pickup_location: 'Dandenong VIC',
    return_location: 'Dandenong VIC',
    phone_number: '+61420987654',
    status: 'pending',
    payment_status: 'pending',
    total_cost: 178,
    created_at: '2024-08-19T11:20:00Z',
    updated_at: '2024-08-19T11:20:00Z'
  }
]

// Demo Usage Logs
export const DEMO_USAGE_LOGS: UsageLog[] = [
  {
    id: 1,
    booking_id: 1002,
    car_id: 103,
    user_id: 3,
    pickup_timestamp: '2024-08-19T08:00:00Z',
    pickup_odometer: 28750,
    fuel_level_pickup: 90,
    pickup_photo_url: '/images/pickup-photos/booking-1002.jpg',
    created_at: '2024-08-19T08:00:00Z',
    updated_at: '2024-08-19T08:00:00Z'
  }
]

// Demo Service Records
export const DEMO_SERVICE_RECORDS: ServiceRecord[] = [
  {
    id: 1,
    car_id: 104,
    service_date: '2024-08-18T00:00:00Z',
    odometer_reading: 32100,
    service_type: 'routine',
    description: 'Oil change, filter replacement, brake inspection',
    cost: 350,
    next_service_odometer: 37100,
    created_at: '2024-08-18T00:00:00Z'
  },
  {
    id: 2,
    car_id: 101,
    service_date: '2024-07-15T00:00:00Z',
    odometer_reading: 12000,
    service_type: 'routine',
    description: 'Oil change, tire rotation, general inspection',
    cost: 280,
    next_service_odometer: 17000,
    created_at: '2024-07-15T00:00:00Z'
  }
]

// Enhanced Filter Function
export function filterDemoCars(query: URLSearchParams) {
  let data = [...DEMO_CARS]
  const make = query.get('make')?.toLowerCase()
  const category = query.get('category') || undefined
  const transmission = query.get('transmission') || undefined
  const fuel = query.get('fuel_type') || undefined
  const seats = Number(query.get('seats') || 0)
  const min = Number(query.get('min_price') || 0)
  const max = Number(query.get('max_price') || 100000)
  const status = query.get('status') || undefined

  if (make) data = data.filter((c) => [c.make, c.model].join(' ').toLowerCase().includes(make))
  if (category && category !== 'Any') data = data.filter((c) => c.category === category)
  if (transmission && transmission !== 'Any') data = data.filter((c) => c.transmission === transmission)
  if (fuel && fuel !== 'Any') data = data.filter((c) => c.fuel_type === fuel)
  if (seats) data = data.filter((c) => c.seats >= seats)
  if (status && status !== 'Any') data = data.filter((c) => c.status === status)
  data = data.filter((c) => Number(c.rental_rate_per_day) >= min && Number(c.rental_rate_per_day) <= max)

  const page = Number(query.get('page') || 1)
  const per_page = Number(query.get('per_page') || 12)
  const total = data.length
  const start = (page - 1) * per_page
  const items = data.slice(start, start + per_page)
  const total_pages = Math.max(1, Math.ceil(total / per_page))

  return { cars: items, pagination: { page, per_page, total, total_pages } }
}

// Helper Functions
export function getAvailableCars(): Car[] {
  return DEMO_CARS.filter(car => car.status === 'available')
}

export function getCarsDueForService(): Car[] {
  return DEMO_CARS.filter(car => {
    const kmSinceService = car.current_odometer - car.last_service_odometer
    return kmSinceService >= car.service_threshold_km
  })
}

export function getPendingPayments(): Booking[] {
  return DEMO_BOOKINGS.filter(booking => booking.payment_status === 'pending')
}

export function getActiveBookings(): Booking[] {
  return DEMO_BOOKINGS.filter(booking => 
    booking.status === 'confirmed' || booking.status === 'in_progress'
  )
}

// Helper function to get agency location by ID
export function getAgencyLocation(agencyId: Agency): AgencyLocation | undefined {
  return AGENCY_LOCATIONS.find(agency => agency.id === agencyId)
}

// Helper function to get formatted agency address
export function getAgencyAddress(agencyId: Agency): string {
  const agency = getAgencyLocation(agencyId)
  if (!agency) return 'Location not specified'
  return `${agency.address}, ${agency.city} ${agency.state} ${agency.postcode}`
}
