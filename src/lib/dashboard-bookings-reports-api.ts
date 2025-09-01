// Dashboard, Bookings, and Reports API Implementation
// This extends the existing API structure from src/lib/api.ts

import type { ApiResponse } from './api'
import type {
  DashboardStats,
  RevenueTrendData,
  BookingDistribution,
  FleetUtilization,
  RecentActivity,
  PendingActions,
  BookingFilters,
  BookingListResponse,
  BookingDetails,
  BookingStatusUpdate,
  CreateBookingRequest,
  BookingAnalytics,
  OverviewReport,
  RevenueReport,
  FleetReport,
  CustomerReport,
  FinancialReport,
  CustomReportRequest
} from './dashboard-bookings-reports-types'

// Import the apiRequest function and base configuration from existing api.ts
// Note: This assumes the existing api.ts exports these functions
import { getStoredToken } from './api'
import { API_BASE_URL as ENV_API_BASE_URL } from '../config'

const API_BASE_URL = (ENV_API_BASE_URL && ENV_API_BASE_URL.trim().length > 0)
  ? ENV_API_BASE_URL
  : 'http://localhost:4000/api/v1'

// Generic API request function (duplicated from api.ts for standalone usage)
async function apiRequest<T>(
  endpoint: string, 
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const token = getStoredToken()
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'ngrok-skip-browser-warning': 'true',
  }
  
  if (token) {
    defaultHeaders.Authorization = `Bearer ${token}`
  }
  
  const config: RequestInit = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  }

  const url = `${API_BASE_URL}${endpoint}`
  console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`)
  console.log('📤 Request Config:', config)
  
  try {
    const response = await fetch(url, config)
    const data = await response.json()

    console.log(`📥 API Response (${response.status}):`, data)
    
    if (!response.ok) {
      throw new Error(data.message || `HTTP error! status: ${response.status}`)
    }
    
    return data
  } catch (error) {
    console.error('❌ API request failed:', error)
    throw error
  }
}

// ==================== DASHBOARD API FUNCTIONS ====================

export const dashboardAPI = {
  // Get comprehensive dashboard statistics
  async getStats(): Promise<ApiResponse<DashboardStats>> {
    console.log('📊 Fetching dashboard statistics')
    
    return await apiRequest<DashboardStats>('/dashboard/stats', {
      method: 'GET'
    })
  },

  // Get revenue trend data
  async getRevenueTrend(period: '7d' | '30d' | '3m' | '12m' = '7d'): Promise<ApiResponse<RevenueTrendData[]>> {
    console.log(`📈 Fetching revenue trend for period: ${period}`)
    
    return await apiRequest<RevenueTrendData[]>(`/dashboard/revenue-trend?period=${period}`, {
      method: 'GET'
    })
  },

  // Get booking status distribution
  async getBookingDistribution(): Promise<ApiResponse<BookingDistribution[]>> {
    console.log('📊 Fetching booking status distribution')
    
    return await apiRequest<BookingDistribution[]>('/dashboard/booking-distribution', {
      method: 'GET'
    })
  },

  // Get fleet utilization data
  async getFleetUtilization(): Promise<ApiResponse<FleetUtilization>> {
    console.log('🚗 Fetching fleet utilization data')
    
    return await apiRequest<FleetUtilization>('/dashboard/fleet-utilization', {
      method: 'GET'
    })
  },

  // Get recent activities
  async getRecentActivities(limit: number = 10): Promise<ApiResponse<RecentActivity[]>> {
    console.log(`📋 Fetching recent activities (limit: ${limit})`)
    
    return await apiRequest<RecentActivity[]>(`/dashboard/recent-activities?limit=${limit}`, {
      method: 'GET'
    })
  },

  // Get pending actions
  async getPendingActions(): Promise<ApiResponse<PendingActions>> {
    console.log('⚠️ Fetching pending actions')
    
    return await apiRequest<PendingActions>('/dashboard/pending-actions', {
      method: 'GET'
    })
  }
}

// ==================== BOOKINGS API FUNCTIONS ====================

export const bookingsAPI = {
  // Get all bookings with filters
  async getBookings(filters: BookingFilters = {}): Promise<BookingListResponse> {
    const queryParams = new URLSearchParams()
    
    if (filters.page !== undefined) queryParams.append('page', filters.page.toString())
    if (filters.size !== undefined) queryParams.append('size', filters.size.toString())
    if (filters.search) queryParams.append('search', filters.search)
    if (filters.status && filters.status !== 'all') queryParams.append('status', filters.status)
    if (filters.sort_by) queryParams.append('sort_by', filters.sort_by)
    if (filters.sort_order) queryParams.append('sort_order', filters.sort_order)
    if (filters.start_date) queryParams.append('start_date', filters.start_date)
    if (filters.end_date) queryParams.append('end_date', filters.end_date)
    if (filters.customer_id !== undefined) queryParams.append('customer_id', filters.customer_id.toString())
    if (filters.car_id !== undefined) queryParams.append('car_id', filters.car_id.toString())
    if (filters.agency_id !== undefined) queryParams.append('agency_id', filters.agency_id.toString())
    if (filters.date_range) queryParams.append('date_range', filters.date_range)

    const endpoint = `/bookings${queryParams.toString() ? `?${queryParams.toString()}` : ''}`
    
    console.log('📅 Fetching bookings with filters:', filters)
    
    return await apiRequest<BookingListResponse['data']>(endpoint, {
      method: 'GET'
    }).then(response => ({
      ...response,
      data: response.data
    }))
  },

  // Get booking details
  async getBookingDetails(bookingId: number): Promise<ApiResponse<BookingDetails>> {
    console.log(`📄 Fetching booking details for ID: ${bookingId}`)
    
    return await apiRequest<BookingDetails>(`/bookings/${bookingId}`, {
      method: 'GET'
    })
  },

  // Update booking status
  async updateBookingStatus(bookingId: number, statusUpdate: BookingStatusUpdate): Promise<ApiResponse<any>> {
    console.log(`🔄 Updating booking ${bookingId} status to: ${statusUpdate.status}`)
    
    return await apiRequest<any>(`/bookings/${bookingId}/status`, {
      method: 'PUT',
      body: JSON.stringify(statusUpdate)
    })
  },

  // Create new booking
  async createBooking(bookingData: CreateBookingRequest): Promise<ApiResponse<BookingDetails>> {
    console.log('➕ Creating new booking:', { 
      user_id: bookingData.user_id, 
      car_id: bookingData.car_id,
      start_date: bookingData.start_date,
      end_date: bookingData.end_date
    })
    
    return await apiRequest<BookingDetails>('/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingData)
    })
  },

  // Get booking analytics
  async getAnalytics(period: 'week' | 'month' | 'quarter' | 'year' = 'month', agencyId?: number): Promise<ApiResponse<BookingAnalytics>> {
    const queryParams = new URLSearchParams()
    queryParams.append('period', period)
    if (agencyId !== undefined) queryParams.append('agency_id', agencyId.toString())

    console.log(`📊 Fetching booking analytics for period: ${period}`)
    
    return await apiRequest<BookingAnalytics>(`/bookings/analytics?${queryParams.toString()}`, {
      method: 'GET'
    })
  },

  // Export bookings
  async exportBookings(
    format: 'csv' | 'excel' | 'pdf',
    filters: BookingFilters = {},
    fields?: string[]
  ): Promise<Blob> {
    const queryParams = new URLSearchParams()
    queryParams.append('format', format)
    
    // Add all filters
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString())
      }
    })
    
    if (fields && fields.length > 0) {
      queryParams.append('fields', fields.join(','))
    }

    console.log(`📥 Exporting bookings as ${format}`)
    
    const token = getStoredToken()
    const headers: HeadersInit = {
      'ngrok-skip-browser-warning': 'true'
    }
    
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE_URL}/bookings/export?${queryParams.toString()}`, {
      method: 'GET',
      headers
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to export bookings')
    }

    return response.blob()
  }
}

