"""User model."""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.route import RouteTemplate, RouteInstance
    from app.models.checkin import CheckIn

# XP thresholds for each level
LEVEL_THRESHOLDS = [
    (1, 0),
    (2, 200),
    (3, 500),
    (4, 1000),
    (5, 1750),
    (6, 2750),
    (7, 4000),
    (8, 5500),
    (9, 7500),
    (10, 10000),
]


def xp_to_level(total_xp: int) -> int:
    """Convert total XP to a level."""
    level = 1
    for lvl, threshold in LEVEL_THRESHOLDS:
        if total_xp >= threshold:
            level = lvl
    return level


class User(Base, UUIDMixin, TimestampMixin):
    """Core user identity."""
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    
    # XP and leveling
    total_xp: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    
    # Relationships
    authored_templates: Mapped[list["RouteTemplate"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    route_instances: Mapped[list["RouteInstance"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    check_ins: Mapped[list["CheckIn"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
