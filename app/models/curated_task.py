"""Curated tasks model - unified places + tasks for each city."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Literal, Optional

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.city import City


VerificationType = Literal["gps", "photo", "both"]


class CuratedTask(Base, UUIDMixin, TimestampMixin):
    """A curated task/challenge within a city.
    
    Can be:
    - Location-only: "Go to Centennial Park" (lat/lng set, task_description null)
    - Task-only: "Eat hot chicken" (lat/lng null, task_description set)
    - Combined: "Pet a dog at Centennial Park" (both set)
    """
    
    __tablename__ = "curated_tasks"
    
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cities.id", ondelete="CASCADE"),
        nullable=False,
    )
    
    # Task identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Location fields (nullable - if null, task is locationless)
    address: Mapped[Optional[str]] = mapped_column(Text)
    lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    google_place_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Task action fields (nullable - if null, just "visit the place")
    task_description: Mapped[Optional[str]] = mapped_column(Text)  # "Eat hot chicken"
    verification_hint: Mapped[Optional[str]] = mapped_column(Text)  # "Photo of you eating"
    
    # Verification type: gps, photo, both
    verification_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="gps",
    )
    
    # Categorization for AI matching
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    vibe_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    dietary_tags: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    price_level: Mapped[Optional[int]] = mapped_column(SmallInteger)  # 1-4
    
    # Curated content
    best_for: Mapped[Optional[str]] = mapped_column(Text)
    pro_tips: Mapped[Optional[str]] = mapped_column(Text)
    photo_url: Mapped[Optional[str]] = mapped_column(Text)
    
    # Time/availability hints
    best_times: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    avg_duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Admin
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)
    
    # Relationships
    city: Mapped["City"] = relationship(back_populates="curated_tasks")
    
    __table_args__ = (
        CheckConstraint(
            "verification_type IN ('gps', 'photo', 'both')",
            name="chk_curated_tasks_verification_type",
        ),
    )
    
    @property
    def has_location(self) -> bool:
        """Check if this task has a physical location."""
        return self.lat is not None and self.lng is not None
    
    @property
    def has_task_action(self) -> bool:
        """Check if this task has an action to perform."""
        return self.task_description is not None
    
    def __repr__(self) -> str:
        return f"<CuratedTask {self.name} ({self.verification_type})>"
