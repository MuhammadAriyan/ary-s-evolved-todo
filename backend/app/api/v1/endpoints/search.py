"""Search API endpoints for intelligent task search."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlmodel import Session
from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field

from app.database import get_session
from app.api.deps import get_current_user
from app.services.search_service import SearchService
from app.models.task import Task


router = APIRouter()


class SearchResult(BaseModel):
    """Search result with task and relevance score."""
    task: Task
    score: float
    highlighted_title: Optional[str] = None
    highlighted_description: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response with results and metadata."""
    results: List[SearchResult]
    total: int
    query: str
    filters_applied: dict


class SearchSuggestion(BaseModel):
    """Search suggestion response."""
    suggestions: List[str]


@router.get("/tasks", response_model=SearchResponse)
async def search_tasks(
    q: str = Query(..., min_length=1, description="Search query text"),
    status: Optional[str] = Query(None, regex="^(completed|pending)$", description="Filter by status"),
    priority: Optional[str] = Query(None, regex="^(High|Medium|Low)$", description="Filter by priority"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags (OR condition)"),
    date_from: Optional[date] = Query(None, description="Filter tasks due on or after this date"),
    date_to: Optional[date] = Query(None, description="Filter tasks due on or before this date"),
    fuzzy: bool = Query(False, description="Enable fuzzy search for typo tolerance"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Search tasks with full-text search and optional filters.

    Supports:
    - Full-text search across title, description, tags, notes
    - Relevance ranking with ts_rank
    - Fuzzy search for typo tolerance (pg_trgm)
    - Filters: status, priority, tags, date range
    - Result highlighting

    Example queries:
    - "client meeting" - Find tasks about client meetings
    - "urgent bug fix" - Find urgent bug fix tasks
    - "meetng" (with fuzzy=true) - Typo-tolerant search
    """
    user_id = current_user["id"]

    # Initialize search service
    search_service = SearchService(session)

    # Perform search
    try:
        tasks, scores = search_service.search_tasks(
            user_id=user_id,
            query_text=q,
            status=status,
            priority=priority,
            tags=tags,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
            use_fuzzy=fuzzy,
            fuzzy_threshold=0.3
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

    # Generate highlighted results
    results = []
    for task, score in zip(tasks, scores):
        try:
            highlights = search_service.highlight_matches(task, q)
            results.append(SearchResult(
                task=task,
                score=score,
                highlighted_title=highlights.get('title'),
                highlighted_description=highlights.get('description')
            ))
        except Exception:
            # Fall back to non-highlighted results if highlighting fails
            results.append(SearchResult(
                task=task,
                score=score,
                highlighted_title=task.title,
                highlighted_description=task.description
            ))

    # Build filters metadata
    filters_applied = {
        "status": status,
        "priority": priority,
        "tags": tags,
        "date_from": date_from.isoformat() if date_from else None,
        "date_to": date_to.isoformat() if date_to else None,
        "fuzzy": fuzzy
    }

    return SearchResponse(
        results=results,
        total=len(results),
        query=q,
        filters_applied=filters_applied
    )


@router.get("/suggestions", response_model=SearchSuggestion)
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Partial search query"),
    limit: int = Query(5, ge=1, le=10, description="Maximum number of suggestions"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get search suggestions based on partial query.
    Returns suggested search terms from user's existing tasks.
    """
    user_id = current_user["id"]

    search_service = SearchService(session)
    suggestions = search_service.get_search_suggestions(user_id, q, limit)

    return SearchSuggestion(suggestions=suggestions)


@router.get("/popular", response_model=SearchSuggestion)
async def get_popular_searches(
    limit: int = Query(10, ge=1, le=20, description="Maximum number of popular terms"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get popular search terms from user's tasks.
    Returns most common tags and keywords.
    """
    user_id = current_user["id"]

    search_service = SearchService(session)
    popular = search_service.get_popular_searches(user_id, limit)

    return SearchSuggestion(suggestions=popular)
