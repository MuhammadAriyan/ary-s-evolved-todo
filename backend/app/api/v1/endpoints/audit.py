"""Audit log API endpoints."""
from fastapi import APIRouter, Depends, Query, HTTPException, Response
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel

from app.database import get_session
from app.api.deps import get_current_user
from app.models.audit_log import AuditLog


router = APIRouter()


class AuditLogResponse(BaseModel):
    """Audit log response model."""
    id: int
    event_id: str
    event_type: str
    task_id: Optional[str]
    user_id: str
    operation: str
    before_state: Optional[dict]
    after_state: Optional[dict]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Audit log list response."""
    logs: List[AuditLogResponse]
    total: int


class ExportRequest(BaseModel):
    """Export request model."""
    format: str  # 'json' or 'csv'
    task_id: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None


@router.get("/tasks/{task_id}", response_model=AuditLogListResponse)
async def get_task_audit_logs(
    task_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get audit logs for a specific task.

    Returns complete change history for the task, ordered by timestamp (newest first).
    """
    user_id = current_user["id"]

    # Build query
    stmt = (
        select(AuditLog)
        .where(AuditLog.task_id == task_id)
        .where(AuditLog.user_id == user_id)
        .order_by(AuditLog.timestamp.desc())
        .limit(limit)
        .offset(offset)
    )

    # Execute query
    logs = session.exec(stmt).all()

    # Count total logs
    count_stmt = (
        select(AuditLog)
        .where(AuditLog.task_id == task_id)
        .where(AuditLog.user_id == user_id)
    )
    total = len(session.exec(count_stmt).all())

    # Convert to response models
    log_responses = [
        AuditLogResponse(
            id=log.id,
            event_id=str(log.event_id),
            event_type=log.event_type,
            task_id=log.task_id,
            user_id=log.user_id,
            operation=log.operation,
            before_state=log.before_state,
            after_state=log.after_state,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent,
            timestamp=log.timestamp,
            created_at=log.created_at
        )
        for log in logs
    ]

    return AuditLogListResponse(logs=log_responses, total=total)


@router.get("/user", response_model=AuditLogListResponse)
async def get_user_audit_logs(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    date_from: Optional[date] = Query(None, description="Filter logs from this date"),
    date_to: Optional[date] = Query(None, description="Filter logs to this date"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all audit logs for the current user.

    Returns complete activity history, ordered by timestamp (newest first).
    """
    user_id = current_user["id"]

    # Build query
    stmt = select(AuditLog).where(AuditLog.user_id == user_id)

    # Apply date filters
    if date_from:
        stmt = stmt.where(AuditLog.timestamp >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        stmt = stmt.where(AuditLog.timestamp <= datetime.combine(date_to, datetime.max.time()))

    # Order and paginate
    stmt = stmt.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset)

    # Execute query
    logs = session.exec(stmt).all()

    # Count total logs
    count_stmt = select(AuditLog).where(AuditLog.user_id == user_id)
    if date_from:
        count_stmt = count_stmt.where(AuditLog.timestamp >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        count_stmt = count_stmt.where(AuditLog.timestamp <= datetime.combine(date_to, datetime.max.time()))
    total = len(session.exec(count_stmt).all())

    # Convert to response models
    log_responses = [
        AuditLogResponse(
            id=log.id,
            event_id=str(log.event_id),
            event_type=log.event_type,
            task_id=log.task_id,
            user_id=log.user_id,
            operation=log.operation,
            before_state=log.before_state,
            after_state=log.after_state,
            ip_address=str(log.ip_address) if log.ip_address else None,
            user_agent=log.user_agent,
            timestamp=log.timestamp,
            created_at=log.created_at
        )
        for log in logs
    ]

    return AuditLogListResponse(logs=log_responses, total=total)


@router.post("/export")
async def export_audit_logs(
    export_request: ExportRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """
    Export audit logs in JSON or CSV format.

    Supports filtering by task_id and date range.
    """
    user_id = current_user["id"]

    # Validate format
    if export_request.format not in ['json', 'csv']:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")

    # Build query
    stmt = select(AuditLog).where(AuditLog.user_id == user_id)

    # Apply filters
    if export_request.task_id:
        stmt = stmt.where(AuditLog.task_id == export_request.task_id)
    if export_request.date_from:
        stmt = stmt.where(AuditLog.timestamp >= datetime.combine(export_request.date_from, datetime.min.time()))
    if export_request.date_to:
        stmt = stmt.where(AuditLog.timestamp <= datetime.combine(export_request.date_to, datetime.max.time()))

    # Order by timestamp
    stmt = stmt.order_by(AuditLog.timestamp.desc())

    # Execute query
    logs = session.exec(stmt).all()

    if not logs:
        raise HTTPException(status_code=404, detail="No audit logs found")

    # Import exporter (lazy import to avoid circular dependency)
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../microservices/audit'))
    from export import AuditLogExporter

    # Export to requested format
    if export_request.format == 'json':
        content = AuditLogExporter.to_json(logs)
        media_type = "application/json"
        filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    else:  # csv
        content = AuditLogExporter.to_csv(logs)
        media_type = "text/csv"
        filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    # Return file response
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
