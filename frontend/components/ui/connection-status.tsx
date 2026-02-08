/**
 * T046: Connection status indicator component
 *
 * Displays the current WebSocket connection status with visual feedback
 */

'use client'

import { useWebSocket } from '@/hooks/useWebSocket'
import { Wifi, WifiOff, RefreshCw, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ConnectionStatusProps {
  className?: string
  showLabel?: boolean
}

export function ConnectionStatus({ className, showLabel = true }: ConnectionStatusProps) {
  const { status, isConnected } = useWebSocket()

  const statusConfig = {
    connected: {
      icon: Wifi,
      label: 'Online',
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
      description: 'Real-time sync active'
    },
    connecting: {
      icon: RefreshCw,
      label: 'Connecting',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
      description: 'Establishing connection...'
    },
    reconnecting: {
      icon: RefreshCw,
      label: 'Reconnecting',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-500/10',
      description: 'Reconnecting to server...'
    },
    disconnected: {
      icon: WifiOff,
      label: 'Offline',
      color: 'text-gray-500',
      bgColor: 'bg-gray-500/10',
      description: 'Not connected'
    },
    disconnecting: {
      icon: WifiOff,
      label: 'Disconnecting',
      color: 'text-gray-500',
      bgColor: 'bg-gray-500/10',
      description: 'Closing connection...'
    },
    error: {
      icon: AlertCircle,
      label: 'Error',
      color: 'text-red-500',
      bgColor: 'bg-red-500/10',
      description: 'Connection error'
    }
  }

  const config = statusConfig[status] || statusConfig.disconnected
  const Icon = config.icon

  return (
    <div
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 rounded-full transition-all',
        config.bgColor,
        className
      )}
      title={config.description}
    >
      <Icon
        className={cn(
          'h-4 w-4',
          config.color,
          (status === 'connecting' || status === 'reconnecting') && 'animate-spin'
        )}
      />
      {showLabel && (
        <span className={cn('text-sm font-medium', config.color)}>
          {config.label}
        </span>
      )}
    </div>
  )
}
