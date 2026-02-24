"""Service for route instance management: importing, snapshotting, progress, sharing."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import RouteInstance, RouteTemplate, InstanceTask, TemplateTask


class InstanceService:
    def __init__(self, db: Session):
        self.db = db

    def import_template(self, template_id: UUID, user_id: UUID) -> RouteInstance:
        """Import a template into a personal route instance with snapshotted tasks."""
        template = (
            self.db.query(RouteTemplate)
            .options(joinedload(RouteTemplate.tasks))
            .filter(RouteTemplate.id == template_id)
            .first()
        )
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        instance = RouteInstance(
            user_id=user_id,
            source_template_id=template.id,
            title=template.title,
            description=template.description,
            status="active",
        )
        self.db.add(instance)
        self.db.flush()

        for tt in template.tasks:
            self._snapshot_task(instance.id, tt)

        self.db.commit()
        self.db.refresh(instance)
        return instance

    def list_instances(self, user_id: UUID) -> list[RouteInstance]:
        """List all route instances for a user, newest first."""
        stmt = (
            select(RouteInstance)
            .options(joinedload(RouteInstance.tasks))
            .where(RouteInstance.user_id == user_id)
            .order_by(RouteInstance.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def get_instance(self, instance_id: UUID, user_id: UUID) -> RouteInstance | None:
        """Get a single instance with tasks, scoped to the owning user."""
        stmt = (
            select(RouteInstance)
            .options(
                joinedload(RouteInstance.tasks).joinedload(InstanceTask.check_in)
            )
            .where(RouteInstance.id == instance_id, RouteInstance.user_id == user_id)
        )
        return self.db.execute(stmt).scalars().unique().first()

    def get_progress(self, instance: RouteInstance) -> dict:
        """Return progress stats for an instance."""
        completed, total = instance.progress
        return {
            "completed_tasks": completed,
            "total_tasks": total,
            "percent": round(completed / total * 100, 1) if total else 0.0,
            "is_complete": instance.is_complete,
        }

    # ── Sharing ──────────────────────────────────────────────────────

    def preview_shared_route(self, share_code: str) -> RouteTemplate | None:
        """Look up a template by share_code for preview (read-only)."""
        stmt = (
            select(RouteTemplate)
            .options(joinedload(RouteTemplate.tasks))
            .where(RouteTemplate.share_code == share_code)
        )
        return self.db.execute(stmt).scalars().unique().first()

    def import_shared_route(self, share_code: str, user_id: UUID) -> RouteInstance:
        """Import a shared route into the user's account as an independent instance."""
        template = self.preview_shared_route(share_code)
        if not template:
            raise ValueError(f"No route found for share code: {share_code}")
        return self.import_template(template.id, user_id)

    # ── Private helpers ──────────────────────────────────────────────

    def _snapshot_task(self, instance_id: UUID, tt: TemplateTask) -> InstanceTask:
        """Copy a template task into an instance task (snapshot)."""
        it = InstanceTask(
            instance_id=instance_id,
            source_template_task_id=tt.id,
            place_id=tt.place_id,
            provider=tt.provider,
            name=tt.name,
            address=tt.address,
            lat=tt.lat,
            lng=tt.lng,
            place_types=list(tt.place_types) if tt.place_types else [],
            task_description=tt.task_description,
            verification_hint=tt.verification_hint,
            verification_type=tt.verification_type,
            notes=tt.notes,
        )
        self.db.add(it)
        return it
