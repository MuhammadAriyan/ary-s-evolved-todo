# Phase V Event-Driven Cloud Deployment Research

## Overview
This document provides comprehensive research on:
1. **PostgreSQL Full-Text Search** - High-performance search implementation
2. **Oracle OKE Deployment** - Microservices deployment on Oracle Cloud free tier with Dapr runtime

---

# Part 1: PostgreSQL Full-Text Search Research

## Overview
This section provides comprehensive research on implementing high-performance full-text search for a task management application using PostgreSQL. The goal is to achieve sub-second search response times with 10,000+ tasks while supporting fuzzy matching, relevance ranking, and multi-column search.

---

## 1. tsvector Column Design and Automatic Update Triggers

### What is tsvector?
`tsvector` is PostgreSQL's data type for storing preprocessed text optimized for full-text search. It contains lexemes (normalized words) with position information.

### Design Patterns

#### Pattern 1: Dedicated tsvector Column (Recommended)
Store a computed `tsvector` column that combines multiple text fields with different weights.

```sql
-- Add tsvector column to tasks table
ALTER TABLE tasks
ADD COLUMN search_vector tsvector;

-- Create weighted search vector combining multiple columns
-- A = highest weight (title), B = high (description), C = medium (tags), D = low (notes)
UPDATE tasks
SET search_vector =
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(array_to_string(tags, ' '), '')), 'C') ||
    setweight(to_tsvector('english', COALESCE(notes, '')), 'D');
```

#### Pattern 2: Automatic Update Trigger (Critical for Performance)
Automatically maintain the search_vector column on INSERT/UPDATE operations.

```sql
-- Create trigger function to update search_vector
CREATE OR REPLACE FUNCTION tasks_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(array_to_string(NEW.tags, ' '), '')), 'C') ||
        setweight(to_tsvector('english', COALESCE(NEW.notes, '')), 'D');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to tasks table
CREATE TRIGGER tasks_search_vector_trigger
BEFORE INSERT OR UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION tasks_search_vector_update();
```

### Language Configuration
PostgreSQL supports multiple text search configurations (dictionaries):
- `english` - English stemming (running → run, tasks → task)
- `simple` - No stemming, case-insensitive
- `pg_catalog.simple` - For technical terms, IDs, codes

```sql
-- Mixed language support example
NEW.search_vector :=
    setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
    setweight(to_tsvector('simple', COALESCE(NEW.task_id, '')), 'A');  -- Don't stem IDs
```

### SQLModel Integration Pattern

```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import TSVECTOR

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int = Field(primary_key=True)
    title: str
    description: str | None = None
    tags: list[str] = Field(sa_column=Column(ARRAY(String)))
    notes: str | None = None

    # tsvector column - maintained by trigger
    search_vector: str | None = Field(
        default=None,
        sa_column=Column(TSVECTOR, nullable=True)
    )
```

---

## 2. GIN Index Configuration for Optimal Search Performance

### GIN vs GiST Indexes
- **GIN (Generalized Inverted Index)**: Faster searches, slower updates, larger size
- **GiST (Generalized Search Tree)**: Faster updates, slower searches, smaller size

**Recommendation**: Use GIN for read-heavy workloads (typical for search).

### Creating GIN Index

```sql
-- Basic GIN index on search_vector
CREATE INDEX idx_tasks_search_vector
ON tasks
USING GIN(search_vector);

-- GIN index with fast update option (reduces insert/update overhead)
CREATE INDEX idx_tasks_search_vector_fastupdate
ON tasks
USING GIN(search_vector)
WITH (fastupdate = on);
```

### GIN Index Tuning Parameters

```sql
-- Optimize GIN index for better performance
ALTER INDEX idx_tasks_search_vector
SET (fastupdate = on);  -- Batch pending updates

ALTER INDEX idx_tasks_search_vector
SET (gin_pending_list_limit = 4096);  -- 4MB pending list (default 4MB)

-- For very high write loads, consider:
-- gin_pending_list_limit = 16384 (16MB)
```

### Multi-Column GIN Indexes

```sql
-- Composite index for filtered searches
CREATE INDEX idx_tasks_search_user_completed
ON tasks
USING GIN(search_vector)
WHERE completed = false;  -- Partial index for active tasks only

-- Index for user-specific searches
CREATE INDEX idx_tasks_search_by_user
ON tasks (user_id)
INCLUDE (search_vector);  -- Covering index
```

### Index Maintenance

```sql
-- Check index bloat
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%search%';

-- Rebuild bloated index
REINDEX INDEX CONCURRENTLY idx_tasks_search_vector;

-- Vacuum to reclaim space
VACUUM ANALYZE tasks;
```

---

## 3. ts_rank Relevance Scoring and Ranking Strategies

