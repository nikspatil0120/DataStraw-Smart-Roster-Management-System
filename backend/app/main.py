"""FastAPI application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.api.routes import (
    auth,
    employees,
    brands,
    processes,
    pods,
    assignments,
    leaves,
    scheduling,
    scheduling_advanced,
    rosters,
    conflicts,
    holidays,
    availability,
    export,
    analytics,
)

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app (table creation happens in startup event)
app = FastAPI(
    title="Smart Roster Management System",
    description="Enterprise roster scheduling system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware - log the origins
logger.info(f"[STARTUP] Allowed CORS origins: {settings.allowed_origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event to create tables
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database tables: {e}")

# Include routers
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(brands.router)
app.include_router(processes.router)
app.include_router(pods.router)
app.include_router(assignments.router)
app.include_router(leaves.router)
app.include_router(scheduling.router)
app.include_router(scheduling_advanced.router)
app.include_router(rosters.router)
app.include_router(conflicts.router)
app.include_router(holidays.router)
app.include_router(availability.router)
app.include_router(export.router)
app.include_router(analytics.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Smart Roster Management System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.exception(f"Unhandled exception: {exc}")
    return {
        "detail": "Internal server error",
        "type": type(exc).__name__,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
