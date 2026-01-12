'use client'

import { useState, FormEvent, KeyboardEvent } from 'react'
import { Send } from 'lucide-react'
import { VoiceInputButton } from './VoiceInputButton'
import type { VoiceLanguage } from '@/hooks/useVoiceInput'
import { cn } from '@/lib/utils'

interface ChatInputProps {
  onSend: (message: string, language?: VoiceLanguage) => void
  disabled?: boolean
  placeholder?: string
  className?: string
}

export function ChatInput({
  onSend,
  disabled = false,
  placeholder = 'Type a message or use voice input...',
  className,
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [language, setLanguage] = useState<VoiceLanguage>('en-US')

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
        'relative flex items-end gap-2 p-4',
        'bg-black/30 backdrop-blur-xl border-t border-white/10',
        className
      )}
    >
      {/* Text input */}
      <div className="flex-1 relative">
        <textarea
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
            'transition-all duration-200'
          )}
          style={{ maxHeight: '120px' }}
        />
      </div>

      {/* Voice input */}
      <VoiceInputButton onTranscript={handleVoiceTranscript} />

      {/* Send button */}
      <button
        type="submit"
        disabled={disabled || !message.trim()}
        className={cn(
          'p-3 rounded-xl transition-all duration-200',
          'bg-aura-purple/80 hover:bg-aura-purple border border-aura-purple/50',
          'text-white',
          'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-aura-purple/80'
        )}
      >
        <Send className="w-5 h-5" />
      </button>
    </form>
  )
}
