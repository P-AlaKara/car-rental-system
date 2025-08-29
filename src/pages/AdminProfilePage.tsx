import * as React from 'react'
import { getCurrentUser } from '../lib/auth'

// Define the API response structure based on the provided examples
interface ProfileApiResponse {
  status: string
  message: string
  data: {
    user: {
      id: number
      first_name: string
      last_name: string
      email: string
      phone: string
      role: 'admin' | 'superAdmin'
      loyalty_points: number
      is_active: boolean
      created_at: string
      updated_at: string
      agency: {
        id: number
        name: string
        location: string
        postal_code: string
        contact: string
        email: string
        is_active: boolean
        created_at: string
        updated_at: string
      }
    }
  }
}

const AdminProfilePage = () => {
  const [profileData, setProfileData] = React.useState<ProfileApiResponse['data']['user'] | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  React.useEffect(() => {
    fetchProfile()
  }, [])

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const currentUser = getCurrentUser()
      
      if (!currentUser) {
        setError('Not authenticated')
        return
      }

      const token = localStorage.getItem('am_token')
      if (!token) {
        setError('No authentication token found')
        return
      }

      const response = await fetch('https://4043f016f021.ngrok-free.app/api/v1/auth/profile', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'ngrok-skip-browser-warning': 'true',
          'Authorization': `Bearer ${token}`
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: ProfileApiResponse = await response.json()
      
      if (data.status === 'success' && data.data?.user) {
        setProfileData(data.data.user)
      } else {
        throw new Error(data.message || 'Failed to fetch profile')
      }
    } catch (err) {
      console.error('Profile fetch error:', err)
      setError(err instanceof Error ? err.message : 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading profile...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <span className="text-red-500 text-2xl">⚠️</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error Loading Profile</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
        <div className="mt-4">
          <button
            onClick={fetchProfile}
            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition text-sm"
          >
            Try Again
          </button>
        </div>
      </div>
    )
  }

  if (!profileData) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
        <p className="text-yellow-800">No profile data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <div className="bg-gradient-to-r from-sky-600 to-sky-700 rounded-lg p-6 text-white">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
            <span className="text-2xl font-bold">
              {profileData.first_name?.[0] || profileData.email[0].toUpperCase()}
            </span>
          </div>
          <div>
            <h1 className="text-2xl font-bold">
              {profileData.first_name} {profileData.last_name}
            </h1>
            <p className="text-sky-100 capitalize">{profileData.role}</p>
            <p className="text-sky-200 text-sm">{profileData.email}</p>
          </div>
        </div>
      </div>

      {/* Profile Information */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Personal Information */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <span className="text-sky-600">👤</span>
            Personal Information
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">First Name</label>
              <p className="text-slate-900 font-medium">{profileData.first_name}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Last Name</label>
              <p className="text-slate-900 font-medium">{profileData.last_name}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Email Address</label>
              <p className="text-slate-900 font-medium">{profileData.email}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Phone Number</label>
              <p className="text-slate-900 font-medium">{profileData.phone || 'Not provided'}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Role</label>
              <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium capitalize ${
                profileData.role === 'superAdmin' 
                  ? 'bg-purple-100 text-purple-800' 
                  : 'bg-blue-100 text-blue-800'
              }`}>
                {profileData.role === 'superAdmin' ? 'Super Admin' : 'Admin'}
              </span>
            </div>
          </div>
        </div>

        {/* Agency Information */}
        <div className="bg-white rounded-lg border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <span className="text-sky-600">🏢</span>
            Agency Information
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Agency Name</label>
              <p className="text-slate-900 font-medium">{profileData.agency.name}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Location</label>
              <p className="text-slate-900 font-medium">{profileData.agency.location}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Postal Code</label>
              <p className="text-slate-900 font-medium">{profileData.agency.postal_code}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Contact</label>
              <p className="text-slate-900 font-medium">{profileData.agency.contact}</p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Agency Email</label>
              <p className="text-slate-900 font-medium">{profileData.agency.email}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Status</label>
              <span className={`inline-flex px-3 py-1 rounded-full text-xs font-medium ${
                profileData.agency.is_active 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {profileData.agency.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Account Status */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <span className="text-sky-600">📊</span>
          Account Status
        </h2>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-slate-50 rounded-lg">
            <div className="text-2xl font-bold text-sky-600">{profileData.loyalty_points}</div>
            <div className="text-sm text-slate-600">Loyalty Points</div>
          </div>
          
          <div className="text-center p-4 bg-slate-50 rounded-lg">
            <div className={`text-2xl font-bold ${profileData.is_active ? 'text-green-600' : 'text-red-600'}`}>
              {profileData.is_active ? 'Active' : 'Inactive'}
            </div>
            <div className="text-sm text-slate-600">Account Status</div>
          </div>
          
          <div className="text-center p-4 bg-slate-50 rounded-lg">
            <div className="text-2xl font-bold text-slate-600">
              {new Date(profileData.created_at).toLocaleDateString()}
            </div>
            <div className="text-sm text-slate-600">Member Since</div>
          </div>
        </div>
      </div>

      {/* Account Activity */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <span className="text-sky-600">🕒</span>
          Account Activity
        </h2>
        
        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center py-2 border-b border-slate-100">
            <span className="text-slate-600">Account Created</span>
            <span className="font-medium">{new Date(profileData.created_at).toLocaleString()}</span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b border-slate-100">
            <span className="text-slate-600">Last Updated</span>
            <span className="font-medium">{new Date(profileData.updated_at).toLocaleString()}</span>
          </div>
          
          <div className="flex justify-between items-center py-2">
            <span className="text-slate-600">Agency Since</span>
            <span className="font-medium">{new Date(profileData.agency.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="bg-white rounded-lg border border-slate-200 p-6">
        <h2 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <span className="text-sky-600">⚙️</span>
          Account Actions
        </h2>
        
        <div className="flex flex-wrap gap-3">
          <button 
            onClick={fetchProfile}
            className="px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition text-sm"
          >
            Refresh Profile
          </button>
          
          <button className="px-4 py-2 border border-slate-200 text-slate-700 rounded-md hover:bg-slate-50 transition text-sm">
            Edit Profile
          </button>
          
          <button className="px-4 py-2 border border-slate-200 text-slate-700 rounded-md hover:bg-slate-50 transition text-sm">
            Change Password
          </button>
        </div>
      </div>
    </div>
  )
}

export default AdminProfilePage
