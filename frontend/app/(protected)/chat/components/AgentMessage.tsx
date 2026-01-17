'use client'

import { cn } from '@/lib/utils'
import type { Message } from '@/types/chat'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface AgentMessageProps {
  message: Message
  className?: string
}

export function AgentMessage({ message, className }: AgentMessageProps) {
  const isUser = message.role === 'user'
  const isSystem = message.role === 'system'

  // Determine avatar colors based on agent
  const getAgentAvatarColor = () => {
    if (isUser) {
      // User: purple/magenta gradient
      return 'bg-gradient-to-br from-aura-purple to-aura-magenta'
    }

    const agentName = message.agent_name?.toLowerCase() || ''

    if (agentName.includes('miyu')) {
      // Miyu: purple/violet gradient
      return 'bg-gradient-to-br from-aura-purple to-purple-600'
    } else if (agentName.includes('riven')) {
      // Riven: magenta/pink gradient
      return 'bg-gradient-to-br from-aura-magenta to-pink-400'
    }

    // Default: white/10 for other agents
    return 'bg-white/10'
  }

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
        <div className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-lg',
          getAgentAvatarColor()
        )}>
          {message.agent_icon || '🤖'}
        </div>
      )}

      {/* Message content */}
      <div className="flex-1 min-w-0">
        {/* Agent name */}
        {!isUser && message.agent_name && (
          <div className="text-xs text-white/50 mb-1 font-medium font-chelsea">
            {message.agent_name}
          </div>
        )}

        {/* Content */}
        <div className="text-white/90 prose prose-invert prose-sm max-w-none font-chelsea">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
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
        <div className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full border-2 border-aura-purple/50',
          getAgentAvatarColor()
        )} />
      )}
    </div>
  )
}
