/**
 * ReminderForm Component
 * T068: Create reminder form component
 * T073: Add timezone selector in reminder form
 */

"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useCreateReminder } from "@/hooks/useReminders"
import { Bell, Calendar, Clock, Globe } from "lucide-react"

interface ReminderFormProps {
  taskId: string
  onSuccess?: () => void
  onCancel?: () => void
}

// Common timezones
const TIMEZONES = [
  { value: "UTC", label: "UTC" },
  { value: "America/New_York", label: "Eastern Time (ET)" },
  { value: "America/Chicago", label: "Central Time (CT)" },
  { value: "America/Denver", label: "Mountain Time (MT)" },
  { value: "America/Los_Angeles", label: "Pacific Time (PT)" },
  { value: "Europe/London", label: "London (GMT)" },
  { value: "Europe/Paris", label: "Paris (CET)" },
  { value: "Asia/Tokyo", label: "Tokyo (JST)" },
  { value: "Asia/Shanghai", label: "Shanghai (CST)" },
  { value: "Asia/Dubai", label: "Dubai (GST)" },
  { value: "Australia/Sydney", label: "Sydney (AEDT)" },
]

export function ReminderForm({ taskId, onSuccess, onCancel }: ReminderFormProps) {
  const [reminderDate, setReminderDate] = useState("")
  const [reminderTime, setReminderTime] = useState("")
  const [timezone, setTimezone] = useState("UTC")
  const [channels, setChannels] = useState({
    in_app: true,
    email: false,
    push: false,
  })

  const createReminder = useCreateReminder()

  // T073: Detect user's timezone on mount
  useEffect(() => {
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    setTimezone(userTimezone)
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!reminderDate || !reminderTime) {
      alert("Please select both date and time")
      return
    }

    // Combine date and time
    const reminderDateTime = `${reminderDate}T${reminderTime}:00`

    // Get selected channels
    const selectedChannels = Object.entries(channels)
      .filter(([_, enabled]) => enabled)
      .map(([channel]) => channel)

    if (selectedChannels.length === 0) {
      alert("Please select at least one notification channel")
      return
    }

    try {
      await createReminder.mutateAsync({
        task_id: taskId,
        reminder_time: reminderDateTime,
        timezone,
        notification_channels: selectedChannels,
      })

      // Reset form
      setReminderDate("")
      setReminderTime("")
      setChannels({ in_app: true, email: false, push: false })

      onSuccess?.()
    } catch (error) {
      console.error("Error creating reminder:", error)
      alert("Failed to create reminder")
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="reminder-date" className="flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          Date
        </Label>
        <Input
          id="reminder-date"
          type="date"
          value={reminderDate}
          onChange={(e) => setReminderDate(e.target.value)}
          required
          className="bg-white/10 border-white/20 text-white"
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="reminder-time" className="flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Time
        </Label>
        <Input
          id="reminder-time"
          type="time"
          value={reminderTime}
          onChange={(e) => setReminderTime(e.target.value)}
          required
          className="bg-white/10 border-white/20 text-white"
        />
      </div>

      {/* T073: Timezone selector */}
      <div className="space-y-2">
        <Label htmlFor="timezone" className="flex items-center gap-2">
          <Globe className="h-4 w-4" />
          Timezone
        </Label>
        <Select value={timezone} onValueChange={setTimezone}>
          <SelectTrigger className="bg-white/10 border-white/20 text-white">
            <SelectValue placeholder="Select timezone" />
          </SelectTrigger>
          <SelectContent>
            {TIMEZONES.map((tz) => (
              <SelectItem key={tz.value} value={tz.value}>
                {tz.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label className="flex items-center gap-2">
          <Bell className="h-4 w-4" />
          Notification Channels
        </Label>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <Checkbox
              id="channel-in-app"
              checked={channels.in_app}
              onCheckedChange={(checked) =>
                setChannels({ ...channels, in_app: checked as boolean })
              }
            />
            <Label htmlFor="channel-in-app" className="cursor-pointer">
              In-App Notification
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="channel-email"
              checked={channels.email}
              onCheckedChange={(checked) =>
                setChannels({ ...channels, email: checked as boolean })
              }
            />
            <Label htmlFor="channel-email" className="cursor-pointer">
              Email
            </Label>
          </div>
          <div className="flex items-center space-x-2">
            <Checkbox
              id="channel-push"
              checked={channels.push}
              onCheckedChange={(checked) =>
                setChannels({ ...channels, push: checked as boolean })
              }
            />
            <Label htmlFor="channel-push" className="cursor-pointer">
              Push Notification (Coming Soon)
            </Label>
          </div>
        </div>
      </div>

      <div className="flex gap-2">
        <Button
          type="submit"
          disabled={createReminder.isPending}
          className="flex-1"
        >
          {createReminder.isPending ? "Creating..." : "Create Reminder"}
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </form>
  )
}
