import * as React from 'react'
import { getUsers, createAdminUser, getAgencies, createAgency, updateAgency, toggleAgencyStatus, deleteAgency, type ApiUser, type Agency, type CreateUserRequest, type CreateAgencyRequest } from '../lib/api'
import { getCurrentUser } from '../lib/auth'

const UsersPage = () => {
  const [users, setUsers] = React.useState<ApiUser[]>([])
  const [agencies, setAgencies] = React.useState<Agency[]>([])
  const [searchTerm, setSearchTerm] = React.useState('')
  const [selectedUser, setSelectedUser] = React.useState<ApiUser | null>(null)
  const [isDetailModalOpen, setIsDetailModalOpen] = React.useState(false)
  const [isCreateUserModalOpen, setIsCreateUserModalOpen] = React.useState(false)
  const [isCreateAgencyModalOpen, setIsCreateAgencyModalOpen] = React.useState(false)
  const [isEditAgencyModalOpen, setIsEditAgencyModalOpen] = React.useState(false)
  const [selectedAgency, setSelectedAgency] = React.useState<Agency | null>(null)
  const [loading, setLoading] = React.useState(true)
  const [activeTab, setActiveTab] = React.useState<'users' | 'agencies'>('users')
  const [roleFilter, setRoleFilter] = React.useState<'all' | 'customer' | 'admin' | 'superAdmin'>('all')

  // User form state
  const [userForm, setUserForm] = React.useState<CreateUserRequest>({
    first_name: '',
    last_name: '',
    agency_id: 0,
    phone: '',
    email: '',
    password: ''
  })

  // Agency form state
  const [agencyForm, setAgencyForm] = React.useState<CreateAgencyRequest>({
    name: '',
    location: '',
    postal_code: '',
    contact: '',
    email: '',
    is_active: true
  })

  React.useEffect(() => {
    const user = getCurrentUser()
    if (!user || user.role !== 'superAdmin') {
      window.location.href = '/admin'
      return
    }
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [usersResponse, agenciesResponse] = await Promise.all([
        getUsers(),
        getAgencies()
      ])
      setUsers(usersResponse.data)
      setAgencies(agenciesResponse.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredUsers = React.useMemo(() => {
    return users.filter(user => {
      const searchText = `${user.first_name} ${user.last_name} ${user.email}`.toLowerCase()
      const matchesSearch = searchText.includes(searchTerm.toLowerCase())
      const matchesRole = roleFilter === 'all' || user.role === roleFilter
      return matchesSearch && matchesRole
    }).sort((a, b) => {
      // Sort by role priority: superAdmin > admin > customer
      const rolePriority = { superAdmin: 3, admin: 2, customer: 1 }
      return rolePriority[b.role] - rolePriority[a.role]
    })
  }, [users, searchTerm, roleFilter])

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createAdminUser(userForm)
      setIsCreateUserModalOpen(false)
      setUserForm({
        first_name: '',
        last_name: '',
        agency_id: 0,
        phone: '',
        email: '',
        password: ''
      })
      fetchData()
      console.log('✅ Admin user created successfully')
    } catch (error) {
      console.error('Failed to create user:', error)
    }
  }

  const handleCreateAgency = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createAgency(agencyForm)
      setIsCreateAgencyModalOpen(false)
      setAgencyForm({
        name: '',
        location: '',
        postal_code: '',
        contact: '',
        email: '',
        is_active: true
      })
      fetchData()
      console.log('✅ Agency created successfully')
    } catch (error) {
      console.error('Failed to create agency:', error)
    }
  }

  const handleUpdateAgency = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAgency) return
    
    try {
      await updateAgency(selectedAgency.id, agencyForm)
      setIsEditAgencyModalOpen(false)
      setSelectedAgency(null)
      setAgencyForm({
        name: '',
        location: '',
        postal_code: '',
        contact: '',
        email: '',
        is_active: true
      })
      fetchData()
      console.log('✅ Agency updated successfully')
    } catch (error) {
      console.error('Failed to update agency:', error)
    }
  }

  const handleToggleAgencyStatus = async (agencyId: number) => {
    try {
      await toggleAgencyStatus(agencyId)
      fetchData()
      console.log('✅ Agency status updated')
    } catch (error) {
      console.error('Failed to toggle agency status:', error)
    }
  }

  const handleDeleteAgency = async (agencyId: number) => {
    if (!confirm('Are you sure you want to delete this agency? This action cannot be undone.')) {
      return
    }
    
    try {
      await deleteAgency(agencyId)
      fetchData()
      console.log('✅ Agency deleted successfully')
    } catch (error) {
      console.error('Failed to delete agency:', error)
    }
  }

  const openEditAgency = (agency: Agency) => {
    setSelectedAgency(agency)
    setAgencyForm({
      name: agency.name,
      location: agency.location,
      postal_code: agency.postal_code,
      contact: agency.contact,
      email: agency.email,
      is_active: agency.is_active
    })
    setIsEditAgencyModalOpen(true)
  }

  const getUserStats = () => {
    const adminUsers = users.filter(u => u.role === 'admin')
    const customerUsers = users.filter(u => u.role === 'customer')
    const superAdminUsers = users.filter(u => u.role === 'superAdmin')
    
    return {
      total: users.length,
      customers: customerUsers.length,
      admins: adminUsers.length,
      superAdmins: superAdminUsers.length,
      activeAgencies: agencies.filter(a => a.is_active).length,
      totalAgencies: agencies.length
    }
  }

  const stats = getUserStats()

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-600 mx-auto"></div>
          <p className="text-slate-600 mt-4">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">System Management</h2>
          <p className="text-gray-600">Manage users and agencies</p>
        </div>
        <div className="flex gap-2">
          {activeTab === 'users' && (
            <button 
              onClick={() => setIsCreateUserModalOpen(true)}
              className="bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Admin User
            </button>
          )}
          {activeTab === 'agencies' && (
            <button 
              onClick={() => setIsCreateAgencyModalOpen(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Agency
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('users')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-sky-500 text-sky-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Users ({stats.total})
          </button>
          <button
            onClick={() => setActiveTab('agencies')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'agencies'
                ? 'border-sky-500 text-sky-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Agencies ({stats.totalAgencies})
          </button>
        </nav>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-gray-900">{stats.total}</div>
          <div className="text-sm text-gray-600">Total Users</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-blue-600">{stats.customers}</div>
          <div className="text-sm text-gray-600">Customers</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-green-600">{stats.admins}</div>
          <div className="text-sm text-gray-600">Admins</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-purple-600">{stats.superAdmins}</div>
          <div className="text-sm text-gray-600">Super Admins</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-orange-600">{stats.totalAgencies}</div>
          <div className="text-sm text-gray-600">Total Agencies</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="text-2xl font-bold text-emerald-600">{stats.activeAgencies}</div>
          <div className="text-sm text-gray-600">Active Agencies</div>
        </div>
      </div>

      {/* Content based on active tab */}
      {activeTab === 'users' ? (
        <>
          {/* Search and Filters */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex gap-4 items-center">
              <div className="flex-1">
                <div className="relative">
                  <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  <input
                    type="text"
                    placeholder="Search users by name or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  />
                </div>
              </div>
              <select
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value as any)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-sky-500"
              >
                <option value="all">All Roles</option>
                <option value="superAdmin">Super Admin</option>
                <option value="admin">Admin</option>
                <option value="customer">Customer</option>
              </select>
            </div>
          </div>

          {/* Users Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredUsers.map((user) => (
              <div key={user.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                <div className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-medium ${
                      user.role === 'superAdmin' ? 'bg-gradient-to-r from-purple-500 to-pink-600' :
                      user.role === 'admin' ? 'bg-gradient-to-r from-blue-500 to-cyan-600' :
                      'bg-gradient-to-r from-green-500 to-teal-600'
                    }`}>
                      {user.first_name.charAt(0)}{user.last_name.charAt(0)}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-sm text-gray-500 truncate">{user.email}</p>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${
                      user.role === 'superAdmin' ? 'bg-purple-100 text-purple-800' :
                      user.role === 'admin' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {user.role}
                    </span>
                  </div>
                </div>

                <div className="mt-4">
                  {user.phone && (
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Phone:</span> {user.phone}
                    </div>
                  )}
                  {user.agency && (
                    <div className="text-sm text-gray-600 mt-1">
                      <span className="font-medium">Agency:</span> {user.agency.name}
                    </div>
                  )}
                  <div className="text-sm text-gray-600 mt-1">
                    <span className="font-medium">Joined:</span> {new Date(user.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="mt-4 flex space-x-2">
                  <button
                    onClick={() => {
                      setSelectedUser(user)
                      setIsDetailModalOpen(true)
                    }}
                    className="flex-1 bg-sky-50 text-sky-700 py-2 px-3 rounded-lg text-sm hover:bg-sky-100 transition-colors"
                  >
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>

          {filteredUsers.length === 0 && (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
              <p className="mt-1 text-sm text-gray-500">Try adjusting your search criteria.</p>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Agencies List */}
          <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Location</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contact</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {agencies.map((agency) => (
                    <tr key={agency.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{agency.name}</div>
                        <div className="text-sm text-gray-500">{agency.email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{agency.location}</div>
                        <div className="text-sm text-gray-500">{agency.postal_code}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {agency.contact}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          agency.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {agency.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex gap-2">
                          <button
                            onClick={() => openEditAgency(agency)}
                            className="text-sky-600 hover:text-sky-900"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleToggleAgencyStatus(agency.id)}
                            className="text-yellow-600 hover:text-yellow-900"
                          >
                            {agency.is_active ? 'Disable' : 'Enable'}
                          </button>
                          <button
                            onClick={() => handleDeleteAgency(agency.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {agencies.length === 0 && (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No agencies found</h3>
                <p className="mt-1 text-sm text-gray-500">Create your first agency to get started.</p>
              </div>
            )}
          </div>
        </>
      )}

      {/* User Detail Modal */}
      {isDetailModalOpen && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">User Details</h3>
                <button
                  onClick={() => setIsDetailModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center text-white font-medium text-xl ${
                    selectedUser.role === 'superAdmin' ? 'bg-gradient-to-r from-purple-500 to-pink-600' :
                    selectedUser.role === 'admin' ? 'bg-gradient-to-r from-blue-500 to-cyan-600' :
                    'bg-gradient-to-r from-green-500 to-teal-600'
                  }`}>
                    {selectedUser.first_name.charAt(0)}{selectedUser.last_name.charAt(0)}
                  </div>
                  <div>
                    <h4 className="text-xl font-medium text-gray-900">
                      {selectedUser.first_name} {selectedUser.last_name}
                    </h4>
                    <p className="text-gray-500">{selectedUser.email}</p>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${
                      selectedUser.role === 'superAdmin' ? 'bg-purple-100 text-purple-800' :
                      selectedUser.role === 'admin' ? 'bg-blue-100 text-blue-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {selectedUser.role}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Phone</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.phone || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Status</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.is_active ? 'Active' : 'Inactive'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Agency</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedUser.agency?.name || 'No agency'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Joined</label>
                    <p className="mt-1 text-sm text-gray-900">{new Date(selectedUser.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 pt-6 border-t border-gray-200">
                <button
                  onClick={() => setIsDetailModalOpen(false)}
                  className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create User Modal */}
      {isCreateUserModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Create Admin User</h3>
                <button
                  onClick={() => setIsCreateUserModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <form onSubmit={handleCreateUser} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                    <input
                      type="text"
                      value={userForm.first_name}
                      onChange={(e) => setUserForm({ ...userForm, first_name: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                    <input
                      type="text"
                      value={userForm.last_name}
                      onChange={(e) => setUserForm({ ...userForm, last_name: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={userForm.email}
                    onChange={(e) => setUserForm({ ...userForm, email: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={userForm.phone}
                    onChange={(e) => setUserForm({ ...userForm, phone: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Agency</label>
                  <select
                    value={userForm.agency_id}
                    onChange={(e) => setUserForm({ ...userForm, agency_id: parseInt(e.target.value) })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  >
                    <option value={0}>Select an agency</option>
                    {agencies.filter(a => a.is_active).map(agency => (
                      <option key={agency.id} value={agency.id}>{agency.name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <input
                    type="password"
                    value={userForm.password}
                    onChange={(e) => setUserForm({ ...userForm, password: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                    minLength={6}
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700"
                  >
                    Create Admin User
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsCreateUserModalOpen(false)}
                    className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Create Agency Modal */}
      {isCreateAgencyModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Create Agency</h3>
                <button
                  onClick={() => setIsCreateAgencyModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <form onSubmit={handleCreateAgency} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Agency Name</label>
                  <input
                    type="text"
                    value={agencyForm.name}
                    onChange={(e) => setAgencyForm({ ...agencyForm, name: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <input
                    type="text"
                    value={agencyForm.location}
                    onChange={(e) => setAgencyForm({ ...agencyForm, location: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
                    <input
                      type="text"
                      value={agencyForm.postal_code}
                      onChange={(e) => setAgencyForm({ ...agencyForm, postal_code: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Contact</label>
                    <input
                      type="tel"
                      value={agencyForm.contact}
                      onChange={(e) => setAgencyForm({ ...agencyForm, contact: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={agencyForm.email}
                    onChange={(e) => setAgencyForm({ ...agencyForm, email: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
                  >
                    Create Agency
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsCreateAgencyModalOpen(false)}
                    className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Edit Agency Modal */}
      {isEditAgencyModalOpen && selectedAgency && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900">Edit Agency</h3>
                <button
                  onClick={() => setIsEditAgencyModalOpen(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <form onSubmit={handleUpdateAgency} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Agency Name</label>
                  <input
                    type="text"
                    value={agencyForm.name}
                    onChange={(e) => setAgencyForm({ ...agencyForm, name: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
                  <input
                    type="text"
                    value={agencyForm.location}
                    onChange={(e) => setAgencyForm({ ...agencyForm, location: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
                    <input
                      type="text"
                      value={agencyForm.postal_code}
                      onChange={(e) => setAgencyForm({ ...agencyForm, postal_code: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Contact</label>
                    <input
                      type="tel"
                      value={agencyForm.contact}
                      onChange={(e) => setAgencyForm({ ...agencyForm, contact: e.target.value })}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    value={agencyForm.email}
                    onChange={(e) => setAgencyForm({ ...agencyForm, email: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-sky-500"
                    required
                  />
                </div>
                
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={agencyForm.is_active}
                    onChange={(e) => setAgencyForm({ ...agencyForm, is_active: e.target.checked })}
                    className="mr-2"
                  />
                  <label htmlFor="is_active" className="text-sm text-gray-700">Active</label>
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 bg-sky-600 text-white px-4 py-2 rounded-lg hover:bg-sky-700"
                  >
                    Update Agency
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsEditAgencyModalOpen(false)}
                    className="flex-1 bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default UsersPage
