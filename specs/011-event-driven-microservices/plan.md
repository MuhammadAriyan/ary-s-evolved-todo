# Implementation Plan: Phase V Event-Driven Cloud Deployment

**Branch**: `011-event-driven-microservices` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/011-event-driven-microservices/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Transform the existing task management application into a cloud-native, event-driven system with real-time synchronization, precise time-based reminders, advanced recurring patterns, full-text search, audit trails, and collaborative features. Deploy to Oracle OKE (free tier) using Dapr runtime with Redpanda Cloud for event streaming, Redis for state management, and comprehensive monitoring via Prometheus/Grafana. Implement microservices architecture with WebSocket Sync Service, Notification Service, Recurring Task Service, and Audit Service communicating exclusively through events.

## Technical Context

**Language/Version**: Python 3.12+ (backend microservices), TypeScript 5.x (frontend Next.js 15+)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, Dapr Python SDK, asyncio, WebSockets
- Frontend: Next.js 15+ (App Router), React 18+, Tailwind CSS, Better Auth (JWT)
- Infrastructure: Dapr runtime, Redpanda Cloud (Kafka-compatible), Redis (managed)
**Storage**:
- Primary: Neon PostgreSQL (existing, extended with new tables for audit, search, collaboration)
- State: Redis (Dapr state store for WebSocket connections, sessions, rate limiting, distributed locks)
- Events: Redpanda Cloud (Kafka-compatible event streaming)
**Testing**: pytest (backend unit/integration), Jest/Vitest (frontend), contract tests for service boundaries
**Target Platform**: Oracle OKE (Oracle Kubernetes Engine) on Oracle Cloud free tier (2 AMD VMs + 4 Arm Ampere cores, 24GB RAM)
**Project Type**: Web application with microservices architecture (frontend + backend API + 4 event-driven microservices)
**Performance Goals**:
- Real-time sync: <2 seconds end-to-end
- Reminder delivery: <10 seconds of scheduled time
- Search response: <1 second for 10k+ tasks
- Event processing: <100ms p95 latency
- API response: <200ms p95
**Constraints**:
- Oracle Cloud free tier resource limits (CPU, memory, storage)
- Redpanda Cloud free tier or minimal paid plan
- Lightweight monitoring (Prometheus + Grafana only, defer Loki)
- At-least-once event delivery semantics
- JWT token validation across all microservices
**Scale/Scope**:
- 10,000 concurrent WebSocket connections per service instance
- 1,000 events per second through event streaming
- 100,000+ tasks per user without degradation
- 1 million audit log entries with efficient querying
- 2-10 replicas per microservice for horizontal scaling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Technology Stack Compliance

✅ **Phase V Stack Requirements**:
- Kafka: Using Redpanda Cloud (Kafka-compatible, preferred option per constitution)
- Dapr: Full capabilities (Pub/Sub, State, Bindings/cron, Secrets, Service Invocation)
- Deployment: Oracle Cloud free tier (explicitly allowed in constitution)
- No deviations from approved stack

✅ **Backend Stack**:
- Python 3.12+ with FastAPI (aligns with Phase II/III foundation)
- SQLModel ORM for database access (required by constitution)
- Neon PostgreSQL (existing, no changes to database provider)
- Better Auth with JWT tokens (required by constitution)

✅ **Frontend Stack**:
- Next.js 15+ with App Router (required by constitution)
- TypeScript 5.x (required by constitution)
- Tailwind CSS (required by constitution)

### Architecture Compliance

✅ **Event-Driven Architecture**:
- Kafka topics for: reminders, recurring tasks, audit logs, real-time sync (per constitution Section III)
- Dapr manages pub/sub, state stores, bindings, service invocation (per constitution Section II)
- Event sourcing for auditability (per constitution Section III)

✅ **Stateless Services**:
- All microservices designed stateless (per constitution Section III)
- State persisted in Redis (Dapr state store) or PostgreSQL
- Horizontal scaling ready by default

✅ **Multi-User Isolation**:
- Every database query filters by authenticated user_id (per constitution Section III)
- JWT verification middleware for all protected endpoints (per constitution Section VII)
- No cross-user data access permitted

✅ **Clean Architecture**:
- Core domain logic isolated from external concerns
- Adapters for databases, APIs, external services
- Inner layers never depend on outer layers

### MCP Tools Compliance

✅ **Exactly 5 Tools** (per constitution Section III):
1. add_task - Create a new task
2. list_tasks - Retrieve tasks for authenticated user
3. complete_task - Mark task as completed
4. delete_task - Remove a task
5. update_task - Modify task details

No additional tools added. Existing tools remain unchanged.

### Database Schema Compliance

✅ **Required Tables** (per constitution Section III):
- Users table (managed by Better Auth) ✓
- Tasks table with user_id foreign key ✓
- Conversations table for chat history ✓
- Messages table for conversation messages ✓

