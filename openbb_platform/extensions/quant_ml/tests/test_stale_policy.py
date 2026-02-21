"""Tests for unified stale policy logic."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from openbb_quant_ml.service import stale_policy as sp


def test_is_stale_uses_latest_progress_timestamp() -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    updated_at = (now - timedelta(minutes=120)).isoformat()
    heartbeat_at = (now - timedelta(minutes=10)).isoformat()

    stale, reason, idle = sp.is_stale(
        updated_at,
        heartbeat_at,
        None,
        timeout_minutes=90,
    )

    assert stale is False
    assert reason is None
    assert idle is not None and idle < 90


def test_is_stale_reports_idle_timeout() -> None:
    now = datetime.now(UTC).replace(microsecond=0)
    updated_at = (now - timedelta(minutes=120)).isoformat()
    heartbeat_at = (now - timedelta(minutes=95)).isoformat()

    stale, reason, idle = sp.is_stale(
        updated_at,
        heartbeat_at,
        None,
        timeout_minutes=90,
    )

    assert stale is True
    assert reason == "idle_timeout"
    assert idle is not None and idle >= 90
