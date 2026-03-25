"""Task submission model - user-submitted tasks pending admin review."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.city import City


class TaskSubmission(Base, UUIDMixin, TimestampMixin):
    """A user-submitted task awaiting admin approval."""

    __tablename__ = "task_submissions"

    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(Text)
    lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    task_description: Mapped[Optional[str]] = mapped_column(Text)
    verification_hint: Mapped[Optional[str]] = mapped_column(Text)
    verification_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="photo",
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    vibe_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String), server_default="{}", nullable=False,
    )
    price_level: Mapped[Optional[int]] = mapped_column(SmallInteger)
    avg_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    pro_tips: Mapped[Optional[str]] = mapped_column(Text)

    # Review workflow
    status: Mapped[str] = mapped_column(
        String(20), server_default="pending", nullable=False,
    )
    reviewed_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"),
    )
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    submitter: Mapped["User"] = relationship(foreign_keys=[submitted_by])
    reviewer: Mapped[Optional["User"]] = relationship(foreign_keys=[reviewed_by])
    city: Mapped["City"] = relationship()

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected')",
            name="chk_task_submissions_status",
        ),
        CheckConstraint(
            "verification_type IN ('gps', 'photo', 'both')",
            name="chk_task_submissions_verification_type",
        ),
    )

    def __repr__(self) -> str:
        return f"<TaskSubmission {self.name} ({self.status})>"
