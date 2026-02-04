/**
 * T041: WebSocket client service with auto-reconnect logic
 *
 * Manages WebSocket connection to the sync service with:
 * - Automatic reconnection with exponential backoff
 * - Heartbeat to keep connection alive
 * - Event subscription and message handling
 * - Connection state tracking
 */

export type WebSocketStatus = 'connecting' | 'connected' | 'disconnecting' | 'disconnected' | 'reconnecting' | 'error'

export interface WebSocketMessage {
  type: string
  [key: string]: any
}

export interface WebSocketClientOptions {
  url: string
  token: string
  reconnectInterval?: number
  maxReconnectInterval?: number
  reconnectDecay?: number
  heartbeatInterval?: number
  onMessage?: (message: WebSocketMessage) => void
  onStatusChange?: (status: WebSocketStatus) => void
  onError?: (error: Error) => void
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private token: string
  private status: WebSocketStatus = 'disconnected'
  private reconnectAttempts = 0
  private reconnectInterval: number
  private maxReconnectInterval: number
  private reconnectDecay: number
  private heartbeatInterval: number
  private heartbeatTimer: NodeJS.Timeout | null = null
  private reconnectTimer: NodeJS.Timeout | null = null
  private messageHandlers: Set<(message: WebSocketMessage) => void> = new Set()
  private statusHandlers: Set<(status: WebSocketStatus) => void> = new Set()
  private errorHandlers: Set<(error: Error) => void> = new Set()
  private shouldReconnect = true

  constructor(options: WebSocketClientOptions) {
    this.url = options.url
    this.token = options.token
    this.reconnectInterval = options.reconnectInterval || 1000
    this.maxReconnectInterval = options.maxReconnectInterval || 30000
    this.reconnectDecay = options.reconnectDecay || 1.5
    this.heartbeatInterval = options.heartbeatInterval || 30000

    if (options.onMessage) {
      this.messageHandlers.add(options.onMessage)
    }
    if (options.onStatusChange) {
      this.statusHandlers.add(options.onStatusChange)
    }
    if (options.onError) {
      this.errorHandlers.add(options.onError)
    }
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connected or connecting')
      return
    }

    this.setStatus('connecting')
    console.log('Connecting to WebSocket:', this.url)

    try {
      // Construct WebSocket URL with token as query parameter
      const wsUrl = `${this.url}?token=${encodeURIComponent(this.token)}`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = this.handleOpen.bind(this)
      this.ws.onmessage = this.handleMessage.bind(this)
      this.ws.onerror = this.handleError.bind(this)
      this.ws.onclose = this.handleClose.bind(this)
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      this.handleError(error as Event)
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    console.log('Disconnecting WebSocket')
    this.shouldReconnect = false
    this.stopHeartbeat()
    this.stopReconnect()

    if (this.ws) {
      this.setStatus('disconnecting')
      this.ws.close()
      this.ws = null
    }

    this.setStatus('disconnected')
  }

  /**
   * Send a message to the server
   */
  send(message: WebSocketMessage): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('WebSocket not connected, cannot send message')
      return
    }

    try {
      this.ws.send(JSON.stringify(message))
    } catch (error) {
      console.error('Failed to send WebSocket message:', error)
      this.notifyError(new Error('Failed to send message'))
    }
  }

  /**
   * Subscribe to task updates
   */
  subscribeToTasks(taskIds: string[]): void {
    this.send({
      type: 'subscribe',
      task_ids: taskIds
    })
  }

  /**
   * Add message handler
   */
  onMessage(handler: (message: WebSocketMessage) => void): () => void {
    this.messageHandlers.add(handler)
    return () => this.messageHandlers.delete(handler)
  }

  /**
   * Add status change handler
   */
  onStatusChange(handler: (status: WebSocketStatus) => void): () => void {
    this.statusHandlers.add(handler)
    return () => this.statusHandlers.delete(handler)
  }

  /**
   * Add error handler
   */
  onError(handler: (error: Error) => void): () => void {
    this.errorHandlers.add(handler)
    return () => this.errorHandlers.delete(handler)
  }

  /**
   * Get current connection status
   */
  getStatus(): WebSocketStatus {
    return this.status
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.status === 'connected' && this.ws?.readyState === WebSocket.OPEN
  }

  // Private methods

  private handleOpen(): void {
    console.log('WebSocket connected')
    this.setStatus('connected')
    this.reconnectAttempts = 0
    this.startHeartbeat()
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message = JSON.parse(event.data) as WebSocketMessage

      // Handle heartbeat acknowledgment
      if (message.type === 'heartbeat_ack') {
        return
      }

      // Notify all message handlers
      this.messageHandlers.forEach(handler => {
        try {
          handler(message)
        } catch (error) {
          console.error('Error in message handler:', error)
        }
      })
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error)
    }
  }

  private handleError(event: Event): void {
    console.error('WebSocket error:', event)
    this.setStatus('error')
    this.notifyError(new Error('WebSocket connection error'))
  }

  private handleClose(event: CloseEvent): void {
    console.log('WebSocket closed:', event.code, event.reason)
    this.stopHeartbeat()
    this.ws = null

    if (this.shouldReconnect) {
      this.setStatus('reconnecting')
      this.scheduleReconnect()
    } else {
      this.setStatus('disconnected')
    }
  }

  private scheduleReconnect(): void {
    this.stopReconnect()

    const delay = Math.min(
      this.reconnectInterval * Math.pow(this.reconnectDecay, this.reconnectAttempts),
      this.maxReconnectInterval
    )

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts + 1})`)

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++
      this.connect()
    }, delay)
  }

  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat()

    this.heartbeatTimer = setInterval(() => {
      if (this.isConnected()) {
        this.send({
          type: 'heartbeat',
          timestamp: new Date().toISOString()
        })
      }
    }, this.heartbeatInterval)
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  private setStatus(status: WebSocketStatus): void {
    if (this.status !== status) {
      this.status = status
      console.log('WebSocket status changed:', status)
      this.statusHandlers.forEach(handler => {
        try {
          handler(status)
        } catch (error) {
          console.error('Error in status handler:', error)
        }
      })
    }
  }

  private notifyError(error: Error): void {
    this.errorHandlers.forEach(handler => {
      try {
        handler(error)
      } catch (err) {
        console.error('Error in error handler:', err)
      }
    })
  }
}

/**
 * Create WebSocket client instance
 */
export function createWebSocketClient(options: WebSocketClientOptions): WebSocketClient {
  return new WebSocketClient(options)
}
