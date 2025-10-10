"""
FastAPI application entry point for Plugin Registry service
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import plugins

app = FastAPI(
    title="Orc Ray Agent - Plugin Registry",
    description="Plugin metadata registry service",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(plugins.router, prefix="/api/v1/plugins", tags=["plugins"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Plugin Registry Service",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
