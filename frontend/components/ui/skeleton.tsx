import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  )
}

function TaskSkeleton() {
  return (
    <div className="p-4 bg-white rounded-lg shadow-sm border border-gray-200 space-y-3">
      <div className="flex items-start gap-3">
        <Skeleton className="h-5 w-5 rounded" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
      </div>
      <div className="flex gap-2">
        <Skeleton className="h-6 w-16 rounded-full" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
    </div>
  );
}

function TaskListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4" aria-label="Loading tasks...">
      {[...Array(count)].map((_, i) => (
        <TaskSkeleton key={i} />
      ))}
    </div>
  );
}

function TaskDetailSkeleton() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="space-y-4">
        <Skeleton className="h-8 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-8 w-full" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-8 w-full" />
        </div>
      </div>

      <div className="space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-32 w-full" />
      </div>

      <div className="flex gap-2">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  );
}

function SearchResultsSkeleton({ count = 10 }: { count?: number }) {
  return (
    <div className="space-y-3" aria-label="Loading search results...">
      {[...Array(count)].map((_, i) => (
        <div key={i} className="p-4 bg-white rounded-lg border border-gray-200 space-y-2">
          <Skeleton className="h-5 w-2/3" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
          <div className="flex gap-2 mt-2">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-20 rounded-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

function NotificationSkeleton() {
  return (
    <div className="p-3 bg-white rounded-lg shadow-sm border border-gray-200 space-y-2">
      <div className="flex items-start gap-3">
        <Skeleton className="h-8 w-8 rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
    </div>
  );
}

function NotificationListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-2" aria-label="Loading notifications...">
      {[...Array(count)].map((_, i) => (
        <NotificationSkeleton key={i} />
      ))}
    </div>
  );
}

function AuditLogSkeleton() {
  return (
    <div className="p-4 bg-white rounded-lg border-l-4 border-gray-300 space-y-2">
      <div className="flex items-center gap-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-32" />
      </div>
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-3 w-40" />
    </div>
  );
}

function AuditLogListSkeleton({ count = 10 }: { count?: number }) {
  return (
    <div className="space-y-3" aria-label="Loading audit logs...">
      {[...Array(count)].map((_, i) => (
        <AuditLogSkeleton key={i} />
      ))}
    </div>
  );
}

function CardSkeleton() {
  return (
    <div className="p-6 bg-white rounded-lg shadow-sm border border-gray-200 space-y-4">
      <Skeleton className="h-6 w-1/3" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-5/6" />
      <Skeleton className="h-4 w-4/6" />
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <CardSkeleton />
        <CardSkeleton />
        <CardSkeleton />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-4">
          <Skeleton className="h-6 w-32" />
          <TaskListSkeleton count={3} />
        </div>
        <div className="space-y-4">
          <Skeleton className="h-6 w-32" />
          <TaskListSkeleton count={3} />
        </div>
      </div>
    </div>
  );
}

export {
  Skeleton,
  TaskSkeleton,
  TaskListSkeleton,
  TaskDetailSkeleton,
  SearchResultsSkeleton,
  NotificationSkeleton,
  NotificationListSkeleton,
  AuditLogSkeleton,
  AuditLogListSkeleton,
  CardSkeleton,
  DashboardSkeleton
}