**New Tables for Phase V** (extensions, not replacements):
- Audit logs table (for event-driven audit trail)
- Search index table (tsvector columns for full-text search)
- Scheduled reminders table (for Dapr Bindings integration)
- Friend connections table (for collaboration features)
- Collaboration groups table (for group task management)
- Group memberships table (for permission management)
- Task assignments table (for collaborative task assignment)
- Task comments table (for task discussions)
- Direct messages table (for friend messaging)

### Security Compliance

✅ **Security Requirements** (per constitution Section VII):
- JWT verification middleware for all protected routes
- Input validation on all endpoints
- No hard-coded secrets (environment variables via Dapr Secrets API)
- SQL injection prevention via SQLModel parameterization
- CORS configured appropriately
- Rate limiting on public endpoints (via Redis state store)

### Testing Compliance

✅ **Testing Standards** (per constitution Section VII):
- Aim for 80%+ unit test coverage on core logic
- Integration tests for API endpoints
- Contract tests for service boundaries
- Tests generated alongside implementation

### Performance Compliance

✅ **Performance Budgets** (per constitution Section VII):
- API response time: <200ms p95 (target: <200ms p95) ✓
- Database queries: <50ms p95 (target: <50ms p95) ✓
- Memory footprint: <100MB per service instance (target: within Oracle free tier limits) ✓

### Reusable Intelligence Compliance

✅ **Reusable Intelligence** (per constitution Section IV):
- 5 specialized agents for common development tasks (to be created)
- 5 reusable skills for code generation and automation (to be created)
- 3 architectural blueprints documenting key patterns (to be created)
- All documented and versioned alongside code

### Bonus Features Compliance

✅ **Multi-Language Support** (per constitution Section V):
- Urdu language support maintained from Phase III
- Language detection for incoming messages
- Localization in responses

✅ **Voice Commands** (per constitution Section VI):
- Web Speech API integration maintained from Phase III
- Voice input for Urdu and English

✅ **Advanced Features** (per constitution Section VIII):
- Recurring tasks (daily, weekly, monthly, custom) ✓
- Due dates with time components ✓
- Reminder notifications ✓
- Real-time sync across devices ✓
- Full audit logging via Kafka events ✓

### Workflow Compliance

✅ **Mandatory Sequence** (per constitution Section IX):
1. Specification (`sp.specify`) - Completed ✓
2. Planning (`sp.plan`) - In progress ✓
3. Tasks (`sp.tasks`) - Next step
4. Implementation (`sp.implement`) - After tasks
5. Testing (`testing-engineer` agent) - After implementation
6. Debugging (`debugger` agent) - After testing
7. Validation - Final step

### Gate Status: ✅ PASS

All constitutional requirements satisfied. No violations requiring justification. Proceed to Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/011-event-driven-microservices/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── events.yaml      # Event schemas for Kafka topics
│   ├── api.yaml         # REST API OpenAPI specification
│   └── dapr/            # Dapr component configurations
│       ├── pubsub.yaml
│       ├── statestore.yaml
│       ├── bindings.yaml
│       └── secrets.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application with microservices architecture

backend/
├── src/
│   ├── models/              # SQLModel database models (extended from Phase II/III)
│   │   ├── task.py          # Existing task model (extended with search, recurring)
│   │   ├── user.py          # Existing user model (Better Auth)
│   │   ├── conversation.py  # Existing conversation model
│   │   ├── message.py       # Existing message model
│   │   ├── audit_log.py     # NEW: Audit trail entries
│   │   ├── reminder.py      # NEW: Scheduled reminders
│   │   ├── friend.py        # NEW: Friend connections
│   │   ├── group.py         # NEW: Collaboration groups
│   │   ├── membership.py    # NEW: Group memberships
│   │   ├── assignment.py    # NEW: Task assignments
│   │   ├── comment.py       # NEW: Task comments
│   │   └── message_dm.py    # NEW: Direct messages
│   ├── services/            # Business logic services
│   │   ├── task_service.py  # Existing task CRUD (extended)
│   │   ├── chat_service.py  # Existing chat service
│   │   ├── event_publisher.py  # NEW: Dapr Pub/Sub event publishing
│   │   ├── search_service.py   # NEW: PostgreSQL full-text search
│   │   ├── collaboration_service.py  # NEW: Friends, groups, permissions
│   │   └── notification_service.py   # NEW: Multi-channel notifications
│   ├── api/                 # FastAPI endpoints (existing, extended)
│   │   ├── tasks.py         # Existing task endpoints
│   │   ├── chat.py          # Existing chat endpoints
│   │   ├── search.py        # NEW: Search endpoints
│   │   ├── friends.py       # NEW: Friend management endpoints
│   │   ├── groups.py        # NEW: Group management endpoints
│   │   ├── comments.py      # NEW: Task comment endpoints
│   │   └── messages.py      # NEW: Direct messaging endpoints
│   ├── mcp/                 # MCP server (existing, unchanged)
│   │   └── server.py        # 5 tools: add_task, list_tasks, complete_task, delete_task, update_task
│   └── middleware/          # Existing JWT auth middleware
│       └── auth.py
├── microservices/           # NEW: Event-driven microservices
│   ├── websocket_sync/      # Real-time synchronization service
│   │   ├── main.py          # WebSocket server with Dapr Pub/Sub subscription
│   │   ├── connection_manager.py  # WebSocket connection management (Redis state)
│   │   └── event_handler.py       # Task event processing and broadcasting
│   ├── notification/        # Notification delivery service
│   │   ├── main.py          # Dapr Bindings consumer for scheduled reminders
│   │   ├── channels/        # Multi-channel notification delivery
│   │   │   ├── email.py
│   │   │   ├── in_app.py
│   │   │   └── push.py
│   │   └── scheduler.py     # Dapr Bindings integration for cron scheduling
│   ├── recurring_task/      # Recurring task generation service
│   │   ├── main.py          # Dapr Pub/Sub consumer for recurring patterns
│   │   ├── pattern_parser.py  # Cron expression parsing and validation
│   │   └── task_generator.py  # Next occurrence calculation and task creation
│   └── audit/               # Audit trail service
│       ├── main.py          # Dapr Pub/Sub consumer for all task events
│       ├── log_writer.py    # Audit log persistence to PostgreSQL
│       └── export.py        # Audit log export (JSON, CSV)
├── tests/
│   ├── unit/                # Unit tests for services and models
│   ├── integration/         # Integration tests for API endpoints
│   └── contract/            # Contract tests for event schemas and service boundaries
└── requirements.txt         # Python dependencies (extended with Dapr SDK, asyncio)

