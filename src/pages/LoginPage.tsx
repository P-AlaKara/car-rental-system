import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import Header from '../components/Header'
import Footer from '../components/Footer'
import { login } from '../lib/auth'

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  // Handle prefilled data from registration and return URL
  useEffect(() => {
    if (location.state) {
      const { email, password, message, from } = location.state as { 
        email?: string, 
        password?: string, 
        message?: string,
        from?: { pathname: string }
      }
      
      if (email) setFormData(prev => ({ ...prev, email }))
      if (password) setFormData(prev => ({ ...prev, password }))
      if (message) {
        setSuccessMessage(message)
        console.log('✅ Registration redirect message:', message)
      }
      
      // Clear the location state to prevent showing message on refresh
      window.history.replaceState({}, document.title)
    }
  }, [location.state])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const profile = await login(formData.email, formData.password)
      
      console.log('🎯 Login successful, navigating based on role:', profile.role)
      
      // Check if there's a return URL from protected route
      const returnUrl = location.state?.from?.pathname
      
      if (returnUrl) {
        console.log('➡️ Navigating to return URL:', returnUrl)
        navigate(returnUrl)
      } else {
        // Navigate based on user role
        if (profile.role === 'customer') {
          console.log('➡️ Navigating to customer dashboard (profile page)')
          navigate('/profile')
        } else if (profile.role === 'admin' || profile.role === 'superAdmin') {
          console.log('➡️ Navigating to admin dashboard')
          navigate('/admin')
        } else {
          console.log('➡️ Unknown role, navigating to profile page')
          navigate('/profile')
        }
      }
    } catch (err) {
      console.error('❌ Login failed:', err)
      setError(err instanceof Error ? err.message : 'An error occurred during login')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }

  return (
    <main className="min-h-screen flex flex-col bg-white">
      <Header />
      
      <div className="flex-1 flex items-center justify-center py-12">
        <div className="w-full max-w-md px-4">
          <div className="bg-white border rounded-lg p-8 shadow-sm">
            <div className="text-center mb-8">
              <div className="flex items-center justify-between mb-4">
                <button
                  onClick={() => navigate('/')}
                  className="flex items-center gap-2 text-sm text-slate-600 hover:text-sky-700 transition"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                  </svg>
                  Back to Homepage
                </button>
              </div>
              <h1 className="text-2xl font-semibold text-slate-900 mb-2">Welcome Back</h1>
              <p className="text-slate-600">Sign in to your account</p>
            </div>

            {successMessage && (
              <div className="bg-green-50 border border-green-200 rounded-md p-3 mb-6">
                <p className="text-green-700 text-sm">{successMessage}</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-6">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                  placeholder="Enter your email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    required
                    className="w-full px-3 py-2 pr-10 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                    placeholder="Enter your password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-600"
                  >
                    {showPassword ? (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L8.464 8.464M14.12 14.12l1.415 1.415" />
                      </svg>
                    ) : (
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="remember"
                    className="h-4 w-4 text-sky-600 focus:ring-sky-500 border-slate-300 rounded"
                  />
                  <label htmlFor="remember" className="ml-2 block text-sm text-slate-700">
                    Remember me
                  </label>
                </div>
                <button
                  type="button"
                  className="text-sm text-sky-600 hover:text-sky-700"
                >
                  Forgot password?
                </button>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-2 bg-sky-600 text-white rounded-md hover:bg-sky-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-slate-600">
                Don't have an account?{' '}
                <button
                  onClick={() => navigate('/register')}
                  className="text-sky-600 hover:text-sky-700 font-medium"
                >
                  Sign up
                </button>
              </p>
            </div>

            {/* Demo Account Info */}
            {/* <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <h3 className="text-sm font-medium text-blue-900 mb-2">Demo Account</h3>
              <p className="text-xs text-blue-700 mb-2">Use these credentials to explore:</p>
              <div className="text-xs text-blue-800 space-y-1">
                <p><strong>Customer:</strong> naih@car.com / secret1234@</p>
                <p><strong>Admin:</strong> admin@example.com / Admin@123</p>
                <p><strong>Super Admin:</strong> superAdmin@example.com / Admin@123</p>
              </div>
            </div> */}
          </div>
        </div>
      </div>

      <Footer />
    </main>
  )
}

export default LoginPage
