"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { CreateTaskInput, Task } from "@/types/task"
import { useCreateTask, useUpdateTask } from "@/hooks/useTasks"

const taskSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().optional(),
  priority: z.enum(["High", "Medium", "Low"]),
  tags: z.string().optional(),
  due_date: z.string().optional(),
  recurring: z.enum(["daily", "weekly", "monthly", ""]).optional(),
})

type TaskFormData = z.infer<typeof taskSchema>

interface TaskFormProps {
  task?: Task
  onClose: () => void
}

export function TaskForm({ task, onClose }: TaskFormProps) {
  const createTask = useCreateTask()
  const updateTask = useUpdateTask()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: task
      ? {
          title: task.title,
          description: task.description || "",
          priority: task.priority as "High" | "Medium" | "Low",
          tags: task.tags.join(", "),
          due_date: task.due_date || "",
          recurring: task.recurring || "",
        }
      : {
          priority: "Medium",
        },
  })

  const onSubmit = async (data: TaskFormData) => {
    const taskData: CreateTaskInput = {
      title: data.title,
      description: data.description || undefined,
      priority: data.priority,
      tags: data.tags
        ? data.tags.split(",").map((t) => t.trim()).filter(Boolean)
        : [],
      due_date: data.due_date || undefined,
      recurring: data.recurring || undefined,
    }

    if (task) {
      await updateTask.mutateAsync({ id: task.id, data: taskData })
    } else {
      await createTask.mutateAsync(taskData)
    }

    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
        <h2 className="mb-4 text-2xl font-bold">
          {task ? "Edit Task" : "Create New Task"}
        </h2>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">
              Title *
            </label>
            <input
              {...register("title")}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="Task title"
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              {...register("description")}
              rows={3}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="Task description"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Priority *
            </label>
            <select
              {...register("priority")}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            >
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Tags (comma-separated)
            </label>
            <input
              {...register("tags")}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
              placeholder="work, urgent, personal"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Due Date
            </label>
            <input
              {...register("due_date")}
              type="date"
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Recurring
            </label>
            <select
              {...register("recurring")}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
            >
              <option value="">None</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={createTask.isPending || updateTask.isPending}
              className="flex-1 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {task ? "Update" : "Create"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