### Basic ts_rank Usage

```sql
-- Simple relevance ranking
SELECT
    id,
    title,
    ts_rank(search_vector, to_tsquery('english', 'urgent & meeting')) as rank
FROM tasks
WHERE search_vector @@ to_tsquery('english', 'urgent & meeting')
ORDER BY rank DESC
LIMIT 20;
```

### ts_rank vs ts_rank_cd

- **ts_rank**: Considers word frequency (TF-IDF style)
- **ts_rank_cd**: Considers word proximity (cover density)

```sql
-- ts_rank_cd for phrase-sensitive ranking
SELECT
    id,
    title,
    ts_rank_cd(search_vector, query, 32) as rank  -- 32 = normalize by document length
FROM tasks, to_tsquery('english', 'project & deadline') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### Normalization Options (Bitmask)

```sql
-- Normalization flags (can be combined with |)
-- 0  = no normalization (default)
-- 1  = divide by 1 + log(document length)
-- 2  = divide by document length
-- 4  = divide by mean harmonic distance between extents
-- 8  = divide by number of unique words
-- 16 = divide by 1 + log(number of unique words)
-- 32 = divide by rank itself + 1

-- Recommended: normalize by document length to avoid bias toward long documents
SELECT
    id,
    title,
    ts_rank(search_vector, query, 1) as rank  -- Normalize by log(length)
FROM tasks, to_tsquery('english', 'important') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### Advanced Ranking with Custom Weights

```sql
-- Custom weight vector [D-weight, C-weight, B-weight, A-weight]
-- Default is {0.1, 0.2, 0.4, 1.0}
SELECT
    id,
    title,
    ts_rank(
        search_vector,
        query,
        1,  -- normalization
        '{0.05, 0.1, 0.3, 1.0}'::float4[]  -- Custom weights: title >> description >> tags >> notes
    ) as rank
FROM tasks, to_tsquery('english', 'bug & fix') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### Boosting Recent Tasks

```sql
-- Combine relevance with recency
SELECT
    id,
    title,
    (
        ts_rank(search_vector, query, 1) * 0.7 +  -- 70% relevance
        (EXTRACT(EPOCH FROM NOW() - created_at) / 86400.0)^(-0.5) * 0.3  -- 30% recency
    ) as combined_score
FROM tasks, to_tsquery('english', 'review') query
WHERE search_vector @@ query
ORDER BY combined_score DESC;
```

### SQLModel Integration

```python
from sqlalchemy import func, text
from sqlmodel import select

def search_tasks(session, query_text: str, user_id: int, limit: int = 20):
    """Search tasks with relevance ranking"""

    # Convert query to tsquery format
    tsquery = func.to_tsquery('english', query_text)

    # Build query with ranking
    stmt = (
        select(
            Task,
            func.ts_rank(
                Task.search_vector,
                tsquery,
                1  # Normalize by log(length)
            ).label('rank')
        )
        .where(Task.user_id == user_id)
        .where(Task.search_vector.op('@@')(tsquery))
        .order_by(text('rank DESC'))
        .limit(limit)
    )

    results = session.exec(stmt).all()
    return [(task, rank) for task, rank in results]
```

---

## 4. Fuzzy Search with pg_trgm Extension for Typo Tolerance

### Enable pg_trgm Extension

```sql
-- Enable trigram extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Trigram Similarity Search

```sql
-- Find tasks with similar titles (typo tolerance)
SELECT
    id,
    title,
    similarity(title, 'importent meeting') as sim
FROM tasks
WHERE similarity(title, 'importent meeting') > 0.3  -- 30% similarity threshold
ORDER BY sim DESC
LIMIT 10;
```

### GIN Index for Trigram Search

```sql
-- Create GIN index for trigram operations
CREATE INDEX idx_tasks_title_trgm
ON tasks
USING GIN(title gin_trgm_ops);

CREATE INDEX idx_tasks_description_trgm
ON tasks
USING GIN(description gin_trgm_ops);

-- For array columns (tags)
CREATE INDEX idx_tasks_tags_trgm
ON tasks
USING GIN(tags array_ops);
```

### Combining Full-Text Search with Fuzzy Matching

```sql
-- Hybrid approach: try exact match first, fall back to fuzzy
WITH exact_matches AS (
    SELECT
        id, title, description,
        ts_rank(search_vector, query, 1) as rank,
        'exact' as match_type
    FROM tasks, to_tsquery('english', 'importent & meting') query
    WHERE search_vector @@ query
),
fuzzy_matches AS (
    SELECT
        id, title, description,
        similarity(title || ' ' || COALESCE(description, ''), 'importent meting') as rank,
        'fuzzy' as match_type
    FROM tasks
    WHERE similarity(title || ' ' || COALESCE(description, ''), 'importent meting') > 0.3
    AND id NOT IN (SELECT id FROM exact_matches)
)
SELECT * FROM exact_matches
UNION ALL
SELECT * FROM fuzzy_matches
ORDER BY rank DESC
LIMIT 20;
```

