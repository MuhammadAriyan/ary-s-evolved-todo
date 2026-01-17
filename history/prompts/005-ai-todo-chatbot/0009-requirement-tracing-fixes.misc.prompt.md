---
id: 0009
title: Requirement Tracing and Gap Fixes
stage: misc
date: 2026-01-14
surface: agent
model: claude-opus-4-5-thinking
feature: 005-ai-todo-chatbot
branch: 005-ai-todo-chatbot
user: ary
command: /sp.trace
labels: ["requirement-tracing", "bidirectional-trace", "gap-fix", "api-alignment"]
links:
  spec: specs/005-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/schemas/chat.py
  - backend/app/api/v1/endpoints/chat.py
  - backend/app/services/ai/agents/orchestrator.py
  - backend/app/services/ai/mcp_server.py
  - .claude/agents/requirement-tracer.md
  - .claude/commands/sp.trace.md
  - .claude/skills/ai-chatbot/requirement-tracing.md
tests:
  - Manual verification of bidirectional traceability
---

## Prompt

User requested creation of a requirement tracer agent for bidirectional traceability (CODE ↔ REQUIREMENTS). After initial trace showed 0% annotation coverage but 100% functional coverage, user provided original spec revealing gaps:
1. Missing `tool_calls` in API response
2. Different endpoint structure than spec
3. MCP tool response format mismatch (`success/message` vs `status/title`)

User approved using existing project agents (api-engineer, ai-backend-engineer, chat-frontend-engineer) to fix gaps.

## Response snapshot

Created requirement tracer agent with:
- Bidirectional matching (CODE → REQ and REQ → CODE)
- Natural language query support
- Agent routing for fixes with user approval

Fixed implementation gaps via three Task subagents:
1. **api-engineer**: Added `UnifiedChatRequest`, `ToolCallInfo`, `UnifiedChatResponse` schemas; created unified `POST /api/v1/chat` endpoint
2. **ai-backend-engineer**: Added `ToolCallItem` extraction in orchestrator to populate `tool_calls` in response
3. **chat-frontend-engineer**: Updated MCP server tool responses to use `{status, title}` format

Final trace: **CODE → REQUIREMENTS = REQUIREMENTS → CODE ✅ MATCH**

## Outcome

- ✅ Impact: All 28 functional requirements now fully traced and implemented
- 🧪 Tests: Manual verification of API responses and tool call extraction
- 📁 Files: 7 files modified (4 backend, 3 agent/command/skill)
- 🔁 Next prompts: Add FR-XXX annotations to code for formal traceability
- 🧠 Reflection: Initial trace only checked annotations; deep dive revealed functional implementation was complete but API format mismatched spec

## Evaluation notes (flywheel)

- Failure modes observed: Annotation-only checking missed functional implementation; spec comparison revealed format mismatches
- Graders run and results (PASS/FAIL): PASS - bidirectional trace verified
- Prompt variant (if applicable): N/A
- Next experiment: Automate spec-to-code format validation in tracer agent
