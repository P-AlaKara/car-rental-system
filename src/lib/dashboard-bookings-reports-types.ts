// Dashboard, Bookings, and Reports API Types and Functions
// Extends the existing API structure in src/lib/api.ts

// ==================== DASHBOARD API TYPES ====================

export interface DashboardStats {
  // Fleet Statistics
  total_cars: number
  available_cars: number
  booked_cars: number
  in_use_cars: number
  under_maintenance_cars: number
  cars_due_service: number
  
  // Booking Statistics
  total_bookings: number
  active_bookings: number
  pending_bookings: number
  confirmed_bookings: number
  completed_bookings: number
  cancelled_bookings: number
  
  // Financial Statistics
  monthly_revenue: number
  total_revenue: number
  pending_payments: number
  pending_amount: number
  avg_booking_value: number
  avg_daily_rate: number
  
  // User Statistics
  total_users: number
  active_users: number
  new_users_month: number
  
  // Operational Statistics
  fleet_utilization_rate: number
  conversion_rate: number
  avg_rental_duration: number
  service_threshold_km: number
  
  // Agency-specific (for admin users)
  agency_stats?: {
    agency_name: string
    agency_cars: number
    agency_revenue: number
    agency_bookings: number
  }
}

export interface RevenueTrendData {
  date: string
  revenue: number
  bookings: number
  avg_value: number
}

export interface BookingDistribution {
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'
  count: number
  percentage: number
  color: string
}

export interface FleetUtilization {
  overall: {
    total_vehicles: number
    in_use: number
    available: number
    maintenance: number
  }
  by_category: Array<{
    category: string
    total: number
    in_use: number
    available: number
    maintenance: number
    utilization_rate: number
  }>
  by_agency: Array<{
    agency_name: string
    total: number
    in_use: number
    available: number
    utilization_rate: number
  }>
}

export interface RecentActivity {
  id: number
  type: 'booking_created' | 'booking_confirmed' | 'booking_cancelled' | 'car_rented' | 'car_returned' | 'payment_received'
  title: string
  description: string
  user: {
    id: number
    name: string
    email: string
  }
  car?: {
    id: number
    make: string
    model: string
    year: number
    license_plate: string
  }
  booking?: {
    id: number
    start_date: string
    end_date: string
    total_cost: number
    status: string
  }
  timestamp: string
  time_ago: string
}

export interface PendingActions {
  pending_bookings: Array<{
    id: number
    user_name: string
    car_details: string
    created_at: string
    total_cost: number
  }>
  pending_payments: Array<{
    booking_id: number
    user_name: string
    amount: number
    due_date: string
    days_overdue: number
  }>
  cars_due_service: Array<{
    id: number
    make: string
    model: string
    license_plate: string
    current_odometer: number
    last_service_odometer: number
    service_threshold_km: number
    overdue_km: number
  }>
}

// ==================== BOOKINGS API TYPES ====================

export interface BookingFilters {
  page?: number
  size?: number
  search?: string
  status?: 'all' | 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'
  sort_by?: 'created_at' | 'start_date' | 'total_cost' | 'customer_name'
  sort_order?: 'asc' | 'desc'
  start_date?: string
  end_date?: string
  customer_id?: number
  car_id?: number
  agency_id?: number
  date_range?: string
}

export interface BookingListItem {
  id: number
  booking_reference: string
  user: {
    id: number
    first_name: string
    last_name: string
    email: string
    phone: string
  }
  car: {
    id: number
    make: string
    model: string
    year: number
    license_plate: string
    category: string
    agency: string
  }
  start_date: string
  end_date: string
  pickup_location: string
  return_location: string
  duration_days: number
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'
  total_cost: number
  payment_status: 'pending' | 'partial' | 'paid' | 'refunded'
  created_at: string
  updated_at: string
  notes?: string
  driver_details?: {
    license_number: string
    license_expiry: string
    additional_drivers: number
  }
}

export interface BookingDetails extends BookingListItem {
  breakdown: {
    base_cost: number
    insurance_cost: number
    additional_fees: number
    taxes: number
    discounts: number
  }
  payment_history: Array<{
    id: number
    amount: number
    payment_method: string
    transaction_id: string
    status: string
    created_at: string
  }>
  special_requests?: string
  cancellation_reason?: string
  refund_amount?: number
}

export interface BookingStatusUpdate {
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'
  notes?: string
  cancellation_reason?: string
  admin_comments?: string
}

export interface CreateBookingRequest {
  user_id: number
  car_id: number
  start_date: string
  end_date: string
  pickup_location: string
  return_location: string
  driver_details: {
    license_number: string
    license_expiry: string
    additional_drivers: number
  }
  special_requests?: string
  insurance_option?: 'basic' | 'comprehensive' | 'premium'
  payment_method?: string
}

export interface BookingAnalytics {
  period_summary: {
    total_bookings: number
    total_revenue: number
    avg_booking_value: number
    completion_rate: number
    cancellation_rate: number
  }
  trend_data: Array<{
    date: string
    bookings: number
    revenue: number
    avg_value: number
  }>
  status_breakdown: Array<{
    status: string
    count: number
    percentage: number
  }>
  popular_cars: Array<{
    car_id: number
    make: string
    model: string
    booking_count: number
    revenue: number
  }>
  peak_periods: Array<{
    period: string
    booking_count: number
    avg_duration: number
  }>
}

// ==================== REPORTS API TYPES ====================

