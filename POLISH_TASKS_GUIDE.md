# Phase 8 Polish Tasks - Implementation Guide

## Overview

This guide provides implementation guidance for the remaining polish and cross-cutting tasks (T161-T170, T174-T175) in Phase 8.

## T161: Error Boundary Components

### Implementation

Create error boundary component in `frontend/components/error-boundary.tsx`:

```typescript
'use client';

import React from 'react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service (e.g., Sentry)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Something went wrong</h2>
            <p className="text-gray-600 mb-4">We're sorry for the inconvenience.</p>
            <button
              onClick={() => this.setState({ hasError: false })}
              className="px-4 py-2 bg-blue-500 text-white rounded"
            >
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Usage

Wrap components in layout:

```typescript
// app/layout.tsx
import { ErrorBoundary } from '@/components/error-boundary';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}
```

## T162: Loading States and Skeletons

### Implementation

Create skeleton components in `frontend/components/ui/skeleton.tsx`:

```typescript
export function TaskSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
    </div>
  );
}

export function TaskListSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <TaskSkeleton key={i} />
      ))}
    </div>
  );
}
```

### Usage

```typescript
// app/tasks/page.tsx
import { Suspense } from 'react';
import { TaskListSkeleton } from '@/components/ui/skeleton';

export default function TasksPage() {
  return (
    <Suspense fallback={<TaskListSkeleton />}>
      <TaskList />
    </Suspense>
  );
}
```

## T163: Rate Limiting Middleware

### Implementation

Create rate limiter in `backend/app/middleware/rate_limit.py`:

```python
from fastapi import Request, HTTPException
from dapr.clients import DaprClient
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting using Redis state store"""

    def __init__(self, store_name: str = "redis-state"):
        self.store_name = store_name

    async def check_rate_limit(
        self,
        user_id: str,
        limit: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """Check if user has exceeded rate limit"""
        async with DaprClient() as client:
            key = f"rate_limit:{user_id}:{datetime.utcnow().strftime('%Y%m%d%H%M')}"

            # Get current count
            state = await client.get_state(
                store_name=self.store_name,
                key=key
            )

            count = int(state.data) if state.data else 0

            if count >= limit:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False

            # Increment count
            await client.save_state(
                store_name=self.store_name,
                key=key,
                value=str(count + 1),
                state_metadata={"ttlInSeconds": str(window_seconds)}
            )

            return True

# Middleware
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    user_id = request.state.user_id if hasattr(request.state, 'user_id') else None

    if user_id:
        rate_limiter = RateLimiter()
        if not await rate_limiter.check_rate_limit(user_id, limit=100, window_seconds=60):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)
    return response
```

## T164: Request Correlation IDs

### Implementation

Add correlation ID middleware in `backend/app/middleware/correlation.py`:

```python
from fastapi import Request
import uuid
import logging

logger = logging.getLogger(__name__)

async def correlation_id_middleware(request: Request, call_next):
    """Add correlation ID to all requests"""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))

    # Add to request state
    request.state.correlation_id = correlation_id

    # Add to logging context
    logger = logging.LoggerAdapter(
        logging.getLogger(__name__),
        {"correlation_id": correlation_id}
    )

    # Add to response headers
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id

    return response
```

## T165: Circuit Breaker Pattern

### Implementation

Create circuit breaker in `backend/app/utils/circuit_breaker.py`:

```python
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for external service calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout_seconds: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    async def call(self, func: Callable):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout_seconds):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = await func()

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN

            raise
```

## T166: Comprehensive Logging

### Implementation

Configure structured logging in `backend/app/utils/logging.py`:

```python
import logging
import json
from datetime import datetime

class StructuredLogger(logging.Formatter):
    """Structured JSON logging formatter"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "user_id": getattr(record, "user_id", None),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

# Configure logging
def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(StructuredLogger())

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
```

## T167: API Documentation

### Implementation

Add OpenAPI documentation in `backend/app/main.py`:

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Evolved Todo API",
    description="Event-driven task management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Evolved Todo API",
        version="1.0.0",
        description="Event-driven task management API with real-time sync",
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## T168: Frontend E2E Tests

### Implementation

Create Playwright tests in `frontend/tests/e2e/tasks.spec.ts`:

```typescript
import { test, expect } from '@playwright/test';

test.describe('Task Management', () => {
  test('should create a new task', async ({ page }) => {
    await page.goto('/tasks');

    // Click create task button
    await page.click('[data-testid="create-task-button"]');

    // Fill in task details
    await page.fill('[data-testid="task-title"]', 'Test Task');
    await page.fill('[data-testid="task-description"]', 'Test Description');

    // Submit form
    await page.click('[data-testid="submit-task"]');

    // Verify task appears in list
    await expect(page.locator('text=Test Task')).toBeVisible();
  });

  test('should complete a task', async ({ page }) => {
    await page.goto('/tasks');

    // Click checkbox to complete task
    await page.click('[data-testid="task-checkbox"]');

    // Verify task is marked as completed
    await expect(page.locator('[data-testid="task-status"]')).toHaveText('Completed');
  });
});
```

## T169: Backend Integration Tests

### Implementation

Create integration tests in `backend/tests/integration/test_tasks.py`:

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_task():
    """Test task creation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/tasks",
            json={
                "title": "Test Task",
                "description": "Test Description"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"

@pytest.mark.asyncio
async def test_list_tasks():
    """Test task listing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/tasks",
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
```

## T170: Performance Benchmarks

### Implementation

Create benchmarks in `backend/tests/performance/benchmark_search.py`:

```python
import asyncio
import time
from locust import HttpUser, task, between

class SearchBenchmark(HttpUser):
    """Performance benchmark for search"""
    wait_time = between(1, 2)

    @task
    def search_tasks(self):
        """Benchmark search performance"""
        start_time = time.time()

        self.client.get(
            "/api/v1/search/tasks?q=test",
            headers={"Authorization": f"Bearer {self.token}"}
        )

        duration = time.time() - start_time

        # Assert <1 second response time
        assert duration < 1.0, f"Search took {duration}s (expected <1s)"
```

## T174: Final Code Review

### Checklist

- [ ] All code follows project conventions
- [ ] No hardcoded secrets or credentials
- [ ] All functions have type hints
- [ ] All public APIs have docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is structured and consistent
- [ ] Tests cover critical paths
- [ ] Performance meets targets
- [ ] Security best practices followed
- [ ] Documentation is complete

## T175: Final E2E Testing

### Test Scenarios

1. **Real-Time Sync**: Open 2 browser tabs, create task in tab 1, verify appears in tab 2 within 2 seconds
2. **Reminders**: Schedule reminder for 5 minutes ahead, verify notification arrives within 10 seconds
3. **Recurring Tasks**: Create "every weekday at 9 AM" task, verify Monday-Friday recurrence
4. **Search**: Create 50 tasks, search "client meeting", verify results in <1 second
5. **Audit Trail**: Modify task 5 times, view audit log, verify all changes recorded
6. **Deployment**: Push code to main, verify auto-deploy to Oracle OKE within 10 minutes
7. **Microservice Creation**: Invoke microservice-creator agent, verify complete service template generated

## Next Steps

1. Implement each polish task systematically
2. Run tests after each implementation
3. Update tasks.md to mark completed tasks
4. Perform final code review
5. Execute end-to-end testing
6. Deploy to production

## Estimated Effort

- T161-T167: 2-3 days (implementation)
- T168-T170: 2-3 days (testing)
- T174: 1 day (code review)
- T175: 1 day (E2E testing)

**Total**: 6-10 days for complete polish phase
