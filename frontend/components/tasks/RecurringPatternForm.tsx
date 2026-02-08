/**
 * RecurringPatternForm Component
 * T114: Create recurring pattern form component
 * T115: Add preset patterns UI (daily, weekly, weekdays, monthly, custom cron)
 * T116: Add cron expression builder with visual preview
 */

"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Repeat, Calendar, Clock, Info } from "lucide-react"
import cronstrue from "cronstrue"

interface RecurringPatternFormProps {
  initialPattern?: string
  onPatternChange?: (pattern: string, description: string) => void
  onCancel?: () => void
}

// T115: Preset patterns for common recurring schedules
const PRESET_PATTERNS = [
  {
    name: "daily",
    label: "Daily at 9:00 AM",
    cron: "0 9 * * *",
    description: "Every day at 9:00 AM",
  },
  {
    name: "weekly",
    label: "Weekly on Monday",
    cron: "0 9 * * 1",
    description: "Every Monday at 9:00 AM",
  },
  {
    name: "weekdays",
    label: "Every Weekday",
    cron: "0 9 * * 1-5",
    description: "Monday through Friday at 9:00 AM",
  },
  {
    name: "monthly",
    label: "Monthly on 1st",
    cron: "0 9 1 * *",
    description: "First day of each month at 9:00 AM",
  },
  {
    name: "first_monday",
    label: "First Monday of Month",
    cron: "0 9 * * 1#1",
    description: "First Monday of each month at 9:00 AM",
  },
]

// T116: Cron builder options
const MINUTES = Array.from({ length: 60 }, (_, i) => i)
const HOURS = Array.from({ length: 24 }, (_, i) => i)
const DAYS_OF_MONTH = Array.from({ length: 31 }, (_, i) => i + 1)
const MONTHS = [
  { value: "*", label: "Every month" },
  { value: "1", label: "January" },
  { value: "2", label: "February" },
  { value: "3", label: "March" },
  { value: "4", label: "April" },
  { value: "5", label: "May" },
  { value: "6", label: "June" },
  { value: "7", label: "July" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "October" },
  { value: "11", label: "November" },
  { value: "12", label: "December" },
]
const DAYS_OF_WEEK = [
  { value: "*", label: "Every day" },
  { value: "1", label: "Monday" },
  { value: "2", label: "Tuesday" },
  { value: "3", label: "Wednesday" },
  { value: "4", label: "Thursday" },
  { value: "5", label: "Friday" },
  { value: "6", label: "Saturday" },
  { value: "0", label: "Sunday" },
  { value: "1-5", label: "Weekdays (Mon-Fri)" },
  { value: "0,6", label: "Weekends (Sat-Sun)" },
]