### Levenshtein Distance for Typo Correction

```sql
-- Find closest matches using edit distance
SELECT
    id,
    title,
    levenshtein(lower(title), 'importent meeting') as distance
FROM tasks
WHERE levenshtein(lower(title), 'importent meeting') <= 3  -- Max 3 character edits
ORDER BY distance
LIMIT 10;
```

### SQLModel Integration with Fuzzy Search

```python
from sqlalchemy import func

def fuzzy_search_tasks(session, query_text: str, user_id: int, threshold: float = 0.3):
    """Fuzzy search with typo tolerance"""

    # Try full-text search first
    tsquery = func.to_tsquery('english', query_text)
    exact_stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(Task.search_vector.op('@@')(tsquery))
        .limit(20)
    )
    exact_results = session.exec(exact_stmt).all()

    if exact_results:
        return exact_results

    # Fall back to fuzzy search
    fuzzy_stmt = (
        select(Task)
        .where(Task.user_id == user_id)
        .where(
            func.similarity(
                func.concat(Task.title, ' ', func.coalesce(Task.description, '')),
                query_text
            ) > threshold
        )
        .order_by(
            func.similarity(
                func.concat(Task.title, ' ', func.coalesce(Task.description, '')),
                query_text
            ).desc()
        )
        .limit(20)
    )

    return session.exec(fuzzy_stmt).all()
```

---

## 5. Multi-Column Search Across Titles, Descriptions, Tags, Notes

### Weighted Multi-Column Search (Already Covered in Section 1)

The tsvector approach with weights is the recommended pattern:

```sql
-- Search across all columns with appropriate weights
SELECT
    id,
    title,
    description,
    tags,
    ts_rank(search_vector, query, 1) as rank,
    ts_headline('english', title, query, 'MaxWords=10, MinWords=5') as title_highlight,
    ts_headline('english', description, query, 'MaxWords=20, MinWords=10') as desc_highlight
FROM tasks, to_tsquery('english', 'urgent & bug & fix') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### Search Result Highlighting

```sql
-- Highlight matching terms in results
SELECT
    id,
    ts_headline(
        'english',
        title,
        query,
        'StartSel=<mark>, StopSel=</mark>, MaxWords=15, MinWords=5, ShortWord=3'
    ) as highlighted_title,
    ts_headline(
        'english',
        description,
        query,
        'StartSel=<mark>, StopSel=</mark>, MaxWords=30, MinWords=10'
    ) as highlighted_description
FROM tasks, to_tsquery('english', 'database & optimization') query
WHERE search_vector @@ query
ORDER BY ts_rank(search_vector, query, 1) DESC;
```

### Tag-Specific Search

```sql
-- Search specifically in tags (array column)
SELECT id, title, tags
FROM tasks
WHERE 'urgent' = ANY(tags)
   OR 'high-priority' = ANY(tags);

-- Combine tag search with full-text search
SELECT
    id, title, tags,
    ts_rank(search_vector, query, 1) as rank
FROM tasks, to_tsquery('english', 'meeting') query
WHERE (search_vector @@ query OR 'urgent' = ANY(tags))
ORDER BY rank DESC NULLS LAST;
```

### SQLModel Multi-Column Search

```python
from sqlalchemy import or_, any_

def advanced_search(
    session,
    query_text: str,
    user_id: int,
    tags: list[str] | None = None,
    search_notes: bool = True,
    limit: int = 20
):
    """Advanced multi-column search with optional filters"""

    tsquery = func.to_tsquery('english', query_text)

    stmt = (
        select(
            Task,
            func.ts_rank(Task.search_vector, tsquery, 1).label('rank'),
            func.ts_headline(
                'english',
                Task.title,
                tsquery,
                'StartSel=<mark>, StopSel=</mark>'
            ).label('highlighted_title')
        )
        .where(Task.user_id == user_id)
    )

    # Build search conditions
    conditions = [Task.search_vector.op('@@')(tsquery)]

    # Add tag filter if specified
    if tags:
        tag_conditions = [Task.tags.contains([tag]) for tag in tags]
        conditions.append(or_(*tag_conditions))

    stmt = stmt.where(or_(*conditions))
    stmt = stmt.order_by(text('rank DESC')).limit(limit)

    return session.exec(stmt).all()
