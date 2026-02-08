import type { Metadata } from 'next'
import localFont from "next/font/local"
import "./globals.css"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { QueryProvider } from "@/components/providers/QueryProvider"
import { WebVitals } from "@/components/analytics/WebVitals"

// Self-hosted fonts with next/font/local for optimal performance
const inter = localFont({
  src: [
    {
      path: '../public/fonts/inter-400.ttf',
      weight: '400',
      style: 'normal',
    },
    {
      path: '../public/fonts/inter-500.ttf',
      weight: '500',
      style: 'normal',
    },
    {
      path: '../public/fonts/inter-600.ttf',
      weight: '600',
      style: 'normal',
    },
    {
      path: '../public/fonts/inter-700.ttf',
      weight: '700',
      style: 'normal',
    },
  ],
  display: 'swap',
  variable: '--font-inter',
})

const chelseaMarket = localFont({
  src: '../public/fonts/chelsea-market.ttf',
  weight: '400',
  display: 'swap',
  variable: '--font-chelsea',
})

// SEO Metadata (T043-T046)
export const metadata: Metadata = {
  title: {
    template: '%s | Ary\'s Evolved Todo',
    default: 'Ary\'s Evolved Todo - AI-Powered Task Management',
  },
  description: 'Intelligent task management with AI chat assistant. Organize, prioritize, and complete your tasks with natural language commands and smart automation.',
  keywords: ['todo', 'task management', 'AI assistant', 'productivity', 'chat interface', 'task automation', 'smart todo'],
  authors: [{ name: 'Ary' }],
  creator: 'Ary',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://ary-evolved-todo.vercel.app',
    title: 'Ary\'s Evolved Todo - AI-Powered Task Management',
    description: 'Intelligent task management with AI chat assistant. Organize, prioritize, and complete your tasks with natural language commands.',
    siteName: 'Ary\'s Evolved Todo',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Ary\'s Evolved Todo',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Ary\'s Evolved Todo - AI-Powered Task Management',
    description: 'Intelligent task management with AI chat assistant. Organize, prioritize, and complete your tasks with natural language commands.',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${inter.variable} ${chelseaMarket.variable}`}>
      <head>
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
      </head>
      <body className={`${inter.className} antialiased`}>
        <WebVitals />
        <QueryProvider>
          <PageWrapper>{children}</PageWrapper>
        </QueryProvider>
      </body>
    </html>
  )
}
