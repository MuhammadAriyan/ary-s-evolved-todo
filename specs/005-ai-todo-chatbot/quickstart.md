# Quickstart: AI Todo Chatbot

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-01-11

## Prerequisites

- Python 3.12+
- Node.js 18+
- UV (Python package manager)
- pnpm (Node package manager)
- Neon PostgreSQL database (existing)
- AI API key (OpenAI-compatible provider)

## Environment Setup

### 1. Backend Environment Variables

Create/update `backend/.env`:

```bash
# Existing variables
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
BETTER_AUTH_SECRET=your-secret

# New AI Chatbot variables
AI_API_KEY=your-openai-compatible-api-key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini

# Optional
DEBUG=true
```

### 2. Frontend Environment Variables

Create/update `frontend/.env.local`:

```bash
# Existing
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

# No new variables required for chat
```

## Installation

### Backend

```bash
cd backend

# Install dependencies (adds openai-agents, mcp)
uv sync

# Run database migration
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

## Verify Installation

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### 2. Check AI Configuration

```bash
curl http://localhost:8000/api/v1/debug/ai-health
# Expected: {"healthy": true, "model": "gpt-4o-mini"}
```

### 3. Check Chat Endpoints

```bash
# Get auth token first (use your existing auth flow)
TOKEN="your-jwt-token"

# Create conversation
curl -X POST http://localhost:8000/api/v1/chat/conversations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Expected: {"id": "uuid", "title": null, ...}
```

### 4. Test Voice Input (Browser)

1. Open http://localhost:3000/chat
2. Click microphone button
3. Allow microphone permission
4. Speak "add task buy groceries"
5. Verify transcription appears

## Project Structure

```
backend/
├── app/
│   ├── api/v1/
│   │   └── chat.py           # Chat endpoints
│   ├── models/
│   │   ├── conversation.py   # Conversation model
│   │   └── message.py        # Message model
│   ├── services/
│   │   └── ai/
│   │       ├── config.py     # AI client setup
│   │       ├── agents/       # 10 AI agents
│   │       └── tools/        # 8 MCP tools
│   └── middleware/
│       └── rate_limit.py     # 5 msg/min limiter

frontend/
├── app/(protected)/chat/
│   ├── page.tsx              # Chat page
│   └── components/           # Chat UI components
└── hooks/
    └── useVoiceInput.ts      # Voice input hook
```

## Development Workflow

### Adding a New MCP Tool

1. Add tool function in `backend/app/services/ai/tools/task_tools.py`:
```python
@mcp.tool()
async def my_new_tool(user_id: str, param: str) -> dict:
    """Tool description for AI."""
    # Implementation
    return {"success": True}
```

2. Add to tool registry
3. Write unit test in `backend/tests/unit/test_mcp_tools.py`

### Adding a New Agent

1. Create agent in `backend/app/services/ai/agents/`:
```python
from agents import Agent

my_agent = Agent(
    name="AgentName",
    instructions="Agent personality and behavior...",
    tools=[my_tool],
)
```

2. Add to parent agent's `handoffs` list
3. Write test in `backend/tests/unit/test_agents.py`

### Modifying Chat UI

1. Components in `frontend/app/(protected)/chat/components/`
2. Follow glass theme pattern:
```tsx
className="bg-black/30 backdrop-blur-xl border border-white/10"
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_mcp_tools.py

# Run with coverage
uv run pytest --cov=app
```

### Frontend Tests

```bash
cd frontend

# Run tests
pnpm test

# Run with watch
pnpm test:watch
```

## Common Issues

### "AI API key not configured"

Ensure `AI_API_KEY` is set in `backend/.env` and restart the server.

### "Rate limit exceeded"

Wait 60 seconds. Rate limit is 5 messages per minute per user.

### "Voice input not working"

- Check browser compatibility (Chrome/Edge/Safari only)
- Ensure microphone permission is granted
- Try HTTPS (required for some browsers)

### "Conversation not found"

- Verify you're authenticated
- Check conversation belongs to current user
- Conversation may have been deleted

## Deployment

See `deployment-engineer` agent for production deployment to:
- Backend: Hugging Face Spaces
- Frontend: Vercel

## Resources

- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Project Spec](./spec.md)
- [Implementation Plan](./plan.md)