export function RecurringPatternForm({
  initialPattern = "",
  onPatternChange,
  onCancel,
}: RecurringPatternFormProps) {
  const [activeTab, setActiveTab] = useState<"preset" | "builder" | "custom">("preset")
  const [selectedPreset, setSelectedPreset] = useState("")
  const [customCron, setCustomCron] = useState(initialPattern)

  // T116: Cron builder state
  const [cronMinute, setCronMinute] = useState("0")
  const [cronHour, setCronHour] = useState("9")
  const [cronDayOfMonth, setCronDayOfMonth] = useState("*")
  const [cronMonth, setCronMonth] = useState("*")
  const [cronDayOfWeek, setCronDayOfWeek] = useState("*")

  const [currentPattern, setCurrentPattern] = useState(initialPattern)
  const [patternDescription, setPatternDescription] = useState("")
  const [validationError, setValidationError] = useState("")

  // T116: Generate cron expression from builder
  const generateCronFromBuilder = () => {
    return `${cronMinute} ${cronHour} ${cronDayOfMonth} ${cronMonth} ${cronDayOfWeek}`
  }

  // T116: Parse cron expression to human-readable description
  const parseCronDescription = (cron: string): string => {
    try {
      if (!cron || cron.trim() === "") {
        return "No pattern selected"
      }
      return cronstrue.toString(cron, { use24HourTimeFormat: true })
    } catch (error) {
      return "Invalid cron expression"
    }
  }

  // Update pattern when preset is selected
  useEffect(() => {
    if (activeTab === "preset" && selectedPreset) {
      const preset = PRESET_PATTERNS.find((p) => p.name === selectedPreset)
      if (preset) {
        setCurrentPattern(preset.cron)
        setPatternDescription(preset.description)
        setValidationError("")
      }
    }
  }, [activeTab, selectedPreset])

  // Update pattern when builder values change
  useEffect(() => {
    if (activeTab === "builder") {
      const cron = generateCronFromBuilder()
      setCurrentPattern(cron)
      setPatternDescription(parseCronDescription(cron))
      setValidationError("")
    }
  }, [activeTab, cronMinute, cronHour, cronDayOfMonth, cronMonth, cronDayOfWeek])

  // Update pattern when custom cron changes
  useEffect(() => {
    if (activeTab === "custom") {
      setCurrentPattern(customCron)
      const description = parseCronDescription(customCron)
      setPatternDescription(description)

      // Basic validation
      if (customCron && description === "Invalid cron expression") {
        setValidationError("Invalid cron expression format")
      } else {
        setValidationError("")
      }
    }
  }, [activeTab, customCron])

  const handleApply = () => {
    if (!currentPattern) {
      setValidationError("Please select or create a recurring pattern")
      return
    }

    if (validationError) {
      return
    }

    onPatternChange?.(currentPattern, patternDescription)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-text-tertiary">
        <Repeat className="h-4 w-4" />
        <span>Configure Recurring Pattern</span>
      </div>

      {/* T115: Tabs for preset, builder, and custom */}
      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="preset">Presets</TabsTrigger>
          <TabsTrigger value="builder">Builder</TabsTrigger>
          <TabsTrigger value="custom">Custom</TabsTrigger>
        </TabsList>

        {/* T115: Preset patterns tab */}
        <TabsContent value="preset" className="space-y-3">
          <div className="grid gap-2">
            {PRESET_PATTERNS.map((preset) => (
              <button
                key={preset.name}
                type="button"
                onClick={() => setSelectedPreset(preset.name)}
                className={`
                  p-3 rounded-lg border text-left transition-all
                  ${
                    selectedPreset === preset.name
                      ? "border-sky-cyan-500 bg-sky-cyan-500/10"
                      : "border-white/20 bg-white/5 hover:bg-white/10"
                  }
                `}
              >
                <div className="font-medium text-white">{preset.label}</div>
                <div className="text-sm text-white/60 mt-1">{preset.description}</div>
                <div className="text-xs text-white/40 mt-1 font-mono">{preset.cron}</div>
              </button>
            ))}
          </div>
        </TabsContent>

        {/* T116: Cron expression builder tab */}
        <TabsContent value="builder" className="space-y-4">
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-2">
                <Label htmlFor="cron-hour" className="flex items-center gap-2">
                  <Clock className="h-4 w-4" />
                  Hour
                </Label>
                <Select value={cronHour} onValueChange={setCronHour}>
                  <SelectTrigger className="bg-white/10 border-white/20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="*">Every hour</SelectItem>
                    {HOURS.map((h) => (
                      <SelectItem key={h} value={h.toString()}>
                        {h.toString().padStart(2, "0")}:00
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="cron-minute">Minute</Label>
                <Select value={cronMinute} onValueChange={setCronMinute}>
                  <SelectTrigger className="bg-white/10 border-white/20">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="0">:00</SelectItem>
                    <SelectItem value="15">:15</SelectItem>
                    <SelectItem value="30">:30</SelectItem>
                    <SelectItem value="45">:45</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cron-day-of-week" className="flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                Day of Week
              </Label>
              <Select value={cronDayOfWeek} onValueChange={setCronDayOfWeek}>
                <SelectTrigger className="bg-white/10 border-white/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {DAYS_OF_WEEK.map((day) => (
                    <SelectItem key={day.value} value={day.value}>
                      {day.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cron-day-of-month">Day of Month</Label>
              <Select value={cronDayOfMonth} onValueChange={setCronDayOfMonth}>
                <SelectTrigger className="bg-white/10 border-white/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="*">Every day</SelectItem>
                  {DAYS_OF_MONTH.map((d) => (
                    <SelectItem key={d} value={d.toString()}>
                      {d}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cron-month">Month</Label>
              <Select value={cronMonth} onValueChange={setCronMonth}>
                <SelectTrigger className="bg-white/10 border-white/20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MONTHS.map((month) => (
                    <SelectItem key={month.value} value={month.value}>
                      {month.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </TabsContent>

        {/* T116: Custom cron expression tab */}
        <TabsContent value="custom" className="space-y-3">
          <div className="space-y-2">
            <Label htmlFor="custom-cron">Cron Expression</Label>
            <Input
              id="custom-cron"
              type="text"
              value={customCron}
              onChange={(e) => setCustomCron(e.target.value)}
              placeholder="0 9 * * 1-5"
              className="bg-white/10 border-white/20 text-white font-mono"
            />
            <div className="text-xs text-white/50">
              Format: minute hour day-of-month month day-of-week
            </div>
          </div>

          <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <div className="flex items-start gap-2">
              <Info className="h-4 w-4 text-blue-400 mt-0.5" />
              <div className="text-xs text-blue-300">
                <div className="font-medium mb-1">Examples:</div>
                <div className="space-y-1 font-mono">
                  <div>0 9 * * * - Daily at 9:00 AM</div>
                  <div>0 */4 * * * - Every 4 hours</div>
                  <div>0 9 * * 1-5 - Weekdays at 9:00 AM</div>
                  <div>0 9 1 * * - Monthly on 1st at 9:00 AM</div>
                </div>
              </div>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* T116: Visual preview of pattern */}
      {currentPattern && (
        <div className="p-4 rounded-lg bg-white/5 border border-white/10">
          <div className="text-sm font-medium text-text-tertiary mb-2">Preview:</div>
          <div className="text-white">{patternDescription}</div>
          <div className="text-xs text-white/40 mt-2 font-mono">{currentPattern}</div>
        </div>
      )}

      {/* Validation error */}
      {validationError && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {validationError}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex gap-2">
        <Button
          type="button"
          onClick={handleApply}
          disabled={!currentPattern || !!validationError}
          className="flex-1"
        >
          Apply Pattern
        </Button>
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>
    </div>
  )
}
