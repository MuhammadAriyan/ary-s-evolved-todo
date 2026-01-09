# ADR-0002: Authentication Strategy with JWKS-Based JWT

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** 001-fullstack-web-app
- **Context:** Need secure, stateless authentication for multi-user todo application. Frontend (Next.js) and backend (FastAPI) are separate services requiring shared authentication mechanism. Must support email/password and Google OAuth. Initial plan proposed shared secret JWT, but implementation revealed Better Auth uses asymmetric cryptography (JWKS) for enhanced security.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Core security architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Session-based, shared secret JWT, JWKS
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all protected endpoints
-->

## Decision

Adopt **JWKS-based JWT authentication** with Better Auth and asymmetric cryptography:

- **Frontend Authentication**: Better Auth 1.0+ with JWT plugin (EdDSA/Ed25519 signing)
- **Token Generation**: Better Auth signs JWTs with private key, publishes public keys via JWKS endpoint
- **Backend Verification**: FastAPI uses PyJWKClient to fetch public keys from `/api/auth/jwks` endpoint
- **Token Storage**: httpOnly cookies (secure, not accessible to JavaScript)
- **Token Expiry**: 24 hours with automatic refresh
- **User Isolation**: JWT payload contains `user_id` (sub claim) for database query filtering
- **OAuth Support**: Google OAuth integrated via Better Auth social providers

**Key Architectural Change**: Moved from shared secret (HS256) to asymmetric JWKS (EdDSA) during implementation when we discovered Better Auth's default JWT plugin uses asymmetric cryptography for enhanced security.

## Consequences

### Positive

- **Enhanced Security**: Asymmetric cryptography means backend only needs public key (private key never leaves frontend)
- **Key Rotation**: JWKS endpoint allows key rotation without backend redeployment
- **Stateless**: No server-side session storage required, enabling horizontal scaling
- **Multi-Provider**: Better Auth handles both email/password and Google OAuth with unified JWT output
- **Standard Compliance**: JWKS is industry standard (used by Auth0, Okta, AWS Cognito)
- **Automatic Refresh**: Better Auth handles token refresh transparently
- **httpOnly Cookies**: Protects against XSS attacks (tokens not accessible to JavaScript)

### Negative

- **Network Dependency**: Backend must fetch JWKS from frontend on first request (cached afterward)
- **Debugging Complexity**: Asymmetric crypto harder to debug than shared secrets (can't manually decode with secret)
- **Initial Setup Complexity**: Required research and implementation adjustment from original plan
- **Better Auth Coupling**: Tightly coupled to Better Auth's JWT implementation
- **Foreign Key Constraint Issue**: Better Auth manages its own user schema independently, requiring removal of FK constraint from tasks table

## Alternatives Considered

### Alternative A: Shared Secret JWT (HS256) - Original Plan
- **Approach**: Both frontend and backend share same secret key for signing/verifying JWTs
- **Pros**: Simpler implementation, easier debugging, symmetric crypto is faster
- **Cons**: Secret must be shared between services (security risk), no key rotation without downtime, if secret leaks both services compromised
- **Why Rejected**: Better Auth's default JWT plugin uses asymmetric crypto (EdDSA), would require custom implementation to use shared secret

### Alternative B: Session-Based Authentication
- **Approach**: Store session data in database or Redis, use session cookies
- **Pros**: Simpler to understand, easy to invalidate sessions, no token expiry issues
- **Cons**: Requires session storage (database/Redis), not stateless, harder to scale horizontally, session synchronization across instances
- **Why Rejected**: Violates constitution requirement for stateless services, adds operational complexity

### Alternative C: OAuth-Only (No Email/Password)
- **Approach**: Only support Google OAuth, no email/password registration
- **Pros**: Simpler implementation, no password management, leverages Google's security
- **Cons**: Users without Google accounts excluded, dependency on Google availability, less control over auth flow
- **Why Rejected**: Spec requires email/password support for users without Google accounts

### Alternative D: Custom JWT Implementation
- **Approach**: Build custom JWT signing/verification without Better Auth
- **Pros**: Full control over implementation, can use any algorithm
- **Cons**: Reinventing the wheel, security risks from custom crypto, no OAuth integration, more code to maintain
- **Why Rejected**: Better Auth provides battle-tested implementation with OAuth support

## References

- Feature Spec: [specs/001-fullstack-web-app/spec.md](../../specs/001-fullstack-web-app/spec.md)
- Implementation Plan: [specs/001-fullstack-web-app/plan.md](../../specs/001-fullstack-web-app/plan.md)
- Auth Flow Contract: [specs/001-fullstack-web-app/contracts/auth-flow.md](../../specs/001-fullstack-web-app/contracts/auth-flow.md)
- Related ADRs: ADR-0001 (Monorepo Architecture), ADR-0003 (Frontend Stack), ADR-0004 (Backend Stack)
- Implementation Files:
  - Frontend: `frontend/lib/auth.ts` (Better Auth config with JWT plugin)
  - Backend: `backend/app/utils/jwt.py` (PyJWKClient for JWKS verification)
  - Backend: `backend/app/middleware/auth.py` (JWT verification middleware)
