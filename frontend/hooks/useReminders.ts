/**
 * TanStack Query hooks for reminder operations
 * T068-T073: Reminder management hooks
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { apiClient } from "@/lib/api-client"
import { useSession } from "@/lib/auth-client"

export interface Reminder {
  id: number
  task_id: string
  user_id: string
  reminder_time: string
  timezone: string
  notification_channels: string[]
  cron_expression?: string
  status: string
  last_triggered_at?: string
  created_at: string
  updated_at: string
}

export interface CreateReminderInput {
  task_id: string
  reminder_time: string
  timezone: string
  notification_channels: string[]
  cron_expression?: string
}

export interface UpdateReminderInput {
  reminder_time?: string
  timezone?: string
  notification_channels?: string[]
  status?: string
}

const REMINDERS_QUERY_KEY = (taskId: string) => ["reminders", taskId]

export function useReminders(taskId: string) {
  const { data: session } = useSession()

  // Fetch reminders for a task
  const {
    data: reminders,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: REMINDERS_QUERY_KEY(taskId),
    queryFn: async () => {
      const response = await apiClient.get<Reminder[]>(
        `/api/v1/tasks/${taskId}/reminders`
      )
      return response
    },
    enabled: !!session?.user && !!taskId,
  })

  return {
    reminders: reminders || [],
    isLoading,
    error,
    refetch,
  }
}

export function useCreateReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (input: CreateReminderInput) => {
      const response = await apiClient.post(
        `/api/v1/tasks/${input.task_id}/reminders`,
        input
      )
      return response
    },
    onSuccess: (_, variables) => {
      // Invalidate reminders query for this task
      queryClient.invalidateQueries({
        queryKey: REMINDERS_QUERY_KEY(variables.task_id),
      })
    },
  })
}

export function useUpdateReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      reminderId,
      taskId,
      data,
    }: {
      reminderId: number
      taskId: string
      data: UpdateReminderInput
    }) => {
      const response = await apiClient.patch(
        `/api/v1/reminders/${reminderId}`,
        data
      )
      return response
    },
    onSuccess: (_, variables) => {
      // Invalidate reminders query for this task
      queryClient.invalidateQueries({
        queryKey: REMINDERS_QUERY_KEY(variables.taskId),
      })
    },
  })
}

export function useDeleteReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      reminderId,
      taskId,
    }: {
      reminderId: number
      taskId: string
    }) => {
      await apiClient.delete(`/api/v1/reminders/${reminderId}`)
    },
    onSuccess: (_, variables) => {
      // Invalidate reminders query for this task
      queryClient.invalidateQueries({
        queryKey: REMINDERS_QUERY_KEY(variables.taskId),
      })
    },
  })
}

/**
 * T071: Request notification permission
 */
export function useNotificationPermission() {
  const requestPermission = async () => {
    if (!("Notification" in window)) {
      console.warn("This browser does not support notifications")
      return false
    }

    if (Notification.permission === "granted") {
      return true
    }

    if (Notification.permission !== "denied") {
      const permission = await Notification.requestPermission()
      return permission === "granted"
    }

    return false
  }

  return {
    permission: typeof window !== "undefined" ? Notification.permission : "default",
    requestPermission,
  }
}
