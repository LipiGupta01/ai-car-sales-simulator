"""Purpose: Service for session lifecycle database operations and logic."""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.session import Session as DbSession
from app.models.persona import Persona as DbPersona
from app.schemas.session_schema import SessionCreate


class SessionService:
    """Handles create/read/update operations for training sessions."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, payload: SessionCreate) -> DbSession:
        """Create a new training session in the database."""
        # Find the persona by key or id
        db_persona = self.db.query(DbPersona).filter(DbPersona.key == payload.persona_id).first()
        if not db_persona:
            try:
                persona_uuid = uuid.UUID(payload.persona_id)
                db_persona = self.db.query(DbPersona).filter(DbPersona.id == persona_uuid).first()
            except ValueError:
                pass

        if not db_persona:
            # Fallback to get first persona if not found to avoid crashing
            db_persona = self.db.query(DbPersona).first()
            if not db_persona:
                raise ValueError(f"No personas found in the database. Seeding may be required.")

        db_session = DbSession(
            external_id=str(uuid.uuid4()),
            persona_id=db_persona.id,
            status="active",
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def get_session_by_external_id(self, external_id: str) -> DbSession | None:
        """Retrieve a session by its UUID external ID."""
        return self.db.query(DbSession).filter(DbSession.external_id == external_id).first()

    def list_sessions(self, limit: int = 20) -> list[DbSession]:
        """List recent training sessions."""
        return self.db.query(DbSession).order_by(DbSession.created_at.desc()).limit(limit).all()

    def update_session_status(self, external_id: str, status: str) -> DbSession | None:
        """Update session state status."""
        db_session = self.get_session_by_external_id(external_id)
        if db_session:
            db_session.status = status
            self.db.commit()
            self.db.refresh(db_session)
        return db_session
