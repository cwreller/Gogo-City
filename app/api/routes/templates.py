"""Route template endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import RouteTemplate, TemplateTask

router = APIRouter()


class TaskResponse(BaseModel):
    id: UUID
    name: str
    address: str | None
    task_description: str | None
    verification_type: str
    
    class Config:
        from_attributes = True


class TemplateResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    share_code: str | None
    estimated_duration_minutes: int | None
    vibe_tags: list[str]
    created_at: str
    tasks: list[TaskResponse]
    
    class Config:
        from_attributes = True


@router.get("/", response_model=list[TemplateResponse])
def list_templates(db: Session = Depends(get_db)):
    """List all route templates."""
    templates = db.query(RouteTemplate).order_by(RouteTemplate.created_at.desc()).all()
    
    return [
        TemplateResponse(
            id=t.id,
            title=t.title,
            description=t.description,
            share_code=t.share_code,
            estimated_duration_minutes=t.estimated_duration_minutes,
            vibe_tags=t.vibe_tags or [],
            created_at=t.created_at.isoformat(),
            tasks=[
                TaskResponse(
                    id=task.id,
                    name=task.name,
                    address=task.address,
                    task_description=task.task_description,
                    verification_type=task.verification_type,
                )
                for task in t.tasks
            ]
        )
        for t in templates
    ]


@router.delete("/{template_id}")
def delete_template(template_id: UUID, db: Session = Depends(get_db)):
    """Delete a route template."""
    template = db.query(RouteTemplate).filter(RouteTemplate.id == template_id).first()
    if template:
        db.delete(template)
        db.commit()
        return {"status": "deleted"}
    return {"status": "not found"}
