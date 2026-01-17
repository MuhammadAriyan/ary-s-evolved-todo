'use client'

import { X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

export interface ToastProps {
  id: string
  title?: string
  description: string
  variant?: 'default' | 'error' | 'success' | 'warning'
  duration?: number
  onClose?: () => void
}

export function Toast({ id, title, description, variant = 'default', duration = 5000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true)

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
      setTimeout(() => onClose?.(), 300) // Wait for fade out animation
    }, duration)

    return () => clearTimeout(timer)
  }, [duration, onClose])

  const handleClose = () => {
    setIsVisible(false)
    setTimeout(() => onClose?.(), 300)
  }

  const variantStyles = {
    default: 'bg-white/10 border-white/20',
    error: 'bg-red-500/20 border-red-500/30',
    success: 'bg-green-500/20 border-green-500/30',
    warning: 'bg-yellow-500/20 border-yellow-500/30',
  }

  return (
    <div
      className={cn(
        'pointer-events-auto flex w-full max-w-md rounded-xl border p-4 shadow-lg backdrop-blur-xl transition-all duration-300',
        variantStyles[variant],
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      )}
    >
      <div className="flex-1">
        {title && (
          <div className="text-sm font-semibold text-white mb-1">
            {title}
          </div>
        )}
        <div className="text-sm text-white/80">
          {description}
        </div>
      </div>
      <button
        onClick={handleClose}
        className="ml-4 inline-flex h-6 w-6 items-center justify-center rounded-md text-white/60 hover:text-white transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

export function ToastContainer({ toasts }: { toasts: ToastProps[] }) {
  return (
    <div className="fixed bottom-0 right-0 z-50 flex flex-col gap-2 p-4 pointer-events-none">
      {toasts.map((toast) => (
        <Toast key={toast.id} {...toast} />
      ))}
    </div>
  )
}
