import * as React from 'react'
import { 
  DEMO_CARS, 
  DEMO_BOOKINGS, 
  DEMO_USERS, 
  getAvailableCars, 
  getCarsDueForService, 
  getPendingPayments, 
  getActiveBookings 
} from '../lib/demo-data'
import type { DashboardStats } from '../lib/types'
import { 
  AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

// Status badge component
const StatusBadge = ({ status, children }: { status: string; children: React.ReactNode }) => {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-green-100 text-green-800',
    in_progress: 'bg-blue-100 text-blue-800',
    completed: 'bg-gray-100 text-gray-800',
    cancelled: 'bg-red-100 text-red-800',
    available: 'bg-green-100 text-green-800',
    booked: 'bg-yellow-100 text-yellow-800',
    in_use: 'bg-blue-100 text-blue-800',
    under_maintenance: 'bg-red-100 text-red-800',
    payment_pending: 'bg-orange-100 text-orange-800',
    invoice_sent: 'bg-blue-100 text-blue-800',
    paid: 'bg-green-100 text-green-800',
    overdue: 'bg-red-100 text-red-800'
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
      {children}
    </span>
  )
}

const DashboardPage = () => {
  const stats: DashboardStats = {
    total_cars: DEMO_CARS.length,
    available_cars: getAvailableCars().length,
    active_bookings: getActiveBookings().length,
    pending_payments: getPendingPayments().length,
    total_users: DEMO_USERS.length,
    monthly_revenue: 588,
    cars_due_service: getCarsDueForService().length,
    service_threshold_km: 5000
  }

  const pendingBookings = DEMO_BOOKINGS.filter(b => b.status === 'pending')
  const carsDueService = getCarsDueForService()

  return (
    <div className="space-y-6">
      {/* Enhanced Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-blue-900">{stats.total_cars}</div>
              <div className="text-sm font-medium text-blue-700">Total Cars</div>
            </div>
            <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
          </div>
          <div className="mt-2 text-xs text-blue-600">+2 this month</div>
        </div>

        <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-green-900">{stats.available_cars}</div>
              <div className="text-sm font-medium text-green-700">Available</div>
            </div>
            <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
          <div className="mt-2 text-xs text-green-600">50% utilization</div>
        </div>
        
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-purple-900">{stats.active_bookings}</div>
              <div className="text-sm font-medium text-purple-700">Active Bookings</div>
            </div>
            <div className="w-10 h-10 bg-purple-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
          </div>
          <div className="mt-2 text-xs text-purple-600">+15% vs last week</div>
        </div>
        
        <div className="bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-orange-900">{stats.pending_payments}</div>
              <div className="text-sm font-medium text-orange-700">Pending Payments</div>
            </div>
            <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
          <div className="mt-2 text-xs text-orange-600">$2,450 pending</div>
        </div>
        
        <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-red-900">{stats.cars_due_service}</div>
              <div className="text-sm font-medium text-red-700">Due for Service</div>
            </div>
            <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
          </div>
          <div className="mt-2 text-xs text-red-600">Schedule maintenance</div>
        </div>
        
        <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-xl p-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-indigo-900">${stats.monthly_revenue.toLocaleString()}</div>
              <div className="text-sm font-medium text-indigo-700">Monthly Revenue</div>
            </div>
            <div className="w-10 h-10 bg-indigo-500 rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            </div>
          </div>
          <div className="mt-2 text-xs text-indigo-600">+8.2% vs last month</div>
        </div>
      </div>

      {/* Charts and Analytics Section */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Revenue Trends</h3>
            <select 
              className="text-sm border border-gray-300 rounded-lg px-3 py-1"
              aria-label="Select time period for revenue trends"
            >
              <option>Last 7 days</option>
              <option>Last 30 days</option>
              <option>Last 3 months</option>
            </select>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={[
                  { day: 'Mon', revenue: 850, bookings: 12 },
                  { day: 'Tue', revenue: 920, bookings: 15 },
                  { day: 'Wed', revenue: 780, bookings: 10 },
                  { day: 'Thu', revenue: 1050, bookings: 18 },
                  { day: 'Fri', revenue: 1200, bookings: 22 },
                  { day: 'Sat', revenue: 980, bookings: 16 },
                  { day: 'Sun', revenue: 1100, bookings: 19 }
                ]}
                margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
              >
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.1}/>
                  </linearGradient>
                  <linearGradient id="colorBookings" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="day" 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `$${value}`}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                  formatter={(value, _name) => [
                    _name === 'revenue' ? `$${value}` : value,
                    _name === 'revenue' ? 'Revenue' : 'Bookings'
                  ]}
                />
                <Legend />
                <Area 
                  type="monotone" 
                  dataKey="revenue" 
                  stroke="#0ea5e9" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorRevenue)" 
                />
                <Area 
                  type="monotone" 
                  dataKey="bookings" 
                  stroke="#8b5cf6" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorBookings)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex items-center justify-between text-sm">
            <span className="text-gray-600">Total: $4,250</span>
            <span className="text-green-600 font-medium">+12.5% vs last week</span>
          </div>
        </div>

        {/* Booking Status Distribution */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-gray-900">Booking Status Distribution</h3>
            <div className="text-sm text-gray-500">This month</div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: 'Confirmed', value: 45, color: '#22c55e' },
                    { name: 'In Progress', value: 12, color: '#3b82f6' },
                    { name: 'Pending', value: 8, color: '#eab308' },
                    { name: 'Cancelled', value: 3, color: '#ef4444' }
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {[
                    { name: 'Confirmed', value: 45, color: '#22c55e' },
                    { name: 'In Progress', value: 12, color: '#3b82f6' },
                    { name: 'Pending', value: 8, color: '#eab308' },
                    { name: 'Cancelled', value: 3, color: '#ef4444' }
                  ].map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Total Bookings</span>
              <span className="font-semibold text-gray-900">68</span>
            </div>
          </div>
        </div>
      </div>

      {/* Fleet Utilization and Quick Actions */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Fleet Utilization */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Fleet Utilization</h3>
          <div className="h-48 mb-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={[
                  { status: 'In Use', count: stats.active_bookings, total: stats.total_cars, color: '#3b82f6' },
                  { status: 'Available', count: stats.available_cars, total: stats.total_cars, color: '#22c55e' },
                  { status: 'Maintenance', count: stats.cars_due_service, total: stats.total_cars, color: '#ef4444' }
                ]}
                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="status" 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#64748b" 
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                  }}
                  formatter={(value) => [value, 'Vehicles']}
                />
                <Bar 
                  dataKey="count" 
                  fill="#0ea5e9" 
                  radius={[4, 4, 0, 0]}
                  maxBarSize={50}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">In Use</span>
              <span className="font-medium">{stats.active_bookings}/{stats.total_cars}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Available</span>
              <span className="font-medium">{stats.available_cars}/{stats.total_cars}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Maintenance</span>
              <span className="font-medium">{stats.cars_due_service}/{stats.total_cars}</span>
            </div>
          </div>
          
          {/* Car Category Distribution */}
          <div className="mt-6 pt-4 border-t border-gray-100">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Fleet by Category</h4>
            <div className="h-32">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={(() => {
                      const categories = DEMO_CARS.reduce((acc, car) => {
                        const categoryKey = typeof car.category === 'object' ? car.category?.name : car.category
                        if (!categoryKey) return acc
                        acc[categoryKey] = (acc[categoryKey] || 0) + 1
                        return acc
                      }, {} as Record<string, number>)
                      
                      const COLORS = ['#3b82f6', '#22c55e', '#8b5cf6', '#f97316', '#eab308', '#ef4444']
                      
                      return Object.entries(categories).map(([category, count], index) => ({
                        name: category,
                        value: count,
                        color: COLORS[index % COLORS.length]
                      }))
                    })()}
                    cx="50%"
                    cy="50%"
                    innerRadius={20}
                    outerRadius={50}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {(() => {
                      const categories = DEMO_CARS.reduce((acc, car) => {
                        const categoryKey = typeof car.category === 'object' ? car.category?.name : car.category
                        if (!categoryKey) return acc
                        acc[categoryKey] = (acc[categoryKey] || 0) + 1
                        return acc
                      }, {} as Record<string, number>)
                      
                      const COLORS = ['#3b82f6', '#22c55e', '#8b5cf6', '#f97316', '#eab308', '#ef4444']
                      
                      return Object.entries(categories).map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))
                    })()}
                  </Pie>
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '1px solid #e2e8f0',
                      borderRadius: '8px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-3 space-y-1">
              {(() => {
                const categories = DEMO_CARS.reduce((acc, car) => {
                  const categoryKey = typeof car.category === 'object' ? car.category?.name : car.category
                  if (!categoryKey) return acc
                  acc[categoryKey] = (acc[categoryKey] || 0) + 1
                  return acc
                }, {} as Record<string, number>)
                
                const COLORS = ['#3b82f6', '#22c55e', '#8b5cf6', '#f97316', '#eab308', '#ef4444']
                
                return Object.entries(categories).map(([category, count], index) => (
                  <div key={category} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-2 h-2 rounded-full" 
                        style={{ backgroundColor: COLORS[index % COLORS.length] }}
                      ></div>
                      <span className="text-gray-700">{category}</span>
                    </div>
                    <span className="font-medium text-gray-900">{count}</span>
                  </div>
                ))
              })()}
            </div>
          </div>
        </div>

        {/* Pending Actions */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Actions</h3>
          <div className="space-y-4">
            {pendingBookings.length > 0 && (
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-yellow-900">{pendingBookings.length} pending bookings</div>
                    <div className="text-sm text-yellow-700">Require admin approval</div>
                  </div>
                  <button className="bg-yellow-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-yellow-700 transition-colors">
                    Review
                  </button>
                </div>
              </div>
            )}
            {getPendingPayments().length > 0 && (
              <div className="bg-gradient-to-r from-orange-50 to-red-50 border border-orange-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-orange-900">{getPendingPayments().length} pending payments</div>
                    <div className="text-sm text-orange-700">Invoices to be sent</div>
                  </div>
                  <button className="bg-orange-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-orange-700 transition-colors">
                    Process
                  </button>
                </div>
              </div>
            )}
            {carsDueService.length > 0 && (
              <div className="bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium text-red-900">{carsDueService.length} cars need service</div>
                    <div className="text-sm text-red-700">Schedule maintenance</div>
                  </div>
                  <button className="bg-red-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-red-700 transition-colors">
                    Schedule
                  </button>
                </div>
              </div>
            )}
            {pendingBookings.length === 0 && getPendingPayments().length === 0 && carsDueService.length === 0 && (
              <div className="text-center py-8">
                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-sm text-gray-600">All caught up!</p>
                <p className="text-xs text-gray-500">No pending actions</p>
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <span className="text-sm text-gray-700">Total Users</span>
              </div>
              <span className="font-semibold text-gray-900">{stats.total_users}</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <span className="text-sm text-gray-700">Avg. Daily Rate</span>
              </div>
              <span className="font-semibold text-gray-900">$85</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <span className="text-sm text-gray-700">Conversion Rate</span>
              </div>
              <span className="font-semibold text-gray-900">68%</span>
            </div>
            
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                  <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-sm text-gray-700">Avg. Rental Duration</span>
              </div>
              <span className="font-semibold text-gray-900">3.2 days</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-600 font-medium">Live</span>
            <button className="text-sm text-sky-600 hover:text-sky-700 font-medium">View All</button>
          </div>
        </div>
        <div className="space-y-4">
          {DEMO_BOOKINGS.slice(0, 5).map((booking, index) => {
            const user = DEMO_USERS.find(u => u.id === booking.user_id)
            const car = DEMO_CARS.find(c => c.id === booking.car_id)
            const timeAgo = (() => {
              const now = new Date()
              const created = new Date(booking.created_at)
              const diff = now.getTime() - created.getTime()
              const minutes = Math.floor(diff / (1000 * 60))
              const hours = Math.floor(minutes / 60)
              const days = Math.floor(hours / 24)
              
              if (days > 0) return `${days}d ago`
              if (hours > 0) return `${hours}h ago`
              if (minutes > 0) return `${minutes}m ago`
              return 'Just now'
            })()
            
            return (
              <div key={booking.id} className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div className="relative">
                  <div className="w-10 h-10 bg-sky-100 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-sky-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  {index === 0 && (
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">
                      {user ? `${user.first_name} ${user.last_name}` : 'Unknown User'}
                    </span>
                    <span className="text-sm text-gray-500">booked</span>
                    <span className="font-medium text-gray-900">
                      {car ? `${car.year} ${car.make} ${car.model}` : `Car ${booking.car_id}`}
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>{new Date(booking.start_date).toLocaleDateString()} - {new Date(booking.end_date).toLocaleDateString()}</span>
                    <span>•</span>
                    <span className="text-xs bg-gray-200 px-2 py-1 rounded-full">{timeAgo}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={booking.status}>{booking.status.replace('_', ' ')}</StatusBadge>
                  <span className="text-sm font-medium text-gray-900">${booking.total_cost}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
