# Tasks: Full-Stack Web Application Transformation

**Input**: Design documents from `/specs/001-fullstack-web-app/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Backend tests included (pytest for CRUD, user isolation, JWT verification, recurring tasks). Frontend tests are manual as specified in plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`, `backend/alembic/`
- **Frontend**: `frontend/app/`, `frontend/lib/`, `frontend/components/`, `frontend/hooks/`
- **Docker**: `docker/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and monorepo structure

- [X] T001 Create monorepo directory structure (backend/, frontend/, docker/, specs/)
- [X] T002 [P] Initialize backend Python project with UV in backend/pyproject.toml
- [X] T003 [P] Initialize frontend Next.js 15 project with TypeScript in frontend/
- [X] T004 [P] Create backend/.env.example with JWT_SECRET_KEY, DATABASE_URL, CORS_ORIGINS
- [X] T005 [P] Create frontend/.env.local.example with BETTER_AUTH_SECRET, DATABASE_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, NEXT_PUBLIC_API_URL
- [X] T006 [P] Configure backend linting (black, isort, flake8, mypy) in backend/pyproject.toml
- [X] T007 [P] Configure frontend linting (ESLint, Prettier) in frontend/.eslintrc.json
- [X] T008 Create docker/docker-compose.yml with postgres, backend, frontend services
- [X] T009 [P] Create docker/backend.Dockerfile
- [X] T010 [P] Create docker/frontend.Dockerfile
- [X] T011 Create root README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [X] T012 Install backend dependencies (FastAPI, SQLModel, Alembic, PyJWT, APScheduler, Uvicorn, pytest) in backend/pyproject.toml
- [X] T013 Create backend/app/main.py with FastAPI app initialization and CORS configuration
- [X] T014 Create backend/app/config.py with Pydantic Settings for environment variables
- [X] T015 Create backend/app/database.py with SQLModel engine and connection pooling (pool_size=5, max_overflow=10)
- [X] T016 Initialize Alembic in backend/alembic/ with alembic init command
- [X] T017 Configure Alembic env.py to use SQLModel metadata in backend/alembic/env.py
- [X] T018 [P] Create backend/app/models/__init__.py
- [X] T019 [P] Create backend/app/schemas/__init__.py
- [X] T020 [P] Create backend/app/api/__init__.py
- [X] T021 [P] Create backend/app/api/v1/__init__.py
- [X] T022 [P] Create backend/app/middleware/__init__.py
- [X] T023 [P] Create backend/app/utils/__init__.py
- [X] T024 [P] Create backend/app/jobs/__init__.py
- [X] T025 [P] Create backend/tests/__init__.py
- [X] T026 Create backend/app/utils/jwt.py with decode_jwt() and verify_token() functions
- [X] T027 Create backend/app/middleware/auth.py with JWT verification middleware using HTTPBearer
- [X] T028 Create backend/app/api/deps.py with get_db() and get_current_user() dependency injection
- [X] T029 Create backend/app/api/v1/router.py with API router setup

### Frontend Foundation

- [X] T030 Install frontend dependencies (Better Auth, TanStack Query, React Hook Form, Zod, shadcn/ui, Tailwind CSS, react-big-calendar) in frontend/package.json
- [X] T031 Initialize shadcn/ui with npx shadcn-ui@latest init in frontend/
- [X] T032 Install shadcn/ui components (button, input, textarea, select, checkbox, card, dialog, dropdown-menu, separator, calendar, popover, badge, scroll-area)
- [X] T033 Configure Tailwind CSS with custom theme in frontend/tailwind.config.ts
- [X] T034 Create frontend/lib/auth.ts with Better Auth configuration (email/password + Google OAuth + JWT plugin)
- [X] T035 Create frontend/app/api/auth/[...all]/route.ts with Better Auth handler
- [X] T036 Create frontend/middleware.ts with protected route middleware
- [X] T037 Create frontend/app/layout.tsx with QueryClient provider and root layout
- [X] T038 Create frontend/types/task.ts with TypeScript types (Task, CreateTaskInput, UpdateTaskInput, Priority, Recurring)
- [X] T039 Create frontend/lib/api-client.ts with API client class and JWT injection from Better Auth session

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Authentication (Priority: P1) 🎯 MVP

**Goal**: Enable users to register and login with email/password or Google OAuth, with JWT-based authentication

**Independent Test**: Register a new account, log out, log back in. Verify JWT token is issued and protected routes require authentication.

### Backend Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T040 [P] [US1] Create backend/tests/test_auth.py with test_jwt_verification() for valid/expired/invalid tokens
- [X] T041 [P] [US1] Add test_jwt_middleware() to backend/tests/test_auth.py for middleware integration
- [X] T042 [P] [US1] Add test_get_current_user() to backend/tests/test_auth.py for dependency injection

### Backend Implementation for User Story 1

- [X] T043 [US1] Create backend/app/models/user.py with User SQLModel (id, email, name, email_verified, created_at, updated_at)
- [X] T044 [US1] Create Alembic migration 001_initial.py for users table in backend/alembic/versions/
- [ ] T045 [US1] Run alembic upgrade head to create users table in Neon PostgreSQL
- [X] T046 [US1] Update backend/app/main.py to include health check endpoint at /health
- [X] T047 [US1] Add OpenAPI documentation configuration to backend/app/main.py (title, description, version)

### Frontend Implementation for User Story 1

- [X] T048 [P] [US1] Create frontend/app/page.tsx with landing page and links to login/signup
- [X] T049 [P] [US1] Create frontend/app/(auth)/login/page.tsx with email/password login form and Google OAuth button
- [X] T050 [P] [US1] Create frontend/app/(auth)/signup/page.tsx with email/password registration form and Google OAuth button
- [X] T051 [US1] Create frontend/app/(protected)/todo/page.tsx with placeholder dashboard (requires authentication)
- [ ] T052 [US1] Test authentication flow: register → logout → login → access protected route

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register, login, and access protected routes

---

## Phase 4: User Story 2 - Basic Todo Management (Priority: P2)

**Goal**: Enable authenticated users to create, view, edit, delete, and mark todos as complete

**Independent Test**: Create several todos, edit them, mark complete, delete them. Verify persistence across page refreshes.

### Backend Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T053 [P] [US2] Create backend/tests/test_tasks.py with test_create_task() for authenticated user
- [X] T054 [P] [US2] Add test_list_tasks() to backend/tests/test_tasks.py with user isolation verification
- [X] T055 [P] [US2] Add test_get_task() to backend/tests/test_tasks.py with user isolation verification
- [X] T056 [P] [US2] Add test_update_task() to backend/tests/test_tasks.py with user isolation verification
- [X] T057 [P] [US2] Add test_toggle_complete() to backend/tests/test_tasks.py
- [X] T058 [P] [US2] Add test_delete_task() to backend/tests/test_tasks.py with user isolation verification
- [X] T059 [P] [US2] Add test_user_isolation() to backend/tests/test_tasks.py verifying users cannot access other users' tasks

### Backend Implementation for User Story 2

- [X] T060 [US2] Create backend/app/models/task.py with Task SQLModel (id, user_id, title, description, completed, priority, tags, due_date, recurring, created_at, updated_at)
- [X] T061 [US2] Update Alembic migration 001_initial.py to include tasks table with indexes (user_id, completed, due_date, tags GIN)
- [ ] T062 [US2] Run alembic upgrade head to create tasks table and indexes
- [X] T063 [P] [US2] Create backend/app/schemas/task.py with TaskCreate, TaskUpdate, TaskResponse Pydantic schemas
- [X] T064 [US2] Create backend/app/api/v1/endpoints/tasks.py with GET /tasks endpoint (filters: tag, priority, completed, sort)
- [X] T065 [US2] Add POST /tasks endpoint to backend/app/api/v1/endpoints/tasks.py with user_id from JWT
- [X] T066 [US2] Add GET /tasks/{id} endpoint to backend/app/api/v1/endpoints/tasks.py with user isolation check
- [X] T067 [US2] Add PUT /tasks/{id} endpoint to backend/app/api/v1/endpoints/tasks.py with user isolation check
- [X] T068 [US2] Add PATCH /tasks/{id}/complete endpoint to backend/app/api/v1/endpoints/tasks.py
- [X] T069 [US2] Add DELETE /tasks/{id} endpoint to backend/app/api/v1/endpoints/tasks.py with user isolation check
- [X] T070 [US2] Register tasks router in backend/app/api/v1/router.py

### Frontend Implementation for User Story 2

- [X] T071 [P] [US2] Create frontend/hooks/useTasks.ts with TanStack Query hooks (useTasks, useCreateTask, useUpdateTask, useDeleteTask, useToggleComplete)
- [X] T072 [P] [US2] Add optimistic updates to all mutation hooks in frontend/hooks/useTasks.ts
- [X] T073 [P] [US2] Create frontend/app/(protected)/todo/components/TaskList.tsx with task cards, completion checkbox, edit/delete buttons
- [X] T074 [P] [US2] Create frontend/app/(protected)/todo/components/TaskForm.tsx with React Hook Form + Zod validation (title, description, priority, tags, due_date, recurring)
- [X] T075 [P] [US2] Create frontend/app/(protected)/todo/components/TaskFilters.tsx with All/Pending/Completed tabs
- [X] T076 [US2] Update frontend/app/(protected)/todo/page.tsx to integrate TaskList, TaskForm, TaskFilters components
- [ ] T077 [US2] Test todo CRUD operations: create → edit → mark complete → delete → verify persistence

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can manage todos

---

## Phase 5: User Story 3 - Tag Organization and Filtering (Priority: P3)

**Goal**: Enable users to organize todos with tags and filter by clicking tags in sidebar

**Independent Test**: Create todos with various tags, use tag sidebar to filter, verify only relevant todos appear

### Frontend Implementation for User Story 3

- [X] T078 [P] [US3] Create frontend/app/(protected)/todo/components/TagSidebar.tsx with unique tag extraction, todo counts, click-to-filter
- [X] T079 [P] [US3] Create React Context for sidebar state (open/closed, selected tag) in frontend/app/(protected)/todo/layout.tsx
- [X] T080 [US3] Update frontend/hooks/useTasks.ts to support tag filtering in query parameters
- [X] T081 [US3] Update frontend/app/(protected)/todo/page.tsx to integrate TagSidebar with filter state
- [X] T082 [US3] Add responsive design for TagSidebar (drawer on mobile) with Tailwind breakpoints
- [ ] T083 [US3] Test tag filtering: create todos with tags → click tag in sidebar → verify filtered results → clear filter

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can organize with tags

---

## Phase 6: User Story 4 - Calendar View with Animations (Priority: P4)

**Goal**: Enable users to visualize todos on a calendar by due date with smooth animations

**Independent Test**: Create todos with due dates, switch to calendar view, verify todos appear on correct dates with smooth transitions

### Frontend Implementation for User Story 4

- [X] T084 [P] [US4] Install react-big-calendar and moment.js in frontend/package.json
- [X] T085 [P] [US4] Create frontend/app/(protected)/todo/components/CalendarView.tsx with react-big-calendar integration
- [X] T086 [P] [US4] Map tasks to calendar events by due_date in CalendarView component
- [X] T087 [P] [US4] Add custom styling for calendar with Tailwind CSS in frontend/app/globals.css
- [X] T088 [P] [US4] Implement event click handler to open task details modal
- [X] T089 [P] [US4] Add priority-based color coding for calendar events (High=red, Medium=yellow, Low=green)
- [X] T090 [US4] Add view toggle button (List/Calendar) to frontend/app/(protected)/todo/page.tsx
- [X] T091 [US4] Implement smooth transition animations between list and calendar views with Tailwind transitions
- [ ] T092 [US4] Test calendar view: create todos with due dates → switch to calendar → verify correct placement → navigate months

**Checkpoint**: At this point, User Stories 1-4 should all work independently - users can visualize todos on calendar

---

## Phase 7: User Story 5 - Recurring Tasks with Scheduler (Priority: P5)

**Goal**: Enable users to create recurring todos that automatically regenerate on schedule

**Independent Test**: Create a recurring todo with daily pattern, wait for next occurrence, verify new instance is created automatically

### Backend Tests for User Story 5

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T093 [P] [US5] Create backend/tests/test_recurring.py with test_calculate_next_due_date() for daily/weekly/monthly patterns
- [X] T094 [P] [US5] Add test_generate_recurring_tasks() to backend/tests/test_recurring.py with idempotency check
- [X] T095 [P] [US5] Add test_recurring_task_scheduler() to backend/tests/test_recurring.py for APScheduler integration

### Backend Implementation for User Story 5

- [X] T096 [P] [US5] Install python-dateutil in backend/pyproject.toml for date calculations
- [X] T097 [US5] Create backend/app/jobs/recurring_tasks.py with generate_recurring_tasks() function
- [X] T098 [US5] Add calculate_next_due_date() function to backend/app/jobs/recurring_tasks.py (daily, weekly, monthly logic)
- [X] T099 [US5] Implement idempotency check in generate_recurring_tasks() to prevent duplicate task creation
- [X] T100 [US5] Add APScheduler BackgroundScheduler configuration in backend/app/jobs/recurring_tasks.py (runs every minute)
- [X] T101 [US5] Add start_scheduler() and stop_scheduler() functions to backend/app/jobs/recurring_tasks.py
- [X] T102 [US5] Integrate scheduler with FastAPI startup/shutdown events in backend/app/main.py
- [X] T103 [US5] Add comprehensive logging for scheduler execution in backend/app/jobs/recurring_tasks.py

### Frontend Implementation for User Story 5

- [X] T104 [US5] Update frontend/app/(protected)/todo/components/TaskForm.tsx to add recurring field with preset options (daily, weekly, monthly)
- [X] T105 [US5] Add recurring pattern indicator to task cards in frontend/app/(protected)/todo/components/TaskList.tsx
- [ ] T106 [US5] Test recurring tasks: create daily recurring todo → wait 1 minute → verify new instance created → mark one complete → verify others remain

**Checkpoint**: At this point, all User Stories 1-5 should work independently - full feature set complete

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Documentation

- [X] T107 [P] Update root README.md with complete setup instructions, architecture overview, deployment guide
- [X] T108 [P] Create backend/README.md with API documentation, testing instructions, environment variables
- [X] T109 [P] Create frontend/README.md with component structure, state management, deployment instructions
- [ ] T110 [P] Verify quickstart.md instructions work end-to-end

### Testing & Quality

- [ ] T111 [P] Run backend test suite with coverage: pytest --cov=app --cov-report=html
- [ ] T112 [P] Verify backend test coverage is >80% for core logic
- [ ] T113 Manual frontend testing: complete all acceptance scenarios from spec.md for all user stories
- [ ] T114 Test mobile responsiveness on real devices for all user stories
- [ ] T115 Test error handling: invalid inputs, network errors, expired tokens, database failures

### Performance & Security

- [ ] T116 [P] Add database query optimization: verify all indexes are used with EXPLAIN ANALYZE
- [ ] T117 [P] Add rate limiting to public endpoints (registration, login) in backend/app/main.py
- [ ] T118 [P] Verify input validation on both client and server for all endpoints
- [ ] T119 [P] Add security headers (HTTPS, CORS, CSP) to backend/app/main.py
- [ ] T120 [P] Test JWT token expiration and refresh flow

### Deployment Preparation

- [X] T121 [P] Create backend/.env.production.example with production environment variables
- [X] T122 [P] Create frontend/.env.production.example with production environment variables
- [X] T123 [P] Create deployment documentation in docs/deployment.md for Vercel + Hugging Face Spaces + Neon
- [X] T124 Test Docker Compose setup: docker-compose up → verify all services start → test full application flow
- [X] T125 Create production deployment checklist in docs/deployment-checklist.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 for authentication but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US2 but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Builds on US2 but independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - Builds on US2 but independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Backend models before backend endpoints
- Backend endpoints before frontend hooks
- Frontend hooks before frontend components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T002-T003, T004-T005, T006-T007, T009-T010 can run in parallel
- **Phase 2 (Foundational)**: T018-T025 (directory creation), T030-T039 (frontend setup) can run in parallel
- **User Story Tests**: All test tasks marked [P] within a story can run in parallel
- **User Story Models**: Backend and frontend tasks marked [P] can run in parallel
- **Different User Stories**: Once Foundational phase completes, all user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 2

```bash
# Launch all backend tests for User Story 2 together:
Task T053: "Create backend/tests/test_tasks.py with test_create_task()"
Task T054: "Add test_list_tasks() to backend/tests/test_tasks.py"
Task T055: "Add test_get_task() to backend/tests/test_tasks.py"
Task T056: "Add test_update_task() to backend/tests/test_tasks.py"
Task T057: "Add test_toggle_complete() to backend/tests/test_tasks.py"
Task T058: "Add test_delete_task() to backend/tests/test_tasks.py"
Task T059: "Add test_user_isolation() to backend/tests/test_tasks.py"

