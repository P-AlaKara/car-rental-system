# API Endpoints Structure - Dashboard, Bookings & Reports

## Base Configuration

```typescript
const API_BASE_URL = "https://4043f016f021.ngrok-free.app/api/v1";
```

## Common Headers

```typescript
{
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'ngrok-skip-browser-warning': 'true',
  'Authorization': 'Bearer ${token}' // When authenticated
}
```

---

## 📊 DASHBOARD PAGE ENDPOINTS

### 1. Dashboard Statistics

**GET** `/dashboard/stats`

**Purpose:** Get comprehensive dashboard statistics

**Response:**

```typescript
interface DashboardStatsResponse {
  status: string;
  message: string;
  data: {
    // Fleet Statistics
    total_cars: number;
    available_cars: number;
    booked_cars: number;
    in_use_cars: number;
    under_maintenance_cars: number;
    cars_due_service: number;

    // Booking Statistics
    total_bookings: number;
    active_bookings: number;
    pending_bookings: number;
    confirmed_bookings: number;
    completed_bookings: number;
    cancelled_bookings: number;

    // Financial Statistics
    monthly_revenue: number;
    total_revenue: number;
    pending_payments: number;
    pending_amount: number;
    avg_booking_value: number;
    avg_daily_rate: number;

    // User Statistics
    total_users: number;
    active_users: number;
    new_users_month: number;

    // Operational Statistics
    fleet_utilization_rate: number;
    conversion_rate: number;
    avg_rental_duration: number;
    service_threshold_km: number;

    // Agency-specific (for admin users)
    agency_stats?: {
      agency_name: string;
      agency_cars: number;
      agency_revenue: number;
      agency_bookings: number;
    };
  };
}
```

### 2. Revenue Trend Data

**GET** `/dashboard/revenue-trend`

**Query Parameters:**

- `period`: `7d` | `30d` | `3m` | `12m` (default: `7d`)

**Response:**

```typescript
interface RevenueTrendResponse {
  status: string;
  message: string;
  data: Array<{
    date: string; // YYYY-MM-DD or day name
    revenue: number;
    bookings: number;
    avg_value: number;
  }>;
}
```

### 3. Booking Status Distribution

**GET** `/dashboard/booking-distribution`

**Response:**

```typescript
interface BookingDistributionResponse {
  status: string;
  message: string;
  data: Array<{
    status: "pending" | "confirmed" | "in_progress" | "completed" | "cancelled";
    count: number;
    percentage: number;
    color: string;
  }>;
}
```

### 4. Fleet Utilization

**GET** `/dashboard/fleet-utilization`

**Response:**

```typescript
interface FleetUtilizationResponse {
  status: string;
  message: string;
  data: {
    overall: {
      total_vehicles: number;
      in_use: number;
      available: number;
      maintenance: number;
    };
    by_category: Array<{
      category: string;
      total: number;
      in_use: number;
      available: number;
      maintenance: number;
      utilization_rate: number;
    }>;
    by_agency: Array<{
      agency_name: string;
      total: number;
      in_use: number;
      available: number;
      utilization_rate: number;
    }>;
  };
}
```

### 5. Recent Activities

**GET** `/dashboard/recent-activities`

**Query Parameters:**

- `limit`: number (default: 10)

**Response:**

```typescript
interface RecentActivitiesResponse {
  status: string;
  message: string;
  data: Array<{
    id: number;
    type:
      | "booking_created"
      | "booking_confirmed"
      | "booking_cancelled"
      | "car_rented"
      | "car_returned"
      | "payment_received";
    title: string;
    description: string;
    user: {
      id: number;
      name: string;
      email: string;
    };
    car?: {
      id: number;
      make: string;
      model: string;
      year: number;
      license_plate: string;
    };
    booking?: {
      id: number;
      start_date: string;
      end_date: string;
      total_cost: number;
      status: string;
    };
    timestamp: string;
    time_ago: string;
  }>;
}
```

### 6. Pending Actions

**GET** `/dashboard/pending-actions`

**Response:**

```typescript
interface PendingActionsResponse {
  status: string;
  message: string;
  data: {
    pending_bookings: Array<{
      id: number;
      user_name: string;
      car_details: string;
      created_at: string;
      total_cost: number;
    }>;
    pending_payments: Array<{
      booking_id: number;
      user_name: string;
      amount: number;
      due_date: string;
      days_overdue: number;
    }>;
    cars_due_service: Array<{
      id: number;
      make: string;
      model: string;
      license_plate: string;
      current_odometer: number;
      last_service_odometer: number;
      service_threshold_km: number;
      overdue_km: number;
    }>;
  };
}
```

---

## 📅 BOOKINGS PAGE ENDPOINTS

