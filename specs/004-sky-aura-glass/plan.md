# Implementation Plan: Sky-Aura Glass UI Transformation

**Branch**: `004-sky-aura-glass` | **Date**: 2026-01-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-sky-aura-glass/spec.md`

## Summary

Transform the existing Next.js todo application into an anime-inspired, nature-themed glassmorphic experience embodying peace, resilience, and quiet strength through the Sky-Aura Glass aesthetic. This is a frontend-focused visual transformation that adds:

1. **Authentication UX Enhancements**: Logout functionality via iPhone-style notch header, session timeout handling with modal notifications, conditional CTA visibility
2. **Glassmorphic Visual System**: Translucent glass-like surfaces with backdrop blur, soft bloom shadows, purple/magenta/gold color palette
3. **Nature-Themed Animations**: Entry animations, floating elements, scroll reveals, parallax effects using Framer Motion
4. **Immersive Components**: Notch header, animated gradient background, cloud animations, hero section with notched borders
5. **Accessibility & Performance**: Reduced motion support, WCAG 2.1 AA compliance, CPU/GPU benchmarking for adaptive performance

**Technical Approach**: Extend existing Next.js 16 App Router application with Framer Motion for animations, shadcn/ui components restyled with glassmorphic design system, Lucide icons for nature metaphors, and Tailwind CSS utilities for Sky-Aura Glass aesthetic.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16+ (App Router)
**Primary Dependencies**:
- Framer Motion (animations)
- shadcn/ui (dropdown-menu, avatar, button, card)
- Lucide React (nature-themed icons)
- Tailwind CSS (styling with custom glassmorphic utilities)
- Better Auth client (existing authentication)

**Storage**: Neon PostgreSQL (existing, no changes required)
**Testing**: Jest + React Testing Library (existing setup)
**Target Platform**: Web browsers (Chrome 76+, Safari 9+, Firefox 103+ for backdrop-filter support)
**Project Type**: Web application (frontend transformation only)
**Performance Goals**:
- 60fps animations on standard devices
- <1.5s todo entry animation
- <200ms interaction response time
- Page load time increase <20% vs current

**Constraints**:
- Must maintain existing authentication functionality (httpOnly cookies, JWT)
- Must not break existing todo CRUD operations
- Must respect prefers-reduced-motion user preferences
- Must maintain WCAG 2.1 AA contrast ratios despite glassmorphic styling
- Must degrade gracefully on browsers without backdrop-filter support
- Purple/magenta/gold palette only (no dark mode)

**Scale/Scope**:
- ~12 new React components (layout, animations, UI primitives)
- ~9 existing components to update (todo pages, auth pages)
- ~200-300 lines of CSS variables and Tailwind config
- 8 implementation phases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Technology Stack Compliance

✅ **PASS** - Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS
- Aligns with Phase II constitution requirements
- No deviations from approved stack

✅ **PASS** - Authentication: Better Auth with JWT tokens
- Existing implementation maintained
- Only adding UI for logout functionality
- No changes to authentication mechanism

✅ **PASS** - Database: Neon PostgreSQL
- No database changes required for this feature
- Existing schema and queries unchanged

### Architecture Compliance

✅ **PASS** - Stateless Services
- All new components are stateless React components
- Session state managed by existing Better Auth system
- No new stateful services introduced

✅ **PASS** - Multi-User Isolation
- No changes to data access patterns
- Existing user_id filtering maintained
- UI transformation only

✅ **PASS** - Clean Architecture
- UI components remain in presentation layer
- No business logic changes
- Separation of concerns maintained

### Code Quality Compliance

✅ **PASS** - Security Requirements
- No new security vulnerabilities introduced
- JWT verification middleware unchanged
- No hard-coded secrets (environment variables for profile URLs)
- Input validation maintained on existing endpoints

✅ **PASS** - Accessibility
- WCAG 2.1 AA compliance maintained
- Keyboard navigation support added
- Screen reader compatibility via ARIA labels
- Reduced motion preferences respected

✅ **PASS** - Performance and Scalability
- Performance budgets defined and monitored
- Adaptive performance via CPU/GPU benchmarking
- Lazy loading for demo video
- Horizontal scaling unaffected (frontend only)

### Spec-Driven Development Compliance

✅ **PASS** - Workflow Adherence
- Feature specification created via `/sp.specify`
- Clarifications completed via `/sp.clarify`
- Implementation plan created via `/sp.plan`
- Tasks will be generated via `/sp.tasks`
- Implementation will follow `/sp.implement`

**Constitution Check Result**: ✅ ALL GATES PASSED - No violations, no complexity justification required

## Project Structure

### Documentation (this feature)

```text
specs/004-sky-aura-glass/
├── spec.md              # Feature specification
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technology research)
├── data-model.md        # Phase 1 output (component architecture)
├── quickstart.md        # Phase 1 output (setup instructions)
├── contracts/           # Phase 1 output (component interfaces)
│   ├── AnimatedBackground.interface.ts
│   ├── NotchHeader.interface.ts
│   ├── GlassCard.interface.ts
│   └── animations.interface.ts
└── tasks.md             # Phase 2 output (NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── page.tsx                              # Landing page (UPDATE)
│   ├── globals.css                           # Global styles (UPDATE)
│   ├── (auth)/
│   │   ├── login/page.tsx                    # Login page (UPDATE)
│   │   └── signup/page.tsx                   # Signup page (UPDATE)
│   └── (protected)/
│       └── todo/
│           ├── page.tsx                      # Todo page (UPDATE)
│           └── components/
│               ├── TaskList.tsx              # Task list (UPDATE)
│               ├── TaskForm.tsx              # Task form (UPDATE)
│               ├── TaskFilters.tsx           # Filters (UPDATE)
│               ├── TagSidebar.tsx            # Tags (UPDATE)
│               └── CalendarView.tsx          # Calendar (UPDATE)
├── components/
│   ├── layout/                               # NEW
│   │   ├── AnimatedBackground.tsx
│   │   ├── NotchHeader.tsx
│   │   ├── PageWrapper.tsx
│   │   └── UserDropdown.tsx
│   ├── animations/                           # NEW
│   │   ├── TasksEntryAnimation.tsx
│   │   ├── ScrollReveal.tsx
│   │   └── FloatingElement.tsx
│   ├── hero/                                 # NEW
│   │   ├── HeroSection.tsx
│   │   ├── CloudBackground.tsx
│   │   └── DemoSection.tsx
│   └── ui/                                   # NEW
│       ├── GlassCard.tsx
│       └── GlassButton.tsx
├── lib/
│   └── utils/
│       └── performance.ts                    # NEW (CPU/GPU benchmarking)
├── package.json                              # UPDATE (add framer-motion)
└── tailwind.config.ts                        # UPDATE (Sky-Aura Glass utilities)
```

**Structure Decision**: Web application structure (Option 2) with frontend-only changes. Backend remains unchanged as authentication and data access are already implemented and working correctly.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All gates passed.

## Phase 0: Research & Technology Validation

### Research Topics

1. **Framer Motion Best Practices**
   - Animation performance optimization techniques
   - useReducedMotion hook implementation
   - AnimatePresence for exit animations
   - Stagger animations for lists
   - Scroll-triggered animations with useInView

2. **Glassmorphism Implementation**
   - CSS backdrop-filter browser support and fallbacks
   - Optimal blur values for readability
   - Layered shadow systems for bloom effects
   - Contrast ratio maintenance for accessibility

3. **Performance Optimization**
   - CPU/GPU benchmarking techniques in browser
   - Adaptive animation complexity strategies
   - will-change CSS property usage
   - Lazy loading for media content

4. **Session Management UX**
   - Session timeout detection patterns
   - Modal notification best practices
   - Session extension vs logout flows

5. **Nature Icon Selection**
   - Lucide icon mapping for growth metaphors
   - Icon sizing and stroke width for mature aesthetic
   - Accessibility considerations for icon-only buttons

**Output**: `research.md` with findings and recommendations

## Phase 1: Design & Component Architecture

### Component Hierarchy

```text
PageWrapper
├── AnimatedBackground (fixed, z-index: -10)
└── NotchHeader (fixed top)
    └── UserDropdown (authenticated users only)

