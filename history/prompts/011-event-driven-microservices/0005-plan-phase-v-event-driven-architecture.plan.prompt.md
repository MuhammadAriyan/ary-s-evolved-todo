---
id: 0005
title: Plan Phase V Event-Driven Architecture
stage: plan
date: 2026-01-31
surface: agent
model: claude-opus-4-5-thinking
feature: 011-event-driven-microservices
branch: 011-event-driven-microservices
user: ary
command: /sp.plan
labels: ["planning", "architecture", "event-driven", "kafka", "dapr", "microservices", "oracle-oke"]
links:
  spec: specs/011-event-driven-microservices/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/011-event-driven-microservices/plan.md
  - specs/011-event-driven-microservices/research.md
  - specs/011-event-driven-microservices/data-model.md
  - specs/011-event-driven-microservices/quickstart.md
  - specs/011-event-driven-microservices/contracts/events.yaml
  - specs/011-event-driven-microservices/contracts/api.yaml
  - specs/011-event-driven-microservices/contracts/dapr/pubsub.yaml
  - specs/011-event-driven-microservices/contracts/dapr/statestore.yaml
  - specs/011-event-driven-microservices/contracts/dapr/bindings.yaml
  - specs/011-event-driven-microservices/contracts/dapr/secrets.yaml
  - CLAUDE.md
tests:
  - N/A (planning phase, no tests)
---

## Prompt

User ran `/sp.plan` to execute the implementation planning workflow for Phase V Event-Driven Cloud Deployment.

**User Request**: "continue and add the kafka for the following Kafka Use Cases (Phase V) – Summary: Reminders/Notifications, Recurring Tasks, Activity/Audit Log, Real-time Sync, and all possible use cases to optimize app"

**Context**: After completing `/sp.clarify` which resolved 5 critical architectural decisions (Oracle OKE, Redpanda Cloud, JWT auth, PostgreSQL FTS, Redis state store, lightweight monitoring), the planning phase began to design the implementation architecture.

**Workflow Executed**:
1. Setup: Ran `setup-plan.sh` to initialize planning environment
2. Load Context: Read spec.md and constitution.md
3. Fill Technical Context: Documented all technology choices from clarification
4. Constitution Check: Verified compliance with all constitutional requirements (ALL PASSED ✅)
5. Project Structure: Defined microservices architecture layout
6. Phase 0 Research: Created comprehensive research.md with:
   - PostgreSQL Full-Text Search implementation guide
   - 8 comprehensive Kafka use cases with event schemas, error handling, and optimization strategies
7. Phase 1 Design: Created data-model.md, contracts/, and quickstart.md
8. Agent Context Update: Updated CLAUDE.md with Phase V technologies

## Response snapshot

**Planning Workflow Completed Successfully**

### Phase 0: Research (research.md)

Created comprehensive research document with two major sections:

**Part 1: PostgreSQL Full-Text Search** (894 lines)
- tsvector column design with automatic update triggers
- GIN index configuration for optimal performance
- ts_rank relevance scoring and ranking strategies
- Fuzzy search with pg_trgm extension for typo tolerance
- Multi-column search across titles, descriptions, tags, notes
- Query optimization for <1 second response with 10k+ tasks
- Index maintenance and performance monitoring

**Part 2: Kafka Event-Driven Architecture** (546 lines)
- 7 Kafka topics with retention policies and partition strategies
- 8 comprehensive use cases:
  1. Reminders/Notifications (Dapr Bindings cron scheduling)
  2. Recurring Tasks (cron expression parsing, next occurrence calculation)
  3. Activity/Audit Log (complete audit trail with before/after state)
  4. Real-time Sync (WebSocket broadcasting via Redis state store)
  5. Collaboration Events (comments, assignments, @mentions)
  6. Friend Activity Notifications (online status, direct messages)
  7. Search Index Updates (PostgreSQL tsvector refresh)
  8. Dead Letter Queue (error recovery with exponential backoff)
- Event schemas with JSON examples
- Dapr Pub/Sub configuration for Redpanda Cloud
- Event-driven optimization strategies (deduplication, ordering, replay, versioning)
- Performance benchmarks and monitoring metrics

### Phase 1: Design

**data-model.md** (8 new tables, 1 extended table)
- audit_logs: Complete audit trail with JSONB before/after state
- scheduled_reminders: Exact-time reminders with cron expressions
- friend_connections: Friend relationships with online status
- collaboration_groups: Group-based task management
- group_memberships: Role-based permissions (owner, admin, member)
- task_assignments: Task assignment to specific users
- task_comments: Comments with @mention support
- direct_messages: Friend-to-friend messaging
- tasks (extended): Added search_vector, recurring_pattern, parent_task_id, group_id

**contracts/events.yaml** (Event schemas for 7 Kafka topics)
- Defined schemas for all event types (task.created, task.updated, task.completed, etc.)
- Partition key strategies for event ordering
- Retention policies per topic
- Dapr Pub/Sub metadata configuration

**contracts/api.yaml** (OpenAPI 3.0 specification)
- 30+ new REST API endpoints for:
  - Search (full-text search with filters)
  - Friends (friend requests, accept/reject, list)
  - Groups (create, update, delete, member management)
  - Comments (create, update, delete with @mentions)
  - Messages (direct messaging between friends)
  - Reminders (schedule, cancel, list)
  - Audit (view logs, export)

