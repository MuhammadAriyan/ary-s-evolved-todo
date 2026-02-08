# Tasks: Production Website Optimization

**Input**: Design documents from `/specs/012-prod-web-optimization/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Tests are NOT explicitly requested in the specification. This task list focuses on implementation and verification through Lighthouse, axe DevTools, and bundle analysis.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` for all frontend code
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish baseline metrics and prepare optimization environment

- [X] T001 Measure current bundle size baseline using `ANALYZE=true npm run build` in frontend/
- [ ] T002 [P] Run Lighthouse audit on current production build and document scores in specs/012-prod-web-optimization/research.md
- [ ] T003 [P] Run axe DevTools accessibility audit and document violations in specs/012-prod-web-optimization/research.md
- [ ] T004 [P] Document current performance metrics (FCP, LCP, TTI, CLS, FID) in specs/012-prod-web-optimization/research.md
- [X] T005 Create backup of critical files: frontend/app/layout.tsx, frontend/app/(protected)/todo/page.tsx, frontend/next.config.js, frontend/tailwind.config.ts, frontend/app/globals.css

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure changes that enable all user story optimizations

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create devLog utility function in frontend/lib/utils.ts for development-only console logging
- [X] T007 [P] Add CSS variable system for text colors in frontend/app/globals.css (--text-primary, --text-secondary, --text-tertiary, --text-muted, --text-disabled, --text-hover, --text-active, --text-link, --text-link-hover)
- [X] T008 [P] Update Tailwind config in frontend/tailwind.config.ts to add text color system (text.primary, text.secondary, text.tertiary, text.muted, text.disabled, text.hover, text.active, text.link, text.link-hover)
- [X] T009 [P] Configure next/font for Chelsea Market in frontend/app/layout.tsx with Latin subset and font-display: swap
- [X] T010 [P] Configure next/font for Inter in frontend/app/layout.tsx with Latin subset and font-display: swap
- [X] T011 Remove external Google Fonts links from frontend/app/layout.tsx (lines 41-43)
- [X] T012 Update Tailwind font configuration in frontend/tailwind.config.ts to use CSS variables (--font-chelsea, --font-inter)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Fast Initial Page Load (Priority: P1) 🎯 MVP

**Goal**: Achieve <1 second page load time through critical performance fixes

**Independent Test**: Measure Time to First Contentful Paint (FCP) and Largest Contentful Paint (LCP) using browser DevTools Performance tab or Lighthouse. Target: TTI <1s, FCP <1.8s, LCP <2.5s

### Implementation for User Story 1

- [X] T013 [P] [US1] Remove duplicate QueryClient instantiation from frontend/app/(protected)/todo/page.tsx line 46
- [X] T014 [P] [US1] Remove QueryClientProvider wrapper from frontend/app/(protected)/todo/page.tsx lines 332-338
- [X] T015 [US1] Change export in frontend/app/(protected)/todo/page.tsx to: `export default function TodoPage() { return <TodoPageContent /> }`
- [X] T016 [P] [US1] Replace console.log with devLog in frontend/lib/websocket-client.ts (7 occurrences)
- [X] T017 [P] [US1] Replace console.log with devLog in frontend/hooks/useWebSocket.ts (5 occurrences)
- [X] T018 [P] [US1] Replace console.log with devLog in frontend/hooks/useTasks.ts (6 occurrences)
- [X] T019 [P] [US1] Replace console.log with devLog in frontend/hooks/useChat.ts (8 occurrences)
- [X] T020 [P] [US1] Replace console.log with devLog in frontend/app/(protected)/todo/page.tsx lines 76, 82, 91-95 (3 occurrences)
- [X] T021 [P] [US1] Replace console.log with devLog in frontend/app/(auth)/login/page.tsx (2 occurrences)
- [X] T022 [P] [US1] Replace console.log with devLog in frontend/lib/chat-client.ts (1 occurrence)
- [X] T023 [US1] Remove unused ConnectionStatusCompact variant from frontend/components/ui/connection-status.tsx lines 94-174
- [X] T024 [US1] Remove unused ConnectionStatusDetailed variant from frontend/components/ui/connection-status.tsx lines 94-174
- [ ] T025 [US1] Verify font optimization by checking Network tab - fonts should be self-hosted with no external requests
- [ ] T026 [US1] Run Lighthouse audit and verify performance score >90, FCP <1.8s, LCP <2.5s, TTI <1s

**Checkpoint**: At this point, User Story 1 should deliver <1 second page load time

---

## Phase 4: User Story 2 - Instant Task Operations (Priority: P1)

**Goal**: Ensure task operations (add, delete, complete) complete within 1 second

**Independent Test**: Perform add/delete/complete operations and measure response time using browser DevTools. Target: <1 second from user action to visual confirmation

