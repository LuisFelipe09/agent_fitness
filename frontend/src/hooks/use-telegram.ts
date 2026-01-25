import { useEffect, useState } from 'react'

interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  language_code?: string
}

interface WebApp {
  initData: string
  initDataUnsafe: {
    user?: TelegramUser
    query_id?: string
    auth_date?: number
    hash?: string
  }
  version: string
  platform: string
  colorScheme: 'light' | 'dark'
  themeParams: any
  isExpanded: boolean
  viewportHeight: number
  viewportStableHeight: number
  headerColor: string
  backgroundColor: string
  isClosingConfirmationEnabled: boolean
  BackButton: any
  MainButton: any
  ready: () => void
  expand: () => void
  close: () => void
  setHeaderColor: (color: string) => void
  setBackgroundColor: (color: string) => void
  enableClosingConfirmation: () => void
  disableClosingConfirmation: () => void
  onEvent: (eventType: string, callback: () => void) => void
  offEvent: (eventType: string, callback: () => void) => void
  sendData: (data: string) => void
  showPopup: (params: any, callback?: (buttonId: string) => void) => void
  showAlert: (message: string, callback?: () => void) => void
  showConfirm: (message: string, callback?: (confirmed: boolean) => void) => void
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: WebApp
    }
  }
}

export function useTelegram() {
  const [webApp, setWebApp] = useState<WebApp | null>(null)
  const [user, setUser] = useState<TelegramUser | null>(null)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      setWebApp(tg)
      setUser(tg.initDataUnsafe.user || null)
    }
  }, [])

  return {
    webApp,
    user,
    isInTelegram: !!webApp,
  }
}
