# Research: Full-Stack Web Application Technologies

**Feature**: 001-fullstack-web-app
**Date**: 2026-01-06
**Status**: Completed

## Overview

This document consolidates research findings for key technologies and integration patterns required for the full-stack web todo application. All research topics identified in plan.md have been investigated and decisions documented.

---

## 1. Better Auth + FastAPI JWT Integration

### Decision
Use shared JWT secret between Better Auth (frontend) and FastAPI (backend) for stateless token verification. Better Auth generates JWT tokens with HS256 algorithm, FastAPI verifies using PyJWT library.

### Rationale
- **Stateless**: No session storage required, enables horizontal scaling
- **Standard**: JWT is industry-standard for API authentication
- **Simple**: Shared secret approach is straightforward to implement and maintain
- **Secure**: HS256 with 32+ character secret provides adequate security for this use case

### Implementation Pattern

**Frontend (Better Auth Configuration)**:
```typescript
// frontend/lib/auth.ts
import { betterAuth } from "better-auth";
import { jwtPlugin } from "better-auth/plugins";

export const auth = betterAuth({
  database: {
    provider: "postgres",
    url: process.env.DATABASE_URL,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Set true in production
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
  },
  plugins: [
    jwtPlugin({
      secret: process.env.BETTER_AUTH_SECRET!,
      expiresIn: "24h",
      algorithm: "HS256",
    }),
  ],
  secret: process.env.BETTER_AUTH_SECRET!,
});
```

**Backend (JWT Verification)**:
```python
# backend/app/utils/jwt.py
import jwt
from jwt.exceptions import InvalidTokenError
from app.config import settings

def verify_token(token: str) -> str | None:
    """Verify JWT token and extract user_id."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,  # MUST match BETTER_AUTH_SECRET
            algorithms=["HS256"]
        )
        return payload.get("sub")  # user_id
    except InvalidTokenError:
        return None
```

**Environment Variables**:
- Frontend: `BETTER_AUTH_SECRET=<32-char-secret>`
- Backend: `JWT_SECRET_KEY=<32-char-secret>` (MUST be identical)

### Alternatives Considered
- **OAuth2 Password Flow**: More complex, requires token endpoint on backend
- **Session-based Auth**: Requires session storage, not horizontally scalable
- **Asymmetric JWT (RS256)**: Overkill for this use case, adds key management complexity

### References
- Better Auth JWT Plugin: https://www.better-auth.com/docs/plugins/jwt
- PyJWT Documentation: https://pyjwt.readthedocs.io/

---

## 2. Neon PostgreSQL Connection Pooling

### Decision
Use SQLModel with connection pooling configured for Neon's serverless architecture. Pool size: 5, max overflow: 10, pool_pre_ping: true, pool_recycle: 3600 seconds.

### Rationale
- **Neon Limits**: Free tier supports up to 100 concurrent connections
- **Efficiency**: Connection pooling reduces overhead of creating new connections
- **Reliability**: pool_pre_ping ensures connections are valid before use
- **Lifecycle**: pool_recycle prevents stale connections (Neon closes idle connections after 5 minutes)

### Implementation Pattern

```python
# backend/app/database.py
from sqlmodel import create_engine, Session
from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=False,  # Disable SQL logging in production
    pool_size=5,  # Maintain 5 persistent connections
    max_overflow=10,  # Allow up to 15 total connections (5 + 10)
    pool_pre_ping=True,  # Verify connection before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "sslmode": "require",  # Neon requires SSL
        "connect_timeout": 10,  # 10 second connection timeout
    }
)

def get_db():
    """Database session dependency for FastAPI."""
    with Session(engine) as session:
        yield session
```

### Configuration Recommendations
- **Development**: pool_size=2, max_overflow=3 (lower resource usage)
- **Production**: pool_size=5, max_overflow=10 (handles traffic spikes)
- **High Traffic**: pool_size=10, max_overflow=20 (requires paid Neon tier)