export interface OverviewReport {
  summary: {
    total_revenue: number
    total_bookings: number
    avg_booking_value: number
    fleet_utilization: number
    completion_rate: number
    revenue_growth: number
    booking_growth: number
  }
  revenue_trend: Array<{
    period: string
    revenue: number
    bookings: number
    avg_value: number
  }>
  booking_distribution: Array<{
    status: string
    count: number
    percentage: number
    color: string
  }>
  top_metrics: {
    most_popular_car: {
      id: number
      make: string
      model: string
      booking_count: number
    }
    highest_revenue_car: {
      id: number
      make: string
      model: string
      revenue: number
    }
    top_customer: {
      id: number
      name: string
      total_spent: number
      booking_count: number
    }
    peak_booking_day: {
      date: string
      booking_count: number
    }
  }
}

export interface RevenueReport {
  current_period: {
    total_revenue: number
    paid_revenue: number
    pending_revenue: number
    refunded_revenue: number
    net_revenue: number
  }
  comparison: {
    previous_period_revenue: number
    growth_amount: number
    growth_percentage: number
    trend: 'up' | 'down' | 'stable'
  }
  breakdown: Array<{
    period: string
    gross_revenue: number
    net_revenue: number
    booking_count: number
    avg_booking_value: number
  }>
  revenue_sources: Array<{
    source: 'base_rental' | 'insurance' | 'additional_fees' | 'late_fees'
    amount: number
    percentage: number
  }>
  payment_methods: Array<{
    method: string
    count: number
    amount: number
    percentage: number
  }>
  top_revenue_cars: Array<{
    car_id: number
    make: string
    model: string
    total_revenue: number
    booking_count: number
    avg_daily_rate: number
  }>
}

export interface FleetReport {
  fleet_overview: {
    total_vehicles: number
    active_vehicles: number
    utilization_rate: number
    avg_daily_rate: number
    maintenance_cost: number
  }
  utilization_by_category: Array<{
    category: string
    total_cars: number
    avg_utilization: number
    total_revenue: number
    most_popular_car: string
  }>
  performance_metrics: Array<{
    car_id: number
    make: string
    model: string
    license_plate: string
    utilization_rate: number
    total_bookings: number
    total_revenue: number
    avg_daily_rate: number
    days_booked: number
    days_available: number
    maintenance_days: number
    customer_rating?: number
  }>
  maintenance_summary: {
    cars_due_service: number
    overdue_service: number
    total_maintenance_cost: number
    avg_service_interval: number
  }
  category_analysis: Array<{
    category: string
    demand_score: number
    revenue_per_car: number
    utilization_rate: number
    recommended_fleet_size: number
  }>
}

export interface CustomerReport {
  customer_summary: {
    total_customers: number
    active_customers: number
    new_customers: number
    returning_customers: number
    customer_lifetime_value: number
  }
  top_customers: Array<{
    id: number
    name: string
    email: string
    total_bookings: number
    total_spent: number
    avg_booking_value: number
    loyalty_points: number
    last_booking: string
    customer_since: string
  }>
  customer_segments: Array<{
    segment: string
    customer_count: number
    avg_booking_value: number
    total_revenue: number
    retention_rate: number
  }>
  booking_patterns: {
    avg_booking_frequency: number
    popular_booking_days: Array<{
      day: string
      booking_count: number
    }>
    seasonal_trends: Array<{
      month: string
      booking_count: number
      avg_duration: number
    }>
  }
  geographic_distribution: Array<{
    location: string
    customer_count: number
    avg_booking_value: number
  }>
}

export interface FinancialReport {
  revenue_summary: {
    gross_revenue: number
    net_revenue: number
    total_refunds: number
    pending_payments: number
    collection_rate: number
  }
  expense_breakdown: {
    maintenance_costs: number
    insurance_costs: number
    operational_costs: number
    staff_costs: number
    total_expenses: number
  }
  profitability: {
    gross_profit: number
    net_profit: number
    profit_margin: number
    roi: number
  }
  cash_flow: Array<{
    month: string
    revenue: number
    expenses: number
    net_cash_flow: number
    cumulative_cash_flow: number
  }>
  aging_report: {
    current: number
    overdue_30: number
    overdue_60: number
    overdue_90: number
    bad_debt: number
  }
  projections?: {
    next_month_revenue: number
    next_quarter_revenue: number
    projected_expenses: number
    expected_profit: number
  }
}

export interface CustomReportRequest {
  report_name: string
  date_range: {
    start_date: string
    end_date: string
  }
  metrics: Array<'revenue' | 'bookings' | 'utilization' | 'customers' | 'fleet_performance'>
  filters: {
    agency_id?: number
    car_category?: string
    customer_segment?: string
    booking_status?: string
  }
  grouping: 'day' | 'week' | 'month' | 'quarter'
  format: 'json' | 'csv' | 'excel' | 'pdf'
}

// ==================== COMMON RESPONSE TYPES ====================

export interface PaginationMeta {
  current_page: number
  last_page: number
  per_page: number
  total: number
  from: number
  to: number
  links: {
    first: string
    last: string
    prev: string | null
    next: string | null
  }
}

export interface BookingListResponse {
  status: string
  message: string
  data: {
    bookings: BookingListItem[]
    meta: PaginationMeta
    summary: {
      total_bookings: number
      total_revenue: number
      status_counts: {
        pending: number
        confirmed: number
        in_progress: number
        completed: number
        cancelled: number
      }
    }
  }
}
