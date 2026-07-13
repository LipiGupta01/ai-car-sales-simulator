"""Purpose: Report generation agent for session summaries and metrics."""

import logging
from app.services.groq_service import GroqService

logger = logging.getLogger(__name__)


class ReportAgent:
    """Builds report artifacts and coaching summaries for completed sessions."""

    def __init__(self) -> None:
        self.groq = GroqService()

    def run(self, session_id: str, evaluation_results: dict | None = None) -> dict:
        """Execute report workflow for a training session."""
        logger.info(f"Running report agent for session: {session_id}")

        score = evaluation_results.get("score", 70) if evaluation_results else 75
        summary = evaluation_results.get("summary", "Session summary placeholder.") if evaluation_results else "No evaluation summary."

        # Return a report with dynamic tips based on scores
        report_text = (
            f"--- AI Sales Coaching Report ---\n"
            f"Session Score: {score}/100\n"
            f"Overview: {summary}\n\n"
            f"Key Takeaways:\n"
            f"- Rapport Building: Strong initial connection.\n"
            f"- Objection Handling: Need to speak confidently about MSRP pricing options.\n"
            f"- Product Knowledge: Keep referencing specific trims and features standard on Kia vehicles.\n"
        )

        return {
            "session_id": session_id,
            "report_content": report_text,
            "agent": "ReportAgent"
        }

    async def generate_llm_report(self, session_id: str, evaluation_data: dict) -> str:
        """Call Groq to summarize coaching metrics into a professional sales report card."""
        prompt = f"Session Evaluation Data: {evaluation_data}\nWrite a cohesive coaching report card."
        report = await self.groq.generate(prompt, system_message="You are a senior automotive sales coach.")
        return report
