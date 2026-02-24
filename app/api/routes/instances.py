"""Route instance endpoints: import a template, list instances, get instance detail."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.instances import (
    ImportTemplateRequest,
    InstanceListItem,
    InstanceResponse,
    InstanceTaskResponse,
    ProgressResponse,
)
from app.services.instance_service import InstanceService

router = APIRouter()


def _progress(instance) -> ProgressResponse:
    completed, total = instance.progress
    return ProgressResponse(
        completed_tasks=completed,
        total_tasks=total,
        percent=round(completed / total * 100, 1) if total else 0.0,
        is_complete=instance.is_complete,
    )


def _task_response(task) -> InstanceTaskResponse:
    return InstanceTaskResponse(
        id=task.id,
        name=task.name,
        address=task.address,
        lat=task.lat,
        lng=task.lng,
        task_description=task.task_description,
        verification_type=task.verification_type,
        verification_hint=task.verification_hint,
        notes=task.notes,
        is_completed=task.check_in is not None,
    )


@router.post("/", response_model=InstanceResponse, status_code=201)
def create_instance(body: ImportTemplateRequest, db: Session = Depends(get_db)):
    """Import a template into a personal route instance."""
    svc = InstanceService(db)
    try:
        instance = svc.import_template(body.template_id, body.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return InstanceResponse(
        id=instance.id,
        title=instance.title,
        description=instance.description,
        status=instance.status,
        source_template_id=instance.source_template_id,
        created_at=instance.created_at.isoformat(),
        progress=_progress(instance),
        tasks=[_task_response(t) for t in instance.tasks],
    )


@router.get("/", response_model=list[InstanceListItem])
def list_instances(user_id: UUID, db: Session = Depends(get_db)):
    """List all route instances for a user."""
    svc = InstanceService(db)
    instances = svc.list_instances(user_id)
    return [
        InstanceListItem(
            id=inst.id,
            title=inst.title,
            description=inst.description,
            status=inst.status,
            source_template_id=inst.source_template_id,
            created_at=inst.created_at.isoformat(),
            progress=_progress(inst),
        )
        for inst in instances
    ]


@router.get("/{instance_id}", response_model=InstanceResponse)
def get_instance(instance_id: UUID, user_id: UUID, db: Session = Depends(get_db)):
    """Get a single route instance with tasks and progress."""
    svc = InstanceService(db)
    instance = svc.get_instance(instance_id, user_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")

    return InstanceResponse(
        id=instance.id,
        title=instance.title,
        description=instance.description,
        status=instance.status,
        source_template_id=instance.source_template_id,
        created_at=instance.created_at.isoformat(),
        progress=_progress(instance),
        tasks=[_task_response(t) for t in instance.tasks],
    )
