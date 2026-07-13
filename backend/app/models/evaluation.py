"""Purpose: SQLAlchemy model for session evaluations."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Evaluation(Base):
    """Represents overall performance scoring and analytics for a completed session."""

    __tablename__ = "evaluations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending, completed
    
    # Store turn breakdowns (e.g. {"empathy": 80}) and list checklists in JSON
    breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    recommendations: Mapped[list[str]] = mapped_column(JSON, default=list)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="evaluation")