// ==================== REPORTS API FUNCTIONS ====================

export const reportsAPI = {
  // Get overview report
  async getOverviewReport(
    period: '7d' | '30d' | '3m' | '6m' | '12m' = '30d',
    agencyId?: number
  ): Promise<ApiResponse<OverviewReport>> {
    const queryParams = new URLSearchParams()
    queryParams.append('period', period)
    if (agencyId !== undefined) queryParams.append('agency_id', agencyId.toString())

    console.log(`📋 Fetching overview report for period: ${period}`)
    
    return await apiRequest<OverviewReport>(`/reports/overview?${queryParams.toString()}`, {
      method: 'GET'
    })
  },

  // Get revenue analysis report
  async getRevenueReport(
    period: 'month' | 'quarter' | 'year' = 'month',
    compareWith: 'previous_period' | 'previous_year' = 'previous_period',
    breakdownBy: 'day' | 'week' | 'month' = 'day',
    agencyId?: number
  ): Promise<ApiResponse<RevenueReport>> {
    const queryParams = new URLSearchParams()
    queryParams.append('period', period)
    queryParams.append('compare_with', compareWith)
    queryParams.append('breakdown_by', breakdownBy)
    if (agencyId !== undefined) queryParams.append('agency_id', agencyId.toString())

    console.log(`💰 Fetching revenue report for period: ${period}`)
    
    return await apiRequest<RevenueReport>(`/reports/revenue?${queryParams.toString()}`, {
      method: 'GET'
    })
  },

  // Get fleet performance report
  async getFleetReport(
    period: 'month' | 'quarter' | 'year' = 'month',
    includeMaintenance: boolean = true,
    agencyId?: number
  ): Promise<ApiResponse<FleetReport>> {
    const queryParams = new URLSearchParams()
    queryParams.append('period', period)
    queryParams.append('include_maintenance', includeMaintenance.toString())
    if (agencyId !== undefined) queryParams.append('agency_id', agencyId.toString())

    console.log(`🚗 Fetching fleet performance report for period: ${period}`)
    
    return await apiRequest<FleetReport>(`/reports/fleet?${queryParams.toString()}`, {
      method: 'GET'
    })
  },

  // Get customer analytics report
  async getCustomerReport(
    period: 'month' | 'quarter' | 'year' = 'month',
    segmentBy: 'loyalty_tier' | 'booking_frequency' | 'spending_level' = 'spending_level'
  ): Promise<ApiResponse<CustomerReport>> {
    const queryParams = new URLSearchParams()
    queryParams.append('period', period)
    queryParams.append('segment_by', segmentBy)

    console.log(`👥 Fetching customer analytics report for period: ${period}`)
    
    return await apiRequest<CustomerReport>(`/reports/customers?${queryParams.toString()}`, {
      method: 'GET'
    })
  },

  // Get financial summary report
  async getFinancialReport(
    period: 'month' | 'quarter' | 'year' = 'month',
    includeProjections: boolean = false
  ): Promise<ApiResponse<FinancialReport>> {
    const queryParams = new URLSearchParams()
    queryParams.append('period', period)
    queryParams.append('include_projections', includeProjections.toString())

    console.log(`💼 Fetching financial report for period: ${period}`)
    
    return await apiRequest<FinancialReport>(`/reports/financial?${queryParams.toString()}`, {
      method: 'GET'
    })
  },

  // Create custom report
  async createCustomReport(reportConfig: CustomReportRequest): Promise<ApiResponse<any>> {
    console.log('🛠️ Creating custom report:', reportConfig.report_name)
    
    return await apiRequest<any>('/reports/custom', {
      method: 'POST',
      body: JSON.stringify(reportConfig)
    })
  },

  // Export report
  async exportReport(
    reportType: 'overview' | 'revenue' | 'fleet' | 'customers' | 'financial',
    format: 'pdf' | 'excel' | 'csv',
    period: string = 'month',
    agencyId?: number
  ): Promise<Blob> {
    const queryParams = new URLSearchParams()
    queryParams.append('format', format)
    queryParams.append('period', period)
    if (agencyId !== undefined) queryParams.append('agency_id', agencyId.toString())

    console.log(`📥 Exporting ${reportType} report as ${format}`)
    
    const token = getStoredToken()
    const headers: HeadersInit = {
      'ngrok-skip-browser-warning': 'true'
    }
    
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE_URL}/reports/export/${reportType}?${queryParams.toString()}`, {
      method: 'GET',
      headers
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.message || 'Failed to export report')
    }

    return response.blob()
  }
}

// ==================== CONVENIENCE EXPORTS ====================

// Dashboard exports
export const getDashboardStats = dashboardAPI.getStats
export const getRevenueTrend = dashboardAPI.getRevenueTrend
export const getBookingDistribution = dashboardAPI.getBookingDistribution
export const getFleetUtilization = dashboardAPI.getFleetUtilization
export const getRecentActivities = dashboardAPI.getRecentActivities
export const getPendingActions = dashboardAPI.getPendingActions

// Bookings exports
export const getBookings = bookingsAPI.getBookings
export const getBookingDetails = bookingsAPI.getBookingDetails
export const updateBookingStatus = bookingsAPI.updateBookingStatus
export const createBooking = bookingsAPI.createBooking
export const getBookingAnalytics = bookingsAPI.getAnalytics
export const exportBookings = bookingsAPI.exportBookings

// Reports exports
export const getOverviewReport = reportsAPI.getOverviewReport
export const getRevenueReport = reportsAPI.getRevenueReport
export const getFleetReport = reportsAPI.getFleetReport
export const getCustomerReport = reportsAPI.getCustomerReport
export const getFinancialReport = reportsAPI.getFinancialReport
export const createCustomReport = reportsAPI.createCustomReport
export const exportReport = reportsAPI.exportReport

// Helper function to download blob as file
export const downloadBlob = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.style.display = 'none'
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}

export default {
  dashboardAPI,
  bookingsAPI,
  reportsAPI
}
