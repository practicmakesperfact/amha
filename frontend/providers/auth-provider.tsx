'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { useTelegramContext } from './telegram-provider'
import { apiClient } from '@/lib/api/client'

interface User {
  id: number
  telegram_id: number
  username: string
  full_name: string
  phone_number: string
  main_wallet: number
  play_wallet: number
  coin: number
  wins: number
  is_registered: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: () => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  isLoading: true,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
  refreshUser: async () => {},
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { initData, isReady, user: tgUser } = useTelegramContext()
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const login = async () => {
    if (!initData) {
      console.error('No Telegram init data available')
      return
    }

    try {
      setIsLoading(true)
      
      // Send initData to backend for verification
      // Backend should validate and return user data
      const response = await apiClient.post('/auth/telegram', {
        init_data: initData,
        telegram_user: tgUser,
      })

      if (response.data.user) {
        setUser(response.data.user)
        setIsAuthenticated(true)
        
        // Store auth token if provided
        if (response.data.token) {
          localStorage.setItem('auth_token', response.data.token)
        }
      }
    } catch (error) {
      console.error('Authentication failed:', error)
      // In development, set mock user
      if (process.env.NODE_ENV === 'development') {
        setUser({
          id: 1,
          telegram_id: tgUser?.id || 123456789,
          username: tgUser?.username || 'testuser',
          full_name: tgUser?.first_name || 'Test User',
          phone_number: '0912345678',
          main_wallet: 500,
          play_wallet: 100,
          coin: 10,
          wins: 5,
          is_registered: true,
        })
        setIsAuthenticated(true)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('auth_token')
  }

  const refreshUser = async () => {
    if (!isAuthenticated) return

    try {
      const response = await apiClient.get('/auth/me')
      if (response.data.user) {
        setUser(response.data.user)
      }
    } catch (error) {
      console.error('Failed to refresh user:', error)
    }
  }

  // Auto-login when Telegram is ready
  useEffect(() => {
    if (isReady && !isAuthenticated && !isLoading) {
      login()
    }
  }, [isReady])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
