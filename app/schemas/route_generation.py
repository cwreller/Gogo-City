"""Schemas for route generation endpoint."""
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class BudgetLevel(str, Enum):
    """Budget preference levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ANY = "any"


class GenerateRouteRequest(BaseModel):
    """Request schema for generating a route."""
    
    city_id: UUID = Field(..., description="ID of the city to generate route for")
    
    # Time constraint
    time_available_hours: float = Field(
        ..., 
        gt=0, 
        le=24,
        description="How many hours the user has available"
    )
    
    # Budget preference
    budget: BudgetLevel = Field(
        default=BudgetLevel.ANY,
        description="Budget preference (low/medium/high/any)"
    )
    
    # Vibe/mood tags - we'll expand this list later
    vibe_tags: list[str] = Field(
        default_factory=list,
        description="Desired vibes: foodie, adventurous, chill, cultural, nightlife, etc."
    )
    
    # Dietary restrictions
    dietary_restrictions: list[str] = Field(
        default_factory=list,
        description="Dietary restrictions: vegetarian, vegan, gluten-free, etc."
    )
    
    # Optional filters
    group_size: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Number of people in the group"
    )
    
    # Optional: user can set a title, otherwise we'll generate one
    custom_title: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Custom title for the route"
    )


class TaskInRoute(BaseModel):
    """A task included in the generated route."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    
    # Location (nullable for locationless tasks)
    address: Optional[str] = None
    lat: Optional[Decimal] = None
    lng: Optional[Decimal] = None
    
    # Task details
    task_description: Optional[str] = None
    verification_type: str
    verification_hint: Optional[str] = None
    
    # Metadata
    category: str
    price_level: Optional[int] = None
    avg_duration_minutes: Optional[int] = None
    
    class Config:
        from_attributes = True


class GenerateRouteResponse(BaseModel):
    """Response schema for generated route."""
    
    template_id: UUID = Field(..., description="ID of the created route template")
    title: str
    description: Optional[str] = None
    
    city_id: UUID
    city_name: str
    
    tasks: list[TaskInRoute]
    
    # Computed metadata
    total_tasks: int
    estimated_duration_minutes: int
    
    class Config:
        from_attributes = True
