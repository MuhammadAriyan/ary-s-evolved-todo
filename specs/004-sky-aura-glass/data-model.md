# Data Model: Sky-Aura Glass Component Architecture

**Feature**: 004-sky-aura-glass
**Date**: 2026-01-07
**Status**: Complete

## Overview

This document defines the component architecture, state models, and data flows for the Sky-Aura Glass UI transformation. All components are stateless React components using TypeScript for type safety.

## Component Hierarchy

```
Application Root
│
├── PageWrapper (Layout)
│   ├── AnimatedBackground (Fixed, z-index: -10)
│   └── NotchHeader (Fixed top, z-index: 50)
│       └── UserDropdown (Conditional: authenticated only)
│
├── Landing Page (/)
│   ├── PageWrapper
│   ├── HeroSection
│   │   ├── CloudBackground (Absolute positioning)
│   │   └── FloatingElement[] (Nature icons)
│   └── DemoSection
│       └── Video/GIF (Lazy loaded)
│
├── Todo Page (/todo)
│   ├── PageWrapper
│   ├── TasksEntryAnimation (Full-screen overlay, z-index: 50)
│   └── Todo Content
│       ├── TaskFilters (Glassmorphic tabs)
│       ├── TaskList
│       │   └── GlassCard[] (Per task, with FloatingElement wrapper)
│       ├── TaskForm (Modal overlay)
│       │   ├── GlassCard (Container)
│       │   └── GlassButton (Submit)
│       ├── TagSidebar (GlassCard container)
│       └── CalendarView (Glassmorphic cells)
│
└── Auth Pages (/login, /signup)
    ├── PageWrapper
    └── Form Container (GlassCard)
        ├── Input Fields (Glassmorphic styling)
        └── GlassButton (Submit)
```

## Component State Models

### 1. Session Timeout State

```typescript
interface SessionTimeoutState {
  lastActivity: number;           // Timestamp of last user activity
  timeoutDuration: number;         // 2 hours in milliseconds (7200000)
  showTimeoutModal: boolean;       // Whether to display timeout modal
  timeRemaining: number;           // Seconds until timeout
}

// Usage in NotchHeader or PageWrapper
const [sessionState, setSessionState] = useState<SessionTimeoutState>({
  lastActivity: Date.now(),
  timeoutDuration: 7200000,
  showTimeoutModal: false,
  timeRemaining: 7200,
});
```

### 2. Animation Performance State

```typescript
interface PerformanceState {
  benchmarkScore: number;          // 0-100 (100 = excellent performance)
  complexity: 'full' | 'reduced' | 'minimal';
  userPreference: 'auto' | 'enabled' | 'disabled';
  hasBeenBenchmarked: boolean;
}

// Thresholds
const COMPLEXITY_THRESHOLDS = {
  full: 60,      // Score >= 60: full animations
  reduced: 30,   // Score >= 30: reduced animations
  minimal: 0,    // Score < 30: minimal animations
};

// Usage in root layout or PageWrapper
const [perfState, setPerfState] = useState<PerformanceState>({
  benchmarkScore: 0,
  complexity: 'full',
  userPreference: 'auto',
  hasBeenBenchmarked: false,
});
```

### 3. Entry Animation State

```typescript
interface EntryAnimationState {
  isPlaying: boolean;              // Animation currently playing
  canSkip: boolean;                // Skip button enabled (after 0.5s)
  hasCompleted: boolean;           // Animation finished
  animationKey: string;            // Unique key per page visit (timestamp)
}

// Usage in TasksEntryAnimation
const [animState, setAnimState] = useState<EntryAnimationState>({
  isPlaying: true,
  canSkip: false,
  hasCompleted: false,
  animationKey: Date.now().toString(),
});
```

### 4. Glass Component Props

