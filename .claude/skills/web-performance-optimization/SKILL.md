---
name: web-performance-optimization
description: Comprehensive guide for optimizing Next.js web applications for production performance, accessibility, and SEO
---

# Web Performance Optimization Skill

This skill provides battle-tested techniques for optimizing Next.js applications for production deployment, covering performance, accessibility, SEO, and bundle size optimization.

## When to Use This Skill

Use this skill when:
- Preparing a Next.js application for production deployment
- Optimizing page load times and runtime performance
- Implementing WCAG accessibility standards
- Setting up comprehensive SEO
- Reducing bundle size
- Eliminating debug logging in production
- Implementing Core Web Vitals monitoring

## Skill Structure

1. **00-overview.md** - Performance optimization overview and methodology
2. **01-bundle-optimization.md** - Bundle size reduction techniques
3. **02-runtime-performance.md** - Runtime optimization patterns
4. **03-seo-setup.md** - SEO configuration guide
5. **04-accessibility.md** - WCAG compliance checklist
6. **05-monitoring.md** - Performance monitoring setup

## Quick Reference

### Critical Optimizations (Do These First)

1. **Self-hosted fonts** - Eliminate external font requests
2. **Development-only logging** - Zero console.log in production
3. **Event-driven session checking** - Reduce polling overhead
4. **WCAG AA text colors** - Ensure accessibility compliance
5. **Dynamic imports** - Code-split large components

### Performance Targets

- Page load: <1 second
- First Contentful Paint (FCP): <1.8s
- Largest Contentful Paint (LCP): <2.5s
- Time to Interactive (TTI): <1s
- Cumulative Layout Shift (CLS): <0.1
- First Input Delay (FID): <100ms

### Bundle Size Targets

- 20%+ reduction from baseline
- Shared JS: <150 kB
- Page-specific JS: <50 kB per route

### Accessibility Targets

- WCAG 2.1 Level AA compliance
- Zero axe DevTools violations
- Lighthouse accessibility score: 100
- Text contrast: 4.5:1 (normal), 3:1 (large)

### SEO Targets

- Lighthouse SEO score: >90
- Valid sitemap.xml
- Proper robots.txt
- Open Graph metadata
- Twitter Card metadata
- JSON-LD structured data

## Implementation Phases

### Phase 1: Setup
Establish baseline metrics and prepare optimization environment

### Phase 2: Foundational
Core infrastructure changes that enable all optimizations

### Phase 3-9: User Stories
Independent, testable optimizations for specific user-facing improvements

### Phase 10: Polish
Final validation, documentation, and monitoring setup

## Success Criteria

- ✅ Zero console.log in production
- ✅ WCAG AA compliance
- ✅ Self-hosted fonts (no external requests)
- ✅ Event-driven session checking
- ✅ Comprehensive SEO metadata
- ⏳ Page load <1 second (requires server testing)
- ⏳ Lighthouse score >90 (requires server testing)
- ⏳ 20%+ bundle size reduction (requires aggressive optimization)

## Related Skills

- `nextjs-best-practices` - Next.js-specific patterns
- `accessibility` - WCAG compliance details
- `seo` - SEO optimization strategies
- `web-performance-optimization` - This skill

## References

- [Next.js Performance Documentation](https://nextjs.org/docs/app/building-your-application/optimizing)
- [Web Vitals](https://web.dev/vitals/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Lighthouse Documentation](https://developer.chrome.com/docs/lighthouse/)
