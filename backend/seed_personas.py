"""Purpose: Standalone database seeder script for customer personas."""

import json
import os
import sys

# Ensure backend directory is in python search path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app.models
from app.core.database import SessionLocal, Base, engine
from app.core.seeder import seed_personas


def seed():
    """Seed personas into the database."""
    print("Initializing database tables for personas...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        seed_personas(db)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
