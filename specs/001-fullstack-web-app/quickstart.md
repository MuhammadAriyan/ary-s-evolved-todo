# Quickstart Guide: Full-Stack Web Todo Application

**Feature**: 001-fullstack-web-app
**Date**: 2026-01-06
**Version**: 1.0.0

## Overview

This guide will help you set up and run the full-stack todo application locally. The application consists of a Next.js frontend, FastAPI backend, and Neon PostgreSQL database.

---

## Prerequisites

### Required Software

- **Node.js**: 18.0.0 or higher
- **Python**: 3.12 or higher
- **UV**: Python package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Git**: For version control
- **Docker** (optional): For local development with Docker Compose

### Required Accounts

- **Neon Account**: Sign up at https://neon.tech (free tier available)
- **Google Cloud Console**: For OAuth credentials (https://console.cloud.google.com)
- **Vercel Account** (optional): For frontend deployment
- **Hugging Face Account** (optional): For backend deployment

---

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd Ary-s-Evolutioned-Todo
git checkout 001-fullstack-web-app
```

---

## Step 2: Database Setup (Neon PostgreSQL)

### 2.1 Create Neon Project

1. Go to https://neon.tech and sign in
2. Click "Create Project"
3. Name: `todo-app`
4. Region: Choose closest to your location
5. Click "Create Project"

### 2.2 Get Connection String

1. In Neon dashboard, go to "Connection Details"
2. Copy the connection string (format: `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require`)
3. Save this for environment configuration

---

## Step 3: Google OAuth Setup

### 3.1 Create OAuth Credentials

1. Go to https://console.cloud.google.com
2. Create new project or select existing
3. Navigate to "APIs & Services" → "Credentials"
4. Click "Create Credentials" → "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Name: "Todo App"
7. Authorized redirect URIs:
   - `http://localhost:3000/api/auth/callback/google` (development)
   - `https://your-app.vercel.app/api/auth/callback/google` (production)
8. Click "Create"
9. Copy Client ID and Client Secret

---

## Step 4: Backend Setup

### 4.1 Navigate to Backend Directory

```bash
cd backend
```

### 4.2 Create Environment File

Create `backend/.env`:

```bash
# JWT Configuration (MUST match frontend BETTER_AUTH_SECRET)
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-long
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# CORS
CORS_ORIGINS=http://localhost:3000
```

**Generate Secret Key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4.3 Install Dependencies

```bash
# Using UV (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 4.4 Run Database Migrations

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Run migrations
alembic upgrade head
```

### 4.5 Start Backend Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Verify Backend**:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Step 5: Frontend Setup

### 5.1 Navigate to Frontend Directory

```bash
cd ../frontend
```

### 5.2 Create Environment File

Create `frontend/.env.local`:

```bash
# Better Auth Configuration
BETTER_AUTH_SECRET=your-super-secret-key-min-32-chars-long
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**CRITICAL**: Use the SAME secret key as backend `JWT_SECRET_KEY`

### 5.3 Install Dependencies

```bash
npm install
# or
yarn install
# or
pnpm install
```

### 5.4 Initialize shadcn/ui

```bash
npx shadcn-ui@latest init
```

Follow prompts:
- Style: Default
- Base color: Slate
- CSS variables: Yes

### 5.5 Install Required Components

```bash
npx shadcn-ui@latest add button input textarea select checkbox card dialog dropdown-menu separator calendar popover badge scroll-area
```

### 5.6 Start Frontend Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

**Verify Frontend**:
- Application: http://localhost:3000
- Should see landing page

---

## Step 6: Docker Compose Setup (Optional)

### 6.1 Create Docker Compose File

Create `docker/docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: todo_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/backend.Dockerfile
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/todo_db
      JWT_SECRET_KEY: your-super-secret-key-min-32-chars-long
      CORS_ORIGINS: http://localhost:3000
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/frontend.Dockerfile
    environment:
      BETTER_AUTH_SECRET: your-super-secret-key-min-32-chars-long
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/todo_db
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 6.2 Start Services

```bash
cd docker
docker-compose up -d
```

### 6.3 Stop Services

```bash
docker-compose down
```

---

## Step 7: Testing

### 7.1 Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

**Test Coverage**:
- Task CRUD operations
- User isolation
- JWT verification
- Recurring task generation

### 7.2 Frontend Manual Testing

**Authentication Flow**:
1. Navigate to http://localhost:3000
2. Click "Sign Up"
3. Register with email/password
4. Verify redirect to /todo dashboard
5. Log out
6. Log in with same credentials
7. Try "Sign in with Google"

**Todo Operations**:
1. Create new todo
2. Edit todo
3. Mark todo as complete
4. Delete todo
5. Add tags to todo
6. Filter by tag
7. Switch to calendar view
8. Create recurring todo

---

## Step 8: Deployment

### 8.1 Frontend Deployment (Vercel)

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

**Set Environment Variables in Vercel Dashboard**:
- `BETTER_AUTH_SECRET`
- `BETTER_AUTH_URL` (your Vercel URL)
- `DATABASE_URL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `NEXT_PUBLIC_API_URL` (your backend URL)

### 8.2 Backend Deployment (Hugging Face Spaces)

1. Create new Space on Hugging Face
2. Select "Docker" as SDK
3. Push backend code to Space repository
4. Set environment variables in Space settings:
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`
   - `CORS_ORIGINS`

**Alternative: Railway/Render**
- Connect GitHub repository
- Set environment variables
- Deploy automatically on push

---

## Troubleshooting

### Backend Issues

**Issue**: Database connection error
```
Solution: Verify DATABASE_URL is correct and includes ?sslmode=require
```

**Issue**: JWT verification fails
```
Solution: Ensure JWT_SECRET_KEY (backend) matches BETTER_AUTH_SECRET (frontend)
```

**Issue**: CORS errors
```
Solution: Add frontend URL to CORS_ORIGINS in backend .env
```

### Frontend Issues

**Issue**: API requests fail with 401
```
Solution: Check that JWT token is being sent in Authorization header
```

**Issue**: Google OAuth fails
```
Solution: Verify redirect URI matches Google Console configuration
```

**Issue**: shadcn/ui components not found
```
Solution: Run npx shadcn-ui@latest add <component-name>
```

### Database Issues

**Issue**: Migration fails
```
Solution: Drop tables and re-run: alembic downgrade base && alembic upgrade head
```

**Issue**: Connection pool exhausted
```
Solution: Increase pool_size in backend/app/database.py
```

---

## Development Workflow

### 1. Start Development Servers

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 2. Make Changes

- Backend: Edit files in `backend/app/`
- Frontend: Edit files in `frontend/app/` or `frontend/components/`
- Auto-reload enabled for both

### 3. Run Tests

```bash
# Backend tests
cd backend
pytest

# Frontend (manual testing)
# Open http://localhost:3000 and test features
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
git push
```

---

## Useful Commands

### Backend

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

### Frontend

```bash
# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint

# Format code
npm run format

# Type check
npm run type-check
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Description | Example |
|----------|-------------|---------|
| JWT_SECRET_KEY | Secret for JWT signing (MUST match frontend) | `abc123...` |
| JWT_ALGORITHM | JWT algorithm | `HS256` |
| JWT_EXPIRATION_HOURS | Token expiration | `24` |
| DATABASE_URL | Neon PostgreSQL connection string | `postgresql://...` |
| CORS_ORIGINS | Allowed origins (comma-separated) | `http://localhost:3000` |

### Frontend (.env.local)

| Variable | Description | Example |
|----------|-------------|---------|
| BETTER_AUTH_SECRET | Secret for JWT (MUST match backend) | `abc123...` |
| BETTER_AUTH_URL | Frontend URL | `http://localhost:3000` |
| DATABASE_URL | Neon PostgreSQL connection string | `postgresql://...` |
| GOOGLE_CLIENT_ID | Google OAuth client ID | `xxx.apps.googleusercontent.com` |
| GOOGLE_CLIENT_SECRET | Google OAuth client secret | `GOCSPX-...` |
| NEXT_PUBLIC_API_URL | Backend API URL | `http://localhost:8000` |

---

## Next Steps

1. **Explore the Application**: Create todos, test features
2. **Read Documentation**: Review API docs at http://localhost:8000/docs
3. **Run Tests**: Ensure everything works correctly
4. **Deploy**: Follow deployment guide for production
5. **Customize**: Modify UI, add features as needed

---

## Support

- **Documentation**: See `specs/001-fullstack-web-app/` directory
- **API Reference**: http://localhost:8000/docs
- **Issues**: Report bugs in GitHub issues
- **Questions**: Ask in project discussions

---

**Quickstart Guide Status**: ✅ Complete
**Version**: 1.0.0
**Last Updated**: 2026-01-06
