"""Purpose: Vehicle and Persona endpoints for knowledge base browsing."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.vehicle_schema import VehicleRead
from app.schemas.persona_schema import PersonaRead
from app.services.vehicle_service import VehicleService
from app.services.persona_service import PersonaService

router = APIRouter(tags=["knowledge_base"])


@router.get("/vehicles", response_model=list[VehicleRead])
async def list_vehicles(db: Session = Depends(get_db)) -> list[VehicleRead]:
    """Retrieve list of all Kia vehicles in the knowledge base."""
    service = VehicleService(db)
    return service.list_vehicles()


@router.get("/personas", response_model=list[PersonaRead])
async def list_personas(db: Session = Depends(get_db)) -> list[PersonaRead]:
    """Retrieve list of available customer personas for simulation selection."""
    service = PersonaService(db)
    return service.list_personas()
