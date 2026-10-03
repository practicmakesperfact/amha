import { useTelegramContext } from '@/providers/telegram-provider'

export function useTelegram() {
  const { webApp, user, initData, isReady } = useTelegramContext()

  const showAlert = (message: string) => {
    if (webApp) {
      webApp.showAlert(message)
    } else {
      alert(message)
    }
  }

  const showConfirm = (message: string): Promise<boolean> => {
    return new Promise((resolve) => {
      if (webApp) {
        webApp.showConfirm(message, resolve)
      } else {
        resolve(confirm(message))
      }
    })
  }

  const showPopup = (params: any) => {
    if (webApp) {
      webApp.showPopup(params)
    }
  }

  const close = () => {
    if (webApp) {
      webApp.close()
    }
  }

  const setHeaderColor = (color: string) => {
    if (webApp) {
      webApp.setHeaderColor(color)
    }
  }

  const setBackgroundColor = (color: string) => {
    if (webApp) {
      webApp.setBackgroundColor(color)
    }
  }

  const enableClosingConfirmation = () => {
    if (webApp) {
      webApp.enableClosingConfirmation()
    }
  }

  const disableClosingConfirmation = () => {
    if (webApp) {
      webApp.disableClosingConfirmation()
    }
  }

  const hapticFeedback = (type: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'medium') => {
    if (webApp?.HapticFeedback) {
      webApp.HapticFeedback.impactOccurred(type)
    }
  }

  return {
    webApp,
    user,
    initData,
    isReady,
    showAlert,
    showConfirm,
    showPopup,
    close,
    setHeaderColor,
    setBackgroundColor,
    enableClosingConfirmation,
    disableClosingConfirmation,
    hapticFeedback,
  }
}
