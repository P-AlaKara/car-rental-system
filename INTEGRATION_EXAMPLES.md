# Integration Example: Dashboard, Bookings & Reports Pages

This document shows how to integrate the new API endpoints into your existing pages.

## 📊 Dashboard Page Integration

### Replace Demo Data with Real API Calls

```typescript
// src/pages/DashboardPage.tsx
import React, { useState, useEffect } from "react";
import { dashboardAPI } from "../lib/dashboard-bookings-reports-api";
import type {
  DashboardStats,
  RevenueTrendData,
  RecentActivity,
} from "../lib/dashboard-bookings-reports-types";

const DashboardPage = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [revenueTrend, setRevenueTrend] = useState<RevenueTrendData[]>([]);
  const [recentActivities, setRecentActivities] = useState<RecentActivity[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);

      // Load all dashboard data in parallel
      const [statsResponse, trendResponse, activitiesResponse] =
        await Promise.all([
          dashboardAPI.getStats(),
          dashboardAPI.getRevenueTrend("7d"),
          dashboardAPI.getRecentActivities(10),
        ]);

      setStats(statsResponse.data);
      setRevenueTrend(trendResponse.data);
      setRecentActivities(activitiesResponse.data);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return <div className="text-red-600 p-4">Error: {error}</div>;
  }

  if (!stats) {
    return <div className="text-gray-600 p-4">No dashboard data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <StatCard title="Total Cars" value={stats.total_cars} icon="car" />
        <StatCard title="Available" value={stats.available_cars} icon="check" />
        <StatCard
          title="Active Bookings"
          value={stats.active_bookings}
          icon="calendar"
        />
        <StatCard
          title="Pending Payments"
          value={stats.pending_payments}
          icon="payment"
        />
        <StatCard
          title="Due for Service"
          value={stats.cars_due_service}
          icon="service"
        />
        <StatCard
          title="Monthly Revenue"
          value={`$${stats.monthly_revenue.toLocaleString()}`}
          icon="revenue"
        />
      </div>

      {/* Revenue Chart - use revenueTrend data */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Revenue Trends
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={revenueTrend}>{/* Chart configuration */}</AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Recent Activities */}
      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Recent Activity
        </h3>
        <div className="space-y-4">
          {recentActivities.map((activity) => (
            <ActivityItem key={activity.id} activity={activity} />
          ))}
        </div>
      </div>
    </div>
  );
};
```

## 📅 Bookings Page Integration

### Replace Demo Data with Real API Calls

```typescript
// src/pages/BookingsPage.tsx
import React, { useState, useEffect } from "react";
import { bookingsAPI } from "../lib/dashboard-bookings-reports-api";
import type {
  BookingListItem,
  BookingFilters,
} from "../lib/dashboard-bookings-reports-types";

const BookingsPage = () => {
  const [bookings, setBookings] = useState<BookingListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<BookingFilters>({
    page: 1,
    size: 20,
    status: "all",
    sort_by: "created_at",
    sort_order: "desc",
  });
  const [totalPages, setTotalPages] = useState(1);
  const [summary, setSummary] = useState<any>(null);

  useEffect(() => {
    loadBookings();
  }, [filters]);

  const loadBookings = async () => {
    try {
      setLoading(true);
      const response = await bookingsAPI.getBookings(filters);

      setBookings(response.data.bookings);
      setTotalPages(response.data.meta.last_page);
      setSummary(response.data.summary);
    } catch (error) {
      console.error("Failed to load bookings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (bookingId: number, newStatus: string) => {
    try {
      await bookingsAPI.updateBookingStatus(bookingId, {
        status: newStatus as any,
        admin_comments: `Status updated to ${newStatus}`,
      });

      // Reload bookings to reflect changes
      await loadBookings();
    } catch (error) {
      console.error("Failed to update booking status:", error);
    }
  };

  const handleFilterChange = (newFilters: Partial<BookingFilters>) => {
    setFilters((prev) => ({ ...prev, ...newFilters, page: 1 }));
  };

  const handleExport = async (format: "csv" | "excel" | "pdf") => {
    try {
      const blob = await bookingsAPI.exportBookings(format, filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `bookings.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export bookings:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Export */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Bookings Management</h2>
        <div className="flex gap-2">
          <button onClick={() => handleExport("pdf")} className="btn-primary">
            Export PDF
          </button>
          <button
            onClick={() => handleExport("excel")}
            className="btn-secondary"
          >
            Export Excel
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-5 gap-4">
          <SummaryCard title="Total" value={summary.total_bookings} />
          <SummaryCard title="Pending" value={summary.status_counts.pending} />
          <SummaryCard
            title="Confirmed"
            value={summary.status_counts.confirmed}
          />
          <SummaryCard
            title="In Progress"
            value={summary.status_counts.in_progress}
          />
          <SummaryCard
            title="Completed"
            value={summary.status_counts.completed}
          />
        </div>
      )}

      {/* Filters */}
      <BookingFilters filters={filters} onChange={handleFilterChange} />

      {/* Bookings Table */}
      <BookingsTable
        bookings={bookings}
        loading={loading}
        onStatusUpdate={handleStatusUpdate}
      />

      {/* Pagination */}
      <Pagination
        currentPage={filters.page || 1}
        totalPages={totalPages}
        onPageChange={(page) => setFilters((prev) => ({ ...prev, page }))}
      />
    </div>
  );
};
```

## 📈 Reports Page Integration

### Replace Demo Data with Real API Calls

```typescript
// src/pages/ReportsPage.tsx
import React, { useState, useEffect } from "react";
import { reportsAPI } from "../lib/dashboard-bookings-reports-api";
import type {
  OverviewReport,
  RevenueReport,
} from "../lib/dashboard-bookings-reports-types";