### Alternatives Considered
- **No Pooling**: Simple but inefficient, creates new connection per request
- **PgBouncer**: External connection pooler, adds deployment complexity
- **Neon Pooler**: Neon's built-in pooler, but SQLModel pooling is sufficient for this scale

### References
- Neon Connection Pooling: https://neon.tech/docs/connect/connection-pooling
- SQLAlchemy Engine Configuration: https://docs.sqlalchemy.org/en/20/core/engines.html

---

## 3. APScheduler Reliability for Recurring Tasks

### Decision
Use APScheduler with BackgroundScheduler, run job every minute, implement idempotency checks to prevent duplicate task creation, add comprehensive logging.

### Rationale
- **Simplicity**: APScheduler is lightweight and easy to integrate with FastAPI
- **Frequency**: Running every minute ensures tasks are created within 1 minute of due time
- **Idempotency**: Prevents duplicate tasks if scheduler runs multiple times
- **Logging**: Enables debugging and monitoring of scheduler execution

### Implementation Pattern

```python
# backend/app/jobs/recurring_tasks.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select
from app.database import engine
from app.models.task import Task
import logging

logger = logging.getLogger(__name__)

def generate_recurring_tasks():
    """Generate next occurrence of recurring tasks."""
    try:
        with Session(engine) as db:
            today = datetime.now().date()

            # Find recurring tasks that are due
            recurring_tasks = db.exec(
                select(Task).where(
                    Task.recurring.isnot(None),
                    Task.due_date <= today
                )
            ).all()

            for task in recurring_tasks:
                # Calculate next due date
                next_due = calculate_next_due_date(task.due_date, task.recurring)

                # Check if next occurrence already exists (idempotency)
                existing = db.exec(
                    select(Task).where(
                        Task.user_id == task.user_id,
                        Task.title == task.title,
                        Task.due_date == next_due,
                        Task.recurring == task.recurring
                    )
                ).first()

                if not existing:
                    # Create new task instance
                    new_task = Task(
                        user_id=task.user_id,
                        title=task.title,
                        description=task.description,
                        priority=task.priority,
                        tags=task.tags,
                        due_date=next_due,
                        recurring=task.recurring,
                        completed=False
                    )
                    db.add(new_task)
                    logger.info(f"Created recurring task: {task.title} for {next_due}")

            db.commit()
            logger.info(f"Recurring task generation completed at {datetime.now()}")

    except Exception as e:
        logger.error(f"Error generating recurring tasks: {e}")

def calculate_next_due_date(current_due: date, pattern: str) -> date:
    """Calculate next due date based on recurring pattern."""
    if pattern == "daily":
        return current_due + timedelta(days=1)
    elif pattern == "weekly":
        return current_due + timedelta(weeks=1)
    elif pattern == "monthly":
        return current_due + relativedelta(months=1)
    else:
        raise ValueError(f"Invalid recurring pattern: {pattern}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    generate_recurring_tasks,
    'interval',
    minutes=1,  # Run every minute
    id='recurring_tasks',
    replace_existing=True
)

def start_scheduler():
    """Start the scheduler (called on app startup)."""
    if not scheduler.running:
        scheduler.start()
        logger.info("APScheduler started")

def stop_scheduler():
    """Stop the scheduler (called on app shutdown)."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped")
```

**FastAPI Integration**:
```python
# backend/app/main.py
from app.jobs.recurring_tasks import start_scheduler, stop_scheduler

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()
```

### Alternatives Considered
- **Celery + Redis**: More robust but adds infrastructure complexity (deferred to Phase V)
- **Cron Jobs**: External scheduler, requires separate process management
- **Database Triggers**: Complex to implement and maintain

### References
- APScheduler Documentation: https://apscheduler.readthedocs.io/
- FastAPI Background Tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/

---

## 4. shadcn/ui + Tailwind CSS Setup

### Decision
Use shadcn/ui CLI to install components on-demand, configure Tailwind with custom theme extending default palette, use CSS variables for theme customization.

### Rationale
- **Flexibility**: Install only needed components, reduces bundle size
- **Customization**: CSS variables enable easy theme adjustments
- **Accessibility**: shadcn/ui components are built on Radix UI (WCAG compliant)
- **Developer Experience**: Well-documented, TypeScript-first, copy-paste friendly

