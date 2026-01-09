# ADR-0001: Full-Stack Monorepo Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** 001-fullstack-web-app
- **Context:** Transform existing Python console todo app into production-ready full-stack web application. Need to decide on project structure, technology separation, and deployment architecture. Requirements include user authentication, multi-user support, and modern web UI with calendar view.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES
-->

## Decision

Adopt a **monorepo structure** with clear separation between frontend and backend:

- **Project Structure**: Monorepo with `frontend/` and `backend/` directories at root level
- **Frontend**: Next.js 15+ (TypeScript, App Router) deployed to Vercel
- **Backend**: FastAPI (Python 3.12+) deployed to Hugging Face Spaces/Railway
- **Database**: Neon PostgreSQL (serverless, shared between frontend auth and backend API)
- **Development**: Docker Compose for local orchestration
- **Communication**: RESTful API with JWT authentication

The monorepo keeps related code together while maintaining clear boundaries between concerns. Frontend handles UI/UX and authentication (Better Auth), backend handles business logic and data persistence, database provides shared storage layer.

## Consequences

### Positive

- **Unified Development**: Single repository simplifies dependency management, versioning, and CI/CD
- **Code Sharing**: TypeScript types can be shared between frontend and backend (future enhancement)
- **Atomic Changes**: Frontend and backend changes can be committed together, ensuring API contract consistency
- **Simplified Onboarding**: New developers clone one repo and have complete application context
- **Docker Compose**: Local development mirrors production architecture with all services running
- **Clear Boundaries**: Separate directories enforce separation of concerns while keeping code discoverable

### Negative

- **Build Complexity**: Need to manage separate build processes for frontend (Next.js) and backend (Python)
- **Deployment Coordination**: Changes affecting both frontend and backend require coordinated deployments
- **Repository Size**: Monorepo grows larger over time with both frontend and backend dependencies
- **CI/CD Complexity**: Need separate pipelines for frontend and backend, with conditional execution based on changed files
- **Tooling Conflicts**: Different language ecosystems (Node.js vs Python) may have conflicting tooling requirements

## Alternatives Considered

### Alternative A: Separate Repositories (Polyrepo)
- **Structure**: `todo-frontend` and `todo-backend` as separate repositories
- **Pros**: Independent versioning, simpler CI/CD per repo, smaller repo sizes
- **Cons**: API contract synchronization issues, harder to track related changes, more complex local setup
- **Why Rejected**: For a small team and tightly coupled frontend/backend, the overhead of managing two repos outweighs benefits

### Alternative B: Backend-Driven Monolith (Django + Templates)
- **Structure**: Single Django application serving both API and HTML templates
- **Pros**: Simpler deployment (one service), no API versioning concerns, traditional MVC pattern
- **Cons**: Limited frontend interactivity, harder to build modern UI (calendar, animations), less separation of concerns
- **Why Rejected**: Requirements demand rich client-side interactions (calendar view, optimistic updates) that are better served by dedicated frontend framework

### Alternative C: Microservices Architecture
- **Structure**: Separate services for auth, tasks, notifications, etc.
- **Pros**: Independent scaling, technology flexibility per service, fault isolation
- **Cons**: Massive complexity overhead for small application, distributed system challenges, operational burden
- **Why Rejected**: Premature optimization - current scale (100 concurrent users) doesn't justify microservices complexity

## References

- Feature Spec: [specs/001-fullstack-web-app/spec.md](../../specs/001-fullstack-web-app/spec.md)
- Implementation Plan: [specs/001-fullstack-web-app/plan.md](../../specs/001-fullstack-web-app/plan.md)
- Related ADRs: ADR-0002 (Authentication Strategy), ADR-0003 (Frontend Stack), ADR-0004 (Backend Stack)
- Project Structure: See plan.md Section "Project Structure" for detailed directory layout
