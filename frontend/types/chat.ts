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
};

// ============================================================================
// Streaming Types (SSE)
// ============================================================================

/** Language hint for faster agent routing */
export type LanguageHint = 'en' | 'ur' | 'auto';

/** Request for streaming chat endpoint */
export interface ChatStreamRequest {
  message: string;
  conversation_id?: string | null;
  language_hint?: LanguageHint;
  context_window?: number;
}

/** Token chunk from AI response */
export interface TokenEvent {
  type: 'token';
  content: string;
}

/** Agent handoff notification */
export interface AgentChangeEvent {
  type: 'agent_change';
  agent: string;
  icon: string;
}

/** Tool call notification */
export interface ToolCallEvent {
  type: 'tool_call';
  tool: string;
  args?: Record<string, unknown> | null;
}

/** New conversation created notification */
export interface ConversationCreatedEvent {
  type: 'conversation_created';
  conversation_id: string;
}

/** Stream completion notification */
export interface DoneEvent {
  type: 'done';
  message_id: string;
}

/** Error notification */
export interface ErrorEvent {
  type: 'error';
  message: string;
}

/** Union type for all stream events */
export type StreamEvent =
  | TokenEvent
  | AgentChangeEvent
  | ToolCallEvent
  | ConversationCreatedEvent
  | DoneEvent
  | ErrorEvent;

/** Type guard for TokenEvent */
export function isTokenEvent(event: StreamEvent): event is TokenEvent {
  return event.type === 'token';
}

/** Type guard for AgentChangeEvent */
export function isAgentChangeEvent(event: StreamEvent): event is AgentChangeEvent {
  return event.type === 'agent_change';
}

/** Type guard for ToolCallEvent */
export function isToolCallEvent(event: StreamEvent): event is ToolCallEvent {
  return event.type === 'tool_call';
}

/** Type guard for ConversationCreatedEvent */
export function isConversationCreatedEvent(event: StreamEvent): event is ConversationCreatedEvent {
  return event.type === 'conversation_created';
}

/** Type guard for DoneEvent */
export function isDoneEvent(event: StreamEvent): event is DoneEvent {
  return event.type === 'done';
}

/** Type guard for ErrorEvent */
export function isErrorEvent(event: StreamEvent): event is ErrorEvent {
  return event.type === 'error';
}
