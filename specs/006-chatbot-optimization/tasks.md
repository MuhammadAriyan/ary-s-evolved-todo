# Tasks: AI Chatbot Production Optimization & Deployment

**Input**: Design documents from `/specs/006-chatbot-optimization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

**Tests**: Not explicitly requested in specification - focusing on manual testing with browser DevTools

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/` at repository root
- Frontend: Next.js 15+ with App Router
- Backend: FastAPI with OpenAI Agents SDK

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Minimal setup - project already exists, only need bundle analyzer

- [x] T001 [P] Install @next/bundle-analyzer in frontend/package.json
- [x] T002 [P] Add bundle analyzer script to frontend/package.json ("analyze": "ANALYZE=true npm run build")

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No foundational work required - all tasks are optimizations to existing code

**⚠️ SKIP**: Project infrastructure already exists, proceeding directly to user stories

---

## Phase 3: User Story 1 - Fast Page Load (Priority: P1) 🎯 MVP

**Goal**: Eliminate performance bottlenecks - reduce bundle size from 38MB to <5MB, enable compression, optimize fonts, achieve FCP <1s

**Independent Test**:
1. Run `npm run build` and check bundle size (<5MB)
2. Run `npm run analyze` to visualize bundle composition
3. Open DevTools → Network tab, navigate to /chat
4. Verify FCP <1s, TTI <2s
5. Check response headers for `Content-Encoding: gzip` or `br`
6. Verify fonts loaded from `/_next/static/media/` (not external)

### Implementation for User Story 1

- [x] T003 [P] [US1] Remove or lazy load Three.js shader from frontend/app/(protected)/chat/page.tsx (search for Three.js imports and remove or implement dynamic import)
- [x] T004 [P] [US1] Add next/font optimization to frontend/app/layout.tsx (import Inter and Poppins from 'next/font/google' with subsets and display: 'swap')
- [x] T005 [P] [US1] Update Tailwind config frontend/tailwind.config.js to use font variables (--font-inter, --font-poppins)
- [x] T006 [P] [US1] Enable compression in frontend/next.config.js (set compress: true, add swcMinify: true, poweredByHeader: false)
- [x] T007 [P] [US1] Add image optimization config to frontend/next.config.js (formats: ['image/avif', 'image/webp'])
- [x] T008 [P] [US1] Add modularizeImports for lucide-react in frontend/next.config.js (optimize tree-shaking)
- [x] T009 [P] [US1] Add experimental.optimizePackageImports in frontend/next.config.js (for framer-motion, @tanstack/react-query, recharts)
- [x] T010 [US1] Configure bundle analyzer in frontend/next.config.js (wrap config with withBundleAnalyzer, enabled when ANALYZE=true)

**Checkpoint**: Bundle size <5MB, FCP <1s, compression enabled, fonts optimized

---

## Phase 4: User Story 2 - Smooth Streaming Experience (Priority: P1) 🎯 MVP

**Goal**: Fix scroll performance during streaming - reduce scroll events from 100+ to ≤10 per response, eliminate jank

**Independent Test**:
1. Send a message and observe streaming response
2. Open DevTools → Performance tab → Record
3. Count scroll events during streaming (should be ≤10)
4. Verify smooth scrolling with no visible jank
5. Test manual scroll up: auto-scroll should disable
6. Test scroll to bottom: auto-scroll should re-enable

### Implementation for User Story 2

- [x] T011 [US2] Implement debounced scroll handler in frontend/app/(protected)/chat/components/MessageThread.tsx (150ms debounce, detect user scroll up)
- [x] T012 [US2] Implement requestAnimationFrame-based smooth scroll in frontend/app/(protected)/chat/components/MessageThread.tsx (replace direct scrollIntoView calls)
- [x] T013 [US2] Add scroll event listener with passive: true in frontend/app/(protected)/chat/components/MessageThread.tsx (performance optimization)
- [x] T014 [US2] Add cleanup for scroll timeout and RAF in frontend/app/(protected)/chat/components/MessageThread.tsx (prevent memory leaks)

