# Tasks: Sky-Aura Glass UI Transformation

**Input**: Design documents from `/specs/004-sky-aura-glass/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: No test tasks included (not requested in specification)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `frontend/src/`, `frontend/app/`, `frontend/components/`
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure build tools for Sky-Aura Glass aesthetic

- [X] T001 Install framer-motion package in frontend/package.json
- [X] T002 [P] Install shadcn/ui components (dropdown-menu, avatar, button, card) via npx shadcn@latest add
- [X] T003 [P] Add environment variables to frontend/.env.local (NEXT_PUBLIC_LINKEDIN_URL, NEXT_PUBLIC_GITHUB_URL, NEXT_PUBLIC_DEMO_VIDEO_URL)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core styling infrastructure and utilities that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Update frontend/tailwind.config.ts with Sky-Aura Glass color palette (purple, magenta, gold)
- [X] T005 [P] Add backdrop blur utilities to frontend/tailwind.config.ts (xs: 2px, glass: 12px, heavy: 20px)
- [X] T006 [P] Add box shadow utilities to frontend/tailwind.config.ts (glass-sm, glass-md, glass-lg, bloom)
- [X] T007 [P] Add animation keyframes to frontend/tailwind.config.ts (float, breathe, gradient)
- [X] T008 Add CSS variables to frontend/app/globals.css (glass properties, glow effects, color palette, animation durations)
- [X] T009 [P] Add utility classes to frontend/app/globals.css (glass-card, glass-button, text-glass, text-glass-secondary)
- [X] T010 [P] Create performance benchmarking utility in frontend/lib/utils/performance.ts with benchmarkDevice(), getComplexity(), getAnimationConfig()
- [X] T011 [P] Create icon mapping constants in frontend/lib/icons.ts with ICON_MAP and ICON_SIZES

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Authentication Session Management (Priority: P1) 🎯 MVP

**Goal**: Users can logout from any page via notch header dropdown and manage their session with timeout notifications

**Independent Test**: Login to the application, verify logout button appears in notch header, click logout and confirm redirect to login page. Test session timeout by waiting 2 hours or manually triggering timeout modal.

### Implementation for User Story 1

- [X] T012 [P] [US1] Create PageWrapper layout component in frontend/components/layout/PageWrapper.tsx with session timeout state management
- [X] T013 [P] [US1] Create NotchHeader component in frontend/components/layout/NotchHeader.tsx with iPhone-style notch geometry using clip-path
- [X] T014 [US1] Create UserDropdown component in frontend/components/layout/UserDropdown.tsx with logout functionality using Better Auth signOut()
- [X] T015 [US1] Add session timeout detection hook in frontend/components/layout/PageWrapper.tsx with 2-hour inactivity tracking
- [X] T016 [US1] Create SessionTimeoutModal component in frontend/components/layout/SessionTimeoutModal.tsx with extend/logout options
- [X] T017 [US1] Integrate NotchHeader into PageWrapper in frontend/components/layout/PageWrapper.tsx with conditional rendering based on auth state
- [X] T018 [US1] Update root layout in frontend/app/layout.tsx to wrap all pages with PageWrapper component

**Checkpoint**: At this point, User Story 1 should be fully functional - users can logout and manage session timeouts

---

## Phase 4: User Story 2 + User Story 3 - Visual Experience + Notch Header (Priority: P2)

**Goal**: Transform the application with glassmorphic styling, animated gradient background, and complete the notch header with external profile links

**Independent Test**: View any page and verify glassmorphic styling is applied, animated gradient background is visible, and notch header contains LinkedIn, GitHub, and Account icons that function correctly.

### Implementation for User Story 2 & 3

- [X] T019 [P] [US2] Create AnimatedBackground component in frontend/components/layout/AnimatedBackground.tsx with 4-state gradient animation (12s duration)
- [X] T020 [P] [US2] Create GlassCard primitive component in frontend/components/ui/GlassCard.tsx with floating and breathing animation props
- [X] T021 [P] [US2] Create GlassButton primitive component in frontend/components/ui/GlassButton.tsx with hover/active states and variants
- [X] T022 [P] [US2] Create FloatingElement wrapper component in frontend/components/animations/FloatingElement.tsx with configurable duration and yOffset
- [X] T023 [US2] Integrate AnimatedBackground into PageWrapper in frontend/components/layout/PageWrapper.tsx with z-index: -10
- [X] T024 [US3] Add LinkedIn and GitHub icon links to NotchHeader in frontend/components/layout/NotchHeader.tsx using environment variables
- [X] T025 [US3] Add ARIA labels and keyboard navigation support to NotchHeader icons in frontend/components/layout/NotchHeader.tsx
- [X] T026 [US2] Update TaskList component in frontend/app/(protected)/todo/components/TaskList.tsx with GlassCard styling and nature icons
- [X] T027 [US2] Update TaskForm component in frontend/app/(protected)/todo/components/TaskForm.tsx with glassmorphic modal styling
- [X] T028 [US2] Update TaskFilters component in frontend/app/(protected)/todo/components/TaskFilters.tsx with glassmorphic tab styling
- [X] T029 [US2] Update TagSidebar component in frontend/app/(protected)/todo/components/TagSidebar.tsx with GlassCard container
- [X] T030 [US2] Update CalendarView component in frontend/app/(protected)/todo/components/CalendarView.tsx with glassmorphic cell styling

**Checkpoint**: At this point, User Stories 1, 2, and 3 should all work - authentication, visual transformation, and notch header complete

---

## Phase 5: User Story 4 - Demo Showcase Section (Priority: P3)

**Goal**: Landing page displays hero section with cloud animations and demo video showcase in glassmorphic containers

**Independent Test**: Visit landing page and verify hero section displays with notched border and animated clouds, demo video autoplays muted and loops, and login/signup CTAs are hidden when authenticated.

### Implementation for User Story 4

- [X] T031 [P] [US4] Create CloudBackground component in frontend/components/hero/CloudBackground.tsx with floating cloud SVG animations
- [X] T032 [P] [US4] Create HeroSection component in frontend/components/hero/HeroSection.tsx with notched border using clip-path
- [X] T033 [P] [US4] Create DemoSection component in frontend/components/hero/DemoSection.tsx with video container and lazy loading
- [X] T034 [US4] Update landing page in frontend/app/page.tsx to integrate HeroSection and DemoSection components
- [X] T035 [US4] Add conditional CTA visibility logic in frontend/app/page.tsx to hide login/signup buttons when user is authenticated
- [X] T036 [US4] Add decorative floating nature icons to HeroSection in frontend/components/hero/HeroSection.tsx using FloatingElement wrapper

**Checkpoint**: At this point, User Stories 1-4 should all work - landing page is fully transformed with hero and demo sections

---

## Phase 6: User Story 5 - Todo Entry Animation (Priority: P3)

**Goal**: Users experience a welcoming 1.5-second animation when entering the todo page with "TASKS" text fade-in followed by content bounce-up, skippable via button or key press

**Independent Test**: Navigate to /todo page and verify "TASKS" text fades in over 0.5s, content bounces up over 1s, skip button appears and functions, animation plays on every visit.

### Implementation for User Story 5

- [X] T037 [P] [US5] Create TasksEntryAnimation component in frontend/components/animations/TasksEntryAnimation.tsx with two-phase animation (tasks-fade 0.5s, content-bounce 1s)
- [X] T038 [US5] Add skip button to TasksEntryAnimation in frontend/components/animations/TasksEntryAnimation.tsx with Escape key handler
- [X] T039 [US5] Add animation state management to TasksEntryAnimation in frontend/components/animations/TasksEntryAnimation.tsx with unique animationKey per visit
- [X] T040 [US5] Integrate TasksEntryAnimation into todo page in frontend/app/(protected)/todo/page.tsx with full-screen overlay (z-index: 50)
- [X] T041 [US5] Add animation completion handler in frontend/app/(protected)/todo/page.tsx to remove overlay and show content

**Checkpoint**: At this point, User Stories 1-5 should all work - todo page has entry animation

---

## Phase 7: User Story 6 + User Story 7 - Scroll Animations + Nature Icons (Priority: P3)

**Goal**: Elements reveal smoothly as users scroll, background has parallax effect, and nature-themed icons are used consistently throughout the application

**Independent Test**: Scroll through pages and verify elements fade in as they enter viewport, background moves at different speed (parallax), and nature icons (Leaf, Mountain, Sprout, Flower, Sun) are used consistently.

### Implementation for User Story 6 & 7

- [X] T042 [P] [US6] Create ScrollReveal wrapper component in frontend/components/animations/ScrollReveal.tsx using Framer Motion useInView hook
- [X] T043 [P] [US6] Add parallax scrolling effect to AnimatedBackground in frontend/components/layout/AnimatedBackground.tsx with 0.5x scroll speed
- [X] T044 [US6] Apply ScrollReveal to HeroSection in frontend/components/hero/HeroSection.tsx with fadeInUp variant
- [X] T045 [US6] Apply ScrollReveal to DemoSection in frontend/components/hero/DemoSection.tsx with fadeInUp variant and 0.2s delay
- [X] T046 [US6] Apply stagger animations to TaskList in frontend/app/(protected)/todo/components/TaskList.tsx using Framer Motion staggerChildren
- [X] T047 [US7] Update task status icons in frontend/app/(protected)/todo/components/TaskList.tsx to use nature metaphor (Leaf: incomplete, Mountain: complete, Sprout: new)
- [X] T048 [US7] Update action button icons in frontend/app/(protected)/todo/components/TaskForm.tsx to use nature icons (Sprout: add, X: delete, Edit: edit)
- [X] T049 [US7] Update tag icons in frontend/app/(protected)/todo/components/TagSidebar.tsx to use Flower icon
- [X] T050 [US7] Update calendar day markers in frontend/app/(protected)/todo/components/CalendarView.tsx to use Sun icon

**Checkpoint**: At this point, all user stories (1-7) should be complete - full Sky-Aura Glass transformation achieved

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Accessibility, performance optimization, and final polish affecting all user stories

- [X] T051 [P] Add prefers-reduced-motion support to all animation components in frontend/components/animations/ using Framer Motion useReducedMotion hook
- [X] T052 [P] Add ARIA labels to all icon-only buttons throughout frontend/components/ and frontend/app/
- [X] T053 [P] Add visible focus states to all interactive elements in frontend/app/globals.css with purple glow outline
- [X] T054 Verify WCAG 2.1 AA contrast ratios for text-glass (purple-900) and text-glass-secondary (purple-700) using WebAIM Contrast Checker
- [X] T055 [P] Add graceful degradation for backdrop-filter in frontend/app/globals.css using @supports not query
- [X] T056 [P] Optimize demo video loading in frontend/components/hero/DemoSection.tsx with loading="lazy" and preload="metadata"
- [X] T057 [P] Add will-change CSS property to actively animating elements in frontend/components/animations/
- [X] T058 Test performance on mobile devices and adjust animation complexity in frontend/lib/utils/performance.ts if needed
- [X] T059 Update frontend/app/(auth)/login/page.tsx with glassmorphic form styling using GlassCard and GlassButton
- [X] T060 Update frontend/app/(auth)/signup/page.tsx with glassmorphic form styling using GlassCard and GlassButton
- [X] T061 Run quickstart.md validation checklist to verify all acceptance criteria are met

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent but enhances US1 visually
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Extends US1 NotchHeader with external links
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Independent landing page transformation
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent todo page animation
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Independent scroll animations
- **User Story 7 (P3)**: Can start after Foundational (Phase 2) - Independent icon updates (integrates with US2)

### Within Each User Story

- Foundation tasks before component creation
- Primitive components (GlassCard, GlassButton) before usage in pages
- Layout components (PageWrapper, NotchHeader) before page integration
- Animation wrappers (FloatingElement, ScrollReveal) before application to content
- Core implementation before polish and accessibility

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- All Foundational tasks (T004-T011) can run in parallel within Phase 2
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within US2+US3: T019-T022 (component creation) can run in parallel
- Within US4: T031-T033 (hero components) can run in parallel
- Within US6+US7: T042-T043 (animation components) can run in parallel
- All Polish tasks marked [P] (T051-T057) can run in parallel

---

## Parallel Example: User Story 2 + 3

```bash
# Launch all primitive components together:
Task: "Create AnimatedBackground component in frontend/components/layout/AnimatedBackground.tsx"
Task: "Create GlassCard primitive component in frontend/components/ui/GlassCard.tsx"
Task: "Create GlassButton primitive component in frontend/components/ui/GlassButton.tsx"
Task: "Create FloatingElement wrapper component in frontend/components/animations/FloatingElement.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T012-T018)
4. **STOP and VALIDATE**: Test authentication and session management independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (P1) → Test independently → Deploy/Demo (MVP!)
3. Add User Stories 2+3 (P2) → Test independently → Deploy/Demo (Visual transformation)
4. Add User Story 4 (P3) → Test independently → Deploy/Demo (Landing page complete)
5. Add User Story 5 (P3) → Test independently → Deploy/Demo (Todo animation)
6. Add User Stories 6+7 (P3) → Test independently → Deploy/Demo (Full experience)
7. Add Polish (Phase 8) → Final validation → Production deployment

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T011)
2. Once Foundational is done:
   - Developer A: User Story 1 (T012-T018)
   - Developer B: User Stories 2+3 (T019-T030)
   - Developer C: User Story 4 (T031-T036)
3. Stories complete and integrate independently
4. Team completes remaining stories (US5, US6+7) and Polish together

---

## Task Summary

- **Total Tasks**: 61
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 8 tasks (BLOCKING)
- **User Story 1 (P1)**: 7 tasks - Authentication Session Management
- **User Story 2+3 (P2)**: 12 tasks - Visual Experience + Notch Header
- **User Story 4 (P3)**: 6 tasks - Demo Showcase Section
- **User Story 5 (P3)**: 5 tasks - Todo Entry Animation
- **User Story 6+7 (P3)**: 9 tasks - Scroll Animations + Nature Icons
- **Polish Phase**: 11 tasks - Accessibility and Performance

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phase 1 (Setup) + Phase 2 (Foundational) + Phase 3 (User Story 1) = 18 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow strict format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- No test tasks included (not requested in specification)
- Frontend-only transformation (no backend changes required)
