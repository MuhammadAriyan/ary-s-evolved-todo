/**
 * Chat API client for AI Todo Chatbot
 */
import { apiClient } from './api-client'
import type {
  Conversation,
  ConversationWithMessages,
  ConversationListResponse,
  ChatResponse,
  SendMessageRequest,
  TitleGenerationResponse,
} from '@/types/chat'

const CHAT_BASE = '/api/v1/chat'

/**
 * Create a new conversation
 */
export async function createConversation(): Promise<Conversation> {
  return apiClient.post<Conversation>(`${CHAT_BASE}/conversations`, {})
}

/**
 * List user conversations with pagination
 */
export async function listConversations(
  limit: number = 50,
  offset: number = 0
): Promise<ConversationListResponse> {
  return apiClient.get<ConversationListResponse>(
    `${CHAT_BASE}/conversations?limit=${limit}&offset=${offset}`
  )
}

/**
 * Get a conversation with all its messages
 */
export async function getConversation(
  conversationId: string
): Promise<ConversationWithMessages> {
  return apiClient.get<ConversationWithMessages>(
    `${CHAT_BASE}/conversations/${conversationId}`
  )
}

/**
 * Delete a conversation
 */
export async function deleteConversation(
  conversationId: string
): Promise<{ success: boolean; message: string }> {
  return apiClient.delete<{ success: boolean; message: string }>(
    `${CHAT_BASE}/conversations/${conversationId}`
  )
}

/**
 * Send a message and get AI response
 */
export async function sendMessage(
  conversationId: string,
  content: string,
  language: 'en-US' | 'ur-PK' = 'en-US'
): Promise<ChatResponse> {
  const request: SendMessageRequest = { content, language }
  return apiClient.post<ChatResponse>(
    `${CHAT_BASE}/conversations/${conversationId}/messages`,
    request
  )
}

/**
 * Generate a title for a conversation
 */
export async function generateTitle(
  conversationId: string
): Promise<TitleGenerationResponse> {
  return apiClient.post<TitleGenerationResponse>(
    `${CHAT_BASE}/conversations/${conversationId}/title`,
    {}
  )
}

/**
 * Chat client object for convenient access
 */
export const chatClient = {
  createConversation,
  listConversations,
  getConversation,
  deleteConversation,
  sendMessage,
  generateTitle,
}
