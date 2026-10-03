import { useEffect, useState, useCallback } from 'react'
import { BingoWebSocket } from '@/lib/websocket/client'
import { WebSocketEvent } from '@/lib/api/types'

export function useBingoWebSocket(gameId: number | null) {
  const [ws, setWs] = useState<BingoWebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketEvent | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')

  useEffect(() => {
    if (!gameId) return

    const websocket = new BingoWebSocket(gameId)

    websocket.onConnect(() => {
      setIsConnected(true)
      setConnectionStatus('connected')
    })

    websocket.onDisconnect(() => {
      setIsConnected(false)
      setConnectionStatus('disconnected')
    })

    websocket.onMessage((event) => {
      setLastMessage(event)
    })

    websocket.onError((error) => {
      console.error('WebSocket error:', error)
    })

    setConnectionStatus('connecting')
    websocket.connect()
    setWs(websocket)

    return () => {
      websocket.disconnect()
    }
  }, [gameId])

  const sendMessage = useCallback(
    (data: any) => {
      if (ws) {
        ws.send(data)
      }
    },
    [ws]
  )

  return {
    isConnected,
    connectionStatus,
    lastMessage,
    sendMessage,
  }
}
