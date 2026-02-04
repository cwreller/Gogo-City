"""City model."""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin

if TYPE_CHECKING:
    from app.models.route import RouteTemplate
    from app.models.curated_task import CuratedTask


class City(Base, UUIDMixin):
    """A city where routes can be created."""
    
    __tablename__ = "cities"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100), server_default="USA", nullable=False)
    
    # City center coordinates
    lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7))
    
    # Timezone (e.g., "America/Chicago")
    timezone: Mapped[Optional[str]] = mapped_column(String(50))
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    
    # Relationships
    route_templates: Mapped[list["RouteTemplate"]] = relationship(
        back_populates="city",
    )
    curated_tasks: Mapped[list["CuratedTask"]] = relationship(
        back_populates="city",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        UniqueConstraint("name", "state", "country", name="uq_cities_name_state_country"),
    )
    
    def __repr__(self) -> str:
        if self.state:
            return f"<City {self.name}, {self.state}>"
        return f"<City {self.name}, {self.country}>"
