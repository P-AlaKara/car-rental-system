import * as React from 'react'
import { DEMO_BOOKINGS, DEMO_USERS, DEMO_CARS } from '../lib/demo-data'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

// Status badge component
const StatusBadge = ({ status, children }: { status: string; children: React.ReactNode }) => {
  const colors = {
    payment_pending: 'bg-orange-100 text-orange-800',
    invoice_sent: 'bg-blue-100 text-blue-800',
    paid: 'bg-green-100 text-green-800',
    overdue: 'bg-red-100 text-red-800',
    refunded: 'bg-gray-100 text-gray-800'
  }
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`}>
      {children}
    </span>
  )
}

const PaymentsPage = () => {
  const [searchTerm, setSearchTerm] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState('all')
  const [selectedPayment, setSelectedPayment] = React.useState<any>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = React.useState(false)

  // Transform bookings into payment records
  const paymentRecords = React.useMemo(() => {
    return DEMO_BOOKINGS.map(booking => ({
      id: `PAY-${booking.id}`,
      booking_id: booking.id,
      user_id: booking.user_id,
      car_id: booking.car_id,
      amount: booking.total_cost,
      payment_status: booking.status === 'completed' ? 'paid' : 
                     booking.status === 'confirmed' ? 'invoice_sent' :
                     booking.status === 'pending' ? 'payment_pending' : 'payment_pending',
      payment_method: ['credit_card', 'paypal', 'bank_transfer'][Math.floor(Math.random() * 3)],
      transaction_id: `TXN-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
      payment_date: booking.status === 'completed' ? booking.created_at : null,
      due_date: new Date(new Date(booking.start_date).getTime() - 24 * 60 * 60 * 1000).toISOString(),
      created_at: booking.created_at
    }))
  }, [])

  const filteredPayments = React.useMemo(() => {
    return paymentRecords
      .filter(payment => {
        const user = DEMO_USERS.find(u => u.id === payment.user_id)
        const searchText = `${user?.first_name} ${user?.last_name} ${user?.email} ${payment.id} ${payment.transaction_id}`.toLowerCase()
        
        const matchesSearch = searchTerm === '' || searchText.includes(searchTerm.toLowerCase())
        const matchesStatus = statusFilter === 'all' || payment.payment_status === statusFilter
        
        return matchesSearch && matchesStatus
      })
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
  }, [searchTerm, statusFilter, paymentRecords])

  const paymentStats = React.useMemo(() => {
    const stats = paymentRecords.reduce((acc, payment) => {
      acc.total += payment.amount
      acc.count += 1
      if (payment.payment_status === 'paid') {
        acc.paid += payment.amount
        acc.paidCount += 1
      } else if (payment.payment_status === 'payment_pending') {
        acc.pending += payment.amount
        acc.pendingCount += 1
      } else if (payment.payment_status === 'overdue') {
        acc.overdue += payment.amount
        acc.overdueCount += 1
      }
      return acc
    }, { 
      total: 0, 
      paid: 0, 
      pending: 0, 
      overdue: 0, 
      count: 0, 
      paidCount: 0, 
      pendingCount: 0, 
      overdueCount: 0 
    })
    
    return stats
  }, [paymentRecords])

  const openPaymentDetail = (payment: any) => {
    setSelectedPayment(payment)
    setIsDetailModalOpen(true)
  }

  const closePaymentDetail = () => {
    setSelectedPayment(null)
    setIsDetailModalOpen(false)
  }

  const handleStatusUpdate = (paymentId: string, newStatus: string) => {
    console.log(`Updating payment ${paymentId} status to ${newStatus}`)
    // In a real app, this would make an API call
  }

  // Chart data
  const monthlyData = [
    { month: 'Jan', revenue: 4250, transactions: 42 },
    { month: 'Feb', revenue: 3800, transactions: 38 },
    { month: 'Mar', revenue: 5200, transactions: 52 },
    { month: 'Apr', revenue: 4800, transactions: 48 },
    { month: 'May', revenue: 6100, transactions: 61 },
    { month: 'Jun', revenue: 5800, transactions: 58 }
  ]

  const paymentMethodData = [
    { name: 'Credit Card', value: 65, color: '#3b82f6' },
    { name: 'PayPal', value: 25, color: '#22c55e' },
    { name: 'Bank Transfer', value: 10, color: '#f97316' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Payments Management</h2>
          <p className="text-gray-600">Track and manage all payment transactions</p>
        </div>
        <div className="flex gap-2">
          <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            Export Report
          </button>
          <button className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700 transition-colors flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Manual Payment
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Total Revenue</dt>
                <dd className="text-lg font-medium text-gray-900">${paymentStats.total.toLocaleString()}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Payments Received</dt>
                <dd className="text-lg font-medium text-gray-900">${paymentStats.paid.toLocaleString()}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Pending Payments</dt>
                <dd className="text-lg font-medium text-gray-900">${paymentStats.pending.toLocaleString()}</dd>
              </dl>
            </div>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
            </div>
            <div className="ml-5 w-0 flex-1">
              <dl>
                <dt className="text-sm font-medium text-gray-500 truncate">Overdue</dt>
                <dd className="text-lg font-medium text-gray-900">${paymentStats.overdue.toLocaleString()}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Revenue Chart */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Revenue</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis 
                  dataKey="month" 
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
                  formatter={(value, name) => [
                    name === 'revenue' ? `$${value}` : value,
                    name === 'revenue' ? 'Revenue' : 'Transactions'
                  ]}
                />
                <Legend />
                <Bar dataKey="revenue" fill="#3b82f6" name="revenue" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Payment Methods */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Methods</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={paymentMethodData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${((percent || 0) * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {paymentMethodData.map((entry, index) => (
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
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex flex-wrap gap-4 items-center">
          <div className="flex-1 min-w-64">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search payments, customers, or transactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
              />
            </div>
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
          >
            <option value="all">All Status</option>
            <option value="payment_pending">Pending</option>
            <option value="invoice_sent">Invoice Sent</option>
            <option value="paid">Paid</option>
            <option value="overdue">Overdue</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>
      </div>

      {/* Payments Table */}
      <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Payment ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPayments.map((payment) => {
                const user = DEMO_USERS.find(u => u.id === payment.user_id)
                const isOverdue = new Date(payment.due_date) < new Date() && payment.payment_status !== 'paid'
                
                return (
                  <tr key={payment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{payment.id}</div>
                      <div className="text-sm text-gray-500">TXN: {payment.transaction_id}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user ? (
                        <div>
                          <div className="text-sm font-medium text-gray-900">{user.first_name} {user.last_name}</div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      ) : (
                        <div className="text-sm text-gray-500">User not found</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">${payment.amount.toLocaleString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={isOverdue ? 'overdue' : payment.payment_status}>
                        {isOverdue ? 'Overdue' : payment.payment_status.replace('_', ' ')}
                      </StatusBadge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {payment.payment_method.replace('_', ' ')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className={`text-sm ${isOverdue ? 'text-red-600 font-medium' : 'text-gray-900'}`}>
                        {new Date(payment.due_date).toLocaleDateString()}
                      </div>
                      {payment.payment_date && (
                        <div className="text-sm text-gray-500">
                          Paid: {new Date(payment.payment_date).toLocaleDateString()}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => openPaymentDetail(payment)}
                          className="text-sky-600 hover:text-sky-900"
                        >
                          View
                        </button>
                        {payment.payment_status !== 'paid' && (
                          <button
                            onClick={() => handleStatusUpdate(payment.id, 'paid')}
                            className="text-green-600 hover:text-green-900"
                          >
                            Mark Paid
                          </button>
                        )}
                        {payment.payment_status === 'payment_pending' && (
                          <button
                            onClick={() => handleStatusUpdate(payment.id, 'invoice_sent')}
                            className="text-blue-600 hover:text-blue-900"
                          >
                            Send Invoice
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        
        {filteredPayments.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No payments found</h3>
            <p className="mt-1 text-sm text-gray-500">Try adjusting your search or filter criteria.</p>
          </div>
        )}
      </div>

      {/* Payment Detail Modal */}
      {isDetailModalOpen && selectedPayment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Payment Details</h3>
                <button
                  onClick={closePaymentDetail}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {(() => {
                const user = DEMO_USERS.find(u => u.id === selectedPayment.user_id)
                const booking = DEMO_BOOKINGS.find(b => b.id === selectedPayment.booking_id)
                const car = DEMO_CARS.find(c => c.id === selectedPayment.car_id)
                const isOverdue = new Date(selectedPayment.due_date) < new Date() && selectedPayment.payment_status !== 'paid'
                
                return (
                  <div className="space-y-6">
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-3">Payment Information</h4>
                        <div className="space-y-2">
                          <div>
                            <span className="text-sm text-gray-500">Payment ID:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedPayment.id}</span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Transaction ID:</span>
                            <span className="ml-2 text-sm text-gray-900">{selectedPayment.transaction_id}</span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Amount:</span>
                            <span className="ml-2 text-sm font-medium text-gray-900">${selectedPayment.amount.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Status:</span>
                            <span className="ml-2">
                              <StatusBadge status={isOverdue ? 'overdue' : selectedPayment.payment_status}>
                                {isOverdue ? 'Overdue' : selectedPayment.payment_status.replace('_', ' ')}
                              </StatusBadge>
                            </span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Payment Method:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {selectedPayment.payment_method.replace('_', ' ')}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-3">Customer Information</h4>
                        <div className="space-y-2">
                          <div>
                            <span className="text-sm text-gray-500">Name:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {user ? `${user.first_name} ${user.last_name}` : 'User not found'}
                            </span>
                          </div>
                          <div>
                            <span className="text-sm text-gray-500">Email:</span>
                            <span className="ml-2 text-sm text-gray-900">{user?.email || 'N/A'}</span>
                          </div>
                          {user?.phone && (
                            <div>
                              <span className="text-sm text-gray-500">Phone:</span>
                              <span className="ml-2 text-sm text-gray-900">{user.phone}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Booking Details</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-sm text-gray-500">Booking ID:</span>
                          <span className="ml-2 text-sm text-gray-900">#{selectedPayment.booking_id}</span>
                        </div>
                        <div>
                          <span className="text-sm text-gray-500">Vehicle:</span>
                          <span className="ml-2 text-sm text-gray-900">
                            {car ? `${car.year} ${car.make} ${car.model}` : 'Car not found'}
                          </span>
                        </div>
                        {booking && (
                          <>
                            <div>
                              <span className="text-sm text-gray-500">Start Date:</span>
                              <span className="ml-2 text-sm text-gray-900">
                                {new Date(booking.start_date).toLocaleDateString()}
                              </span>
                            </div>
                            <div>
                              <span className="text-sm text-gray-500">End Date:</span>
                              <span className="ml-2 text-sm text-gray-900">
                                {new Date(booking.end_date).toLocaleDateString()}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-3">Payment Timeline</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-sm text-gray-500">Due Date:</span>
                          <span className={`ml-2 text-sm ${isOverdue ? 'text-red-600 font-medium' : 'text-gray-900'}`}>
                            {new Date(selectedPayment.due_date).toLocaleDateString()}
                          </span>
                        </div>
                        {selectedPayment.payment_date && (
                          <div>
                            <span className="text-sm text-gray-500">Payment Date:</span>
                            <span className="ml-2 text-sm text-gray-900">
                              {new Date(selectedPayment.payment_date).toLocaleDateString()}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex gap-3 pt-4 border-t border-gray-200">
                      {selectedPayment.payment_status !== 'paid' && (
                        <button
                          onClick={() => handleStatusUpdate(selectedPayment.id, 'paid')}
                          className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                        >
                          Mark as Paid
                        </button>
                      )}
                      {selectedPayment.payment_status === 'payment_pending' && (
                        <button
                          onClick={() => handleStatusUpdate(selectedPayment.id, 'invoice_sent')}
                          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                        >
                          Send Invoice
                        </button>
                      )}
                      <button
                        onClick={closePaymentDetail}
                        className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                      >
                        Close
                      </button>
                    </div>
                  </div>
                )
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PaymentsPage
