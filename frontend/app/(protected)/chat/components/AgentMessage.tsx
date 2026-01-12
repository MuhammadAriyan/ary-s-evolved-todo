'use client'

import { cn } from '@/lib/utils'
import type { Message } from '@/types/chat'

interface AgentMessageProps {
  message: Message
  className?: string
}

export function AgentMessage({ message, className }: AgentMessageProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-xl',
        isUser
          ? 'bg-aura-purple/20 border border-aura-purple/30 ml-8'
          : 'bg-white/5 border border-white/10 mr-8',
        isSystem && 'bg-sky-500/10 border-sky-500/20 mx-4 text-sm',
        className
      )}
    >
      {/* Agent icon */}
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-lg">
          {message.agent_icon || '🤖'}
        </div>
      )}

      {/* Message content */}
      <div className="flex-1 min-w-0">
        {/* Agent name */}
        {!isUser && message.agent_name && (
          <div className="text-xs text-white/50 mb-1 font-medium">
            {message.agent_name}
          </div>
        )}

        {/* Content */}
        <div className="text-white/90 whitespace-pre-wrap break-words">
          {message.content}
        </div>

        {/* Timestamp */}
        <div className="text-xs text-white/30 mt-2">
          {new Date(message.created_at).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>

      {/* User icon */}
      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-aura-purple/30 flex items-center justify-center text-lg">
          👤
        </div>
      )}
    </div>
  )
}
