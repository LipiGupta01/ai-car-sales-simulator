"""Purpose: Pydantic schemas for persona entities."""

import uuid
from pydantic import BaseModel, Field


class PersonaRead(BaseModel):
    """Response payload for customer persona details."""

    id: uuid.UUID
    key: str
    persona_type: str | None = None
    sympathy_level: str | None = None
    name: str
    age: int | None = None
    budget_range: str | None = None
    personality: str
    profile: str | None = None
    preferences: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
