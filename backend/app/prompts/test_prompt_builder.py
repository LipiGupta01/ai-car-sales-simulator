"""Purpose: Test utility to generate and inspect simulated customer prompts."""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.prompts.customer_prompt import build_customer_prompt

# 1. Define mock personas matching DB seeded data
family_persona = {
    "name": "Sarah & Mike Jenkins",
    "persona_type": "family",
    "personality": "Practical, detail-oriented family coordinators",
    "goals": ["Comfortably transport three kids and luggage", "Low maintenance cost and high warranty coverage"],
    "preferences": ["Spacious cabin", "Top crash safety ratings", "Rear-seat USB chargers", "Kia Carens style space"],
    "pain_points": ["Aggressive upselling of luxury packages", "Vague answers about third-row legroom and crash safety tests"],
    "budget_range": "35000-45000"
}

budget_persona = {
    "name": "Alex Thompson",
    "persona_type": "budget",
    "personality": "Cautious, price-sensitive, researched",
    "goals": ["Establish low monthly lease or loan payment", "Minimize hidden charges"],
    "preferences": ["Lowest possible MSRP", "Excellent city fuel economy", "Bluetooth standard connectivity"],
    "pain_points": ["Dealer add-ons", "Being pushed to look at higher trim models"],
    "budget_range": "18000-25000"
}

performance_persona = {
    "name": "Marcus Vance",
    "persona_type": "performance",
    "personality": "Enthusiastic, tech-focused, specifications-driven",
    "goals": ["Verify dynamic handling capabilities and engine torque specs", "Ensure advanced connectivity"],
    "preferences": ["Turbocharged engine", "Paddle shifters", "Sport-tuned suspension"],
    "pain_points": ["Sales representatives who do not understand mechanical specs"],
    "budget_range": "40000-55000"
}

eco_persona = {
    "name": "Elena Rostova",
    "persona_type": "eco",
    "personality": "Environmentally conscious, analytical, quiet",
    "goals": ["Minimize daily carbon footprint", "Maximize hybrid mileage"],
    "preferences": ["EV or Hybrid powertrain", "Regenerative braking metrics"],
    "pain_points": ["Vague explanations of battery warranty and degradation"],
    "budget_range": "30000-40000"
}

# 2. Define mock vehicles matching DB seeded data
carens_vehicle = {
    "make": "Kia",
    "model": "Carens",
    "year": "2025",
    "category": "MPV/MUV",
    "features": ["6 Airbags standard", "One-touch electric tumble second row", "Roof vents for 2nd/3rd rows"],
    "msrp": 32000.00,
    "key": "kia-carens-2025"
}

sonet_vehicle = {
    "make": "Kia",
    "model": "Sonet",
    "year": "2025",
    "category": "Compact SUV",
    "features": ["8-inch touchscreen", "Standard Bluetooth hands-free", "32 MPG combined rating"],
    "msrp": 19900.00,
    "key": "kia-sonet-2025"
}

seltos_vehicle = {
    "make": "Kia",
    "model": "Seltos",
    "year": "2025",
    "category": "Mid SUV",
    "features": ["1.6L Turbocharged engine", "GT-Line AWD setup", "Paddle shifters", "Bose Audio system"],
    "msrp": 42000.00,
    "key": "kia-seltos-2025"
}

# 3. Setup test scenarios
scenarios = [
    {
        "title": "Scenario 1: Family Buyer + High Sympathy",
        "persona": family_persona,
        "vehicle": carens_vehicle,
        "sympathy": "High"
    },
    {
        "title": "Scenario 2: Budget Buyer + Low Sympathy",
        "persona": budget_persona,
        "vehicle": sonet_vehicle,
        "sympathy": "Low"
    },
    {
        "title": "Scenario 3: Performance Enthusiast + Moderate Sympathy",
        "persona": performance_persona,
        "vehicle": seltos_vehicle,
        "sympathy": "Moderate"
    },
    {
        "title": "Scenario 4: Eco-Conscious Buyer + Moderate Sympathy",
        "persona": eco_persona,
        "vehicle": sonet_vehicle,
        "sympathy": "Moderate"
    }
]

def run_tests():
    print("=" * 80)
    print("RUNNING PROMPT BUILDER TESTING UTILITY")
    print("=" * 80)
    
    for idx, s in enumerate(scenarios, 1):
        print(f"\n--- {s['title']} ---")
        prompt = build_customer_prompt(s["persona"], s["vehicle"], s["sympathy"])
        
        # Verify content exists in generated prompt
        assert s["persona"]["name"] in prompt, "Persona Name missing"
        assert s["vehicle"]["model"] in prompt, "Vehicle Model missing"
        assert s["sympathy"] in prompt, "Sympathy level missing"
        assert "SECURITY GUARDRAILS & SIMULATION INTEGRITY" in prompt, "Guardrails missing"
        assert "EXAMPLES" in prompt, "Few-shots missing"
        
        # Print preview of the generated prompt (first 20 lines + last 10 lines)
        lines = prompt.strip().split("\n")
        print("\n[PROMPT PREVIEW (FIRST 20 LINES)]")
        print("\n".join(lines[:20]))
        print("\n...")
        print("[PROMPT PREVIEW (LAST 10 LINES)]")
        print("\n".join(lines[-10:]))
        print("-" * 80)
        
    print("\nAll prompt builder assertions passed successfully!")

if __name__ == "__main__":
    run_tests()
