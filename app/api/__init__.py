"""API router configuration."""
from fastapi import APIRouter

from app.api.routes import cities, generate, health, instances, sharing, templates

api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["health"])
api_router.include_router(cities.router, prefix="/cities", tags=["cities"])
api_router.include_router(generate.router, prefix="/routes", tags=["routes"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(instances.router, prefix="/instances", tags=["instances"])
api_router.include_router(sharing.router, prefix="/routes", tags=["sharing"])
