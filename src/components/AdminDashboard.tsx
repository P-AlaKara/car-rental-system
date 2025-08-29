import * as React from 'react'
import { getCurrentUser, logout } from '../lib/auth'
import type { Profile } from '../lib/types'

// Import the extracted admin pages
import DashboardPage from '../pages/DashboardPage'
import BookingsPage from '../pages/BookingsPage'
import FleetPage from '../pages/FleetPage'
import UsersPage from '../pages/UsersPage'
import DriversPage from '../pages/DriversPage'
import PaymentsPage from '../pages/PaymentsPage'
import MaintenancePage from '../pages/MaintenancePage'
import ReportsPage from '../pages/ReportsPage'

// Sidebar component
const AdminSidebar = ({ isOpen, activeSection, onSectionChange, user }: { 
  isOpen: boolean; 
  activeSection: string; 
  onSectionChange: (section: string) => void;
  user: Profile | null;
}) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'bookings', label: 'Bookings', icon: '📅' },
    { id: 'fleet', label: 'Fleet Management', icon: '🚗' },
    ...(user?.role === 'superAdmin' ? [{ id: 'users', label: 'Users', icon: '👥' }] : []),
    // { id: 'drivers', label: 'Driver Profiles', icon: '🪪' },
    { id: 'payments', label: 'Payments', icon: '💳' },
    { id: 'maintenance', label: 'Maintenance', icon: '🔧' },
    { id: 'reports', label: 'Reports', icon: '📈' },
  ]

  return (
    <div className={`bg-slate-900 text-white h-full transition-all duration-300 ${isOpen ? 'w-64' : 'w-16'}`}>
      <div className="p-4">
        {/* Logo */}
        <button
          onClick={() => onSectionChange('dashboard')}
          className="flex items-center gap-3 mb-4 w-full hover:opacity-80 transition-opacity"
        >
          <img 
            src="/images/logo.jpg" 
            alt="Aurora Motors Logo" 
            className={`rounded-lg object-cover ${isOpen ? 'w-12 h-12' : 'w-8 h-8'}`}
          />
          {isOpen && (
            <span className="text-white font-semibold text-lg">Smart Car Rentals</span>
          )}
        </button>
        
        {/* User Info */}
        {isOpen && user && (
          <div className="text-center mb-6 pb-4 border-b border-slate-700">
            <div className="text-sm font-medium text-white">
              {user.first_name} {user.last_name}
            </div>
            <div className="text-xs text-slate-400 mt-1 capitalize">
              {user.role}
            </div>
          </div>
        )}
      </div>
      
      <nav className="mt-8">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onSectionChange(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-slate-800 transition-colors ${
              activeSection === item.id ? 'bg-slate-800 border-r-2 border-sky-500' : ''
            }`}
          >
            <span className="text-xl">{item.icon}</span>
            {isOpen && <span className="text-sm">{item.label}</span>}
          </button>
        ))}
      </nav>
    </div>
  )
}

// Top navigation bar
const AdminTopBar = ({ user, onToggleSidebar }: { user: Profile | null; onToggleSidebar: () => void }) => {
  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  if (!user) return null

  return (
    <div className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex justify-between items-center">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-md hover:bg-gray-100"
        >
          <span className="text-xl">☰</span>
        </button>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-sky-100 rounded-full flex items-center justify-center">
              <span className="text-sky-700 font-medium text-sm">
                {user.first_name?.[0] || user.email[0].toUpperCase()}
              </span>
            </div>
            <span className="text-sm text-gray-700">{user.first_name} {user.last_name}</span>
          </div>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 text-sm bg-slate-600 text-white rounded-md hover:bg-slate-700"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  )
}

const AdminDashboard = () => {
  const [user, setUser] = React.useState<Profile | null>(null)
  const [sidebarOpen, setSidebarOpen] = React.useState(true)
  const [activeSection, setActiveSection] = React.useState('dashboard')

  React.useEffect(() => {
    const currentUser = getCurrentUser()
    if (!currentUser || (currentUser.role !== 'admin' && currentUser.role !== 'superAdmin')) {
      window.location.href = '/login'
      return
    }
    setUser(currentUser)
  }, [])

  // Collapse sidebar on small screens for responsiveness
  React.useEffect(() => {
    if (typeof window !== 'undefined') {
      if (window.innerWidth < 1024) setSidebarOpen(false)
    }
  }, [])

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return <DashboardPage />
      case 'bookings':
        return <BookingsPage />
      case 'fleet':
        return <FleetPage />
      case 'users':
        return <UsersPage />
      case 'drivers':
        return <DriversPage />
      case 'payments':
        return <PaymentsPage />
      case 'maintenance':
        return <MaintenancePage />
      case 'reports':
        return <ReportsPage />
      default:
        return <DashboardPage />
    }
  }

  if (!user) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <AdminSidebar 
        isOpen={sidebarOpen} 
        activeSection={activeSection} 
        onSectionChange={setActiveSection}
        user={user}
      />
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top navigation */}
        <AdminTopBar 
          user={user} 
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} 
        />
        
        {/* Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">
                {activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}
              </h1>
              <div className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleString()}
              </div>
            </div>
            {renderContent()}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
