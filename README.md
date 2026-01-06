# Full-Stack Web Todo Application

A production-ready full-stack web application with authentication, todo management, tags, calendar view, and recurring tasks. Built with Next.js 15+, FastAPI, and Neon PostgreSQL.

## Phase II: Full-Stack Web Application (Current)

This repository contains both the original console app (Phase I) and the new full-stack web application (Phase II).

## Architecture

**Monorepo Structure:**
- `backend/` - FastAPI backend with SQLModel ORM
- `frontend/` - Next.js 15+ with TypeScript and shadcn/ui
- `docker/` - Docker Compose configuration
- `specs/` - Feature specifications and documentation
- `src/` - Original Phase I console app

**Technology Stack:**
- **Frontend**: Next.js 15+, React 19, TypeScript, shadcn/ui, Tailwind CSS, Better Auth, TanStack Query
- **Backend**: FastAPI, Python 3.12+, SQLModel, Alembic, PyJWT, APScheduler
- **Database**: Neon PostgreSQL (serverless)
- **Authentication**: Better Auth with JWT (Email/Password + Google OAuth)

## Quick Start (Phase II Web App)

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+ and UV package manager
- Neon PostgreSQL account
- Google OAuth credentials (optional)

### Setup

1. **Backend setup:**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your database URL and JWT secret
   uv pip install -e ".[dev]"
   alembic upgrade head
   uvicorn app.main:app --reload
   ```

2. **Frontend setup:**
   ```bash
   cd frontend
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   npm install
   npm run dev
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Docker Setup (Alternative)

```bash
cd docker
docker-compose up -d
```

## Documentation

- **Quickstart Guide**: `specs/001-fullstack-web-app/quickstart.md`
- **API Contracts**: `specs/001-fullstack-web-app/contracts/`
- **Implementation Plan**: `specs/001-fullstack-web-app/plan.md`
- **Task Breakdown**: `specs/001-fullstack-web-app/tasks.md`

## Phase I: Console App

See the original console app in `src/` directory. Run with:

```bash
python src/main.py
```

## Features

### Basic Level (Core Essentials)
- **Add Task** - Create new todo items with title (required) and description (optional)
- **Delete Task** - Remove tasks from the list by ID
- **Update Task** - Modify existing task details by ID
- **View Task List** - Display all tasks with status indicators
- **Mark as Complete** - Toggle task completion status by ID

### Intermediate Level (Organization & Usability)
- **Priorities** - Assign High, Medium, or Low priority levels
- **Tags** - Categorize tasks with multiple labels
- **Search** - Keyword search in title or description
- **Filter** - Filter by status, priority, or tag
- **Sort** - Sort by priority, due date, or title

### Advanced Level (Structural Preparation)
- **Due Dates** - Set optional due dates (YYYY-MM-DD format)
- **Recurring** - Mark tasks as recurring (daily, weekly, monthly)

## Installation

```bash
# Using UV (recommended)
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
uv sync

# Or using pip
pip install -e .
```

## Running the Application

```bash
# Run with Python directly
python src/main.py

# Or with UV
uv run python src/main.py
```

## Usage Guide

### Main Menu

```
=== Todo Manager ===
1. Add Task
2. Delete Task
3. Update Task
4. List All Tasks
5. Mark Complete
6. List Pending
7. List Completed
8. Search Tasks
9. Filter by Priority
10. Filter by Tag
11. Sort Tasks
0. Exit
```

### Example Session

```
=== Todo Manager ===
1. Add Task
0. Exit
> 1

Title: Finish report
Description (optional): Q4 summary
Priority (H/M/L, default M): h
Tags (comma-separated, optional): work,urgent
Due date (YYYY-MM-DD, optional): 2026-01-15

[OK] Task added successfully! (ID: 1)

> 4
 ID | Status | Prio | Due        | Title       | Tags          | Description
--------------------------------------------------------------------------------------------------------------
  1 | [ ]    | H    | 2026-01-15 | Finish report | work,urgent   | Q4 summary
```

## Running Tests

```bash
# Run all tests
PYTHONPATH=src python -m unittest discover -s tests -v

# Run specific test file
PYTHONPATH=src python -m unittest tests.test_task tests.test_todo_manager -v
```

## Project Structure

```
├── src/
│   ├── todo.py          # Task dataclass + TodoManager class
│   └── main.py          # CLI loop and presentation
├── tests/
│   ├── test_task.py     # Task dataclass tests
│   ├── test_todo_manager.py  # TodoManager unit tests
│   └── test_cli.py      # CLI integration tests
├── specs/               # Spec-Kit Plus documentation
│   └── 001-in-memory-todo/
│       ├── spec.md      # Feature specification
│       ├── plan.md      # Implementation plan
│       └── tasks.md     # Task breakdown
├── .claude/skills/      # Claude Code skills
│   └── validate-todo.md
└── README.md
```

## Technology Stack

- **Language**: Python 3.12+
- **Dependencies**: Python standard library only
- **Testing**: unittest (standard library)
- **Architecture**: Clean Architecture with separation of concerns

## Hackathon Phase I

This is Phase I of a multi-phase project:
- **Phase I**: In-memory Python Console App (current)
- **Phase II**: FastAPI + Neon DB Web Application
- **Phase III**: AI-Powered Chatbot
- **Phase IV**: Local Kubernetes Deployment
- **Phase V**: Cloud-Native Event-Driven System
