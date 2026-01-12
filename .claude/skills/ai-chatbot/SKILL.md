---
name: ai-chatbot
description: Comprehensive patterns for building AI chatbots with OpenAI Agents SDK, MCP tools, FastAPI endpoints, and glass-themed UI. Use when implementing chat features, agent hierarchies, or debugging AI behavior.
---

# AI Chatbot Development Skill

This skill provides patterns and best practices for the AI Todo Chatbot feature.

## Included Patterns

1. **ai-chatbot-setup.md** - OpenAI Agents SDK configuration
2. **mcp-tools-pattern.md** - MCP @function_tool patterns
3. **agent-hierarchy-design.md** - Multi-agent handoff patterns
4. **fastapi-chat-endpoints.md** - Chat API endpoint patterns
5. **sqlmodel-patterns.md** - Database model patterns
6. **chatkit-theming.md** - Glass theme CSS overrides
7. **voice-input-integration.md** - Web Speech API patterns
8. **agent-testing-patterns.md** - AI testing strategies
9. **debugging-patterns.md** - AI debugging strategies
10. **requirement-tracing.md** - Traceability patterns

## Quick Reference

### Agent Hierarchy
```
Main Orchestrator (Aren 🤖)
├── English Agent (Miyu 🇬🇧)
│   └── Task Agents (7 specialized)
└── Urdu Agent (Riven 🇵🇰)
    └── Task Agents (shared)
```

### MCP Tools (8 total)
- add_task, list_tasks, complete_task, delete_task
- update_task, uncomplete_task, get_task_analytics, search_tasks

### Glass Theme
```tsx
className="bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl"
```

### Rate Limiting
- 5 messages per minute per user
- 1000 character message limit
- 100 conversations per user max
