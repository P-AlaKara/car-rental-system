# Updated Login Response Structure with Dashboard Data

## SuperAdmin Login Response

**POST** `/auth/login`

**REQUEST:**

```json
{
  "email": "superAdmin@example.com",
  "password": "Admin@123"
}
```

**RESPONSE:**

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "43|kQKUL76g68W8ctK47RTsuZNYVpaT9j9sCmv8pdGta8918f87",
    "user": {
      "id": 1,
      "first_name": "System",
      "last_name": "Admin",
      "email": "superAdmin@example.com",
      "phone": "0700000000",
      "role": "superAdmin",
      "loyalty_points": 0,
      "is_active": true,
      "created_at": "2025-08-28 10:21:40",
      "updated_at": "2025-08-29 08:10:24",
      "agency": {
        "id": 1,
        "name": "City Drive Rentals Ltd",
        "location": "Nairobi CBD, Kenya",
        "postal_code": "00101",
        "contact": "+254798765432",
        "email": "citydrive-updated@example.com",
        "is_active": true,
        "created_at": "2025-08-28 10:21:39",
        "updated_at": "2025-08-28 18:35:52"
      }
    },
    "dashboard": {
      // === BASIC STATS ===
      "total_cars": 4,
      "available_cars": 2,
      "rented_cars": 0,
      "disabled_cars": 1,
      "under_maintenance_cars": 1,
      "cars_due_service": 2,

      // === BOOKING STATS ===
      "total_bookings": 1,
      "active_bookings": 0,
      "pending_bookings": 1,
      "confirmed_bookings": 0,
      "in_progress_bookings": 0,
      "completed_bookings": 0,
      "cancelled_bookings": 0,

      // === USER STATS ===
      "total_users": 12,
      "active_users": 12,
      "inactive_users": 0,
      "customer_users": 10,
      "admin_users": 1,
      "superadmin_users": 1,

      // === AGENCY STATS (SuperAdmin Only) ===
      "agencies_count": 3,
      "active_agencies": 3,
      "inactive_agencies": 0,

      // === FINANCIAL STATS ===
      "monthly_revenue": 5880.0,
      "total_revenue": 15000.0,
      "pending_payments": 3,
      "pending_amount": 2450.0,
      "paid_amount": 12550.0,
      "avg_booking_value": 850.0,
      "avg_daily_rate": 85.0,

      // === OPERATIONAL STATS ===
      "fleet_utilization_rate": 50.0,
      "conversion_rate": 68.0,
      "avg_rental_duration": 3.2,
      "service_threshold_km": 5000,

      // === REVENUE TREND (Last 7 days) ===
      "revenue_trend": [
        {
          "date": "2025-08-23",
          "day": "Mon",
          "revenue": 850,
          "bookings": 12
        },
        {
          "date": "2025-08-24",
          "day": "Tue",
          "revenue": 920,
          "bookings": 15
        },
        {
          "date": "2025-08-25",
          "day": "Wed",
          "revenue": 780,
          "bookings": 10
        },
        {
          "date": "2025-08-26",
          "day": "Thu",
          "revenue": 1050,
          "bookings": 18
        },
        {
          "date": "2025-08-27",
          "day": "Fri",
          "revenue": 1200,
          "bookings": 22
        },
        {
          "date": "2025-08-28",
          "day": "Sat",
          "revenue": 980,
          "bookings": 16
        },
        {
          "date": "2025-08-29",
          "day": "Sun",
          "revenue": 1100,
          "bookings": 19
        }
      ],

      // === BOOKING STATUS DISTRIBUTION ===
      "booking_distribution": [
        {
          "status": "confirmed",
          "count": 45,
          "percentage": 66.2,
          "color": "#22c55e"
        },
        {
          "status": "in_progress",
          "count": 12,
          "percentage": 17.6,
          "color": "#3b82f6"
        },
        {
          "status": "pending",
          "count": 8,
          "percentage": 11.8,
          "color": "#eab308"
        },
        {
          "status": "cancelled",
          "count": 3,
          "percentage": 4.4,
          "color": "#ef4444"
        }
      ],

      // === FLEET BY CATEGORY ===
      "fleet_by_category": [
        {
          "category": "Sedan",
          "count": 2,
          "available": 1,
          "rented": 1,
          "maintenance": 0,
          "color": "#3b82f6"
        },
        {
          "category": "SUV",
          "count": 1,
          "available": 1,
          "rented": 0,
          "maintenance": 0,
          "color": "#22c55e"
        },
        {
          "category": "Hatchback",
          "count": 1,
          "available": 0,
          "rented": 0,
          "maintenance": 1,
          "color": "#8b5cf6"
        }
      ],

      // === RECENT ACTIVITIES (Last 5) ===
      "recent_activities": [
        {
          "id": 1,
          "type": "booking_created",
          "title": "New Booking Created",
          "description": "John Doe booked 2023 Toyota Camry",
          "user": {
            "id": 15,
            "name": "John Doe",
            "email": "john@example.com"
          },
          "car": {
            "id": 1,
            "make": "Toyota",
            "model": "Camry",
            "year": 2023,
            "license_plate": "KCB 123A"
          },
          "booking": {
            "id": 1,
            "start_date": "2025-08-30",
            "end_date": "2025-09-02",
            "total_cost": 850,
            "status": "pending"
          },
          "timestamp": "2025-08-29T14:30:00Z",
          "time_ago": "2 hours ago"
        },
        {
          "id": 2,
          "type": "payment_received",
          "title": "Payment Received",
          "description": "Payment of $1,200 received from Jane Smith",
          "user": {
            "id": 16,
            "name": "Jane Smith",
            "email": "jane@example.com"
          },
          "booking": {
            "id": 2,
            "total_cost": 1200,
            "status": "confirmed"
          },
          "timestamp": "2025-08-29T12:15:00Z",
          "time_ago": "4 hours ago"
        }
      ],

      // === PENDING ACTIONS ===
      "pending_actions": {
        "pending_bookings": [
          {
            "id": 1,
            "user_name": "John Doe",
            "car_details": "2023 Toyota Camry (KCB 123A)",
            "created_at": "2025-08-29T14:30:00Z",
            "total_cost": 850
          }
        ],
        "pending_payments": [
          {
            "booking_id": 3,
            "user_name": "Mike Johnson",
            "amount": 450,
            "due_date": "2025-08-25",
            "days_overdue": 4
          },
          {
            "booking_id": 4,
            "user_name": "Sarah Wilson",
            "amount": 1200,
            "due_date": "2025-08-27",
            "days_overdue": 2
          }
        ],
        "cars_due_service": [
          {
            "id": 2,
            "make": "Honda",
            "model": "Civic",
            "license_plate": "KCA 456B",
            "current_odometer": 15500,
            "last_service_odometer": 10000,
            "service_threshold_km": 5000,
            "overdue_km": 500
          },
          {
            "id": 3,
            "make": "Nissan",
            "model": "Altima",
            "license_plate": "KCC 789C",
            "current_odometer": 22000,
            "last_service_odometer": 15000,
            "service_threshold_km": 5000,
            "overdue_km": 2000
          }
        ]
      },

      // === GROWTH METRICS ===
      "growth_metrics": {
        "revenue_growth_percentage": 12.5,
        "booking_growth_percentage": 15.0,
        "user_growth_percentage": 8.3,
        "fleet_growth_count": 2
      }
    }
  }
}
```

## Admin Login Response

**POST** `/auth/login`

**REQUEST:**

```json
{
  "email": "admin@example.com",
  "password": "Admin@123"
}
```

**RESPONSE:**

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "45|eWRWuh8XrbpoQSTioxHy8tit7EpzSLciG3Ix4HlS921ebe7a",
    "user": {
      "id": 2,
      "first_name": "System",
      "last_name": "Admin",
      "email": "admin@example.com",
      "phone": "0711111111",
      "role": "admin",
      "loyalty_points": 0,
      "is_active": true,
      "created_at": "2025-08-28 10:21:40",
      "updated_at": "2025-08-29 08:19:20",
      "agency": {
        "id": 1,
        "name": "City Drive Rentals Ltd",
        "location": "Nairobi CBD, Kenya",
        "postal_code": "00101",
        "contact": "+254798765432",
        "email": "citydrive-updated@example.com",
        "is_active": true,
        "created_at": "2025-08-28 10:21:39",
        "updated_at": "2025-08-28 18:35:52"
      }
    },
    "dashboard": {
      // === AGENCY-SPECIFIC STATS ===
      "agency_name": "City Drive Rentals Ltd",
      "agency_id": 1,

      // === BASIC STATS (Agency-filtered) ===
      "total_cars": 4,
      "available_cars": 2,
      "rented_cars": 0,
      "disabled_cars": 1,
      "under_maintenance_cars": 1,
      "cars_due_service": 2,

      // === BOOKING STATS (Agency-filtered) ===
      "total_bookings": 1,
      "active_bookings": 0,
      "pending_bookings": 1,
      "confirmed_bookings": 0,
      "in_progress_bookings": 0,
      "completed_bookings": 0,
      "cancelled_bookings": 0,

      // === USER STATS (Agency customers only) ===
      "total_users": 8,
      "active_users": 8,
      "inactive_users": 0,
      "customer_users": 8,

      // === FINANCIAL STATS (Agency-filtered) ===
      "monthly_revenue": 5880.0,
      "total_revenue": 15000.0,
      "pending_payments": 3,
      "pending_amount": 2450.0,
      "paid_amount": 12550.0,
      "avg_booking_value": 850.0,
      "avg_daily_rate": 85.0,

      // === OPERATIONAL STATS ===
      "fleet_utilization_rate": 50.0,
      "conversion_rate": 68.0,
      "avg_rental_duration": 3.2,
      "service_threshold_km": 5000,

      // === REVENUE TREND (Last 7 days, Agency-specific) ===
      "revenue_trend": [
        {
          "date": "2025-08-23",
          "day": "Mon",
          "revenue": 850,
          "bookings": 12
        },
        {
          "date": "2025-08-24",
          "day": "Tue",
          "revenue": 920,
          "bookings": 15
        },
        {
          "date": "2025-08-25",
          "day": "Wed",
          "revenue": 780,
          "bookings": 10
        },
        {
          "date": "2025-08-26",
          "day": "Thu",
          "revenue": 1050,
          "bookings": 18
        },
        {
          "date": "2025-08-27",
          "day": "Fri",
          "revenue": 1200,
          "bookings": 22
        },
        {
          "date": "2025-08-28",
          "day": "Sat",
          "revenue": 980,
          "bookings": 16
        },
        {
          "date": "2025-08-29",
          "day": "Sun",
          "revenue": 1100,
          "bookings": 19
        }
      ],

      // === BOOKING STATUS DISTRIBUTION (Agency-specific) ===
      "booking_distribution": [
        {
          "status": "confirmed",
          "count": 45,
          "percentage": 66.2,
          "color": "#22c55e"
        },
        {
          "status": "in_progress",
          "count": 12,
          "percentage": 17.6,
          "color": "#3b82f6"
        },
        {
          "status": "pending",
          "count": 8,
          "percentage": 11.8,
          "color": "#eab308"
        },
        {
          "status": "cancelled",
          "count": 3,
          "percentage": 4.4,
          "color": "#ef4444"
        }
      ],

      // === FLEET BY CATEGORY (Agency-specific) ===
      "fleet_by_category": [
        {
          "category": "Sedan",
          "count": 2,
          "available": 1,
          "rented": 1,
          "maintenance": 0,
          "color": "#3b82f6"
        },
        {
          "category": "SUV",
          "count": 1,
          "available": 1,
          "rented": 0,
          "maintenance": 0,
          "color": "#22c55e"
        },
        {
          "category": "Hatchback",
          "count": 1,
          "available": 0,
          "rented": 0,
          "maintenance": 1,
          "color": "#8b5cf6"
        }
      ],

      // === RECENT ACTIVITIES (Agency-specific, Last 5) ===
      "recent_activities": [
        {
          "id": 1,
          "type": "booking_created",
          "title": "New Booking Created",
          "description": "John Doe booked 2023 Toyota Camry",
          "user": {
            "id": 15,
            "name": "John Doe",
            "email": "john@example.com"
          },
          "car": {
            "id": 1,
            "make": "Toyota",
            "model": "Camry",
            "year": 2023,
            "license_plate": "KCB 123A"
          },
          "booking": {
            "id": 1,
            "start_date": "2025-08-30",
            "end_date": "2025-09-02",
            "total_cost": 850,
            "status": "pending"
          },
          "timestamp": "2025-08-29T14:30:00Z",
          "time_ago": "2 hours ago"
        }
      ],

      // === PENDING ACTIONS (Agency-specific) ===
      "pending_actions": {
        "pending_bookings": [
          {
            "id": 1,
            "user_name": "John Doe",
            "car_details": "2023 Toyota Camry (KCB 123A)",
            "created_at": "2025-08-29T14:30:00Z",
            "total_cost": 850
          }
        ],
        "pending_payments": [
          {
            "booking_id": 3,
            "user_name": "Mike Johnson",
            "amount": 450,
            "due_date": "2025-08-25",
            "days_overdue": 4
          }
        ],
        "cars_due_service": [
          {
            "id": 2,
            "make": "Honda",
            "model": "Civic",
            "license_plate": "KCA 456B",
            "current_odometer": 15500,
            "last_service_odometer": 10000,
            "service_threshold_km": 5000,
            "overdue_km": 500
          }
        ]
      },

      // === GROWTH METRICS (Agency-specific) ===
      "growth_metrics": {
        "revenue_growth_percentage": 12.5,
        "booking_growth_percentage": 15.0,
        "user_growth_percentage": 8.3,
        "fleet_growth_count": 2
      }
    }
  }
}
```

