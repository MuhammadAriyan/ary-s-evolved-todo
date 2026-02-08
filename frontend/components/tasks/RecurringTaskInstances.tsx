/**
 * RecurringTaskInstances Component
 * Displays instances of a recurring task
 */

"use client"

import { useQuery } from "@tanstack/react-query"
import { Task } from "@/types/task"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { CheckCircle2, Circle, Calendar } from "lucide-react"
import { format } from "date-fns"

interface RecurringTaskInstancesProps {
  parentTaskId: number
}

export function RecurringTaskInstances({ parentTaskId }: RecurringTaskInstancesProps) {
  const { data: instances, isLoading } = useQuery<Task[]>({
    queryKey: ['task-instances', parentTaskId],
    queryFn: async () => {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/tasks?parent_task_id=${parentTaskId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        }
      )
      if (!response.ok) throw new Error('Failed to fetch instances')
      return response.json()
    },
  })

  if (isLoading) {
    return (
      <div className="p-4 text-sm text-white/60">
        Loading instances...
      </div>
    )
  }

  if (!instances || instances.length === 0) {
    return (
      <div className="p-4 text-sm text-white/60">
        No instances generated yet. Instances will be created automatically based on the recurring pattern.
      </div>
    )
  }

  return (
    <div className="space-y-2 p-4 bg-white/5 rounded-lg border border-white/10">
      <div className="flex items-center gap-2 text-sm font-medium text-white/80 mb-3">
        <Calendar className="h-4 w-4" />
        <span>Recurring Instances ({instances.length})</span>
      </div>

      <div className="space-y-2">
        {instances.map((instance) => (
          <div
            key={instance.id}
            className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors"
          >
            <div className="flex items-center gap-3 flex-1">
              {instance.completed ? (
                <CheckCircle2 className="h-5 w-5 text-green-400" />
              ) : (
                <Circle className="h-5 w-5 text-white/40" />
              )}

              <div className="flex-1">
                <div className="text-sm text-white">{instance.title}</div>
                {instance.due_date && (
                  <div className="text-xs text-white/50 mt-1">
                    Due: {format(new Date(instance.due_date), 'MMM d, yyyy')}
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Badge
                variant={instance.completed ? "default" : "secondary"}
                className="text-xs"
              >
                {instance.completed ? "Completed" : "Pending"}
              </Badge>

              {instance.recurrence_count !== undefined && (
                <Badge variant="outline" className="text-xs">
                  #{instance.recurrence_count}
                </Badge>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
