"""Database connection and session management."""
from sqlmodel import create_engine, Session
from app.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
