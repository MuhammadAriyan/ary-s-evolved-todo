/**
 * TanStack Query hooks for task operations with optimistic updates
 */

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { apiClient } from "@/lib/api-client"
import { useSession, authClient } from "@/lib/auth-client"
import type { Task, CreateTaskInput, UpdateTaskInput } from "@/types/task"

const TASKS_QUERY_KEY = ["tasks"]

export function useTasks(filters?: {
  tag?: string
  priority?: string
  completed?: boolean
  sort?: string
}) {
  const { data: session } = useSession()
  const [tokenReady, setTokenReady] = useState(false)

  // Set JWT token in API client when session changes
  useEffect(() => {
    const fetchAndSetToken = async () => {
      if (session?.user) {
        try {
          // Use Better Auth JWT client plugin to get JWT token
          const { data, error } = await authClient.token()

          if (data?.token) {
            console.log("✅ JWT token retrieved successfully")
            console.log("Token preview:", data.token.substring(0, 50) + "...")
            apiClient.setToken(data.token)
            setTokenReady(true)
          } else if (error) {
            console.error("❌ Failed to retrieve JWT token:", error)
            apiClient.clearToken()
            setTokenReady(false)
          }
        } catch (err) {
          console.error("❌ Error fetching JWT token:", err)
          apiClient.clearToken()
          setTokenReady(false)
        }
      } else {
        console.log("⚠️ No session, clearing token")
        apiClient.clearToken()
        setTokenReady(false)
      }
    }

    fetchAndSetToken()
  }, [session])

  return useQuery({
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
  })
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
