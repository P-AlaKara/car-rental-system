import type { Profile, Booking, DashboardData } from './types'
import { authAPI, type User, type LoginRequest, type RegisterRequest } from './api'

const USER_KEY = 'am_user'
const DASHBOARD_KEY = 'am_dashboard'
const BOOKINGS_KEY = 'am_bookings'
const SESSION_START_KEY = 'am_session_start'
const TOKEN_EXPIRY_KEY = 'am_token_expiry'

export function getCurrentUser(): Profile | null {
  try { 
    const userData = localStorage.getItem(USER_KEY)
    const token = localStorage.getItem('am_token')
    
    if (!userData || !token) return null
    
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
    localStorage.setItem('am_token', response.token) // Use consistent token key
    
    // Set session start time and token expiry (24 hours from now)
    const now = new Date()
    const sessionStart = now.getTime()
    const tokenExpiry = now.getTime() + (24 * 60 * 60 * 1000) // 24 hours
    
    localStorage.setItem(SESSION_START_KEY, sessionStart.toString())
    localStorage.setItem(TOKEN_EXPIRY_KEY, tokenExpiry.toString())
    
    console.log('⏰ Auth: Session started at:', new Date(sessionStart).toLocaleString())
    console.log('⏰ Auth: Token expires at:', new Date(tokenExpiry).toLocaleString())
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
  localStorage.removeItem('am_token') // Use consistent token key
  localStorage.removeItem(SESSION_START_KEY)
  localStorage.removeItem(TOKEN_EXPIRY_KEY)
  
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

// Token validation and management
export function isAuthenticated(): boolean {
  const token = localStorage.getItem('am_token')
  const user = localStorage.getItem(USER_KEY)
  const tokenExpiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
  
  if (!token || !user) {
    return false
  }
  
  // Check if token has expired
  if (tokenExpiry) {
    const expiryTime = parseInt(tokenExpiry)
    const now = new Date().getTime()
    
    if (now > expiryTime) {
      console.log('🔴 Auth: Token expired, clearing session')
      // Clear expired session
      localStorage.removeItem('am_token')
      localStorage.removeItem(USER_KEY)
      localStorage.removeItem(DASHBOARD_KEY)
      localStorage.removeItem(SESSION_START_KEY)
      localStorage.removeItem(TOKEN_EXPIRY_KEY)
      return false
    }
  }
  
  return true
}

export function getToken(): string | null {
  return localStorage.getItem('am_token')
}

// Session management utilities
export function getSessionInfo() {
  const sessionStart = localStorage.getItem(SESSION_START_KEY)
  const tokenExpiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
  
  if (!sessionStart || !tokenExpiry) {
    return null
  }
  
  const startTime = parseInt(sessionStart)
  const expiryTime = parseInt(tokenExpiry)
  const now = new Date().getTime()
  
  return {
    sessionStart: new Date(startTime),
    tokenExpiry: new Date(expiryTime),
    timeRemaining: expiryTime - now,
    isExpired: now > expiryTime,
    sessionDuration: now - startTime
  }
}

export function getSessionTimeRemaining(): number {
  const tokenExpiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
  if (!tokenExpiry) return 0
  
  const expiryTime = parseInt(tokenExpiry)
  const now = new Date().getTime()
  return Math.max(0, expiryTime - now)
}

export function formatTimeRemaining(milliseconds: number): string {
  const hours = Math.floor(milliseconds / (1000 * 60 * 60))
  const minutes = Math.floor((milliseconds % (1000 * 60 * 60)) / (1000 * 60))
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

export async function validateAndRefreshToken(): Promise<boolean> {
  try {
    const token = getToken()
    if (!token) {
      console.log('🔴 Auth: No token found')
      return false
    }

    // Check if token is close to expiry (within 1 hour)
    const tokenExpiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
    if (tokenExpiry) {
      const expiryTime = parseInt(tokenExpiry)
      const now = new Date().getTime()
      const oneHour = 60 * 60 * 1000
      
      // Only refresh if token expires within the next hour
      if (now < expiryTime - oneHour) {
        console.log('✅ Auth: Token still valid, no refresh needed')
        return true
      }
    }

    // Try to refresh the token
    const response = await authAPI.refreshToken()
    if (response.data.token) {
      localStorage.setItem('am_token', response.data.token)
      
      // Update token expiry (extend by 24 hours)
      const now = new Date()
      const newExpiry = now.getTime() + (24 * 60 * 60 * 1000) // 24 hours
      localStorage.setItem(TOKEN_EXPIRY_KEY, newExpiry.toString())
      
      console.log('✅ Auth: Token refreshed successfully')
      console.log('⏰ Auth: New token expires at:', new Date(newExpiry).toLocaleString())
      return true
    }
    
    return false
  } catch (error) {
    console.error('🔴 Auth: Token validation failed:', error)
    // Clear invalid token
    localStorage.removeItem('am_token')
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem(DASHBOARD_KEY)
    localStorage.removeItem(SESSION_START_KEY)
    localStorage.removeItem(TOKEN_EXPIRY_KEY)
    return false
  }
}

// Auto-refresh token before it expires
export function setupTokenRefresh() {
  console.log('🔄 Auth: Setting up token refresh system')
  
  // Check token every 10 minutes
  setInterval(async () => {
    if (isAuthenticated()) {
      await validateAndRefreshToken()
    }
  }, 10 * 60 * 1000) // 10 minutes
  
  // Also check on page visibility change (when user returns to tab)
  document.addEventListener('visibilitychange', async () => {
    if (!document.hidden && isAuthenticated()) {
      console.log('👁️ Auth: Page became visible, checking token')
      await validateAndRefreshToken()
    }
  })
  
  // Check on window focus (when user switches back to browser)
  window.addEventListener('focus', async () => {
    if (isAuthenticated()) {
      console.log('🎯 Auth: Window focused, checking token')
      await validateAndRefreshToken()
    }
  })
}


