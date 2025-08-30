import * as React from 'react'
import { getCurrentUser, logout } from '../lib/auth'
import type { Profile } from '../lib/types'

// Import the extracted admin pages
import DashboardPageReal from '../pages/DashboardPageReal'
import BookingsPageReal from '../pages/BookingsPageReal'
import FleetPage from '../pages/FleetPage'
import UsersPage from '../pages/UsersPage'
import DriversPage from '../pages/DriversPage'
import PaymentsPage from '../pages/PaymentsPage'
import MaintenancePage from '../pages/MaintenancePage'
import ReportsPage from '../pages/ReportsPage'
import AdminProfilePage from '../pages/AdminProfilePage'

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
    // { id: 'payments', label: 'Payments', icon: '💳' },
    { id: 'maintenance', label: 'Maintenance', icon: '🔧' },
    { id: 'reports', label: 'Reports', icon: '📈' },
    { id: 'profile', label: 'Profile', icon: '👤' },
  ]

  const handleLogout = () => {
    // Clear the stored admin section on logout
    localStorage.removeItem('admin_active_section')
    logout()
    window.location.href = '/login'
  }

  return (
    <div className={`bg-slate-900 text-white h-full transition-all duration-300 flex flex-col ${isOpen ? 'w-64' : 'w-16'}`}>
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
      
      {/* Navigation Menu - Flex grow to push logout to bottom */}
      <nav className="flex-1 mt-8">
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

      {/* Logout Button at Bottom */}
      <div className="p-4 border-t border-slate-700">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-red-600 transition-colors rounded-md bg-red-500"
        >
          <span className="text-xl">🚪</span>
          {isOpen && <span className="text-sm">Logout</span>}
        </button>
      </div>
    </div>
  )
}

// Top navigation bar
const AdminTopBar = ({ 
  user, 
  onToggleSidebar, 
  onSectionChange 
}: { 
  user: Profile | null; 
  onToggleSidebar: () => void;
  onSectionChange: (section: string) => void;
}) => {
  const [dropdownOpen, setDropdownOpen] = React.useState(false)
  const dropdownRef = React.useRef<HTMLDivElement>(null)

  // Close dropdown when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = () => {
    // Clear the stored admin section on logout
    localStorage.removeItem('admin_active_section')
    logout()
    window.location.href = '/login'
  }

  const handleProfileClick = () => {
    setDropdownOpen(false)
    onSectionChange('profile')
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
          <div className="relative" ref={dropdownRef}>
            {/* Clickable User Icon */}
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-3 p-2 rounded-md hover:bg-gray-100 transition-colors"
            >
              <div className="w-8 h-8 bg-sky-100 rounded-full flex items-center justify-center">
                <span className="text-sky-700 font-medium text-sm">
                  {user.first_name?.[0] || user.email[0].toUpperCase()}
                </span>
              </div>
              <span className="text-sm text-gray-700">{user.first_name} {user.last_name}</span>
              <span className={`text-gray-400 transition-transform ${dropdownOpen ? 'rotate-180' : ''}`}>
                ▼
              </span>
            </button>

            {/* Dropdown Menu */}
            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50">
                <div className="py-1">
                  <button
                    onClick={handleProfileClick}
                    className="flex items-center gap-3 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                  >
                    <span className="text-sky-600">👤</span>
                    View Profile
                  </button>
                  <hr className="my-1 border-gray-200" />
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <span>🚪</span>
                    Logout
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

const AdminDashboard = () => {
  const [user, setUser] = React.useState<Profile | null>(null)
  const [sidebarOpen, setSidebarOpen] = React.useState(true)
  
  // Initialize activeSection from localStorage or default to 'dashboard'
  const [activeSection, setActiveSection] = React.useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('admin_active_section') || 'dashboard'
    }
    return 'dashboard'
  })

  // Save activeSection to localStorage whenever it changes
  const handleSectionChange = (section: string) => {
    setActiveSection(section)
    localStorage.setItem('admin_active_section', section)
  }

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
        return <DashboardPageReal onSectionChange={handleSectionChange} />
      case 'bookings':
        return <BookingsPageReal />
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
      case 'profile':
        return <AdminProfilePage />
      default:
        return <DashboardPageReal />
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
        onSectionChange={handleSectionChange}
        user={user}
      />
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top navigation */}
        <AdminTopBar 
          user={user} 
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          onSectionChange={handleSectionChange}
        />
        
        {/* Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-6">
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-900">
                {activeSection === 'profile' ? 'Profile' : activeSection.charAt(0).toUpperCase() + activeSection.slice(1)}
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
