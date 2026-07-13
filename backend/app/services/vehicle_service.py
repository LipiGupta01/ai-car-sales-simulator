"""Purpose: Service for vehicle loading, seeding, and database queries."""

import json
import os
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle


class VehicleService:
    """Provides vehicle lookup and recommendation helpers."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_vehicles(self) -> list[Vehicle]:
        """Retrieve all vehicles stored in the database."""
        vehicles = self.db.query(Vehicle).all()
        if not vehicles:
            # Auto-seed if database is empty
            self.seed_vehicles()
            vehicles = self.db.query(Vehicle).all()
        return vehicles

    def get_vehicle_by_key(self, key: str) -> Vehicle | None:
        """Find a vehicle record by its string key."""
        return self.db.query(Vehicle).filter(Vehicle.key == key).first()

    def seed_vehicles(self) -> None:
        """Seed vehicles from seed_data/vehicles.json if not present."""
        seed_paths = [
            "../seed_data/vehicles.json",
            "seed_data/vehicles.json",
            "../../seed_data/vehicles.json"
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

        for v_data in data:
            # Check if exists
            existing = self.db.query(Vehicle).filter(Vehicle.key == v_data["id"]).first()
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
                    summary=f"{v_data['year']} {v_data['make']} {v_data['model']} has MSRP {v_data['msrp']}.",
                    features=v_data.get("features", [])
                )
                self.db.add(vehicle)
        self.db.commit()
