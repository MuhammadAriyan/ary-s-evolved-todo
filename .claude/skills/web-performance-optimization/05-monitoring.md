# Performance Monitoring Setup

## Core Web Vitals Monitoring

### Implementation

Create a WebVitals component:

```typescript
'use client'

import { useReportWebVitals } from 'next/web-vitals'
import { devLog } from '@/lib/utils'

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Log in development
    devLog('Web Vitals:', {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
      id: metric.id,
    })

    // Send to analytics in production
    if (process.env.NODE_ENV === 'production' && process.env.NEXT_PUBLIC_ANALYTICS_ID) {
      // Google Analytics example
      window.gtag?.('event', metric.name, {
        value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
        event_label: metric.id,
        non_interaction: true,
      })
    }
  })

  return null
}
```

Add to root layout:

```typescript
import { WebVitals } from '@/components/analytics/WebVitals'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <WebVitals />
        {children}
      </body>
    </html>
  )
}
```

## Metrics to Track

### Core Web Vitals

1. **Largest Contentful Paint (LCP)**
   - Target: <2.5s
   - Measures: Loading performance
   - Tracks: When main content becomes visible

2. **First Input Delay (FID)**
   - Target: <100ms
   - Measures: Interactivity
   - Tracks: Time from first interaction to browser response

3. **Cumulative Layout Shift (CLS)**
   - Target: <0.1
   - Measures: Visual stability
   - Tracks: Unexpected layout shifts

### Additional Metrics

4. **First Contentful Paint (FCP)**
   - Target: <1.8s
   - Measures: Initial render
   - Tracks: When first content appears

5. **Time to Interactive (TTI)**
   - Target: <1s
   - Measures: Full interactivity
   - Tracks: When page becomes fully interactive

6. **Total Blocking Time (TBT)**
   - Target: <200ms
   - Measures: Main thread blocking
   - Tracks: Time main thread is blocked

## Analytics Integration

### Google Analytics 4

```typescript
// Add to layout
<Script
  src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
  strategy="afterInteractive"
/>
<Script id="google-analytics" strategy="afterInteractive">
  {`
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', '${GA_ID}');
  `}
</Script>
```

### Custom Analytics

```typescript
// lib/analytics.ts
export const trackEvent = (name: string, properties?: Record<string, any>) => {
  if (process.env.NODE_ENV === 'production') {
    // Send to your analytics service
    fetch('/api/analytics', {
      method: 'POST',
      body: JSON.stringify({ name, properties }),
    })
  }
}

// Usage
trackEvent('task_created', { priority: 'high' })
```

## Error Monitoring

### Error Boundary

```typescript
'use client'

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: any) {
    // Log to error tracking service
    console.error('Error caught by boundary:', error, errorInfo)

    if (process.env.NODE_ENV === 'production') {
      // Send to error tracking service (Sentry, etc.)
    }
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-4 text-center">
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
```

## Performance Budgets

Set performance budgets in CI/CD:

```javascript
// lighthouse-budget.json
{
  "resourceSizes": [
    {
      "resourceType": "script",
      "budget": 300
    },
    {
      "resourceType": "total",
      "budget": 500
    }
  ],
  "resourceCounts": [
    {
      "resourceType": "third-party",
      "budget": 10
    }
  ]
}
```

Run in CI:

```bash
lighthouse https://yourapp.com --budget-path=lighthouse-budget.json
```

## Monitoring Dashboard

### Key Metrics to Display

1. **Performance**
   - Average page load time
   - Core Web Vitals (LCP, FID, CLS)
   - Bundle size trends
   - API response times

2. **Errors**
   - Error rate
   - Error types
   - Affected users
   - Stack traces

3. **Usage**
   - Active users
   - Page views
   - Feature usage
   - User flows

4. **Business**
   - Conversion rates
   - Task completion rates
   - User engagement
   - Retention metrics

## Continuous Monitoring

### Automated Checks

```yaml
# .github/workflows/performance.yml
name: Performance Check

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://staging.yourapp.com
          budgetPath: ./lighthouse-budget.json
          uploadArtifacts: true
```

### Alerts

Set up alerts for:
- Performance degradation (>10% slower)
- Error rate spikes (>1%)
- Bundle size increases (>5%)
- Core Web Vitals failures

## Tools

### Development
- Chrome DevTools Performance tab
- React DevTools Profiler
- Lighthouse CI
- webpack-bundle-analyzer

### Production
- Google Analytics 4
- Vercel Analytics
- Sentry (error tracking)
- LogRocket (session replay)
- DataDog (infrastructure monitoring)

### Testing
- Lighthouse
- WebPageTest
- GTmetrix
- Pingdom

## Best Practices

1. **Monitor Real Users** - Track actual user experience, not just synthetic tests
2. **Set Baselines** - Establish performance baselines before optimization
3. **Track Trends** - Monitor metrics over time, not just point-in-time
4. **Alert on Regressions** - Get notified when performance degrades
5. **Correlate with Business** - Connect performance to business metrics
6. **Test on Real Devices** - Use actual devices, not just emulators
7. **Monitor Globally** - Track performance across different regions
8. **Review Regularly** - Weekly performance review meetings

## Monitoring Checklist

- [ ] Core Web Vitals tracking implemented
- [ ] Error boundary configured
- [ ] Analytics integration complete
- [ ] Performance budgets set
- [ ] CI/CD performance checks enabled
- [ ] Alerts configured for regressions
- [ ] Dashboard created for key metrics
- [ ] Real user monitoring (RUM) enabled
- [ ] Error tracking service integrated
- [ ] Regular performance reviews scheduled
