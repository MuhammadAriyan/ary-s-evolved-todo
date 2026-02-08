# Runtime Performance Optimization

## Event-Driven Patterns

### Session Checking

Replace polling with event-driven validation:

```typescript
// ❌ Bad - Polls every 3 seconds (20 checks/minute)
useEffect(() => {
  const interval = setInterval(() => {
    checkSession()
  }, 3000)
  return () => clearInterval(interval)
}, [])

// ✅ Good - Event-driven with 60s fallback (1 check/minute when idle)
useEffect(() => {
  let lastCheckTime = Date.now()

  const checkSession = () => {
    const now = Date.now()
    if (now - lastCheckTime < 5000) return // Debounce
    lastCheckTime = now
    // Perform session check
  }

  // Check on visibility change
  const handleVisibilityChange = () => {
    if (document.visibilityState === 'visible') {
      checkSession()
    }
  }

  // Check on user activity
  const handleUserActivity = () => {
    checkSession()
  }

  // 60-second fallback
  const fallbackInterval = setInterval(checkSession, 60000)

  document.addEventListener('visibilitychange', handleVisibilityChange)
  document.addEventListener('click', handleUserActivity, { passive: true })

  return () => {
    clearInterval(fallbackInterval)
    document.removeEventListener('visibilitychange', handleVisibilityChange)
    document.removeEventListener('click', handleUserActivity)
  }
}, [])
```

**Impact:** 95% reduction in session checks

### Development-Only Logging

Create utility for production-safe logging:

```typescript
// lib/utils.ts
export const devLog = (...args: any[]) => {
  if (process.env.NODE_ENV === 'development') {
    console.log(...args)
  }
}

// Usage
devLog('User activity detected:', event)
```

**Benefits:**
- Zero console.log in production builds
- No manual cleanup needed
- Consistent logging pattern

## React Optimization

### Prevent Unnecessary Re-renders

```typescript
// Use useMemo for expensive computations
const filteredTasks = useMemo(() => {
  if (!searchQuery.trim()) return tasks
  return tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase())
  )
}, [tasks, searchQuery])

// Use useCallback for event handlers
const handleClick = useCallback(() => {
  // Handler logic
}, [dependencies])
```

### Optimize Context Usage

```typescript
// Split contexts to prevent unnecessary re-renders
const QueryProvider = ({ children }) => {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000,
        gcTime: 10 * 60 * 1000,
        refetchOnWindowFocus: false,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}
```

## Network Optimization

### Optimize Font Loading

```typescript
// Use font-display: swap for faster FCP
const inter = localFont({
  src: '../public/fonts/inter-400.ttf',
  display: 'swap', // Show fallback immediately
  variable: '--font-inter',
})
```

### Lazy Load Images

```typescript
import Image from 'next/image'

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={630}
  loading="lazy"
  placeholder="blur"
/>
```

## Performance Monitoring

### Core Web Vitals

```typescript
'use client'

import { useReportWebVitals } from 'next/web-vitals'

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Log in development
    if (process.env.NODE_ENV === 'development') {
      console.log(metric.name, metric.value)
    }

    // Send to analytics in production
    if (process.env.NODE_ENV === 'production') {
      // Send to your analytics service
    }
  })

  return null
}
```

## Best Practices

1. **Event-Driven Over Polling** - Use events instead of intervals
2. **Debounce User Input** - Prevent excessive API calls
3. **Memoize Expensive Computations** - Use useMemo/useCallback
4. **Lazy Load Non-Critical Resources** - Images, fonts, components
5. **Monitor Real User Metrics** - Track Core Web Vitals

## Performance Targets

- **Time to Interactive (TTI):** <1 second
- **First Input Delay (FID):** <100ms
- **Session checks:** <2 per minute when idle
- **Re-renders:** Minimize with proper memoization
- **Network requests:** Batch and debounce

## Tools

- Chrome DevTools Performance tab
- React DevTools Profiler
- Lighthouse Performance audit
- Web Vitals extension