### Implementation for User Story 2

- [X] T027 [US2] Implement event-driven session checking in frontend/app/(protected)/todo/page.tsx with visibilitychange listener
- [X] T028 [US2] Add user activity listener for session validation in frontend/app/(protected)/todo/page.tsx
- [X] T029 [US2] Replace 3-second polling interval with 60-second fallback in frontend/app/(protected)/todo/page.tsx lines 89-99
- [X] T030 [US2] Add cleanup for event listeners in useEffect return in frontend/app/(protected)/todo/page.tsx
- [ ] T031 [US2] Test task operations (add, delete, complete) and verify <1 second response time using browser DevTools Performance tab

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - fast page load AND instant task operations

---

## Phase 5: User Story 3 - Accessible Interface for All Users (Priority: P1)

**Goal**: Achieve WCAG 2.1 Level AA compliance by fixing 94 text contrast violations

**Independent Test**: Run axe DevTools and Lighthouse accessibility audit. Target: Zero WCAG AA violations, all text meets 4.5:1 (normal) or 3:1 (large) contrast ratios

### Implementation for User Story 3

- [X] T032 [P] [US3] Replace text-white/50 and text-white/60 with text-text-muted in frontend/app/(protected)/todo/page.tsx (5 occurrences)
- [X] T033 [P] [US3] Replace text-white/50 and text-white/60 with text-text-muted in frontend/components/tasks/TaskList.tsx (7 occurrences)
- [X] T034 [P] [US3] Replace text-white/50 and text-white/60 with text-text-muted in frontend/components/chat/MessageThread.tsx (6 occurrences)
- [X] T035 [P] [US3] Replace text-white/50 and text-white/60 with text-text-muted in frontend/components/layout/NotchHeader.tsx (4 occurrences)
- [X] T036 [P] [US3] Replace text-white/70 with text-text-tertiary across remaining 32 files (systematic replacement)
- [X] T037 [P] [US3] Replace text-white/80 with text-text-secondary across remaining files (systematic replacement)
- [ ] T038 [P] [US3] Replace text-white with text-text-primary where appropriate (preserve existing usage where correct)
- [ ] T039 [US3] Run axe DevTools accessibility audit and verify zero WCAG AA violations
- [ ] T040 [US3] Test keyboard navigation - verify all interactive elements are reachable with Tab key
- [ ] T041 [US3] Verify text contrast ratios using browser DevTools - all text should meet 4.5:1 (normal) or 3:1 (large)
- [ ] T042 [US3] Run Lighthouse accessibility audit and verify score of 100

**Checkpoint**: All user stories (1, 2, 3) should now be independently functional with WCAG AA compliance

---

## Phase 6: User Story 4 - Discoverable via Search Engines (Priority: P2)

**Goal**: Implement comprehensive SEO with metadata, sitemap, robots.txt, and structured data

**Independent Test**: Inspect page metadata, run Google's Rich Results Test, verify robots.txt and sitemap.xml exist and are valid

### Implementation for User Story 4

- [X] T043 [P] [US4] Add metadata export to frontend/app/layout.tsx with title template, description, keywords, authors
- [X] T044 [P] [US4] Add Open Graph metadata to frontend/app/layout.tsx (type, locale, url, title, description, siteName, images)
- [X] T045 [P] [US4] Add Twitter Card metadata to frontend/app/layout.tsx (card, title, description, images)
- [X] T046 [P] [US4] Add robots configuration to frontend/app/layout.tsx (index: true, follow: true, googleBot settings)
- [X] T047 [P] [US4] Create sitemap.ts in frontend/app/ with routes: /, /todo, /chat, /login, /signup
- [X] T048 [P] [US4] Create robots.ts in frontend/app/ with allow: /, disallow: /api/, /admin/, sitemap reference
- [ ] T049 [US4] Add JSON-LD structured data script to frontend/app/layout.tsx (WebApplication schema)
- [ ] T050 [US4] Verify sitemap.xml is accessible at /sitemap.xml and shows all routes
- [ ] T051 [US4] Verify robots.txt is accessible at /robots.txt and shows correct rules
- [ ] T052 [US4] Test Open Graph preview using https://www.opengraph.xyz/ - verify rich preview cards display correctly
- [ ] T053 [US4] Run Google Rich Results Test and verify structured data is valid

**Checkpoint**: Application should now be discoverable by search engines with proper metadata

---

## Phase 7: User Story 5 - Optimized Bundle Size (Priority: P2)

**Goal**: Reduce bundle size by 20%+ through code splitting and dynamic imports

**Independent Test**: Analyze bundle size using webpack-bundle-analyzer, compare before/after metrics. Target: 20%+ reduction from baseline

### Implementation for User Story 5

