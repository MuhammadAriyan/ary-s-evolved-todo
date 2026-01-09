# ADR-0003: Frontend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-07
- **Feature:** 001-fullstack-web-app
- **Context:** Need modern, interactive web UI for todo application with calendar view, tag filtering, and real-time updates. Requirements include authentication integration, mobile responsiveness, and smooth animations. Must integrate with FastAPI backend via REST API.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security? ✅ YES - Defines entire frontend architecture
     2) Alternatives: Multiple viable options considered with tradeoffs? ✅ YES - Multiple framework options evaluated
     3) Scope: Cross-cutting concern (not an isolated detail)? ✅ YES - Affects all UI development
-->

## Decision

Adopt **Next.js 15+ ecosystem** as integrated frontend solution:

- **Framework**: Next.js 15.1.0+ with App Router (React 19+, TypeScript 5.3+)
- **Styling**: Tailwind CSS 3.4+ for utility-first styling
- **UI Components**: shadcn/ui (Radix UI primitives with Tailwind)
- **State Management**: TanStack Query 5.0+ for server state, React hooks for UI state
- **Forms**: React Hook Form 7.50+ with Zod 3.22+ validation
- **Calendar**: react-big-calendar 1.8+ for calendar view
- **Authentication**: Better Auth 1.0+ with JWT plugin
- **Deployment**: Vercel (serverless, edge functions, automatic HTTPS)

This stack provides integrated tooling, excellent developer experience, and production-ready components while maintaining flexibility for custom requirements.

## Consequences

### Positive

- **Integrated Ecosystem**: Next.js + Vercel provides seamless deployment with zero configuration
- **Type Safety**: TypeScript throughout ensures compile-time error detection
- **Server Components**: Next.js App Router enables server-side rendering for better performance
- **Component Library**: shadcn/ui provides accessible, customizable components without bloat
- **Optimistic Updates**: TanStack Query handles optimistic UI updates with automatic rollback
- **Form Validation**: React Hook Form + Zod provides type-safe form validation
- **Mobile First**: Tailwind CSS makes responsive design straightforward
- **Fast Iteration**: Hot module replacement and fast refresh speed up development
- **SEO Ready**: Server-side rendering improves SEO (though less critical for authenticated app)

### Negative

- **Framework Lock-in**: Tightly coupled to Next.js conventions and Vercel deployment
- **Learning Curve**: App Router is newer paradigm, requires learning server vs client components
- **Bundle Size**: React 19 + Next.js + dependencies result in larger initial bundle
- **Vercel Dependency**: Optimal experience requires Vercel deployment (though can deploy elsewhere)
- **Complexity**: Multiple state management approaches (TanStack Query for server, hooks for UI) require clear patterns
- **Calendar Styling**: react-big-calendar requires custom CSS for Tailwind integration

## Alternatives Considered

### Alternative A: Remix + styled-components + Cloudflare
- **Stack**: Remix framework, styled-components for styling, Cloudflare Pages deployment
- **Pros**: Excellent data loading patterns, CSS-in-JS flexibility, edge deployment
- **Cons**: Smaller ecosystem than Next.js, less mature tooling, styled-components adds runtime overhead
- **Why Rejected**: Next.js has larger community, better TypeScript support, and Vercel integration is superior

### Alternative B: Vite + React + vanilla CSS + AWS Amplify
- **Stack**: Vite build tool, plain React, vanilla CSS, AWS Amplify hosting
- **Pros**: Minimal framework overhead, full control over architecture, fast builds
- **Cons**: No SSR out of box, manual routing setup, more boilerplate, AWS Amplify complexity
- **Why Rejected**: Too much manual setup for features Next.js provides (routing, SSR, API routes)

### Alternative C: SvelteKit + Tailwind + Vercel
- **Stack**: SvelteKit framework, Tailwind CSS, Vercel deployment
- **Pros**: Smaller bundle sizes, simpler reactivity model, excellent performance
- **Cons**: Smaller ecosystem, fewer component libraries, team less familiar with Svelte
- **Why Rejected**: React ecosystem is more mature, Better Auth has better React support

### Alternative D: Create React App (CRA)
- **Stack**: CRA with React Router, Tailwind, manual deployment
- **Pros**: Simple setup, well-understood patterns, no framework magic
- **Cons**: CRA is deprecated, no SSR, manual routing, no built-in API routes
- **Why Rejected**: CRA is no longer maintained, Next.js is the recommended React framework

## References

- Feature Spec: [specs/001-fullstack-web-app/spec.md](../../specs/001-fullstack-web-app/spec.md)
- Implementation Plan: [specs/001-fullstack-web-app/plan.md](../../specs/001-fullstack-web-app/plan.md)
- Related ADRs: ADR-0001 (Monorepo Architecture), ADR-0002 (Authentication Strategy), ADR-0004 (Backend Stack)
- Implementation Files:
  - `frontend/app/layout.tsx` (Root layout with QueryClient)
  - `frontend/app/(protected)/todo/page.tsx` (Main todo page)
  - `frontend/hooks/useTasks.ts` (TanStack Query hooks)
  - `frontend/lib/api-client.ts` (API client with JWT)
  - `frontend/tailwind.config.ts` (Tailwind configuration)
