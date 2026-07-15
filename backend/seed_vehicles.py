"""Purpose: Standalone database seeder script for vehicle specifications."""

import json
import os
import sys

# Ensure backend directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app.models
from app.core.database import SessionLocal, Base, engine
from app.core.seeder import seed_vehicles


def seed():
    """Seed vehicles into the database."""
    print("Initializing database tables for vehicles...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_vehicles(db)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
