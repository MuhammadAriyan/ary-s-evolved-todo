# ADR-0004: Backend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** 001-fullstack-web-app
- **Context:** Need robust, performant backend API for todo application with JWT authentication, database persistence, and recurring task scheduling. Must support 100+ concurrent users with <200ms p95 response time. Requirements include user isolation, input validation, and comprehensive testing.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines entire backend architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Multiple framework options evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all API development
-->

## Decision

Adopt **FastAPI + SQLModel ecosystem** as integrated backend solution:

- **Framework**: FastAPI 0.109+ (async Python web framework)
- **ORM**: SQLModel 0.0.14+ (combines SQLAlchemy + Pydantic)
- **Database**: Neon PostgreSQL (serverless, auto-scaling)
- **Migrations**: Alembic 1.13+ for database schema management
- **Authentication**: PyJWT 2.8+ with PyJWKClient for JWKS verification
- **Scheduler**: APScheduler 3.10+ for recurring tasks
- **Server**: Uvicorn 0.27+ (ASGI server)
- **Validation**: Pydantic Settings for environment variables
- **Testing**: pytest with coverage for endpoints and business logic
- **Deployment**: Docker container on Hugging Face Spaces/Railway

This stack provides type safety, automatic API documentation, and excellent async performance while maintaining Python's readability and ecosystem.

## Consequences

### Positive

- **Type Safety**: SQLModel + Pydantic provide end-to-end type safety from database to API
- **Automatic Docs**: FastAPI generates OpenAPI/Swagger documentation automatically
- **Async Performance**: Native async/await support enables high concurrency
- **Developer Experience**: Python's readability and FastAPI's intuitive API speed development
- **Database Flexibility**: SQLModel abstracts SQLAlchemy, making database changes easier
- **Migration Management**: Alembic provides robust schema versioning
- **Testing**: pytest ecosystem is mature with excellent async support
- **Validation**: Pydantic validates request/response data automatically
- **Serverless Database**: Neon PostgreSQL auto-scales and requires no maintenance

### Negative

- **SQLModel Maturity**: SQLModel is relatively new (0.0.x versions), less battle-tested than pure SQLAlchemy
- **APScheduler Limitations**: Single-instance scheduler not ideal for distributed systems (planned Celery migration)
- **Python Performance**: Slower than compiled languages (Go, Rust) though async mitigates this
- **Deployment Complexity**: Docker container deployment more complex than serverless functions
- **Database Coupling**: Neon PostgreSQL-specific features (connection pooling) may not transfer to other databases
- **Foreign Key Constraints**: Better Auth's independent schema management required removing FK constraints

## Alternatives Considered

### Alternative A: Django + Django REST Framework
- **Stack**: Django 4.x, DRF for API, Django ORM, Celery for tasks
- **Pros**: Mature ecosystem, built-in admin panel, excellent ORM, robust migrations
- **Cons**: Synchronous by default (async support limited), heavier framework, slower API performance
- **Why Rejected**: FastAPI's async performance and automatic docs better fit API-first architecture

### Alternative B: Node.js + Express + Prisma
- **Stack**: Express.js, Prisma ORM, TypeScript, Bull for job queue
- **Pros**: JavaScript/TypeScript throughout stack, Prisma excellent DX, large ecosystem
- **Cons**: Callback hell without careful async handling, less mature than Python for data processing
- **Why Rejected**: Team more familiar with Python, FastAPI performance comparable to Node.js

### Alternative C: Go + Gin + GORM
- **Stack**: Go language, Gin web framework, GORM for database
- **Pros**: Compiled performance, excellent concurrency, small binary size
- **Cons**: Verbose error handling, smaller ecosystem, team less familiar with Go
- **Why Rejected**: Python's ecosystem and readability outweigh Go's performance benefits at current scale

### Alternative D: Ruby on Rails
- **Stack**: Rails 7.x with Active Record, Sidekiq for background jobs
- **Pros**: Convention over configuration, mature ecosystem, excellent for CRUD apps
- **Cons**: Slower than async Python, less suitable for API-only backend, team unfamiliar with Ruby
- **Why Rejected**: FastAPI better suited for API-first architecture, Python more familiar to team

## References

- Feature Spec: [specs/001-fullstack-web-app/spec.md](../../specs/001-fullstack-web-app/spec.md)
- Implementation Plan: [specs/001-fullstack-web-app/plan.md](../../specs/001-fullstack-web-app/plan.md)
- API Contracts: [specs/001-fullstack-web-app/contracts/api-endpoints.md](../../specs/001-fullstack-web-app/contracts/api-endpoints.md)
- Database Schema: [specs/001-fullstack-web-app/contracts/database-schema.md](../../specs/001-fullstack-web-app/contracts/database-schema.md)
- Related ADRs: ADR-0001 (Monorepo Architecture), ADR-0002 (Authentication Strategy), ADR-0003 (Frontend Stack)
- Implementation Files:
  - `backend/app/main.py` (FastAPI app entry point)
  - `backend/app/models/task.py` (SQLModel task model)
  - `backend/app/api/v1/endpoints/tasks.py` (Task CRUD endpoints)
  - `backend/app/utils/jwt.py` (PyJWKClient for JWKS verification)
  - `backend/app/services/scheduler.py` (APScheduler for recurring tasks)