### 1. Get All Bookings (with Filters)

**GET** `/bookings`

**Query Parameters:**

```typescript
interface BookingFilters {
  page?: number; // Pagination page (default: 1)
  size?: number; // Items per page (default: 20)
  search?: string; // Search in customer name, car, booking ID
  status?:
    | "all"
    | "pending"
    | "confirmed"
    | "in_progress"
    | "completed"
    | "cancelled";
  sort_by?: "created_at" | "start_date" | "total_cost" | "customer_name";
  sort_order?: "asc" | "desc";
  start_date?: string; // Filter by booking start date (YYYY-MM-DD)
  end_date?: string; // Filter by booking end date (YYYY-MM-DD)
  customer_id?: number; // Filter by specific customer
  car_id?: number; // Filter by specific car
  agency_id?: number; // Filter by agency (admin users)
  date_range?: string; // Predefined ranges: 'today', 'week', 'month', 'year'
}
```

**Response:**

```typescript
interface BookingsListResponse {
  status: string;
  message: string;
  data: {
    bookings: Array<{
      id: number;
      booking_reference: string;
      user: {
        id: number;
        first_name: string;
        last_name: string;
        email: string;
        phone: string;
      };
      car: {
        id: number;
        make: string;
        model: string;
        year: number;
        license_plate: string;
        category: string;
        agency: string;
      };
      start_date: string;
      end_date: string;
      pickup_location: string;
      return_location: string;
      duration_days: number;
      status:
        | "pending"
        | "confirmed"
        | "in_progress"
        | "completed"
        | "cancelled";
      total_cost: number;
      payment_status: "pending" | "partial" | "paid" | "refunded";
      created_at: string;
      updated_at: string;
      notes?: string;
      driver_details?: {
        license_number: string;
        license_expiry: string;
        additional_drivers: number;
      };
    }>;
    meta: {
      current_page: number;
      last_page: number;
      total: number;
      per_page: number;
      from: number;
      to: number;
    };
    summary: {
      total_bookings: number;
      total_revenue: number;
      status_counts: {
        pending: number;
        confirmed: number;
        in_progress: number;
        completed: number;
        cancelled: number;
      };
    };
  };
}
```

### 2. Get Booking Details

**GET** `/bookings/{booking_id}`

**Response:**

```typescript
interface BookingDetailsResponse {
  status: string;
  message: string;
  data: {
    id: number;
    booking_reference: string;
    user: {
      id: number;
      first_name: string;
      last_name: string;
      email: string;
      phone: string;
      loyalty_points: number;
    };
    car: {
      id: number;
      make: string;
      model: string;
      year: number;
      license_plate: string;
      category: string;
      transmission: string;
      fuel_type: string;
      seats: number;
      rental_rate_per_day: number;
      images: Array<{
        id: number;
        image_url: string;
      }>;
      agency: {
        id: number;
        name: string;
        location: string;
        contact: string;
      };
    };
    start_date: string;
    end_date: string;
    pickup_location: string;
    return_location: string;
    duration_days: number;
    status: string;
    total_cost: number;
    breakdown: {
      base_cost: number;
      insurance_cost: number;
      additional_fees: number;
      taxes: number;
      discounts: number;
    };
    payment_status: string;
    payment_history: Array<{
      id: number;
      amount: number;
      payment_method: string;
      transaction_id: string;
      status: string;
      created_at: string;
    }>;
    driver_details: {
      license_number: string;
      license_expiry: string;
      additional_drivers: number;
    };
    special_requests?: string;
    notes?: string;
    created_at: string;
    updated_at: string;
    cancellation_reason?: string;
    refund_amount?: number;
  };
}
```

### 3. Update Booking Status

**PUT** `/bookings/{booking_id}/status`

**Request Body:**

```typescript
{
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled'
  notes?: string
  cancellation_reason?: string // Required if status is 'cancelled'
  admin_comments?: string
}
```

**Response:**

```typescript
interface BookingStatusUpdateResponse {
  status: string;
  message: string;
  data: {
    booking: BookingDetails;
    status_history: Array<{
      id: number;
      previous_status: string;
      new_status: string;
      changed_by: string;
      reason?: string;
      created_at: string;
    }>;
  };
}
```

### 4. Create New Booking

**POST** `/bookings`

**Request Body:**

```typescript
{
  user_id: number
  car_id: number
  start_date: string // YYYY-MM-DD
  end_date: string   // YYYY-MM-DD
  pickup_location: string
  return_location: string
  driver_details: {
    license_number: string
    license_expiry: string // YYYY-MM-DD
    additional_drivers: number
  }
  special_requests?: string
  insurance_option?: 'basic' | 'comprehensive' | 'premium'
  payment_method?: string
}
```

