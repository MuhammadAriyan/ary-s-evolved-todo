"use client"

import { Area, AreaChart, XAxis, YAxis } from "recharts"
import { Info, ChartArea } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

interface TaskAnalyticsProps {
  taskData?: { day: string; count: number }[]
  totalTasks?: number
  completedTasks?: number
}

const chartConfig: ChartConfig = {
  count: {
    label: "Tasks",
    color: "#9929EA",
  },
}

export function TaskAnalyticsCard({ taskData, totalTasks = 0, completedTasks = 0 }: TaskAnalyticsProps) {
  // Generate mock data if no real data provided
  const data = taskData || Array.from({ length: 28 }, (_, i) => ({
    day: `Day ${i + 1}`,
    count: Math.floor(Math.random() * 10) + 1,
  }))

  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  return (
    <Card className="flex w-full flex-col gap-0 overflow-hidden p-0 shadow-none border-white/10 bg-black/30 backdrop-blur-xl">
      <CardHeader className="flex flex-row items-center justify-between px-5 pt-4.5 pb-0">
        <div className="flex flex-row items-center gap-1">
          <CardTitle className="text-base font-medium text-white/60">
            Task Activity
          </CardTitle>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger>
                <Info className="w-4 h-4 text-white/30" />
              </TooltipTrigger>
              <TooltipContent showArrow className="max-w-70">
                <p className="text-xs">
                  This chart shows your task activity for the last 28 days.
                  Track trends and optimize your productivity.
                </p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>
        <ChartArea className="h-5 w-5 text-white/40" />
      </CardHeader>

      <CardContent className="flex flex-col gap-4 p-0">
        <div className="flex items-center gap-3 px-5">
          <span className="text-2xl font-medium tracking-tight tabular-nums text-white">
            {totalTasks} Tasks
          </span>
          <Badge className="rounded-full bg-sky-cyan-500/20 text-xs text-sky-cyan-400 border-sky-cyan-500/30">
            Last 28 days
          </Badge>
        </div>

        <div className="grid h-[95px] grid-cols-[1fr_150px] border-t border-white/10">
          <ChartContainer
            config={chartConfig}
            className="aspect-auto h-auto w-full"
          >
            <AreaChart
              accessibilityLayer
              data={data}
              margin={{
                right: -5,
              }}
            >
              <XAxis hide />
              <YAxis hide domain={["dataMin - 2", "dataMax + 2"]} />
              <ChartTooltip
                content={
                  <ChartTooltipContent
                    formatter={(value) => `${value} tasks`}
                  />
                }
                cursor={{ stroke: "rgba(255,255,255,0.1)", strokeWidth: 1 }}
              />
              <Area
                type="linear"
                dataKey="count"
                stroke="#9929EA"
                fill="url(#gradient)"
                fillOpacity={0.3}
                strokeWidth={2}
                dot={false}
                activeDot={{
                  r: 4,
                  fill: "#9929EA",
                  stroke: "#000",
                  strokeWidth: 2,
                }}
              />
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#9929EA" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#9929EA" stopOpacity={0} />
                </linearGradient>
              </defs>
            </AreaChart>
          </ChartContainer>
          <div className="flex flex-col items-start justify-end border-l-2 border-sky-cyan-500 px-4 pb-4">
            <div className="text-sm font-semibold tracking-[-0.006em] text-white">
              {completionRate}%
            </div>
            <div className="text-xs font-medium tracking-[-0.006em] text-white/50">
              {completedTasks} completed
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default TaskAnalyticsCard
