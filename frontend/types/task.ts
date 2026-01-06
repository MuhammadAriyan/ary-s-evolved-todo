/**
 * Task types for the todo application
 */

export type Priority = "High" | "Medium" | "Low"

export type Recurring = "daily" | "weekly" | "monthly" | null

export interface Task {
  id: number
  user_id: string
  title: string
  description?: string
  completed: boolean
  priority: Priority
  tags: string[]
  due_date?: string
  recurring?: Recurring
  created_at: string
  updated_at: string
}

export interface CreateTaskInput {
  title: string
  description?: string
  priority: Priority
  tags?: string[]
  due_date?: string
  recurring?: Recurring
}

export interface UpdateTaskInput {
  title?: string
  description?: string
  priority?: Priority
  tags?: string[]
  due_date?: string
  recurring?: Recurring
  completed?: boolean
}
