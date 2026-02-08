# Implementation Plan: Production Website Optimization

**Branch**: `012-prod-web-optimization` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/012-prod-web-optimization/spec.md`

## Summary

Transform the Todo application into a production-ready, high-performance website achieving <1 second load time, WCAG AA accessibility compliance, and SEO optimization while preserving the Sky-Aura Glass aesthetic. This optimization addresses 8 critical performance issues through systematic improvements across bundle size, runtime performance, accessibility, SEO, and code quality.

**Primary Goals:**
- Achieve Lighthouse performance score >90
- Reduce page load time to <1 second
- Ensure WCAG 2.1 Level AA compliance
- Reduce bundle size by 20%+
- Eliminate all console.log statements in production
- Implement comprehensive SEO with metadata, sitemap, and robots.txt

**Technical Approach:**
- Event-driven session checking (hybrid with 60s fallback)
- Self-hosted font subsetting for Chelsea Market font
- Component-based code splitting with dynamic imports
- CSS variable system with WCAG AA compliant color palette
- Comprehensive SEO metadata and structured data

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 15+ (App Router), React 19
**Primary Dependencies**:
- Frontend: Next.js, React, Tailwind CSS, Framer Motion, TanStack Query
- Fonts: next/font for self-hosted Chelsea Market (Latin subset)
- Analytics: next/web-vitals for Core Web Vitals monitoring
**Storage**: Neon PostgreSQL (existing, no schema changes required)
**Testing**: Lighthouse CLI, axe DevTools, webpack-bundle-analyzer
**Target Platform**: Web (modern browsers: last 2 versions Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (frontend optimization focus)
**Performance Goals**:
- Page load <1s (TTI)
- Task operations <1s
- Lighthouse score >90
- Bundle size reduction 20%+
**Constraints**:
- Preserve Sky-Aura Glass aesthetic
- Maintain existing functionality
- No breaking changes to API
- WCAG AA compliance mandatory
**Scale/Scope**:
- 36 files with 94 color contrast occurrences to fix
- 7 files with 32 console.log statements to remove
- 3 files >300 lines to refactor
- 8 critical performance issues to resolve

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Technology Stack Compliance
✅ **PASS** - Using approved Next.js 15+ with TypeScript
✅ **PASS** - Frontend optimization aligns with Phase II technology stack
✅ **PASS** - No changes to backend FastAPI or Neon PostgreSQL
✅ **PASS** - Better Auth authentication preserved

### Architecture Principles Compliance
✅ **PASS** - Stateless services maintained (event-driven session checking)
✅ **PASS** - Multi-user isolation unchanged (no database query modifications)
✅ **PASS** - Clean architecture preserved (frontend optimization only)

### Code Quality Standards Compliance
✅ **PASS** - Security: No hard-coded secrets, JWT verification unchanged
✅ **PASS** - Accessibility: WCAG 2.1 AA compliance is primary goal
✅ **PASS** - Performance: Targets align with constitution budgets (<200ms API, <50ms DB)
✅ **PASS** - Testing: Lighthouse and accessibility audits planned

### Spec-Driven Development Compliance
✅ **PASS** - Feature created via `/sp.specify`
✅ **PASS** - Clarifications completed via `/sp.clarify`
✅ **PASS** - Implementation plan via `/sp.plan` (this document)
✅ **PASS** - Tasks will be generated via `/sp.tasks`

### Violations Requiring Justification
**NONE** - All optimizations align with constitution principles

## Project Structure

### Documentation (this feature)

```text
specs/012-prod-web-optimization/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technology research)
├── data-model.md        # Phase 1 output (N/A - no data model changes)
├── quickstart.md        # Phase 1 output (optimization guide)
├── contracts/           # Phase 1 output (N/A - no API changes)
├── checklists/          # Quality validation checklists
│   └── requirements.md  # Specification quality checklist (completed)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── layout.tsx                    # [MODIFY] Add metadata, fonts, structured data
│   ├── sitemap.ts                    # [CREATE] SEO sitemap generation
│   ├── robots.ts                     # [CREATE] SEO robots.txt
│   ├── globals.css                   # [MODIFY] Add CSS variable system
│   └── (protected)/
│       └── todo/
│           └── page.tsx              # [MODIFY] Remove duplicate QueryClient, session check
├── components/
│   ├── ui/
│   │   ├── connection-status.tsx     # [MODIFY] Remove unused variants
│   │   └── empty-state.tsx           # [CREATE] Reusable empty state component
│   ├── tasks/
│   │   ├── TaskList.tsx              # [MODIFY] Replace hardcoded colors
│   │   └── TaskMetadata.tsx          # [CREATE] Reusable metadata component
│   ├── layout/
│   │   ├── NotchHeader.tsx           # [MODIFY] Add ConnectionStatus, DeveloperLinks
│   │   └── DeveloperLinks.tsx        # [CREATE] Quick access dropdown
│   └── analytics/
│       └── WebVitals.tsx             # [CREATE] Core Web Vitals monitoring
├── lib/
│   ├── utils.ts                      # [MODIFY] Add devLog utility
│   ├── websocket-client.ts           # [MODIFY] Replace console.log with devLog
│   └── chat-client.ts                # [MODIFY] Replace console.log with devLog
├── hooks/
│   ├── useWebSocket.ts               # [MODIFY] Replace console.log with devLog
│   ├── useTasks.ts                   # [MODIFY] Replace console.log with devLog
│   └── useChat.ts                    # [MODIFY] Replace console.log with devLog
├── tailwind.config.ts                # [MODIFY] Add text color system
├── next.config.js                    # [VERIFY] Confirm optimizePackageImports
└── package.json                      # [VERIFY] Dependencies up to date