```

---

## 6. Search Query Optimization for <1 Second Response Time with 10,000+ Tasks

### Query Performance Checklist

1. **Use GIN indexes** (covered in Section 2)
2. **Limit result sets** (LIMIT clause)
3. **Use covering indexes** (INCLUDE clause)
4. **Partition large tables** (if >1M rows)
5. **Use materialized views** for complex aggregations
6. **Enable query plan caching**

### Optimized Query Pattern

```sql
-- Optimized search query with all best practices
EXPLAIN ANALYZE
SELECT
    id,
    title,
    description,
    tags,
    created_at,
    ts_rank(search_vector, query, 1) as rank
FROM tasks, to_tsquery('english', 'urgent & meeting') query
WHERE
    user_id = 123  -- Filter by user first (indexed)
    AND completed = false  -- Use partial index
    AND search_vector @@ query  -- Full-text search (GIN indexed)
ORDER BY rank DESC
LIMIT 20;  -- Always limit results

-- Expected execution time: 5-50ms for 10,000 tasks
```

### Covering Index for Common Queries

```sql
-- Create covering index to avoid table lookups
CREATE INDEX idx_tasks_search_covering
ON tasks (user_id, completed)
INCLUDE (id, title, description, tags, created_at, search_vector);

-- This allows index-only scans for common queries
```

### Pagination with Cursor-Based Approach

```sql
-- Avoid OFFSET for large result sets (slow)
-- Use cursor-based pagination instead

-- First page
SELECT id, title, rank
FROM (
    SELECT
        id, title,
        ts_rank(search_vector, query, 1) as rank
    FROM tasks, to_tsquery('english', 'project') query
    WHERE user_id = 123 AND search_vector @@ query
    ORDER BY rank DESC, id DESC
    LIMIT 20
) sub;

-- Next page (using last_rank and last_id from previous page)
SELECT id, title, rank
FROM (
    SELECT
        id, title,
        ts_rank(search_vector, query, 1) as rank
    FROM tasks, to_tsquery('english', 'project') query
    WHERE
        user_id = 123
        AND search_vector @@ query
        AND (rank, id) < (0.5, 12345)  -- Cursor from last page
    ORDER BY rank DESC, id DESC
    LIMIT 20
) sub;
```

### Query Plan Analysis

```sql
-- Analyze query performance
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT id, title, ts_rank(search_vector, query, 1) as rank
FROM tasks, to_tsquery('english', 'urgent') query
WHERE user_id = 123 AND search_vector @@ query
ORDER BY rank DESC
LIMIT 20;

-- Look for:
-- - "Index Scan" or "Bitmap Index Scan" (good)
-- - "Seq Scan" (bad - missing index)
-- - Execution time < 100ms (target)
```

### Connection Pooling Configuration

```python
# SQLModel/SQLAlchemy connection pool settings
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:pass@host/db",
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=10,  # Additional connections under load
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Disable SQL logging in production
)
```

### Caching Strategy

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache search results for 5 minutes
@lru_cache(maxsize=1000)
def cached_search(query_text: str, user_id: int, timestamp: int):
    """Cache search results with 5-minute TTL"""
    # timestamp is rounded to 5-minute intervals
    return search_tasks(session, query_text, user_id)

def search_with_cache(query_text: str, user_id: int):
    # Round timestamp to 5-minute intervals
    now = datetime.now()
    cache_key = int(now.timestamp() // 300)  # 300 seconds = 5 minutes
    return cached_search(query_text, user_id, cache_key)
```

---

## 7. Index Maintenance and Performance Monitoring

### Regular Maintenance Tasks

```sql
-- 1. Update table statistics (run weekly or after bulk changes)
ANALYZE tasks;

-- 2. Vacuum to reclaim space (run weekly)
VACUUM ANALYZE tasks;

-- 3. Reindex if index bloat detected (run monthly or as needed)
REINDEX INDEX CONCURRENTLY idx_tasks_search_vector;

-- 4. Check for missing indexes
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'tasks'
ORDER BY n_distinct DESC;
```

### Performance Monitoring Queries

```sql
-- Monitor index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE tablename = 'tasks'
ORDER BY idx_scan DESC;

-- Identify slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
WHERE query LIKE '%tasks%' AND query LIKE '%search_vector%'
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check index bloat
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    CASE
        WHEN idx_scan = 0 THEN 'UNUSED'
        WHEN idx_tup_read = 0 THEN 'NEVER_READ'
        ELSE 'ACTIVE'
    END as status
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Automated Monitoring with pg_stat_statements

```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Add to postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.track = all
-- pg_stat_statements.max = 10000

-- Query to find slow search queries
SELECT
    substring(query, 1, 100) as short_query,
    calls,
    round(total_exec_time::numeric, 2) as total_time_ms,
    round(mean_exec_time::numeric, 2) as avg_time_ms,
    round(stddev_exec_time::numeric, 2) as stddev_time_ms,
    round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) as pct_total
