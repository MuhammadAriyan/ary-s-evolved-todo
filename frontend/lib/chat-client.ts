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
  ChatStreamRequest,
  StreamEvent,
  LanguageHint,
} from '@/types/chat'

const CHAT_BASE = '/api/v1/chat'

// CRITICAL: For chat streaming, we MUST bypass Vercel proxy because it strips Authorization headers
// Use direct HuggingFace URL in production, localhost in development
const API_URL = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
  ? 'https://maryanrar-ary-todo-backend.hf.space' // Production: direct to HuggingFace (CORS configured)
  : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000' // Development: use localhost

// For non-streaming endpoints, use Vercel proxy (works fine for regular requests)
const API_URL_PROXY = typeof window !== 'undefined' && window.location.hostname !== 'localhost'
  ? '' // Production: use relative URLs to leverage Vercel proxy
  : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000' // Development: use localhost

/**
 * Fetch with exponential backoff retry logic
 * Retries: 1s, 2s, 4s (max 3 retries)
 * Skips 4xx errors (client errors should not be retried)
 */
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries: number = 3
): Promise<Response> {
  let lastError: Error | null = null

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, options)

      // Don't retry 4xx errors (client errors)
      if (response.status >= 400 && response.status < 500) {
        return response
      }

      // Return successful responses
      if (response.ok) {
        return response
      }

      // 5xx errors - retry with exponential backoff
      if (attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 1000 // 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, delay))
        continue
      }

      return response
    } catch (error) {
      lastError = error instanceof Error ? error : new Error('Unknown error')

      // Don't retry on abort
      if (error instanceof DOMException && error.name === 'AbortError') {
        throw error
      }

      // Retry network errors with exponential backoff
      if (attempt < maxRetries) {
        const delay = Math.pow(2, attempt) * 1000 // 1s, 2s, 4s
        await new Promise(resolve => setTimeout(resolve, delay))
        continue
      }
    }
  }

  throw lastError || new Error('Max retries exceeded')
}

/**
 * Create a new conversation
 * Uses apiClient which goes through Vercel proxy (works for non-streaming)
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
  streamMessage,
}

/**
 * Stream a message and receive AI response via SSE
 *
 * @param message - The user's message content
 * @param options - Optional parameters for streaming
 * @param token - Auth token for the request
 * @yields StreamEvent objects as they arrive
 */
export async function* streamMessage(
  message: string,
  options: {
    conversationId?: string | null;
    languageHint?: LanguageHint;
    contextWindow?: number;
    signal?: AbortSignal;
  } = {},
  token?: string
): AsyncGenerator<StreamEvent, void, unknown> {
  const request: ChatStreamRequest = {
    message,
    conversation_id: options.conversationId ?? null,
    language_hint: options.languageHint ?? 'auto',
    context_window: options.contextWindow ?? 6,
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // Use direct fetch for streaming (no retry, no timeout)
  // Streaming connections need to stay open indefinitely while AI processes
  let response: Response
  try {
    response = await fetch(`${API_URL}${CHAT_BASE}/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify(request),
      signal: options.signal,
      // Keep connection alive - no timeout
      keepalive: true,
    })
  } catch (error) {
    // Handle network errors (offline, DNS failure, etc.)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Network error: Please check your internet connection')
    }
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new Error('Request cancelled')
    }
    throw error
  }

  if (!response.ok) {
    // Log detailed error information for debugging
    console.error('🔴 Chat stream error:', {
      status: response.status,
      statusText: response.statusText,
      url: response.url,
      headers: Object.fromEntries(response.headers.entries()),
    })

    // Try to get error details from response body
    let errorDetail = response.statusText
    try {
      const errorData = await response.json()
      errorDetail = errorData.detail || errorData.message || response.statusText
      console.error('🔴 Error response body:', errorData)
    } catch (e) {
      // Response body is not JSON, use statusText
      console.error('🔴 Could not parse error response:', e)
    }

    // Create detailed error messages
    if (response.status === 401) {
      throw new Error(`Auth failed (401): ${errorDetail}. Token present: ${!!token}`)
    }
    if (response.status === 404) {
      throw new Error(`Endpoint not found (404): ${response.url}`)
    }
    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please wait a moment.')
    }
    if (response.status === 403) {
      throw new Error(`Access forbidden (403): ${errorDetail}. Check CORS configuration.`)
    }
    throw new Error(`Chat error (${response.status}): ${errorDetail}`)
  }

  const reader = response.body?.getReader()
  if (!reader) {
    throw new Error('No response body')
  }

  const decoder = new TextDecoder()
  let buffer = ''
  let eventCount = 0

  alert('🟢 STREAM STARTED - Check console now!')
  console.log('🟢 Stream started, reading data...')

  try {
    while (true) {
      let result: ReadableStreamReadResult<Uint8Array>
      try {
        result = await reader.read()
      } catch (error) {
        alert('🔴 STREAM READ ERROR: ' + error)
        console.error('🔴 Stream read error:', error)
        // Handle stream read errors (connection dropped, etc.)
        if (error instanceof TypeError) {
          throw new Error('Connection lost during streaming')
        }
        throw error
      }

      const { done, value } = result

      if (done) {
        alert(`🟢 STREAM ENDED - Got ${eventCount} events`)
        console.log(`🟢 Stream ended. Total events: ${eventCount}`)
        break
      }

      const chunk = decoder.decode(value, { stream: true })
      console.log('📦 Received chunk:', chunk.substring(0, 100))
      buffer += chunk

      // Process complete SSE messages (separated by double newlines)
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || '' // Keep incomplete message in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6) // Remove 'data: ' prefix
          try {
            const event = JSON.parse(jsonStr) as StreamEvent
            console.log('✅ Parsed event:', event.type)
            eventCount++
            yield event
          } catch (e) {
            console.error('🔴 Failed to parse SSE event:', jsonStr, e)
          }
        }
      }
    }
  } catch (error) {
    console.error('🔴 Stream processing error:', error)
    throw error
  }

    // Process any remaining data in buffer
    if (buffer.startsWith('data: ')) {
      const jsonStr = buffer.slice(6)
      try {
        const event = JSON.parse(jsonStr) as StreamEvent
        yield event
      } catch {
        // Ignore incomplete final message
      }
    }
  } finally {
    reader.releaseLock()
  }
}
