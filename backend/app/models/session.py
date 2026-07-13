"""Purpose: SQLAlchemy model for training sessions."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Session(Base):
    """Represents a single training simulation session."""

    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active")  # active, completed, evaluated
    
    # Linked to Persona table
    persona_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("personas.id"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan"
    )
    evaluation: Mapped["Evaluation"] = relationship(
        "Evaluation", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    metrics: Mapped[list["SessionMetrics"]] = relationship(
        "SessionMetrics", back_populates="session", cascade="all, delete-orphan"
    )
    
    persona: Mapped["Persona"] = relationship("Persona")
