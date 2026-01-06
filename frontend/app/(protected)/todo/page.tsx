"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useSession } from "@/lib/auth-client"
import { useTasks } from "@/hooks/useTasks"
import { TaskList } from "./components/TaskList"
import { TaskForm } from "./components/TaskForm"
import { TaskFilters } from "./components/TaskFilters"
import { TagSidebar } from "./components/TagSidebar"
import { CalendarView } from "./components/CalendarView"
import { Task } from "@/types/task"
import "./components/calendar.css"

const queryClient = new QueryClient()

function TodoPageContent() {
  const router = useRouter()
  const { data: session, isPending } = useSession()
  const [showForm, setShowForm] = useState(false)
  const [editingTask, setEditingTask] = useState<Task | undefined>()
  const [filter, setFilter] = useState<"all" | "pending" | "completed">("all")
  const [selectedTag, setSelectedTag] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [viewMode, setViewMode] = useState<"list" | "calendar">("list")

  // Debug session state
  useEffect(() => {
    console.log("📊 Session state:", {
      isPending,
      hasSession: !!session,
      hasUser: !!session?.user,
      user: session?.user
    })
  }, [session, isPending])

  // Check authentication - redirect to login if not authenticated
  useEffect(() => {
    if (!isPending && !session?.user) {
      console.log("🔒 No authenticated user, redirecting to login")
      router.push("/login")
    }
  }, [session, isPending, router])

  const { data: tasks = [], isLoading, error } = useTasks({
    completed: filter === "all" ? undefined : filter === "completed",
    tag: selectedTag || undefined,
  })

  const handleEdit = (task: Task) => {
    setEditingTask(task)
    setShowForm(true)
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingTask(undefined)
  }

  const handleTagSelect = (tag: string | null) => {
    setSelectedTag(tag)
  }

  // Show loading while checking authentication
  if (isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Checking authentication...</p>
        </div>
      </div>
    )
  }

  // Don't render if not authenticated (redirect will happen)
  if (!session?.user) {
    return null
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-4 text-gray-600">Loading tasks...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <p className="text-red-800">Error loading tasks. Please try again.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Todos</h1>
            <p className="mt-2 text-gray-600">
              Manage your tasks and stay organized
              {selectedTag && (
                <span className="ml-2 rounded-full bg-blue-100 px-2 py-1 text-sm text-blue-800">
                  Filtered by: {selectedTag}
                </span>
              )}
            </p>
          </div>
          <div className="flex gap-3">
            {/* View Toggle */}
            <div className="flex rounded-md border border-gray-300 bg-white">
              <button
                onClick={() => setViewMode("list")}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  viewMode === "list"
                    ? "bg-blue-600 text-white"
                    : "text-gray-700 hover:bg-gray-50"
                } rounded-l-md`}
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              </button>
              <button
                onClick={() => setViewMode("calendar")}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  viewMode === "calendar"
                    ? "bg-blue-600 text-white"
                    : "text-gray-700 hover:bg-gray-50"
                } rounded-r-md border-l border-gray-300`}
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </button>
            </div>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 md:hidden"
            >
              {sidebarOpen ? "Hide Tags" : "Show Tags"}
            </button>
            <button
              onClick={() => setShowForm(true)}
              className="rounded-md bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              + New Task
            </button>
          </div>
        </div>

        <div className="flex gap-6">
          {/* Tag Sidebar */}
          <aside
            className={`w-64 flex-shrink-0 transition-all ${
              sidebarOpen ? "block" : "hidden md:block"
            }`}
          >
            <TagSidebar
              tasks={tasks}
              selectedTag={selectedTag}
              onTagSelect={handleTagSelect}
            />
          </aside>

          {/* Main Content */}
          <main className="flex-1">
            {viewMode === "list" ? (
              <div className="animate-fadeIn rounded-lg bg-white p-6 shadow-sm">
                <TaskFilters activeFilter={filter} onFilterChange={setFilter} />

                <div className="mt-6">
                  <TaskList tasks={tasks} onEdit={handleEdit} />
                </div>
              </div>
            ) : (
              <div className="animate-fadeIn">
                <CalendarView tasks={tasks} onEventClick={handleEdit} />
              </div>
            )}
          </main>
        </div>

        {showForm && (
          <TaskForm task={editingTask} onClose={handleCloseForm} />
        )}
      </div>
    </div>
  )
}

export default function TodoPage() {
  return (
    <QueryClientProvider client={queryClient}>
      <TodoPageContent />
    </QueryClientProvider>
  )
}
