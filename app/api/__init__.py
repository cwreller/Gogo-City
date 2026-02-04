"""API router configuration."""
from fastapi import APIRouter

from app.api.routes import generate, health, templates

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(generate.router, prefix="/routes", tags=["routes"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
