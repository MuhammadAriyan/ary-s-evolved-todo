# Research: AI Todo Chatbot (Phase 0)

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-01-11
**Status**: Complete

## Research Questions

### 1. OpenAI Agents SDK Handoff Pattern

**Question**: How do we implement multi-agent routing with handoffs?

**Source**: Context7 `/openai/openai-agents-python`

**Findings**:

The OpenAI Agents SDK provides a `handoffs` parameter for agent-to-agent delegation:

```python
from agents import Agent, Runner
import asyncio

# Create specialized agents
spanish_agent = Agent(
    name="Spanish Agent",
    instructions="You only speak Spanish."
)

english_agent = Agent(
    name="English Agent",
    instructions="You only speak English."
)

# Create triage agent that routes to specialists
triage_agent = Agent(
    name="Triage Agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent]
)

async def main():
    result = await Runner.run(triage_agent, "Hola, ¿cómo estás?")
    print(result.final_output)
    print(f"Handled by: {result.current_agent.name}")

asyncio.run(main())
```

**Key Points**:
- Handoffs are configured via `handoffs` parameter (list of agents)
- When handoff occurs, delegated agent receives full conversation history
- `result.current_agent.name` identifies which agent handled the request
- Pattern enables modular, single-task-focused agents

**Decision**: Use this exact pattern for our hierarchy:
- Main Orchestrator (Aren) → handoffs to [EnglishAgent, UrduAgent]
- EnglishAgent (Miyu) → handoffs to [7 task agents]
- UrduAgent (Riven) → handoffs to [7 task agents]

---

### 2. FastMCP Tool Registration

**Question**: How do we create MCP tools using the Official MCP SDK?

**Source**: Context7 `/modelcontextprotocol/python-sdk`

**Findings**:

FastMCP uses the `@mcp.tool()` decorator:

```python
from mcp.server.fastmcp import FastMCP

# Initialize server
mcp = FastMCP("Task Service", json_response=True)

# Define a tool
@mcp.tool()
def add_task(user_id: str, title: str, priority: str = "medium") -> dict:
    """Create a new task for the user.

    Args:
        user_id: The authenticated user's ID
        title: Task title
        priority: Task priority (low, medium, high)

    Returns:
        dict with task_id and success status
    """
    # Implementation here
    return {"success": True, "task_id": "123"}

# Run server
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

**Key Points**:
- `@mcp.tool()` decorator exposes functions as MCP tools
- Docstrings are used as tool descriptions (important for AI understanding)
- Type hints define parameter schemas
- `json_response=True` for JSON output format
- Supports multiple transports: stdio, streamable-http

**Decision**: Use `@mcp.tool()` decorator for all 8 task tools. Ensure comprehensive docstrings for AI comprehension.

---

### 3. Web Speech API Browser Support

**Question**: Which browsers support Web Speech API for voice input?

**Source**: caniuse.com, MDN Web Docs

**Findings**:

| Browser | Support | Notes |
|---------|---------|-------|
| Chrome | ✅ Full | Best support, webkit prefix |
| Edge | ✅ Full | Chromium-based |
| Safari | ✅ Partial | iOS 14.5+, macOS 11+ |
| Firefox | ❌ None | Not supported |
| Opera | ✅ Full | Chromium-based |

**Implementation Notes**:
```typescript
// Check for support
const isSupported = 'SpeechRecognition' in window ||
                    'webkitSpeechRecognition' in window;

// Use webkit prefix for broader support
const SpeechRecognition = window.SpeechRecognition ||
                          window.webkitSpeechRecognition;
```

**Language Support**:
- `en-US` (English): Excellent recognition
- `ur-PK` (Urdu): Supported but accuracy varies

**Decision**:
- Implement with webkit prefix for Chrome/Edge/Safari
- Hide voice button on Firefox (graceful degradation)
- Show fallback message suggesting text input

---

### 4. ChatKit Customization

**Question**: How customizable is OpenAI ChatKit for glass theme styling?

**Source**: OpenAI ChatKit documentation

**Findings**:

ChatKit provides CSS custom properties and component overrides:

```css
/* Global theme variables */
:root {
  --chatkit-bg: rgba(0, 0, 0, 0.3);
  --chatkit-border: rgba(255, 255, 255, 0.1);
  --chatkit-text: rgba(255, 255, 255, 0.9);
}

/* Component-level overrides */
.chatkit-message-user {
  background: rgba(168, 85, 247, 0.2);
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.chatkit-message-assistant {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

**Customization Options**:
- CSS variables for colors, spacing, typography
- Component class overrides
- Custom message renderers for agent icons
- Input area customization

**Decision**: Use CSS overrides to apply glass theme. Create custom `AgentMessage` component for icon display.

---

### 5. OpenAI Agents SDK with Custom Provider

**Question**: Can we use a custom AI provider (not OpenAI) with the Agents SDK?

**Source**: Context7 `/openai/openai-agents-python`

**Findings**:

The SDK supports custom OpenAI-compatible providers:

```python
from openai import AsyncOpenAI
from agents import Agent, Runner, set_default_openai_client

# Create custom client
external_client = AsyncOpenAI(
    api_key="your-api-key",
    base_url="https://your-provider.com/v1",
)

# Set as default for all agents
set_default_openai_client(external_client)

# Agents now use custom provider
agent = Agent(name="MyAgent", instructions="...")
```

**Key Points**:
- `set_default_openai_client()` configures global client
- Any OpenAI-compatible API works (OpenRouter, Together, etc.)
- Must be called before creating agents

**Decision**: Use environment variables for `AI_API_KEY` and `AI_BASE_URL`. Call `set_default_openai_client()` at application startup.

---

## Summary of Decisions

| Area | Decision |
|------|----------|
| Agent Handoffs | Use `handoffs` parameter with 3-tier hierarchy |
| MCP Tools | Use `@mcp.tool()` decorator with comprehensive docstrings |
| Voice Input | Webkit prefix, graceful degradation for Firefox |
| ChatKit Theme | CSS overrides + custom AgentMessage component |
| AI Provider | Environment variables + `set_default_openai_client()` |

## Unknowns Resolved

All Phase 0 unknowns have been resolved. Ready to proceed to Phase 1 design.

## References

- OpenAI Agents SDK: `/openai/openai-agents-python` (Context7)
- MCP Python SDK: `/modelcontextprotocol/python-sdk` (Context7)
- Web Speech API: MDN Web Docs, caniuse.com
- ChatKit: OpenAI documentation
