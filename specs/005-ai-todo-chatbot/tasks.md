# Tasks: AI Todo Chatbot (Phase 3)

**Input**: Design documents from `/specs/005-ai-todo-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included as the constitution mandates 80%+ unit test coverage on core logic.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/` for source, `backend/tests/` for tests
- **Frontend**: `frontend/app/`, `frontend/hooks/`, `frontend/lib/`, `frontend/types/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and AI chatbot dependencies

- [x] T001 Add OpenAI Agents SDK dependency (`openai-agents`) to backend/pyproject.toml
- [x] T002 Add MCP SDK dependency (`mcp`) to backend/pyproject.toml
- [x] T003 [P] Add AI environment variables (AI_API_KEY, AI_BASE_URL, AI_MODEL) to backend/.env.example
- [x] T004 [P] Create backend/app/services/ai/ directory structure per plan.md
- [x] T005 [P] Create frontend/app/(protected)/chat/ directory structure per plan.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models & Migration

- [x] T006 Create Conversation model in backend/app/models/conversation.py per data-model.md
- [x] T007 [P] Create Message model in backend/app/models/message.py per data-model.md
- [x] T008 Create Alembic migration for conversations and messages tables in backend/alembic/versions/
- [x] T009 Run migration and verify tables created in Neon PostgreSQL

### AI Client Configuration

- [x] T010 Create AI client configuration with custom base_url/api_key in backend/app/services/ai/config.py per research.md
- [x] T011 Implement set_default_openai_client() call at application startup in backend/app/main.py

### Conversation Service (Repository Layer)

- [x] T012 Create ConversationService with CRUD operations in backend/app/services/conversation_service.py
- [x] T013 Implement get_user_conversations() with 100 limit in backend/app/services/conversation_service.py
- [x] T014 Implement count_user_conversations() for limit check in backend/app/services/conversation_service.py
- [x] T015 Implement add_message() with agent metadata in backend/app/services/conversation_service.py

### Rate Limiting Middleware

- [x] T016 Create RateLimiter class (5 req/60s) in backend/app/middleware/rate_limit.py
- [x] T017 Implement @rate_limit decorator for endpoints in backend/app/middleware/rate_limit.py

### Pydantic Schemas

- [x] T018 Create SendMessageRequest schema (1000 char limit) in backend/app/schemas/chat.py
- [x] T019 [P] Create MessageResponse, ChatResponse schemas in backend/app/schemas/chat.py
- [x] T020 [P] Create ConversationResponse, ConversationListResponse schemas in backend/app/schemas/chat.py

### Frontend Types

- [x] T021 Create chat types (Conversation, Message, ChatResponse) in frontend/types/chat.ts
- [x] T022 [P] Create Web Speech API type declarations in frontend/types/speech.d.ts

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks by typing "add task buy groceries" in chat

**Independent Test**: Send "add task buy milk" and verify task appears in user's task list

### Tests for User Story 1

- [x] T023 [P] [US1] Unit test for add_task MCP tool in backend/tests/unit/test_mcp_tools.py
- [x] T024 [P] [US1] Unit test for AddTaskAgent in backend/tests/unit/test_agents.py

### MCP Tool Implementation

- [x] T025 [US1] Create add_task MCP tool with @mcp.tool() decorator in backend/app/services/ai/tools/task_tools.py

### Agent Implementation

- [x] T026 [US1] Create AddTaskAgent (Elara ➕) with personality in backend/app/services/ai/agents/task_agents.py

**Checkpoint**: User Story 1 core functionality ready

---

## Phase 4: User Story 2 - Task Listing and Filtering (Priority: P1)

**Goal**: Users can ask "show my tasks" and see tasks displayed in chat

**Independent Test**: Ask "show my pending tasks" and verify ListTasksAgent (📋) displays tasks

### Tests for User Story 2

- [x] T027 [P] [US2] Unit test for list_tasks MCP tool in backend/tests/unit/test_mcp_tools.py

### MCP Tool Implementation

- [x] T028 [US2] Create list_tasks MCP tool with filters in backend/app/services/ai/tools/task_tools.py

### Agent Implementation

- [x] T029 [US2] Create ListTasksAgent (Kael 📋) with personality in backend/app/services/ai/agents/task_agents.py

**Checkpoint**: User Stories 1 AND 2 ready

---

## Phase 5: User Story 3 - Task Completion (Priority: P1)

**Goal**: Users can say "complete task 1" to mark tasks done

**Independent Test**: Say "complete task [id]" and verify task status changes

### Tests for User Story 3

- [x] T030 [P] [US3] Unit test for complete_task MCP tool in backend/tests/unit/test_mcp_tools.py
- [x] T031 [P] [US3] Unit test for uncomplete_task MCP tool in backend/tests/unit/test_mcp_tools.py

### MCP Tool Implementation

- [x] T032 [US3] Create complete_task MCP tool in backend/app/services/ai/tools/task_tools.py
- [x] T033 [US3] Create uncomplete_task MCP tool in backend/app/services/ai/tools/task_tools.py

### Agent Implementation

- [x] T034 [US3] Create CompleteTaskAgent (Nyra ✅) with personality in backend/app/services/ai/agents/task_agents.py

**Checkpoint**: Core P1 stories (create, list, complete) ready - MVP functional

---

## Phase 6: User Story 5 - Task Deletion (Priority: P2)

**Goal**: Users can say "delete task 2" to remove tasks

**Independent Test**: Say "delete task [id]" and verify task is removed

### Tests for User Story 5

- [x] T035 [P] [US5] Unit test for delete_task MCP tool in backend/tests/unit/test_mcp_tools.py

### MCP Tool Implementation

- [x] T036 [US5] Create delete_task MCP tool in backend/app/services/ai/tools/task_tools.py

### Agent Implementation

- [x] T037 [US5] Create DeleteTaskAgent (Taro 🗑️) with personality in backend/app/services/ai/agents/task_agents.py

---

## Phase 7: User Story 6 - Task Updates (Priority: P2)

**Goal**: Users can say "change task 1 priority to high" to modify tasks

**Independent Test**: Say "update task 1 priority to high" and verify change

### Tests for User Story 6

- [x] T038 [P] [US6] Unit test for update_task MCP tool in backend/tests/unit/test_mcp_tools.py

### MCP Tool Implementation

- [x] T039 [US6] Create update_task MCP tool in backend/app/services/ai/tools/task_tools.py

### Agent Implementation

- [x] T040 [US6] Create UpdateTaskAgent (Lys ✏️) with personality in backend/app/services/ai/agents/task_agents.py

---

## Phase 8: User Story 7 - Task Search (Priority: P2)

**Goal**: Users can say "find tasks about groceries" to search

**Independent Test**: Say "search for groceries" and verify matching tasks returned

### Tests for User Story 7

- [x] T041 [P] [US7] Unit test for search_tasks MCP tool in backend/tests/unit/test_mcp_tools.py

### MCP Tool Implementation

- [x] T042 [US7] Create search_tasks MCP tool in backend/app/services/ai/tools/task_tools.py

### Agent Implementation

- [x] T043 [US7] Create SearchAgent (Vera 🔍) with personality in backend/app/services/ai/agents/task_agents.py

---

## Phase 9: User Story 8 - Task Analytics (Priority: P3)

**Goal**: Users can ask "show my stats" to see productivity metrics

**Independent Test**: Ask "show my statistics" and verify AnalyticsAgent (📊) returns counts

### Tests for User Story 8

- [x] T044 [P] [US8] Unit test for get_task_analytics MCP tool in backend/tests/unit/test_mcp_tools.py

### MCP Tool Implementation

- [x] T045 [US8] Create get_task_analytics MCP tool in backend/app/services/ai/tools/task_tools.py

### Agent Implementation

- [x] T046 [US8] Create AnalyticsAgent (Orion 📊) with personality in backend/app/services/ai/agents/task_agents.py

**Checkpoint**: All 8 MCP tools and 7 task agents complete

---

## Phase 10: Agent Hierarchy (Language Agents & Orchestrator)

**Purpose**: Multi-agent routing system per research.md handoff pattern

### Language Agents

- [x] T047 Create EnglishAgent (Miyu 🇬🇧) with handoffs to task agents in backend/app/services/ai/agents/language_agents.py
- [x] T048 Create UrduAgent (Riven 🇵🇰) with handoffs to task agents in backend/app/services/ai/agents/language_agents.py

### Main Orchestrator

- [x] T049 Create MainOrchestrator (Aren 🤖) with language detection in backend/app/services/ai/agents/orchestrator.py
- [x] T050 Implement handoffs to EnglishAgent and UrduAgent in backend/app/services/ai/agents/orchestrator.py

### Agent Integration Tests

- [x] T051 Integration test for agent handoffs in backend/tests/integration/test_agent_handoffs.py
- [x] T052 Test language detection routing (English → Miyu, Urdu → Riven) in backend/tests/integration/test_agent_handoffs.py

**Checkpoint**: Full agent hierarchy operational

---

## Phase 11: Chat API Endpoints

**Purpose**: REST API for chat functionality per contracts/chat-api.yaml

### Conversation Endpoints

- [x] T053 Implement POST /chat/conversations (create) in backend/app/api/v1/chat.py
- [x] T054 Implement GET /chat/conversations (list) in backend/app/api/v1/chat.py
- [x] T055 Implement GET /chat/conversations/{id} (get with messages) in backend/app/api/v1/chat.py
- [x] T056 Implement DELETE /chat/conversations/{id} in backend/app/api/v1/chat.py

### Message Endpoint (Main Chat)

- [x] T057 Implement POST /chat/conversations/{id}/messages with rate limiting in backend/app/api/v1/chat.py
- [x] T058 Integrate MainOrchestrator for AI processing in backend/app/api/v1/chat.py
- [x] T059 Save user and assistant messages with agent metadata in backend/app/api/v1/chat.py

### Title Generation

- [x] T060 Implement POST /chat/conversations/{id}/title for AI title generation in backend/app/api/v1/chat.py

### API Router Registration

- [x] T061 Register chat router in backend/app/api/v1/__init__.py
- [x] T062 Add chat routes to main FastAPI app in backend/app/main.py

### API Integration Tests

- [x] T063 Integration test for chat endpoints in backend/tests/integration/test_chat_endpoints.py
- [x] T064 Test rate limiting (5 msg/min) in backend/tests/integration/test_chat_endpoints.py
- [x] T065 Test 1000 char message limit in backend/tests/integration/test_chat_endpoints.py
- [x] T066 Test 100 conversation limit in backend/tests/integration/test_chat_endpoints.py

**Checkpoint**: Backend API complete

---

## Phase 12: User Story 9 - Conversation Persistence (Priority: P2)

**Goal**: Chat history saved and restored across sessions

**Independent Test**: Have conversation, close browser, reopen, verify history restored

### Frontend Implementation

- [x] T067 [US9] Create chat-client.ts with API functions in frontend/lib/chat-client.ts
- [x] T068 [US9] Create useChat hook for conversation state in frontend/hooks/useChat.ts
- [x] T069 [US9] Create ConversationList component (sidebar) in frontend/app/(protected)/chat/components/ConversationList.tsx
- [x] T070 [US9] Implement conversation selection and history loading in frontend/app/(protected)/chat/components/ConversationList.tsx

---

## Phase 13: User Story 10 - Agent Icon Display (Priority: P2)

**Goal**: Each AI response shows the responding agent's icon

**Independent Test**: Send different commands, verify correct agent icon appears

### Frontend Implementation

- [x] T071 [US10] Create AgentMessage component with icon display in frontend/app/(protected)/chat/components/AgentMessage.tsx
- [x] T072 [US10] Create MessageThread component in frontend/app/(protected)/chat/components/MessageThread.tsx
- [x] T073 [US10] Display agent_name and agent_icon from API response in frontend/app/(protected)/chat/components/AgentMessage.tsx

---

## Phase 14: User Story 4 - Voice Input (Priority: P2)

**Goal**: Users can tap microphone and speak commands

**Independent Test**: Click mic, speak "add task call mom", verify task created

### Voice Input Implementation

- [x] T074 [US4] Create useVoiceInput hook with Web Speech API in frontend/hooks/useVoiceInput.ts
- [x] T075 [US4] Implement language toggle (en-US, ur-PK) in frontend/hooks/useVoiceInput.ts
- [x] T076 [US4] Create VoiceInputButton component in frontend/app/(protected)/chat/components/VoiceInputButton.tsx
- [x] T077 [US4] Add visual feedback during recording in frontend/app/(protected)/chat/components/VoiceInputButton.tsx
- [x] T078 [US4] Implement graceful degradation for Firefox in frontend/hooks/useVoiceInput.ts

---

## Phase 15: Chat UI Assembly

**Purpose**: Assemble all chat components with glass theme styling

### Core Components

- [x] T079 Create ChatContainer with glass theme in frontend/app/(protected)/chat/components/ChatContainer.tsx
- [x] T080 Create ChatInput with voice button integration in frontend/app/(protected)/chat/components/ChatInput.tsx
- [x] T081 Create chat page layout in frontend/app/(protected)/chat/layout.tsx
- [x] T082 Create main chat page in frontend/app/(protected)/chat/page.tsx

### Glass Theme Styling

- [x] T083 Apply glass theme CSS (bg-black/30 backdrop-blur-xl border-white/10) to all chat components
- [x] T084 Style user messages (bg-aura-purple/20) in frontend/app/(protected)/chat/components/AgentMessage.tsx
- [x] T085 Style assistant messages (bg-white/5) in frontend/app/(protected)/chat/components/AgentMessage.tsx

### Navigation Integration

- [x] T086 Add chat icon to navigation bar linking to /chat in frontend/components/navigation

**Checkpoint**: Full frontend complete

---

## Phase 16: Polish & Cross-Cutting Concerns

**Purpose**: Final quality improvements

### Testing

- [x] T087 [P] Unit test for rate limiter in backend/tests/unit/test_rate_limiter.py
- [x] T088 [P] Verify all MCP tools filter by user_id (isolation test) in backend/tests/unit/test_mcp_tools.py

### Error Handling

- [x] T089 Add user-friendly error messages for AI service failures in backend/app/services/ai/orchestrator.py
- [x] T090 Add error boundary for chat component failures in frontend/app/(protected)/chat/

### Documentation

- [x] T091 Update backend/.env.example with all AI chatbot variables
- [x] T092 Verify quickstart.md instructions work end-to-end

### Deployment Preparation

- [x] T093 Add AI environment variables to HF Spaces secrets
- [x] T094 Verify backend deployment with AI dependencies
- [x] T095 Verify frontend deployment with chat routes

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ─────────────────────────────────────────────────────────────►
                 │
Phase 2 (Foundational) ──────────────────────────────────────────────────────►
                         │
                         ├── Phase 3-9 (MCP Tools & Task Agents) ────────────►
                         │                                          │
                         │                                          ▼
                         │                              Phase 10 (Agent Hierarchy)
                         │                                          │
                         │                                          ▼
                         │                              Phase 11 (Chat API)
                         │                                          │
                         ├── Phase 12-14 (Frontend Stories) ────────┤
                         │                                          │
                         │                                          ▼
                         │                              Phase 15 (UI Assembly)
                         │                                          │
                         └──────────────────────────────────────────►
                                                                    │
                                                        Phase 16 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Parallel With |
|-------|------------|-------------------|
| US1 (Create) | Foundational | US2, US3 |
| US2 (List) | Foundational | US1, US3 |
| US3 (Complete) | Foundational | US1, US2 |
| US5 (Delete) | Foundational | US6, US7, US8 |
| US6 (Update) | Foundational | US5, US7, US8 |
| US7 (Search) | Foundational | US5, US6, US8 |
| US8 (Analytics) | Foundational | US5, US6, US7 |
| US4 (Voice) | Foundational | US9, US10 |
| US9 (Persistence) | Chat API | US10 |
| US10 (Icons) | Chat API | US9 |

### Parallel Opportunities

**Backend MCP Tools (T025-T046)**: All 8 tools can be developed in parallel
**Backend Task Agents (T026-T046)**: All 7 task agents can be developed in parallel
**Frontend Components (T067-T086)**: Most components can be developed in parallel

---

## Parallel Example: MCP Tools

```bash
# Launch all MCP tool implementations in parallel:
Task: "Create add_task MCP tool in backend/app/services/ai/tools/task_tools.py"
Task: "Create list_tasks MCP tool in backend/app/services/ai/tools/task_tools.py"
Task: "Create complete_task MCP tool in backend/app/services/ai/tools/task_tools.py"
Task: "Create delete_task MCP tool in backend/app/services/ai/tools/task_tools.py"
Task: "Create update_task MCP tool in backend/app/services/ai/tools/task_tools.py"
Task: "Create uncomplete_task MCP tool in backend/app/services/ai/tools/task_tools.py"
Task: "Create search_tasks MCP tool in backend/app/services/ai/tools/task_tools.py"
Task: "Create get_task_analytics MCP tool in backend/app/services/ai/tools/task_tools.py"
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phases 3-5: US1, US2, US3 (create, list, complete)
4. Complete Phase 10: Agent Hierarchy
5. Complete Phase 11: Chat API
6. **STOP and VALIDATE**: Test core chat functionality
7. Deploy MVP with basic task management via chat

