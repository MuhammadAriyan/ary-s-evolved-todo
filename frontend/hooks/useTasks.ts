/**
 * TanStack Query hooks for task operations with optimistic updates
 * T043: Extended with WebSocket real-time synchronization
 */

import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from "@tanstack/react-query"
import { useEffect, useState, useCallback } from "react"
import { apiClient } from "@/lib/api-client"
import { useSession, authClient } from "@/lib/auth-client"
import { useWebSocket } from "./useWebSocket"
import type { Task, CreateTaskInput, UpdateTaskInput } from "@/types/task"
import type { WebSocketMessage } from "@/lib/websocket-client"
import { devLog } from "@/lib/utils"

const TASKS_QUERY_KEY = ["tasks"]

export function useTasks(
  filters?: {
    tag?: string
    priority?: string
    completed?: boolean
    sort?: string
  },
  options?: Omit<UseQueryOptions<Task[], Error>, 'queryKey' | 'queryFn'>
) {
  const { data: session } = useSession()
  const [tokenReady, setTokenReady] = useState(false)
  const queryClient = useQueryClient()

  // Set JWT token in API client when session changes
  useEffect(() => {
    const fetchAndSetToken = async () => {
      if (session?.user) {
        try {
          // Use Better Auth JWT client plugin to get JWT token
          const { data, error } = await authClient.token()

          if (data?.token) {
            devLog("✅ JWT token retrieved successfully")
            devLog("Token preview:", data.token.substring(0, 50) + "...")
            apiClient.setToken(data.token)
            setTokenReady(true)
          } else if (error) {
            devLog("❌ Failed to retrieve JWT token:", error)
            apiClient.clearToken()
            setTokenReady(false)
          }
        } catch (err) {
          devLog("❌ Error fetching JWT token:", err)
          apiClient.clearToken()
          setTokenReady(false)
        }
      } else {
        devLog("⚠️ No session, clearing token")
        apiClient.clearToken()
        setTokenReady(false)
      }
    }

    fetchAndSetToken()
  }, [session])

  // T043: Subscribe to WebSocket updates for real-time synchronization
  const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
    if (message.type === 'task_update') {
      const eventType = message.event_type
      const task = message.task

      devLog(`📡 Real-time update: ${eventType}`, task)

      // Update query cache based on event type
      queryClient.setQueryData<Task[]>(TASKS_QUERY_KEY, (old = []) => {
        switch (eventType) {
          case 'task.created':
            // Add new task if not already present
            if (!old.find(t => t.id === task.id)) {
              return [task, ...old]
            }
            return old

          case 'task.updated':
          case 'task.completed':
          case 'task.uncompleted':
            // Update existing task
            return old.map(t => t.id === task.id ? { ...t, ...task } : t)

          case 'task.deleted':
            // Remove deleted task
            return old.filter(t => t.id !== task.id)

          default:
            return old
        }
      })
    } else if (message.type === 'replay_start') {
      devLog(`📡 Replaying ${message.count} missed events since ${message.since}`)
    } else if (message.type === 'replay_complete') {
      devLog(`📡 Replay complete: ${message.count} events`)
    }
  }, [queryClient])

  // Connect to WebSocket for real-time updates
  const { status: wsStatus, isConnected: wsConnected } = useWebSocket({
    enabled: !!session?.user && tokenReady,
    onMessage: handleWebSocketMessage,
    onError: (error) => {
      devLog('WebSocket error in useTasks:', error)
    }
  })

  const query = useQuery({
    queryKey: [...TASKS_QUERY_KEY, filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters?.tag) params.append("tag", filters.tag)
      if (filters?.priority) params.append("priority", filters.priority)
      if (filters?.completed !== undefined)
        params.append("completed", String(filters.completed))
      if (filters?.sort) params.append("sort", filters.sort)

      const query = params.toString()
      return apiClient.get<Task[]>(`/api/v1/tasks${query ? `?${query}` : ""}`)
    },
    enabled: !!session?.user && tokenReady, // Only run query if user is authenticated AND token is ready
    ...options, // Merge provided options
  })

  return {
    ...query,
    wsStatus,
    wsConnected
  }
}

export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (data: CreateTaskInput) => {
      return apiClient.post<Task>("/api/v1/tasks", data)
    },
    onMutate: async (newTask) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: TASKS_QUERY_KEY })

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData(TASKS_QUERY_KEY)

      // Optimistically update
      queryClient.setQueryData<Task[]>(TASKS_QUERY_KEY, (old = []) => [
        {
          ...newTask,
          id: Date.now(), // Temporary ID
          user_id: "temp",
          completed: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        } as Task,
        ...old,
      ])

      return { previousTasks }
    },
    onError: (err, newTask, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(TASKS_QUERY_KEY, context.previousTasks)
      }
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY })
    },
  })
}

export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ id, data }: { id: number; data: UpdateTaskInput }) => {
      return apiClient.put<Task>(`/api/v1/tasks/${id}`, data)
    },
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: TASKS_QUERY_KEY })

      const previousTasks = queryClient.getQueryData(TASKS_QUERY_KEY)

      queryClient.setQueryData<Task[]>(TASKS_QUERY_KEY, (old = []) =>
        old.map((task) =>
          task.id === id
            ? { ...task, ...data, updated_at: new Date().toISOString() }
            : task
        )
      )

      return { previousTasks }
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(TASKS_QUERY_KEY, context.previousTasks)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY })
    },
  })
}

export function useToggleComplete() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      return apiClient.patch<Task>(`/api/v1/tasks/${id}/complete`, {})
    },
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: TASKS_QUERY_KEY })

      const previousTasks = queryClient.getQueryData(TASKS_QUERY_KEY)

      queryClient.setQueryData<Task[]>(TASKS_QUERY_KEY, (old = []) =>
        old.map((task) =>
          task.id === id
            ? {
                ...task,
                completed: !task.completed,
                updated_at: new Date().toISOString(),
              }
            : task
        )
      )

      return { previousTasks }
    },
    onError: (err, id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(TASKS_QUERY_KEY, context.previousTasks)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY })
    },
  })
}

export function useDeleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (id: number) => {
      return apiClient.delete(`/api/v1/tasks/${id}`)
    },
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: TASKS_QUERY_KEY })

      const previousTasks = queryClient.getQueryData(TASKS_QUERY_KEY)

      queryClient.setQueryData<Task[]>(TASKS_QUERY_KEY, (old = []) =>
        old.filter((task) => task.id !== id)
      )

      return { previousTasks }
    },
    onError: (err, id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(TASKS_QUERY_KEY, context.previousTasks)
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: TASKS_QUERY_KEY })
    },
  })
}
