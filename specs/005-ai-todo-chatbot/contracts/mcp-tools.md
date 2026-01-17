# MCP Tools Contract

**Feature**: 005-ai-todo-chatbot
**Date**: 2026-01-11

## Overview

This document defines the contract for 8 MCP tools exposed by the AI Todo Chatbot. All tools are stateless and interact with the database for persistence.

## Tool Registry

| Tool | Purpose | Agent |
|------|---------|-------|
| `add_task` | Create new task | Elara (➕) |
| `list_tasks` | Query tasks with filters | Kael (📋) |
| `complete_task` | Mark task completed | Nyra (✅) |
| `delete_task` | Remove task | Taro (🗑️) |
| `update_task` | Modify task properties | Lys (✏️) |
| `uncomplete_task` | Reopen completed task | Nyra (✅) |
| `get_task_analytics` | Return statistics | Orion (📊) |
| `search_tasks` | Keyword search | Vera (🔍) |

---

## Tool Specifications

### 1. add_task

Creates a new task for the authenticated user.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |
| `title` | string | Yes | Task title (max 500 chars) |
| `description` | string | No | Task description (max 2000 chars) |
| `priority` | string | No | Priority: low, medium, high (default: medium) |
| `tags` | string[] | No | List of tags |
| `due_date` | string | No | ISO 8601 date string |

**Returns**:
```json
{
  "success": true,
  "task_id": "uuid-string",
  "message": "Task 'Buy groceries' created successfully"
}
```

**Errors**:
```json
{
  "success": false,
  "error": "Title is required"
}
```

**Implementation**:
```python
@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: list[str] = [],
    due_date: str | None = None,
) -> dict:
    """Create a new task for the user.

    Args:
        user_id: The authenticated user's ID (required for isolation)
        title: Task title (max 500 characters)
        description: Optional task description
        priority: Task priority (low, medium, high)
        tags: Optional list of tags
        due_date: Optional due date in ISO format (YYYY-MM-DD)

    Returns:
        dict with task_id and success status
    """
```

---

### 2. list_tasks

Retrieves tasks for the user with optional filters.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |
| `completed` | boolean | No | Filter by completion status |
| `priority` | string | No | Filter by priority |
| `tags` | string[] | No | Filter by tags (any match) |
| `limit` | integer | No | Max results (default: 50, max: 100) |

**Returns**:
```json
{
  "success": true,
  "count": 5,
  "tasks": [
    {
      "id": "uuid",
      "title": "Buy groceries",
      "description": "",
      "completed": false,
      "priority": "medium",
      "tags": ["shopping"],
      "due_date": null,
      "created_at": "2026-01-11T10:00:00Z"
    }
  ]
}
```

**Implementation**:
```python
@mcp.tool()
async def list_tasks(
    user_id: str,
    completed: bool | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    limit: int = 50,
) -> dict:
    """List tasks for the user with optional filters.

    Args:
        user_id: The authenticated user's ID
        completed: Filter by completion status (true/false)
        priority: Filter by priority level (low/medium/high)
        tags: Filter by tags (returns tasks with any matching tag)
        limit: Maximum number of tasks to return (default 50, max 100)

    Returns:
        dict with list of tasks and count
    """
```

---

### 3. complete_task

Marks a task as completed.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |
| `task_id` | string | Yes | Task ID to complete |

**Returns**:
```json
{
  "success": true,
  "message": "Task 'Buy groceries' marked as completed"
}
```

**Errors**:
```json
{
  "success": false,
  "error": "Task not found or access denied"
}
```

**Implementation**:
```python
@mcp.tool()
async def complete_task(user_id: str, task_id: str) -> dict:
    """Mark a task as completed.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to complete

    Returns:
        dict with success status and confirmation message
    """
```

---

### 4. delete_task

Removes a task permanently.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |
| `task_id` | string | Yes | Task ID to delete |

