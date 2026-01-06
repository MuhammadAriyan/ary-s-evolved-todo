"use client"

import { Calendar, momentLocalizer, Event } from "react-big-calendar"
import moment from "moment"
import { Task } from "@/types/task"
import "react-big-calendar/lib/css/react-big-calendar.css"

const localizer = momentLocalizer(moment)

interface CalendarViewProps {
  tasks: Task[]
  onEventClick: (task: Task) => void
}

interface CalendarEvent extends Event {
  task: Task
}

export function CalendarView({ tasks, onEventClick }: CalendarViewProps) {
  // Map tasks to calendar events
  const events: CalendarEvent[] = tasks
    .filter((task) => task.due_date)
    .map((task) => ({
      title: task.title,
      start: new Date(task.due_date!),
      end: new Date(task.due_date!),
      allDay: true,
      task,
    }))

  // Custom event style based on priority and completion
  const eventStyleGetter = (event: CalendarEvent) => {
    const { task } = event
    let backgroundColor = "#3b82f6" // Default blue

    if (task.completed) {
      backgroundColor = "#10b981" // Green for completed
    } else if (task.priority === "High") {
      backgroundColor = "#ef4444" // Red for high priority
    } else if (task.priority === "Medium") {
      backgroundColor = "#f59e0b" // Orange for medium priority
    } else if (task.priority === "Low") {
      backgroundColor = "#6b7280" // Gray for low priority
    }

    return {
      style: {
        backgroundColor,
        borderRadius: "6px",
        opacity: task.completed ? 0.6 : 1,
        color: "white",
        border: "none",
        display: "block",
        fontSize: "0.875rem",
        padding: "2px 6px",
      },
    }
  }

  // Handle event selection
  const handleSelectEvent = (event: CalendarEvent) => {
    onEventClick(event.task)
  }

  if (events.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50">
        <div className="text-center">
          <p className="text-lg font-medium text-gray-900">No tasks with due dates</p>
          <p className="mt-2 text-sm text-gray-600">
            Add due dates to your tasks to see them on the calendar
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="calendar-container rounded-lg bg-white p-4 shadow-sm">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: 600 }}
        eventPropGetter={eventStyleGetter}
        onSelectEvent={handleSelectEvent}
        views={["month", "week", "day", "agenda"]}
        defaultView="month"
        popup
        className="custom-calendar"
      />
    </div>
  )
}