- [ ] T054 [P] [US5] Add dynamic import for RecurringPatternForm in parent component using Next.js dynamic() with ssr: false
- [X] T055 [P] [US5] Add dynamic import for SearchBar in parent component using Next.js dynamic() with ssr: false
- [X] T056 [P] [US5] Add dynamic import for TaskAnalyticsCard in parent component using Next.js dynamic() with ssr: false (chart.tsx)
- [ ] T057 [P] [US5] Add Skeleton loading component for RecurringPatternForm (h-96)
- [X] T058 [P] [US5] Add Skeleton loading component for SearchBar (h-10)
- [X] T059 [P] [US5] Add Skeleton loading component for TaskAnalyticsCard (h-64)
- [X] T060 [US5] Verify optimizePackageImports in frontend/next.config.js includes: framer-motion, @tanstack/react-query, recharts, lucide-react
- [ ] T061 [US5] Run bundle analyzer: `ANALYZE=true npm run build` in frontend/
- [ ] T062 [US5] Compare bundle sizes - verify 20%+ reduction from baseline documented in T001
- [ ] T063 [US5] Test lazy loading - verify components load on demand using browser DevTools Network tab

**Checkpoint**: Bundle size should be reduced by 20%+ with lazy loading working correctly

---

## Phase 8: User Story 6 - Clean Production Environment (Priority: P2)

**Goal**: Zero console.log statements in production, proper error handling

**Independent Test**: Open browser DevTools console in production build - verify zero console.log, console.debug, or console.info statements appear

### Implementation for User Story 6

- [X] T064 [US6] Build production bundle: `npm run build` in frontend/
- [ ] T065 [US6] Start production server: `npm start` in frontend/
- [ ] T066 [US6] Open browser DevTools console and verify zero console.log statements appear
- [ ] T067 [US6] Navigate through all pages (/todo, /chat, /login, /signup) and verify console remains clean
- [ ] T068 [US6] Perform task operations (add, delete, complete) and verify no console output
- [ ] T069 [US6] Test error scenarios and verify error boundaries display user-friendly messages (not console errors)

**Checkpoint**: Production environment should be clean with zero debug logging

---

## Phase 9: User Story 7 - Consistent Visual Design (Priority: P3)

**Goal**: Preserve Sky-Aura Glass aesthetic while meeting accessibility standards

**Independent Test**: Visual inspection and automated accessibility checks to ensure aesthetic meets WCAG AA standards

### Implementation for User Story 7

- [X] T070 [P] [US7] Create EmptyState component in frontend/components/ui/empty-state.tsx with props: icon, title, description, action, className
- [X] T071 [P] [US7] Create TaskMetadata component in frontend/components/tasks/TaskMetadata.tsx with props: task, showTags, showDueDate, showPriority, compact
- [X] T072 [P] [US7] Create DeveloperLinks component in frontend/components/layout/DeveloperLinks.tsx with dropdown menu for frontend, API docs, API health
- [X] T073 [P] [US7] Create WebVitals component in frontend/components/analytics/WebVitals.tsx using useReportWebVitals hook
- [ ] T074 [US7] Add ConnectionStatus to NotchHeader in frontend/components/layout/NotchHeader.tsx with showLabel={false}
- [ ] T075 [US7] Remove ConnectionStatus from frontend/app/(protected)/todo/page.tsx line 231
- [ ] T076 [US7] Add DeveloperLinks to NotchHeader in frontend/components/layout/NotchHeader.tsx
- [ ] T077 [US7] Add login/signup button to NotchHeader when user is not authenticated in frontend/components/layout/NotchHeader.tsx
- [X] T078 [US7] Add WebVitals component to frontend/app/layout.tsx body
- [ ] T079 [US7] Replace EmptyState usage in frontend/components/tasks/TaskList.tsx
- [ ] T080 [US7] Replace EmptyState usage in frontend/components/chat/ConversationList.tsx
- [ ] T081 [US7] Replace EmptyState usage in frontend/components/tasks/TagSidebar.tsx
- [ ] T082 [US7] Replace EmptyState usage in frontend/components/tasks/CalendarView.tsx
- [ ] T083 [US7] Verify Sky-Aura Glass aesthetic is preserved - glassmorphic effects, nature-inspired colors, soft glows
- [ ] T084 [US7] Verify visual effects do not cause performance degradation on low-end devices

**Checkpoint**: All user stories should now be complete with consistent visual design

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final optimizations and validation across all user stories