**Checkpoint**: Scroll events ≤10 per response, smooth scrolling, no jank, manual scroll control works

---

## Phase 5: User Story 5 - Successful Deployment (Priority: P1) 🎯 MVP

**Goal**: Configure deployment to Vercel (frontend) and HuggingFace Spaces (backend) with proper CORS and health checks

**Independent Test**:
1. Deploy frontend to Vercel staging
2. Deploy backend to HuggingFace Spaces staging
3. Test cross-origin requests from Vercel to HuggingFace
4. Verify `/health` endpoint returns 200 in <10ms
5. Verify `/health/ready` endpoint checks database and OpenAI API
6. Test environment variables are properly configured

### Implementation for User Story 5

- [x] T015 [P] [US5] Create vercel.json in frontend/ (configure headers, rewrites, environment variables)
- [x] T016 [P] [US5] Create Dockerfile in backend/ (port 7860, FastAPI with uvicorn)
- [x] T017 [P] [US5] Create .dockerignore in backend/ (exclude __pycache__, .env, tests)
- [x] T018 [P] [US5] Implement /health endpoint in backend/app/main.py (basic liveness check, return {"status": "healthy"} in <10ms)
- [x] T019 [US5] Implement /health/ready endpoint in backend/app/main.py (check database connection and OpenAI API, return detailed status)
- [x] T020 [US5] Update CORS configuration in backend/app/main.py (allow Vercel domain, credentials: true)
- [x] T021 [US5] Update quickstart.md with deployment instructions (Vercel CLI commands, HuggingFace Spaces setup)

**Checkpoint**: Frontend deploys to Vercel, backend deploys to HuggingFace Spaces, CORS works, health checks pass

---

## Phase 6: User Story 3 - Polished UI Appearance (Priority: P2)

**Goal**: Professional UI polish - custom scrollbar, correct avatar colors (purple/magenta), agent icons, improved dropdown

**Independent Test**:
1. Open chat page in Chrome, Firefox, Safari
2. Verify custom scrollbar visible with purple/magenta gradient
3. Check avatar colors: user (purple/magenta), Miyu (purple/violet), Riven (magenta/pink)
4. Verify agent icons display next to messages
5. Check user dropdown has glass styling with backdrop blur
6. Verify loading indicators appear during message sending

### Implementation for User Story 3

- [x] T022 [P] [US3] Add custom scrollbar CSS to frontend/app/globals.css (webkit and Firefox scrollbar styles with purple/magenta gradient)
- [x] T023 [P] [US3] Update avatar colors in frontend/app/(protected)/chat/components/AgentMessage.tsx (user: purple/magenta, Miyu: purple/violet, Riven: magenta/pink)
- [x] T024 [P] [US3] Add agent icons to messages in frontend/app/(protected)/chat/components/AgentMessage.tsx (display agentIcon from message data)
- [x] T025 [P] [US3] Find and update sign-in button component (search frontend/app/(auth)/ for sign-in, add Chrome icon from lucide-react)
- [x] T026 [P] [US3] Find and update navbar component (search frontend/components/ for navbar, add ClipboardList icon from lucide-react)
- [x] T027 [P] [US3] Find and update user dropdown component (search frontend/components/ for dropdown, add glass styling with bg-black/80 backdrop-blur-xl)
- [x] T028 [US3] Add loading spinner to ChatInput in frontend/app/(protected)/chat/components/ChatInput.tsx (show spinner in send button when isLoading)

**Checkpoint**: Custom scrollbar visible, avatar colors correct, agent icons display, dropdown styled, loading indicators work

---

## Phase 7: User Story 4 - Reliable Production Performance (Priority: P2)

**Goal**: Production-ready features - session caching (5min TTL), retry logic (1s exponential backoff), Web Vitals tracking, hybrid error UI

**Independent Test**:
1. Open DevTools → Network tab, navigate to chat
2. Verify initial API calls, navigate away and back within 5 minutes
3. Verify no new API calls (served from cache)
4. Simulate network failure, verify retry attempts with 1s, 2s, 4s delays
5. Check Vercel Analytics dashboard for Web Vitals data
6. Test error scenarios: network error (toast), streaming error (inline), auth error (modal)

