"use client"

import { Task } from "@/types/task"
import { useToggleComplete, useDeleteTask } from "@/hooks/useTasks"

interface TaskListProps {
  tasks: Task[]
  onEdit: (task: Task) => void
}

export function TaskList({ tasks, onEdit }: TaskListProps) {
  const toggleComplete = useToggleComplete()
  const deleteTask = useDeleteTask()

  if (tasks.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
        <p className="text-gray-500">No tasks found. Create your first task!</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <div
          key={task.id}
          className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
        >
          <div className="flex items-start gap-3">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => toggleComplete.mutate(task.id)}
              className="mt-1 h-5 w-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />

            <div className="flex-1">
              <h3
                className={`text-lg font-medium ${
                  task.completed ? "text-gray-400 line-through" : "text-gray-900"
                }`}
              >
                {task.title}
              </h3>

              {task.description && (
                <p className="mt-1 text-sm text-gray-600">{task.description}</p>
              )}

              <div className="mt-2 flex flex-wrap items-center gap-2">
                <span
                  className={`rounded-full px-2 py-1 text-xs font-medium ${
                    task.priority === "High"
                      ? "bg-red-100 text-red-800"
                      : task.priority === "Medium"
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-green-100 text-green-800"
                  }`}
                >
                  {task.priority}
                </span>

                {task.due_date && (
                  <span className="text-xs text-gray-500">
                    Due: {new Date(task.due_date).toLocaleDateString()}
                  </span>
                )}

                {task.tags.map((tag) => (
                  <span
                    key={tag}
                    className="rounded-full bg-blue-100 px-2 py-1 text-xs text-blue-800"
                  >
                    {tag}
                  </span>
                ))}

                {task.recurring && (
                  <span className="rounded-full bg-purple-100 px-2 py-1 text-xs text-purple-800">
                    🔄 {task.recurring}
                  </span>
                )}
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => onEdit(task)}
                className="rounded-md px-3 py-1 text-sm text-blue-600 hover:bg-blue-50"
              >
                Edit
              </button>
              <button
                onClick={() => {
                  if (confirm("Are you sure you want to delete this task?")) {
                    deleteTask.mutate(task.id)
                  }
                }}
                className="rounded-md px-3 py-1 text-sm text-red-600 hover:bg-red-50"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
