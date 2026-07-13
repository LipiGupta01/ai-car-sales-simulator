"""Purpose: Pydantic schemas for vehicle entities."""

import uuid
from pydantic import BaseModel, Field


class VehicleRead(BaseModel):
    """Response payload for vehicle specifications details."""

    id: uuid.UUID
    key: str
    make: str
    model: str
    year: int
    msrp: float
    category: str | None = None
    fuel_type: str | None = None
    inventory_status: str
    summary: str | None = None
    features: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}
