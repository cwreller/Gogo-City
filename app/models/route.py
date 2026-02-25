"""Route-related models: templates, instances, and tasks."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.city import City
    from app.models.checkin import CheckIn


class RouteTemplate(Base, UUIDMixin, TimestampMixin):
    """A shareable route template (the plan) containing tasks."""
    
    __tablename__ = "route_templates"
    
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    city_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="SET NULL"),
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    
    # Sharing mechanism
    share_code: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    is_public: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    
    # Metadata for filtering/display
    estimated_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    estimated_budget_cents: Mapped[Optional[int]] = mapped_column(Integer)
    vibe_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    
    # Relationships
    author: Mapped["User"] = relationship(back_populates="authored_templates")
    city: Mapped[Optional["City"]] = relationship(back_populates="route_templates")
    tasks: Mapped[list["TemplateTask"]] = relationship(
        back_populates="template",
        cascade="all, delete-orphan",
    )
    instances: Mapped[list["RouteInstance"]] = relationship(
        back_populates="source_template",
    )


class TemplateTask(Base, UUIDMixin):
    """A task within a route template. Can be location-based, action-based, or both."""
    
    __tablename__ = "template_tasks"
    
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("route_templates.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Place reference (optional for locationless tasks)
    place_id: Mapped[Optional[str]] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50), server_default="google", nullable=False)
    
    # Snapshot fields (nullable for locationless tasks)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String)
    lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    place_types: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    
    # Task action fields
    task_description: Mapped[Optional[str]] = mapped_column(Text)  # "Eat hot chicken"
    verification_hint: Mapped[Optional[str]] = mapped_column(Text)  # "Photo of you eating"
    verification_type: Mapped[str] = mapped_column(
        String(20),
        server_default="gps",
        nullable=False,
    )  # gps, photo, both
    
    # XP awarded on completion (snapshotted from curated task)
    xp: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    
    # Author's custom note for this task
    notes: Mapped[Optional[str]] = mapped_column(String)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
    )
    
    # Relationships
    template: Mapped["RouteTemplate"] = relationship(back_populates="tasks")
    
    @property
    def has_location(self) -> bool:
        """Check if this task has a physical location."""
        return self.lat is not None and self.lng is not None
    
    @property
    def has_task_action(self) -> bool:
        """Check if this task has an action to perform."""
        return self.task_description is not None


class RouteInstance(Base, UUIDMixin, TimestampMixin):
    """A user's personal instance of a route, created by importing a template."""
    
    __tablename__ = "route_instances"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_template_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("route_templates.id", ondelete="SET NULL"),
    )
    
    # Copied from template at import (snapshot)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    
    # Progress tracking
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="active",
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="route_instances")
    source_template: Mapped[Optional["RouteTemplate"]] = relationship(
        back_populates="instances",
    )
    tasks: Mapped[list["InstanceTask"]] = relationship(
        back_populates="instance",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'archived')",
            name="chk_route_instances_status",
        ),
    )
    
    @property
    def progress(self) -> tuple[int, int]:
        """Return (completed_tasks, total_tasks) tuple."""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.check_in is not None)
        return (completed, total)
    
    @property
    def is_complete(self) -> bool:
        """Check if all tasks have been completed."""
        return all(task.check_in is not None for task in self.tasks)


class InstanceTask(Base, UUIDMixin):
    """A task within a route instance. Snapshot copied from template at import."""
    
    __tablename__ = "instance_tasks"
    
    instance_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("route_instances.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_template_task_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
    )
    
    # Place reference (optional for locationless tasks)
    place_id: Mapped[Optional[str]] = mapped_column(String(255))
    provider: Mapped[str] = mapped_column(String(50), server_default="google", nullable=False)
    
    # Snapshot fields (nullable for locationless tasks)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String)
    lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    place_types: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    
    # Task action fields
    task_description: Mapped[Optional[str]] = mapped_column(Text)
    verification_hint: Mapped[Optional[str]] = mapped_column(Text)
    verification_type: Mapped[str] = mapped_column(
        String(20),
        server_default="gps",
        nullable=False,
    )
    
    # XP awarded on completion (snapshotted from template task)
    xp: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    
    notes: Mapped[Optional[str]] = mapped_column(String)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default="now()",
        nullable=False,
    )
    
    # Relationships
    instance: Mapped["RouteInstance"] = relationship(back_populates="tasks")
    check_in: Mapped[Optional["CheckIn"]] = relationship(
        back_populates="instance_task",
        uselist=False,
    )
    
    @property
    def has_location(self) -> bool:
        """Check if this task has a physical location."""
        return self.lat is not None and self.lng is not None
    
    @property
    def has_task_action(self) -> bool:
        """Check if this task has an action to perform."""
        return self.task_description is not None
