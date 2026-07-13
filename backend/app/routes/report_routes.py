"""Purpose: Report endpoints for session analytics and coaching summaries."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.evaluation_schema import EvaluationRead
from app.services.evaluation_service import EvaluationService

router = APIRouter(tags=["reports"])


@router.get("/reports/{session_id}", response_model=EvaluationRead)
async def get_report(session_id: str, db: Session = Depends(get_db)) -> EvaluationRead:
    """Get evaluation and coaching summary report for a completed session."""
    eval_service = EvaluationService(db)
    evaluation = eval_service.get_evaluation_by_session_external_id(session_id)
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coaching report not found for session: {session_id}. Ensure session is completed and evaluated first."
        )
    return evaluation