### 5. Booking Analytics

**GET** `/bookings/analytics`

**Query Parameters:**

- `period`: `week` | `month` | `quarter` | `year`
- `agency_id`: number (optional, admin filter)

**Response:**

```typescript
interface BookingAnalyticsResponse {
  status: string;
  message: string;
  data: {
    period_summary: {
      total_bookings: number;
      total_revenue: number;
      avg_booking_value: number;
      completion_rate: number;
      cancellation_rate: number;
    };
    trend_data: Array<{
      date: string;
      bookings: number;
      revenue: number;
      avg_value: number;
    }>;
    status_breakdown: Array<{
      status: string;
      count: number;
      percentage: number;
    }>;
    popular_cars: Array<{
      car_id: number;
      make: string;
      model: string;
      booking_count: number;
      revenue: number;
    }>;
    peak_periods: Array<{
      period: string;
      booking_count: number;
      avg_duration: number;
    }>;
  };
}
```

### 6. Export Bookings

**GET** `/bookings/export`

**Query Parameters:**

- `format`: `csv` | `excel` | `pdf`
- `filters`: Same as booking list filters
- `fields`: Comma-separated list of fields to include

**Response:** File download

---

## 📈 REPORTS PAGE ENDPOINTS

### 1. Overview Report

**GET** `/reports/overview`

**Query Parameters:**

- `period`: `7d` | `30d` | `3m` | `6m` | `12m`
- `agency_id`: number (optional, for admin users)

**Response:**

```typescript
interface OverviewReportResponse {
  status: string;
  message: string;
  data: {
    summary: {
      total_revenue: number;
      total_bookings: number;
      avg_booking_value: number;
      fleet_utilization: number;
      completion_rate: number;
      revenue_growth: number;
      booking_growth: number;
    };
    revenue_trend: Array<{
      period: string;
      revenue: number;
      bookings: number;
      avg_value: number;
    }>;
    booking_distribution: Array<{
      status: string;
      count: number;
      percentage: number;
      color: string;
    }>;
    top_metrics: {
      most_popular_car: {
        id: number;
        make: string;
        model: string;
        booking_count: number;
      };
      highest_revenue_car: {
        id: number;
        make: string;
        model: string;
        revenue: number;
      };
      top_customer: {
        id: number;
        name: string;
        total_spent: number;
        booking_count: number;
      };
      peak_booking_day: {
        date: string;
        booking_count: number;
      };
    };
  };
}
```

### 2. Revenue Analysis Report

**GET** `/reports/revenue`

**Query Parameters:**

- `period`: `month` | `quarter` | `year`
- `compare_with`: `previous_period` | `previous_year`
- `breakdown_by`: `day` | `week` | `month`
- `agency_id`: number (optional)

**Response:**

```typescript
interface RevenueReportResponse {
  status: string;
  message: string;
  data: {
    current_period: {
      total_revenue: number;
      paid_revenue: number;
      pending_revenue: number;
      refunded_revenue: number;
      net_revenue: number;
    };
    comparison: {
      previous_period_revenue: number;
      growth_amount: number;
      growth_percentage: number;
      trend: "up" | "down" | "stable";
    };
    breakdown: Array<{
      period: string;
      gross_revenue: number;
      net_revenue: number;
      booking_count: number;
      avg_booking_value: number;
    }>;
    revenue_sources: Array<{
      source: "base_rental" | "insurance" | "additional_fees" | "late_fees";
      amount: number;
      percentage: number;
    }>;
    payment_methods: Array<{
      method: string;
      count: number;
      amount: number;
      percentage: number;
    }>;
    top_revenue_cars: Array<{
      car_id: number;
      make: string;
      model: string;
      total_revenue: number;
      booking_count: number;
      avg_daily_rate: number;
    }>;
  };
}
```

### 3. Fleet Performance Report

**GET** `/reports/fleet`

**Query Parameters:**

- `period`: `month` | `quarter` | `year`
- `include_maintenance`: boolean
- `agency_id`: number (optional)

**Response:**

```typescript
interface FleetReportResponse {
  status: string;
  message: string;
  data: {
    fleet_overview: {
      total_vehicles: number;
      active_vehicles: number;
      utilization_rate: number;
      avg_daily_rate: number;
      maintenance_cost: number;
    };
    utilization_by_category: Array<{
      category: string;
      total_cars: number;
      avg_utilization: number;
      total_revenue: number;
      most_popular_car: string;
    }>;
    performance_metrics: Array<{
      car_id: number;
      make: string;
      model: string;
      license_plate: string;
      utilization_rate: number;
      total_bookings: number;
      total_revenue: number;
      avg_daily_rate: number;
      days_booked: number;
      days_available: number;
      maintenance_days: number;
      customer_rating?: number;
    }>;
    maintenance_summary: {
      cars_due_service: number;
      overdue_service: number;
      total_maintenance_cost: number;
      avg_service_interval: number;
    };
    category_analysis: Array<{
      category: string;
      demand_score: number;
      revenue_per_car: number;
      utilization_rate: number;
      recommended_fleet_size: number;
    }>;
  };
}
```

