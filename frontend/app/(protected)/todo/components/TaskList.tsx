"use client"

import { Task } from "@/types/task"
import { useToggleComplete, useDeleteTask } from "@/hooks/useTasks"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Badge } from "@/components/ui/badge"
import { Pencil, Trash2, Calendar, Tag, Repeat } from "lucide-react"

interface TaskListProps {
  tasks: Task[]
  onEdit: (task: Task) => void
}

export function TaskList({ tasks, onEdit }: TaskListProps) {
  const toggleComplete = useToggleComplete()
  const deleteTask = useDeleteTask()

  if (tasks.length === 0) {
    return (
      <div className="py-12 text-center">
        <p className="text-white/50 font-chelsea">No tasks found. Create your first task!</p>
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
                  task.completed ? "line-through text-white/50" : "text-white"
                }`}
              >
                {task.title}
              </h3>

              {task.description && (
                <p className="mt-1 text-sm text-white/50">{task.description}</p>
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
                  <Badge variant="outline" className="gap-1 border-white/20 text-white/70">
                    <Calendar className="h-3 w-3" />
                    {new Date(task.due_date).toLocaleDateString()}
                  </Badge>
                )}

                {task.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="gap-1 border-white/20 text-white/70">
                    <Tag className="h-3 w-3" />
                    {tag}
                  </Badge>
                ))}

                {task.recurring && (
                  <Badge variant="outline" className="gap-1 border-white/20 text-white/70">
                    <Repeat className="h-3 w-3" />
                    {task.recurring}
                  </Badge>
                )}
              </div>
            </div>

            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-white/60 hover:text-white hover:bg-white/10"
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
        </Card>
      ))}
    </div>
  )
}