**Returns**:
```json
{
  "success": true,
  "message": "Task 'Buy groceries' deleted"
}
```

**Implementation**:
```python
@mcp.tool()
async def delete_task(user_id: str, task_id: str) -> dict:
    """Delete a task permanently.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to delete

    Returns:
        dict with success status and confirmation message
    """
```

---

### 5. update_task

Modifies task properties.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |
| `task_id` | string | Yes | Task ID to update |
| `title` | string | No | New title |
| `description` | string | No | New description |
| `priority` | string | No | New priority |
| `tags` | string[] | No | New tags (replaces existing) |
| `due_date` | string | No | New due date |

**Returns**:
```json
{
  "success": true,
  "message": "Task updated successfully",
  "updated_fields": ["title", "priority"]
}
```

**Implementation**:
```python
@mcp.tool()
async def update_task(
    user_id: str,
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    tags: list[str] | None = None,
    due_date: str | None = None,
) -> dict:
    """Update task properties.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to update
        title: New task title (optional)
        description: New description (optional)
        priority: New priority level (optional)
        tags: New tags list - replaces existing (optional)
        due_date: New due date in ISO format (optional)

    Returns:
        dict with success status and list of updated fields
    """
```

---

### 6. uncomplete_task

Reopens a previously completed task.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |
| `task_id` | string | Yes | Task ID to uncomplete |

**Returns**:
```json
{
  "success": true,
  "message": "Task 'Buy groceries' reopened"
}
```

**Implementation**:
```python
@mcp.tool()
async def uncomplete_task(user_id: str, task_id: str) -> dict:
    """Reopen a completed task.

    Args:
        user_id: The authenticated user's ID
        task_id: The task ID to reopen

    Returns:
        dict with success status and confirmation message
    """
```

---

### 7. get_task_analytics

Returns task statistics for the user.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |

**Returns**:
```json
{
  "success": true,
  "analytics": {
    "total_tasks": 25,
    "completed_tasks": 18,
    "pending_tasks": 7,
    "completion_rate": 72.0,
    "by_priority": {
      "high": 5,
      "medium": 15,
      "low": 5
    },
    "overdue_tasks": 2,
    "tasks_due_today": 1
  }
}
```

**Implementation**:
```python
@mcp.tool()
async def get_task_analytics(user_id: str) -> dict:
    """Get task statistics for the user.

    Args:
        user_id: The authenticated user's ID

    Returns:
        dict with analytics including counts, completion rate, and breakdowns
    """
```

---

### 8. search_tasks

Searches tasks by keyword in title and description.

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | Yes | Authenticated user's ID |
| `query` | string | Yes | Search keyword |
| `limit` | integer | No | Max results (default: 20) |

**Returns**:
```json
{
  "success": true,
  "count": 3,
  "query": "groceries",
  "tasks": [
    {
      "id": "uuid",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "relevance_score": 0.95
    }
  ]
}
```

**Implementation**:
```python
@mcp.tool()
async def search_tasks(
    user_id: str,
    query: str,
    limit: int = 20,
) -> dict:
    """Search tasks by keyword.

    Args:
        user_id: The authenticated user's ID
        query: Search keyword to match in title or description
        limit: Maximum number of results (default 20)

    Returns:
        dict with matching tasks and count
    """
```

---

## Security Requirements

1. **User Isolation**: Every tool MUST filter by `user_id`
2. **No Cross-User Access**: Tools MUST NOT return or modify other users' tasks
3. **Input Validation**: All inputs validated before database operations
4. **Error Handling**: Never expose internal errors; return user-friendly messages

## Error Response Format

All tools return consistent error format:
```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

Common errors:
- `"Task not found or access denied"` - Task doesn't exist or belongs to another user
- `"Title is required"` - Missing required parameter
- `"Invalid priority value"` - Invalid enum value
- `"Database error occurred"` - Internal error (logged, not exposed)
