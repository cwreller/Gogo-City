"""Check-in model for tracking task completion."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.route import InstanceTask


class CheckIn(Base, UUIDMixin):
    """Records a user completing a task. One check-in per instance_task."""
    
    __tablename__ = "check_ins"
    
    instance_task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("instance_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    checked_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Verification: how was this check-in verified?
    verified_by: Mapped[Optional[str]] = mapped_column(String(20))  # gps, photo, both, null=pending
    
    # Location at check-in (for GPS verification)
    lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    
    # Photo for photo verification
    photo_url: Mapped[Optional[str]] = mapped_column(String)
    
    # User additions
    notes: Mapped[Optional[str]] = mapped_column(String)
    rating: Mapped[Optional[int]] = mapped_column(SmallInteger)  # 1-5
    
    # Relationships
    instance_task: Mapped["InstanceTask"] = relationship(back_populates="check_in")
    user: Mapped["User"] = relationship(back_populates="check_ins")
    
    __table_args__ = (
        # Enforce one check-in per task per instance
        UniqueConstraint("instance_task_id", name="uq_check_ins_instance_task"),
        # Rating must be 1-5 if provided
        CheckConstraint(
            "rating IS NULL OR (rating >= 1 AND rating <= 5)",
            name="chk_check_ins_rating",
        ),
    )
