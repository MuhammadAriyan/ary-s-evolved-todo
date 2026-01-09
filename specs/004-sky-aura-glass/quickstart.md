# Quickstart: Sky-Aura Glass UI Transformation

**Feature**: 004-sky-aura-glass
**Date**: 2026-01-07
**Branch**: `004-sky-aura-glass`

## Overview

This guide provides setup instructions for implementing the Sky-Aura Glass UI transformation. Follow these steps to prepare your development environment and understand the implementation workflow.

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Git
- Next.js 16+ project (existing)
- Better Auth configured (existing)
- Neon PostgreSQL database (existing)

## Environment Setup

### 1. Install Dependencies

```bash
cd frontend

# Install Framer Motion
npm install framer-motion

# Install shadcn/ui components
npx shadcn@latest add dropdown-menu avatar button card

# Verify installations
npm list framer-motion
npm list lucide-react  # Should already be installed
```

### 2. Configure Environment Variables

Create or update `.env.local`:

```bash
# External Profile URLs (for NotchHeader)
NEXT_PUBLIC_LINKEDIN_URL=https://linkedin.com/in/your-username
NEXT_PUBLIC_GITHUB_URL=https://github.com/your-username

# Demo Video URL (for DemoSection)
NEXT_PUBLIC_DEMO_VIDEO_URL=/videos/demo.mp4

# Existing Better Auth variables (unchanged)
BETTER_AUTH_SECRET=your-secret
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=your-neon-postgres-url
```

### 3. Update Tailwind Configuration

Add Sky-Aura Glass utilities to `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  // ... existing config
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
  },
};

export default config;
```

### 4. Add CSS Variables

Add to `app/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
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
}

@layer utilities {
  .glass-card {
    @apply backdrop-blur-glass bg-white/30 border border-white/50 rounded-3xl shadow-bloom;
  }

  .glass-button {
    @apply backdrop-blur-glass bg-white/25 border border-white/40 rounded-2xl shadow-glass-md;
    @apply hover:scale-105 hover:brightness-110 active:scale-98;
    @apply focus:outline-none focus:ring-2 focus:ring-sky-cyan/50;
  }

  .text-glass {
    @apply text-cyan-900;
  }

  .text-glass-secondary {
    @apply text-cyan-700;
  }
}
```

## Implementation Workflow

### Phase 1: Foundation (1 session)

```bash
# Verify all dependencies installed
npm list framer-motion lucide-react

# Create performance utility
mkdir -p lib/utils
touch lib/utils/performance.ts

# Test Tailwind config
npm run dev
# Visit http://localhost:3000 and check console for errors
```

### Phase 2: Core Layout (2-3 sessions)

```bash
# Create component directories
mkdir -p components/layout
mkdir -p components/animations
mkdir -p components/hero
mkdir -p components/ui

# Create core layout components
touch components/layout/AnimatedBackground.tsx
touch components/layout/NotchHeader.tsx
touch components/layout/UserDropdown.tsx
touch components/layout/PageWrapper.tsx

# Test each component in isolation
npm run dev
```

### Phase 3: Hero & Landing (2 sessions)

```bash
# Create hero components
touch components/hero/HeroSection.tsx
touch components/hero/CloudBackground.tsx
touch components/hero/DemoSection.tsx

# Update landing page
# Edit app/page.tsx

# Test landing page
npm run dev
# Visit http://localhost:3000
```

### Phase 4: Todo Entry Animation (1-2 sessions)

```bash
# Create animation components
touch components/animations/TasksEntryAnimation.tsx
touch components/animations/FloatingElement.tsx
touch components/animations/ScrollReveal.tsx

# Update todo page
# Edit app/(protected)/todo/page.tsx

# Test entry animation
npm run dev
# Visit http://localhost:3000/todo
```

### Phase 5: Glassmorphic UI (3-4 sessions)

```bash
# Create UI primitives
touch components/ui/GlassCard.tsx
touch components/ui/GlassButton.tsx

# Update todo components
# Edit app/(protected)/todo/components/TaskList.tsx
# Edit app/(protected)/todo/components/TaskForm.tsx
# Edit app/(protected)/todo/components/TaskFilters.tsx
# Edit app/(protected)/todo/components/TagSidebar.tsx
# Edit app/(protected)/todo/components/CalendarView.tsx

# Test all todo components
npm run dev
```

### Phase 6: Auth Pages (1 session)

```bash
# Update auth pages
# Edit app/(auth)/login/page.tsx
# Edit app/(auth)/signup/page.tsx

# Test auth flows
npm run dev
# Visit http://localhost:3000/login
# Visit http://localhost:3000/signup
```

