/**
 * useChat hook for managing chat state and operations
 */
'use client'

import { useState, useCallback, useEffect } from 'react'
import {
  chatClient,
  createConversation,
  getConversation,
  listConversations,
  sendMessage,
  deleteConversation,
  generateTitle,
} from '@/lib/chat-client'
import { apiClient } from '@/lib/api-client'
import { useSession, authClient } from '@/lib/auth-client'
import type {
  Conversation,
  ConversationWithMessages,
  Message,
  InputLanguage,
} from '@/types/chat'

interface UseChatState {
  conversations: Conversation[]
  currentConversation: ConversationWithMessages | null
  messages: Message[]
  isLoading: boolean
  isSending: boolean
  error: string | null
  tokenReady: boolean
}

interface UseChatActions {
  loadConversations: () => Promise<void>
  selectConversation: (conversationId: string) => Promise<void>
  createNewConversation: () => Promise<Conversation | null>
  sendChatMessage: (content: string, language?: InputLanguage) => Promise<void>
  deleteCurrentConversation: () => Promise<void>
  generateConversationTitle: () => Promise<void>
  clearError: () => void
}

export type UseChatReturn = UseChatState & UseChatActions

export function useChat(): UseChatReturn {
  const { data: session } = useSession()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<ConversationWithMessages | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tokenReady, setTokenReady] = useState(false)

  // Set JWT token in API client when session changes
  useEffect(() => {
    const fetchAndSetToken = async () => {
      if (session?.user) {
        try {
          const { data, error } = await authClient.token()

          if (data?.token) {
            apiClient.setToken(data.token)
            setTokenReady(true)
          } else if (error) {
            console.error('Failed to retrieve JWT token for chat:', error)
            apiClient.clearToken()
            setTokenReady(false)
          }
        } catch (err) {
          console.error('Error fetching JWT token for chat:', err)
          apiClient.clearToken()
          setTokenReady(false)
        }
      } else {
        apiClient.clearToken()
        setTokenReady(false)
      }
    }

    fetchAndSetToken()
  }, [session])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  const loadConversations = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await listConversations(50, 0)
      setConversations(response.conversations)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversations')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const selectConversation = useCallback(async (conversationId: string) => {
    setIsLoading(true)
    setError(null)
    try {
      const conversation = await getConversation(conversationId)
      setCurrentConversation(conversation)
      setMessages(conversation.messages || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load conversation')
    } finally {
      setIsLoading(false)
    }
  }, [])

  const createNewConversation = useCallback(async (): Promise<Conversation | null> => {
    setIsLoading(true)
    setError(null)
    try {
      const conversation = await createConversation()
      setConversations(prev => [conversation, ...prev])
      setCurrentConversation({ ...conversation, messages: [] })
      setMessages([])
      return conversation
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create conversation'
      setError(errorMessage)
      return null
    } finally {
      setIsLoading(false)
    }
  }, [])

  const sendChatMessage = useCallback(async (content: string, language: InputLanguage = 'en-US') => {
    if (!currentConversation) {
      setError('No conversation selected')
      return
    }

    if (!content.trim()) {
      return
    }

    setIsSending(true)
    setError(null)

    // Optimistically add user message
    const tempUserMessage: Message = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      agent_name: null,
      agent_icon: null,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMessage])

    try {
      const response = await sendMessage(currentConversation.id, content.trim(), language)

      // Replace temp message with actual user message and add assistant response
      setMessages(prev => {
        const withoutTemp = prev.filter(m => m.id !== tempUserMessage.id)
        return [
          ...withoutTemp,
          {
            id: `user-${Date.now()}`,
            role: 'user' as const,
            content: content.trim(),
            agent_name: null,
            agent_icon: null,
            created_at: new Date().toISOString(),
          },
          response.message,
        ]
      })

      // Generate title if this is the first message
      if (messages.length === 0 && !currentConversation.title) {
        await generateConversationTitle()
      }
    } catch (err) {
      // Remove optimistic message on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id))

      if (err instanceof Error && err.message.includes('429')) {
        setError('Rate limit exceeded. Please wait a moment before sending another message.')
      } else {
        setError(err instanceof Error ? err.message : 'Failed to send message')
      }
    } finally {
      setIsSending(false)
    }
  }, [currentConversation, messages.length])

  const deleteCurrentConversation = useCallback(async () => {
    if (!currentConversation) {
      return
    }

    setIsLoading(true)
    setError(null)
    try {
      await deleteConversation(currentConversation.id)
      setConversations(prev => prev.filter(c => c.id !== currentConversation.id))
      setCurrentConversation(null)
      setMessages([])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete conversation')
    } finally {
      setIsLoading(false)
    }
  }, [currentConversation])

  const generateConversationTitle = useCallback(async () => {
    if (!currentConversation) {
      return
    }

    try {
      const response = await generateTitle(currentConversation.id)
      setCurrentConversation(prev => prev ? { ...prev, title: response.title } : null)
      setConversations(prev =>
        prev.map(c =>
          c.id === currentConversation.id ? { ...c, title: response.title } : c
        )
      )
    } catch (err) {
      // Title generation failure is not critical, don't show error
      console.warn('Failed to generate title:', err)
    }
  }, [currentConversation])

  return {
    // State
    conversations,
    currentConversation,
    messages,
    isLoading,
    isSending,
    error,
    tokenReady,
    // Actions
    loadConversations,
    selectConversation,
    createNewConversation,
    sendChatMessage,
    deleteCurrentConversation,
    generateConversationTitle,
    clearError,
  }
}
