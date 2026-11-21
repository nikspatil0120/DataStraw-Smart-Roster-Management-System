"""FastAPI application."""
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
import logging

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(
    title="Smart Roster Management System",
    description="Enterprise roster scheduling system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
