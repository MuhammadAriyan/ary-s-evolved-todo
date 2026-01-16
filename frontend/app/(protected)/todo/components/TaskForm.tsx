"use client"

import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { CreateTaskInput, Task } from "@/types/task"
import { useCreateTask, useUpdateTask } from "@/hooks/useTasks"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { X } from "lucide-react"

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
    setValue,
    watch,
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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="font-chelsea">{task ? "Edit Task" : "Create New Task"}</CardTitle>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8">
            <X className="h-4 w-4" />
          </Button>
        </CardHeader>

        <form onSubmit={handleSubmit(onSubmit)}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                {...register("title")}
                placeholder="Task title"
              />
              {errors.title && (
                <p className="text-sm text-destructive">{errors.title.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                {...register("description")}
                placeholder="Task description"
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="priority">Priority *</Label>
              <Select
                defaultValue={watch("priority")}
                onValueChange={(value) => setValue("priority", value as "High" | "Medium" | "Low")}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="High">High</SelectItem>
                  <SelectItem value="Medium">Medium</SelectItem>
                  <SelectItem value="Low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="tags">Tags (comma-separated)</Label>
              <Input
                id="tags"
                {...register("tags")}
                placeholder="work, urgent, personal"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="due_date">Due Date</Label>
              <Input
                id="due_date"
                type="date"
                {...register("due_date")}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="recurring">Recurring</Label>
              <Select
                defaultValue={watch("recurring") || "none"}
                onValueChange={(value) => setValue("recurring", value === "none" ? "" : value as "" | "daily" | "weekly" | "monthly")}
              >
                <SelectTrigger>
                  <SelectValue placeholder="None" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">None</SelectItem>
                  <SelectItem value="daily">Daily</SelectItem>
                  <SelectItem value="weekly">Weekly</SelectItem>
                  <SelectItem value="monthly">Monthly</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>

          <CardFooter className="flex gap-3">
            <Button
              type="submit"
              className="flex-1"
              disabled={createTask.isPending || updateTask.isPending}
            >
              {createTask.isPending || updateTask.isPending
                ? "Saving..."
                : task
                ? "Update"
                : "Create"}
            </Button>
            <Button type="button" variant="outline" className="flex-1" onClick={onClose}>
              Cancel
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