frontend/
├── src/
│   ├── components/          # React components (existing, extended)
│   │   ├── chat/            # Existing ChatKit components
│   │   ├── tasks/           # Existing task components (extended with search, recurring)
│   │   ├── friends/         # NEW: Friend list, online status
│   │   ├── groups/          # NEW: Group management, permissions
│   │   ├── comments/        # NEW: Task comment threads
│   │   └── messages/        # NEW: Direct messaging UI
│   ├── pages/               # Next.js App Router pages (existing, extended)
│   │   ├── app/             # Existing authenticated pages
│   │   ├── friends/         # NEW: Friends page
│   │   ├── groups/          # NEW: Groups page
│   │   └── search/          # NEW: Search results page
│   ├── services/            # Frontend services (existing, extended)
│   │   ├── api.ts           # Existing API client (extended with new endpoints)
│   │   ├── websocket.ts     # NEW: WebSocket client for real-time sync
│   │   └── auth.ts          # Existing Better Auth client
│   └── hooks/               # React hooks (existing, extended)
│       ├── useTasks.ts      # Existing task hook (extended with real-time updates)
│       ├── useWebSocket.ts  # NEW: WebSocket connection hook
│       ├── useFriends.ts    # NEW: Friends management hook
│       └── useGroups.ts     # NEW: Groups management hook
├── tests/
│   ├── unit/                # Jest/Vitest unit tests
│   └── integration/         # E2E tests with Playwright
└── package.json             # Node dependencies (extended with WebSocket client)

infrastructure/              # NEW: Kubernetes and Dapr configurations
├── helm/                    # Helm charts for Oracle OKE deployment
│   ├── backend/             # Backend API Helm chart
│   ├── frontend/            # Frontend Helm chart
│   ├── websocket-sync/      # WebSocket Sync Service Helm chart
│   ├── notification/        # Notification Service Helm chart
│   ├── recurring-task/      # Recurring Task Service Helm chart
│   ├── audit/               # Audit Service Helm chart
│   ├── dapr/                # Dapr runtime Helm chart
│   ├── prometheus/          # Prometheus monitoring Helm chart
│   └── grafana/             # Grafana dashboards Helm chart
├── dapr/                    # Dapr component configurations
│   ├── pubsub-redpanda.yaml      # Redpanda Cloud Pub/Sub component
│   ├── statestore-redis.yaml     # Redis state store component
│   ├── bindings-cron.yaml        # Cron bindings for reminders
│   └── secrets-kubernetes.yaml   # Kubernetes secrets component
├── monitoring/              # Monitoring configurations
│   ├── prometheus.yaml      # Prometheus scrape configs
│   ├── grafana-dashboards/  # Grafana dashboard JSON files
│   └── alerts.yaml          # Prometheus alert rules
└── ci-cd/                   # GitHub Actions workflows
    ├── build-test.yaml      # Build and test on PR
    ├── deploy-staging.yaml  # Deploy to staging on merge to main
    └── deploy-prod.yaml     # Deploy to production with manual approval

.github/
└── workflows/               # GitHub Actions CI/CD
    ├── build-test.yml       # Build, test, security scan on PR
    ├── deploy-staging.yml   # Auto-deploy to staging on main merge
    └── deploy-prod.yml      # Manual approval for production deployment
```

**Structure Decision**: Web application with microservices architecture. Existing backend/ and frontend/ directories extended with new models, services, and components. New microservices/ directory for event-driven services. New infrastructure/ directory for Kubernetes, Dapr, and monitoring configurations. Maintains separation of concerns while building on Phase II/III foundation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: N/A - No constitutional violations detected. All requirements align with established principles and technology stack.
