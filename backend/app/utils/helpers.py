"""Purpose: Shared utility functions for formatting, parsing, and seeding helpers."""

import json
from datetime import datetime


def format_datetime(value: datetime | None) -> str:
    """Format datetime object into clean ISO string."""
    return value.isoformat() if value else ""


def parse_json_safely(content: str) -> dict:
    """Safely parse JSON content falling back to empty dict on failure."""
    try:
        return json.loads(content)
    except Exception:
        return {}
