"""Purpose: Service for evaluation orchestration and database operations."""

from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.session import Session as DbSession
from app.models.evaluation import Evaluation
from app.models.session_metrics import SessionMetrics
from app.models.message import Message
from app.agents.evaluation_agent import EvaluationAgent


class EvaluationService:
    """Coordinates evaluation pipeline for coaching and scoring."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.agent = EvaluationAgent()

    async def evaluate_session(self, session_external_id: str) -> Evaluation | None:
        """Run evaluation agent on completed session and save report."""
        db_session = self.db.query(DbSession).filter(DbSession.external_id == session_external_id).first()
        if not db_session:
            return None

        # Retrieve dialogue history
        history_msgs = (
            self.db.query(Message)
            .filter(Message.session_id == db_session.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        history_list = [{"role": m.role, "content": m.content} for m in history_msgs]

        # Call evaluation agent
        agent_result = await self.agent.run(session_external_id, history_list)

        # Create or update evaluation record
        evaluation = self.db.query(Evaluation).filter(Evaluation.session_id == db_session.id).first()
        if not evaluation:
            evaluation = Evaluation(
                session_id=db_session.id,
                score=agent_result.get("score", 70),
                summary=agent_result.get("summary", "Placeholder evaluation summary."),
                status="completed",
                breakdown=agent_result.get("breakdown", {
                    "communication": 70,
                    "product_knowledge": 70,
                    "needs_analysis": 70,
                    "pricing_accuracy": 70,
                    "professionalism": 70
                }),
                recommendations=agent_result.get("recommendations", ["Improve objection handling."]),
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(evaluation)
        else:
            evaluation.score = agent_result.get("score", evaluation.score)
            evaluation.summary = agent_result.get("summary", evaluation.summary)
            evaluation.status = "completed"
            evaluation.breakdown = agent_result.get("breakdown", evaluation.breakdown)
            evaluation.recommendations = agent_result.get("recommendations", evaluation.recommendations)

        # Update session status
        db_session.status = "evaluated"

        # Save session metrics
        for metric, value in evaluation.breakdown.items():
            db_metric = SessionMetrics(
                session_id=db_session.id,
                metric_name=metric,
                metric_value=str(value)
            )
            self.db.add(db_metric)

        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation

    def get_evaluation_by_session_external_id(self, session_external_id: str) -> Evaluation | None:
        """Retrieve evaluation details for a specific session."""
        db_session = self.db.query(DbSession).filter(DbSession.external_id == session_external_id).first()
        if not db_session:
            return None
        return self.db.query(Evaluation).filter(Evaluation.session_id == db_session.id).first()
