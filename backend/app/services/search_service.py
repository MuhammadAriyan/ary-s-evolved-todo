"""Search service with PostgreSQL full-text search and fuzzy matching."""
from sqlalchemy import func, text, or_
from sqlmodel import Session, select
from typing import List, Optional, Tuple
from datetime import date

from app.models.task import Task


class SearchService:
    """Service for intelligent task search with relevance ranking."""

    def __init__(self, session: Session):
        self.session = session

    def search_tasks(
        self,
        user_id: str,
        query_text: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: int = 20,
        offset: int = 0,
        use_fuzzy: bool = False,
        fuzzy_threshold: float = 0.3
    ) -> Tuple[List[Task], List[float]]:
        """
        Search tasks with full-text search and optional filters.

        Args:
            user_id: User ID for task isolation
            query_text: Search query text
            status: Filter by completion status ('completed', 'pending', or None for all)
            priority: Filter by priority ('High', 'Medium', 'Low', or None)
            tags: Filter by tags (OR condition)
            date_from: Filter tasks due on or after this date
            date_to: Filter tasks due on or before this date
            limit: Maximum number of results
            offset: Pagination offset
            use_fuzzy: Enable fuzzy search for typo tolerance
            fuzzy_threshold: Similarity threshold for fuzzy search (0.0-1.0)

        Returns:
            Tuple of (tasks, relevance_scores)
        """
        if use_fuzzy:
            return self._fuzzy_search(
                user_id, query_text, status, priority, tags,
                date_from, date_to, limit, offset, fuzzy_threshold
            )

        return self._fulltext_search(
            user_id, query_text, status, priority, tags,
            date_from, date_to, limit, offset
        )

    def _fulltext_search(
        self,
        user_id: str,
        query_text: str,
        status: Optional[str],
        priority: Optional[str],
        tags: Optional[List[str]],
        date_from: Optional[date],
        date_to: Optional[date],
        limit: int,
        offset: int
    ) -> Tuple[List[Task], List[float]]:
        """Full-text search with ts_rank relevance scoring."""

        # Convert query to tsquery format (handle special characters)
        # Replace spaces with & for AND queries
        tsquery_text = ' & '.join(query_text.split())
        tsquery = func.to_tsquery('english', tsquery_text)

        # Build query with ranking
        # Normalization flag 1 = divide by 1 + log(document length)
        rank_expr = func.ts_rank(Task.search_vector, tsquery, 1).label('rank')

        stmt = (
            select(Task, rank_expr)
            .where(Task.user_id == user_id)
            .where(Task.search_vector.op('@@')(tsquery))
        )

        # Apply filters
        stmt = self._apply_filters(stmt, status, priority, tags, date_from, date_to)

        # Order by relevance and apply pagination
        stmt = stmt.order_by(text('rank DESC')).limit(limit).offset(offset)

        results = self.session.exec(stmt).all()

        if not results:
            return [], []

        tasks = [task for task, _ in results]
        scores = [float(rank) for _, rank in results]

        return tasks, scores

    def _fuzzy_search(
        self,
        user_id: str,
        query_text: str,
        status: Optional[str],
        priority: Optional[str],
        tags: Optional[List[str]],
        date_from: Optional[date],
        date_to: Optional[date],
        limit: int,
        offset: int,
        threshold: float
    ) -> Tuple[List[Task], List[float]]:
        """Fuzzy search using pg_trgm for typo tolerance."""

        # Try full-text search first
        tasks, scores = self._fulltext_search(
            user_id, query_text, status, priority, tags,
            date_from, date_to, limit, offset
        )

        if tasks:
            return tasks, scores

        # Fall back to fuzzy search with trigram similarity
        search_text = func.concat(
            Task.title, ' ',
            func.coalesce(Task.description, '')
        )

        similarity_expr = func.similarity(search_text, query_text).label('similarity')

        stmt = (
            select(Task, similarity_expr)
            .where(Task.user_id == user_id)
            .where(func.similarity(search_text, query_text) > threshold)
        )

        # Apply filters
        stmt = self._apply_filters(stmt, status, priority, tags, date_from, date_to)

        # Order by similarity
        stmt = stmt.order_by(text('similarity DESC')).limit(limit).offset(offset)

        results = self.session.exec(stmt).all()

        if not results:
            return [], []

        tasks = [task for task, _ in results]
        scores = [float(sim) for _, sim in results]

        return tasks, scores

    def _apply_filters(
        self,
        stmt,
        status: Optional[str],
        priority: Optional[str],
        tags: Optional[List[str]],
        date_from: Optional[date],
        date_to: Optional[date]
    ):
        """Apply optional filters to search query."""

        # Status filter
        if status == 'completed':
            stmt = stmt.where(Task.completed == True)
        elif status == 'pending':
            stmt = stmt.where(Task.completed == False)

        # Priority filter
        if priority:
            stmt = stmt.where(Task.priority == priority)

        # Tags filter (OR condition - match any tag)
        if tags:
            tag_conditions = [Task.tags.contains([tag]) for tag in tags]
            stmt = stmt.where(or_(*tag_conditions))

        # Date range filters
        if date_from:
            stmt = stmt.where(Task.due_date >= date_from)
        if date_to:
            stmt = stmt.where(Task.due_date <= date_to)

        return stmt

    def get_search_suggestions(
        self,
        user_id: str,
        partial_query: str,
        limit: int = 5
    ) -> List[str]:
        """
        Get search suggestions based on partial query.
        Returns list of suggested search terms from existing tasks.
        """
        if len(partial_query) < 2:
            return []

        # Use trigram similarity to find similar titles
        stmt = (
            select(Task.title)
            .where(Task.user_id == user_id)
            .where(func.similarity(Task.title, partial_query) > 0.2)
            .order_by(func.similarity(Task.title, partial_query).desc())
            .limit(limit)
        )

        results = self.session.exec(stmt).all()
        return list(results)

    def highlight_matches(
        self,
        task: Task,
        query_text: str
    ) -> dict:
        """
        Generate highlighted snippets for search results.
        Returns dict with highlighted title and description.
        """
        tsquery_text = ' & '.join(query_text.split())
        tsquery = func.to_tsquery('english', tsquery_text)

        # Generate highlighted title
        title_highlight = self.session.exec(
            select(
                func.ts_headline(
                    'english',
                    task.title,
                    tsquery,
                    'StartSel=<mark>, StopSel=</mark>, MaxWords=15, MinWords=5'
                )
            )
        ).first()

        # Generate highlighted description
        desc_highlight = None
        if task.description:
            desc_highlight = self.session.exec(
                select(
                    func.ts_headline(
                        'english',
                        task.description,
                        tsquery,
                        'StartSel=<mark>, StopSel=</mark>, MaxWords=30, MinWords=10'
                    )
                )
            ).first()

        return {
            'title': title_highlight or task.title,
            'description': desc_highlight or task.description
        }

    def get_popular_searches(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[str]:
        """
        Get popular search terms from user's tasks.
        Returns most common words from task titles and tags.
        """
        # Get most common tags
        stmt = (
            select(func.unnest(Task.tags).label('tag'), func.count().label('count'))
            .where(Task.user_id == user_id)
            .group_by(text('tag'))
            .order_by(text('count DESC'))
            .limit(limit)
        )

        results = self.session.exec(stmt).all()
        return [tag for tag, _ in results]
