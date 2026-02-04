---
id: 0002
title: Phase V Event-Driven Cloud Deployment Plan
stage: plan
date: 2026-01-31
surface: agent
model: claude-opus-4-5-thinking
feature: 011-event-driven-microservices
branch: 011-event-driven-microservices
user: ary
command: /sp.plan
labels: ["event-driven", "microservices", "kafka", "dapr", "cloud-deployment", "kubernetes", "ci-cd", "monitoring", "websocket", "real-time"]
links:
  spec: specs/011-event-driven-microservices/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/011-event-driven-microservices/plan.md
tests:
  - N/A - planning phase, no tests executed
---

## Prompt

User provided extensive high-level approach and detailed implementation plan for Phase V Event-Driven Cloud Deployment, including:

**Architecture Transformation**:
- From: Monolithic REST API with polling-based APScheduler (midnight cron)
- To: Event-driven microservices with Kafka + Dapr, 4 new services (Recurring Task, Notification, Audit, WebSocket Sync)

**Implementation Strategy** (6 phases):
- Phase 5A: Event Infrastructure (Kafka, Dapr, event schemas, event publishing)
- Phase 5B: Consumer Microservices (4 new services)
- Phase 5C: Advanced Features (DB migration, Dapr Jobs API, full-text search, WebSocket)
- Phase 5D: Cloud Deployment (Oracle OKE/DigitalOcean, Redpanda Cloud, Helm, TLS, monitoring)
- Phase 5E: CI/CD Pipeline (GitHub Actions, multi-stage, security scanning)
- Phase 5F: Reusable Intelligence (5 agents, 5 skills, 3 blueprints)

**Key Decisions**:
- Kafka: Strimzi (local) + Redpanda Cloud (production)
- Dapr: HTTP API (no SDK dependency)
- WebSocket: FastAPI + Redis Pub/Sub for multi-pod scaling
- Cloud: Oracle OKE free tier (2 VMs, 24GB RAM)
- Notifications: Email only (SendGrid) for Phase V
- Search: PostgreSQL tsvector with GIN index

**Critical Files**:
- Backend: event_publisher.py, reminder_scheduler.py, events.py, 002_phase5_schema.py
- Microservices: 4 new services (recurring-task, notification, audit, websocket-sync)
- Frontend: websocket-client.ts, useTasks.ts (modified), TaskForm.tsx (modified)
- Infrastructure: kafka/, dapr-components/, monitoring/, .github/workflows/cicd.yml
- Reusable Intelligence: .claude/agents/ (5), .claude/skills/ (5), blueprints/ (3)

## Response snapshot

Created comprehensive implementation plan (plan.md, 727 lines) with:

**Technical Context**:
- Languages: Python 3.12+, TypeScript 5.x, Bash
- Dependencies: Kafka, Dapr 1.12+, FastAPI, SQLModel, httpx, croniter, redis-asyncio, Next.js 15+
- Storage: Neon PostgreSQL (extended), Kafka topics, Redis, tsvector search
- Testing: pytest, jest, E2E (Playwright/Cypress), load testing (k6/Locust)
- Platforms: Minikube (local), Oracle OKE/DigitalOcean (production), GitHub Actions (CI/CD)

**Constitution Check**: ✅ PASS
- All Phase V stack requirements satisfied (Kafka, Dapr, Oracle OKE/DigitalOcean)
- Event-driven architecture principles followed
- Stateless services with horizontal scaling
- Multi-user isolation preserved
- Reusable intelligence requirements met (5 agents, 5 skills, 3 blueprints)
- Security, testing, and performance standards satisfied
- No violations requiring justification

**Project Structure**:
- Existing backend/frontend extended (not replaced)
- 4 new microservices with consistent structure (main.py, Dockerfile, k8s/, requirements.txt)
- Infrastructure organized by concern (kafka/, dapr-components/, monitoring/)
- Reusable intelligence in .claude/ and blueprints/

**Phase 0: Research & Technology Validation**:
- 8 key decisions documented with rationale and alternatives
- Technology validation for Kafka+Dapr, Dapr Jobs API, PostgreSQL full-text search, FastAPI WebSocket+Redis, Oracle OKE, GitHub Actions

**Phase 1: Design & Contracts**:
- Data model extensions: audit_events table (new), tasks table (3 new columns, priority migration)
- Event schemas: TaskEvent, ReminderEvent, TaskUpdateEvent (3 Kafka topics)
- API contract extensions: search endpoint, audit log endpoint, reminder scheduling
- Dapr component contracts: pub/sub, state store, jobs API
- Microservice contracts: 4 services with clear responsibilities

**Phase 2: Implementation Phases**:
- 6 weeks of phased implementation (5A-5F)
- Agent-driven workflow specified for each phase
- Clear deliverables and verification criteria
- Risk mitigation strategies documented

## Outcome

- ✅ Impact: Created production-ready implementation plan for Phase V Event-Driven Cloud Deployment. Plan transforms monolithic REST API into event-driven microservices architecture with Kafka+Dapr, enabling real-time sync, precise reminders, advanced features, cloud deployment, CI/CD, and monitoring. All constitutional requirements satisfied with no violations.
- 🧪 Tests: N/A - planning phase. Testing strategy defined: pytest (backend), jest (frontend), E2E (Playwright/Cypress), load testing (k6/Locust). Target: 80%+ backend coverage, 70%+ frontend coverage.
- 📁 Files: Created plan.md (727 lines) with complete technical context, constitution check, project structure, data models, event schemas, API contracts, Dapr components, microservice contracts, and 6-phase implementation roadmap.
- 🔁 Next prompts: `/sp.tasks` to generate implementation tasks from this plan, then `/sp.implement` to execute tasks with agent-driven workflow
- 🧠 Reflection: Successfully created comprehensive plan that balances architectural transformation (monolithic → microservices) with practical implementation (6 phased weeks). Key insight: Embedded Phase 0 research directly in plan to avoid separate research.md file, making all technology decisions explicit with rationale. Constitution check passed cleanly - all Phase V requirements (Kafka, Dapr, cloud, reusable intelligence) satisfied without deviations. Plan ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Plan completed successfully with all constitutional requirements satisfied.
- Graders run and results (PASS/FAIL):
  - Constitution Check: PASS (all Phase V stack requirements, architecture principles, reusable intelligence, code quality, workflow compliance)
  - Technical Context: PASS (all fields specified, no NEEDS CLARIFICATION markers)
  - Project Structure: PASS (clear organization, existing structure preserved, new services follow consistent pattern)
  - Data Model: PASS (audit_events table, tasks extensions, indexes, triggers)
  - Contracts: PASS (event schemas, API extensions, Dapr components, microservice contracts)
  - Implementation Phases: PASS (6 phases with deliverables, agents, verification criteria)
  - Risk Mitigation: PASS (7 risks identified with mitigation strategies)
- Prompt variant (if applicable): N/A - standard /sp.plan workflow with extensive user input
- Next experiment (smallest change to try): N/A - plan complete and validated, ready for task generation
