"""Purpose: Integration service for Groq Llama 3.3 70B interactions using Groq SDK."""

import json
import logging
import asyncio
from groq import AsyncGroq
from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqService:
    """Encapsulates external AI provider calls and prompt execution using the Groq SDK."""

    def __init__(self) -> None:
        self.api_key = settings.groq_api_key
        self.model = settings.model_name
        self.provider = settings.model_provider
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        if self.api_key and self.api_key != "replace_with_real_key":
            self._client = AsyncGroq(api_key=self.api_key)
        else:
            self._client = None

    @property
    def client(self) -> AsyncGroq | None:
        """Lazily initialize and return the AsyncGroq client if API key is configured."""
        return self._client

    def clean_response(self, content: str) -> str:
        """Strip markdown formatting fences and extract JSON content robustly."""
        cleaned = content.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()
            
        if not (cleaned.startswith("{") and cleaned.endswith("}")):
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned = cleaned[start_idx:end_idx + 1]
                
        return cleaned

    def _clean_and_parse_json(self, content: str) -> dict:
        """Strip markdown formatting fences and parse JSON content robustly."""
        cleaned = self.clean_response(content)
        return json.loads(cleaned)

    async def generate_customer_response(
        self,
        prompt: str,
        system_message: str | None = None,
        response_format: dict | None = None
    ) -> str:
        """Generate raw model response using the official Groq SDK with timeout, retries, and logging."""
        client = self.client
        if not client:
            logger.error("Groq client not initialized (missing or placeholder API key).")
            raise ValueError("Groq client not initialized.")

        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        # Retry configuration: 3 retries (4 attempts total)
        max_attempts = 4
        delay = 1.0  # initial delay in seconds
        
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(
                    f"Submitting request to Groq (Model: {self.model}) - Attempt {attempt}/{max_attempts}"
                )
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.7,
                    "timeout": 30.0,
                }
                if response_format:
                    kwargs["response_format"] = response_format
                else:
                    kwargs["max_tokens"] = 1024

                chat_completion = await client.chat.completions.create(**kwargs)
                content = chat_completion.choices[0].message.content
                if content is None:
                    raise ValueError("Groq returned empty response content.")
                
                logger.info(f"Groq API call succeeded on attempt {attempt}")
                return content
            except Exception as e:
                logger.error(f"Groq API Error on attempt {attempt} of {max_attempts}: {e}")
                if attempt == max_attempts:
                    raise e
                # Exponential backoff delay
                await asyncio.sleep(delay)
                delay *= 2.0
        
        raise RuntimeError("All attempts to call Groq API failed.")

    async def generate(self, prompt: str, system_message: str | None = None) -> str:
        """Generate model output from prompt using Groq SDK."""
        try:
            return await self.generate_customer_response(prompt, system_message)
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return "Fallback response due to connection issues."

    async def test_groq_call(self) -> bool:
        """Perform a test connection/health check call to Groq API.
        
        Returns True if successful, False otherwise.
        """
        client = self.client
        if not client:
            logger.warning("Groq API Key is not set or placeholder. Test call bypassed.")
            return False
            
        messages = [{"role": "user", "content": "ping"}]
        try:
            await client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=5,
                timeout=10.0,
            )
            return True
        except Exception as e:
            logger.error(f"Groq API connection test failed: {e}")
            return False

    async def generate_structured_response(self, prompt: str, system_message: str | None = None) -> dict:
        """Call Groq API using JSON response format, implementing retries and error handling.
        
        Falls back to rule-based mock responses if request fails or API key is not configured.
        """
        client = self.client
        if not client:
            logger.info("Groq API key not configured or using default placeholder. Utilizing local fallback parser.")
            return self._generate_mock_structured_response(prompt)

        # Ensure the word 'json' is present in prompt or system message to satisfy Groq request validations
        if "json" not in prompt.lower() and (not system_message or "json" not in system_message.lower()):
            if system_message:
                system_message += " (respond in JSON format)"
            else:
                prompt += " (respond in JSON format)"

        try:
            content = await self.generate_customer_response(
                prompt=prompt,
                system_message=system_message,
                response_format={"type": "json_object"}
            )
            parsed = self._clean_and_parse_json(content)
            
            # Ensure required keys exist
            required_keys = [
                "customer_reply", "conversation_stage", "evaluation", 
                "decision_state", "coaching_feedback", "conversation_state"
            ]
            missing_keys = [k for k in required_keys if k not in parsed]
            if not missing_keys:
                return parsed
            else:
                raise ValueError(f"Groq response missing expected keys: {missing_keys}")
        except Exception as e:
            logger.error(f"Structured response generation failed: {e}. Falling back to mock scorecard.")
            return self._generate_mock_structured_response(prompt)

    def _generate_mock_structured_response(self, prompt: str) -> dict:
        """Generate static, rule-based structured responses for fallback or keyless operation."""
        prompt_lower = prompt.lower()
        
        # Defaults
        customer_reply = "I see. Can you tell me more about the features and standard trim options?"
        coaching_feedback = "Provide clear product specs and ask an open-ended question to confirm their needs."
        evaluation_data = {
            "communication": 80,
            "product_knowledge": 75,
            "needs_analysis": 70,
            "pricing_accuracy": 70,
            "professionalism": 85
        }
        decision_state = {
            "recommended_action": "show_specs",
            "customer_mood": "neutral"
        }
        conversation_state = {
            "hesitation_level": "medium",
            "active_objections": ["pricing"],
            "discussed_vehicles": []
        }
        
        # Extract stage based on history length in prompt
        msg_count = prompt_lower.count("salesperson:") + prompt_lower.count("customer:")
        if msg_count <= 2:
            stage = "greeting"
        elif msg_count <= 6:
            stage = "qualification"
        elif msg_count <= 10:
            stage = "presentation"
        elif msg_count <= 14:
            stage = "objection"
        else:
            stage = "closing"

        # Determine persona matching from prompt text
        if "jenkins" in prompt_lower or "family" in prompt_lower:
            conversation_state["discussed_vehicles"] = ["kia-carens-2025"]
            if any(k in prompt_lower for k in ["space", "seat", "carens", "third"]):
                customer_reply = "The Carens space looks good, but can we fit a child seat in the middle row easily while leaving room for groceries?"
                coaching_feedback = "Confirm the Carens' flexible one-touch tumble seat feature and detail the cargo volume."
                evaluation_data["needs_analysis"] = 85
                decision_state = {
                    "recommended_action": "highlight_features",
                    "customer_mood": "engaged"
                }
                conversation_state["hesitation_level"] = "low"
            elif any(k in prompt_lower for k in ["safety", "crash", "airbag"]):
                customer_reply = "With three kids in the back, safety is my absolute top concern. Are 6 airbags standard?"
                coaching_feedback = "Highlight that 6 airbags are standard on the Carens, building trust on safety."
                evaluation_data["professionalism"] = 95
                decision_state = {
                    "recommended_action": "confirm_safety",
                    "customer_mood": "reassured"
                }
                conversation_state["active_objections"] = []
            elif "hello" in prompt_lower or "hi" in prompt_lower:
                customer_reply = "Hello. My spouse and I are looking for a reliable vehicle with plenty of room for our kids. What do you recommend?"
                coaching_feedback = "Introduce yourself, acknowledge the family needs, and ask about their seating/cargo preferences."
        elif "alex" in prompt_lower or "budget" in prompt_lower:
            conversation_state["discussed_vehicles"] = ["kia-sonet-2025"]
            if any(k in prompt_lower for k in ["price", "budget", "msrp", "sonet"]):
                customer_reply = "Under $20k for the Kia Sonet MSRP sounds attractive. What are the final dealer fees, and is there a lease deal?"
                coaching_feedback = "Break down the Sonet's value pricing, keep financing options simple, and avoid pushing expensive extras."
                decision_state = {
                    "recommended_action": "quote_price",
                    "customer_mood": "cautious"
                }
                conversation_state["hesitation_level"] = "high"
            elif any(k in prompt_lower for k in ["add", "extra", "deal"]):
                customer_reply = "I read online that dealerships add fees for paint protection. Can I opt out of those?"
                coaching_feedback = "Acknowledge their pricing concern directly. Confirm transparency in dealer pricing."
                conversation_state["active_objections"] = ["dealer-add-ons"]
            elif "hello" in prompt_lower or "hi" in prompt_lower:
                customer_reply = "Hi there. I'm looking for a commuter car with high fuel economy and a low MSRP."
                coaching_feedback = "Focus on the Kia Sonet starting price of $19,900 and highlight its 32 MPG efficiency."
        elif "marcus" in prompt_lower or "performance" in prompt_lower:
            conversation_state["discussed_vehicles"] = ["kia-seltos-2025"]
            if any(k in prompt_lower for k in ["seltos", "engine", "turbo", "torque"]):
                customer_reply = "Does the Seltos have a turbocharged engine option, and what are the horsepowers and torque curves?"
                coaching_feedback = "Detail the Seltos' turbocharged performance option and highlight the dual-clutch transmission."
            elif "hello" in prompt_lower or "hi" in prompt_lower:
                customer_reply = "Hey. I'm interested in a vehicle that is fun to drive, handles well in corners, and has good tech connectivity."
                coaching_feedback = "Highlight the Seltos' turbo option and dynamic AWD handling capabilities."
        elif "elena" in prompt_lower or "eco" in prompt_lower:
            conversation_state["discussed_vehicles"] = ["kia-sonet-2025"]
            if any(k in prompt_lower for k in ["hybrid", "fuel", "battery"]):
                customer_reply = "I'm interested in hybrid options. How long is the battery warranty, and what is the degradation policy?"
                coaching_feedback = "Explain Kia's industry-leading 10-year/100,000-mile battery and hybrid warranty."
            elif "hello" in prompt_lower or "hi" in prompt_lower:
                customer_reply = "Hello. I want to minimize my fuel consumption and environmental footprint. What hybrid or EV models do you suggest?"
                coaching_feedback = "Suggest hybrid trim options or highly fuel-efficient vehicles like the Sonet, emphasizing MPG stats."

        return {
            "customer_reply": customer_reply,
            "conversation_stage": stage,
            "evaluation": evaluation_data,
            "decision_state": decision_state,
            "coaching_feedback": coaching_feedback,
            "conversation_state": conversation_state
        }

    async def generate_dialogue_and_hint(self, persona: dict, chat_history: list[dict]) -> dict:
        """Backwards compatible wrapper executing simulated dialogue turns via generate_structured_response."""
        prompt = f"Customer Persona details:\nName: {persona.get('name')}\nType: {persona.get('persona_type')}\n"
        prompt += f"Dialogue History:\n"
        for m in chat_history:
            role_label = "Salesperson" if m["role"] == "user" else "Customer"
            prompt += f"{role_label}: {m['content']}\n"
        return await self.generate_structured_response(prompt)
