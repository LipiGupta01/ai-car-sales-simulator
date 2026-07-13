"""Purpose: Conversation Orchestrator service coordinating user turns and shared LLM operations."""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.session import Session as DbSession
from app.models.persona import Persona as DbPersona
from app.models.vehicle import Vehicle
from app.agents.communication_agent import CommunicationAgent
from app.agents.decision_agent import DecisionAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.services.groq_service import GroqService
from app.core.config import settings

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """Coordinates a single dialogue turn, invoking Groq and saving states in the database."""

    def __init__(
        self,
        db: Session,
        groq_service: GroqService = None,
        comm_agent: CommunicationAgent = None,
        dec_agent: DecisionAgent = None,
        eval_agent: EvaluationAgent = None,
        mock_mode: bool = False,
    ) -> None:
        """Initialize orchestrator with dependency injection supporting custom services/agents."""
        self.db = db
        self.groq_service = groq_service or GroqService()
        self.comm_agent = comm_agent or CommunicationAgent()
        self.dec_agent = dec_agent or DecisionAgent()
        self.eval_agent = eval_agent or EvaluationAgent()
        self.mock_mode = mock_mode

    def load_persona(self, persona_id: uuid.UUID) -> DbPersona | None:
        """Load customer persona by database ID."""
        return self.db.query(DbPersona).filter(DbPersona.id == persona_id).first()

    def load_vehicle(self, vehicle_key: str) -> Vehicle | None:
        """Load vehicle by its lookup key."""
        return self.db.query(Vehicle).filter(Vehicle.key == vehicle_key).first()

    def build_prompt_context(self, persona: DbPersona, history_list: list[dict], vehicle_context: str) -> str:
        """Build the prompt context combining showroom inventory specs and active chat history."""
        context = f"Showroom Inventory:\n{vehicle_context}\n\n"
        context += "Dialogue History:\n"
        for m in history_list:
            role_label = "Salesperson" if m["role"] == "user" else "Customer"
            context += f"{role_label}: {m['content']}\n"
        return context

    def save_messages(self, session_id: uuid.UUID, role: str, content: str) -> Message:
        """Save a message turn to the database and commit."""
        msg = Message(
            session_id=session_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(msg)
        self.db.commit()
        return msg

    def save_conversation(self, session_id: uuid.UUID, role: str, content: str) -> Message:
        """Save a message turn (backwards-compatible wrapper calling save_messages)."""
        return self.save_messages(session_id, role, content)

    async def generate_customer_response(self, prompt_context: str, system_message: str | None = None) -> dict:
        """Submit context to the LLM service or return mock response depending on mock_mode."""
        if self.mock_mode:
            logger.info("Mock mode is enabled. Returning mock structured response.")
            return {
                "customer_reply": "Mock response generated from persona context",
                "conversation_stage": "greeting",
                "decision_state": "engaged"
            }
        return await self.groq_service.generate_structured_response(prompt_context, system_message)

    async def process_message(
        self,
        session_external_id: str,
        user_content: str,
        vehicle_key: str | None = None
    ) -> dict | None:
        """Main turn-processing coordinator flow.

        Loads database records, prepares system settings and catalog context, submits requests,
        parses output variables, and saves dialogue updates to the database.
        """
        # 1. Fetch active session
        db_session = self.db.query(DbSession).filter(DbSession.external_id == session_external_id).first()
        if not db_session:
            logger.error(f"Session {session_external_id} not found in database.")
            return None

        # 2. Save user message to database
        user_msg = self.save_messages(db_session.id, "user", user_content)

        # 3. Retrieve complete dialogue history
        history_msgs = (
            self.db.query(Message)
            .filter(Message.session_id == db_session.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        history_list = [{"role": m.role, "content": m.content} for m in history_msgs]

        # 4. Retrieve associated customer persona
        db_persona = self.load_persona(db_session.persona_id)
        if not db_persona:
            logger.error(f"Persona for session {session_external_id} not found.")
            return None

        # 5. Load vehicle catalog context for prompt grounding
        vehicles = self.db.query(Vehicle).all()
        vehicle_lines = []
        for v in vehicles:
            features_str = ", ".join(v.features) if v.features else "none"
            vehicle_lines.append(
                f"- {v.year} {v.make} {v.model} ({v.category}, Fuel: {v.fuel_type}): "
                f"MSRP ${v.msrp:,.2f}. Features: {features_str}. Status: {v.inventory_status}"
            )
        vehicle_context = "\n".join(vehicle_lines) if vehicle_lines else "No vehicles in inventory."

        # Select matching vehicle for prompt builder based on persona type
        if not vehicle_key:
            p_type = db_persona.persona_type or ""
            vehicle_key = "kia-sonet-2025"
            if "family" in p_type.lower():
                vehicle_key = "kia-carens-2025"
            elif "performance" in p_type.lower():
                vehicle_key = "kia-seltos-2025"
            elif "eco" in p_type.lower():
                vehicle_key = "kia-sonet-2025"

        target_vehicle = self.load_vehicle(vehicle_key)
        if not target_vehicle:
            target_vehicle = self.db.query(Vehicle).first()

        # 6. Build the system prompt using the prompt framework
        from app.prompts.customer_prompt import build_customer_prompt
        
        system_message = build_customer_prompt(
            persona=db_persona,
            vehicle=target_vehicle,
            sympathy_level=db_persona.sympathy_level or "Moderate Sympathy"
        )

        # 7. Build history context + vehicles list
        prompt_context = self.build_prompt_context(db_persona, history_list, vehicle_context)

        # 8. Generate customer response from AI
        shared_payload = await self.generate_customer_response(prompt_context, system_message)

        # 9. Parse response fields using modular agents
        customer_reply_text = self.comm_agent.parse_reply(shared_payload)
        stage_text = self.comm_agent.parse_stage(shared_payload)
        coaching_feedback_text = self.dec_agent.parse_feedback(shared_payload)
        decision_state_dict = self.dec_agent.parse_decision_state(shared_payload)
        evaluation_dict = self.eval_agent.parse_turn_evaluation(shared_payload)
        conversation_state_dict = shared_payload.get("conversation_state", {})

        # 10. Save customer message
        customer_msg = self.save_messages(db_session.id, "assistant", customer_reply_text)

        # Update session status if completed
        if stage_text in ["finished", "closing"]:
            db_session.status = "completed"
            self.db.commit()

        return {
            "customer_reply": customer_reply_text,
            "conversation_stage": stage_text,
            "evaluation": evaluation_dict,
            "decision_state": decision_state_dict,
            "coaching_feedback": coaching_feedback_text,
            "conversation_state": conversation_state_dict,
            "user_msg_timestamp": user_msg.created_at.isoformat(),
            "customer_msg_timestamp": customer_msg.created_at.isoformat()
        }

    async def execute_turn(self, session_external_id: str, user_content: str) -> dict | None:
        """Backwards compatible wrapper executing a turn using the process_message flow."""
        return await self.process_message(session_external_id, user_content)
