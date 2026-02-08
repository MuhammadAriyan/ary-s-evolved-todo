# Bundle Size Optimization

## Techniques

### 1. Dynamic Imports

Use Next.js `dynamic()` for code splitting large components:

```typescript
import dynamic from 'next/dynamic'
import { Skeleton } from '@/components/ui/skeleton'

// Dynamic import with loading state
const SearchBar = dynamic(() => import('@/components/search/SearchBar'), {
  ssr: false,
  loading: () => <Skeleton className="h-10 w-full bg-white/10" />,
})
```

**When to use:**
- Components >50 KB
- Components used on specific routes only
- Heavy third-party libraries (charts, editors)
- Components below the fold

### 2. Optimize Package Imports

Configure `next.config.js` for better tree-shaking:

```javascript
experimental: {
  optimizePackageImports: [
    'framer-motion',
    '@tanstack/react-query',
    'recharts',
    'lucide-react'
  ],
}
```

### 3. Modularize Imports

Use specific imports instead of barrel exports:

```typescript
// ❌ Bad - imports entire library
import { debounce } from 'lodash'

// ✅ Good - imports only what's needed
import debounce from 'lodash/debounce'

// ✅ Better - custom implementation
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}
```

### 4. Self-Hosted Fonts

Replace Google Fonts CDN with self-hosted fonts:

```typescript
import localFont from "next/font/local"

const inter = localFont({
  src: [
    { path: '../public/fonts/inter-400.ttf', weight: '400' },
    { path: '../public/fonts/inter-700.ttf', weight: '700' },
  ],
  display: 'swap',
  variable: '--font-inter',
})
```

**Benefits:**
- No external network requests
- Faster FCP (200-400ms improvement)
- Full control over loading strategy
- Better privacy

### 5. Remove Unused Code

Identify and remove dead code:

```bash
# Find unused exports
npx ts-prune

# Analyze bundle
ANALYZE=true npm run build
```

**Common sources:**
- Unused component variants
- Duplicate utilities
- Commented-out code
- Unused dependencies

### 6. Production Optimizations

Configure `next.config.js`:

```javascript
compiler: {
  removeConsole: process.env.NODE_ENV === 'production',
},

// Enable compression
compress: true,

// Optimize images
images: {
  formats: ['image/avif', 'image/webp'],
},
```

## Measurement

### Before Optimization

```bash
npm run build
```

Document baseline:
- Total bundle size
- Largest page size
- Shared JS size
- Number of chunks

### After Optimization

```bash
ANALYZE=true npm run build
```

Compare:
- Bundle size reduction (target: 20%+)
- Chunk count reduction
- Lazy-loaded components
- Network waterfall improvements

## Best Practices

1. **Measure First** - Always establish baseline before optimizing
2. **Incremental Changes** - Optimize one thing at a time
3. **Verify Impact** - Check bundle analyzer after each change
4. **Test Functionality** - Ensure dynamic imports don't break features
5. **Monitor Production** - Track bundle size in CI/CD

## Common Pitfalls

- Over-splitting (too many small chunks)
- Breaking SSR with client-only imports
- Forgetting loading states for dynamic imports
- Not testing on slow networks
- Ignoring mobile bundle sizes

## Tools

- `@next/bundle-analyzer` - Visualize bundle composition
- `webpack-bundle-analyzer` - Detailed bundle analysis
- Chrome DevTools Network tab - Measure actual load times
- Lighthouse - Overall performance impact
