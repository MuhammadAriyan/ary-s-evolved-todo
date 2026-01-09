---
id: 0004
title: architecture-decision-records
stage: plan
date: 2026-01-07
surface: agent
model: claude-opus-4-5-thinking
feature: 001-fullstack-web-app
branch: 002-fullstack-web-app
user: ary
command: /sp.adr
labels: ["architecture", "adr", "decisions", "documentation", "planning"]
links:
  spec: specs/001-fullstack-web-app/spec.md
  ticket: null
  adr: history/adr/0001-full-stack-monorepo-architecture.md, history/adr/0002-authentication-strategy-with-jwks-based-jwt.md, history/adr/0003-frontend-technology-stack.md, history/adr/0004-backend-technology-stack.md
  pr: null
files:
  - history/adr/0001-full-stack-monorepo-architecture.md
  - history/adr/0002-authentication-strategy-with-jwks-based-jwt.md
  - history/adr/0003-frontend-technology-stack.md
  - history/adr/0004-backend-technology-stack.md
tests:
  - N/A (documentation task)
---

## Prompt

/sp.adr

## Response snapshot

Analyzed planning artifacts from `specs/001-fullstack-web-app/plan.md` and identified 4 architecturally significant decision clusters following the clustering principle (grouping related technologies that work together):

1. **ADR-0001: Full-Stack Monorepo Architecture**
   - Decision: Monorepo with `frontend/` and `backend/` directories, Docker Compose for local development
   - Alternatives: Polyrepo, Backend-driven monolith (Django), Microservices
   - Rationale: Unified development, atomic changes, simplified onboarding while maintaining clear boundaries

2. **ADR-0002: Authentication Strategy with JWKS-Based JWT**
   - Decision: JWKS-based JWT with Better Auth using EdDSA/Ed25519 asymmetric cryptography
   - Key Change: Original plan proposed shared secret JWT (HS256), but implementation revealed Better Auth uses asymmetric JWKS for enhanced security
   - Alternatives: Shared secret JWT, Session-based auth, OAuth-only, Custom JWT
   - Rationale: Enhanced security (backend only needs public key), key rotation, stateless, standard compliance

3. **ADR-0003: Frontend Technology Stack**
   - Decision: Next.js 15+ ecosystem with App Router, Tailwind CSS, shadcn/ui, TanStack Query, Better Auth
   - Alternatives: Remix + styled-components, Vite + React, SvelteKit, Create React App
   - Rationale: Integrated tooling, type safety, server components, excellent DX, Vercel deployment

4. **ADR-0004: Backend Technology Stack**
   - Decision: FastAPI + SQLModel ecosystem with Neon PostgreSQL
   - Alternatives: Django + DRF, Node.js + Express + Prisma, Go + Gin + GORM, Ruby on Rails
   - Rationale: Type safety, automatic docs, async performance, Python readability, serverless database

Each ADR includes comprehensive documentation: context, decision details, positive/negative consequences, alternatives considered with rejection rationale, and references to specs/plans/implementation files.

## Outcome

- ✅ Impact: Created 4 ADRs documenting all architecturally significant decisions for the full-stack todo application, establishing permanent record of technical choices and rationale
- 🧪 Tests: N/A - documentation task
- 📁 Files: 4 ADR files created in `history/adr/` directory
- 🔁 Next prompts: Begin implementation (`/sp.implement`), review ADRs with team, update ADRs as implementation reveals new insights
- 🧠 Reflection: Successfully applied decision clustering principle to group related technologies. Documented important architectural change (shared secret → JWKS) discovered during implementation. All ADRs pass significance checklist (impact, alternatives, scope).

## Evaluation notes (flywheel)

- Failure modes observed: Initial feature directory mismatch (script looked for 002-fullstack-web-app instead of 001-fullstack-web-app), required manual context loading
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
