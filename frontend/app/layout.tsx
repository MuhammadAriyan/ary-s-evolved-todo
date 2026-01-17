'use client'

import { Inter } from "next/font/google"
import "./globals.css"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Analytics } from '@vercel/analytics/react'
import { useState } from 'react'

// Optimize font loading with next/font
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Create QueryClient instance with session caching configuration
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 5 * 60 * 1000, // 5 minutes - data stays fresh
        gcTime: 10 * 60 * 1000, // 10 minutes - cache garbage collection
        refetchOnWindowFocus: false, // Don't refetch on window focus
        retry: 1, // Retry failed queries once
      },
    },
  }))

  return (
    <html lang="en" className={inter.variable}>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Ary's Evolved Todo</title>
        <meta name="description" content="AI-powered todo application with chat interface" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Chelsea+Market&display=swap" rel="stylesheet" />
      </head>
      <body className={`${inter.className} antialiased`}>
        <QueryClientProvider client={queryClient}>
          <PageWrapper>{children}</PageWrapper>
          <Analytics />
        </QueryClientProvider>
      </body>
    </html>
  )
}
