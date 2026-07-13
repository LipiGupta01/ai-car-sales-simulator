"""Purpose: Pydantic schemas for session API payloads."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    """Request payload to create a training session."""

    persona_id: str = Field(..., min_length=1, description="String key identifier for the customer persona")


class SessionRead(BaseModel):
    """Response payload for session data."""

    id: uuid.UUID
    external_id: str
    persona_id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
