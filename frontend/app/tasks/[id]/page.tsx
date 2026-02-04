/**
 * Task Detail Page with Reminder Scheduling
 * T069: Add reminder scheduling UI to task detail page
 */

"use client"

import { useState } from "react"
import { useParams } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Bell, Plus } from "lucide-react"
import { ReminderForm } from "@/components/tasks/ReminderForm"
import { ReminderList } from "@/components/tasks/ReminderList"
import { useNotificationPermission } from "@/hooks/useReminders"

export default function TaskDetailPage() {
  const params = useParams()
  const taskId = params.id as string
  const [showReminderForm, setShowReminderForm] = useState(false)
  const { permission, requestPermission } = useNotificationPermission()

  // T071: Request notification permission on first interaction
  const handleAddReminder = async () => {
    if (permission !== "granted") {
      const granted = await requestPermission()
      if (!granted) {
        alert(
          "Please enable notifications in your browser settings to receive reminders"
        )
        return
      }
    }
    setShowReminderForm(true)
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <Card className="bg-white/5 border-white/10 backdrop-blur-sm p-6">
        <Tabs defaultValue="details" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="reminders">
              <Bell className="h-4 w-4 mr-2" />
              Reminders
            </TabsTrigger>
            <TabsTrigger value="comments">Comments</TabsTrigger>
          </TabsList>

          <TabsContent value="details" className="space-y-4">
            {/* Task details would go here */}
            <div className="text-white">
              <h2 className="text-2xl font-bold mb-4">Task Details</h2>
              <p className="text-white/60">Task ID: {taskId}</p>
            </div>
          </TabsContent>

          {/* T069: Reminder scheduling UI */}
          <TabsContent value="reminders" className="space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-white">Reminders</h2>
              {!showReminderForm && (
                <Button onClick={handleAddReminder} size="sm">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Reminder
                </Button>
              )}
            </div>

            {/* T068: Reminder form */}
            {showReminderForm && (
              <Card className="bg-white/5 border-white/10 backdrop-blur-sm p-4 mb-4">
                <h3 className="text-lg font-semibold text-white mb-4">
                  Schedule New Reminder
                </h3>
                <ReminderForm
                  taskId={taskId}
                  onSuccess={() => setShowReminderForm(false)}
                  onCancel={() => setShowReminderForm(false)}
                />
              </Card>
            )}

            {/* T072: Reminder list */}
            <ReminderList taskId={taskId} />
          </TabsContent>

          <TabsContent value="comments" className="space-y-4">
            <div className="text-white">
              <h2 className="text-2xl font-bold mb-4">Comments</h2>
              <p className="text-white/60">Comments feature coming soon...</p>
            </div>
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  )
}
