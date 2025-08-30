import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/Header'
import Footer from '../components/Footer'
import SessionStatus from '../components/SessionStatus'
import { getCurrentUser, setCurrentUser, logout } from '../lib/auth'
import { DEMO_BOOKINGS, DEMO_CARS } from '../lib/demo-data'
import type { Profile, Booking } from '../lib/types'

function ProfilePage() {
  const navigate = useNavigate()
  const [user, setUser] = useState<Profile | null>(null)
  const [userBookings, setUserBookings] = useState<Booking[]>([])
  const [activeTab, setActiveTab] = useState<'profile' | 'bookings' | 'settings'>('profile')
  const [editMode, setEditMode] = useState(false)
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: ''
  })

  useEffect(() => {
    const currentUser = getCurrentUser()
    if (!currentUser) {
      navigate('/login')
      return
    }
    setUser(currentUser)
    setFormData({
      first_name: currentUser.first_name || '',
      last_name: currentUser.last_name || '',
      phone: currentUser.phone || ''
    })

    // Get user's bookings
    const bookings = DEMO_BOOKINGS.filter(b => b.user_id === currentUser.id)
    setUserBookings(bookings)
  }, [navigate])

  const handleSaveProfile = () => {
    if (!user) return
    
    const updatedUser = {
      ...user,
      first_name: formData.first_name,
      last_name: formData.last_name,
      phone: formData.phone,
      updated_at: new Date().toISOString()
    }
    
    setCurrentUser(updatedUser)
    setUser(updatedUser)
    setEditMode(false)
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const getBookingStatusColor = (status: string) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-green-100 text-green-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-gray-100 text-gray-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'
  }

  if (!user) {
    return (
      <main className="min-h-screen flex flex-col bg-white">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-slate-600">Loading...</p>
          </div>
        </div>
        <Footer />
      </main>
    )
  }

  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Header />
      
      <div className="flex-1">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <h1 className="text-3xl font-semibold text-slate-900 mb-2">My Account</h1>
              <p className="text-slate-600">Manage your profile and rental history</p>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-200 mb-8">
              {[
                { key: 'profile', label: 'Profile' },
                { key: 'bookings', label: 'My Bookings' },
                { key: 'settings', label: 'Settings' }
              ].map(tab => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`px-6 py-3 border-b-2 font-medium text-sm transition ${
                    activeTab === tab.key
                      ? 'border-sky-500 text-sky-600'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="bg-white border rounded-lg p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-slate-900">Profile Information</h2>
                  <button
                    onClick={() => editMode ? handleSaveProfile() : setEditMode(true)}
                    className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition"
                  >
                    {editMode ? 'Save Changes' : 'Edit Profile'}
                  </button>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      First Name
                    </label>
                    {editMode ? (
                      <input
                        type="text"
                        id="first_name"
                        name="first_name"
                        value={formData.first_name}
                        onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                        placeholder="Enter your first name"
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      />
                    ) : (
                      <p className="py-2 text-slate-900">{user.first_name || 'Not provided'}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Last Name
                    </label>
                    {editMode ? (
                      <input
                        type="text"
                        id="last_name"
                        name="last_name"
                        value={formData.last_name}
                        onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                        placeholder="Enter your last name"
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      />
                    ) : (
                      <p className="py-2 text-slate-900">{user.last_name || 'Not provided'}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Email Address
                    </label>
                    <p className="py-2 text-slate-900">{user.email}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Phone Number
                    </label>
                    {editMode ? (
                      <input
                        type="tel"
                        id="phone"
                        name="phone"
                        value={formData.phone}
                        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                        placeholder="Enter your phone number"
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      />
                    ) : (
                      <p className="py-2 text-slate-900">{user.phone || 'Not provided'}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Member Since
                    </label>
                    <p className="py-2 text-slate-900">
                      {new Date(user.created_at).toLocaleDateString()}
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">
                      Loyalty Points
                    </label>
                    <p className="py-2 text-sky-600 font-semibold">
                      {user.loyalty_points || 0} points
                    </p>
                  </div>
                </div>

                {editMode && (
                  <div className="mt-6 flex gap-4">
                    <button
                      onClick={() => setEditMode(false)}
                      className="px-4 py-2 border border-slate-200 text-slate-700 rounded-md hover:bg-slate-50 transition"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* Bookings Tab */}
            {activeTab === 'bookings' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-semibold text-slate-900">My Bookings</h2>
                  <button
                    onClick={() => navigate('/cars')}
                    className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition"
                  >
                    New Booking
                  </button>
                </div>

                {userBookings.length === 0 ? (
                  <div className="text-center py-12 bg-slate-50 rounded-lg">
                    <p className="text-slate-500 mb-4">No bookings found</p>
                    <button
                      onClick={() => navigate('/cars')}
                      className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition"
                    >
                      Book Your First Car
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {userBookings.map(booking => {
                      const car = DEMO_CARS.find(c => c.id === booking.car_id)
                      return (
                        <div key={booking.id} className="bg-white border rounded-lg p-6">
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <h3 className="text-lg font-semibold text-slate-900">
                                {car ? `${car.year} ${car.make} ${car.model}` : 'Vehicle Details'}
                              </h3>
                              <p className="text-slate-600">Booking #{booking.id}</p>
                            </div>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getBookingStatusColor(booking.status)}`}>
                              {booking.status.replace('_', ' ').toUpperCase()}
                            </span>
                          </div>

                          <div className="grid md:grid-cols-3 gap-4 text-sm">
                            <div>
                              <p className="text-slate-600">Pickup Date</p>
                              <p className="font-medium">{new Date(booking.start_date).toLocaleDateString()}</p>
                            </div>
                            <div>
                              <p className="text-slate-600">Return Date</p>
                              <p className="font-medium">{new Date(booking.end_date).toLocaleDateString()}</p>
                            </div>
                            <div>
                              <p className="text-slate-600">Total Cost</p>
                              <p className="font-medium text-sky-600">${booking.total_cost}</p>
                            </div>
                          </div>

                          <div className="mt-4 flex gap-2">
                            <button className="px-3 py-1 text-sm border border-slate-200 rounded hover:bg-slate-50 transition">
                              View Details
                            </button>
                            {booking.status === 'pending' && (
                              <button className="px-3 py-1 text-sm text-red-600 border border-red-200 rounded hover:bg-red-50 transition">
                                Cancel
                              </button>
                            )}
                          </div>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            )}

            {/* Settings Tab */}
            {activeTab === 'settings' && (
              <div className="bg-white border rounded-lg p-6">
                <h2 className="text-xl font-semibold text-slate-900 mb-6">Account Settings</h2>
                
                <div className="space-y-6">
                  <div className="border-b border-slate-200 pb-4">
                    <h3 className="text-lg font-medium text-slate-900 mb-2">Session Information</h3>
                    <p className="text-slate-600 mb-4">View your current session details</p>
                    <SessionStatus showDetails={true} />
                  </div>

                  <div className="border-b border-slate-200 pb-4">
                    <h3 className="text-lg font-medium text-slate-900 mb-2">Password</h3>
                    <p className="text-slate-600 mb-4">Update your password to keep your account secure</p>
                    <button className="px-4 py-2 border border-slate-200 text-slate-700 rounded-md hover:bg-slate-50 transition">
                      Change Password
                    </button>
                  </div>

                  <div className="border-b border-slate-200 pb-4">
                    <h3 className="text-lg font-medium text-slate-900 mb-2">Notifications</h3>
                    <p className="text-slate-600 mb-4">Manage your email and SMS preferences</p>
                    <div className="space-y-3">
                      <label className="flex items-center">
                        <input type="checkbox" defaultChecked className="h-4 w-4 text-sky-600 focus:ring-sky-500 border-slate-300 rounded" />
                        <span className="ml-2 text-sm text-slate-700">Email notifications for bookings</span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" defaultChecked className="h-4 w-4 text-sky-600 focus:ring-sky-500 border-slate-300 rounded" />
                        <span className="ml-2 text-sm text-slate-700">SMS reminders</span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" className="h-4 w-4 text-sky-600 focus:ring-sky-500 border-slate-300 rounded" />
                        <span className="ml-2 text-sm text-slate-700">Marketing communications</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-lg font-medium text-red-900 mb-2">Danger Zone</h3>
                    <p className="text-slate-600 mb-4">Permanently delete your account and all data</p>
                    <button className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition">
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Logout */}
            <div className="mt-8 text-center">
              <button
                onClick={handleLogout}
                className="px-6 py-2 border border-slate-200 text-slate-700 rounded-md hover:bg-slate-50 transition"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}

export default ProfilePage