### Implementation for User Story 4

- [x] T029 [P] [US4] Install @tanstack/react-query in frontend/package.json (for session caching)
- [x] T030 [P] [US4] Install @vercel/analytics in frontend/package.json (for Web Vitals tracking)
- [x] T031 [P] [US4] Setup QueryClientProvider in frontend/app/layout.tsx (wrap app with React Query provider)
- [x] T032 [US4] Implement session caching in frontend/hooks/useChat.ts (use useQuery with staleTime: 5*60*1000, gcTime: 10*60*1000)
- [x] T033 [US4] Implement fetchWithRetry in frontend/lib/chat-client.ts (exponential backoff: 1s, 2s, 4s, max 3 retries, skip 4xx errors)
- [x] T034 [US4] Update chatClient.sendMessage to use fetchWithRetry in frontend/lib/chat-client.ts
- [x] T035 [US4] Add Vercel Analytics to frontend/app/layout.tsx (import Analytics from '@vercel/analytics/react', add <Analytics /> component)
- [x] T036 [P] [US4] Create toast notification component in frontend/components/ui/toast.tsx (for minor errors like network retry)
- [x] T037 [P] [US4] Create error modal component in frontend/components/ui/error-modal.tsx (for critical errors like authentication failure)
- [x] T038 [US4] Implement hybrid error handling in frontend/hooks/useChat.ts (toast for network errors, inline for streaming errors, modal for auth errors)
- [x] T039 [US4] Add reconnection logic for SSE in frontend/hooks/useChat.ts (auto-reconnect on connection loss with exponential backoff)

**Checkpoint**: Session caching works (5min TTL), retry logic recovers from failures, Web Vitals tracked, hybrid error UI displays correctly

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation updates

- [x] T040 [P] Run bundle analyzer and verify bundle size <5MB (npm run analyze in frontend/)
- [x] T041 [P] Test all user stories independently with acceptance criteria from spec.md
- [x] T042 [P] Update quickstart.md with final deployment steps and validation checklist
- [x] T043 [P] Verify all clarified requirements are implemented (Vercel Analytics, 5min cache, 1s retry, hybrid errors, tiered health checks)
- [x] T044 Run full production deployment test (Vercel + HuggingFace Spaces)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: SKIPPED - no foundational work needed
- **User Story 1 (Phase 3)**: Can start immediately - Fast Page Load (P1)
- **User Story 2 (Phase 4)**: Can start immediately - Smooth Streaming (P1)
- **User Story 5 (Phase 5)**: Depends on US1 and US2 for MVP deployment
- **User Story 3 (Phase 6)**: Can start after US1/US2 - Polished UI (P2)
- **User Story 4 (Phase 7)**: Can start after US1/US2 - Production Performance (P2)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - Fast Page Load
- **User Story 2 (P1)**: Independent - Smooth Streaming
- **User Story 5 (P1)**: Depends on US1 and US2 for MVP deployment
- **User Story 3 (P2)**: Independent - Polished UI
- **User Story 4 (P2)**: Independent - Production Performance

### Within Each User Story

- All tasks marked [P] can run in parallel (different files)
- Tasks without [P] have dependencies on previous tasks in the same story
- Complete all tasks in a story before testing that story independently

### Parallel Opportunities

**Phase 1 (Setup)**: Both tasks can run in parallel
- T001 and T002 (different package.json operations)

**Phase 3 (US1)**: Tasks T003-T009 can all run in parallel (different files/sections)
- T003: chat/page.tsx
- T004: layout.tsx
- T005: tailwind.config.js
- T006-T009: next.config.js (can be done together)
- T010: next.config.js (depends on T001 from Phase 1)

**Phase 4 (US2)**: All tasks modify MessageThread.tsx sequentially

**Phase 5 (US5)**: Tasks T015-T017 can run in parallel, T018-T019 can run in parallel
- T015: vercel.json (frontend)
- T016: Dockerfile (backend)
- T017: .dockerignore (backend)
- T018 and T019: main.py (can be done together)
- T020: main.py CORS (after T018-T019)
- T021: quickstart.md (after all deployment config)

