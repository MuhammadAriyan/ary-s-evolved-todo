---
id: "0002"
title: "Chatbot Optimization Implementation Plan"
stage: plan
date: 2026-01-15
surface: agent
model: claude-opus-4-5-thinking
feature: 006-chatbot-optimization
branch: 006-chatbot-optimization
user: ary
command: /sp.plan
labels: ["architecture", "streaming", "sse", "mobile-responsive", "agent-simplification"]
links:
  spec: specs/006-chatbot-optimization/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-chatbot-optimization/plan.md
  - specs/006-chatbot-optimization/research.md
  - specs/006-chatbot-optimization/data-model.md
  - specs/006-chatbot-optimization/quickstart.md
  - specs/006-chatbot-optimization/contracts/chat-stream.openapi.yaml
tests:
  - null
---

## Prompt

/sp.plan for AI Chatbot Performance & UX Optimization (006-chatbot-optimization)

User provided detailed architecture analysis showing:
- Current 3-level agent hierarchy (Orchestrator → Language Agents → 7 Task Agents)
- Problems: 2 handoffs causing latency and ~20% routing errors, no streaming, full history token waste
- Proposed 2-level hierarchy (Orchestrator → Language Agents with MCP tools)
- Key decisions: SSE streaming, last 6 messages context, unified first-message endpoint

Implementation components identified:
1. Backend streaming orchestrator (Runner.run_streamed())
2. SSE endpoint (POST /api/v1/chat/stream)
3. Simplified agents (delete task_agents.py, add tools to language agents)
4. Context window service
5. Frontend streaming client
6. Mobile responsive UI
7. Skeleton loaders

## Response snapshot

Created comprehensive implementation plan with:

**Phase 0 - Research** (research.md):
- OpenAI Agents SDK streaming patterns
- FastAPI SSE implementation
- Agent hierarchy simplification rationale
- Context window strategy (last 6 messages)
- First message flow design
- Mobile responsive strategy

**Phase 1 - Design**:
- data-model.md: Runtime structures (StreamEvent, ContextWindow, LanguageHint)
- contracts/chat-stream.openapi.yaml: SSE endpoint OpenAPI spec
- quickstart.md: Development setup and testing guide

**Constitution Check**: PASSED
- All principles satisfied
- Existing MCP tool deviation (8 vs 5) documented but not introduced by this feature

**Files to Modify**: 14 files identified
- 1 DELETE (task_agents.py)
- 4 MAJOR changes (orchestrator, language_agents, chat endpoint, useChat hook)
- 5 MODERATE changes (UI components)
- 3 MINOR changes (schemas, types)
- 1 NEW file (SkeletonLoaders.tsx)

## Outcome

- ✅ Impact: High - comprehensive plan for 6 critical UX fixes
- 🧪 Tests: N/A - planning phase, no code tests
- 📁 Files: 5 planning artifacts created
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: User provided excellent architecture analysis which accelerated planning. 2-level agent hierarchy is elegant solution to routing errors.

## Evaluation notes (flywheel)

- Failure modes observed: None - user input was comprehensive
- Graders run and results (PASS/FAIL): Constitution Check PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A - proceed to /sp.tasks
