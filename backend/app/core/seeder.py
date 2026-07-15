"""Purpose: Seed default personas and vehicles into the database idempotently."""

import json
import os
import logging
from sqlalchemy.orm import Session
from app.models.persona import Persona
from app.models.vehicle import Vehicle

logger = logging.getLogger("seeder")


def find_seed_file(filename: str) -> str | None:
    """Search for the seed file in multiple potential directories."""
    paths = [
        os.path.join("seed_data", filename),
        os.path.join("..", "seed_data", filename),
        os.path.join("backend", "seed_data", filename),
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None


def seed_personas(db: Session) -> int:
    """Seed personas if the table is empty or does not contain them."""
    count_existing = db.query(Persona).count()
    if count_existing > 0:
        logger.info(f"Personas table already contains {count_existing} records. Skipping seeding.")
        return 0

    seed_path = find_seed_file("personas.json")
    if not seed_path:
        logger.error("Could not locate personas.json seed file.")
        return 0

    logger.info(f"Reading persona seed data from {seed_path}...")
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
    
    db.commit()
    logger.info(f"Successfully seeded {count} personas.")
    return count


def seed_vehicles(db: Session) -> int:
    """Seed vehicles if the table is empty or does not contain them."""
    count_existing = db.query(Vehicle).count()
    if count_existing > 0:
        logger.info(f"Vehicles table already contains {count_existing} records. Skipping seeding.")
        return 0

    seed_path = find_seed_file("vehicles.json")
    if not seed_path:
        logger.error("Could not locate vehicles.json seed file.")
        return 0

    logger.info(f"Reading vehicle seed data from {seed_path}...")
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for v_data in data:
        existing = db.query(Vehicle).filter(Vehicle.key == v_data["id"]).first()
        if not existing:
            vehicle = Vehicle(
                key=v_data["id"],
                make=v_data["make"],
                model=v_data["model"],
                year=v_data["year"],
                msrp=v_data["msrp"],
                category=v_data.get("category"),
                fuel_type=v_data.get("fuel_type"),
                inventory_status=v_data.get("inventory_status", "in_stock"),
                summary=f"{v_data['year']} {v_data['make']} {v_data['model']} has MSRP ${v_data['msrp']:,}.",
                features=v_data.get("features", [])
            )
            db.add(vehicle)
            count += 1

    db.commit()
    logger.info(f"Successfully seeded {count} vehicles.")
    return count


def seed_all(db: Session) -> None:
    """Run all seeding operations."""
    seed_personas(db)
    seed_vehicles(db)
