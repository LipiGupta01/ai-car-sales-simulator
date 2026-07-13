"""Purpose: Pydantic schemas for evaluation and report payloads."""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class EvaluationRead(BaseModel):
    """Response payload for session evaluation outputs."""

    id: uuid.UUID
    session_id: uuid.UUID
    score: int
    summary: str
    status: str
    breakdown: dict[str, int] = Field(default_factory=dict)
    recommendations: list[str] = Field(default_factory=list)
    created_at: datetime

    model_config = {"from_attributes": True}
