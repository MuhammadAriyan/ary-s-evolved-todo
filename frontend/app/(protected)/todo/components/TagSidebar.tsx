"use client"

import { Task } from "@/types/task"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tag, X } from "lucide-react"

interface TagSidebarProps {
  tasks: Task[]
  selectedTag: string | null
  onTagSelect: (tag: string | null) => void
}

export function TagSidebar({ tasks, selectedTag, onTagSelect }: TagSidebarProps) {
  // Extract unique tags with counts from ALL tasks (not filtered)
  const tagCounts = tasks.reduce((acc, task) => {
    task.tags.forEach((tag) => {
      acc[tag] = (acc[tag] || 0) + 1
    })
    return acc
  }, {} as Record<string, number>)

  const sortedTags = Object.entries(tagCounts).sort((a, b) => b[1] - a[1])

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-medium flex items-center gap-2 text-white/60">
            <Tag className="h-4 w-4 text-sky-cyan-400" />
            Tags
          </CardTitle>
          {selectedTag && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onTagSelect(null)}
              className="h-7 px-2 text-xs text-white/60 hover:text-white hover:bg-white/10"
            >
              <X className="h-3 w-3 mr-1" />
              Clear
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {sortedTags.length === 0 ? (
          <p className="text-sm text-white/40">
            No tags yet. Add tags to your tasks to organize them.
          </p>
        ) : (
          <div className="space-y-1">
            {sortedTags.map(([tag, count]) => (
              <button
                key={tag}
                onClick={() => onTagSelect(tag === selectedTag ? null : tag)}
                className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-all ${
                  selectedTag === tag
                    ? "bg-sky-cyan-500/20 text-sky-cyan-400 border border-sky-cyan-500/30"
                    : "text-white/70 hover:bg-white/10 hover:text-white border border-transparent"
                }`}
              >
                <span className="truncate">{tag}</span>
                <Badge variant="secondary" className="ml-2 bg-white/10 text-white/60 border-0">
                  {count}
                </Badge>
              </button>
            ))}
          </div>
        )}

        {sortedTags.length > 0 && (
          <p className="mt-4 pt-4 border-t border-white/10 text-xs text-white/40">
            {sortedTags.length} {sortedTags.length === 1 ? "tag" : "tags"} total
          </p>
        )}
      </CardContent>
    </Card>
  )
}
