"""Purpose: Test endpoints to validate dialogue pipelines without Groq API dependency."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.persona import Persona as DbPersona
from app.models.vehicle import Vehicle
from app.services.session_service import SessionService
from app.schemas.session_schema import SessionCreate
from app.services.conversation_orchestrator import ConversationOrchestrator

router = APIRouter(tags=["test"])


class ConversationTestInput(BaseModel):
    """Input parameters for simulation pipeline testing."""

    persona_key: str = Field(..., description="String key identifier for the customer persona")
    vehicle_key: str = Field(..., description="String key identifier for the vehicle")
    message: str = Field(..., description="The user message to send to the orchestrator")
    session_external_id: str | None = Field(None, description="Optional active session external ID for multi-turn history")


@router.post("/test/conversation", status_code=status.HTTP_200_OK)
async def test_conversation(payload: ConversationTestInput, db: Session = Depends(get_db)):
    """Execute simulated dialogue turns for testing the conversation pipeline."""
    # 1. Verify persona exists
    persona = db.query(DbPersona).filter(DbPersona.key == payload.persona_key).first()
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Persona key '{payload.persona_key}' not found."
        )

    # 2. Verify vehicle exists
    vehicle = db.query(Vehicle).filter(Vehicle.key == payload.vehicle_key).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle key '{payload.vehicle_key}' not found."
        )

    # 3. Retrieve or create training session for this persona
    session_service = SessionService(db)
    if payload.session_external_id:
        session = session_service.get_session_by_external_id(payload.session_external_id)
        if not session:
            session = session_service.create_session(SessionCreate(persona_id=persona.key))
    else:
        session = session_service.create_session(SessionCreate(persona_id=persona.key))

    # 4. Invoke orchestrator process_message in real mode
    orchestrator = ConversationOrchestrator(db, mock_mode=False)
    turn_result = await orchestrator.process_message(
        session_external_id=session.external_id,
        user_content=payload.message,
        vehicle_key=payload.vehicle_key
    )

    if not turn_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process conversation message."
        )

    return {
        "session_external_id": session.external_id,
        **turn_result
    }
