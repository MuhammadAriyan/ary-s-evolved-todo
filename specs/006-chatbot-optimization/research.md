# Research: AI Chatbot Performance & UX Optimization

**Feature**: 006-chatbot-optimization
**Date**: 2026-01-15
**Status**: Complete

## Research Tasks

### 1. OpenAI Agents SDK Streaming

**Question**: How to implement streaming with OpenAI Agents SDK?

**Decision**: Use `Runner.run_streamed()` with async iteration over stream events

**Rationale**:
- The SDK provides `Runner.run_streamed()` which returns an async generator
- Stream events include: `RawResponsesStreamEvent`, `AgentUpdatedStreamEvent`, `RunItemStreamEvent`
- This is the official way to get real-time token streaming

**Implementation Pattern**:
```python
async def stream_response(orchestrator, messages):
    result = Runner.run_streamed(orchestrator, messages)
    async for event in result.stream_events():
        if event.type == "raw_response_event":
            # Token chunk
            yield {"type": "token", "content": event.data.delta}
        elif event.type == "agent_updated_event":
            # Agent handoff
            yield {"type": "agent_change", "agent": event.data.agent.name}
    # Final result available after iteration
    final = await result.final_output()
```

**Alternatives Considered**:
- Custom streaming wrapper: Rejected - SDK already provides this
- WebSocket instead of SSE: Rejected - SSE simpler, sufficient for unidirectional streaming

---

### 2. FastAPI SSE Implementation

**Question**: Best practice for Server-Sent Events in FastAPI?

**Decision**: Use `StreamingResponse` with `text/event-stream` media type

**Rationale**:
- Native FastAPI support via `StreamingResponse`
- SSE format is simple: `data: {json}\n\n`
- Browser `EventSource` API handles reconnection automatically

**Implementation Pattern**:
```python
from fastapi.responses import StreamingResponse

async def sse_generator():
    async for chunk in stream_response(...):
        yield f"data: {json.dumps(chunk)}\n\n"
    yield "data: {\"type\": \"done\"}\n\n"

@router.post("/chat/stream")
async def stream_chat(...):
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )
```

**Alternatives Considered**:
- WebSocket: Rejected - overkill for unidirectional streaming
- Long polling: Rejected - inefficient, poor UX

---

### 3. Agent Hierarchy Simplification

**Question**: How to reduce handoffs while maintaining language support?

**Decision**: 2-level hierarchy - Orchestrator → Language Agents (with tools)

**Rationale**:
- Current 3-level hierarchy causes ~20% routing errors
- Task agents are redundant - language agents can use tools directly
- Single handoff reduces latency and error chance
- Language agents already understand intent; they can call tools directly

**New Architecture**:
```
User Message + Language Hint
       │
       ▼
┌─────────────┐
│   Aren 🤖   │  Orchestrator (fast routing)
└──────┬──────┘
       │ single handoff
       ▼
┌─────────────────────┐  ┌─────────────────────┐
│      Miyu 🇬🇧        │  │      Riven 🇵🇰        │
│  + ALL MCP Tools    │  │  + ALL MCP Tools    │
└─────────────────────┘  └─────────────────────┘
```

**Changes Required**:
1. Delete `task_agents.py`
2. Add `mcp_servers=[mcp_server]` to language agents
3. Merge task agent instructions into language agent prompts
4. Update orchestrator to pass MCP server to language agents

**Alternatives Considered**:
- Keep task agents, improve routing: Rejected - fundamental architecture issue
- Single agent (no orchestrator): Rejected - need language-specific personas

---

### 4. Context Window Strategy

**Question**: How many messages to include for context?

**Decision**: Last 6 messages (configurable)

**Rationale**:
- 6 messages = 3 user + 3 assistant turns
- Sufficient for "that task" references in typical conversations
- Predictable token cost (~2000 tokens average)
- Simple sliding window implementation

**Implementation**:
```python
def get_optimized_context(conversation_id: str, window_size: int = 6) -> list[dict]:
    messages = get_messages(conversation_id)
    return messages[-window_size:] if len(messages) > window_size else messages
```

**Alternatives Considered**:
- Last 10 messages: Rejected - higher token cost, diminishing returns
- Token budget (2000): Rejected - complex to implement, variable message count
- Summary + recent: Rejected - extra LLM call adds latency

---

### 5. First Message Flow

**Question**: How to handle first message without existing conversation?

**Decision**: Unified endpoint that auto-creates conversation

**Rationale**:
- Single atomic operation reduces complexity
- No race conditions between create and send
- Frontend doesn't need to manage conversation creation separately

**Implementation**:
```python
@router.post("/chat/stream")
async def stream_chat(
    request: ChatStreamRequest,  # conversation_id is optional
    user: User = Depends(get_current_user)
):
    if not request.conversation_id:
        # Auto-create conversation
        conversation = await create_conversation(user.id)
        request.conversation_id = conversation.id
    # Continue with streaming...
```

**Frontend Flow**:
1. User sends message (no conversation selected)
2. Call `/chat/stream` without `conversation_id`
3. Backend creates conversation, streams response
4. Response includes `conversation_id` in first event
5. Frontend updates conversation list, auto-selects new conversation

---

### 6. Mobile Responsive Strategy

**Question**: How to make chat interface mobile-friendly?

**Decision**: Tailwind breakpoints with collapsible sidebar

**Rationale**:
- Tailwind already in use, consistent with existing codebase
- Collapsible sidebar maximizes chat area on mobile
- 44px touch targets follow Apple HIG guidelines

**Breakpoints**:
- `< 640px` (sm): Mobile - sidebar hidden, hamburger menu
- `640px - 1024px` (md): Tablet - sidebar collapsible
- `> 1024px` (lg): Desktop - sidebar always visible

**Key Changes**:
- Sidebar: `hidden md:block` with slide-out drawer on mobile
- Input: Bottom-anchored, full width on mobile
- Messages: Reduced padding, larger touch targets
- Buttons: Minimum 44px height/width

---

### 7. Skeleton Loading Strategy

**Question**: How to implement skeleton loaders for fast perceived load?

**Decision**: CSS-based skeleton components with Tailwind animate-pulse

**Rationale**:
- No additional dependencies
- Consistent with existing glass theme
- Fast to render (no JS required for animation)

**Implementation**:
```tsx
// ConversationListSkeleton
<div className="animate-pulse space-y-2">
  {[...Array(5)].map((_, i) => (
    <div key={i} className="h-12 bg-white/10 rounded-lg" />
  ))}
</div>

// MessageSkeleton
<div className="animate-pulse flex gap-3">
  <div className="w-8 h-8 bg-white/10 rounded-full" />
  <div className="flex-1 space-y-2">
    <div className="h-4 bg-white/10 rounded w-3/4" />
    <div className="h-4 bg-white/10 rounded w-1/2" />
  </div>
</div>
```

---

## Summary of Decisions

| Area | Decision | Key Benefit |
|------|----------|-------------|
| Streaming | `Runner.run_streamed()` + SSE | Real-time token display |
| Agent hierarchy | 2-level (remove task agents) | 95%+ routing accuracy |
| Context | Last 6 messages | Balance context vs cost |
| First message | Unified auto-create endpoint | Single atomic operation |
| Mobile | Tailwind breakpoints + collapsible sidebar | Full mobile support |
| Loading | CSS skeleton with animate-pulse | Fast perceived load |

## Unresolved Items

None - all technical decisions resolved.
