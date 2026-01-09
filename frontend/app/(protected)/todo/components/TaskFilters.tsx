"use client"

import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

interface TaskFiltersProps {
  activeFilter: "all" | "pending" | "completed"
  onFilterChange: (filter: "all" | "pending" | "completed") => void
}

export function TaskFilters({ activeFilter, onFilterChange }: TaskFiltersProps) {
  return (
    <Tabs value={activeFilter} onValueChange={(v) => onFilterChange(v as "all" | "pending" | "completed")}>
      <TabsList>
        <TabsTrigger value="all">All</TabsTrigger>
        <TabsTrigger value="pending">Pending</TabsTrigger>
        <TabsTrigger value="completed">Completed</TabsTrigger>
      </TabsList>
    </Tabs>
  )
}
