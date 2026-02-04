/**
 * ParentTaskLink Component
 * T118: Add "view parent task" link in recurring task instances
 */

"use client"

import { Link2, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ParentTaskLinkProps {
  parentTaskId: string
  onViewParent?: (parentTaskId: string) => void
  className?: string
}

export function ParentTaskLink({
  parentTaskId,
  onViewParent,
  className = ""
}: ParentTaskLinkProps) {
  const handleClick = () => {
    if (onViewParent) {
      onViewParent(parentTaskId)
    }
  }

  return (
    <div className={`flex items-center gap-2 text-sm ${className}`}>
      <Link2 className="h-4 w-4 text-white/50" />
      <span className="text-white/60">Instance of recurring task</span>
      <Button
        variant="ghost"
        size="sm"
        onClick={handleClick}
        className="h-auto p-1 text-sky-cyan-400 hover:text-sky-cyan-300"
      >
        <span className="flex items-center gap-1">
          View parent
          <ExternalLink className="h-3 w-3" />
        </span>
      </Button>
    </div>
  )
}