### 4. Customer Analytics Report

**GET** `/reports/customers`

**Query Parameters:**

- `period`: `month` | `quarter` | `year`
- `segment_by`: `loyalty_tier` | `booking_frequency` | `spending_level`

**Response:**

```typescript
interface CustomerReportResponse {
  status: string;
  message: string;
  data: {
    customer_summary: {
      total_customers: number;
      active_customers: number;
      new_customers: number;
      returning_customers: number;
      customer_lifetime_value: number;
    };
    top_customers: Array<{
      id: number;
      name: string;
      email: string;
      total_bookings: number;
      total_spent: number;
      avg_booking_value: number;
      loyalty_points: number;
      last_booking: string;
      customer_since: string;
    }>;
    customer_segments: Array<{
      segment: string;
      customer_count: number;
      avg_booking_value: number;
      total_revenue: number;
      retention_rate: number;
    }>;
    booking_patterns: {
      avg_booking_frequency: number;
      popular_booking_days: Array<{
        day: string;
        booking_count: number;
      }>;
      seasonal_trends: Array<{
        month: string;
        booking_count: number;
        avg_duration: number;
      }>;
    };
    geographic_distribution: Array<{
      location: string;
      customer_count: number;
      avg_booking_value: number;
    }>;
  };
}
```

### 5. Financial Summary Report

**GET** `/reports/financial`

**Query Parameters:**

- `period`: `month` | `quarter` | `year`
- `include_projections`: boolean

**Response:**

```typescript
interface FinancialReportResponse {
  status: string;
  message: string;
  data: {
    revenue_summary: {
      gross_revenue: number;
      net_revenue: number;
      total_refunds: number;
      pending_payments: number;
      collection_rate: number;
    };
    expense_breakdown: {
      maintenance_costs: number;
      insurance_costs: number;
      operational_costs: number;
      staff_costs: number;
      total_expenses: number;
    };
    profitability: {
      gross_profit: number;
      net_profit: number;
      profit_margin: number;
      roi: number;
    };
    cash_flow: Array<{
      month: string;
      revenue: number;
      expenses: number;
      net_cash_flow: number;
      cumulative_cash_flow: number;
    }>;
    aging_report: {
      current: number;
      overdue_30: number;
      overdue_60: number;
      overdue_90: number;
      bad_debt: number;
    };
    projections?: {
      next_month_revenue: number;
      next_quarter_revenue: number;
      projected_expenses: number;
      expected_profit: number;
    };
  };
}
```

### 6. Custom Report Builder

**POST** `/reports/custom`

**Request Body:**

```typescript
{
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
```

### 7. Export Reports

**GET** `/reports/export/{report_type}`

**Path Parameters:**

- `report_type`: `overview` | `revenue` | `fleet` | `customers` | `financial`

**Query Parameters:**

- `format`: `pdf` | `excel` | `csv`
- `period`: Time period for the report
- `agency_id`: number (optional)

**Response:** File download with appropriate MIME type

---

## 🔧 IMPLEMENTATION NOTES

### Error Handling

All endpoints should return consistent error responses:

```typescript
interface ErrorResponse {
  status: "error";
  message: string;
  code: string;
  details?: any;
  timestamp: string;
}
```

### Pagination

For paginated endpoints, use consistent pagination format:

```typescript
interface PaginationMeta {
  current_page: number;
  last_page: number;
  per_page: number;
  total: number;
  from: number;
  to: number;
  links: {
    first: string;
    last: string;
    prev: string | null;
    next: string | null;
  };
}
```

### Rate Limiting

- Dashboard endpoints: 60 requests per minute
- Reports endpoints: 30 requests per minute
- Export endpoints: 10 requests per minute

### Caching Strategy

- Dashboard stats: Cache for 5 minutes
- Recent activities: Cache for 2 minutes
- Reports data: Cache for 15 minutes
- Export files: Cache for 1 hour

### Authentication & Authorization

- All endpoints require valid JWT token
- Role-based access control:
  - **Customer**: Limited dashboard data, own bookings only
  - **Admin**: Agency-specific data, agency bookings and reports
  - **SuperAdmin**: All data across all agencies

### Real-time Updates

Consider implementing WebSocket connections for:

- Dashboard live statistics
- Booking status changes
- Fleet status updates
- Payment notifications
