'use client'

import { Suspense } from 'react'
import { ChatContainer } from './components/ChatContainer'
import { ChatErrorBoundary } from './components/ChatErrorBoundary'
import { ChatSkeleton } from './components/SkeletonLoaders'

export default function ChatPage() {
  return (
    <ChatErrorBoundary>
      <Suspense fallback={<ChatSkeleton />}>
        <ChatContainer className="h-full" />
      </Suspense>
    </ChatErrorBoundary>
  )
}
