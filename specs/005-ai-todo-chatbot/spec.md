# Feature Specification: AI Todo Chatbot (Phase 3)

**Feature Branch**: `005-ai-todo-chatbot`
**Created**: 2026-01-11
**Status**: Draft
**Input**: User description: "AI-powered chatbot interface for managing todos through natural language conversation with multi-agent architecture, voice input, and agent-specific icons"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation (Priority: P1)

As a user, I want to create tasks by typing natural language commands like "add task buy groceries" so that I can quickly capture tasks without navigating forms.

**Why this priority**: Task creation is the core functionality. Without it, the chatbot has no value. This enables the fundamental use case of conversational task management.

**Independent Test**: Can be fully tested by sending a chat message "add task buy milk" and verifying a new task appears in the user's task list with title "buy milk".

**Acceptance Scenarios**:

1. **Given** a logged-in user in the chat interface, **When** they type "add task buy groceries", **Then** the AddTaskAgent creates a task titled "buy groceries" and confirms creation with its icon (➕)
2. **Given** a logged-in user, **When** they type "add task meeting tomorrow at 3pm priority high", **Then** the system extracts title, due date, and priority from natural language
3. **Given** a logged-in user, **When** they type an ambiguous message like "groceries", **Then** the system asks for clarification before creating a task

---

### User Story 2 - Task Listing and Filtering (Priority: P1)

As a user, I want to ask "show my tasks" or "what's pending?" and see my tasks displayed in the chat so that I can review my workload conversationally.

**Why this priority**: Viewing tasks is equally critical as creating them. Users need to see what they've added to manage their work effectively.

**Independent Test**: Can be fully tested by asking "show my pending tasks" and verifying the ListTasksAgent (📋) displays the user's incomplete tasks.

**Acceptance Scenarios**:

1. **Given** a user with 5 pending tasks, **When** they ask "show my tasks", **Then** the ListTasksAgent displays all 5 tasks with their details
2. **Given** a user with tasks of varying priorities, **When** they ask "show high priority tasks", **Then** only high-priority tasks are displayed
3. **Given** a user with no tasks, **When** they ask "show my tasks", **Then** the system responds with a friendly "no tasks found" message

---

### User Story 3 - Task Completion (Priority: P1)

As a user, I want to say "complete task 3" or "mark buy groceries as done" so that I can update task status through conversation.

**Why this priority**: Completing tasks is essential for task management workflow. Users need to mark progress without leaving the chat.

**Independent Test**: Can be fully tested by saying "complete task [id]" and verifying the task status changes to completed.

**Acceptance Scenarios**:

1. **Given** a user with a pending task, **When** they say "complete task 1", **Then** the CompleteTaskAgent (✅) marks it complete and confirms
2. **Given** a user, **When** they say "mark buy groceries as done", **Then** the system finds the task by title and completes it
3. **Given** a user trying to complete a non-existent task, **When** they say "complete task 999", **Then** the system responds with "task not found"

---

### User Story 4 - Voice Input for Task Management (Priority: P2)

As a user, I want to tap a microphone button and speak my commands so that I can manage tasks hands-free.

**Why this priority**: Voice input significantly improves accessibility and convenience but requires the core text-based functionality to work first.

**Independent Test**: Can be fully tested by clicking the microphone button, speaking "add task call mom", and verifying the task is created.

**Acceptance Scenarios**:

1. **Given** a user on the chat page, **When** they click the microphone button and speak "show my tasks", **Then** the speech is transcribed and processed as a text command
2. **Given** a user speaking in English, **When** they use voice input, **Then** the English Agent (🇬🇧) processes the query
3. **Given** a user speaking in Urdu, **When** they use voice input, **Then** the Urdu Agent (🇵🇰) processes the query
4. **Given** a user in a noisy environment, **When** speech recognition fails, **Then** the system displays an error and suggests typing instead

---

### User Story 5 - Task Deletion (Priority: P2)

As a user, I want to say "delete task 2" or "remove buy groceries" so that I can clean up my task list conversationally.

**Why this priority**: Deletion is important for task hygiene but less frequent than creation, viewing, and completion.

**Independent Test**: Can be fully tested by saying "delete task [id]" and verifying the task is removed.

**Acceptance Scenarios**:

1. **Given** a user with an existing task, **When** they say "delete task 1", **Then** the DeleteTaskAgent (🗑️) removes it and confirms
2. **Given** a user, **When** they say "remove all completed tasks", **Then** the system asks for confirmation before bulk deletion

---

### User Story 6 - Task Updates (Priority: P2)

As a user, I want to say "change task 1 priority to high" or "update task title to new title" so that I can modify tasks without recreating them.

