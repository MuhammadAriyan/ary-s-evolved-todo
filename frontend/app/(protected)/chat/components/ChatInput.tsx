'use client'

import { useState, useEffect, useRef, FormEvent, KeyboardEvent } from 'react'
import dynamic from 'next/dynamic'
import { Send, Loader2 } from 'lucide-react'
import type { VoiceLanguage } from '@/hooks/useVoiceInput'
import { cn } from '@/lib/utils'

// Dynamically import VoiceInputButton to prevent @huggingface/transformers from being bundled in serverless functions
const VoiceInputButton = dynamic(
  () => import('./VoiceInputButton').then(mod => ({ default: mod.VoiceInputButton })),
  {
    ssr: false,
    loading: () => null
  }
)

interface ChatInputProps {
  onSend: (message: string, language?: VoiceLanguage) => void
  disabled?: boolean
  isLoading?: boolean
  placeholder?: string
  className?: string
}

export function ChatInput({
  onSend,
  disabled = false,
  isLoading = false,
  placeholder = 'Type a message or use voice input...',
  className,
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [language, setLanguage] = useState<VoiceLanguage>('en-US')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Handle mobile keyboard visibility - scroll input into view when focused
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    const handleFocus = () => {
      // Small delay to let keyboard appear
      setTimeout(() => {
        textarea.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 300)
    }

    textarea.addEventListener('focus', handleFocus)
    return () => textarea.removeEventListener('focus', handleFocus)
  }, [])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (message.trim() && !disabled) {
      onSend(message.trim(), language)
      setMessage('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleVoiceTranscript = (transcript: string, lang: VoiceLanguage) => {
    setLanguage(lang)
    if (transcript.trim()) {
      onSend(transcript.trim(), lang)
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={cn(
        'relative flex items-end gap-2 p-3 md:p-4',
        'bg-black/30 backdrop-blur-xl border-t border-white/10',
        // Safe area padding for mobile devices with notches
        'pb-[max(0.75rem,env(safe-area-inset-bottom))]',
        className
      )}
    >
      {/* Text input */}
      <div className="flex-1 relative">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          className={cn(
            'w-full px-4 py-3 rounded-xl resize-none',
            'bg-white/5 border border-white/10',
            'text-white placeholder-white/40',
            'focus:outline-none focus:ring-2 focus:ring-aura-purple/50 focus:border-aura-purple/50',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'transition-all duration-200',
            // Mobile: larger text for readability
            'text-base md:text-sm',
            // Minimum height for touch accessibility
            'min-h-[44px]'
          )}
          style={{ maxHeight: '120px' }}
        />
      </div>

      {/* Voice input - 44px minimum touch target */}
      <VoiceInputButton onTranscript={handleVoiceTranscript} />

      {/* Send button - 44px minimum touch target */}
      <button
        type="submit"
        disabled={disabled || !message.trim() || isLoading}
        className={cn(
          'p-3 rounded-xl transition-all duration-200',
          'bg-aura-purple/80 hover:bg-aura-purple border border-aura-purple/50',
          'text-white',
          'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-aura-purple/80',
          // 44px minimum touch target
          'min-w-[44px] min-h-[44px] flex items-center justify-center'
        )}
      >
        {isLoading ? (
          <Loader2 className="w-5 h-5 animate-spin" />
        ) : (
          <Send className="w-5 h-5" />
        )}
      </button>
    </form>
  )
}