**Phase 6 (US3)**: Tasks T022-T027 can all run in parallel (different files)
- T022: globals.css
- T023-T024: AgentMessage.tsx (can be done together)
- T025: sign-in component
- T026: navbar component
- T027: dropdown component
- T028: ChatInput.tsx

**Phase 7 (US4)**: Tasks T029-T031 can run in parallel, T036-T037 can run in parallel
- T029-T031: package installs and provider setup
- T032-T035: sequential implementation
- T036-T037: UI components (parallel)
- T038-T039: error handling and reconnection

**Phase 8 (Polish)**: Tasks T040-T043 can all run in parallel

---

## Parallel Example: User Story 1 (Fast Page Load)

```bash
# Launch all parallelizable tasks for User Story 1 together:
Task: "Remove or lazy load Three.js shader from frontend/app/(protected)/chat/page.tsx"
Task: "Add next/font optimization to frontend/app/layout.tsx"
Task: "Update Tailwind config frontend/tailwind.config.js"
Task: "Enable compression in frontend/next.config.js"
Task: "Add image optimization config to frontend/next.config.js"
Task: "Add modularizeImports for lucide-react in frontend/next.config.js"
Task: "Add experimental.optimizePackageImports in frontend/next.config.js"

# Then complete:
Task: "Configure bundle analyzer in frontend/next.config.js"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 5 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 3: User Story 1 - Fast Page Load (T003-T010)
3. **VALIDATE**: Test bundle size <5MB, FCP <1s, compression enabled
4. Complete Phase 4: User Story 2 - Smooth Streaming (T011-T014)
5. **VALIDATE**: Test scroll performance ≤10 events, no jank
6. Complete Phase 5: User Story 5 - Deployment (T015-T021)
7. **VALIDATE**: Deploy to staging, test cross-origin requests, health checks
8. **STOP and DEMO**: MVP ready with core performance fixes and deployment

### Incremental Delivery

1. **MVP (P1 stories)**: Setup + US1 + US2 + US5 → Deploy and validate
2. **Polish (P2 stories)**: Add US3 (Polished UI) → Deploy and validate
3. **Production (P2 stories)**: Add US4 (Production Performance) → Deploy and validate
4. **Final**: Complete Phase 8 (Polish) → Production ready

### Parallel Team Strategy

With multiple developers:

1. **Team completes Setup together** (Phase 1)
2. **Parallel implementation**:
   - Developer A: User Story 1 (Fast Page Load)
   - Developer B: User Story 2 (Smooth Streaming)
   - Developer C: User Story 5 (Deployment config)
3. **Integrate and test MVP** (US1 + US2 + US5)
4. **Continue in parallel**:
   - Developer A: User Story 3 (Polished UI)
   - Developer B: User Story 4 (Production Performance)
5. **Final polish together** (Phase 8)

---

## Task Summary

**Total Tasks**: 44 tasks across 8 phases

**Tasks per User Story**:
- Setup: 2 tasks
- US1 (Fast Page Load): 8 tasks
- US2 (Smooth Streaming): 4 tasks
- US5 (Deployment): 7 tasks
- US3 (Polished UI): 7 tasks
- US4 (Production Performance): 11 tasks
- Polish: 5 tasks

**Parallel Opportunities**: 28 tasks marked [P] can run in parallel

**MVP Scope** (Recommended first delivery):
- Phase 1: Setup (2 tasks)
- Phase 3: User Story 1 (8 tasks)
- Phase 4: User Story 2 (4 tasks)
- Phase 5: User Story 5 (7 tasks)
- **Total MVP**: 21 tasks

**Estimated Time**:
- MVP (US1 + US2 + US5): 2-3 hours
- Full implementation (all stories): 4-6 hours

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- No tests explicitly requested - using manual testing with browser DevTools
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All clarified requirements incorporated (Vercel Analytics, 5min cache, 1s retry, hybrid errors, tiered health checks)