**Why this priority**: Updates are needed for task refinement but users can work around this by deleting and recreating.

**Independent Test**: Can be fully tested by saying "update task 1 priority to high" and verifying the change.

**Acceptance Scenarios**:

1. **Given** a user with an existing task, **When** they say "change task 1 priority to high", **Then** the UpdateTaskAgent (✏️) updates the priority
2. **Given** a user, **When** they say "rename task 1 to new title", **Then** the task title is updated
3. **Given** a user, **When** they say "set due date for task 1 to tomorrow", **Then** the due date is updated

---

### User Story 7 - Task Search (Priority: P2)

As a user, I want to say "find tasks about groceries" so that I can locate specific tasks by keyword.

**Why this priority**: Search becomes important as task lists grow but is not critical for initial usage.

**Independent Test**: Can be fully tested by saying "search for groceries" and verifying matching tasks are returned.

**Acceptance Scenarios**:

1. **Given** a user with tasks containing "groceries", **When** they say "find tasks about groceries", **Then** the SearchAgent (🔍) returns matching tasks
2. **Given** a user searching for non-existent term, **When** they search, **Then** the system responds with "no matching tasks found"

---

### User Story 8 - Task Analytics (Priority: P3)

As a user, I want to ask "how am I doing?" or "show my stats" so that I can understand my productivity patterns.

**Why this priority**: Analytics provide value but are not essential for core task management functionality.

**Independent Test**: Can be fully tested by asking "show my statistics" and verifying the AnalyticsAgent (📊) returns task counts and completion rates.

**Acceptance Scenarios**:

1. **Given** a user with task history, **When** they ask "show my stats", **Then** the AnalyticsAgent displays total tasks, completed count, completion rate, and tasks by priority
2. **Given** a new user with no tasks, **When** they ask for analytics, **Then** the system shows zero counts with encouraging message

---

### User Story 9 - Conversation Persistence (Priority: P2)

As a user, I want my chat history saved so that I can continue conversations across sessions and devices.

**Why this priority**: Persistence is important for user experience but the core functionality works without it (stateless requests).

**Independent Test**: Can be fully tested by having a conversation, closing the browser, reopening, and verifying the conversation history is restored.

**Acceptance Scenarios**:

1. **Given** a user with previous conversations, **When** they open the chat page, **Then** they see a list of past conversations in the sidebar
2. **Given** a user, **When** they select a past conversation, **Then** the full message history is displayed
3. **Given** a user, **When** they delete a conversation, **Then** it is removed from the sidebar and database

---

### User Story 10 - Agent Icon Display (Priority: P2)

As a user, I want to see which AI agent is responding (with its unique icon) so that I understand what action is being performed.

**Why this priority**: Visual feedback improves user experience and trust but the system works without it.

**Independent Test**: Can be fully tested by sending different commands and verifying the correct agent icon appears with each response.

**Acceptance Scenarios**:

1. **Given** a user creating a task, **When** the AddTaskAgent responds, **Then** the ➕ icon is displayed with the response
2. **Given** a user listing tasks, **When** the ListTasksAgent responds, **Then** the 📋 icon is displayed
3. **Given** a user speaking English, **When** the English Agent routes the query, **Then** the 🇬🇧 icon appears briefly before the task agent icon

---

### Edge Cases

- What happens when the user sends an empty message? System should prompt for input.
- What happens when voice recognition returns gibberish? System should ask user to repeat or type.
- What happens when the AI service is unavailable? System should display a friendly error message and allow manual retry; no automatic failover to backup providers.
- What happens when a user tries to access another user's tasks? System must enforce user isolation.
- What happens when the user's session expires mid-conversation? System should redirect to login.
- What happens when the user speaks a language other than English or Urdu? System should respond in English with a note about supported languages.
- What happens when task creation fails due to database error? System should inform user and suggest retry.
- What happens when MCP tool execution fails? System should return a user-friendly error and log the failure.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Chat Functionality
- **FR-001**: System MUST allow users to create tasks via natural language commands (e.g., "add task [title]")
- **FR-002**: System MUST allow users to list their tasks with optional filters (status, priority, tags)
- **FR-003**: System MUST allow users to mark tasks as completed via natural language
- **FR-004**: System MUST allow users to delete tasks via natural language
- **FR-005**: System MUST allow users to update task properties (title, description, priority, tags, due date) via natural language
- **FR-006**: System MUST allow users to uncomplete (reopen) previously completed tasks
- **FR-007**: System MUST provide task analytics (counts, completion rates, breakdowns)
- **FR-008**: System MUST allow users to search tasks by keyword
- **FR-009**: System MUST implement conversational interface for all Basic Level task features (create, read, update, delete, complete, uncomplete, search, analytics)

