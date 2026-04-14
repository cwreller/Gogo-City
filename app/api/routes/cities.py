"""Cities endpoints."""
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin
from app.db.session import get_db
from app.models import City, CuratedTask

router = APIRouter()


class CityResponse(BaseModel):
    id: UUID
    name: str
    state: str | None
    country: str
    
    class Config:
        from_attributes = True


class CuratedTaskResponse(BaseModel):
    id: UUID
    name: str
    category: str
    description: str | None = None
    address: str | None = None
    task_description: str | None = None
    verification_type: str
    verification_hint: str | None = None
    vibe_tags: list[str] = []
    price_level: int | None = None
    avg_duration_minutes: int | None = None
    xp: int = 0
    lat: Optional[Decimal] = None
    lng: Optional[Decimal] = None
    is_active: bool = True

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CityResponse])
def list_cities(db: Session = Depends(get_db)):
    """List all available cities."""
    cities = db.query(City).order_by(City.name).all()
    return cities


@router.get("/{city_id}", response_model=CityResponse)
def get_city(city_id: UUID, db: Session = Depends(get_db)):
    """Get a single city by ID."""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


@router.get("/{city_id}/tasks", response_model=list[CuratedTaskResponse])
def list_curated_tasks(
    city_id: UUID,
    db: Session = Depends(get_db),
    _admin: UUID = Depends(get_current_admin),
):
    """List all curated tasks for a city (admin only)."""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    tasks = (
        db.query(CuratedTask)
        .filter(CuratedTask.city_id == city_id)
        .order_by(CuratedTask.category, CuratedTask.name)
        .all()
    )
    return tasks
