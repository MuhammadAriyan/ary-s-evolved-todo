/**
 * WebVitals component for monitoring Core Web Vitals
 * T073: Reports performance metrics in development mode
 */

'use client'

import { useReportWebVitals } from 'next/web-vitals'
import { devLog } from '@/lib/utils'

export function WebVitals() {
  useReportWebVitals((metric) => {
    // Only log in development mode
    devLog('Web Vitals:', {
      name: metric.name,
      value: metric.value,
      rating: metric.rating,
      delta: metric.delta,
      id: metric.id,
    })

    // Send to analytics in production (if configured)
    if (process.env.NODE_ENV === 'production' && process.env.NEXT_PUBLIC_ANALYTICS_ID) {
      // Example: Send to Google Analytics
      // window.gtag?.('event', metric.name, {
      //   value: Math.round(metric.name === 'CLS' ? metric.value * 1000 : metric.value),
      //   event_label: metric.id,
      //   non_interaction: true,
      // })
    }
  })

  return null
}