```typescript
interface GlassCardProps {
  children: React.ReactNode;
  floating?: boolean;              // Enable floating animation
  breathing?: boolean;             // Enable breathing glow on hover
  className?: string;              // Additional Tailwind classes
  onClick?: () => void;            // Optional click handler
}

interface GlassButtonProps {
  children: React.ReactNode;
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'ghost';
  disabled?: boolean;
  onClick?: () => void;
  className?: string;
}

interface FloatingElementProps {
  children: React.ReactNode;
  duration?: number;               // Animation duration (default: 4s)
  yOffset?: number;                // Vertical movement (default: -12px)
  delay?: number;                  // Animation delay (default: 0s)
}

interface ScrollRevealProps {
  children: React.ReactNode;
  delay?: number;                  // Reveal delay (default: 0s)
  once?: boolean;                  // Animate once (default: true)
  margin?: string;                 // Intersection margin (default: '-100px')
}
```

## CSS Variables Model

```typescript
// globals.css
:root {
  /* Glass Properties */
  --glass-bg: rgba(255, 255, 255, 0.3);
  --glass-border: rgba(255, 255, 255, 0.5);
  --glass-blur: 12px;
  --glass-blur-heavy: 20px;

  /* Glow Effects */
  --cyan-glow: rgba(125, 211, 252, 0.3);
  --aqua-glow: rgba(186, 230, 253, 0.2);
  --white-glow: rgba(224, 242, 254, 0.4);

  /* Color Palette */
  --sky-cyan: #7dd3fc;
  --soft-aqua: #bae6fd;
  --misty-white: #e0f2fe;
  --misty-green: #d1fae5;

  /* Animation Durations */
  --duration-fast: 0.3s;
  --duration-normal: 0.5s;
  --duration-slow: 1s;
  --duration-entry: 1.5s;

  /* Easing Functions */
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

## Tailwind Configuration Extensions

```typescript
// tailwind.config.ts extensions
theme: {
  extend: {
    colors: {
      'sky-cyan': '#7dd3fc',
      'soft-aqua': '#bae6fd',
      'misty-white': '#e0f2fe',
      'misty-green': '#d1fae5',
    },
    backdropBlur: {
      xs: '2px',
      glass: '12px',
      heavy: '20px',
    },
    boxShadow: {
      'glass-sm': '0 2px 8px rgba(125, 211, 252, 0.2)',
      'glass-md': '0 4px 16px rgba(125, 211, 252, 0.3)',
      'glass-lg': '0 8px 32px rgba(186, 230, 253, 0.2)',
      'bloom': `
        inset 0 1px 0 0 rgba(255, 255, 255, 0.4),
        0 4px 16px rgba(125, 211, 252, 0.3),
        0 8px 32px rgba(186, 230, 253, 0.2),
        0 12px 48px rgba(224, 242, 254, 0.4)
      `,
    },
    animation: {
      'float': 'float 4s ease-in-out infinite',
      'breathe': 'breathe 3s ease-in-out infinite',
      'gradient': 'gradient 12s ease-in-out infinite',
    },
    keyframes: {
      float: {
        '0%, 100%': { transform: 'translateY(0)' },
        '50%': { transform: 'translateY(-12px)' },
      },
      breathe: {
        '0%, 100%': { opacity: '0.8' },
        '50%': { opacity: '1' },
      },
      gradient: {
        '0%, 100%': { backgroundPosition: '0% 50%' },
        '50%': { backgroundPosition: '100% 50%' },
      },
    },
  },
}
```

## Component Data Flows

### 1. Authentication Flow

```
User Action (Logout) → UserDropdown
  ↓
signOut() from Better Auth client
  ↓
POST /api/auth/signout
  ↓
Clear httpOnly cookie
  ↓
Redirect to /login
```

### 2. Session Timeout Flow

```
User Activity Events → PageWrapper/NotchHeader
  ↓
Update lastActivity timestamp
  ↓
Interval check (every 60s)
  ↓
If elapsed >= 2 hours → Show timeout modal
  ↓
User Choice:
  ├─ Extend Session → Refresh token, reset timer
  └─ Logout → signOut(), redirect to /login