### Implementation Pattern

**Installation**:
```bash
# Initialize shadcn/ui
npx shadcn-ui@latest init

# Install required components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add input
npx shadcn-ui@latest add textarea
npx shadcn-ui@latest add select
npx shadcn-ui@latest add checkbox
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add calendar
npx shadcn-ui@latest add popover
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add scroll-area
```

**Tailwind Configuration**:
```typescript
// frontend/tailwind.config.ts
import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
```

### Alternatives Considered
- **Material-UI**: Heavier bundle, more opinionated styling
- **Chakra UI**: Good but less flexible than shadcn/ui
- **Headless UI**: Lower-level, requires more custom styling

### References
- shadcn/ui Documentation: https://ui.shadcn.com/
- Tailwind CSS Documentation: https://tailwindcss.com/docs

---

## 5. TanStack Query Optimistic Updates

### Decision
Use TanStack Query mutations with optimistic updates for create/update/delete operations, implement rollback on error, invalidate queries on success.

### Rationale
- **UX**: Immediate feedback to users, app feels faster
- **Reliability**: Automatic rollback if mutation fails
- **Caching**: TanStack Query handles cache invalidation automatically
- **Type Safety**: Full TypeScript support

### Implementation Pattern

```typescript
// frontend/hooks/useTasks.ts
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";
import type { Task, CreateTaskInput, UpdateTaskInput } from "@/types/task";

// Query key factory
const taskKeys = {
  all: ["tasks"] as const,
  lists: () => [...taskKeys.all, "list"] as const,
  list: (filters?: Record<string, any>) => [...taskKeys.lists(), filters] as const,
  details: () => [...taskKeys.all, "detail"] as const,
  detail: (id: number) => [...taskKeys.details(), id] as const,
};

// List tasks query
export function useTasks(filters?: Record<string, any>) {
  return useQuery({
    queryKey: taskKeys.list(filters),
    queryFn: () => apiClient.getTasks(filters),
  });
}

// Create task mutation with optimistic update
export function useCreateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateTaskInput) => apiClient.createTask(data),
    onMutate: async (newTask) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData(taskKeys.list());

      // Optimistically update cache
      queryClient.setQueryData(taskKeys.list(), (old: Task[] = []) => [
        ...old,
        { ...newTask, id: Date.now(), completed: false, created_at: new Date().toISOString() },
      ]);

      return { previousTasks };
    },
    onError: (err, newTask, context) => {
      // Rollback on error
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.list(), context.previousTasks);
      }
    },
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}

// Update task mutation with optimistic update
export function useUpdateTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateTaskInput }) =>
      apiClient.updateTask(id, data),
    onMutate: async ({ id, data }) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });

      const previousTasks = queryClient.getQueryData(taskKeys.list());

      queryClient.setQueryData(taskKeys.list(), (old: Task[] = []) =>
        old.map((task) => (task.id === id ? { ...task, ...data } : task))
      );

      return { previousTasks };
    },
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.list(), context.previousTasks);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}

// Delete task mutation with optimistic update
export function useDeleteTask() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => apiClient.deleteTask(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });

      const previousTasks = queryClient.getQueryData(taskKeys.list());

      queryClient.setQueryData(taskKeys.list(), (old: Task[] = []) =>
        old.filter((task) => task.id !== id)
      );

      return { previousTasks };
    },
    onError: (err, id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.list(), context.previousTasks);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}

// Toggle complete mutation
export function useToggleComplete() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => apiClient.toggleComplete(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: taskKeys.lists() });

      const previousTasks = queryClient.getQueryData(taskKeys.list());

      queryClient.setQueryData(taskKeys.list(), (old: Task[] = []) =>
        old.map((task) =>
          task.id === id ? { ...task, completed: !task.completed } : task
        )
      );

      return { previousTasks };
    },
    onError: (err, id, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(taskKeys.list(), context.previousTasks);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskKeys.lists() });
    },
  });
}
```

