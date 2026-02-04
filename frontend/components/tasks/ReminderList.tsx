/**
 * ReminderList Component
 * T072: Add reminder list view in task detail showing all scheduled reminders
 */

"use client"

import { useState } from "react"
import { useReminders, useDeleteReminder } from "@/hooks/useReminders"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bell, Trash2, Mail, Smartphone, Globe } from "lucide-react"
import { format } from "date-fns"

interface ReminderListProps {
  taskId: string
}

export function ReminderList({ taskId }: ReminderListProps) {
  const { reminders, isLoading } = useReminders(taskId)
  const deleteReminder = useDeleteReminder()
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const handleDelete = async (reminderId: number) => {
    if (!confirm("Are you sure you want to delete this reminder?")) {
      return
    }

    setDeletingId(reminderId)
    try {
      await deleteReminder.mutateAsync({ reminderId, taskId })
    } catch (error) {
      console.error("Error deleting reminder:", error)
      alert("Failed to delete reminder")
    } finally {
      setDeletingId(null)
    }
  }

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case "email":
        return <Mail className="h-3 w-3" />
      case "push":
        return <Smartphone className="h-3 w-3" />
      case "in_app":
        return <Bell className="h-3 w-3" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pending":
        return "bg-blue-500/20 text-blue-300"
      case "sent":
        return "bg-green-500/20 text-green-300"
      case "failed":
        return "bg-red-500/20 text-red-300"
      default:
        return "bg-gray-500/20 text-gray-300"
    }
  }

  if (isLoading) {
    return (
      <div className="text-center py-4 text-white/60">
        Loading reminders...
      </div>
    )
  }

  if (!reminders || reminders.length === 0) {
    return (
      <div className="text-center py-8 text-white/60">
        <Bell className="h-12 w-12 mx-auto mb-2 opacity-50" />
        <p>No reminders set for this task</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {reminders.map((reminder) => (
        <Card
          key={reminder.id}
          className="p-4 bg-white/5 border-white/10 backdrop-blur-sm"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 space-y-2">
              {/* Reminder time */}
              <div className="flex items-center gap-2 text-white">
                <Bell className="h-4 w-4" />
                <span className="font-medium">
                  {format(new Date(reminder.reminder_time), "PPp")}
                </span>
              </div>

              {/* Timezone */}
              <div className="flex items-center gap-2 text-white/60 text-sm">
                <Globe className="h-3 w-3" />
                <span>{reminder.timezone}</span>
              </div>

              {/* Notification channels */}
              <div className="flex items-center gap-2 flex-wrap">
                {reminder.notification_channels.map((channel) => (
                  <Badge
                    key={channel}
                    variant="outline"
                    className="bg-white/5 border-white/20 text-white/80 text-xs"
                  >
                    <span className="mr-1">{getChannelIcon(channel)}</span>
                    {channel.replace("_", " ")}
                  </Badge>
                ))}
              </div>

              {/* Status */}
              <div>
                <Badge className={getStatusColor(reminder.status)}>
                  {reminder.status}
                </Badge>
              </div>

              {/* Last triggered */}
              {reminder.last_triggered_at && (
                <div className="text-xs text-white/40">
                  Last triggered:{" "}
                  {format(new Date(reminder.last_triggered_at), "PPp")}
                </div>
              )}
            </div>

            {/* Delete button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleDelete(reminder.id)}
              disabled={deletingId === reminder.id}
              className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </Card>
      ))}
    </div>
  )
}
