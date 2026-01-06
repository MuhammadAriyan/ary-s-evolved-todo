"""Dependency injection for database and authentication."""
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from app.database import get_session
from app.middleware.auth import verify_jwt_token

# Database dependency
SessionDep = Annotated[Session, Depends(get_session)]

# Current user dependency
CurrentUser = Annotated[str, Depends(verify_jwt_token)]


def get_db() -> Session:
    """Get database session (for explicit use)."""
    return next(get_session())


def get_current_user(user_id: CurrentUser) -> str:
    """Get current authenticated user ID."""
    return user_id
