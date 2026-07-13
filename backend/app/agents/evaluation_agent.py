import json
import logging
from app.services.groq_service import GroqService
from app.prompts.system_prompts import EVALUATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class EvaluationAgent:
    """Evaluates session messages and computes performance quality metrics."""

    def __init__(self) -> None:
        self.groq = GroqService()

    def parse_turn_evaluation(self, shared_payload: dict) -> dict:
        """Extract intermediate evaluation feedback from the shared API result."""
        evaluation = shared_payload.get("evaluation")
        if not evaluation:
            evaluation = {}
        logger.info(f"Parsed turn evaluation details: {evaluation}")
        return evaluation

    async def run(self, session_id: str, chat_history: list[dict] = None) -> dict:
        """Execute evaluation workflow for a completed training session."""
        logger.info(f"Running session evaluation for: {session_id}")

        if self.groq.api_key and self.groq.api_key != "replace_with_real_key" and chat_history:
            try:
                evaluation_result = await self.evaluate_with_llm(session_id, chat_history)
                return evaluation_result
            except Exception as e:
                logger.error(f"Error during live LLM evaluation: {e}. Falling back to mock scorecard.")

        # Default static scoring report with updated performance categories
        return {
            "session_id": session_id,
            "score": 85,
            "summary": "Great overall performance! You established rapport quickly, handled the customer's vehicle inquiries, and remained highly professional. Try to conduct a more structured needs analysis and explain standard pricing details clearly.",
            "breakdown": {
                "communication": 88,
                "product_knowledge": 85,
                "needs_analysis": 78,
                "pricing_accuracy": 80,
                "professionalism": 90
            },
            "recommendations": [
                "Acknowledge the customer's safety worries before jumping into vehicle features.",
                "Detail Kia's 10-year warranty when budget and value objections arise.",
                "Use an open-ended closing question like 'Would you like to schedule a test drive for the Seltos this weekend?'"
            ],
            "agent": "EvaluationAgent"
        }

    async def evaluate_with_llm(self, session_id: str, chat_history: list[dict]) -> dict:
        """Trigger Groq API to analyze dialogue transcripts and produce a JSON evaluation payload."""
        dialogue_text = ""
        for m in chat_history:
            role_label = "Salesperson" if m["role"] == "user" else "Customer"
            dialogue_text += f"{role_label}: {m['content']}\n"

        prompt = f"Analyze the following dealership dialogue history:\n{dialogue_text}"
        res = await self.groq.generate(prompt, system_message=EVALUATION_SYSTEM_PROMPT)
        logger.info(f"LLM evaluation raw response: {res}")

        clean_res = res.strip()
        if clean_res.startswith("```json"):
            clean_res = clean_res[7:]
        if clean_res.endswith("```"):
            clean_res = clean_res[:-3]
        clean_res = clean_res.strip()

        parsed = json.loads(clean_res)
        return {
            "session_id": session_id,
            "score": parsed.get("score", 80),
            "summary": parsed.get("summary", "Session evaluation completed."),
            "breakdown": parsed.get("breakdown", {
                "communication": 80,
                "product_knowledge": 80,
                "needs_analysis": 80,
                "pricing_accuracy": 80,
                "professionalism": 80
            }),
            "recommendations": parsed.get("recommendations", ["Continue practicing regular objection handling exercises."])
        }