## Customer Login Response (for reference)

**POST** `/auth/login`

**REQUEST:**

```json
{
  "email": "customer@example.com",
  "password": "password123"
}
```

**RESPONSE:**

```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "token": "46|xYzAbC123DefGhi456JklMno789PqrStu012VwxYz345Abc",
    "user": {
      "id": 15,
      "first_name": "John",
      "last_name": "Doe",
      "email": "customer@example.com",
      "phone": "0722000000",
      "role": "customer",
      "loyalty_points": 150,
      "is_active": true,
      "created_at": "2025-08-15 09:30:00",
      "updated_at": "2025-08-29 10:45:00",
      "agency": null
    },
    "dashboard": {
      "data": "Customer dashboard data would be minimal - just their bookings and profile info"
    }
  }
}
```

## Summary of Dashboard Data Requirements

### Key Data Fields Needed:

#### **Basic Fleet Statistics:**

- `total_cars`, `available_cars`, `rented_cars`, `disabled_cars`, `under_maintenance_cars`, `cars_due_service`

#### **Booking Statistics:**

- `total_bookings`, `active_bookings`, `pending_bookings`, `confirmed_bookings`, `in_progress_bookings`, `completed_bookings`, `cancelled_bookings`

#### **User Statistics:**

- `total_users`, `active_users`, `inactive_users`, `customer_users`, `admin_users` (SuperAdmin only), `superadmin_users` (SuperAdmin only)

#### **Financial Data:**

- `monthly_revenue`, `total_revenue`, `pending_payments`, `pending_amount`, `paid_amount`, `avg_booking_value`, `avg_daily_rate`

#### **Charts & Analytics:**

- `revenue_trend` (7 days), `booking_distribution`, `fleet_by_category`

#### **Real-time Data:**

- `recent_activities` (last 5), `pending_actions` (bookings, payments, maintenance)

#### **Growth Metrics:**

- `revenue_growth_percentage`, `booking_growth_percentage`, `user_growth_percentage`, `fleet_growth_count`

### Role-Based Data Filtering:

- **SuperAdmin**: Gets system-wide data across all agencies
- **Admin**: Gets data filtered to their specific agency only
- **Customer**: Gets minimal dashboard data (just their own bookings)

This structure ensures all dashboard data is available immediately upon login, eliminating the need for additional API calls to populate the dashboard.
