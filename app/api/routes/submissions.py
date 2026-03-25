"""Task submission endpoints: users suggest tasks, admins approve/reject."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_admin, get_current_user
from app.db.session import get_db
from app.models import City, CuratedTask, TaskSubmission, User
from app.schemas.submissions import ReviewSubmissionRequest, SubmissionResponse, SubmitTaskRequest

router = APIRouter()


def _to_response(sub: TaskSubmission) -> SubmissionResponse:
    return SubmissionResponse(
        id=sub.id,
        submitted_by=sub.submitted_by,
        submitter_username=sub.submitter.username if sub.submitter else "unknown",
        city_id=sub.city_id,
        city_name=sub.city.name if sub.city else "unknown",
        name=sub.name,
        description=sub.description,
        address=sub.address,
        task_description=sub.task_description,
        verification_hint=sub.verification_hint,
        verification_type=sub.verification_type,
        category=sub.category,
        vibe_tags=sub.vibe_tags,
        price_level=sub.price_level,
        avg_duration_minutes=sub.avg_duration_minutes,
        pro_tips=sub.pro_tips,
        status=sub.status,
        rejection_reason=sub.rejection_reason,
        created_at=sub.created_at,
    )


@router.post("/", response_model=SubmissionResponse, status_code=201)
def submit_task(
    body: SubmitTaskRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    """Submit a new task suggestion for admin review."""
    city = db.query(City).filter(City.id == body.city_id).first()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    if body.verification_type not in ("gps", "photo", "both"):
        raise HTTPException(status_code=422, detail="verification_type must be gps, photo, or both")

    sub = TaskSubmission(
        submitted_by=user_id,
        city_id=body.city_id,
        name=body.name,
        description=body.description,
        address=body.address,
        task_description=body.task_description,
        verification_hint=body.verification_hint,
        verification_type=body.verification_type,
        category=body.category,
        vibe_tags=body.vibe_tags,
        price_level=body.price_level,
        avg_duration_minutes=body.avg_duration_minutes,
        pro_tips=body.pro_tips,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return _to_response(sub)


@router.get("/mine", response_model=list[SubmissionResponse])
def my_submissions(
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user),
):
    """List the current user's submissions."""
    subs = (
        db.query(TaskSubmission)
        .filter(TaskSubmission.submitted_by == user_id)
        .order_by(TaskSubmission.created_at.desc())
        .all()
    )
    return [_to_response(s) for s in subs]


@router.get("/", response_model=list[SubmissionResponse])
def list_submissions(
    submission_status: str = Query("pending", alias="status"),
    db: Session = Depends(get_db),
    _admin_id: UUID = Depends(get_current_admin),
):
    """Admin: list submissions filtered by status."""
    query = db.query(TaskSubmission)
    if submission_status != "all":
        query = query.filter(TaskSubmission.status == submission_status)
    subs = query.order_by(TaskSubmission.created_at.desc()).all()
    return [_to_response(s) for s in subs]


@router.patch("/{submission_id}", response_model=SubmissionResponse)
def review_submission(
    submission_id: UUID,
    body: ReviewSubmissionRequest,
    db: Session = Depends(get_db),
    admin_id: UUID = Depends(get_current_admin),
):
    """Admin: approve or reject a submission."""
    sub = db.query(TaskSubmission).filter(TaskSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    if sub.status != "pending":
        raise HTTPException(status_code=409, detail="Submission already reviewed")

    if body.action == "approve":
        curated = CuratedTask(
            city_id=sub.city_id,
            name=sub.name,
            description=sub.description,
            address=sub.address,
            lat=sub.lat,
            lng=sub.lng,
            task_description=sub.task_description,
            verification_hint=sub.verification_hint,
            verification_type=sub.verification_type,
            category=sub.category,
            vibe_tags=sub.vibe_tags,
            dietary_tags=[],
            price_level=sub.price_level,
            avg_duration_minutes=sub.avg_duration_minutes,
            pro_tips=sub.pro_tips,
            xp=body.xp or 50,
            is_active=True,
        )
        db.add(curated)
        sub.status = "approved"
    else:
        sub.status = "rejected"
        sub.rejection_reason = body.rejection_reason

    sub.reviewed_by = admin_id
    sub.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(sub)
    return _to_response(sub)
