"""Purpose: Service for persona loading, seeding, and database queries."""

import json
import os
from sqlalchemy.orm import Session
from app.models.persona import Persona


class PersonaService:
    """Provides persona lookup and seeding operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_personas(self) -> list[Persona]:
        """Retrieve all personas stored in the database."""
        personas = self.db.query(Persona).all()
        if not personas:
            # Auto-seed if database is empty
            self.seed_personas()
            personas = self.db.query(Persona).all()
        return personas

    def get_persona_by_key(self, key: str) -> Persona | None:
        """Find a single persona profile by its string key."""
        return self.db.query(Persona).filter(Persona.key == key).first()

    def seed_personas(self) -> None:
        """Seed personas from seed_data/personas.json if not present."""
        seed_paths = [
            "../seed_data/personas.json",
            "seed_data/personas.json",
            "../../seed_data/personas.json"
        ]
        seed_path = None
        for path in seed_paths:
            if os.path.exists(path):
                seed_path = path
                break

        if not seed_path:
            return

        with open(seed_path, encoding="utf-8") as f:
            data = json.load(f)

        for p_data in data:
            # Check if exists
            existing = self.db.query(Persona).filter(Persona.key == p_data["id"]).first()
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
                self.db.add(persona)
        self.db.commit()
