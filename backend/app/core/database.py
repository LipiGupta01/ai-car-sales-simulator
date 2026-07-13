"""Purpose: SQLAlchemy engine, session factory, and Base model setup."""

from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


import logging
logger = logging.getLogger("database")

db_url = settings.database_url
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = None

if db_url.startswith("postgresql"):
    try:
        # Create engine and try a test connection to verify PostgreSQL is online
        temp_engine = create_engine(db_url, pool_pre_ping=True)
        with temp_engine.connect() as connection:
            pass
        engine = temp_engine
        logger.info("Successfully connected to PostgreSQL database.")
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL at {db_url}: {e}")
        if settings.app_env == "production":
            logger.error("SQLite fallback is disabled in production. Database connection failure is critical.")
            raise e
        logger.warning("Falling back to SQLite (sqlite:///./app.db) for local development.")
        db_url = "sqlite:///./app.db"
        engine = None

if engine is None:
    # Use SQLite or other fallback database
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {}
    )
    logger.info(f"Database engine initialized using URL: {db_url}")

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request-scoped dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
