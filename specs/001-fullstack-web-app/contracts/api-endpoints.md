# API Endpoints Contract

**Feature**: 001-fullstack-web-app
**Date**: 2026-01-06
**Version**: 1.0.0

## Base Configuration

**Base URL**: `http://localhost:8000/api/v1` (development)
**Production URL**: `https://your-api.hf.space/api/v1`

**Authentication**: All endpoints require `Authorization: Bearer <jwt_token>` header unless marked as public.

**Content-Type**: `application/json`

**CORS**: Configured to allow requests from frontend origin (http://localhost:3000 in development)

---

## Authentication Endpoints

### POST /auth/register
**Description**: Register new user with email and password
**Authentication**: Public
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```
**Response**: 201 Created
```json
{
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "email_verified": false
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
**Errors**:
- 400 Bad Request: Invalid email format or password too short
- 409 Conflict: Email already registered

### POST /auth/login
**Description**: Login with email and password
**Authentication**: Public
**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```
**Response**: 200 OK
```json
{
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```
**Errors**:
- 401 Unauthorized: Invalid credentials

### POST /auth/google
**Description**: Authenticate with Google OAuth
**Authentication**: Public
**Request Body**:
```json
{
  "code": "google_oauth_code",
  "redirect_uri": "http://localhost:3000/auth/callback"
}
```
**Response**: 200 OK
```json
{
  "user": {
    "id": "user_abc123",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## Task Endpoints

### GET /tasks
**Description**: List all tasks for authenticated user with optional filters
**Authentication**: Required
**Query Parameters**:
- `tag` (string, optional): Filter by tag
- `priority` (string, optional): Filter by priority (High, Medium, Low)
- `completed` (boolean, optional): Filter by completion status
- `sort` (string, optional): Sort field (created_at, priority, due_date, title)

**Example Request**:
```
GET /api/v1/tasks?tag=work&priority=High&completed=false&sort=due_date
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**: 200 OK
```json
[
  {
    "id": 1,
    "user_id": "user_abc123",
    "title": "Finish project report",
    "description": "Complete the Q4 project report",
    "completed": false,
    "priority": "High",
    "tags": ["work", "urgent"],
    "due_date": "2026-01-15",
    "recurring": null,
    "created_at": "2026-01-06T10:00:00Z",
    "updated_at": "2026-01-06T10:00:00Z"
  }
]
```

**Errors**:
- 401 Unauthorized: Invalid or expired token

---

### POST /tasks
**Description**: Create new task for authenticated user
**Authentication**: Required
**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "Medium",
  "tags": ["home", "shopping"],
  "due_date": "2026-01-10",
  "recurring": null
}
```

**Response**: 201 Created
```json
{
  "id": 2,
  "user_id": "user_abc123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "priority": "Medium",
  "tags": ["home", "shopping"],
  "due_date": "2026-01-10",
  "recurring": null,
  "created_at": "2026-01-06T11:00:00Z",
  "updated_at": "2026-01-06T11:00:00Z"
}
```

**Validation Rules**:
- `title`: Required, max 200 characters
- `description`: Optional, max 2000 characters
- `priority`: Optional, must be "High", "Medium", or "Low" (default: "Medium")
- `tags`: Optional, max 10 tags, each max 50 characters
- `due_date`: Optional, ISO date format (YYYY-MM-DD)
- `recurring`: Optional, must be "daily", "weekly", or "monthly"

**Errors**:
- 401 Unauthorized: Invalid or expired token
- 422 Unprocessable Entity: Validation error

---

### GET /tasks/{id}
**Description**: Get task by ID for authenticated user
**Authentication**: Required
**Path Parameters**:
- `id` (integer): Task ID

**Example Request**:
```
GET /api/v1/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**: 200 OK
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Finish project report",
  "description": "Complete the Q4 project report",
  "completed": false,
  "priority": "High",
  "tags": ["work", "urgent"],
  "due_date": "2026-01-15",
  "recurring": null,
  "created_at": "2026-01-06T10:00:00Z",
  "updated_at": "2026-01-06T10:00:00Z"
}
```

**Errors**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Task not found or doesn't belong to user

---

### PUT /tasks/{id}
**Description**: Update task for authenticated user
**Authentication**: Required
**Path Parameters**:
- `id` (integer): Task ID

**Request Body** (all fields optional):
```json
{
  "title": "Finish project report (updated)",
  "description": "Complete the Q4 project report with charts",
  "priority": "High",
  "tags": ["work", "urgent", "q4"],
  "due_date": "2026-01-20",
  "recurring": null
}
```

**Response**: 200 OK
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Finish project report (updated)",
  "description": "Complete the Q4 project report with charts",
  "completed": false,
  "priority": "High",
  "tags": ["work", "urgent", "q4"],
  "due_date": "2026-01-20",
  "recurring": null,
  "created_at": "2026-01-06T10:00:00Z",
  "updated_at": "2026-01-06T12:00:00Z"
}
```

**Errors**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Task not found or doesn't belong to user
- 422 Unprocessable Entity: Validation error

---

### PATCH /tasks/{id}/complete
**Description**: Toggle task completion status
**Authentication**: Required
**Path Parameters**:
- `id` (integer): Task ID

**Example Request**:
```
PATCH /api/v1/tasks/1/complete
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**: 200 OK
```json
{
  "id": 1,
  "user_id": "user_abc123",
  "title": "Finish project report",
  "description": "Complete the Q4 project report",
  "completed": true,
  "priority": "High",
  "tags": ["work", "urgent"],
  "due_date": "2026-01-15",
  "recurring": null,
  "created_at": "2026-01-06T10:00:00Z",
  "updated_at": "2026-01-06T13:00:00Z"
}
```

**Errors**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Task not found or doesn't belong to user

---

### DELETE /tasks/{id}
**Description**: Delete task for authenticated user
**Authentication**: Required
**Path Parameters**:
- `id` (integer): Task ID

**Example Request**:
```
DELETE /api/v1/tasks/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response**: 204 No Content

**Errors**:
- 401 Unauthorized: Invalid or expired token
- 404 Not Found: Task not found or doesn't belong to user

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common HTTP Status Codes**:
- 200 OK: Request succeeded
- 201 Created: Resource created successfully
- 204 No Content: Request succeeded with no response body
- 400 Bad Request: Invalid request format
- 401 Unauthorized: Authentication required or token invalid
- 403 Forbidden: Authenticated but not authorized
- 404 Not Found: Resource not found
- 409 Conflict: Resource already exists
- 422 Unprocessable Entity: Validation error
- 500 Internal Server Error: Server error

---

## Rate Limiting

**Development**: No rate limiting
**Production**:
- 100 requests per minute per IP for public endpoints
- 1000 requests per minute per user for authenticated endpoints

---

## OpenAPI/Swagger Documentation

FastAPI automatically generates interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Example Usage (cURL)

### Register User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123","name":"John Doe"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### List Tasks
```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","priority":"Medium","tags":["home"]}'
```

### Update Task
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries (updated)","completed":true}'
```

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

**API Contract Status**: ✅ Complete
**Version**: 1.0.0
**Last Updated**: 2026-01-06
