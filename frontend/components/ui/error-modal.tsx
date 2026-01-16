'use client'

import { AlertTriangle, X } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface ErrorModalProps {
  isOpen: boolean
  title?: string
  message: string
  onClose: () => void
  onRetry?: () => void
}

export function ErrorModal({ isOpen, title = 'Error', message, onClose, onRetry }: ErrorModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative w-full max-w-md rounded-xl bg-black/80 backdrop-blur-xl border border-red-500/30 p-6 shadow-lg animate-fadeIn">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-white/60 hover:text-white transition-colors"
        >
          <X className="h-5 w-5" />
        </button>

        {/* Icon */}
        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-500/20 mb-4">
          <AlertTriangle className="h-6 w-6 text-red-400" />
        </div>

        {/* Title */}
        <h2 className="text-xl font-semibold text-white mb-2">
          {title}
        </h2>

        {/* Message */}
        <p className="text-white/80 mb-6">
          {message}
        </p>

        {/* Actions */}
        <div className="flex gap-3">
          {onRetry && (
            <button
              onClick={() => {
                onRetry()
                onClose()
              }}
              className="flex-1 px-4 py-2 rounded-lg bg-aura-purple/80 hover:bg-aura-purple text-white font-medium transition-colors"
            >
              Retry
            </button>
          )}
          <button
            onClick={onClose}
            className={cn(
              'px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white font-medium transition-colors',
              onRetry ? 'flex-1' : 'w-full'
            )}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