#### Voice & Language Support
- **FR-010**: System MUST support voice input for all commands via microphone button
- **FR-011**: System MUST support English language input (text and voice)
- **FR-012**: System MUST support Urdu language input (text and voice)

#### Agent Architecture
- **FR-013**: System MUST display the responding agent's icon with each message
- **FR-014**: System MUST route queries through a main orchestrator to appropriate language agents
- **FR-015**: System MUST route language-specific queries to appropriate task agents
- **FR-016**: System MUST use OpenAI Agents SDK for all AI agent logic and orchestration

#### MCP Server & Tools
- **FR-017**: System MUST build an MCP server using the Official MCP SDK (FastMCP)
- **FR-018**: MCP server MUST expose task operations as tools (add_task, list_tasks, complete_task, delete_task, update_task, uncomplete_task, get_task_analytics, search_tasks)
- **FR-019**: AI agents MUST use MCP tools to manage tasks (not direct database access)
- **FR-020**: MCP tools MUST be stateless and store all state in the database

#### Conversation Persistence
- **FR-021**: System MUST persist all conversations and messages to the database
- **FR-022**: System MUST allow users to view their conversation history
- **FR-023**: System MUST allow users to delete conversations
- **FR-024**: Chat endpoint MUST be stateless (no server-side session state)
- **FR-025**: Conversation state MUST be persisted to database and fetched on each request

#### Security & Access
- **FR-026**: System MUST require authentication for all chat functionality
- **FR-027**: System MUST isolate user data (users can only access their own tasks and conversations)
- **FR-028**: Chat interface MUST be accessible via a chat icon in the navigation bar

### Key Entities

- **Conversation**: Represents a chat session between user and AI. Contains user reference, title (AI-generated summary after first exchange), and timestamps. One user can have many conversations (maximum 100 per user; oldest auto-deleted when limit exceeded).
- **Message**: Represents a single message in a conversation. Contains role (user/assistant), content (maximum 1000 characters for user messages), metadata (including responding agent identifier), and timestamp. One conversation has many messages.
- **Agent**: Represents an AI agent with unique identifier, display name, icon, personality, and specialized capability.

### Agent Personalities

Each agent has a distinct personality that shapes their communication style:

| Agent | Icon | Character | Gender | Tone & Personality |
| ----- | ---- | --------- | ------ | ------------------ |
| Main Orchestrator | 🤖 | Aren | Male | Quiet, calculating, outcome-driven. Rarely reacts; always evaluates. |
| English Agent | 🇬🇧 | Miyu | Female | Calm, precise, emotionally reserved. Speaks softly, thinks sharply. |
| Urdu Agent | 🇵🇰 | Riven | Male | Direct, intense, impatient with hesitation. Thrives on momentum. |
| AddTaskAgent | ➕ | Elara | Female | Composed, structured, intellectually dominant. Values order over speed. |
| ListTasksAgent | 📋 | Kael | Male | Minimalist, detached, observant. Communicates only when necessary. |
| CompleteTaskAgent | ✅ | Nyra | Female | Smooth, persuasive, socially aware. Controls situations through words. |
| DeleteTaskAgent | 🗑️ | Taro | Male | Disciplined, grounded, stoic. Prefers consistency and restraint. |
| UpdateTaskAgent | ✏️ | Lys | Female | Curious, unconventional, playful under pressure. Enjoys disruption. |
| AnalyticsAgent | 📊 | Orion | Male | Reflective, philosophical, emotionally distant. Questions everything. |
| SearchAgent | 🔍 | Vera | Female | Self-assured, firm, quietly authoritative. Accepts no dependency. |

### MCP Tools Specification

The following tools MUST be exposed by the MCP server:

| Tool Name          | Parameters                                                        | Description                        |
| ------------------ | ----------------------------------------------------------------- | ---------------------------------- |
| add_task           | user_id, title, description?, priority?, tags?, due_date?         | Creates a new task for the user    |
| list_tasks         | user_id, status?, priority?, tag?                                 | Lists tasks with optional filters  |
| complete_task      | user_id, task_id                                                  | Marks a task as completed          |
| delete_task        | user_id, task_id                                                  | Deletes a task                     |
| update_task        | user_id, task_id, title?, description?, priority?, tags?, due_date? | Updates task properties          |
| uncomplete_task    | user_id, task_id                                                  | Reopens a completed task           |
| get_task_analytics | user_id                                                           | Returns task statistics            |
| search_tasks       | user_id, query                                                    | Searches tasks by keyword          |

