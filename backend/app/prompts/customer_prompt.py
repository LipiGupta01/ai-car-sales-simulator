"""Purpose: Customer persona prompt builder coordinating metadata, vehicle info, and guardrails."""

from app.core.config import settings
from app.prompts.guardrails import GUARDRAILS
from app.prompts.few_shot_examples import (
    FAMILY_BUYER_EXAMPLES,
    BUDGET_BUYER_EXAMPLES,
    PERFORMANCE_ENTHUSIAST_EXAMPLES,
    ECO_CONSCIOUS_EXAMPLES,
)


def _get_val(obj, key, default=""):
    """Helper to extract attribute value from dict or DB model object."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _format_list(val):
    """Helper to cleanly format list values into comma-separated strings."""
    if not val:
        return "None specified"
    if isinstance(val, str):
        return val
    if isinstance(val, list):
        return ", ".join(val)
    return str(val)


def build_customer_prompt(persona, vehicle, sympathy_level) -> str:
    """Generate a system prompt combining persona, vehicle, showroom info, sympathy level, guardrails, and few-shots."""
    
    # 1. Persona Information
    name = _get_val(persona, "name", "Valued Customer")
    persona_type = _get_val(persona, "persona_type", "Standard")
    personality = _get_val(persona, "personality", "Standard buyer profile")
    goals = _format_list(_get_val(persona, "goals", []))
    preferences = _format_list(_get_val(persona, "preferences", []))
    pain_points = _format_list(_get_val(persona, "pain_points", []))
    budget_range = _get_val(persona, "budget_range", "Standard")

    # 2. Vehicle Context
    make = _get_val(vehicle, "make", "Kia")
    model = _get_val(vehicle, "model", "Vehicle")
    year = _get_val(vehicle, "year", "2025")
    vehicle_name = f"{year} {make} {model}"
    category = _get_val(vehicle, "category", "SUV/Crossover")
    features = _format_list(_get_val(vehicle, "features", []))
    msrp = _get_val(vehicle, "msrp", 0.0)
    try:
        price_str = f"${float(msrp):,.2f}"
    except (ValueError, TypeError):
        price_str = str(msrp)

    # 3. Showroom Context
    showroom_name = settings.showroom_name
    showroom_city = settings.showroom_city
    showroom_state = settings.showroom_state
    showroom_country = settings.showroom_country
    showroom_address = settings.showroom_address
    showroom_location_detail = f"{showroom_name} in {showroom_city}, {showroom_state}, {showroom_country} (Address: {showroom_address})"

    # 4. Sympathy Guidelines
    sympathy_clean = str(sympathy_level).lower()
    if "high" in sympathy_clean:
        sympathy_guidelines = (
            "You have HIGH SYMPATHY. Be exceptionally friendly, collaborative, patient, and appreciative of the salesperson. "
            "Forgive minor salesperson mistakes, express gratitude, listen closely, and actively consider test drives or package deals."
        )
    elif "low" in sympathy_clean:
        sympathy_guidelines = (
            "You have LOW SYMPATHY. Be highly skeptical, impatient, critical, and difficult to please. "
            "Challenge sales claims, demand exact proof, keep answers brief and dry, reject pushy sales tactics, and object to add-ons immediately."
        )
    else:  # Moderate / default
        sympathy_guidelines = (
            "You have MODERATE SYMPATHY. Be professional, neutral, objective, and task-oriented. "
            "Expect clear answers, raise logical objections when appropriate, and remain reasonable but demanding."
        )

    # 5. Few-Shot Selection
    p_type_clean = str(persona_type).lower()
    if "family" in p_type_clean:
        few_shots = FAMILY_BUYER_EXAMPLES
    elif "budget" in p_type_clean:
        few_shots = BUDGET_BUYER_EXAMPLES
    elif "performance" in p_type_clean:
        few_shots = PERFORMANCE_ENTHUSIAST_EXAMPLES
    elif "eco" in p_type_clean:
        few_shots = ECO_CONSCIOUS_EXAMPLES
    else:
        few_shots = BUDGET_BUYER_EXAMPLES

    # 6. Assemble complete prompt
    return f"""### 1. INSTRUCTIONS
You are a simulated customer visiting a Kia showroom.
Showroom Location Context: {showroom_location_detail}
Your Name: {name}

Act strictly according to your customer profile:
- Persona Type: {persona_type}
- Personality: {personality}
- Seating/Budget/Purchase Goals: {goals}
- Vehicle Preferences: {preferences}
- Pain Points & Hesitations: {pain_points}
- Budget Range: {budget_range}

Sympathy Guidelines:
- Style: {sympathy_level}
- Rules: {sympathy_guidelines}

Primary practice vehicle of interest:
- Vehicle Name: {vehicle_name}
- Category: {category}
- Key Specs & Features: {features}
- MSRP: {price_str}

Your primary task is to simulate dialogue with the salesperson (the user) dynamically. Ask questions about this vehicle (especially its specs and features), raise objections matching your profile, and negotiate appropriately.
Never state you are an AI. Keep response dialogue brief, natural, and realistic (1-3 sentences per turn).

{few_shots}

{GUARDRAILS}

### 4. EXPECTED OUTPUT FORMAT
You must respond with a strict, valid JSON object containing exactly these 6 keys. Do not include markdown code fence formatting or other wrapping text outside of the raw JSON:
{{
  "customer_reply": "Your dialogue reply text (1-3 sentences).",
  "conversation_stage": "One of: greeting, qualification, presentation, objection, closing, finished.",
  "evaluation": {{
    "communication": 80,
    "product_knowledge": 75,
    "needs_analysis": 85,
    "pricing_accuracy": 70,
    "professionalism": 90
  }},
  "decision_state": {{
    "recommended_action": "Action for the salesperson (e.g., ask discovery questions, present specs, quote MSRP).",
    "customer_mood": "Mood description (e.g., cooperative, cautious, defensive, interested)."
  }},
  "coaching_feedback": "A short, 1-sentence tactical coaching advice phrase advising the salesperson on what move to make next.",
  "conversation_state": {{
    "active_objections": ["pricing", "space", "add-on-fees"],
    "hesitation_level": "medium",
    "discussed_vehicles": ["{_get_val(vehicle, 'key', 'vehicle-key')}"]
  }}
}}
"""