```

### 3. Performance Detection Flow

```
App Mount → PageWrapper
  ↓
Check localStorage for cached benchmark
  ↓
If not cached:
  ├─ Run CPU/GPU benchmark
  ├─ Calculate score (0-100)
  ├─ Determine complexity (full/reduced/minimal)
  └─ Cache result in localStorage
  ↓
Apply animation complexity globally
  ↓
Respect user preference override (if set)
```

### 4. Entry Animation Flow

```
Navigate to /todo → TasksEntryAnimation mounts
  ↓
Generate unique animationKey (timestamp)
  ↓
Phase 1: "TASKS" text fade-in (0.5s)
  ↓
Enable skip button
  ↓
Phase 2: Content bounce-up (1s)
  ↓
Animation complete → Remove overlay
  ↓
Show todo content
```

## Icon Mapping (Nature Metaphor System)

```typescript
// lib/icons.ts
import {
  Leaf,
  Mountain,
  Sprout,
  Droplet,
  Sun,
  Wind,
  Flower,
  Linkedin,
  Github,
  User,
  LogOut,
  DoorOpen,
  X,
  Edit,
} from 'lucide-react';

export const ICON_MAP = {
  // Task states (growth cycle)
  task: {
    incomplete: Leaf,      // Growing, active
    complete: Mountain,    // Achievement, peak
    new: Sprout,          // Potential, beginning
  },

  // Header
  header: {
    linkedin: Linkedin,
    github: Github,
    account: User,
  },

  // User dropdown
  dropdown: {
    profile: User,
    logout: LogOut,
  },

  // Todo actions
  actions: {
    add: Sprout,
    delete: X,
    edit: Edit,
  },

  // Decorative (hero section)
  decorative: [Leaf, Droplet, Sun, Wind],

  // UI elements
  ui: {
    tags: Flower,
    calendar: Sun,
    auth: DoorOpen,
  },
} as const;

export const ICON_SIZES = {
  sm: 16,
  md: 20,
  lg: 24,
  xl: 32,
} as const;

export const ICON_STROKE_WIDTH = 1.5;
```

## Animation Configuration

```typescript
// lib/animations.ts
import { Variants } from 'framer-motion';

export const ANIMATION_VARIANTS = {
  // Fade in from bottom
  fadeInUp: {
    hidden: { opacity: 0, y: 40 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.5, ease: 'easeOut' },
    },
  } as Variants,

  // Scale and fade
  scaleIn: {
    hidden: { opacity: 0, scale: 0.8 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.3, ease: 'easeOut' },
    },
  } as Variants,

  // Stagger container
  staggerContainer: {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2,
      },
    },
  } as Variants,

  // Entry animation (TASKS text)
  tasksEntry: {
    hidden: { opacity: 0, scale: 0.8, y: 20 },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: { duration: 0.5, ease: 'easeOut' },
    },
  } as Variants,

  // Content bounce up
  contentBounce: {
    hidden: { opacity: 0, y: 60 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 1, ease: 'easeOut' },
    },
  } as Variants,
};

export const ANIMATION_DURATIONS = {
  fast: 0.3,
  normal: 0.5,
  slow: 1,
  entry: 1.5,
  gradient: 12,
  float: 4,
  breathe: 3,
} as const;
```

## Performance Utilities

```typescript
// lib/utils/performance.ts
export interface BenchmarkResult {
  score: number;
  complexity: 'full' | 'reduced' | 'minimal';
  timestamp: number;
}

