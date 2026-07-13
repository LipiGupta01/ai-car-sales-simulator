"""Purpose: Standalone database seeder script for vehicle specifications."""

import json
import os
import sys

# Ensure backend directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app.models
from app.core.database import SessionLocal, Base, engine
from app.models.vehicle import Vehicle


def seed():
    """Seed vehicles into the database."""
    print("Initializing database tables for vehicles...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Locate vehicles.json
    seed_paths = [
        "seed_data/vehicles.json",
        "../seed_data/vehicles.json",
        "backend/seed_data/vehicles.json"
    ]
    seed_path = None
    for p in seed_paths:
        if os.path.exists(p):
            seed_path = p
            break
            
    if not seed_path:
        print("Error: Could not locate seed_data/vehicles.json")
        sys.exit(1)
        
    print(f"Reading vehicle seed data from {seed_path}...")
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
            print(f"Adding vehicle: {v_data['year']} {v_data['make']} {v_data['model']} ({v_data['id']})")
            
    db.commit()
    db.close()
    print(f"Successfully seeded {count} new vehicle entries.")


if __name__ == "__main__":
    seed()
