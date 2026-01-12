/**
 * Chat types for AI Todo Chatbot
 */

/** Message role in a conversation */
export type MessageRole = 'user' | 'assistant' | 'system';

/** Supported input languages */
export type InputLanguage = 'en-US' | 'ur-PK';

/** A single message in a conversation */
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  agent_name?: string | null;
  agent_icon?: string | null;
  created_at: string;
}

/** A conversation (chat session) */
export interface Conversation {
  id: string;
  title?: string | null;
  created_at: string;
  updated_at: string;
}

/** Conversation with messages loaded */
export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

/** Request to send a message */
export interface SendMessageRequest {
  content: string;
  language?: InputLanguage;
}

/** Response from sending a message */
export interface ChatResponse {
  message: Message;
  agent_name: string;
  agent_icon: string;
}

/** Response for listing conversations */
export interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
  limit: number;
  offset: number;
}

/** Response for title generation */
export interface TitleGenerationResponse {
  title: string;
}

/** Error response from API */
export interface ChatErrorResponse {
  detail: string;
}

/** Agent information for display */
export interface AgentInfo {
  name: string;
  icon: string;
  description?: string;
}

/** Known agents in the system */
export const AGENTS: Record<string, AgentInfo> = {
  'Aren': { name: 'Aren', icon: '🤖', description: 'Main Orchestrator' },
  'Miyu': { name: 'Miyu', icon: '🇬🇧', description: 'English Agent' },
  'Riven': { name: 'Riven', icon: '🇵🇰', description: 'Urdu Agent' },
  'Elara': { name: 'Elara', icon: '➕', description: 'Task Creator' },
  'Kael': { name: 'Kael', icon: '📋', description: 'Task Lister' },
  'Nyra': { name: 'Nyra', icon: '✅', description: 'Task Completer' },
  'Taro': { name: 'Taro', icon: '🗑️', description: 'Task Deleter' },
  'Lys': { name: 'Lys', icon: '✏️', description: 'Task Updater' },
  'Orion': { name: 'Orion', icon: '📊', description: 'Analytics' },
  'Vera': { name: 'Vera', icon: '🔍', description: 'Search' },
};
