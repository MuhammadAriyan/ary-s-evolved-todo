/**
 * Task types for the todo application
 */

export type Priority = "High" | "Medium" | "Low"

export type Recurring = "daily" | "weekly" | "monthly" | null

export interface RecurringPattern {
  type: 'preset' | 'custom'
  preset?: 'daily' | 'weekly' | 'monthly' | 'yearly'
  customCron?: string
  timezone?: string
  endDate?: string
  maxOccurrences?: number
}

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
  recurring_pattern?: RecurringPattern
  parent_task_id?: number
  recurrence_count?: number
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
  recurring_pattern?: RecurringPattern
}

export interface UpdateTaskInput {
  title?: string
  description?: string
  priority?: Priority
  tags?: string[]
  due_date?: string
  recurring?: Recurring
  recurring_pattern?: RecurringPattern
  completed?: boolean
}
