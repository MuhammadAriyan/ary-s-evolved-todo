/**
 * NotificationToast Component
 * T070: Create notification display component (toast)
 */

"use client"

import { useEffect, useState } from "react"
import { Bell, X, CheckCircle, AlertCircle, Info } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"

export interface ToastNotification {
  id: string
  type: "reminder" | "success" | "error" | "info"
  title: string
  message: string
  timestamp?: string
  taskId?: string
}

interface NotificationToastProps {
  notification: ToastNotification
  onClose: (id: string) => void
  duration?: number
}

export function NotificationToast({
  notification,
  onClose,
  duration = 5000,
}: NotificationToastProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => onClose(notification.id), 300)
    }, duration)

    return () => clearTimeout(timer)
  }, [notification.id, duration, onClose])

  const getIcon = () => {
    switch (notification.type) {
      case "reminder":
        return <Bell className="h-5 w-5 text-blue-400" />
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-400" />
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-400" />
      case "info":
        return <Info className="h-5 w-5 text-blue-400" />
      default:
        return <Bell className="h-5 w-5 text-blue-400" />
    }
  }

  const getBackgroundColor = () => {
    switch (notification.type) {
      case "reminder":
        return "bg-blue-500/20 border-blue-500/30"
      case "success":
        return "bg-green-500/20 border-green-500/30"
      case "error":
        return "bg-red-500/20 border-red-500/30"
      case "info":
        return "bg-blue-500/20 border-blue-500/30"
      default:
        return "bg-white/10 border-white/20"
    }
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: -20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -20, scale: 0.95 }}
          transition={{ duration: 0.2 }}
          className={`
            flex items-start gap-3 p-4 rounded-lg border backdrop-blur-md
            shadow-lg max-w-md w-full
            ${getBackgroundColor()}
          `}
        >
          {/* Icon */}
          <div className="flex-shrink-0 mt-0.5">{getIcon()}</div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <h4 className="text-white font-semibold text-sm mb-1">
              {notification.title}
            </h4>
            <p className="text-white/80 text-sm">{notification.message}</p>
            {notification.timestamp && (
              <p className="text-white/40 text-xs mt-1">
                {new Date(notification.timestamp).toLocaleTimeString()}
              </p>
            )}
          </div>

          {/* Close button */}
          <button
            onClick={() => {
              setIsVisible(false)
              setTimeout(() => onClose(notification.id), 300)
            }}
            className="flex-shrink-0 text-white/60 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  )
}

/**
 * NotificationContainer Component
 * Container for managing multiple toast notifications
 */
interface NotificationContainerProps {
  notifications: ToastNotification[]
  onClose: (id: string) => void
}

export function NotificationContainer({
  notifications,
  onClose,
}: NotificationContainerProps) {
  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 pointer-events-none">
      <div className="pointer-events-auto space-y-2">
        {notifications.map((notification) => (
          <NotificationToast
            key={notification.id}
            notification={notification}
            onClose={onClose}
          />
        ))}
      </div>
    </div>
  )
}

/**
 * Hook for managing notifications
 */
export function useNotifications() {
  const [notifications, setNotifications] = useState<ToastNotification[]>([])

  const addNotification = (
    notification: Omit<ToastNotification, "id">
  ) => {
    const id = `notification-${Date.now()}-${Math.random()}`
    setNotifications((prev) => [...prev, { ...notification, id }])
  }

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }

  const clearAll = () => {
    setNotifications([])
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
  }
}