### Alternatives Considered
- **SWR**: Similar to TanStack Query but less feature-rich
- **Redux Toolkit Query**: More complex setup, overkill for this use case
- **Manual State Management**: Error-prone, requires custom caching logic

### References
- TanStack Query Documentation: https://tanstack.com/query/latest
- Optimistic Updates Guide: https://tanstack.com/query/latest/docs/react/guides/optimistic-updates

---

## 6. React Big Calendar Integration

### Decision
Use react-big-calendar with moment.js for date handling, customize with Tailwind CSS classes, map tasks to calendar events by due_date.

### Rationale
- **Feature-Rich**: Supports month/week/day views, event rendering, navigation
- **Customizable**: Accepts custom components and styling
- **Maintained**: Active development, good community support
- **TypeScript**: Full type definitions available

### Implementation Pattern

```typescript
// frontend/app/(protected)/todo/components/CalendarView.tsx
"use client";

import { Calendar, momentLocalizer, Event } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { useTasks } from "@/hooks/useTasks";
import type { Task } from "@/types/task";

const localizer = momentLocalizer(moment);

interface CalendarEvent extends Event {
  task: Task;
}

export function CalendarView() {
  const { data: tasks = [], isLoading } = useTasks();

  // Map tasks to calendar events
  const events: CalendarEvent[] = tasks
    .filter((task) => task.due_date)
    .map((task) => ({
      title: task.title,
      start: new Date(task.due_date!),
      end: new Date(task.due_date!),
      task,
    }));

  if (isLoading) {
    return <div className="animate-pulse h-96 bg-muted rounded-lg" />;
  }

  return (
    <div className="h-[600px] bg-card rounded-lg p-4 shadow-sm">
      <Calendar
        localizer={localizer}
        events={events}
        startAccessor="start"
        endAccessor="end"
        style={{ height: "100%" }}
        views={["month"]}
        defaultView="month"
        onSelectEvent={(event: CalendarEvent) => {
          // Open task details modal
          console.log("Selected task:", event.task);
        }}
        eventPropGetter={(event: CalendarEvent) => ({
          className: `
            ${event.task.completed ? "opacity-50 line-through" : ""}
            ${event.task.priority === "High" ? "bg-red-500" : ""}
            ${event.task.priority === "Medium" ? "bg-yellow-500" : ""}
            ${event.task.priority === "Low" ? "bg-green-500" : ""}
          `,
        })}
      />
    </div>
  );
}
```

**Custom Styling**:
```css
/* frontend/app/globals.css */
.rbc-calendar {
  @apply font-sans;
}

.rbc-header {
  @apply bg-muted text-foreground font-semibold py-2;
}

.rbc-today {
  @apply bg-accent/20;
}

.rbc-event {
  @apply rounded px-2 py-1 text-xs font-medium;
}

.rbc-event:hover {
  @apply opacity-80 cursor-pointer;
}
```

### Alternatives Considered
- **FullCalendar**: More features but heavier bundle, requires license for commercial use
- **Custom Calendar**: Too much effort to build from scratch
- **react-calendar**: Simpler but lacks event rendering features

### References
- react-big-calendar Documentation: https://jquense.github.io/react-big-calendar/
- Moment.js Documentation: https://momentjs.com/docs/

---

## Summary

All research topics have been investigated and implementation patterns documented. Key decisions:

1. **Authentication**: Shared JWT secret between Better Auth and FastAPI
2. **Database**: SQLModel with connection pooling optimized for Neon
3. **Scheduler**: APScheduler with idempotency checks, runs every minute
4. **UI Components**: shadcn/ui with Tailwind CSS, on-demand installation
5. **State Management**: TanStack Query with optimistic updates
6. **Calendar**: react-big-calendar with Tailwind styling

All patterns are production-ready and align with constitution requirements. Ready to proceed to Phase 1 (Design & Contracts).

---

**Research Status**: ✅ Complete
**Next Phase**: Phase 1 - Generate data-model.md, contracts/, quickstart.md
