# Data Model: AI Chatbot Performance & UX Optimization

**Feature**: 006-chatbot-optimization
**Date**: 2026-01-15

## Overview

This feature does NOT require database schema changes. It modifies how existing entities are used and adds new runtime concepts.

## Existing Entities (No Changes)

### Conversation
```
Conversation
├── id: UUID (PK)
├── user_id: UUID (FK → users.id)
├── title: String (nullable)
├── created_at: DateTime
└── updated_at: DateTime
```

### Message
```
Message
├── id: UUID (PK)
├── conversation_id: UUID (FK → conversations.id)
├── role: Enum ["user", "assistant"]
├── content: String
├── agent_name: String (nullable) - e.g., "Miyu", "Riven"
├── agent_icon: String (nullable) - e.g., "🇬🇧", "🇵🇰"
├── created_at: DateTime
└── tool_calls: JSON (nullable) - array of tool call records
```

## New Runtime Concepts (Not Persisted)

### StreamEvent
Runtime object for SSE streaming. Not stored in database.

```typescript
type StreamEvent =
  | { type: "token"; content: string }
  | { type: "agent_change"; agent: string; icon: string }
  | { type: "tool_call"; tool: string; args: Record<string, unknown> }
  | { type: "conversation_created"; conversation_id: string }
  | { type: "done"; message_id: string }
  | { type: "error"; message: string }
```

### ContextWindow
Runtime concept for message context. Computed on each request.

```python
@dataclass
class ContextWindow:
    messages: list[Message]  # Last N messages
    window_size: int = 6     # Configurable default

    @classmethod
    def from_conversation(cls, conversation_id: str, size: int = 6) -> "ContextWindow":
        all_messages = get_messages(conversation_id)
        return cls(messages=all_messages[-size:], window_size=size)
```

### LanguageHint
Optional hint from frontend to speed up language routing.

```python
class LanguageHint(str, Enum):
    ENGLISH = "en"
    URDU = "ur"
    AUTO = "auto"  # Let orchestrator detect
```

## Agent Configuration Changes

### Before (3-level hierarchy)
```
Orchestrator (Aren)
├── handoffs: [Miyu, Riven]
└── mcp_servers: []

Language Agent (Miyu/Riven)
├── handoffs: [Elara, Kael, Nyra, Taro, Lys, Vera, Orion]
└── mcp_servers: []

Task Agent (Elara, etc.)
├── handoffs: []
└── mcp_servers: [mcp_server]
```

### After (2-level hierarchy)
```
Orchestrator (Aren)
├── handoffs: [Miyu, Riven]
└── mcp_servers: []

Language Agent (Miyu/Riven)
├── handoffs: []
└── mcp_servers: [mcp_server]  # NOW HAS TOOLS
```

## State Transitions

### Conversation State
```
[No Conversation]
    │ user sends first message
    ▼
[Created] ──────────────────────────────────────┐
    │ messages exchanged                        │
    ▼                                           │
[Active] ◄──────────────────────────────────────┘
    │ user deletes
    ▼
[Deleted]
```

### Message Streaming State
```
[Idle]
    │ user sends message
    ▼
[Sending] ─── optimistic UI update
    │ SSE connection established
    ▼
[Streaming] ─── tokens arriving
    │ "done" event received
    ▼
[Complete]
    │ error occurs
    ▼
[Error] ─── retry available
```

## Validation Rules

### ChatStreamRequest
- `message`: Required, non-empty string, max 10,000 characters
- `conversation_id`: Optional UUID, must exist if provided
- `language_hint`: Optional enum, defaults to "auto"
- `context_window`: Optional integer 1-20, defaults to 6

### StreamEvent
- `type`: Required, one of defined event types
- `content`: Required for "token" type
- `agent`/`icon`: Required for "agent_change" type
- `conversation_id`: Required for "conversation_created" type
- `message_id`: Required for "done" type

## Indexes (Existing, No Changes)

- `conversations.user_id` - Filter by user
- `messages.conversation_id` - Get messages for conversation
- `messages.created_at` - Order messages chronologically
