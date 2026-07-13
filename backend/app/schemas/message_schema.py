"""Purpose: Pydantic schemas for message exchange payloads."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class MessageCreate(BaseModel):
    """Request payload to submit a user message."""

    session_id: str = Field(..., description="External UUID/key of the active session")
    content: str = Field(..., min_length=1, description="Text content of the message")
    role: str = Field("user", description="Sender role: user, assistant, system")


class MessageRead(BaseModel):
    """Response payload for chat messages."""

    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}
