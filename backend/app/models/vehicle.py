"""Purpose: SQLAlchemy model for vehicle knowledge base entries."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Integer, String, Text, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Vehicle(Base):
    """Represents a vehicle record available for recommendation and comparison."""

    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    make: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    model: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    msrp: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=True)
    fuel_type: Mapped[str] = mapped_column(String(64), nullable=True)
    inventory_status: Mapped[str] = mapped_column(String(32), default="in_stock")
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Store list of specs in JSON
    features: Mapped[list[str]] = mapped_column(JSON, default=list)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
