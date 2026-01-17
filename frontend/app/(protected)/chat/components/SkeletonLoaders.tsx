'use client'

import { cn } from '@/lib/utils'

interface SkeletonProps {
  className?: string
}

/** Base skeleton pulse animation */
function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-lg bg-white/10',
        className
      )}
    />
  )
}

/** Skeleton for a single conversation item */
function ConversationItemSkeleton() {
  return (
    <div className="flex items-center gap-2 p-3 rounded-lg">
      <Skeleton className="w-4 h-4 rounded" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
      </div>
    </div>
  )
}

/** Skeleton for the conversation list sidebar */
export function ConversationListSkeleton({ className }: SkeletonProps) {
  return (
    <div className={cn('space-y-1 p-2', className)}>
      {Array.from({ length: 5 }).map((_, i) => (
        <ConversationItemSkeleton key={i} />
      ))}
    </div>
  )
}

/** Skeleton for a single message */
function MessageSkeleton({ isUser = false }: { isUser?: boolean }) {
  return (
    <div
      className={cn(
        'flex gap-3 p-4 rounded-xl',
        isUser
          ? 'bg-aura-purple/10 border border-aura-purple/20 ml-8'
          : 'bg-white/5 border border-white/10 mr-8'
      )}
    >
      {!isUser && <Skeleton className="w-8 h-8 rounded-full flex-shrink-0" />}
      <div className="flex-1 space-y-2">
        {!isUser && <Skeleton className="h-3 w-16" />}
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
        {!isUser && <Skeleton className="h-4 w-1/2" />}
        <Skeleton className="h-3 w-12 mt-2" />
      </div>
      {isUser && <Skeleton className="w-8 h-8 rounded-full flex-shrink-0" />}
    </div>
  )
}

/** Skeleton for the message thread */
export function MessageThreadSkeleton({ className }: SkeletonProps) {
  return (
    <div className={cn('space-y-4 p-4', className)}>
      <MessageSkeleton isUser />
      <MessageSkeleton />
      <MessageSkeleton isUser />
      <MessageSkeleton />
    </div>
  )
}

/** Full chat skeleton combining sidebar and messages */
export function ChatSkeleton() {
  return (
    <div className="flex h-full">
      {/* Sidebar skeleton */}
      <div className="w-72 flex-shrink-0 bg-black/40 border-r border-white/10">
        <div className="p-4 border-b border-white/10">
          <Skeleton className="h-12 w-full rounded-xl" />
        </div>
        <ConversationListSkeleton />
      </div>

      {/* Main area skeleton */}
      <div className="flex-1 flex flex-col bg-black/20">
        <MessageThreadSkeleton className="flex-1" />
        <div className="p-4 bg-black/30 border-t border-white/10">
          <div className="flex gap-2">
            <Skeleton className="flex-1 h-12 rounded-xl" />
            <Skeleton className="w-12 h-12 rounded-xl" />
            <Skeleton className="w-12 h-12 rounded-xl" />
          </div>
        </div>
      </div>
    </div>
  )
}
