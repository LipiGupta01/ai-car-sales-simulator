"""Purpose: Communication agent module for parsing customer replies and stages from shared LLM responses."""

import logging

logger = logging.getLogger(__name__)


class CommunicationAgent:
    """Handles parsing and processing of simulated customer dialogue and stage from unified outputs."""

    def parse_reply(self, shared_payload: dict) -> str:
        """Extract customer dialogue string from the shared API result."""
        reply = shared_payload.get("customer_reply")
        if not reply:
            reply = shared_payload.get("reply", "I am thinking about your offer...")
        logger.info("Parsed customer dialogue reply.")
        return reply

    def parse_stage(self, shared_payload: dict) -> str:
        """Extract current conversation stage from the shared API result."""
        stage = shared_payload.get("conversation_stage")
        if not stage:
            stage = "qualification"
        logger.info(f"Parsed conversation stage: {stage}")
        return stage

    def get_instructions(self, persona: dict) -> str:
        """Returns customer prompt segments to inject into the unified request context."""
        return (
            f"Act as simulated customer: {persona.get('name')}. "
            f"Persona Type: {persona.get('persona_type')}. "
            f"Personality profile: {persona.get('personality')}. "
            f"Preferences: {persona.get('preferences')}. "
            f"Goals: {persona.get('goals')}. "
            f"Pain Points: {persona.get('pain_points')}."
        )
