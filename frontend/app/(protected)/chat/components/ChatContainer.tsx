'use client'

import { useEffect, useState } from 'react'
import { Menu, X } from 'lucide-react'
import { useChat } from '@/hooks/useChat'
import { ConversationList } from './ConversationList'
import { MessageThread } from './MessageThread'
import { ChatInput } from './ChatInput'
import type { VoiceLanguage } from '@/hooks/useVoiceInput'
import { cn } from '@/lib/utils'

interface ChatContainerProps {
  className?: string
}

export function ChatContainer({ className }: ChatContainerProps) {
  const {
    conversations,
    currentConversation,
    messages,
    isLoading,
    isSending,
    error,
    tokenReady,
    loadConversations,
    selectConversation,
    createNewConversation,
    sendChatMessage,
    deleteCurrentConversation,
    clearError,
  } = useChat()

  const [sidebarOpen, setSidebarOpen] = useState(true)

  // Load conversations when token is ready
  useEffect(() => {
    if (tokenReady) {
      loadConversations()
    }
  }, [tokenReady, loadConversations])

  const handleNewChat = async () => {
    const conversation = await createNewConversation()
    if (conversation) {
      // Conversation created and selected
    }
  }

  const handleSelectConversation = async (conversationId: string) => {
    await selectConversation(conversationId)
  }

  const handleDeleteConversation = async (conversationId: string) => {
    if (currentConversation?.id === conversationId) {
      await deleteCurrentConversation()
    } else {
      // Delete non-current conversation
      // For now, just reload the list
      await loadConversations()
    }
  }

  const handleSendMessage = async (content: string, language?: VoiceLanguage) => {
    // Create conversation if none selected
    if (!currentConversation) {
      const conversation = await createNewConversation()
      if (!conversation) return
    }

    await sendChatMessage(content, language)
  }

  return (
    <div className={cn('flex h-full', className)}>
      {/* Mobile sidebar toggle */}
      <button
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className={cn(
          'fixed top-20 left-4 z-50 p-2 rounded-lg md:hidden',
          'bg-black/50 backdrop-blur-sm border border-white/10',
          'text-white/70 hover:text-white'
        )}
      >
        {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Sidebar */}
      <div
        className={cn(
          'w-72 flex-shrink-0 transition-all duration-300',
          'fixed md:relative inset-y-0 left-0 z-40',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:w-0 md:overflow-hidden'
        )}
      >
        <ConversationList
          conversations={conversations}
          currentConversationId={currentConversation?.id}
          onSelect={handleSelectConversation}
          onNew={handleNewChat}
          onDelete={handleDeleteConversation}
          isLoading={isLoading}
          className="h-full"
        />
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main chat area */}
      <div className="flex-1 flex flex-col min-w-0 bg-black/20">
        {/* Error banner */}
        {error && (
          <div className="p-3 bg-red-500/20 border-b border-red-500/30 text-red-300 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={clearError}
              className="text-red-400 hover:text-red-300"
            >
              ×
            </button>
          </div>
        )}

        {/* Messages */}
        <MessageThread
          messages={messages}
          isLoading={isSending}
          className="flex-1"
        />

        {/* Input */}
        <ChatInput
          onSend={handleSendMessage}
          disabled={isSending}
          placeholder={
            currentConversation
              ? 'Type a message or use voice input...'
              : 'Start a new conversation...'
          }
        />
      </div>
    </div>
  )
}