FROM pg_stat_statements
WHERE query LIKE '%search_vector%'
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Health Check Script

```python
from sqlalchemy import text

def check_search_health(session):
    """Run health checks on search infrastructure"""

    results = {}

    # Check if indexes exist
    index_check = session.exec(text("""
        SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid)) as size
        FROM pg_stat_user_indexes
        WHERE tablename = 'tasks' AND indexname LIKE '%search%'
    """)).all()
    results['indexes'] = index_check

    # Check index usage
    usage_check = session.exec(text("""
        SELECT indexname, idx_scan, idx_tup_read
        FROM pg_stat_user_indexes
        WHERE tablename = 'tasks' AND indexname LIKE '%search%'
    """)).all()
    results['index_usage'] = usage_check

    # Check table statistics freshness
    stats_check = session.exec(text("""
        SELECT
            schemaname,
            tablename,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        WHERE tablename = 'tasks'
    """)).first()
    results['statistics'] = stats_check

    # Check for bloat
    bloat_check = session.exec(text("""
        SELECT
            pg_size_pretty(pg_total_relation_size('tasks')) as total_size,
            pg_size_pretty(pg_relation_size('tasks')) as table_size,
            pg_size_pretty(pg_total_relation_size('tasks') - pg_relation_size('tasks')) as index_size
    """)).first()
    results['bloat'] = bloat_check

    return results
```

### Performance Benchmarking

```python
import time
from statistics import mean, stdev

def benchmark_search(session, query_text: str, iterations: int = 100):
    """Benchmark search query performance"""

    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        results = search_tasks(session, query_text, user_id=1, limit=20)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds

    return {
        'mean_ms': mean(times),
        'stddev_ms': stdev(times),
        'min_ms': min(times),
        'max_ms': max(times),
        'p95_ms': sorted(times)[int(len(times) * 0.95)],
        'p99_ms': sorted(times)[int(len(times) * 0.99)],
    }
```

---

## Summary and Recommendations

### Implementation Checklist

- [ ] Add `search_vector` tsvector column to tasks table
- [ ] Create automatic update trigger for search_vector
- [ ] Create GIN index on search_vector with fastupdate
- [ ] Enable pg_trgm extension for fuzzy search
- [ ] Create trigram indexes on title and description
- [ ] Implement ts_rank relevance scoring in queries
- [ ] Add covering indexes for common query patterns
- [ ] Set up connection pooling (20 connections, 10 overflow)
- [ ] Implement cursor-based pagination
- [ ] Add query result caching (5-minute TTL)
- [ ] Schedule weekly VACUUM ANALYZE
- [ ] Schedule monthly REINDEX CONCURRENTLY
- [ ] Enable pg_stat_statements for monitoring
- [ ] Create health check and benchmark scripts

### Expected Performance

With proper implementation:
- **Search latency**: 10-50ms for 10,000 tasks
- **Index size**: ~2-5MB for 10,000 tasks
- **Memory usage**: ~50-100MB for search operations
- **Write overhead**: <5ms per INSERT/UPDATE (trigger + index update)

### Migration Path

1. **Phase 1**: Add search_vector column and trigger
2. **Phase 2**: Create GIN index and backfill existing data
3. **Phase 3**: Update application code to use full-text search
4. **Phase 4**: Add fuzzy search with pg_trgm
5. **Phase 5**: Implement caching and monitoring

### References

- PostgreSQL Full-Text Search Documentation: https://www.postgresql.org/docs/current/textsearch.html
- pg_trgm Extension: https://www.postgresql.org/docs/current/pgtrgm.html
- GIN Indexes: https://www.postgresql.org/docs/current/gin.html
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- PostgreSQL Performance Tuning: https://wiki.postgresql.org/wiki/Performance_Optimization

---

# Part 2: Kafka Event-Driven Architecture - Comprehensive Use Cases

## Overview

This section provides comprehensive Kafka use cases for Phase V event-driven microservices architecture using Redpanda Cloud (Kafka-compatible) with Dapr Pub/Sub integration.

**Event Streaming Platform**: Redpanda Cloud (Kafka-compatible)
**Integration Layer**: Dapr Pub/Sub component
**Delivery Guarantee**: At-least-once semantics
**Event Ordering**: Partition key-based (per task_id or user_id)

---

## Core Kafka Topics Architecture

