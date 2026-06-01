"""Time helpers."""

from datetime import UTC, datetime


def utc_now_iso() -> str:
    """Return current UTC time."""
    return datetime.now(UTC).isoformat()
