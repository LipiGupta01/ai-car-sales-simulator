"""Purpose: Standalone database seeder script for customer personas."""

import json
import os
import sys

# Ensure backend directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app.models
from app.core.database import SessionLocal, Base, engine
from app.models.persona import Persona


def seed():
    """Seed personas into the database."""
    print("Initializing database tables for personas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Locate personas.json
    seed_paths = [
        "seed_data/personas.json",
        "../seed_data/personas.json",
        "backend/seed_data/personas.json"
    ]
    seed_path = None
    for p in seed_paths:
        if os.path.exists(p):
            seed_path = p
            break
            
    if not seed_path:
        print("Error: Could not locate seed_data/personas.json")
        sys.exit(1)
        
    print(f"Reading persona seed data from {seed_path}...")
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)
        
    count = 0
    for p_data in data:
        existing = db.query(Persona).filter(Persona.key == p_data["id"]).first()
        if not existing:
            persona = Persona(
                key=p_data["id"],
                persona_type=p_data.get("persona_type"),
                sympathy_level=p_data.get("sympathy_level"),
                name=p_data["name"],
                age=p_data.get("age"),
                budget_range=p_data.get("budget_range"),
                personality=p_data["personality"],
                profile=f"Goals: {', '.join(p_data.get('goals', []))}. Pain Points: {', '.join(p_data.get('pain_points', []))}",
                preferences=p_data.get("preferences", []),
                goals=p_data.get("goals", []),
                pain_points=p_data.get("pain_points", [])
            )
            db.add(persona)
            count += 1
            print(f"Adding persona: {p_data['name']} ({p_data['id']})")
            
    db.commit()
    db.close()
    print(f"Successfully seeded {count} new persona profiles.")


if __name__ == "__main__":
    seed()
