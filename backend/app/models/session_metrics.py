"""Purpose: SQLAlchemy model for coaching analytics and session metrics."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SessionMetrics(Base):
    """Stores key performance indicators (KPIs) for training sessions."""

    __tablename__ = "session_metrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    metric_name: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    metric_value: Mapped[str] = mapped_column(String(128), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="metrics")
