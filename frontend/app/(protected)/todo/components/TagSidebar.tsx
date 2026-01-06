"use client"

import { Task } from "@/types/task"

interface TagSidebarProps {
  tasks: Task[]
  selectedTag: string | null
  onTagSelect: (tag: string | null) => void
}

export function TagSidebar({ tasks, selectedTag, onTagSelect }: TagSidebarProps) {
  // Extract unique tags with counts
  const tagCounts = tasks.reduce((acc, task) => {
    task.tags.forEach((tag) => {
      acc[tag] = (acc[tag] || 0) + 1
    })
    return acc
  }, {} as Record<string, number>)

  const sortedTags = Object.entries(tagCounts).sort((a, b) => b[1] - a[1])

  if (sortedTags.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h2 className="mb-4 text-lg font-semibold text-gray-900">Tags</h2>
        <p className="text-sm text-gray-500">
          No tags yet. Add tags to your tasks to organize them!
        </p>
      </div>
    )
  }

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900">Tags</h2>
        {selectedTag && (
          <button
            onClick={() => onTagSelect(null)}
            className="text-sm text-blue-600 hover:text-blue-700"
          >
            Clear filter
          </button>
        )}
      </div>

      <div className="space-y-2">
        {sortedTags.map(([tag, count]) => (
          <button
            key={tag}
            onClick={() => onTagSelect(tag === selectedTag ? null : tag)}
            className={`flex w-full items-center justify-between rounded-md px-3 py-2 text-left transition-colors ${
              selectedTag === tag
                ? "bg-blue-100 text-blue-900"
                : "hover:bg-gray-100 text-gray-700"
            }`}
          >
            <span className="flex items-center gap-2">
              <span className="text-sm font-medium">{tag}</span>
            </span>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                selectedTag === tag
                  ? "bg-blue-200 text-blue-900"
                  : "bg-gray-200 text-gray-700"
              }`}
            >
              {count}
            </span>
          </button>
        ))}
      </div>

      <div className="mt-4 border-t border-gray-200 pt-4">
        <div className="text-xs text-gray-500">
          {sortedTags.length} {sortedTags.length === 1 ? "tag" : "tags"} total
        </div>
      </div>
    </div>
  )
}
