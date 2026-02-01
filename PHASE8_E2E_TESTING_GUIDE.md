# Phase 8 - Final End-to-End Testing Guide

**Date**: 2026-02-01
**Phase**: Phase 8 - Polish & Cross-Cutting Concerns
**Task**: T175 - Final end-to-end testing of all user stories

## Overview

This document provides comprehensive end-to-end testing procedures for all 7 user stories in Phase V Event-Driven Cloud Deployment.

---

## Test Environment Setup

### Prerequisites
- Backend API running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- PostgreSQL database accessible
- Redis running (for Dapr state store)
- Kafka/Redpanda running (for event streaming)
- Dapr runtime initialized

### Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/evolved_todo
REDIS_URL=redis://localhost:6379
KAFKA_BROKERS=localhost:9092
JWT_SECRET_KEY=your-secret-key

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_URL=http://localhost:3000
```

### Starting Services
```bash
# Terminal 1: Start infrastructure
docker-compose -f infrastructure/docker-compose.dev.yml up

# Terminal 2: Start backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 3: Start frontend
cd frontend
npm run dev

# Terminal 4: Start Dapr sidecars (if needed)
dapr run --app-id backend-api --app-port 8000 --dapr-http-port 3500
```

---

## User Story 1: Real-Time Task Synchronization

**Goal**: Task changes appear instantly across all user devices within 2 seconds

### Test Scenario 1.1: Two Browser Tabs Sync
**Steps**:
1. Open application in Chrome tab 1
2. Open application in Chrome tab 2 (incognito or different profile)
3. Log in with same user in both tabs
4. In tab 1: Create a new task "Sync Test Task"
5. Observe tab 2

**Expected Result**:
- Task appears in tab 2 within 2 seconds
- No page refresh required
- Task details match exactly

**Acceptance Criteria**: ✓ PASS if task appears in <2 seconds

### Test Scenario 1.2: Cross-Device Sync
**Steps**:
1. Open application on desktop browser
2. Open application on mobile browser (or mobile device)
3. Log in with same user on both devices
4. On desktop: Update task status to "completed"
5. Observe mobile device

**Expected Result**:
- Task status updates on mobile within 2 seconds
- Visual indicator shows task as completed
- No manual refresh needed

**Acceptance Criteria**: ✓ PASS if sync occurs in <2 seconds

### Test Scenario 1.3: WebSocket Reconnection
**Steps**:
1. Open application and verify WebSocket connected
2. Disable network (airplane mode or disconnect WiFi)
3. Wait 5 seconds
4. Re-enable network
5. Create a task on another device
6. Observe first device

**Expected Result**:
- Connection status shows "reconnecting"
- Connection re-establishes automatically
- Missed events are replayed
- New task appears after reconnection

**Acceptance Criteria**: ✓ PASS if reconnection works and events replayed

### Test Scenario 1.4: Optimistic UI Updates
**Steps**:
1. Open application
2. Create a new task
3. Observe UI immediately after clicking submit

**Expected Result**:
- Task appears in list immediately (optimistic update)
- Loading indicator shows briefly
- Task persists after server confirmation
- If error occurs, task is removed with error message

**Acceptance Criteria**: ✓ PASS if optimistic update works correctly

---

## User Story 2: Precise Time-Based Task Reminders

**Goal**: Users receive notifications within 10 seconds of scheduled time

### Test Scenario 2.1: Email Reminder
**Steps**:
1. Create a task "Email Reminder Test"
2. Schedule reminder for 2 minutes from now
3. Select "Email" as notification channel
4. Wait for scheduled time

**Expected Result**:
- Email received within 10 seconds of scheduled time
- Email contains task title and description
- Email has link to task

**Acceptance Criteria**: ✓ PASS if email arrives within 10 seconds

### Test Scenario 2.2: In-App Notification
**Steps**:
1. Create a task "In-App Reminder Test"
2. Schedule reminder for 1 minute from now
3. Select "In-App" as notification channel
4. Keep application open
5. Wait for scheduled time

**Expected Result**:
- Toast notification appears within 10 seconds
- Notification shows task title
- Clicking notification navigates to task

**Acceptance Criteria**: ✓ PASS if notification appears within 10 seconds

### Test Scenario 2.3: Multiple Reminders
**Steps**:
1. Create task "Multiple Reminders Test"
2. Schedule 3 reminders:
   - 1 minute from now
   - 2 minutes from now
   - 3 minutes from now
3. Wait and observe

**Expected Result**:
- All 3 reminders delivered on time
- Each reminder arrives within 10 seconds of scheduled time
- No duplicate notifications

**Acceptance Criteria**: ✓ PASS if all reminders delivered correctly

### Test Scenario 2.4: Timezone Handling
**Steps**:
1. Create task "Timezone Test"
2. Set reminder for "10:00 AM" in timezone "America/New_York"
3. Verify current time in New York
4. Wait for scheduled time

**Expected Result**:
- Reminder delivered at correct time in New York timezone
- Time conversion handled correctly
- Notification shows correct local time

**Acceptance Criteria**: ✓ PASS if timezone conversion correct

### Test Scenario 2.5: Idempotency Check
**Steps**:
1. Create task with reminder
2. Restart notification service
3. Wait for scheduled time

**Expected Result**:
- Only one notification delivered
- No duplicate notifications after service restart
- Idempotency key prevents duplicates

**Acceptance Criteria**: ✓ PASS if no duplicates

---

## User Story 3: Advanced Recurring Task Patterns

**Goal**: Tasks recur according to complex cron patterns

### Test Scenario 3.1: Daily Recurrence
**Steps**:
1. Create task "Daily Standup"
2. Set recurring pattern: "Every day at 9:00 AM"
3. Complete the task
4. Wait for next occurrence

**Expected Result**:
- New task instance created for next day
- Original task marked as completed
- New task has same title and description
- Due date is next day at 9:00 AM

**Acceptance Criteria**: ✓ PASS if task recurs daily

### Test Scenario 3.2: Weekday Recurrence
**Steps**:
1. Create task "Work Meeting"
2. Set recurring pattern: "Every weekday at 2:00 PM"
3. Complete task on Friday
4. Verify next occurrence

**Expected Result**:
- Next occurrence is Monday (not Saturday/Sunday)
- Task skips weekends
- Correct time maintained

**Acceptance Criteria**: ✓ PASS if weekends skipped

### Test Scenario 3.3: Monthly Recurrence
**Steps**:
1. Create task "Monthly Report"
2. Set recurring pattern: "First Monday of each month at 10:00 AM"
3. Complete task
4. Verify next occurrence

**Expected Result**:
- Next occurrence is first Monday of next month
- Date calculated correctly
- Time maintained

**Acceptance Criteria**: ✓ PASS if monthly pattern correct

### Test Scenario 3.4: Custom Cron Expression
**Steps**:
1. Create task "Custom Pattern"
2. Set custom cron: "0 */4 * * *" (every 4 hours)
3. Complete task
4. Verify next occurrence

**Expected Result**:
- Next occurrence is 4 hours later
- Pattern validated correctly
- Task recurs at correct intervals

**Acceptance Criteria**: ✓ PASS if custom cron works

### Test Scenario 3.5: Modify Recurring Pattern
**Steps**:
1. Create recurring task
2. Complete one instance
3. Modify recurring pattern on parent task
4. Complete next instance
5. Verify new pattern applied

**Expected Result**:
- Future instances use new pattern
- Past instances unchanged
- Pattern modification works correctly

**Acceptance Criteria**: ✓ PASS if pattern update works

---

## User Story 4: Intelligent Task Search

**Goal**: Search returns results in <1 second with fuzzy matching

### Test Scenario 4.1: Simple Search
**Steps**:
1. Create 50 tasks with various titles
2. Search for "meeting"
3. Measure response time

**Expected Result**:
- Results returned in <1 second
- All tasks with "meeting" in title or description shown
- Results ranked by relevance

**Acceptance Criteria**: ✓ PASS if response time <1s

### Test Scenario 4.2: Fuzzy Search
**Steps**:
1. Create task "Client Meeting"
2. Search for "meetng" (typo - missing 'i')
3. Observe results

**Expected Result**:
- "Client Meeting" appears in results
- Fuzzy matching handles typo
- Suggestion shown for correct spelling

**Acceptance Criteria**: ✓ PASS if fuzzy matching works

### Test Scenario 4.3: Search with Filters
**Steps**:
1. Create tasks with different statuses and priorities
2. Search for "project" with filters:
   - Status: pending
   - Priority: high
3. Observe results

**Expected Result**:
- Only pending, high-priority tasks shown
- Filters applied correctly
- Results still returned in <1 second

**Acceptance Criteria**: ✓ PASS if filters work correctly

### Test Scenario 4.4: Search Result Highlighting
**Steps**:
1. Search for "authentication"
2. Observe search results

**Expected Result**:
- Matched terms highlighted in results
- Highlighting works in title and description
- Visual distinction clear

**Acceptance Criteria**: ✓ PASS if highlighting works

### Test Scenario 4.5: Large Result Set Performance
**Steps**:
1. Create 1000 tasks
2. Search for common term
3. Measure response time

**Expected Result**:
- Results still returned in <1 second
- Pagination works correctly
- Performance maintained with large dataset

**Acceptance Criteria**: ✓ PASS if performance maintained

---

## User Story 5: Complete Audit Trail

**Goal**: All task changes recorded with before/after state

### Test Scenario 5.1: Task Creation Audit
**Steps**:
1. Create a new task
2. View audit log for task
3. Verify audit entry

**Expected Result**:
- Audit log shows "created" event
- Timestamp recorded
- User ID captured
- Initial state recorded

**Acceptance Criteria**: ✓ PASS if creation logged

### Test Scenario 5.2: Task Update Audit
**Steps**:
1. Create a task
2. Update title, description, status
3. View audit log
4. Verify entries

**Expected Result**:
- Each update creates audit entry
- Before/after state captured
- Changes clearly shown
- Chronological order maintained

**Acceptance Criteria**: ✓ PASS if all changes logged

### Test Scenario 5.3: Multiple Updates Audit
**Steps**:
1. Create a task
2. Make 5 different updates
3. View complete audit log
4. Verify all changes

**Expected Result**:
- All 5 updates logged
- Complete change history visible
- Can trace task evolution
- No missing entries

**Acceptance Criteria**: ✓ PASS if complete history shown

### Test Scenario 5.4: Audit Log Export
**Steps**:
1. Create task with multiple updates
2. Export audit log as JSON
3. Export audit log as CSV
4. Verify exports

**Expected Result**:
- JSON export contains all data
- CSV export formatted correctly
- Both formats downloadable
- Data integrity maintained

**Acceptance Criteria**: ✓ PASS if exports work

### Test Scenario 5.5: Audit Log Performance
**Steps**:
1. Create task with 100 updates
2. View audit log
3. Measure load time

**Expected Result**:
- Audit log loads in <2 seconds
- Pagination works for large logs
- Performance acceptable

**Acceptance Criteria**: ✓ PASS if performance acceptable

---

## User Story 6: Production-Ready Cloud Deployment

**Goal**: Auto-deploy to Oracle OKE within 10 minutes with health checks passing

### Test Scenario 6.1: CI/CD Pipeline
**Steps**:
1. Make code change
2. Commit and push to main branch
3. Observe GitHub Actions
4. Monitor deployment

**Expected Result**:
- Build completes successfully
- Tests pass
- Docker images built
- Deployment to staging automatic
- Health checks pass
- Deployment completes in <10 minutes

**Acceptance Criteria**: ✓ PASS if deployment completes in <10 min

### Test Scenario 6.2: Health Checks
**Steps**:
1. Access health check endpoints
2. Verify all services healthy

**Endpoints to Check**:
- `GET /health` - Overall health
- `GET /health/basic` - Liveness check
- `GET /health/legacy` - Readiness check

**Expected Result**:
- All health checks return 200 OK
- Database connection healthy
- Redis connection healthy
- Kafka connection healthy
- All microservices responding

**Acceptance Criteria**: ✓ PASS if all checks pass

### Test Scenario 6.3: Monitoring Dashboards
**Steps**:
1. Access Grafana dashboard
2. Verify metrics displayed
3. Check Prometheus targets

**Expected Result**:
- All services reporting metrics
- Dashboards show real-time data
- No missing metrics
- Alerts configured

**Acceptance Criteria**: ✓ PASS if monitoring works

### Test Scenario 6.4: Rollback Test
**Steps**:
1. Deploy version with intentional error
2. Observe health checks fail
3. Verify automatic rollback

**Expected Result**:
- Failed health checks detected
- Automatic rollback triggered
- Previous version restored
- Service availability maintained

**Acceptance Criteria**: ✓ PASS if rollback works

---

## User Story 7: Reusable Intelligence

**Goal**: Microservice creator agent generates complete service template

### Test Scenario 7.1: Agent Invocation
**Steps**:
1. Invoke microservice-creator agent
2. Provide service specification
3. Verify generated files

**Expected Result**:
- Complete service template generated
- Dockerfile included
- Helm charts included
- CI/CD configuration included
- README with instructions

**Acceptance Criteria**: ✓ PASS if complete template generated

### Test Scenario 7.2: Skills Usage
**Steps**:
1. Use event-pattern skill
2. Use dapr-component skill
3. Use helm-chart skill
4. Verify outputs

**Expected Result**:
- Skills generate correct code
- Code follows best practices
- Documentation included
- Examples provided

**Acceptance Criteria**: ✓ PASS if skills work correctly

---

## Cross-Cutting Concerns Testing

### Error Handling
**Test**: Trigger various errors and verify graceful handling
- Network errors
- Database errors
- Validation errors
- Authentication errors

**Expected**: User-friendly error messages, no crashes

### Rate Limiting
**Test**: Exceed rate limits
- Send 150 requests in 1 minute
- Verify 429 responses after 100 requests
- Check rate limit headers

**Expected**: Rate limiting enforced, proper headers

### Correlation IDs
**Test**: Make requests and verify correlation IDs
- Check X-Correlation-ID in responses
- Verify same ID in logs
- Trace request through services

**Expected**: Correlation IDs present and consistent

### Circuit Breakers
**Test**: Simulate external service failure
- Stop email service
- Trigger email sending
- Verify circuit opens

**Expected**: Circuit breaker prevents cascading failures

### Logging
**Test**: Verify structured logging
- Check log format (JSON in production)
- Verify correlation IDs in logs
- Check log levels

**Expected**: Structured logs with proper context

---

## Performance Testing Summary

### Targets and Results

| Metric | Target | Result | Status |
|--------|--------|--------|--------|
| Search response time | <1s | TBD | ⏳ |
| Task create | <500ms | TBD | ⏳ |
| Task read | <200ms | TBD | ⏳ |
| WebSocket connections | 100+ | TBD | ⏳ |
| Event processing | <100ms | TBD | ⏳ |
| Real-time sync | <2s | TBD | ⏳ |
| Reminder delivery | <10s | TBD | ⏳ |

---

## Test Execution Checklist

### Pre-Testing
- [ ] All services running
- [ ] Database seeded with test data
- [ ] Test user accounts created
- [ ] Monitoring enabled

### User Story Testing
- [ ] US1: Real-Time Sync (4 scenarios)
- [ ] US2: Reminders (5 scenarios)
- [ ] US3: Recurring Tasks (5 scenarios)
- [ ] US4: Search (5 scenarios)
- [ ] US5: Audit Trail (5 scenarios)
- [ ] US6: Deployment (4 scenarios)
- [ ] US7: Reusable Intelligence (2 scenarios)

### Cross-Cutting Testing
- [ ] Error handling
- [ ] Rate limiting
- [ ] Correlation IDs
- [ ] Circuit breakers
- [ ] Logging

### Performance Testing
- [ ] Run API benchmarks
- [ ] Run WebSocket benchmarks
- [ ] Run event benchmarks
- [ ] Verify all targets met

### Post-Testing
- [ ] Document results
- [ ] File bugs for failures
- [ ] Update metrics
- [ ] Generate test report

---

## Test Results Template

```markdown
# Test Execution Results

**Date**: YYYY-MM-DD
**Tester**: Name
**Environment**: Staging/Production

## Summary
- Total Scenarios: 30
- Passed: X
- Failed: Y
- Blocked: Z

## User Story Results
- US1: ✓ PASS / ✗ FAIL
- US2: ✓ PASS / ✗ FAIL
- US3: ✓ PASS / ✗ FAIL
- US4: ✓ PASS / ✗ FAIL
- US5: ✓ PASS / ✗ FAIL
- US6: ✓ PASS / ✗ FAIL
- US7: ✓ PASS / ✗ FAIL

## Issues Found
1. [Issue description]
2. [Issue description]

## Performance Results
[Table with actual measurements]

## Recommendations
[List of recommendations]
```

---

## Conclusion

This comprehensive E2E testing guide covers all 7 user stories with 30 test scenarios. Execute all tests systematically and document results.

**Status**: Ready for execution
**Next Steps**: Execute tests and document results
