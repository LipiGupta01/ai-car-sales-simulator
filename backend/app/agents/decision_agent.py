"""Purpose: Decision agent module for parsing coaching feedback and state variables from shared LLM responses."""

import logging

logger = logging.getLogger(__name__)


class DecisionAgent:
    """Handles parsing and processing of dynamic coaching feedback and decision state from unified outputs."""

    def parse_feedback(self, shared_payload: dict) -> str:
        """Extract coaching feedback string from the shared API result."""
        feedback = shared_payload.get("coaching_feedback")
        if not feedback:
            feedback = shared_payload.get("coaching_hint")
            if not feedback:
                feedback = shared_payload.get("recommendation", "Ask open-ended questions about their family needs.")
        logger.info("Parsed coaching feedback recommendation.")
        return feedback

    def parse_decision_state(self, shared_payload: dict) -> dict:
        """Extract simulator state variables from the shared API result."""
        state = shared_payload.get("decision_state")
        if not state:
            state = {}
        logger.info(f"Parsed decision state payload: {state}")
        return state

    def get_instructions(self) -> str:
        """Returns coach prompt segments to inject into the unified request context."""
        return "Act as an expert real-time sales coach. Suggest a single tactical advice phrase for the salesperson."