# Launch backend schemas and frontend hooks in parallel:
Task T063: "Create backend/app/schemas/task.py with Pydantic schemas"
Task T071: "Create frontend/hooks/useTasks.ts with TanStack Query hooks"

# Launch all frontend components in parallel:
Task T073: "Create frontend/app/(protected)/todo/components/TaskList.tsx"
Task T074: "Create frontend/app/(protected)/todo/components/TaskForm.tsx"
Task T075: "Create frontend/app/(protected)/todo/components/TaskFilters.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup (T001-T011)
2. Complete Phase 2: Foundational (T012-T039) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T040-T052) - Authentication
4. Complete Phase 4: User Story 2 (T053-T077) - Basic Todo Management
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready - this is a functional todo app with auth!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (Auth working!)
3. Add User Story 2 → Test independently → Deploy/Demo (MVP - functional todo app!)
4. Add User Story 3 → Test independently → Deploy/Demo (Tags added!)
5. Add User Story 4 → Test independently → Deploy/Demo (Calendar added!)
6. Add User Story 5 → Test independently → Deploy/Demo (Recurring tasks added!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T039)
2. Once Foundational is done:
   - Developer A: User Story 1 (T040-T052)
   - Developer B: User Story 2 (T053-T077) - starts after US1 auth is ready
   - Developer C: User Story 3 (T078-T083) - starts after US2 is ready
   - Developer D: User Story 4 (T084-T092) - starts after US2 is ready
   - Developer E: User Story 5 (T093-T106) - starts after US2 is ready
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 125 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 11 tasks
- Phase 2 (Foundational): 28 tasks
- Phase 3 (US1 - Authentication): 13 tasks
- Phase 4 (US2 - Todo Management): 25 tasks
- Phase 5 (US3 - Tags): 6 tasks
- Phase 6 (US4 - Calendar): 9 tasks
- Phase 7 (US5 - Recurring): 14 tasks
- Phase 8 (Polish): 19 tasks

**Parallel Opportunities**: 47 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Register → logout → login → access protected route
- US2: Create → edit → mark complete → delete → verify persistence
- US3: Create with tags → filter by tag → verify results
- US4: Create with due dates → switch to calendar → verify placement
- US5: Create recurring → wait → verify new instance created

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2) = 77 tasks for functional todo app with authentication

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Backend tests use pytest with coverage for CRUD, user isolation, JWT verification, recurring tasks
- Frontend tests are manual as specified in plan.md
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
