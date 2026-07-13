"""Purpose: SQLAlchemy model for chat messages within sessions."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Message(Base):
    """Stores individual dialogue turns exchanged in a simulation session."""

    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)  # system, user, assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="messages")
