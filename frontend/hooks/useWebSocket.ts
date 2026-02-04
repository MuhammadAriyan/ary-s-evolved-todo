/**
 * T042: useWebSocket hook for connection management
 *
 * React hook that manages WebSocket connection lifecycle and provides:
 * - Connection state management
 * - Automatic connection/disconnection based on authentication
 * - Message handling
 * - Status tracking
 */

import { useEffect, useState, useCallback, useRef } from 'react'
import { useSession, authClient } from '@/lib/auth-client'
import { WebSocketClient, WebSocketStatus, WebSocketMessage, createWebSocketClient } from '@/lib/websocket-client'

// WebSocket URL - use environment variable or default
const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8001/ws'

export interface UseWebSocketOptions {
  enabled?: boolean
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Error) => void
}

export interface UseWebSocketReturn {
  status: WebSocketStatus
  isConnected: boolean
  send: (message: WebSocketMessage) => void
  subscribeToTasks: (taskIds: string[]) => void
  connect: () => void
  disconnect: () => void
}

export function useWebSocket(options: UseWebSocketOptions = {}): UseWebSocketReturn {
  const { enabled = true, onMessage, onError } = options
  const { data: session } = useSession()
  const [status, setStatus] = useState<WebSocketStatus>('disconnected')
  const [isConnected, setIsConnected] = useState(false)
  const clientRef = useRef<WebSocketClient | null>(null)
  const [token, setToken] = useState<string | null>(null)

  // Fetch JWT token when session changes
  useEffect(() => {
    const fetchToken = async () => {
      if (session?.user) {
        try {
          const { data, error } = await authClient.token()
          if (data?.token) {
            console.log('✅ JWT token retrieved for WebSocket')
            setToken(data.token)
          } else if (error) {
            console.error('❌ Failed to retrieve JWT token for WebSocket:', error)
            setToken(null)
          }
        } catch (err) {
          console.error('❌ Error fetching JWT token for WebSocket:', err)
          setToken(null)
        }
      } else {
        setToken(null)
      }
    }

    fetchToken()
  }, [session])

  // Initialize WebSocket client when token is available
  useEffect(() => {
    if (!enabled || !token || !session?.user) {
      // Disconnect if disabled or no token
      if (clientRef.current) {
        clientRef.current.disconnect()
        clientRef.current = null
      }
      return
    }

    // Create WebSocket client
    console.log('Creating WebSocket client')
    const client = createWebSocketClient({
      url: WS_URL,
      token,
      onMessage: (message) => {
        console.log('WebSocket message received:', message.type)
        if (onMessage) {
          onMessage(message)
        }
      },
      onStatusChange: (newStatus) => {
        console.log('WebSocket status changed:', newStatus)
        setStatus(newStatus)
        setIsConnected(newStatus === 'connected')
      },
      onError: (error) => {
        console.error('WebSocket error:', error)
        if (onError) {
          onError(error)
        }
      }
    })

    clientRef.current = client

    // Connect to WebSocket
    client.connect()

    // Cleanup on unmount
    return () => {
      console.log('Cleaning up WebSocket client')
      client.disconnect()
      clientRef.current = null
    }
  }, [enabled, token, session?.user, onMessage, onError])

  // Send message
  const send = useCallback((message: WebSocketMessage) => {
    if (clientRef.current) {
      clientRef.current.send(message)
    } else {
      console.warn('Cannot send message: WebSocket client not initialized')
    }
  }, [])

  // Subscribe to task updates
  const subscribeToTasks = useCallback((taskIds: string[]) => {
    if (clientRef.current) {
      clientRef.current.subscribeToTasks(taskIds)
    } else {
      console.warn('Cannot subscribe: WebSocket client not initialized')
    }
  }, [])

  // Manual connect
  const connect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.connect()
    }
  }, [])

  // Manual disconnect
  const disconnect = useCallback(() => {
    if (clientRef.current) {
      clientRef.current.disconnect()
    }
  }, [])

  return {
    status,
    isConnected,
    send,
    subscribeToTasks,
    connect,
    disconnect
  }
}