**contracts/dapr/** (4 Dapr component configurations)
- pubsub.yaml: Redpanda Cloud Pub/Sub with SASL authentication, resiliency policies
- statestore.yaml: Redis state store with connection pooling, TTL configuration
- bindings.yaml: Cron bindings for reminder scheduling with Dapr Jobs API examples
- secrets.yaml: Kubernetes secrets management with rotation strategy

**quickstart.md** (Complete local development guide)
- Prerequisites installation (Docker, Dapr CLI, kubectl)
- Infrastructure setup with Docker Compose (PostgreSQL, Redis, Redpanda)
- Dapr initialization and component configuration
- Backend setup (dependencies, migrations, environment variables)
- Frontend setup (Next.js configuration)
- Multi-service startup instructions (5 microservices + frontend)
- Verification steps and troubleshooting guide
- Development workflow (testing, database operations, logging)

### Constitution Check Results

✅ **ALL REQUIREMENTS PASSED**

- Technology Stack: Compliant (Redpanda Cloud, Dapr, Oracle OKE, Better Auth JWT)
- Architecture: Compliant (event-driven, stateless services, multi-user isolation, clean architecture)
- MCP Tools: Compliant (exactly 5 tools, no additions)
- Database Schema: Compliant (8 new tables, 1 extended table)
- Security: Compliant (JWT verification, input validation, secrets via Dapr)
- Testing: Compliant (80%+ coverage target, contract tests)
- Performance: Compliant (<200ms p95 API, <50ms p95 DB queries)
- Reusable Intelligence: Compliant (5 agents, 5 skills, 3 blueprints to be created)
- Workflow: Compliant (spec → plan → tasks → implement → test → debug → validate)

### Project Structure

**Microservices Architecture**:
- backend/ (existing, extended with new models, services, API endpoints)
- backend/microservices/ (NEW: 4 event-driven services)
  - websocket_sync/ (real-time synchronization)
  - notification/ (reminder delivery)
  - recurring_task/ (recurring task generation)
  - audit/ (audit log persistence)
- frontend/ (existing, extended with new components, pages, hooks)
- infrastructure/ (NEW: Helm charts, Dapr configs, monitoring, CI/CD)

### Agent Context Updated

Updated CLAUDE.md with Phase V technologies:
- Python 3.12+ (backend microservices), TypeScript 5.x (frontend Next.js 15+)

## Outcome

- ✅ Impact: Completed comprehensive implementation plan for Phase V event-driven architecture. Designed 8 new database tables, 7 Kafka topics, 30+ REST API endpoints, 4 Dapr components, and 4 microservices. Resolved all architectural ambiguities and provided complete local development setup guide. Ready for task decomposition and implementation.

- 🧪 Tests: N/A (planning phase, no code changes)

- 📁 Files: Created 11 files:
  - plan.md (comprehensive architecture plan with constitution check)
  - research.md (1440 lines: PostgreSQL FTS + Kafka use cases)
  - data-model.md (8 new tables + 1 extended table with SQLModel schemas)
  - quickstart.md (complete local development guide)
  - contracts/events.yaml (event schemas for 7 Kafka topics)
  - contracts/api.yaml (OpenAPI 3.0 spec with 30+ endpoints)
  - contracts/dapr/pubsub.yaml (Redpanda Cloud Pub/Sub config)
  - contracts/dapr/statestore.yaml (Redis state store config)
  - contracts/dapr/bindings.yaml (Cron scheduling config)
  - contracts/dapr/secrets.yaml (Kubernetes secrets config)
  - Updated CLAUDE.md (agent context)

- 🔁 Next prompts: `/sp.tasks` to decompose implementation plan into testable, dependency-ordered tasks

- 🧠 Reflection: Planning phase successfully completed with comprehensive Kafka use cases as requested. The event-driven architecture is well-designed with clear separation of concerns across 4 microservices. All 8 use cases (reminders, recurring tasks, audit log, real-time sync, collaboration, friend activity, search indexing, error recovery) are fully documented with event schemas, error handling strategies, and performance optimizations. The Dapr abstraction layer provides flexibility for future cloud provider changes while maintaining Oracle OKE as the primary deployment target. Local development environment is fully specified with Docker Compose for all infrastructure services.

## Evaluation notes (flywheel)

- Failure modes observed: Initial tool invocation errors when calling Write without parameters (repeated empty Write calls). Resolved by properly structuring Write tool calls with file_path and content parameters. Context7 MCP used successfully to retrieve Dapr documentation for accurate component configurations.

- Graders run and results (PASS/FAIL): PASS - All constitutional requirements satisfied. No violations detected. Project structure aligns with web application microservices pattern. All technology choices from clarification phase properly integrated into plan.

- Prompt variant (if applicable): Standard /sp.plan workflow with user request to add comprehensive Kafka use cases. Successfully incorporated 8 detailed use cases with event schemas, error handling, and optimization strategies.

- Next experiment (smallest change to try): Consider adding cost estimation section to plan based on Oracle Cloud free tier limits, Redpanda Cloud pricing, and Redis instance sizing. May help with resource allocation decisions during implementation.
