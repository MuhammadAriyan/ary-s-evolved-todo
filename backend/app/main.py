"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.router import router as api_v1_router
from app.services.scheduler import start_scheduler, shutdown_scheduler
import logging
import time

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    start_scheduler()
    yield
    # Shutdown
    logger.info("Shutting down application...")
    shutdown_scheduler()


app = FastAPI(
    title="Todo API",
    description="Full-stack todo application API with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with headers for debugging."""
    start_time = time.time()

    # Log request details
    print(f"\n{'='*60}")
    print(f"📥 Incoming Request: {request.method} {request.url.path}")
    print(f"Headers:")
    for header, value in request.headers.items():
        if header.lower() == "authorization":
            print(f"  🔑 {header}: {value[:50]}..." if len(value) > 50 else f"  🔑 {header}: {value}")
        else:
            print(f"  {header}: {value}")

    response = await call_next(request)

    process_time = time.time() - start_time
    print(f"✅ Response: {response.status_code} (took {process_time:.3f}s)")
    print(f"{'='*60}\n")

    return response

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_v1_router)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "todo-api", "version": "1.0.0"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Todo API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }
