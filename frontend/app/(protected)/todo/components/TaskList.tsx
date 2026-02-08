"use client"

import { useState } from "react"
import { Task } from "@/types/task"
import { useToggleComplete, useDeleteTask } from "@/hooks/useTasks"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Pencil, Trash2, Calendar, Tag, Repeat, ChevronDown, ChevronUp } from "lucide-react"
import { RecurringTaskInstances } from "@/components/tasks/RecurringTaskInstances"

interface TaskListProps {
  tasks: Task[]
  onEdit: (task: Task) => void
}

export function TaskList({ tasks, onEdit }: TaskListProps) {
  const toggleComplete = useToggleComplete()
  const deleteTask = useDeleteTask()
  const [expandedTaskId, setExpandedTaskId] = useState<number | null>(null)

  if (tasks.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-text-muted font-chelsea">No tasks found. Create your first task!</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <Card
          key={task.id}
          className={`p-4 transition-opacity ${task.completed ? "opacity-60" : ""}`}
        >
          <div className="flex items-start gap-4">
            <Checkbox
              checked={task.completed}
              onCheckedChange={() => toggleComplete.mutate(task.id)}
              className="mt-1"
            />

            <div className="flex-1 min-w-0">
              <h3
                className={`font-medium font-chelsea ${
                  task.completed ? "line-through text-text-muted" : "text-white"
                }`}
              >
                {task.title}
              </h3>

              {task.description && (
                <p className="mt-1 text-sm text-text-muted">{task.description}</p>
              )}

              <div className="mt-2 flex flex-wrap items-center gap-2">
                <Badge
                  variant={
                    task.priority === "High"
                      ? "destructive"
                      : task.priority === "Medium"
                      ? "default"
                      : "secondary"
                  }
                >
                  {task.priority}
                </Badge>

                {task.due_date && (
                  <Badge variant="outline" className="gap-1 border-white/20 text-text-tertiary">
                    <Calendar className="h-3 w-3" />
                    {new Date(task.due_date).toLocaleDateString()}
                  </Badge>
                )}

                {task.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="gap-1 border-white/20 text-text-tertiary">
                    <Tag className="h-3 w-3" />
                    {tag}
                  </Badge>
                ))}

                {task.recurring && (
                  <Badge variant="outline" className="gap-1 border-white/20 text-text-tertiary">
                    <Repeat className="h-3 w-3" />
                    {task.recurring}
                  </Badge>
                )}

                {task.recurring_pattern && !task.parent_task_id && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2 text-xs text-sky-cyan-400 hover:text-sky-cyan-300 hover:bg-sky-cyan-500/10"
                    onClick={() => setExpandedTaskId(expandedTaskId === task.id ? null : task.id)}
                  >
                    {expandedTaskId === task.id ? (
                      <>
                        <ChevronUp className="h-3 w-3 mr-1" />
                        Hide Instances
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-3 w-3 mr-1" />
                        View Instances
                      </>
                    )}
                  </Button>
                )}

                {task.parent_task_id && (
                  <Badge variant="outline" className="gap-1 border-purple-500/30 text-purple-400 bg-purple-500/10">
                    Instance #{task.recurrence_count || 0}
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-text-muted hover:text-white hover:bg-white/10"
                onClick={() => onEdit(task)}
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                onClick={() => {
                  if (confirm("Are you sure you want to delete this task?")) {
                    deleteTask.mutate(task.id)
                  }
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {expandedTaskId === task.id && task.recurring_pattern && !task.parent_task_id && (
            <div className="mt-4 pt-4 border-t border-white/10">
              <RecurringTaskInstances parentTaskId={task.id} />
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