| Topic Name | Purpose | Producers | Consumers | Partition Key | Retention |
|------------|---------|-----------|-----------|---------------|-----------|
| `task-events` | All task lifecycle events | Backend API | Audit Service, Recurring Task Service | `task_id` | 7 days |
| `task-updates` | Real-time sync events | Backend API | WebSocket Sync Service | `user_id` | 1 hour |
| `reminders` | Scheduled reminder triggers | Backend API | Notification Service | `user_id` | 24 hours |
| `collaboration-events` | Comments, assignments, mentions | Backend API | WebSocket Sync Service, Notification Service | `group_id` or `user_id` | 3 days |
| `friend-activity` | Friend status, messages | Backend API | WebSocket Sync Service | `user_id` | 1 day |
| `search-index-updates` | Search index refresh triggers | Backend API | Search Indexer Service | `task_id` | 1 hour |
| `dead-letter-queue` | Failed event processing | All consumers | Manual review/replay | `original_topic` | 30 days |

---

## Use Case 1: Reminders / Notifications

**Flow**: Todo Service → `reminders` topic → Notification Service → User Device

### Event Flow Diagram

```
1. User sets task due date/reminder
   ↓
2. Backend API publishes to `reminders` topic
   Event: { task_id, user_id, reminder_time, notification_channels }
   ↓
3. Notification Service (Dapr Bindings cron consumer)
   - Schedules reminder using Dapr Bindings API
   - Stores scheduled job in Redis state store
   ↓
4. At reminder_time, Dapr Bindings triggers callback
   ↓
5. Notification Service delivers via channels:
   - In-app notification (WebSocket)
   - Email (SendGrid/AWS SES)
   - Push notification (optional)
```

### Event Schema

```json
{
  "event_type": "reminder.scheduled",
  "event_id": "uuid-v4",
  "timestamp": "2026-01-31T14:30:00Z",
  "task_id": "task-123",
  "user_id": "user-456",
  "reminder_time": "2026-02-01T09:00:00Z",
  "notification_channels": ["in_app", "email"],
  "cron_expression": null,
  "timezone": "America/New_York",
  "metadata": {
    "task_title": "Team meeting",
    "task_priority": "high"
  }
}
```

### Dapr Bindings Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: reminder-cron
spec:
  type: bindings.cron
  version: v1
  metadata:
  - name: schedule
    value: "@every 1m"  # Check for due reminders every minute
  - name: direction
    value: "input"
```

### Error Handling & Retry Strategy

- **Delivery Failure**: Exponential backoff (5s, 10s, 30s, 1m, 5m)
- **Max Retries**: 10 attempts before dead letter queue
- **Idempotency**: Redis state store check (key: `reminder:{task_id}:{reminder_time}`)
- **Circuit Breaker**: Email service fails 5x in 1 minute → switch to in-app only

### Performance Optimization

- **Batch Processing**: Group reminders by user_id to reduce API calls
- **Time Window**: Process in 1-minute windows (not exact second)
- **Timezone Handling**: Store UTC in events, convert at delivery

---

## Use Case 2: Recurring Tasks

**Flow**: Task Completed → `task-events` topic → Recurring Task Service → Auto-create next occurrence

### Event Flow Diagram

```
1. User completes a recurring task
   ↓
2. Backend API publishes to `task-events` topic
   Event: { event_type: "task.completed", task_id, recurring_pattern }
   ↓
3. Recurring Task Service consumes event
   - Checks if task has recurring_pattern
   - Calculates next occurrence using cron parser
   - Creates new task instance via Backend API
   ↓
4. Backend API publishes to `task-events` topic
   Event: { event_type: "task.created", task_id: new_task_id, parent_task_id }
   ↓
5. WebSocket Sync Service broadcasts to user's devices
```

### Event Schema

```json
{
  "event_type": "task.completed",
  "event_id": "uuid-v4",
  "timestamp": "2026-01-31T14:30:00Z",
  "task_id": "task-123",
  "user_id": "user-456",
  "recurring_pattern": {
    "type": "cron",
    "expression": "0 9 * * 1-5",
    "timezone": "America/New_York",
    "end_date": null
  },
  "completed_at": "2026-01-31T14:30:00Z",
  "metadata": {
    "task_title": "Daily standup",
    "recurrence_count": 15
  }
}
```

### Cron Pattern Examples

| Pattern | Description | Cron Expression |
|---------|-------------|-----------------|
| Daily at 9 AM | Every day at 9:00 AM | `0 9 * * *` |
| Weekdays at 9 AM | Monday-Friday at 9:00 AM | `0 9 * * 1-5` |
| First Monday of month | First Monday at 9:00 AM | `0 9 1-7 * 1` |
| Every 3 days | Every 3 days at 9:00 AM | `0 9 */3 * *` |
| Every 4 hours | Every 4 hours | `0 */4 * * *` |

### Error Handling

- **Invalid Cron**: Validate before saving, reject invalid patterns
- **Excessive Frequency**: Reject intervals < 1 minute
- **Creation Failure**: Retry 3x, then alert user
- **Duplicate Prevention**: Idempotency key: `recurring:{parent_task_id}:{next_occurrence_date}`

---

## Use Case 3: Activity / Audit Log

**Flow**: All Task Operations → `task-events` topic → Audit Service → PostgreSQL audit_logs table

### Event Flow Diagram

```
1. Any task operation (create, update, delete, complete, assign, comment)
   ↓
