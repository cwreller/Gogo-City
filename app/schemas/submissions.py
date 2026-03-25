"""Pydantic schemas for task submissions."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SubmitTaskRequest(BaseModel):
    city_id: UUID
    name: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    address: str | None = None
    task_description: str | None = None
    verification_hint: str | None = None
    verification_type: str = "photo"
    category: str = Field(..., min_length=1, max_length=50)
    vibe_tags: list[str] = []
    price_level: int | None = Field(None, ge=1, le=4)
    avg_duration_minutes: int | None = Field(None, ge=1)
    pro_tips: str | None = None


class SubmissionResponse(BaseModel):
    id: UUID
    submitted_by: UUID
    submitter_username: str
    city_id: UUID
    city_name: str
    name: str
    description: str | None
    address: str | None
    task_description: str | None
    verification_hint: str | None
    verification_type: str
    category: str
    vibe_tags: list[str]
    price_level: int | None
    avg_duration_minutes: int | None
    pro_tips: str | None
    status: str
    rejection_reason: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewSubmissionRequest(BaseModel):
    action: str = Field(..., pattern="^(approve|reject)$")
    rejection_reason: str | None = None
    xp: int | None = Field(None, ge=0)