.claude/skills/
└── web-performance-optimization/     # [CREATE] Reusable optimization skill
    ├── SKILL.md
    ├── 00-overview.md
    ├── 01-bundle-optimization.md
    ├── 02-runtime-performance.md
    ├── 03-seo-setup.md
    ├── 04-accessibility.md
    └── 05-monitoring.md
```

**Structure Decision**: Web application structure with frontend-only modifications. No backend changes required. Focus on performance optimization, accessibility compliance, and SEO implementation within existing Next.js App Router architecture.

## Complexity Tracking

> **No violations - this section intentionally left empty**

All optimizations align with constitution principles. No additional complexity introduced.

---

## Phase 0: Research & Technology Validation

### Research Tasks

1. **Bundle Analysis Baseline**
   - Run `ANALYZE=true npm run build` to establish current bundle size
   - Document baseline metrics: total bundle size, largest chunks, dependencies
   - Identify optimization opportunities from bundle analyzer output

2. **Performance Baseline Measurement**
   - Run Lighthouse audit on current production build
   - Document current scores: Performance, Accessibility, Best Practices, SEO
   - Measure current page load times (FCP, LCP, TTI, CLS, FID)
   - Establish baseline for 20% reduction target

3. **Accessibility Audit**
   - Run axe DevTools on all pages
   - Document current WCAG violations
   - Verify 94 text contrast issues (text-white/50, text-white/60)
   - Test keyboard navigation coverage

4. **Font Loading Analysis**
   - Analyze current Google Fonts loading (Chelsea Market)
   - Measure render-blocking impact
   - Research next/font implementation for self-hosting
   - Validate Latin subset size (~20-30KB)

5. **Code Splitting Opportunities**
   - Identify components >300 lines (RecurringPatternForm, chart.tsx, SearchBar)
   - Analyze current dynamic imports
   - Research React.lazy() and Next.js dynamic() patterns
   - Document component-based splitting strategy

6. **Session Checking Patterns**
   - Research event-driven session validation patterns
   - Document best practices for token expiry detection
   - Analyze page visibility API for tab switching
   - Design hybrid approach (event-driven + 60s fallback)

7. **Color Palette Validation**
   - Test provided colors (FFCF56, EDEAD0, 86BAA1, A0E8AF, 3AB795) for WCAG AA compliance
   - Calculate contrast ratios against typical backgrounds
   - Document which colors meet 4.5:1 (normal text) and 3:1 (large text)
   - Create mapping strategy for 94 occurrences

**Output**: `research.md` with baseline metrics, technology decisions, and implementation patterns

---

## Phase 1: Design & Implementation Strategy

### 1.1 Data Model

**N/A** - This feature involves frontend optimization only. No database schema changes required.

### 1.2 API Contracts

**N/A** - No new API endpoints. Existing endpoints unchanged.

### 1.3 Component Architecture

**New Components:**
1. **EmptyState** (`components/ui/empty-state.tsx`)
   - Props: icon, title, description, action, className
   - Purpose: Reusable empty state for TaskList, ConversationList, TagSidebar, CalendarView
   - Reduces code duplication by ~100 lines

2. **TaskMetadata** (`components/tasks/TaskMetadata.tsx`)
   - Props: task, showTags, showDueDate, showPriority, compact
   - Purpose: Consistent metadata display across task views
   - Consolidates tag, due date, priority rendering logic

3. **DeveloperLinks** (`components/layout/DeveloperLinks.tsx`)
   - Props: None (uses environment variables)
   - Purpose: Quick access dropdown for frontend, API docs, API health
   - Improves developer experience

4. **WebVitals** (`components/analytics/WebVitals.tsx`)
   - Props: None
   - Purpose: Core Web Vitals monitoring and reporting
   - Tracks FCP, LCP, CLS, FID, TTFB

**Modified Components:**
- `app/layout.tsx`: Add metadata, fonts, structured data, WebVitals
- `app/(protected)/todo/page.tsx`: Remove duplicate QueryClient, optimize session check
- `components/layout/NotchHeader.tsx`: Add ConnectionStatus, DeveloperLinks, login button
- `components/ui/connection-status.tsx`: Remove unused variants (70 lines)
- 36 files: Replace hardcoded colors with CSS variables

### 1.4 CSS Variable System

**Color System** (`app/globals.css`):
```css
:root {
  /* Text Color System - WCAG AA Compliant */
  --text-primary: rgba(255, 255, 255, 1);        /* Primary text */
  --text-secondary: rgba(255, 255, 255, 0.85);   /* Secondary text */
  --text-tertiary: rgba(255, 255, 255, 0.70);    /* Tertiary text */
  --text-muted: rgba(255, 255, 255, 0.60);       /* Muted text */
  --text-disabled: rgba(255, 255, 255, 0.40);    /* Disabled text */

  /* Interactive States */
  --text-hover: rgba(255, 255, 255, 1);
  --text-active: rgba(125, 211, 252, 1);         /* Sky-cyan */
  --text-link: rgba(125, 211, 252, 0.9);
  --text-link-hover: rgba(186, 230, 253, 1);

  /* Status Colors */
  --text-success: rgba(34, 197, 94, 1);
  --text-warning: rgba(234, 179, 8, 1);
  --text-error: rgba(239, 68, 68, 1);
  --text-info: rgba(59, 130, 246, 1);
}
```

**Tailwind Integration** (`tailwind.config.ts`):
```typescript
text: {
  primary: 'var(--text-primary)',
  secondary: 'var(--text-secondary)',
  tertiary: 'var(--text-tertiary)',
  muted: 'var(--text-muted)',
  disabled: 'var(--text-disabled)',
  hover: 'var(--text-hover)',
  active: 'var(--text-active)',
  link: 'var(--text-link)',
  'link-hover': 'var(--text-link-hover)',
}
```

**Color Mapping Strategy:**
- `text-white/50` → `text-text-muted`
- `text-white/60` → `text-text-muted`
- `text-white/70` → `text-text-tertiary`
- `text-white/80` → `text-text-secondary`
- `text-white` → `text-text-primary`

### 1.5 SEO Configuration

**Metadata** (`app/layout.tsx`):
- Title template: "%s | Ary's Evolved Todo"
- Description: Production-ready task management with AI chatbot
- Open Graph tags for social sharing
- Twitter Card metadata
- Robots configuration (index: true, follow: true)

**Sitemap** (`app/sitemap.ts`):
- Routes: /, /todo, /chat, /login, /signup
- Priority and change frequency per route
- Dynamic generation from Next.js MetadataRoute

**Robots.txt** (`app/robots.ts`):
- Allow: /
- Disallow: /api/, /admin/
- Sitemap reference

**Structured Data** (`app/layout.tsx`):
- JSON-LD WebApplication schema
- Application category: ProductivityApplication
- Pricing information (free)

### 1.6 Font Optimization Strategy

**Implementation** (`app/layout.tsx`):
```typescript
import { Inter, Chelsea_Market } from "next/font/google"

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

