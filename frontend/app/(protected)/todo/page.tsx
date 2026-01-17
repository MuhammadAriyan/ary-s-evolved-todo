"use client"

import { useState, useEffect, useMemo, Suspense } from "react"
import dynamic from "next/dynamic"
import { useRouter } from "next/navigation"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useSession } from "@/lib/auth-client"
import { useTasks } from "@/hooks/useTasks"
import { TaskList } from "./components/TaskList"
import { TaskForm } from "./components/TaskForm"
import { TaskFilters } from "./components/TaskFilters"
import { TagSidebar } from "./components/TagSidebar"
import { Task } from "@/types/task"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { SuggestiveSearch } from "@/components/ui/suggestive-search"
import { List, CalendarDays, Plus, Tag, X } from "lucide-react"
import "./components/calendar.css"

// Lazy load heavy components for better performance
const CalendarView = dynamic(
  () => import("./components/CalendarView").then((mod) => ({ default: mod.CalendarView })),
  {
    ssr: false,
    loading: () => (
      <div className="p-6 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl">
        <div className="space-y-4">
          <Skeleton className="h-8 w-48 bg-white/10" />
          <Skeleton className="h-[400px] w-full bg-white/10" />
        </div>
      </div>
    ),
  }
)

const TaskAnalyticsCard = dynamic(
  () => import("@/components/ui/task-analytics-card").then((mod) => ({ default: mod.TaskAnalyticsCard })),
  {
    ssr: false,
    loading: () => <Skeleton className="h-40 w-full bg-white/10 rounded-2xl" />,
  }
)

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
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    if (!isPending && !session?.user) {
      router.push("/login")
    }
  }, [session, isPending, router])

  // Fetch ALL tasks for tag counts and analytics
  const { data: allTasks = [], isLoading: allTasksLoading } = useTasks({})

  // Fetch filtered tasks based on selected tag and completion filter
  const { data: tasks = [], isLoading, error } = useTasks({
    completed: filter === "all" ? undefined : filter === "completed",
    tag: selectedTag || undefined,
  })

  // Filter tasks by search query
  const filteredTasks = useMemo(() => {
    if (!searchQuery.trim()) return tasks
    const query = searchQuery.toLowerCase()
    return tasks.filter(
      (task) =>
        task.title.toLowerCase().includes(query) ||
        task.description?.toLowerCase().includes(query) ||
        task.tags?.some((tag) => tag.toLowerCase().includes(query))
    )
  }, [tasks, searchQuery])

  // Calculate analytics data from ALL tasks
  const analyticsData = useMemo(() => {
    const last28Days = Array.from({ length: 28 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (27 - i))
      return date.toISOString().split("T")[0]
    })

    const tasksByDay = last28Days.map((day) => ({
      day: `Day ${last28Days.indexOf(day) + 1}`,
      count: allTasks.filter((task) => {
        const taskDate = task.created_at?.split("T")[0]
        return taskDate === day
      }).length,
    }))

    return tasksByDay
  }, [allTasks])

  const completedTasks = allTasks.filter((t) => t.completed).length

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

  const handleSearch = (query: string) => {
    setSearchQuery(query)
  }

  if (isPending || isLoading || allTasksLoading) {
    return (
      <div className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-7xl space-y-6">
          <div className="flex justify-between items-center">
            <div className="space-y-2">
              <Skeleton className="h-8 w-48 bg-white/10" />
              <Skeleton className="h-4 w-64 bg-white/10" />
            </div>
            <Skeleton className="h-10 w-32 bg-white/10" />
          </div>
          <div className="flex gap-6">
            <div className="w-80 space-y-4">
              <Skeleton className="h-40 w-full bg-white/10" />
              <Skeleton className="h-40 w-full bg-white/10" />
            </div>
            <div className="flex-1 space-y-4">
              <Skeleton className="h-12 w-full bg-white/10" />
              <Skeleton className="h-24 w-full bg-white/10" />
              <Skeleton className="h-24 w-full bg-white/10" />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!session?.user) {
    return null
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="p-8 text-center rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl">
          <p className="text-red-400 text-sm">Error loading tasks. Please try again.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl space-y-6">
        {/* Page Header */}
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="space-y-1">
            <h1 className="text-2xl font-semibold text-white sm:text-3xl font-chelsea">My Todos</h1>
            <p className="text-sm text-white/50">
              Manage your tasks and stay organized
            </p>
            {selectedTag && (
              <Badge
                variant="secondary"
                className="mt-1 bg-sky-cyan-500/20 text-sky-cyan-400 border-sky-cyan-500/30 cursor-pointer hover:bg-sky-cyan-500/30"
                onClick={() => setSelectedTag(null)}
              >
                {selectedTag}
                <X className="w-3 h-3 ml-1" />
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* View Toggle */}
            <div className="flex border border-white/10 rounded-lg p-1 bg-black/30 backdrop-blur-sm">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setViewMode("list")}
                className={`h-8 px-3 ${viewMode === "list" ? "bg-sky-cyan-500/20 text-sky-cyan-400" : "text-white/60 hover:text-white hover:bg-white/10"}`}
              >
                <List className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setViewMode("calendar")}
                className={`h-8 px-3 ${viewMode === "calendar" ? "bg-sky-cyan-500/20 text-sky-cyan-400" : "text-white/60 hover:text-white hover:bg-white/10"}`}
              >
                <CalendarDays className="h-4 w-4" />
              </Button>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden border border-white/10 text-white/60 hover:text-white hover:bg-white/10"
            >
              <Tag className="h-4 w-4 mr-1" />
              Tags
            </Button>

            <Button
              onClick={() => setShowForm(true)}
              size="sm"
              className="bg-gradient-to-r from-sky-cyan-500 to-soft-aqua-400 text-white hover:opacity-90 border-0"
            >
              <Plus className="h-4 w-4 mr-1" />
              New Task
            </Button>
          </div>
        </header>

        {/* Search Bar */}
        <div className="max-w-xl">
          <SuggestiveSearch
            onChange={handleSearch}
            onSearch={handleSearch}
            suggestions={[
              "Search tasks by title...",
              "Filter by tag name...",
              "Find completed tasks...",
            ]}
            className="w-full"
          />
        </div>

        {/* Main Content Grid - Sidebar (Analytics + Tags) | Tasks */}
        <div className="flex gap-6">
          {/* Left Sidebar - Analytics + Tags */}
          <aside
            className={`w-80 flex-shrink-0 space-y-4 transition-all duration-200 ${
              sidebarOpen ? "block" : "hidden md:block"
            }`}
          >
            {/* Analytics Card */}
            <TaskAnalyticsCard
              taskData={analyticsData}
              totalTasks={allTasks.length}
              completedTasks={completedTasks}
            />

            {/* Tag Sidebar */}
            <TagSidebar
              tasks={allTasks}
              selectedTag={selectedTag}
              onTagSelect={handleTagSelect}
            />
          </aside>

          {/* Main Content - Task List */}
          <main className="flex-1 min-w-0">
            {viewMode === "list" ? (
              <div className="p-6 space-y-6 rounded-2xl border border-white/10 bg-black/30 backdrop-blur-xl">
                <TaskFilters activeFilter={filter} onFilterChange={setFilter} />
                <TaskList tasks={filteredTasks} onEdit={handleEdit} />
              </div>
            ) : (
              <CalendarView tasks={filteredTasks} onEventClick={handleEdit} />
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
