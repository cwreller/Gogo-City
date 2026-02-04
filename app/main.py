"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="GoGoCity API",
    description="API for generating personalized city exploration routes",
    version="0.1.0",
    debug=settings.debug,
)

# CORS middleware - configure for your frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "GoGoCity API",
        "version": "0.1.0",
        "docs": "/docs",
    }