### Incremental Delivery

1. **MVP**: Setup + Foundational + US1-3 + Agents + API → Basic chat works
2. **+Delete/Update**: Add US5, US6 → Full CRUD via chat
3. **+Search/Analytics**: Add US7, US8 → Advanced features
4. **+Frontend**: Add US4, US9, US10 → Full UI with voice
5. **+Polish**: Phase 16 → Production ready

### Suggested MVP Scope

**Minimum Viable Product**: Phases 1-5, 10-11
- 3 MCP tools (add, list, complete)
- 3 task agents + 2 language agents + orchestrator
- Chat API endpoints
- ~40 tasks

---

## Summary

| Metric | Count | Completed |
|--------|-------|-----------|
| Total Tasks | 95 | 95 ✅ |
| Setup Tasks | 5 | 5 ✅ |
| Foundational Tasks | 17 | 17 ✅ |
| US1 (Create) Tasks | 4 | 4 ✅ |
| US2 (List) Tasks | 3 | 3 ✅ |
| US3 (Complete) Tasks | 5 | 5 ✅ |
| US5 (Delete) Tasks | 3 | 3 ✅ |
| US6 (Update) Tasks | 3 | 3 ✅ |
| US7 (Search) Tasks | 3 | 3 ✅ |
| US8 (Analytics) Tasks | 3 | 3 ✅ |
| Agent Hierarchy Tasks | 6 | 6 ✅ |
| Chat API Tasks | 14 | 14 ✅ |
| US9 (Persistence) Tasks | 4 | 4 ✅ |
| US10 (Icons) Tasks | 3 | 3 ✅ |
| US4 (Voice) Tasks | 5 | 5 ✅ |
| UI Assembly Tasks | 8 | 8 ✅ |
| Polish Tasks | 9 | 9 ✅ |
| Parallel Opportunities | 40+ tasks marked [P] | - |

**Status: COMPLETE** 🎉

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All MCP tools MUST filter by user_id for isolation
- Agent personalities defined in spec.md must be implemented exactly