const chelseaMarket = Chelsea_Market({
  weight: '400',
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-chelsea',
})
```

**Benefits:**
- Self-hosted fonts (no external requests)
- Latin subset only (~20-30KB)
- font-display: swap prevents FOIT
- CSS variables for Tailwind integration
- 200-400ms faster FCP

### 1.7 Session Checking Strategy

**Event-Driven Implementation** (`app/(protected)/todo/page.tsx`):
```typescript
useEffect(() => {
  // Event-driven checks
  const handleVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      // Check session when user returns to tab
      validateSession()
    }
  }

  const handleUserActivity = () => {
    // Check session on user interaction after idle
    if (isIdle) {
      validateSession()
    }
  }

  // Fallback polling (60s)
  const interval = setInterval(() => {
    validateSession()
  }, 60000)

  document.addEventListener('visibilitychange', handleVisibilityChange)
  window.addEventListener('click', handleUserActivity)

  return () => {
    clearInterval(interval)
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    window.removeEventListener('click', handleUserActivity)
  }
}, [session])
```

**Benefits:**
- Zero overhead when idle
- Immediate validation on user return
- 60s fallback for edge cases
- Eliminates 20 checks per minute

### 1.8 Code Splitting Strategy

**Component-Based Dynamic Imports:**
```typescript
// Heavy form component (388 lines)
const RecurringPatternForm = dynamic(
  () => import('@/components/tasks/RecurringPatternForm'),
  { ssr: false, loading: () => <Skeleton className="h-96" /> }
)

