import { WebSocketEvent } from '../api/types'

const WS_BASE_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

type MessageHandler = (event: WebSocketEvent) => void
type ConnectionHandler = () => void
type ErrorHandler = (error: Event) => void

export class BingoWebSocket {
  private ws: WebSocket | null = null
  private gameId: number
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectDelay = 1000
  private messageHandlers: MessageHandler[] = []
  private connectHandlers: ConnectionHandler[] = []
  private disconnectHandlers: ConnectionHandler[] = []
  private errorHandlers: ErrorHandler[] = []
  private isManualClose = false

  constructor(gameId: number) {
    this.gameId = gameId
  }

  connect() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    const url = `${WS_BASE_URL}/ws/bingo/${this.gameId}`
    console.log('Connecting to WebSocket:', url)

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.reconnectDelay = 1000
        this.connectHandlers.forEach((handler) => handler())
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketEvent
          console.log('WebSocket message:', data)
          this.messageHandlers.forEach((handler) => handler(data))
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.errorHandlers.forEach((handler) => handler(error))
      }

      this.ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason)
        this.disconnectHandlers.forEach((handler) => handler())

        // Attempt reconnection if not manually closed
        if (!this.isManualClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++
          console.log(
            `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
          )
          
          setTimeout(() => {
            this.connect()
          }, this.reconnectDelay)

          // Exponential backoff
          this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
    }
  }

  disconnect() {
    this.isManualClose = true
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  onMessage(handler: MessageHandler) {
    this.messageHandlers.push(handler)
    return () => {
      this.messageHandlers = this.messageHandlers.filter((h) => h !== handler)
    }
  }

  onConnect(handler: ConnectionHandler) {
    this.connectHandlers.push(handler)
    return () => {
      this.connectHandlers = this.connectHandlers.filter((h) => h !== handler)
    }
  }

  onDisconnect(handler: ConnectionHandler) {
    this.disconnectHandlers.push(handler)
    return () => {
      this.disconnectHandlers = this.disconnectHandlers.filter((h) => h !== handler)
    }
  }

  onError(handler: ErrorHandler) {
    this.errorHandlers.push(handler)
    return () => {
      this.errorHandlers = this.errorHandlers.filter((h) => h !== handler)
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}
