"""
FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import auth, jobs, users
from app.dashboard import routes as dashboard_routes
from app.core.config import settings

app = FastAPI(
    title="Orc Ray Agent API",
    description="Ray-based distributed ML plugin agent system",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])

# Include dashboard routes
app.include_router(dashboard_routes.router, prefix="/dashboard", tags=["dashboard"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Orc Ray Agent API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
