'use client'

import { ChatContainer } from './components/ChatContainer'
import { ChatErrorBoundary } from './components/ChatErrorBoundary'

export default function ChatPage() {
  return (
    <ChatErrorBoundary>
      <ChatContainer className="h-full" />
    </ChatErrorBoundary>
  )
}
