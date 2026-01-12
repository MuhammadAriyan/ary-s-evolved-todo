'use client'

import { Plus, Trash2, MessageSquare } from 'lucide-react'
import type { Conversation } from '@/types/chat'
import { cn } from '@/lib/utils'

interface ConversationListProps {
  conversations: Conversation[]
  currentConversationId?: string
  onSelect: (conversationId: string) => void
  onNew: () => void
  onDelete: (conversationId: string) => void
  isLoading?: boolean
  className?: string
}

export function ConversationList({
  conversations,
  currentConversationId,
  onSelect,
  onNew,
  onDelete,
  isLoading,
  className,
}: ConversationListProps) {
  return (
    <div
      className={cn(
        'flex flex-col h-full',
        'bg-black/40 backdrop-blur-xl border-r border-white/10',
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <button
          onClick={onNew}
          disabled={isLoading}
          className={cn(
            'w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl',
            'bg-aura-purple/80 hover:bg-aura-purple border border-aura-purple/50',
            'text-white font-medium transition-all duration-200',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          <Plus className="w-5 h-5" />
          New Chat
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <div className="text-center text-white/40 text-sm py-8 px-4">
            No conversations yet. Start a new chat!
          </div>
        ) : (
          conversations.map((conversation) => (
            <div
              key={conversation.id}
              className={cn(
                'group flex items-center gap-2 p-3 rounded-lg cursor-pointer',
                'transition-all duration-200',
                currentConversationId === conversation.id
                  ? 'bg-white/10 border border-white/20'
                  : 'hover:bg-white/5 border border-transparent'
              )}
              onClick={() => onSelect(conversation.id)}
            >
              <MessageSquare className="w-4 h-4 text-white/50 flex-shrink-0" />

              <div className="flex-1 min-w-0">
                <div className="text-sm text-white/90 truncate">
                  {conversation.title || 'New Conversation'}
                </div>
                <div className="text-xs text-white/40">
                  {new Date(conversation.updated_at).toLocaleDateString()}
                </div>
              </div>

              {/* Delete button */}
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(conversation.id)
                }}
                className={cn(
                  'p-1.5 rounded-lg opacity-0 group-hover:opacity-100',
                  'hover:bg-red-500/20 text-white/50 hover:text-red-400',
                  'transition-all duration-200'
                )}
                title="Delete conversation"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
