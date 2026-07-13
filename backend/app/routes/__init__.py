"""Purpose: API route package exports."""

from app.routes.session_routes import router as session_routes
from app.routes.report_routes import router as report_routes
from app.routes.vehicle_routes import router as vehicle_routes
from app.routes.test_routes import router as test_routes

__all__ = ["session_routes", "report_routes", "vehicle_routes", "test_routes"]
