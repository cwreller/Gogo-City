"""Places cache model for Google Places API responses."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Optional

import sqlalchemy as sa
from sqlalchemy import DateTime, Numeric, SmallInteger, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


def default_expires_at() -> datetime:
    """Default expiration: 30 days from now."""
    return datetime.now().astimezone() + timedelta(days=30)


class PlacesCache(Base, UUIDMixin):
    """Cache for Google Places API responses to reduce API costs."""
    
    __tablename__ = "places_cache"
    
    # Place identifiers
    place_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), server_default="google", nullable=False)
    
    # Essential denormalized fields
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String)
    lat: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    lng: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    place_types: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    
    # Google-specific fields
    price_level: Mapped[Optional[int]] = mapped_column(SmallInteger)  # 0-4
    rating: Mapped[Optional[Decimal]] = mapped_column(Numeric(2, 1))  # 1.0-5.0
    rating_count: Mapped[Optional[int]] = mapped_column()
    photo_references: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        server_default="{}",
        nullable=False,
    )
    
    # Full API response for fields we don't denormalize
    raw_data: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    
    # Cache management
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=default_expires_at,
        nullable=False,
    )
    
    __table_args__ = (
        # Unique constraint on place_id + provider
        UniqueConstraint("place_id", "provider", name="uq_places_cache_place_provider"),
    )
    
    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return datetime.now().astimezone() > self.expires_at
