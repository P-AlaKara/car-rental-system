import './App.css'
import AdminPage from './components/AdminPage'
import AdminSetup from './components/AdminSetup'
import ProtectedRoute from './components/ProtectedRoute'
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { setupTokenRefresh } from './lib/auth'

// Import extracted page components
import HomePage from './pages/HomePage'
import CarsPage from './pages/CarsPage'
import CarDetailsPage from './pages/CarDetailsPage'
import BookPage from './pages/BookPage'
import AboutPage from './pages/AboutPage'
import ContactPage from './pages/ContactPage'
import TermsPage from './pages/TermsPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProfilePage from './pages/ProfilePage'

function AppContent() {
  const location = useLocation()
  
  useEffect(() => {
    // Preserve the current URL path on page refresh
    // This prevents unwanted redirects by ensuring we stay on the current page
    console.log('🔍 Current route:', location.pathname)
  }, [location.pathname])

  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/cars" element={<CarsPage />} />
      <Route path="/car/:carId" element={<CarDetailsPage />} />
      <Route path="/book/:carId" element={
        <ProtectedRoute>
          <BookPage />
        </ProtectedRoute>
      } />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/contact" element={<ContactPage />} />
      <Route path="/terms" element={<TermsPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/profile" element={
        <ProtectedRoute>
          <ProfilePage />
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <ProtectedRoute>
          <AdminPage />
        </ProtectedRoute>
      } />
      <Route path="/admin/setup" element={
        <ProtectedRoute>
          <AdminSetup />
        </ProtectedRoute>
      } />
      <Route path="*" element={<HomePage />} />
    </Routes>
  )
}

export default function App() {
  // Setup token refresh on app initialization
  useEffect(() => {
    setupTokenRefresh()
  }, [])

  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <AppContent />
    </BrowserRouter>
  )
}
