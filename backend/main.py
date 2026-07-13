"""Purpose: FastAPI application entry point, registering routes and database setup."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
import app.models

# Import routers
from app.routes.session_routes import router as session_router
from app.routes.report_routes import router as report_router
from app.routes.vehicle_routes import router as vehicle_router
from app.routes.test_routes import router as test_router
from app.websocket.chat_socket import router as websocket_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events manager to set up database tables in development."""
    logger.info("Starting FastAPI application...")
    
    if settings.app_env == "development":
        logger.info("Development mode: Verifying/creating database tables via create_all()...")
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables verified.")
        except Exception as e:
            logger.error(f"Error during development table create_all: {e}")
            
    yield
    logger.info("Shutting down FastAPI application...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    app = FastAPI(
        title="AI Car Sales Training Simulator API",
        version="0.1.0",
        lifespan=lifespan
    )

    # Configure CORS middleware
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    if settings.app_env == "production":
        origins = [o for o in origins if o != "*"]
        if not origins:
            logger.warning("CORS_ORIGINS is empty in production. CORS requests might fail.")
    else:
        if "*" in origins or not origins:
            origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(session_router, prefix="/api/v1")
    app.include_router(report_router, prefix="/api/v1")
    app.include_router(vehicle_router, prefix="/api/v1")
    app.include_router(test_router, prefix="/api/v1")
    app.include_router(websocket_router)

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        """Simple health check endpoint for monitoring and startup validation."""
        return {"status": "ok"}

    return app


app = create_app()
