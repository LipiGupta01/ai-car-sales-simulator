"""Purpose: Session endpoints for simulation lifecycle operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.session_schema import SessionCreate, SessionRead
from app.schemas.evaluation_schema import EvaluationRead
from app.services.session_service import SessionService
from app.services.evaluation_service import EvaluationService

router = APIRouter(tags=["sessions"])


@router.post("/sessions", response_model=SessionRead, status_code=status.HTTP_201_CREATED)
async def create_session(payload: SessionCreate, db: Session = Depends(get_db)) -> SessionRead:
    """Create a new training simulation session for a selected persona."""
    service = SessionService(db)
    session = service.create_session(payload)
    return session


@router.get("/sessions", response_model=list[SessionRead])
async def list_sessions(db: Session = Depends(get_db)) -> list[SessionRead]:
    """Retrieve list of all training sessions in descending chronological order."""
    service = SessionService(db)
    return service.list_sessions()


@router.get("/sessions/{session_id}", response_model=SessionRead)
async def get_session(session_id: str, db: Session = Depends(get_db)) -> SessionRead:
    """Retrieve session details by its external UUID."""
    service = SessionService(db)
    session = service.get_session_by_external_id(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return session


@router.post("/sessions/{session_id}/evaluate", response_model=EvaluationRead)
async def evaluate_session(session_id: str, db: Session = Depends(get_db)) -> EvaluationRead:
    """Execute evaluation agent, score dialogue performance, and finalize session."""
    eval_service = EvaluationService(db)
    evaluation = await eval_service.evaluate_session(session_id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or could not be evaluated"
        )
    return evaluation
