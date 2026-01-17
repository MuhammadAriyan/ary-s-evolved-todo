'use client'

import { useRef, useEffect, useState } from 'react'
import { AgentMessage } from './AgentMessage'
import { MessageThreadSkeleton } from './SkeletonLoaders'
import type { Message } from '@/types/chat'
import type { StreamingState } from '@/hooks/useChat'
import { cn } from '@/lib/utils'

interface MessageThreadProps {
  messages: Message[]
  isLoading?: boolean
  isInitialLoad?: boolean
  streaming?: StreamingState
  className?: string
}

export function MessageThread({ messages, isLoading, isInitialLoad, streaming, className }: MessageThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [userScrolledUp, setUserScrolledUp] = useState(false)
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const rafRef = useRef<number | null>(null)

  // Debounced scroll handler (150ms debounce, detect user scroll up)
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleScroll = () => {
      // Clear existing timeout
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current)
      }

      // Debounce scroll detection by 150ms
      scrollTimeoutRef.current = setTimeout(() => {
        const { scrollTop, scrollHeight, clientHeight } = container
        // User is "scrolled up" if they're more than 100px from bottom
        const isNearBottom = scrollHeight - scrollTop - clientHeight < 100
        setUserScrolledUp(!isNearBottom)
      }, 150)
    }

    // Add scroll listener with passive: true for performance
    container.addEventListener('scroll', handleScroll, { passive: true })

    return () => {
      container.removeEventListener('scroll', handleScroll)
      // Cleanup scroll timeout
      if (scrollTimeoutRef.current) {
        clearTimeout(scrollTimeoutRef.current)
      }
    }
  }, [])

  // RequestAnimationFrame-based smooth scroll to bottom
  const smoothScrollToBottom = () => {
    const container = containerRef.current
    const bottom = bottomRef.current
    if (!container || !bottom) return

    // Cancel any existing RAF
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current)
    }

    const targetScrollTop = container.scrollHeight - container.clientHeight
    const startScrollTop = container.scrollTop
    const distance = targetScrollTop - startScrollTop
    const duration = 300 // ms
    const startTime = performance.now()

    const animateScroll = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // Ease-out cubic function for smooth deceleration
      const easeOutCubic = 1 - Math.pow(1 - progress, 3)

      container.scrollTop = startScrollTop + distance * easeOutCubic

      if (progress < 1) {
        rafRef.current = requestAnimationFrame(animateScroll)
      } else {
        rafRef.current = null
      }
    }

    rafRef.current = requestAnimationFrame(animateScroll)
  }

  // Auto-scroll to bottom when new messages arrive or streaming content updates
  // But only if user hasn't scrolled up
  useEffect(() => {
    if (!userScrolledUp) {
      smoothScrollToBottom()
    }
  }, [messages, streaming?.content, userScrolledUp])

  // Cleanup RAF on unmount
  useEffect(() => {
    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
      }
    }
  }, [])

  // Show skeleton during initial load
  if (isInitialLoad) {
    return <MessageThreadSkeleton className={className} />
  }

  if (messages.length === 0 && !isLoading && !streaming?.isStreaming) {
    return (
      <div className={cn('flex-1 flex items-center justify-center', className)}>
        <div className="text-center text-white/50 max-w-md px-4">
          <div className="text-4xl mb-4">🤖</div>
          <h3 className="text-lg font-medium text-white/70 mb-2 font-chelsea">
            Hello! I'm Aren, your AI task assistant.
          </h3>
          <p className="text-sm font-chelsea">
            I can help you manage your tasks through conversation. Try saying:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-white/60 font-chelsea">
            <li>"Add task buy groceries"</li>
            <li>"Show my pending tasks"</li>
            <li>"Complete task 1"</li>
            <li>"Show my stats"</li>
          </ul>
        </div>
      </div>
    )
  }

  return (
    <div ref={containerRef} className={cn('flex-1 overflow-y-auto p-4 space-y-4', className)}>
      {messages.map((message) => (
        <AgentMessage key={message.id} message={message} />
      ))}

      {/* Streaming message */}
      {streaming?.isStreaming && (
        <div className="flex gap-3 p-4 rounded-xl bg-white/5 border border-white/10 mr-8">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-lg">
            {streaming.agentIcon}
          </div>
          <div className="flex-1 min-w-0">
            {streaming.agentName && (
              <div className="text-xs text-white/50 mb-1 font-medium font-chelsea">
                {streaming.agentName}
              </div>
            )}
            <div className="text-white/90 prose prose-invert prose-sm max-w-none font-chelsea">
              {streaming.content || (
                <span className="text-white/50">Thinking...</span>
              )}
              {/* Typing cursor */}
              <span className="inline-block w-2 h-4 bg-white/70 ml-0.5 animate-pulse" />
            </div>
            {/* Tool calls indicator */}
            {streaming.toolCalls.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {streaming.toolCalls.map((tool, idx) => (
                  <span
                    key={idx}
                    className="text-xs px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-300 border border-sky-500/30"
                  >
                    {tool}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Loading indicator (non-streaming fallback) */}
      {isLoading && !streaming?.isStreaming && (
        <div className="flex gap-3 p-4 rounded-xl bg-white/5 border border-white/10 mr-8">
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-white/30 border-t-white/70 rounded-full animate-spin" />
          </div>
          <div className="flex items-center">
            <span className="text-white/50 text-sm font-chelsea">Thinking...</span>
          </div>
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={bottomRef} />
    </div>
  )
}