### Phase 7: Scroll & Parallax (1-2 sessions)

```bash
# Implement scroll animations
# Update components/animations/ScrollReveal.tsx
# Update components/layout/AnimatedBackground.tsx (parallax)

# Apply to all pages
# Test scrolling behavior
npm run dev
```

### Phase 8: Polish & Accessibility (2 sessions)

```bash
# Add reduced motion support
# Add ARIA labels
# Test contrast ratios
# Optimize performance

# Run accessibility audit
npm run build
npm run start
# Use Lighthouse or axe DevTools
```

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Run tests
npm test

# Run linter
npm run lint

# Type check
npm run type-check
```

## Testing Checklist

### Functionality Tests

- [ ] User can logout from NotchHeader dropdown
- [ ] Session persists across page refreshes
- [ ] Session timeout modal appears after 2 hours
- [ ] Login/signup CTAs hidden when authenticated
- [ ] All existing todo features work (CRUD, filters, tags, calendar)

### Design Tests

- [ ] Notch header displays with glassmorphic styling
- [ ] Animated gradient background on all pages
- [ ] Hero section with notched border and clouds
- [ ] Demo video autoplays muted and loops
- [ ] Todo entry animation (1.5s, skippable)
- [ ] All components use glassmorphic styling
- [ ] Nature icons used throughout
- [ ] Scroll animations and parallax work
- [ ] Floating and breathing animations work

### Performance Tests

- [ ] Animations run at 60fps
- [ ] No layout shifts or jank
- [ ] Page load time increase <20%
- [ ] CPU/GPU benchmarking works
- [ ] Reduced motion preferences respected

### Accessibility Tests

- [ ] WCAG 2.1 AA contrast ratios maintained
- [ ] Keyboard navigation works
- [ ] ARIA labels present
- [ ] Focus states visible
- [ ] Screen reader compatible

## Browser Testing

Test on minimum supported browsers:

- Chrome 76+ (backdrop-filter support)
- Safari 9+ (backdrop-filter support)
- Firefox 103+ (backdrop-filter support)
- Edge 79+ (Chromium-based)

## Performance Monitoring

```typescript
// Add to components for performance tracking
import { useEffect } from 'react';

useEffect(() => {
  const observer = new PerformanceObserver((list) => {
    for (const entry of list.getEntries()) {
      console.log(`${entry.name}: ${entry.duration}ms`);
    }
  });

  observer.observe({ entryTypes: ['measure'] });

  return () => observer.disconnect();
}, []);
```

## Troubleshooting

### Issue: Backdrop blur not working

**Solution**: Check browser support. Add fallback:

```css
@supports not (backdrop-filter: blur(12px)) {
  .glass-card {
    background: rgba(255, 255, 255, 0.85);
  }
}
```

### Issue: Animations causing jank

**Solution**: Check performance benchmark score. Reduce complexity:

```typescript
const complexity = getAnimationComplexity(benchmarkScore);
if (complexity === 'minimal') {
  // Disable floating/breathing animations
}
```

### Issue: Session timeout not triggering

**Solution**: Check activity event listeners:

```typescript
const events = ['mousedown', 'keydown', 'scroll', 'touchstart'];
events.forEach(event => window.addEventListener(event, updateActivity));
```

### Issue: Contrast ratio failing

**Solution**: Increase text color darkness or background opacity:

```css
.text-glass {
  @apply text-cyan-900; /* AAA contrast: 7.5:1 */
}
```

## Resources

### Documentation

- [Framer Motion Docs](https://www.framer.com/motion/)
- [Lucide Icons](https://lucide.dev/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)

### Design References

- [Glassmorphism Generator](https://hype4.academy/tools/glassmorphism-generator)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Can I Use: backdrop-filter](https://caniuse.com/css-backdrop-filter)

### Performance Tools

- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)

## Next Steps

After completing setup:

1. Generate implementation tasks: `/sp.tasks`
2. Begin implementation: `/sp.implement`
3. Test thoroughly against acceptance criteria
4. Deploy to staging for user acceptance testing
5. Deploy to production after approval

## Support

For questions or issues:

1. Check specification: `specs/004-sky-aura-glass/spec.md`
2. Review plan: `specs/004-sky-aura-glass/plan.md`
3. Check research: `specs/004-sky-aura-glass/research.md`
4. Review component contracts: `specs/004-sky-aura-glass/contracts/`

---

**Quickstart Status**: ✅ COMPLETE
**Ready for**: Task generation (`/sp.tasks`)
