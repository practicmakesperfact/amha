'use client'

import { createContext, useContext, useEffect, useState } from 'react'

interface TelegramContextType {
  webApp: any
  user: any
  initData: string
  isReady: boolean
}

const TelegramContext = createContext<TelegramContextType>({
  webApp: null,
  user: null,
  initData: '',
  isReady: false,
})

export function TelegramProvider({ children }: { children: React.ReactNode }) {
  const [webApp, setWebApp] = useState<any>(null)
  const [user, setUser] = useState<any>(null)
  const [initData, setInitData] = useState<string>('')
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    // Check if running in Telegram
    if (typeof window !== 'undefined') {
      const tg = (window as any).Telegram?.WebApp

      if (tg) {
        tg.ready()
        tg.expand()
        
        setWebApp(tg)
        setUser(tg.initDataUnsafe?.user)
        setInitData(tg.initData || '')
        setIsReady(true)

        // Set theme
        document.documentElement.classList.toggle('dark', tg.colorScheme === 'dark')
      } else {
        // Development mode - simulate Telegram user
        console.warn('Not running in Telegram WebApp - using mock data')
        setUser({
          id: 123456789,
          first_name: 'Test',
          last_name: 'User',
          username: 'testuser',
        })
        setInitData('mock_init_data_for_development')
        setIsReady(true)
      }
    }
  }, [])

  return (
    <TelegramContext.Provider value={{ webApp, user, initData, isReady }}>
      {children}
    </TelegramContext.Provider>
  )
}

export const useTelegramContext = () => useContext(TelegramContext)
