"""Background scheduler for macro regime refresh."""

from __future__ import annotations

import atexit
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

LOGGER = logging.getLogger(__name__)

try:
    from apscheduler.schedulers.background import BackgroundScheduler
except Exception:  # noqa: BLE001
    BackgroundScheduler = None

_scheduler: Any | None = None
_last_market_refresh_at: str | None = None
_last_fred_update_at: str | None = None
_scheduler_registered = False


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _refresh_market_regime() -> None:
    global _last_market_refresh_at
    try:
        from openbb_quant_ml.service.macro_update import update_market_symbols

        update_market_symbols(["SPY", "HYG", "TLT", "VIX", "GLD", "DBC"])
        _last_market_refresh_at = _utc_now_iso()
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Market regime refresh failed: %s", exc, exc_info=True)


def _daily_fred_update() -> None:
    global _last_fred_update_at
    try:
        from openbb_quant_ml.service.macro_update import update_all_defaults

        update_all_defaults(compute_features=True)
        _last_fred_update_at = _utc_now_iso()
    except Exception as exc:  # noqa: BLE001
        LOGGER.warning("Daily FRED update failed: %s", exc, exc_info=True)


def _register_atexit() -> None:
    global _scheduler_registered
    if _scheduler_registered:
        return
    atexit.register(stop_regime_scheduler)
    _scheduler_registered = True


def start_regime_scheduler() -> bool:
    """Start scheduler if available and not already running."""
    global _scheduler
    if _scheduler is not None:
        return True
    if BackgroundScheduler is None:
        LOGGER.warning("APScheduler is unavailable; regime scheduler is disabled.")
        return False
    scheduler = BackgroundScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        _refresh_market_regime,
        "interval",
        minutes=30,
        id="market_regime_refresh",
        replace_existing=True,
    )
    scheduler.add_job(
        _daily_fred_update,
        "cron",
        hour=7,
        minute=0,
        id="fred_daily_update",
        replace_existing=True,
    )
    scheduler.start()
    _scheduler = scheduler
    _register_atexit()
    return True


def ensure_scheduler_started() -> bool:
    """Lazy singleton start hook for router endpoints."""
    return start_regime_scheduler()


def stop_regime_scheduler() -> None:
    """Stop scheduler if running."""
    global _scheduler
    if _scheduler is None:
        return
    try:
        _scheduler.shutdown(wait=False)
    except Exception:  # noqa: BLE001
        pass
    _scheduler = None


def trigger_regime_refresh() -> dict[str, Any]:
    """Trigger immediate market/fred refresh."""
    _refresh_market_regime()
    _daily_fred_update()
    return {"status": "ok", "updated_at": _utc_now_iso()}


def get_scheduler_status() -> dict[str, Any]:
    """Return current scheduler state and next run hints."""
    running = _scheduler is not None
    next_market_refresh: str | None = None
    next_fred_update: str | None = None
    if running:
        try:
            market_job = _scheduler.get_job("market_regime_refresh")
            fred_job = _scheduler.get_job("fred_daily_update")
            if market_job and market_job.next_run_time:
                next_market_refresh = (
                    market_job.next_run_time.astimezone(UTC)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
            if fred_job and fred_job.next_run_time:
                next_fred_update = (
                    fred_job.next_run_time.astimezone(UTC)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
        except Exception:  # noqa: BLE001
            pass
    if next_market_refresh is None and _last_market_refresh_at:
        next_market_refresh = (
            datetime.fromisoformat(_last_market_refresh_at.replace("Z", "+00:00"))
            + timedelta(minutes=30)
        ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return {
        "running": running,
        "last_market_refresh": _last_market_refresh_at,
        "last_fred_update": _last_fred_update_at,
        "next_market_refresh": next_market_refresh,
        "next_fred_update": next_fred_update,
    }
