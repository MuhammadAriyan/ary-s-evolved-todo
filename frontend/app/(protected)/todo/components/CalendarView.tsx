"use client"

import { useState, useCallback } from "react"
import { Calendar, momentLocalizer, Event, View, NavigateAction } from "react-big-calendar"
import moment from "moment"
import { Task } from "@/types/task"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { CalendarDays } from "lucide-react"
import "react-big-calendar/lib/css/react-big-calendar.css"

const localizer = momentLocalizer(moment)

interface CalendarViewProps {
  tasks: Task[]
  onEventClick: (task: Task) => void
}

interface CalendarEvent extends Event {
  task: Task
}

// Custom messages to rename Day to Today
const messages = {
  day: "Today",
  week: "Week",
  month: "Month",
  previous: "Back",
  next: "Next",
  today: "Today",
  agenda: "Agenda",
}

// Custom toolbar with Today button for navigation
function CustomToolbar({ label, onNavigate, onView, view }: any) {
  return (
    <div className="rbc-toolbar">
      <span className="rbc-btn-group">
        <button type="button" onClick={() => onNavigate("PREV")}>
          Back
        </button>
        <button type="button" onClick={() => onNavigate("TODAY")}>
          Today
        </button>
        <button type="button" onClick={() => onNavigate("NEXT")}>
          Next
        </button>
      </span>
      <span className="rbc-toolbar-label">{label}</span>
      <span className="rbc-btn-group">
        <button
          type="button"
          className={view === "month" ? "rbc-active" : ""}
          onClick={() => onView("month")}
        >
          Month
        </button>
        <button
          type="button"
          className={view === "week" ? "rbc-active" : ""}
          onClick={() => onView("week")}
        >
          Week
        </button>
        <button
          type="button"
          className={view === "day" ? "rbc-active" : ""}
          onClick={() => onView("day")}
        >
          Day
        </button>
      </span>
    </div>
  )
}

export function CalendarView({ tasks, onEventClick }: CalendarViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [currentView, setCurrentView] = useState<View>("month")

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
    let backgroundColor = "#9929EA" // Purple theme color

    if (task.completed) {
      backgroundColor = "rgba(153, 41, 234, 0.4)"
    } else if (task.priority === "High") {
      backgroundColor = "#ef4444" // Red for high priority
    } else if (task.priority === "Medium") {
      backgroundColor = "#9929EA" // Purple for medium
    } else if (task.priority === "Low") {
      backgroundColor = "rgba(153, 41, 234, 0.6)" // Lighter purple for low
    }

    return {
      style: {
        backgroundColor,
        borderRadius: "4px",
        opacity: task.completed ? 0.6 : 1,
        color: "white",
        border: "none",
        fontSize: "0.75rem",
        padding: "2px 4px",
      },
    }
  }

  // Handle event selection
  const handleSelectEvent = (event: CalendarEvent) => {
    onEventClick(event.task)
  }

  // Handle navigation (Back, Next)
  const handleNavigate = useCallback((newDate: Date, view: View, action: NavigateAction) => {
    setCurrentDate(newDate)
  }, [])

  // Handle view change (Month, Week, Today)
  const handleViewChange = useCallback((view: View) => {
    // When switching to "day" view, set date to today
    if (view === "day") {
      setCurrentDate(new Date())
    }
    setCurrentView(view)
  }, [])

  if (events.length === 0) {
    return (
      <Card className="h-96 flex items-center justify-center">
        <div className="text-center">
          <CalendarDays className="h-12 w-12 text-sky-cyan-500/50 mx-auto mb-4" />
          <p className="font-medium text-white">No tasks with due dates</p>
          <p className="mt-1 text-sm text-white/50">
            Add due dates to your tasks to see them on the calendar
          </p>
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="text-base font-medium flex items-center gap-2">
          <CalendarDays className="h-4 w-4" />
          Calendar View
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Calendar
          localizer={localizer}
          events={events}
          startAccessor="start"
          endAccessor="end"
          style={{ height: 500 }}
          eventPropGetter={eventStyleGetter}
          onSelectEvent={handleSelectEvent}
          views={["month", "week", "day"]}
          view={currentView}
          date={currentDate}
          onNavigate={handleNavigate}
          onView={handleViewChange}
          messages={messages}
          components={{
            toolbar: CustomToolbar,
          }}
          popup
        />
      </CardContent>
    </Card>
  )
}