const ReportsPage = () => {
  const [selectedReport, setSelectedReport] = useState<
    "overview" | "revenue" | "fleet" | "customers"
  >("overview");
  const [selectedPeriod, setSelectedPeriod] = useState<
    "30d" | "3m" | "6m" | "12m"
  >("30d");
  const [overviewData, setOverviewData] = useState<OverviewReport | null>(null);
  const [revenueData, setRevenueData] = useState<RevenueReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadReportData();
  }, [selectedReport, selectedPeriod]);

  const loadReportData = async () => {
    try {
      setLoading(true);

      switch (selectedReport) {
        case "overview":
          const overviewResponse = await reportsAPI.getOverviewReport(
            selectedPeriod
          );
          setOverviewData(overviewResponse.data);
          break;

        case "revenue":
          const revenueResponse = await reportsAPI.getRevenueReport("month");
          setRevenueData(revenueResponse.data);
          break;

        // Add other report types as needed
      }
    } catch (error) {
      console.error("Failed to load report data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExportReport = async (format: "pdf" | "excel" | "csv") => {
    try {
      const blob = await reportsAPI.exportReport(
        selectedReport,
        format,
        selectedPeriod
      );
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${selectedReport}-report.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export report:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Reports & Analytics</h2>
        <div className="flex gap-2">
          <select
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value as any)}
            className="select"
          >
            <option value="30d">Last 30 Days</option>
            <option value="3m">Last 3 Months</option>
            <option value="6m">Last 6 Months</option>
            <option value="12m">Last Year</option>
          </select>
          <button
            onClick={() => handleExportReport("pdf")}
            className="btn-primary"
          >
            Export PDF
          </button>
        </div>
      </div>

      {/* Report Navigation */}
      <div className="flex gap-2">
        {["overview", "revenue", "fleet", "customers"].map((report) => (
          <button
            key={report}
            onClick={() => setSelectedReport(report as any)}
            className={`btn ${
              selectedReport === report ? "btn-primary" : "btn-secondary"
            }`}
          >
            {report.charAt(0).toUpperCase() + report.slice(1)}
          </button>
        ))}
      </div>

      {/* Report Content */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          Loading report...
        </div>
      ) : (
        <div className="space-y-6">
          {selectedReport === "overview" && overviewData && (
            <OverviewReportView data={overviewData} />
          )}
          {selectedReport === "revenue" && revenueData && (
            <RevenueReportView data={revenueData} />
          )}
          {/* Add other report views as needed */}
        </div>
      )}
    </div>
  );
};
```

## 🔧 Error Handling & Loading States

### Common Error Handling Pattern

```typescript
// src/hooks/useApiCall.ts
import { useState, useEffect } from "react";

export function useApiCall<T>(
  apiCall: () => Promise<{ data: T }>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, dependencies);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiCall();
      setData(response.data);
    } catch (err) {
      console.error("API call failed:", err);
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch: loadData };
}

// Usage example:
const {
  data: stats,
  loading,
  error,
} = useApiCall(() => dashboardAPI.getStats(), []);
```

## 🚀 Quick Migration Steps

1. **Install the new API files:**

   - Add `dashboard-bookings-reports-types.ts`
   - Add `dashboard-bookings-reports-api.ts`

2. **Update your pages:**

   - Replace demo data imports with API calls
   - Add loading and error states
   - Implement real-time updates where needed

3. **Test the integration:**

   - Verify all endpoints work with your backend
   - Test error scenarios
   - Validate data transformations

4. **Add advanced features:**
   - Real-time updates with WebSockets
   - Offline support with caching
   - Advanced filtering and search

## 📝 Notes

- All API functions include proper TypeScript types
- Error handling is consistent across all endpoints
- Export functionality is built-in for reports and bookings
- Role-based data filtering happens on the backend
- All endpoints support pagination where appropriate
- Loading states should be shown for better UX
