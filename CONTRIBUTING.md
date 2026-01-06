# Contributing to Ary's Evolutioned Todo

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.12+ and pip/uv
- PostgreSQL (Neon or local)
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/ary-s-evolutioned-todo.git
   cd ary-s-evolutioned-todo
   ```

2. **Set up backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp env.example .env
   # Edit .env with your configuration
   alembic upgrade head
   ```

3. **Set up frontend**
   ```bash
   cd frontend
   npm install
   cp env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Run development servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Creating a Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Making Changes

1. **Write clean, readable code**
   - Follow existing code style
   - Add comments for complex logic
   - Keep functions small and focused

2. **Write tests**
   - Backend: pytest tests in `backend/tests/`
   - Frontend: Jest/React Testing Library tests
   - Aim for >80% code coverage

3. **Update documentation**
   - Update README.md if needed
   - Add/update API documentation
   - Update DEPLOYMENT.md for infrastructure changes

### Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(backend): add task priority filtering endpoint

Add new endpoint to filter tasks by priority level.
Includes tests and API documentation.

Closes #123
```

```
fix(frontend): resolve calendar view date formatting issue

Fixed incorrect date display in calendar view for tasks
with due dates in different timezones.

Fixes #456
```

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/ -v --cov=app
```

**Frontend:**
```bash
cd frontend
npm run test
npm run type-check
npm run lint
```

### Code Quality

**Backend:**
```bash
# Linting
ruff check .

# Type checking
mypy app/

# Format code
black app/ tests/
```

**Frontend:**
```bash
# Linting
npm run lint

# Type checking
npm run type-check

# Format code
npm run format
```

## Pull Request Process

1. **Update your branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature-name
   git rebase develop
   ```

2. **Push your changes**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to GitHub and create a PR from your branch to `develop`
   - Fill in the PR template
   - Link related issues
   - Request reviews from maintainers

4. **PR Requirements**
   - [ ] All tests pass
   - [ ] Code coverage maintained or improved
   - [ ] Documentation updated
   - [ ] No merge conflicts
   - [ ] Approved by at least one maintainer

5. **After Approval**
   - Maintainer will merge your PR
   - Delete your feature branch

## Project Structure

```
ary-s-evolutioned-todo/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   └── core/        # Core utilities
│   ├── tests/           # Backend tests
│   └── alembic/         # Database migrations
├── frontend/            # Next.js frontend
│   ├── app/            # App Router pages
│   ├── components/     # React components
│   ├── hooks/          # Custom hooks
│   └── lib/            # Utilities
├── docker/             # Docker configurations
└── specs/              # Feature specifications
```

## Coding Standards

### Backend (Python)

- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Use docstrings for classes and functions
- Prefer composition over inheritance
- Keep functions pure when possible

**Example:**
```python
from typing import Optional
from sqlmodel import Session, select
from app.models.task import Task

def get_task_by_id(
    session: Session,
    task_id: int,
    user_id: str
) -> Optional[Task]:
    """
    Retrieve a task by ID with user isolation.

    Args:
        session: Database session
        task_id: Task ID to retrieve
        user_id: User ID for isolation

    Returns:
        Task if found and belongs to user, None otherwise
    """
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id
    )
    return session.exec(statement).first()
```

### Frontend (TypeScript/React)

- Use TypeScript for all files
- Prefer functional components with hooks
- Use meaningful variable names
- Extract reusable logic into custom hooks
- Keep components small and focused
- Use proper TypeScript types (avoid `any`)

**Example:**
```typescript
import { useState, useEffect } from "react"
import { Task } from "@/types/task"

interface TaskListProps {
  tasks: Task[]
  onEdit: (task: Task) => void
}

export function TaskList({ tasks, onEdit }: TaskListProps) {
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const handleSelect = (task: Task) => {
    setSelectedId(task.id)
    onEdit(task)
  }

  return (
    <div className="space-y-2">
      {tasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          isSelected={task.id === selectedId}
          onSelect={handleSelect}
        />
      ))}
    </div>
  )
}
```

## Database Migrations

### Creating a Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new column to tasks table"
```

### Reviewing Migration

- Always review auto-generated migrations
- Test migrations on development database
- Ensure migrations are reversible
- Add data migrations if needed

### Applying Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current
```

## Testing Guidelines

### Backend Tests

- Test all API endpoints
- Test business logic in services
- Test database models and queries
- Test error handling
- Use fixtures for common test data
- Mock external dependencies

**Example:**
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_create_task(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "Test task",
            "priority": "High",
            "tags": ["test"]
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["priority"] == "High"
```

### Frontend Tests

- Test component rendering
- Test user interactions
- Test form validation
- Test API integration
- Test error states

## Documentation

### API Documentation

- Use OpenAPI/Swagger annotations
- Document all endpoints
- Include request/response examples
- Document error responses
- Keep documentation up to date

### Code Documentation

- Add docstrings to functions and classes
- Explain complex algorithms
- Document assumptions and constraints
- Add TODO comments for future improvements

## Security

### Reporting Security Issues

- **DO NOT** open public issues for security vulnerabilities
- Email security concerns to: security@example.com
- Include detailed description and steps to reproduce
- Allow time for fix before public disclosure

### Security Best Practices

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user input
- Use parameterized queries (SQLModel handles this)
- Implement proper authentication and authorization
- Keep dependencies up to date

## Getting Help

- **Documentation**: Check README.md and DEPLOYMENT.md
- **Issues**: Search existing issues on GitHub
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact maintainers at support@example.com

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project README

Thank you for contributing to Ary's Evolutioned Todo! 🎉
