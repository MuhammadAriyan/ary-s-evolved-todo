/**
 * RecurringTaskBadge Component
 * T117: Add recurring task indicator badge in task list
 */

"use client"

import { Badge } from "@/components/ui/badge"
import { Repeat } from "lucide-react"
import cronstrue from "cronstrue"

interface RecurringTaskBadgeProps {
  recurringPattern: string
  className?: string
}

export function RecurringTaskBadge({ recurringPattern, className = "" }: RecurringTaskBadgeProps) {
  // Parse cron expression to human-readable description
  const getDescription = () => {
    try {
      return cronstrue.toString(recurringPattern, {
        use24HourTimeFormat: true,
        verbose: false
      })
    } catch (error) {
      return "Recurring"
    }
  }

  return (
    <Badge
      variant="secondary"
      className={`flex items-center gap-1 bg-purple-500/20 text-purple-300 border-purple-500/30 ${className}`}
    >
      <Repeat className="h-3 w-3" />
      <span className="text-xs">{getDescription()}</span>
    </Badge>
  )
}