2. Backend API publishes to `task-events` topic
   Event: { event_type, task_id, user_id, before_state, after_state }
   ↓
3. Audit Service consumes ALL events from `task-events`
   - Enriches with IP address, user agent, timestamp
   - Writes to audit_logs table in PostgreSQL
   - Indexes by user_id, task_id, timestamp
   ↓
4. Audit logs available for:
   - Compliance reporting
   - Debugging
   - User activity history
   - Conflict resolution
```

### Event Schema

```json
{
  "event_type": "task.updated",
  "event_id": "uuid-v4",
  "timestamp": "2026-01-31T14:30:00Z",
  "task_id": "task-123",
  "user_id": "user-456",
  "operation": "update",
  "before_state": {
    "title": "Old title",
    "status": "pending",
    "priority": "medium"
  },
  "after_state": {
    "title": "New title",
    "status": "in_progress",
    "priority": "high"
  },
  "metadata": {
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "request_id": "req-789"
  }
}
```

### Performance Optimization

- **Batch Writes**: Buffer 100 events or 5 seconds, write in single transaction
- **Async Processing**: Never blocks main API flow
- **Partitioning**: Partition audit_logs by month
- **Retention**: Archive logs >90 days to cold storage

---

## Use Case 4: Real-time Sync

**Flow**: Task Changed → `task-updates` topic → WebSocket Sync Service → All Connected Clients

### Event Flow Diagram

```
1. Task created/updated/deleted/completed
   ↓
2. Backend API publishes to `task-updates` topic
   Event: { event_type, task_id, user_id, change_summary }
   ↓
3. WebSocket Sync Service consumes event
   - Looks up active WebSocket connections for user_id (Redis state)
   - Broadcasts change to all connected clients
   ↓
4. Frontend receives WebSocket message
   - Updates local state (React hooks)
   - Displays change in UI within 2 seconds
```

### Event Schema

```json
{
  "event_type": "task.updated",
  "event_id": "uuid-v4",
  "timestamp": "2026-01-31T14:30:00Z",
  "task_id": "task-123",
  "user_id": "user-456",
  "change_summary": {
    "fields_changed": ["title", "priority"],
    "changed_by": "user-789"
  },
  "full_task": {
    "id": "task-123",
    "title": "Updated title",
    "status": "in_progress",
    "priority": "high",
    "due_date": "2026-02-01T09:00:00Z"
  }
}
```

### WebSocket Connection Management (Redis State Store)

```python
# Store active connections in Redis via Dapr State API
await dapr_client.save_state(
    store_name="redis-state",
    key=f"ws:user:{user_id}",
    value=connection_ids,  # Set: {"conn-123", "conn-456"}
    state_options={"ttl": 3600}  # 1 hour TTL
)
```

### Performance Optimization

- **Connection Pooling**: 10,000 connections per service instance
- **Horizontal Scaling**: Scale at 8,000 connections per pod
- **Message Compression**: WebSocket compression for large payloads
- **Selective Broadcasting**: Only broadcast to users with task access
- **Debouncing**: Batch multiple updates within 100ms

---

## Use Case 5: Collaboration Events

**Flow**: User comments/assigns task → `collaboration-events` topic → WebSocket + Notification Services

### Event Schema

```json
{
  "event_type": "task.comment.created",
  "event_id": "uuid-v4",
  "timestamp": "2026-01-31T14:30:00Z",
  "task_id": "task-123",
  "group_id": "group-789",
  "comment_id": "comment-456",
  "user_id": "user-111",
  "content": "Hey @user-222, can you review this?",
  "mentioned_users": ["user-222"],
  "metadata": {
    "comment_text": "Hey @user-222, can you review this?",
    "task_title": "Design review"
  }
}
```

---

## Use Case 6: Friend Activity Notifications

**Flow**: Friend status change → `friend-activity` topic → WebSocket Sync Service → Online friends

### Event Schema

```json
{
  "event_type": "friend.status.changed",
  "event_id": "uuid-v4",
  "timestamp": "2026-01-31T14:30:00Z",
  "user_id": "user-456",
  "status": "online",
  "metadata": {
    "last_seen": "2026-01-31T14:30:00Z",
    "activity": "Working on tasks"
  }
}
```

---

## Use Case 7: Search Index Updates

**Flow**: Task changed → `search-index-updates` topic → Search Indexer Service → PostgreSQL tsvector update

### Event Schema

```json
{
  "event_type": "search.index.update",
  "event_id": "uuid-v4",
  "timestamp": "2026-01-31T14:30:00Z",
  "task_id": "task-123",
  "indexable_content": {
    "title": "Team meeting preparation",
    "description": "Prepare slides for quarterly review",
    "tags": ["meeting", "quarterly", "review"]
  }
}
```

---

## Use Case 8: Dead Letter Queue (Error Recovery)

**Flow**: Failed event processing → `dead-letter-queue` topic → Manual review/replay

### Dapr Resiliency Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Resiliency
metadata:
  name: event-resiliency
spec:
  policies:
    retries:
      eventRetry:
        policy: exponential
        maxInterval: 5m
        maxRetries: 10
    circuitBreakers:
      eventCircuitBreaker:
        maxRequests: 5
        timeout: 60s
        trip: consecutiveFailures > 5
  targets:
    components:
      kafka-pubsub:
        inbound:
          retry: eventRetry
          circuitBreaker: eventCircuitBreaker
```