- [X] T085 [P] Create web-performance-optimization skill directory: .claude/skills/web-performance-optimization/
- [X] T086 [P] Create SKILL.md in .claude/skills/web-performance-optimization/ with optimization overview
- [X] T087 [P] Create 00-overview.md in .claude/skills/web-performance-optimization/ with performance optimization overview
- [X] T088 [P] Create 01-bundle-optimization.md in .claude/skills/web-performance-optimization/ with bundle size reduction techniques
- [X] T089 [P] Create 02-runtime-performance.md in .claude/skills/web-performance-optimization/ with runtime optimization patterns
- [X] T090 [P] Create 03-seo-setup.md in .claude/skills/web-performance-optimization/ with SEO configuration guide
- [X] T091 [P] Create 04-accessibility.md in .claude/skills/web-performance-optimization/ with WCAG compliance checklist
- [X] T092 [P] Create 05-monitoring.md in .claude/skills/web-performance-optimization/ with performance monitoring setup
- [ ] T093 Run final Lighthouse audit and verify all scores >90 (Performance, Accessibility, Best Practices, SEO)
- [ ] T094 Run final bundle analysis and document final bundle size reduction percentage
- [ ] T095 Test all user stories independently to verify each works without dependencies
- [ ] T096 Create quickstart.md in specs/012-prod-web-optimization/ with optimization verification guide
- [X] T097 Document final performance metrics in specs/012-prod-web-optimization/research.md (compare with baseline from T001-T004)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational (Phase 2) - Depends on T007-T008 (CSS variables)
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 6 (P2)**: Depends on User Story 1 completion (T013-T022 console.log removal)
- **User Story 7 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Models/utilities before services
- Services before components
- Components before integration
- Core implementation before verification
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T004)
- All Foundational tasks marked [P] can run in parallel (T007, T008, T009, T010)
- Once Foundational phase completes, User Stories 1, 2, 3, 4, 5, 7 can start in parallel
- Within User Story 1: T016-T022 (console.log replacements) can run in parallel
- Within User Story 3: T032-T038 (color replacements) can run in parallel
- Within User Story 4: T043-T048 (SEO files) can run in parallel
- Within User Story 5: T054-T059 (dynamic imports and skeletons) can run in parallel
- Within User Story 7: T070-T073 (new components) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all console.log replacements for User Story 1 together:
Task: "Replace console.log with devLog in frontend/lib/websocket-client.ts"
Task: "Replace console.log with devLog in frontend/hooks/useWebSocket.ts"
Task: "Replace console.log with devLog in frontend/hooks/useTasks.ts"
Task: "Replace console.log with devLog in frontend/hooks/useChat.ts"
Task: "Replace console.log with devLog in frontend/app/(protected)/todo/page.tsx"
Task: "Replace console.log with devLog in frontend/app/(auth)/login/page.tsx"
Task: "Replace console.log with devLog in frontend/lib/chat-client.ts"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only - All P1)

1. Complete Phase 1: Setup (establish baseline)
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Fast Initial Page Load)
4. Complete Phase 4: User Story 2 (Instant Task Operations)
5. Complete Phase 5: User Story 3 (Accessible Interface)
6. **STOP and VALIDATE**: Test all P1 stories independently
7. Run Lighthouse audit - verify Performance >90, Accessibility 100
8. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Lighthouse audit (Performance focus)
3. Add User Story 2 → Test independently → Verify task operations <1s
4. Add User Story 3 → Test independently → Lighthouse audit (Accessibility focus)
5. Add User Story 4 → Test independently → Verify SEO metadata
6. Add User Story 5 → Test independently → Bundle analysis (20%+ reduction)
7. Add User Story 6 → Test independently → Production console check
8. Add User Story 7 → Test independently → Visual inspection
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Fast Page Load)
   - Developer B: User Story 2 (Instant Operations)
   - Developer C: User Story 3 (Accessibility)
   - Developer D: User Story 4 (SEO)
   - Developer E: User Story 5 (Bundle Size)
3. Stories complete and integrate independently

---

## Success Metrics

### Before Optimization (Baseline from Phase 1)

- Page load: ~2-3 seconds (to be measured in T004)
- Bundle size: ~500KB (to be measured in T001)
- Lighthouse score: ~70 (to be measured in T002)
- Console logs: 32 in production
- WCAG compliance: Fails with 94 violations (to be measured in T003)

### After Optimization (Target)

- Page load: <1 second ✅ (User Story 1)
- Bundle size: ~300KB (20%+ reduction) ✅ (User Story 5)
- Lighthouse score: >90 ✅ (User Stories 1, 3, 4)
- Console logs: 0 in production ✅ (User Story 6)
- WCAG compliance: AA ✅ (User Story 3)

### Performance Targets

- First Contentful Paint: <1.8s (User Story 1)
- Largest Contentful Paint: <2.5s (User Story 1)
- Cumulative Layout Shift: <0.1 (User Story 1)
- First Input Delay: <100ms (User Story 2)
- Time to Interactive: <1s (User Story 1)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All optimizations maintain existing functionality
- Sky-Aura Glass aesthetic preserved throughout
- No breaking changes to API
- Accessibility prioritized over pure aesthetic
