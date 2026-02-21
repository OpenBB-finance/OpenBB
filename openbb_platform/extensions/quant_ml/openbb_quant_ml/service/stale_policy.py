"""Shared stale-run policy utilities."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

STALE_TIMEOUT_MINUTES = 90


def _is_progress_artifact(path: Path) -> bool:
    name = path.name.lower()
    if name in {"config.json", "config_used.json"}:
        return False
    if name.startswith("."):
        return False
    return True


def parse_iso_timestamp(value: str | None) -> datetime | None:
    """Parse ISO timestamp into UTC-aware datetime."""
    if not value:
        return None
    try:
        normalized = str(value).replace("Z", "+00:00")
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)
    except ValueError:
        return None


def latest_artifact_mtime(run_dir: Path) -> datetime | None:
    """Return latest artifact file mtime under run directory."""
    if not run_dir.exists():
        return None
    latest: float | None = None
    for path in run_dir.iterdir():
        if not path.is_file():
            continue
        if not _is_progress_artifact(path):
            continue
        mtime = float(path.stat().st_mtime)
        latest = mtime if latest is None else max(latest, mtime)
    if latest is None:
        return None
    return datetime.fromtimestamp(latest, tz=UTC)


def _coerce_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    if isinstance(value, str):
        return parse_iso_timestamp(value)
    return None


def latest_progress_timestamp(
    run_updated_at: Any,
    heartbeat_at: Any,
    artifact_mtime: Any,
) -> datetime | None:
    """Return latest known progress timestamp."""
    points = [
        _coerce_datetime(run_updated_at),
        _coerce_datetime(heartbeat_at),
        _coerce_datetime(artifact_mtime),
    ]
    valid = [point for point in points if point is not None]
    if not valid:
        return None
    return max(valid)


def compute_idle_minutes(
    run_updated_at: Any,
    heartbeat_at: Any,
    artifact_mtime: Any,
) -> float | None:
    """Return idle minutes since latest known progress timestamp."""
    latest = latest_progress_timestamp(run_updated_at, heartbeat_at, artifact_mtime)
    if latest is None:
        return None
    idle = (datetime.now(UTC) - latest).total_seconds() / 60.0
    return max(0.0, float(idle))


def is_stale(
    run_updated_at: Any,
    heartbeat_at: Any,
    artifact_mtime: Any,
    *,
    timeout_minutes: int = STALE_TIMEOUT_MINUTES,
) -> tuple[bool, str | None, float | None]:
    """Evaluate stale status using run update, heartbeat, and artifact timestamps."""
    idle = compute_idle_minutes(run_updated_at, heartbeat_at, artifact_mtime)
    if idle is None:
        return True, "missing_progress_timestamp", None
    stale = idle >= float(max(1, int(timeout_minutes)))
    if not stale:
        return False, None, idle
    return True, "idle_timeout", idle
