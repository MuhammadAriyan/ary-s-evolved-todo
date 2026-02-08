/**
 * TaskMetadata component for consistent task metadata display
 * T071: Reusable component with Sky-Aura Glass aesthetic
 */

import { Task } from '@/types/task'
import { Badge } from '@/components/ui/badge'
import { Calendar, Tag, Repeat } from 'lucide-react'
import { cn } from '@/lib/utils'

interface TaskMetadataProps {
  task: Task
  showTags?: boolean
  showDueDate?: boolean
  showPriority?: boolean
  compact?: boolean
  className?: string
}

export function TaskMetadata({
  task,
  showTags = true,
  showDueDate = true,
  showPriority = true,
  compact = false,
  className,
}: TaskMetadataProps) {
  return (
    <div className={cn('flex flex-wrap items-center gap-2', className)}>
      {showPriority && (
        <Badge
          variant={
            task.priority === 'High'
              ? 'destructive'
              : task.priority === 'Medium'
              ? 'default'
              : 'secondary'
          }
          className={compact ? 'text-xs' : ''}
        >
          {task.priority}
        </Badge>
      )}

      {showDueDate && task.due_date && (
        <Badge
          variant="outline"
          className={cn(
            'gap-1 border-white/20 text-text-tertiary',
            compact ? 'text-xs' : ''
          )}
        >
          <Calendar className={compact ? 'h-2.5 w-2.5' : 'h-3 w-3'} />
          {new Date(task.due_date).toLocaleDateString()}
        </Badge>
      )}

      {showTags &&
        task.tags.map((tag) => (
          <Badge
            key={tag}
            variant="outline"
            className={cn(
              'gap-1 border-white/20 text-text-tertiary',
              compact ? 'text-xs' : ''
            )}
          >
            <Tag className={compact ? 'h-2.5 w-2.5' : 'h-3 w-3'} />
            {tag}
          </Badge>
        ))}

      {task.recurring && (
        <Badge
          variant="outline"
          className={cn(
            'gap-1 border-white/20 text-text-tertiary',
            compact ? 'text-xs' : ''
          )}
        >
          <Repeat className={compact ? 'h-2.5 w-2.5' : 'h-3 w-3'} />
          {task.recurring}
        </Badge>
      )}
    </div>
  )
}
