/**
 * useChat hook for managing chat state and operations
 */
'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import {
  chatClient,
  createConversation,
  getConversation,
  listConversations,
  sendMessage,
  deleteConversation,
  generateTitle,
  streamMessage,
} from '@/lib/chat-client'
import { apiClient } from '@/lib/api-client'
import { useSession, authClient } from '@/lib/auth-client'
import type {
  Conversation,
  ConversationWithMessages,
  Message,
  InputLanguage,
  LanguageHint,
  StreamEvent,
} from '@/types/chat'
import {
  isTokenEvent,
  isAgentChangeEvent,
  isToolCallEvent,
  isConversationCreatedEvent,
  isDoneEvent,
  isErrorEvent,
} from '@/types/chat'

/** Current streaming state */
export interface StreamingState {
  isStreaming: boolean;
  content: string;
  agentName: string;
  agentIcon: string;
  toolCalls: string[];
}

interface UseChatState {
  conversations: Conversation[]
  currentConversation: ConversationWithMessages | null
  messages: Message[]
  isLoading: boolean
  isSending: boolean
  error: string | null
  tokenReady: boolean
  streaming: StreamingState
}

interface UseChatActions {
  loadConversations: () => Promise<void>
  selectConversation: (conversationId: string) => Promise<void>
  createNewConversation: () => Promise<Conversation | null>
  sendChatMessage: (content: string, language?: InputLanguage) => Promise<void>
  sendStreamingMessage: (content: string, options?: { languageHint?: LanguageHint }) => Promise<void>
  deleteCurrentConversation: () => Promise<void>
  generateConversationTitle: () => Promise<void>
  clearError: () => void
}

export type UseChatReturn = UseChatState & UseChatActions

const initialStreamingState: StreamingState = {
  isStreaming: false,
  content: '',
  agentName: 'Aren',
  agentIcon: '🤖',
  toolCalls: [],
}

export function useChat(): UseChatReturn {
  const { data: session } = useSession()
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversation, setCurrentConversation] = useState<ConversationWithMessages | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tokenReady, setTokenReady] = useState(false)
  const [streaming, setStreaming] = useState<StreamingState>(initialStreamingState)
  const tokenRef = useRef<string | null>(null)

  // Set JWT token in API client when session changes
  useEffect(() => {
    const fetchAndSetToken = async () => {
      if (session?.user) {
        try {
          const { data, error } = await authClient.token()

          if (data?.token) {
            apiClient.setToken(data.token)
            tokenRef.current = data.token
            setTokenReady(true)
          } else if (error) {
            console.error('Failed to retrieve JWT token for chat:', error)
            apiClient.clearToken()
            tokenRef.current = null
            setTokenReady(false)
          }
        } catch (err) {
          console.error('Error fetching JWT token for chat:', err)
          apiClient.clearToken()
          tokenRef.current = null
          setTokenReady(false)
        }
      } else {
        apiClient.clearToken()
        tokenRef.current = null
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

  const sendStreamingMessage = useCallback(async (
    content: string,
    options: { languageHint?: LanguageHint } = {}
  ) => {
    if (!content.trim()) {
      return
    }

    if (!tokenRef.current) {
      setError('Not authenticated')
      return
    }

    setIsSending(true)
    setError(null)

    // Optimistically add user message
    const tempUserMessage: Message = {
      id: `temp-user-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      agent_name: null,
      agent_icon: null,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, tempUserMessage])

    // Reset streaming state
    setStreaming({
      isStreaming: true,
      content: '',
      agentName: 'Aren',
      agentIcon: '🤖',
      toolCalls: [],
    })

    let newConversationId: string | null = null
    let finalContent = ''
    let finalAgentName = 'Aren'
    let finalAgentIcon = '🤖'
    let messageId = ''

    try {
      const stream = streamMessage(
        content.trim(),
        {
          conversationId: currentConversation?.id ?? null,
          languageHint: options.languageHint ?? 'auto',
          contextWindow: 6,
        },
        tokenRef.current
      )

      for await (const event of stream) {
        if (isConversationCreatedEvent(event)) {
          newConversationId = event.conversation_id
          // Create new conversation in state
          const newConv: Conversation = {
            id: event.conversation_id,
            title: null,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          }
          setConversations(prev => [newConv, ...prev])
          setCurrentConversation({ ...newConv, messages: [] })
        } else if (isTokenEvent(event)) {
          finalContent += event.content
          setStreaming(prev => ({
            ...prev,
            content: prev.content + event.content,
          }))
        } else if (isAgentChangeEvent(event)) {
          finalAgentName = event.agent
          finalAgentIcon = event.icon
          setStreaming(prev => ({
            ...prev,
            agentName: event.agent,
            agentIcon: event.icon,
          }))
        } else if (isToolCallEvent(event)) {
          setStreaming(prev => ({
            ...prev,
            toolCalls: [...prev.toolCalls, event.tool],
          }))
        } else if (isDoneEvent(event)) {
          messageId = event.message_id
        } else if (isErrorEvent(event)) {
          throw new Error(event.message)
        }
      }

      // First, clear streaming state to prevent duplicate display
      setStreaming(initialStreamingState)

      // Then replace temp user message and add final assistant message
      const assistantMessage: Message = {
        id: messageId || `assistant-${Date.now()}`,
        role: 'assistant',
        content: finalContent,
        agent_name: finalAgentName,
        agent_icon: finalAgentIcon,
        created_at: new Date().toISOString(),
      }

      setMessages(prev => {
        const withoutTemp = prev.filter(m => m.id !== tempUserMessage.id)
        return [
          ...withoutTemp,
          {
            ...tempUserMessage,
            id: `user-${Date.now()}`,
          },
          assistantMessage,
        ]
      })

      // Generate title if this is the first message
      const conversationId = newConversationId || currentConversation?.id
      if (conversationId && messages.length === 0) {
        try {
          const response = await generateTitle(conversationId)
          setCurrentConversation(prev => prev ? { ...prev, title: response.title } : null)
          setConversations(prev =>
            prev.map(c =>
              c.id === conversationId ? { ...c, title: response.title } : c
            )
          )
        } catch {
          // Title generation failure is not critical
        }
      }
    } catch (err) {
      // Remove optimistic message on error
      setMessages(prev => prev.filter(m => m.id !== tempUserMessage.id))

      if (err instanceof Error && err.message.includes('429')) {
        setError('Rate limit exceeded. Please wait a moment before sending another message.')
      } else if (err instanceof Error && err.message === 'Unauthorized') {
        setError('Session expired. Please log in again.')
      } else {
        setError(err instanceof Error ? err.message : 'Failed to send message')
      }
    } finally {
      setIsSending(false)
      // Streaming state already cleared in success path, only clear here if error occurred
      setStreaming(initialStreamingState)
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
    streaming,
    // Actions
    loadConversations,
    selectConversation,
    createNewConversation,
    sendChatMessage,
    sendStreamingMessage,
    deleteCurrentConversation,
    generateConversationTitle,
    clearError,
  }
}
