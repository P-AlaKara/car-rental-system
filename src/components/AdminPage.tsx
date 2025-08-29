import * as React from 'react'
import { getCurrentUser } from '../lib/auth'
import type { Profile } from '../lib/types'
import AdminDashboard from './AdminDashboard'

const AdminPage = () => {
  const [user, setUser] = React.useState<Profile | null>(null)
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const currentUser = getCurrentUser()
    setUser(currentUser)
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-slate-600">Loading...</div>
      </div>
    )
  }

  if (!user || (user.role !== 'admin' && user.role !== 'superAdmin')) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-semibold text-slate-900 mb-2">Access Denied</h1>
          <p className="text-slate-600">You need admin privileges to access this page.</p>
          <a href="/" className="mt-4 inline-block px-4 py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700">
            Go Home
          </a>
        </div>
      </div>
    )
  }

  return <AdminDashboard />
}

export default AdminPage
