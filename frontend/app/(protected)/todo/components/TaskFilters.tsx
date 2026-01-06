"use client"

interface TaskFiltersProps {
  activeFilter: "all" | "pending" | "completed"
  onFilterChange: (filter: "all" | "pending" | "completed") => void
}

export function TaskFilters({ activeFilter, onFilterChange }: TaskFiltersProps) {
  return (
    <div className="flex gap-2 border-b border-gray-200">
      <button
        onClick={() => onFilterChange("all")}
        className={`px-4 py-2 text-sm font-medium transition-colors ${
          activeFilter === "all"
            ? "border-b-2 border-blue-600 text-blue-600"
            : "text-gray-600 hover:text-gray-900"
        }`}
      >
        All
      </button>
      <button
        onClick={() => onFilterChange("pending")}
        className={`px-4 py-2 text-sm font-medium transition-colors ${
          activeFilter === "pending"
            ? "border-b-2 border-blue-600 text-blue-600"
            : "text-gray-600 hover:text-gray-900"
        }`}
      >
        Pending
      </button>
      <button
        onClick={() => onFilterChange("completed")}
        className={`px-4 py-2 text-sm font-medium transition-colors ${
          activeFilter === "completed"
            ? "border-b-2 border-blue-600 text-blue-600"
            : "text-gray-600 hover:text-gray-900"
        }`}
      >
        Completed
      </button>
    </div>
  )
}
