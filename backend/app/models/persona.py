"""Purpose: SQLAlchemy model for customer personas used in simulation."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, Text, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Persona(Base):
    """Represents a customer persona profile with specific attributes and preferences."""

    __tablename__ = "personas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    persona_type: Mapped[str] = mapped_column(String(64), nullable=True)  # family, budget, performance, eco
    sympathy_level: Mapped[str] = mapped_column(String(32), nullable=True)  # High Sympathy, Moderate Sympathy, Low Sympathy
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    budget_range: Mapped[str] = mapped_column(String(64), nullable=True)
    personality: Mapped[str] = mapped_column(Text, nullable=False)
    profile: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Store list data in JSON mode compatible with SQLite/PostgreSQL
    preferences: Mapped[list[str]] = mapped_column(JSON, default=list)
    goals: Mapped[list[str]] = mapped_column(JSON, default=list)
    pain_points: Mapped[list[str]] = mapped_column(JSON, default=list)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