export async function benchmarkDevice(): Promise<BenchmarkResult> {
  // Check cache first
  const cached = localStorage.getItem('device-benchmark');
  if (cached) {
    const result = JSON.parse(cached) as BenchmarkResult;
    // Cache valid for 7 days
    if (Date.now() - result.timestamp < 7 * 24 * 60 * 60 * 1000) {
      return result;
    }
  }

  // Run benchmark
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');

  if (!gl) {
    const result = { score: 0, complexity: 'minimal' as const, timestamp: Date.now() };
    localStorage.setItem('device-benchmark', JSON.stringify(result));
    return result;
  }

  const startTime = performance.now();
  const iterations = 1000;

  for (let i = 0; i < iterations; i++) {
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  }

  const endTime = performance.now();
  const duration = endTime - startTime;
  const score = Math.max(0, Math.min(100, 100 - (duration / 10)));

  const complexity = getComplexity(score);
  const result = { score, complexity, timestamp: Date.now() };

  localStorage.setItem('device-benchmark', JSON.stringify(result));
  return result;
}

export function getComplexity(score: number): 'full' | 'reduced' | 'minimal' {
  if (score >= 60) return 'full';
  if (score >= 30) return 'reduced';
  return 'minimal';
}

export function getAnimationConfig(complexity: 'full' | 'reduced' | 'minimal') {
  return {
    full: {
      duration: 1.5,
      stagger: 0.1,
      parallax: true,
      floating: true,
      breathing: true,
    },
    reduced: {
      duration: 0.8,
      stagger: 0.05,
      parallax: false,
      floating: false,
      breathing: true,
    },
    minimal: {
      duration: 0.3,
      stagger: 0,
      parallax: false,
      floating: false,
      breathing: false,
    },
  }[complexity];
}
```

## Environment Variables

```typescript
// .env.local (example)
NEXT_PUBLIC_LINKEDIN_URL=https://linkedin.com/in/username
NEXT_PUBLIC_GITHUB_URL=https://github.com/username
NEXT_PUBLIC_DEMO_VIDEO_URL=/videos/demo.mp4

// Usage in components
const linkedinUrl = process.env.NEXT_PUBLIC_LINKEDIN_URL;
const githubUrl = process.env.NEXT_PUBLIC_GITHUB_URL;
const demoVideoUrl = process.env.NEXT_PUBLIC_DEMO_VIDEO_URL;
```

## Component Relationships

```
PageWrapper (Context Provider)
  ├─ Provides: PerformanceState, SessionTimeoutState
  ├─ Consumes: Better Auth session
  └─ Children: All pages

GlassCard (Primitive)
  ├─ Provides: Glassmorphic styling
  ├─ Consumes: PerformanceState (for animations)
  └─ Used by: TaskList, TaskForm, TagSidebar, Auth forms

FloatingElement (Wrapper)
  ├─ Provides: Floating animation
  ├─ Consumes: PerformanceState (for animation complexity)
  └─ Used by: Task cards, hero icons

ScrollReveal (Wrapper)
  ├─ Provides: Scroll-triggered reveal
  ├─ Consumes: useInView from Framer Motion
  └─ Used by: Hero, Demo, Task sections
```

## State Management Strategy

**No global state management library required**. All state is:

1. **Local component state** (useState) for UI interactions
2. **Context** (React Context) for shared state (performance, session)
3. **Server state** (Better Auth) for authentication
4. **URL state** (Next.js router) for navigation

This keeps the architecture simple and avoids unnecessary complexity.

## Data Persistence

1. **Session data**: httpOnly cookies (managed by Better Auth)
2. **Performance benchmark**: localStorage (cached for 7 days)
3. **User preferences**: localStorage (animation toggle)
4. **Todo data**: PostgreSQL (existing, unchanged)

## Type Safety

All components use TypeScript with strict mode enabled:

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true
  }
}
```

## Testing Considerations

### Unit Tests
- Component rendering with different props
- Animation state transitions
- Performance utility calculations
- Session timeout logic

### Integration Tests
- Logout flow end-to-end
- Session timeout modal interaction
- Entry animation skip functionality
- Conditional rendering based on auth state

### Visual Tests
- Glassmorphic styling consistency
- Animation smoothness
- Responsive design
- Browser compatibility

---

**Data Model Status**: ✅ COMPLETE
**Next Step**: Create component interface contracts
