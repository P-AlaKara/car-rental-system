import React, { useState, useEffect } from 'react'
import { getSessionInfo, getSessionTimeRemaining, formatTimeRemaining } from '../lib/auth'

interface SessionStatusProps {
  showDetails?: boolean
  className?: string
}

export default function SessionStatus({ showDetails = false, className = '' }: SessionStatusProps) {
  const [sessionInfo, setSessionInfo] = useState<ReturnType<typeof getSessionInfo> | null>(null)
  const [timeRemaining, setTimeRemaining] = useState<number>(0)

  useEffect(() => {
    const updateSessionInfo = () => {
      const info = getSessionInfo()
      setSessionInfo(info)
      setTimeRemaining(getSessionTimeRemaining())
    }

    updateSessionInfo()
    
    // Update every minute
    const interval = setInterval(updateSessionInfo, 60 * 1000)
    
    return () => clearInterval(interval)
  }, [])

  if (!sessionInfo) {
    return null
  }

  const { isExpired, sessionStart, tokenExpiry } = sessionInfo
  const formattedTimeRemaining = formatTimeRemaining(timeRemaining)

  if (isExpired) {
    return (
      <div className={`text-red-600 text-sm ${className}`}>
        Session expired
      </div>
    )
  }

  return (
    <div className={`text-slate-600 text-sm ${className}`}>
      {showDetails ? (
        <div className="space-y-1">
          <div>Session: {formattedTimeRemaining} remaining</div>
          <div className="text-xs text-slate-500">
            Started: {sessionStart.toLocaleTimeString()}
          </div>
          <div className="text-xs text-slate-500">
            Expires: {tokenExpiry.toLocaleTimeString()}
          </div>
        </div>
      ) : (
        <div>Session: {formattedTimeRemaining} remaining</div>
      )}
    </div>
  )
}
