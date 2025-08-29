import type { Profile, Booking, DashboardData } from './types'
import { authAPI, type User, type LoginRequest, type RegisterRequest } from './api'

const USER_KEY = 'am_user'
const DASHBOARD_KEY = 'am_dashboard'
const BOOKINGS_KEY = 'am_bookings'

export function getCurrentUser(): Profile | null {
  try { 
    const userData = localStorage.getItem(USER_KEY)
    if (!userData) return null
    
    const user: User = JSON.parse(userData)
    
    // Convert API User to Profile type for compatibility
    return {
      id: user.id,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      role: user.role,
      loyalty_points: user.loyalty_points || 0,
      created_at: user.created_at,
      updated_at: user.updated_at,
      phone: user.phone,
      agency: user.agency,
      is_active: user.is_active
    }
  } catch { 
    return null 
  }
}

export function getCurrentDashboard(): DashboardData | null {
  try {
    const dashboardData = localStorage.getItem(DASHBOARD_KEY)
    if (!dashboardData) return null
    return JSON.parse(dashboardData)
  } catch {
    return null
  }
}

export function setCurrentUser(user: Profile | null) {
  if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
  else localStorage.removeItem(USER_KEY)
}

export function setCurrentDashboard(dashboard: DashboardData | null) {
  if (dashboard) localStorage.setItem(DASHBOARD_KEY, JSON.stringify(dashboard))
  else localStorage.removeItem(DASHBOARD_KEY)
}

export async function login(email: string, password: string): Promise<Profile> {
  console.log('🔐 Auth: Starting login process')
  
  const credentials: LoginRequest = { email, password }
  const response = await authAPI.login(credentials)
  
  const user = response.user
  
  // Convert API User to Profile type for compatibility
  const profile: Profile = {
    id: user.id,
    email: user.email,
    first_name: user.first_name,
    last_name: user.last_name,
    role: user.role,
    loyalty_points: user.loyalty_points || 0,
    created_at: user.created_at,
    updated_at: user.updated_at,
    phone: user.phone,
    agency: user.agency,
    is_active: user.is_active
  }
  
  // Store user data and token in localStorage
  setCurrentUser(profile)
  if (response.token) {
    localStorage.setItem('auth_token', response.token)
  }
  
  // Store dashboard data if present
  if (response.dashboard) {
    setCurrentDashboard(response.dashboard)
    console.log('📊 Auth: Dashboard data stored:', response.dashboard.agency_name)
  }
  
  console.log('✅ Auth: Login successful, profile created and stored:', profile)
  console.log('🎯 Auth: User role:', profile.role)
  console.log('🏢 Auth: User agency:', profile.agency?.name || 'No agency')
  
  return profile
}

export async function register(data: { 
  first_name: string; 
  last_name: string; 
  email: string; 
  password: string; 
  phone?: string 
}): Promise<Profile> {
  console.log('🔐 Auth: Starting registration process')
  
  const registerData: RegisterRequest = {
    first_name: data.first_name,
    last_name: data.last_name,
    email: data.email,
    password: data.password,
    password_confirmation: data.password,
    phone: data.phone || ''
  }
  
  const response = await authAPI.register(registerData)
  const user = response.user
  
  // Convert API User to Profile type for compatibility
  const profile: Profile = {
    id: user.id,
    email: user.email,
    first_name: user.first_name,
    last_name: user.last_name,
    role: user.role,
    loyalty_points: user.loyalty_points || 0,
    created_at: user.created_at,
    updated_at: user.updated_at,
    phone: user.phone,
    agency: user.agency,
    is_active: user.is_active
  }
  
  console.log('✅ Auth: Registration successful, profile created:', profile)
  return profile
}

export async function logout() { 
  console.log('🔓 Auth: Starting logout process')
  try {
    await authAPI.logout()
  } catch (error) {
    console.error('🔴 Auth: API logout failed:', error)
  }
  
  // Clear local storage regardless of API call success
  setCurrentUser(null)
  setCurrentDashboard(null)
  localStorage.removeItem('auth_token')
  
  console.log('✅ Auth: Logout completed - user data, dashboard, and token cleared')
}

export function listBookings(): Booking[] {
  try { return JSON.parse(localStorage.getItem(BOOKINGS_KEY) || '[]') } catch { return [] }
}

export function addBooking(b: Booking) {
  const list = listBookings()
  list.unshift(b)
  localStorage.setItem(BOOKINGS_KEY, JSON.stringify(list))
}

export function updateBooking(id: number, updater: (b: Booking) => Booking) {
  const list = listBookings()
  const updated = list.map(b => (b.id === id ? updater(b) : b))
  localStorage.setItem(BOOKINGS_KEY, JSON.stringify(updated))
}

export function getBooking(id: number): Booking | null {
  return listBookings().find(b => b.id === id) || null
}