---

## Event-Driven Optimization Strategies

### 1. Event Deduplication (Idempotency)

```python
async def process_event(event):
    event_id = event["event_id"]

    # Check if already processed (Redis state store)
    processed = await dapr_client.get_state(
        store_name="redis-state",
        key=f"processed:{event_id}"
    )

    if processed:
        return  # Skip duplicate

    # Process event
    await handle_event(event)

    # Mark as processed (TTL: 7 days)
    await dapr_client.save_state(
        store_name="redis-state",
        key=f"processed:{event_id}",
        value="true",
        state_options={"ttl": 604800}
    )
```

### 2. Event Ordering Guarantee

```python
# Partition by task_id for task events
await dapr_client.publish_event(
    pubsub_name="kafka-pubsub",
    topic_name="task-events",
    data=event_data,
    metadata={"partitionKey": task_id}  # Same task → same partition
)
```

### 3. Event Replay for Debugging

```bash
# Reset consumer group to replay last 1 hour
kafka-consumer-groups --bootstrap-server redpanda:9092 \
  --group audit-service \
  --topic task-events \
  --reset-offsets --to-datetime 2026-01-31T13:30:00.000 \
  --execute
```

### 4. Event Schema Versioning

```json
{
  "schema_version": "v2",
  "event_type": "task.updated",
  "event_id": "uuid-v4"
}
```

---

## Performance Benchmarks

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Event publish latency | <10ms p95 | Dapr Pub/Sub metrics |
| Event processing latency | <100ms p95 | Consumer processing time |
| WebSocket broadcast latency | <2 seconds end-to-end | Client timestamp - event timestamp |
| Reminder delivery accuracy | ±10 seconds | Scheduled time - actual delivery time |
| Audit log write latency | <5 seconds | Event timestamp - DB write timestamp |
| Search index update latency | <5 seconds | Task update - search availability |

---

## Dapr Pub/Sub Configuration for Redpanda Cloud

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "redpanda-cloud-broker.example.com:9092"
  - name: consumerGroup
    value: "{namespace}"
  - name: authType
    value: "password"
  - name: saslUsername
    value: "redpanda-user"
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: saslPassword
  - name: saslMechanism
    value: "SCRAM-SHA-256"
  - name: maxMessageBytes
    value: "1048576"  # 1MB
  - name: consumeRetryInterval
    value: "200ms"
  - name: version
    value: "2.8.0"
```

---

## Summary

### Implementation Checklist

- [ ] Configure Redpanda Cloud cluster
- [ ] Create 7 Kafka topics with appropriate retention
- [ ] Deploy Dapr runtime to Oracle OKE
- [ ] Configure Dapr Pub/Sub component for Redpanda
- [ ] Configure Dapr State Store component for Redis
- [ ] Configure Dapr Bindings component for cron scheduling
- [ ] Implement event publishers in Backend API
- [ ] Implement 4 event consumer microservices
- [ ] Set up dead letter queue handling
- [ ] Configure resiliency policies (retry, circuit breaker)
- [ ] Implement idempotency checks in all consumers
- [ ] Set up monitoring for event processing metrics
- [ ] Test event replay scenarios
- [ ] Document event schemas in contracts/

### Expected Performance

- **Event throughput**: 1,000 events/second
- **End-to-end latency**: <2 seconds (publish → consume → action)
- **At-least-once delivery**: Guaranteed by Kafka + Dapr
- **Event ordering**: Per partition key (task_id or user_id)
- **Fault tolerance**: Automatic retry with exponential backoff

### References

- Dapr Pub/Sub Documentation: https://docs.dapr.io/developing-applications/building-blocks/pubsub/
- Redpanda Cloud Documentation: https://docs.redpanda.com/
- Kafka Best Practices: https://kafka.apache.org/documentation/
- Event-Driven Architecture Patterns: https://martinfowler.com/articles/201701-event-driven.html