Landing Page
├── PageWrapper
├── HeroSection
│   ├── CloudBackground
│   └── Nature Icons (floating)
└── DemoSection
    └── Video/GIF (autoplay, muted, loop)

Todo Page
├── PageWrapper
├── TasksEntryAnimation (on mount, skippable)
└── Todo Content
    ├── TaskFilters (glassmorphic tabs)
    ├── TaskList (GlassCard per task, floating)
    ├── TaskForm (glassmorphic modal)
    ├── TagSidebar (glassmorphic container)
    └── CalendarView (glassmorphic cells)

Auth Pages
├── PageWrapper
└── Form Container (glassmorphic)
    ├── Input Fields (glassmorphic, purple focus)
    └── GlassButton (submit)
```

### Data Model

**Component State Models**:

```typescript
// Session Timeout State
interface SessionTimeoutState {
  lastActivity: number;
  timeoutDuration: number; // 2 hours in ms
  showTimeoutModal: boolean;
}

// Animation Performance State
interface PerformanceState {
  benchmarkScore: number;
  reducedAnimations: boolean;
  userPreference: 'auto' | 'enabled' | 'disabled';
}

// Entry Animation State
interface EntryAnimationState {
  isPlaying: boolean;
  canSkip: boolean;
  hasCompleted: boolean;
}
```

**CSS Variables Model**:

```css
:root {
  /* Glass Properties */
  --glass-bg: rgba(255, 255, 255, 0.3);
  --glass-border: rgba(255, 255, 255, 0.5);
  --glass-blur: 12px;

  /* Glow Effects */
  --purple-glow: rgba(153, 41, 234, 0.3);
  --magenta-glow: rgba(255, 95, 207, 0.2);
  --gold-glow: rgba(250, 235, 146, 0.4);

  /* Color Palette */
  --aura-purple: #9929EA;
  --aura-magenta: #FF5FCF;
  --aura-gold: #FAEB92;
}
```

### API Contracts

**No new API endpoints required**. This feature uses existing authentication endpoints:

- `POST /api/auth/signout` - Existing Better Auth endpoint for logout
- Session validation handled by existing middleware

**Component Interfaces**: See `contracts/` directory for TypeScript interfaces

### Technology Decisions

1. **Animation Library**: Framer Motion
   - Rationale: Industry standard, excellent performance, built-in accessibility features
   - Alternatives considered: React Spring (more complex API), CSS animations (less control)

2. **Icon Library**: Lucide React
   - Rationale: Nature-themed icons available, thin stroke width, tree-shakeable
   - Alternatives considered: Heroicons (limited nature icons), custom SVGs (maintenance burden)

3. **UI Components**: shadcn/ui
   - Rationale: Already in use, headless components easy to restyle
   - Alternatives considered: Radix UI directly (more setup), custom components (time-consuming)

4. **Performance Detection**: Custom CPU/GPU benchmarking
   - Rationale: Real-time adaptive performance based on actual device capability
   - Alternatives considered: User agent detection (inaccurate), manual toggle only (poor UX)

**Output**: `data-model.md`, `contracts/`, `quickstart.md`

## Phase 2: Implementation Phases

### Phase 1: Foundation & Dependencies (Priority: P1)

**Duration**: 1 implementation session

**Tasks**:
1. Install framer-motion package
2. Install shadcn/ui components (dropdown-menu, avatar, button, card)
3. Update tailwind.config.ts with Sky-Aura Glass utilities
4. Add CSS variables to globals.css
5. Create performance benchmarking utility

**Acceptance Criteria**:
- All packages installed without conflicts
- Tailwind config includes glassmorphic utilities
- CSS variables accessible throughout application
- Performance utility can measure device capabilities

### Phase 2: Core Layout Components (Priority: P1)

**Duration**: 2-3 implementation sessions

**Tasks**:
1. Create AnimatedBackground component with gradient animation
2. Create NotchHeader component with iPhone-style notch
3. Create UserDropdown component with logout functionality
4. Create PageWrapper component for consistent layout
5. Test session timeout detection and modal display

**Acceptance Criteria**:
- Background animates smoothly (60fps)
- Notch header displays on all pages when authenticated
- Logout functionality works correctly
- Session timeout modal appears after 2 hours of inactivity
- PageWrapper provides consistent layout structure

### Phase 3: Hero & Landing Page (Priority: P2)

**Duration**: 2 implementation sessions

**Tasks**:
1. Create CloudBackground component with floating animations
2. Create HeroSection component with notched border
3. Create DemoSection component with video container
4. Update app/page.tsx with new components
5. Implement conditional CTA visibility based on auth state

**Acceptance Criteria**:
- Clouds float smoothly with interactive hover effects
- Hero section displays with glassmorphic styling
- Demo video autoplays muted and loops
- Login/signup CTAs hidden when user is authenticated
- All animations respect reduced motion preferences

### Phase 4: Todo Page Entry Animation (Priority: P3)

**Duration**: 1-2 implementation sessions

**Tasks**:
1. Create TasksEntryAnimation component (1.5s duration)
2. Create FloatingElement wrapper component
3. Update todo/page.tsx with entry animation
4. Implement skip functionality
5. Test animation triggers on every page visit

**Acceptance Criteria**:
- "TASKS" text fades in over 0.5 seconds
- Content bounces up over 1 second
- Skip button appears and functions correctly
- Animation plays on every visit (not just first)
- Animation can be skipped via button or key press

### Phase 5: Glassmorphic UI Components (Priority: P2)

**Duration**: 3-4 implementation sessions

**Tasks**:
1. Create GlassCard component with floating/breathing props
2. Create GlassButton component with interactions
3. Update TaskList with GlassCard and nature icons
4. Update TaskForm with glassmorphic styling
5. Update TaskFilters with glassmorphic tabs
6. Update TagSidebar with glassmorphic container
7. Update CalendarView with glassmorphic cells

**Acceptance Criteria**:
- All components display glassmorphic styling
- Nature icons (Leaf, Mountain, Sprout, Flower, Sun) used appropriately
- Hover states show breathing glow effects
- Focus states show purple glow outline
- Stagger animations work for list items

### Phase 6: Auth Pages Transformation (Priority: P2)

**Duration**: 1 implementation session

**Tasks**:
1. Update login/page.tsx with glassmorphic styling
2. Update signup/page.tsx with glassmorphic styling
3. Add nature icon (Door metaphor)
4. Test form functionality with new styling

**Acceptance Criteria**:
- Auth forms display glassmorphic styling
- Input fields show purple glow on focus
- Submit buttons use GlassButton component
- Forms remain fully functional

### Phase 7: Scroll Animations & Parallax (Priority: P3)

**Duration**: 1-2 implementation sessions

**Tasks**:
1. Create ScrollReveal component with useInView
2. Implement parallax background effect
3. Add stagger animations to task list and hero icons
4. Apply ScrollReveal to hero, demo, and task sections

**Acceptance Criteria**:
- Elements fade in as they enter viewport
- Background moves at 0.5x scroll speed
- Stagger animations create smooth sequential reveals
- Performance remains at 60fps during scrolling

### Phase 8: Polish & Accessibility (Priority: P1)

**Duration**: 2 implementation sessions

**Tasks**:
1. Implement reduced motion support throughout
2. Add focus states to all interactive elements
3. Add ARIA labels to icon buttons and skip button
4. Verify contrast ratios meet WCAG 2.1 AA
5. Optimize performance (lazy loading, will-change)
6. Test on mobile devices and adjust animations

**Acceptance Criteria**:
- Reduced motion preferences disable animations
- All interactive elements have visible focus states
- ARIA labels present for accessibility
- Contrast ratios meet WCAG 2.1 AA standards
- Page load time increase <20% vs baseline
- Animations run smoothly on mobile devices

## Implementation Order

1. **Foundation** (Phase 1): Install packages, update configs, add CSS variables
2. **Layout** (Phase 2): AnimatedBackground, NotchHeader, UserDropdown, PageWrapper
3. **Hero** (Phase 3): CloudBackground, HeroSection, DemoSection, update landing page
4. **Todo Animation** (Phase 4): TasksEntryAnimation, FloatingElement, update todo page
5. **Glassmorphic UI** (Phase 5): GlassCard, GlassButton, update all todo components
6. **Auth Pages** (Phase 6): Update login/signup with glassmorphic styling
7. **Scroll & Parallax** (Phase 7): ScrollReveal, parallax background, stagger animations
8. **Polish** (Phase 8): Accessibility, reduced motion, performance optimization

## Success Criteria

### Functionality

✅ User can logout from any page via NotchHeader dropdown
✅ Session persists across page refreshes until logout
✅ Session timeout modal appears after 2 hours of inactivity
✅ Login/signup CTAs hidden when user is authenticated
✅ All existing features work (task CRUD, calendar, filters, tags)

### Design

✅ iPhone-style notch header with glassmorphic styling
✅ Animated purple/magenta gradient background on all pages
✅ Hero section with notched border and interactive clouds
✅ Demo section with video autoplay (muted, looped)
✅ Todo page entry animation (1.5s, skippable)
✅ All components use glassmorphic styling (Sky-Aura Glass)
✅ Nature-aligned Lucide icons throughout
✅ Scroll animations and parallax effects
✅ Floating, breathing, organic motion
✅ Mature, peaceful, nature-inspired aesthetic

### Performance

✅ Animations run smoothly (60fps)
✅ No layout shifts or jank
✅ Reduced motion preferences respected
✅ Mobile-friendly (responsive, optimized animations)
✅ Page load time increase <20% vs current
✅ CPU/GPU benchmarking adapts animation complexity

### Accessibility

✅ WCAG 2.1 AA contrast ratios maintained
✅ Keyboard navigation support
✅ ARIA labels on icon buttons
✅ Focus states visible on all interactive elements
✅ Screen reader compatible

## Risk Mitigation

### Performance Risk
**Risk**: Complex animations and glassmorphic effects may impact performance on low-powered devices
**Mitigation**:
- Implement CPU/GPU benchmarking on first load
- Automatically reduce animation complexity on slower devices
- Provide manual toggle in settings
- Use will-change CSS property strategically
- Lazy load demo video

### Browser Compatibility Risk
**Risk**: Glassmorphic effects (backdrop-filter) not supported in older browsers
**Mitigation**:
- Provide graceful degradation with solid backgrounds
- Test on minimum supported browsers (Chrome 76+, Safari 9+, Firefox 103+)
- Document browser requirements in README

### Accessibility Risk
**Risk**: Translucent glassmorphic styling may reduce contrast and readability
**Mitigation**:
- Test contrast ratios thoroughly with automated tools
- Adjust opacity/blur levels to maintain WCAG 2.1 AA compliance
- Provide sufficient color contrast for text on glass surfaces

### User Preference Risk
**Risk**: Some users may find animations distracting or prefer minimal interfaces
**Mitigation**:
- Respect prefers-reduced-motion settings
- Provide skip options for animations
- Offer manual toggle in settings for animation control

### Scope Creep Risk
**Risk**: Visual transformation touches many components and may reveal additional work needed
**Mitigation**:
- Maintain strict focus on specified components
- Defer additional enhancements to future iterations
- Use phased implementation approach
- Regular checkpoint reviews against spec

## Dependencies

### External Dependencies
- Framer Motion: ^11.0.0 (animation library)
- Lucide React: ^0.300.0 (icon library)
- shadcn/ui components: dropdown-menu, avatar, button, card

### Internal Dependencies
- Existing Better Auth authentication system
- Existing Next.js App Router structure
- Existing Tailwind CSS configuration
- Existing task CRUD functionality

### Environment Variables
- `NEXT_PUBLIC_LINKEDIN_URL`: LinkedIn profile URL for notch header
- `NEXT_PUBLIC_GITHUB_URL`: GitHub profile URL for notch header
- `NEXT_PUBLIC_DEMO_VIDEO_URL`: Demo video/GIF URL for demo section

## Testing Strategy

### Unit Tests
- Component rendering tests for all new components
- Animation state management tests
- Performance benchmarking utility tests
- Session timeout detection tests

### Integration Tests
- Logout flow end-to-end
- Session timeout modal interaction
- Entry animation skip functionality
- Conditional CTA visibility based on auth state

### Visual Regression Tests
- Glassmorphic styling consistency
- Animation smoothness verification
- Responsive design across viewports
- Browser compatibility testing

### Accessibility Tests
- Automated contrast ratio checks
- Keyboard navigation testing
- Screen reader compatibility
- ARIA label verification

### Performance Tests
- Animation frame rate monitoring (target: 60fps)
- Page load time comparison (target: <20% increase)
- Memory usage profiling
- Mobile device performance testing

## Rollout Plan

### Phase 1: Development (Current)
- Implement all 8 phases in feature branch `004-sky-aura-glass`
- Test thoroughly in development environment
- Verify all acceptance criteria met

### Phase 2: Staging
- Deploy to staging environment
- Conduct user acceptance testing
- Gather feedback on aesthetic and performance
- Make adjustments as needed

### Phase 3: Production
- Deploy to production after approval
- Monitor performance metrics
- Collect user feedback
- Address any issues promptly

## Documentation Updates

### README.md
- Add Sky-Aura Glass design system documentation
- Document browser requirements
- Add screenshots of new UI

### CLAUDE.md (frontend)
- Add glassmorphic component patterns
- Document animation best practices
- Add nature icon mapping guide

### API Documentation
- No changes required (no new endpoints)

## Maintenance Considerations

### Long-term Maintenance
- Monitor Framer Motion updates for breaking changes
- Keep Lucide React updated for new nature icons
- Maintain glassmorphic design system consistency
- Update browser compatibility as needed

### Future Enhancements
- Additional nature-themed animations
- More glassmorphic components for future features
- Enhanced performance optimizations
- Additional accessibility improvements

---

**Plan Status**: ✅ READY FOR PHASE 0 RESEARCH

**Next Steps**:
1. Execute Phase 0 research on Framer Motion, glassmorphism, and performance optimization
2. Generate `research.md` with findings
3. Proceed to Phase 1 design artifacts (data-model.md, contracts/, quickstart.md)
4. Generate tasks via `/sp.tasks` command
