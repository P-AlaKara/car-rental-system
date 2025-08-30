import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { isAuthenticated } from '../lib/auth'

interface ProtectedRouteProps {
  children: React.ReactNode
  requireAuth?: boolean
}

export default function ProtectedRoute({ children, requireAuth = true }: ProtectedRouteProps) {
  const location = useLocation()
  
  if (requireAuth && !isAuthenticated()) {
    // Redirect to login page with the current location as the return URL
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  
  return <>{children}</>
}