## Technology Stack *(mandatory)*

| Component      | Technology                    |
| -------------- | ----------------------------- |
| Frontend       | OpenAI ChatKit                |
| Backend        | Python FastAPI                |
| AI Framework   | OpenAI Agents SDK             |
| MCP Server     | Official MCP SDK (FastMCP)    |
| ORM            | SQLModel                      |
| Database       | Neon Serverless PostgreSQL    |
| Authentication | Better Auth                   |

### Technology References (Context7)

**OpenAI Agents SDK** (`/openai/openai-agents-python`):
- Multi-agent workflows with handoffs pattern for language routing
- Agent definition with `Agent()` class, `handoffs` parameter for routing
- `Runner.run()` for async execution of agent workflows

**MCP SDK** (`/modelcontextprotocol/python-sdk`):
- FastMCP for rapid MCP server development
- `@mcp.tool()` decorator for exposing functions as MCP tools
- Stateless tool execution with database persistence

**SQLModel** (`/websites/sqlmodel_tiangolo`):
- SQLModel classes with `table=True` for database models
- `Session` for database operations
- Integration with FastAPI via dependency injection

**FastAPI** (`/websites/fastapi_tiangolo`):
- Async endpoints for chat operations
- Dependency injection for database sessions
- Pydantic models for request/response validation

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task via chat in under 5 seconds from typing to confirmation
- **SC-002**: Users can complete any task management operation (create, list, complete, delete, update, search) through natural language
- **SC-003**: Voice input successfully transcribes and processes commands with 90%+ accuracy in quiet environments
- **SC-004**: System correctly routes 95%+ of queries to the appropriate agent
- **SC-005**: Conversation history loads within 2 seconds when selecting a past conversation
- **SC-006**: System supports at least 100 concurrent chat users without degradation
- **SC-007**: Each agent response displays the correct agent icon 100% of the time
- **SC-008**: Users can access their chat history from any device after logging in
- **SC-009**: All 8 MCP tools (add, list, complete, delete, update, uncomplete, analytics, search) work correctly via chat
- **SC-010**: Glass theme styling matches existing application UI (consistent with bg-black/30 backdrop-blur-xl border-white/10 pattern)
- **SC-011**: MCP server responds to tool calls within 500ms under normal load
- **SC-012**: Stateless architecture allows horizontal scaling without session affinity
- **SC-013**: Chat API enforces rate limit of 5 messages per minute per user

## Out of Scope *(mandatory)*

The following items are explicitly excluded from this feature:

- **OS-001**: Offline chat functionality - requires service worker and local storage implementation
- **OS-002**: Languages other than English and Urdu - additional language agents not included
- **OS-003**: Voice output (text-to-speech responses) - only voice input is supported
- **OS-004**: File attachments in chat - no file upload/download capability
- **OS-005**: Group/shared conversations - conversations are single-user only
- **OS-006**: Chat export functionality - no export to PDF/JSON/etc.
- **OS-007**: Custom agent creation by users - agents are predefined
- **OS-008**: Integration with external calendar systems - no Google Calendar, Outlook, etc.
- **OS-009**: Push notifications for chat messages - no real-time notifications
- **OS-010**: Rich media responses (images, charts) - text-only responses
- **OS-011**: Conversation branching/threading - linear conversation flow only
- **OS-012**: User-customizable agent personalities - agent personalities are predefined and fixed

## Clarifications

### Session 2026-01-11

- Q: AI Provider Failover Strategy - When the configured AI provider is unavailable, how should the system behave? → A: Display error message and allow manual retry (no automatic failover)
- Q: Conversation History Retention - How long should conversation history be retained? → A: Keep last 100 conversations per user, delete oldest when limit exceeded
- Q: Message Length Limits - What is the maximum length for a single user message? → A: 1000 characters (standard conversational length)
- Q: Chat API Rate Limiting - How many chat messages per minute per user? → A: 5 messages per minute (strict, cost-conscious)
- Q: Conversation Title Generation - How should conversation titles be generated? → A: AI generates a summary title after first exchange

## Assumptions

- Users have modern browsers that support Web Speech API for voice input
- The existing authentication system (Better Auth) will be used for protecting chat routes
- The existing task database schema supports all required operations
- Users understand basic natural language commands for task management
- English is the primary language; Urdu is secondary but fully supported
- The AI service (configurable via environment variables) is OpenAI-compatible
- Network connectivity is required for all chat functionality (no offline mode)
- OpenAI Agents SDK is compatible with the configured AI provider
- Official MCP SDK (FastMCP) supports Python for server implementation