// Complex autocomplete (327 lines)
const SearchBar = dynamic(
  () => import('@/components/search/SearchBar'),
  { ssr: false, loading: () => <Skeleton className="h-10" /> }
)

// Chart component (Recharts is heavy)
const TaskAnalyticsCard = dynamic(
  () => import('@/components/tasks/TaskAnalyticsCard'),
  { ssr: false, loading: () => <Skeleton className="h-64" /> }
)
```

**Benefits:**
- 20-30% smaller initial bundle
- Faster page loads
- Better code organization
- Lazy loading for non-critical features

**Output**: `quickstart.md` with optimization implementation guide

---

## Phase 2: Implementation Phases

### Phase 2.1: Critical Performance Fixes (HIGH PRIORITY)

**Estimated Impact**: 30-40% performance improvement, 200-400ms faster load

#### Task 2.1.1: Remove Duplicate QueryClient
**File**: `frontend/app/(protected)/todo/page.tsx`
**Changes**:
- Remove line 46: `const queryClient = new QueryClient()`
- Remove lines 332-338: QueryClientProvider wrapper
- Change export to: `export default function TodoPage() { return <TodoPageContent /> }`

**Impact**: Fixes cache conflicts, reduces memory by 2-3MB, 50-100ms faster transitions

**Verification**:
```bash
npm run dev
# Navigate to /todo, add/edit/delete tasks
# Check browser console for errors
# Verify real-time updates function
```

#### Task 2.1.2: Optimize Console.log Statements
**Files**: 7 files with 32 occurrences

**Create utility** in `frontend/lib/utils.ts`:
```typescript
export const devLog = (...args: any[]) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(...args)
  }
}
```

**Replace in**:
- `lib/websocket-client.ts` (7 occurrences)
- `hooks/useWebSocket.ts` (5 occurrences)
- `hooks/useTasks.ts` (6 occurrences)
- `hooks/useChat.ts` (8 occurrences)
- `app/(protected)/todo/page.tsx` (3 occurrences - lines 76, 82, 91-95)
- `app/(auth)/login/page.tsx` (2 occurrences)
- `lib/chat-client.ts` (1 occurrence)

**Impact**: Eliminates 32 console calls in production, 10-20ms improvement per page load

#### Task 2.1.3: Implement Event-Driven Session Checking
**File**: `frontend/app/(protected)/todo/page.tsx` lines 89-99

**Implementation**: Replace 3-second polling with hybrid event-driven approach (see Phase 1.7)

**Impact**: Eliminates 20 checks per minute, 20-30ms better responsiveness

#### Task 2.1.4: Optimize Font Loading with next/font
**File**: `frontend/app/layout.tsx`

**Implementation**: Self-host Chelsea Market font with Latin subset (see Phase 1.6)

**Impact**: 200-400ms faster FCP, eliminates render-blocking, improves Lighthouse by 5-10 points

#### Task 2.1.5: Remove Unused ConnectionStatus Variants
**File**: `frontend/components/ui/connection-status.tsx`

**Changes**: Remove lines 94-174 (ConnectionStatusCompact, ConnectionStatusDetailed)

**Impact**: 2-3KB smaller bundle, cleaner code

### Phase 2.2: Layout & UX Improvements

#### Task 2.2.1: Move ConnectionStatus to NotchHeader
**File**: `frontend/components/layout/NotchHeader.tsx`

**Changes**:
- Add import: `import { ConnectionStatus } from '@/components/ui/connection-status'`
- Add to navigation: `<ConnectionStatus showLabel={false} className="px-2 py-1 mr-1" />`
- Remove from `frontend/app/(protected)/todo/page.tsx` line 231

**Impact**: Connection status visible on all authenticated pages

#### Task 2.2.2: Create DeveloperLinks Component
**File**: `frontend/components/layout/DeveloperLinks.tsx` (new)

**Implementation**: Dropdown menu with links to frontend, API docs, API health (see Phase 1.3)

**Impact**: Easy access to backend API docs and health checks

#### Task 2.2.3: Add Login Button to Navbar
**File**: `frontend/components/layout/NotchHeader.tsx`

**Changes**: Add login/signup button when user is not authenticated

**Impact**: Improved discoverability and user experience

### Phase 2.3: Color System & Accessibility

#### Task 2.3.1: Create CSS Variable System
**File**: `frontend/app/globals.css`

**Implementation**: Add CSS variables for text colors (see Phase 1.4)

**Impact**: Foundation for WCAG AA compliance

#### Task 2.3.2: Update Tailwind Config
**File**: `frontend/tailwind.config.ts`

**Implementation**: Add text color system to extend.colors (see Phase 1.4)

**Impact**: Tailwind classes for accessible colors

#### Task 2.3.3: Replace Hardcoded Colors
**Strategy**: Replace across 36 files with 94 occurrences

**Priority files**:
1. `app/(protected)/todo/page.tsx` (5 occurrences)
2. `components/tasks/TaskList.tsx` (7 occurrences)
3. `components/chat/MessageThread.tsx` (6 occurrences)
4. `components/layout/NotchHeader.tsx` (4 occurrences)

**Impact**: WCAG AA compliance, consistent theming, better readability

### Phase 2.4: Component Library & Reusability

#### Task 2.4.1: Create EmptyState Component
**File**: `frontend/components/ui/empty-state.tsx` (new)

**Implementation**: Reusable empty state component (see Phase 1.3)

**Use in**:
- `components/tasks/TaskList.tsx`
- `components/chat/ConversationList.tsx`
- `components/tasks/TagSidebar.tsx`
- `components/tasks/CalendarView.tsx`

**Impact**: Reduces code duplication by ~100 lines

#### Task 2.4.2: Create TaskMetadata Component
**File**: `frontend/components/tasks/TaskMetadata.tsx` (new)

**Implementation**: Reusable metadata component (see Phase 1.3)

**Impact**: Consistent metadata display, reduced duplication

### Phase 2.5: SEO & Production Readiness

#### Task 2.5.1: Add Metadata Configuration
**File**: `frontend/app/layout.tsx`

**Implementation**: Add metadata export (see Phase 1.5)

**Impact**: SEO optimized, proper social sharing

#### Task 2.5.2: Create Sitemap
**File**: `frontend/app/sitemap.ts` (new)

**Implementation**: Generate sitemap with all public routes (see Phase 1.5)

**Impact**: Search engine discoverability

#### Task 2.5.3: Create Robots.txt
**File**: `frontend/app/robots.ts` (new)

**Implementation**: Configure crawling rules (see Phase 1.5)

**Impact**: Proper search engine indexing

#### Task 2.5.4: Add JSON-LD Structured Data
**File**: `frontend/app/layout.tsx`

**Implementation**: Add WebApplication schema (see Phase 1.5)

**Impact**: Rich search results

#### Task 2.5.5: Implement Core Web Vitals Monitoring
**File**: `frontend/components/analytics/WebVitals.tsx` (new)

**Implementation**: Track and report Core Web Vitals (see Phase 1.3)

**Impact**: Performance monitoring and optimization feedback

### Phase 2.6: Bundle Optimization

#### Task 2.6.1: Add Dynamic Imports for Heavy Components
**Files**:
1. `RecurringPatternForm.tsx` (388 lines)
2. `chart.tsx` (389 lines)
3. `SearchBar.tsx` (327 lines)

**Implementation**: Use React.lazy() and dynamic() (see Phase 1.8)

**Impact**: 20-30% smaller initial bundle

#### Task 2.6.2: Verify Package Import Optimization
**File**: `frontend/next.config.js`

**Verification**: Confirm optimizePackageImports includes framer-motion, @tanstack/react-query, recharts, lucide-react

**Impact**: Optimized third-party dependencies

#### Task 2.6.3: Analyze Bundle with webpack-bundle-analyzer
**Command**: `ANALYZE=true npm run build`

**Verification**: Check bundle sizes, verify dynamic imports work, test lazy loading

**Impact**: Validate 20%+ bundle size reduction

### Phase 2.7: Create Reusable Skill

#### Task 2.7.1: Create Skill Structure
**Directory**: `.claude/skills/web-performance-optimization/`

**Files**:
1. `SKILL.md` - Main skill documentation
2. `00-overview.md` - Performance optimization overview
3. `01-bundle-optimization.md` - Bundle size reduction techniques
4. `02-runtime-performance.md` - Runtime optimization patterns
5. `03-seo-setup.md` - SEO configuration guide
6. `04-accessibility.md` - WCAG compliance checklist
7. `05-monitoring.md` - Performance monitoring setup

**Impact**: Reusable optimization knowledge for future features

---

## Verification & Testing

### Phase 1 Verification

**QueryClient Fix**:
```bash
npm run dev
# Navigate to /todo, add/edit/delete tasks
# Check browser console for errors
# Verify real-time updates work
```

**Console.log Removal**:
```bash
npm run build
npm start
# Check browser console - should be clean
```

**Font Optimization**:
```bash
npm run build
# Check Network tab - fonts should be self-hosted
# Measure FCP improvement
```

**Lighthouse Audit**:
```bash
npm run build
npm start
# Open Chrome DevTools > Lighthouse
# Run audit, verify score > 90
```

### Phase 2 Verification

**ConnectionStatus Visibility**:
- Navigate to /todo, /chat - status should be visible on both
- Test DeveloperLinks dropdown
- Click links, verify they open correctly

### Phase 3 Verification

**Color System**:
- Check text contrast with browser DevTools
- Verify WCAG AA compliance
- Test hover states

### Phase 4 Verification

**EmptyState Component**:
- Delete all tasks, verify empty state shows
- Test TaskMetadata component
- Verify tags, due dates, priority display correctly

### Phase 5 Verification

**SEO**:
- Visit /sitemap.xml - should show all routes
- Visit /robots.txt - should show rules
- Check page source for metadata tags
- Test OpenGraph with https://www.opengraph.xyz/

**Core Web Vitals**:
- Open Chrome DevTools > Performance
- Record page load
- Check CLS, LCP, FID metrics

### Phase 6 Verification

**Bundle Analysis**:
```bash
ANALYZE=true npm run build
# Check bundle sizes
# Verify dynamic imports work
# Test lazy loading
```

---

## Rollback Plan

### If Issues Occur

1. **Revert specific commit**: `git revert <commit-hash>`
2. **Restore from backup**: Keep backup of critical files before changes
3. **Feature flags**: Wrap changes in environment checks

### Critical Files to Backup

- `frontend/app/layout.tsx`
- `frontend/app/(protected)/todo/page.tsx`
- `frontend/next.config.js`
- `frontend/tailwind.config.ts`
- `frontend/app/globals.css`

---

## Success Metrics

### Before Optimization

- Page load: ~2-3 seconds
- Bundle size: ~500KB (baseline to be measured)
- Lighthouse score: ~70 (baseline to be measured)
- Console logs: 32 in production
- WCAG compliance: Fails (94 contrast violations)

### After Optimization

- Page load: <1 second ✅
- Bundle size: ~300KB (20%+ reduction) ✅
- Lighthouse score: >90 ✅
- Console logs: 0 in production ✅
- WCAG compliance: AA ✅

### Performance Targets

- First Contentful Paint: <1.8s
- Largest Contentful Paint: <2.5s
- Cumulative Layout Shift: <0.1
- First Input Delay: <100ms
- Time to Interactive: <1s

---

## Estimated Impact Summary

| Phase | Impact | Priority |
|-------|--------|----------|
| Phase 1 | 30-40% perf improvement | HIGH |
| Phase 2 | Better UX | HIGH |
| Phase 3 | WCAG AA compliance | HIGH |
| Phase 4 | 15-20% code reduction | MEDIUM |
| Phase 5 | SEO optimized | HIGH |
| Phase 6 | 20-30% bundle reduction | MEDIUM |
| Phase 7 | Reusable skill | LOW |

**Total Performance Gain**: 40-50% faster load times
**Bundle Size Reduction**: 30-40%

---

## Notes

- All changes maintain existing functionality
- Sky-Aura Glass aesthetic preserved with new color palette (FFCF56, EDEAD0, 86BAA1, A0E8AF, 3AB795)
- No breaking changes to API
- Backward compatible
- Production-ready
- Accessibility prioritized over pure aesthetic (ease of use is priority)
- Event-driven session checking eliminates polling overhead
- Self-hosted fonts eliminate external dependencies
- Component-based code splitting maximizes bundle reduction
