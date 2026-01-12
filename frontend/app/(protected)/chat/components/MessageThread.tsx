'use client'

import { useRef, useEffect } from 'react'
import { AgentMessage } from './AgentMessage'
import type { Message } from '@/types/chat'
import { cn } from '@/lib/utils'

interface MessageThreadProps {
  messages: Message[]
  isLoading?: boolean
  className?: string
}

export function MessageThread({ messages, isLoading, className }: MessageThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  if (messages.length === 0 && !isLoading) {
    return (
      <div className={cn('flex-1 flex items-center justify-center', className)}>
        <div className="text-center text-white/50 max-w-md px-4">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-lg font-medium text-white/70 mb-2">
            Hello! I'm Aren, your AI task assistant.
          </h3>
          <p className="text-sm">
            I can help you manage your tasks through conversation. Try saying:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-white/60">
            <li>"Add task buy groceries"</li>
            <li>"Show my pending tasks"</li>
            <li>"Complete task 1"</li>
            <li>"Show my stats"</li>
          </ul>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('flex-1 overflow-y-auto p-4 space-y-4', className)}>
      {messages.map((message) => (
        <AgentMessage key={message.id} message={message} />
      ))}

      {/* Loading indicator */}
      {isLoading && (
        <div className="flex gap-3 p-4 rounded-xl bg-white/5 border border-white/10 mr-8">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-white/30 border-t-white/70 rounded-full animate-spin" />
          </div>
          <div className="flex items-center">
            <span className="text-white/50 text-sm">Thinking...</span>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={bottomRef} />
    </div>
  )
}
