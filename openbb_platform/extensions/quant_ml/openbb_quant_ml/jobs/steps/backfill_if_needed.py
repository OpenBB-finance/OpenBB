"""Step: selective market-data backfill.

Compares the latest cached market date per symbol against a staleness
threshold and only re-downloads symbols whose data is out of date.  If
every symbol is already fresh the step short-circuits to a no-op.
"""

from __future__ import annotations

import logging
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from openbb_quant_ml.jobs.logging import append_heartbeat
from openbb_quant_ml.service.data_loader import load_market_data
from openbb_quant_ml.service.storage import get_run_dir
from openbb_quant_ml.service.universe import get_symbols_for_universe

logger = logging.getLogger(__name__)

_DEFAULT_STALENESS_DAYS = 3
_DEFAULT_LOOKBACK_YEARS = 3


def _coerce_date(value: Any, fallback: date) -> date:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return fallback
    return fallback


def _detect_stale_symbols(
    symbols: list[str],
    run_id: str | None,
    staleness_days: int,
) -> list[str]:
    """Return symbols whose latest cached data is older than *staleness_days*.

    Falls back to returning all symbols when no cached run is available.
    """
    if not run_id:
        return symbols

    run_dir = get_run_dir(run_id)
    market_path = run_dir / "market_data.parquet"
    if not market_path.exists():
        return symbols

    try:
        import pandas as pd

        market = pd.read_parquet(market_path, columns=["date", "symbol"])
        if market.empty:
            return symbols

        market["date"] = pd.to_datetime(market["date"])
        latest_by_symbol = market.groupby("symbol")["date"].max()
        cutoff = pd.Timestamp(date.today() - timedelta(days=staleness_days))

        stale = set()
        for symbol in symbols:
            if symbol not in latest_by_symbol.index or latest_by_symbol[symbol] < cutoff:
                stale.add(symbol)

        if not stale:
            return []

        return sorted(stale)
    except Exception:  # noqa: BLE001
        logger.warning("Stale-symbol detection failed; falling back to full update.")
        return symbols


def run_market_update(config: dict[str, Any]) -> dict[str, Any]:
    """Load market data for the provided symbol list."""
    symbols = [str(sym).strip() for sym in config.get("symbols", []) if str(sym).strip()]
    if not symbols:
        return {
            "status": "skipped",
            "symbols_loaded": 0,
            "symbols_skipped": 0,
            "message": "No symbols requested for update.",
        }

    end_default = date.today()
    end_date = _coerce_date(config.get("end_date"), end_default)
    start_default = end_date - timedelta(days=365 * _DEFAULT_LOOKBACK_YEARS)
    start_date = _coerce_date(config.get("start_date"), start_default)

    run_dir_raw = str(config.get("_job_run_dir", "")).strip()
    run_dir = Path(run_dir_raw) if run_dir_raw else None
    timeout_sec = int(config.get("market_data_timeout_sec", 20))
    retry = int(config.get("market_data_retry", 2))
    workers = int(config.get("market_data_workers", 6))
    backoff = float(config.get("market_data_backoff_base", 2.0))
    heartbeat_interval = int(config.get("heartbeat_interval_sec", 30))
    heartbeat_step = str(config.get("heartbeat_step", "backfill_if_needed"))

    started = time.monotonic()
    last_heartbeat_ts = started
    last_heartbeat_processed = 0

    def _progress(processed: int, total: int, symbol: str, loaded: bool) -> None:
        nonlocal last_heartbeat_ts, last_heartbeat_processed
        now = time.monotonic()
        processed_delta = processed - last_heartbeat_processed
        if (
            processed_delta >= 50
            or (now - last_heartbeat_ts) >= float(max(5, heartbeat_interval))
            or processed >= total
        ):
            if run_dir is not None:
                append_heartbeat(
                    run_dir=run_dir,
                    step=heartbeat_step,
                    processed=processed,
                    total=total,
                    elapsed_sec=now - started,
                )
            last_heartbeat_ts = now
            last_heartbeat_processed = processed

    datasets, skipped = load_market_data(
        symbols,
        start_date=start_date,
        end_date=end_date,
        progress_callback=_progress,
        timeout_sec=timeout_sec,
        retry=retry,
        backoff_base=backoff,
        max_workers=workers,
    )
    return {
        "status": "ok",
        "symbols_loaded": len(datasets),
        "symbols_skipped": len(skipped),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
    }


def run(config: dict[str, Any]) -> dict[str, Any]:
    """Selectively backfill market data for stale symbols only.

    Configuration keys:
      - ``universe_id``: symbol universe to use.
      - ``run_id``: latest completed run for staleness check.
      - ``backfill_staleness_days``: number of days before data is
        considered stale (default: 3).
      - ``backfill_lookback_years``: how far back to fetch for missing
        symbols (default: 3).
      - ``backfill_force_full``: if ``true``, skip staleness check and
        update everything (equivalent to the legacy behaviour).
    """
    # Backward-compatible escape hatch for legacy callers/tests that
    # monkeypatch run_market_update directly.
    if config.get("universe_id") is None and not config.get("symbols"):
        return run_market_update(config)

    universe_id = config.get("universe_id")
    symbols = get_symbols_for_universe(universe_id)
    staleness_days = int(config.get("backfill_staleness_days", _DEFAULT_STALENESS_DAYS))
    lookback_years = int(config.get("backfill_lookback_years", _DEFAULT_LOOKBACK_YEARS))
    force_full = bool(config.get("backfill_force_full", False))
    run_id = str(config.get("run_id", "")).strip() or None

    end_date = date.today()
    start_date = end_date - timedelta(days=365 * lookback_years)

    if force_full:
        stale_symbols = symbols
    else:
        stale_symbols = _detect_stale_symbols(symbols, run_id, staleness_days)

    if not stale_symbols:
        return {
            "status": "skipped",
            "message": "All symbols are up-to-date; no backfill required.",
            "symbols_total": len(symbols),
            "symbols_stale": 0,
        }

    # Narrow the fetch window when only a small portion is stale.
    if not force_full and len(stale_symbols) < len(symbols):
        start_date = end_date - timedelta(days=staleness_days + 30)

    update_result = run_market_update(
        {
            **config,
            "symbols": stale_symbols,
            "start_date": start_date,
            "end_date": end_date,
            "heartbeat_step": "backfill_if_needed",
        }
    )

    return {
        "status": str(update_result.get("status", "ok")),
        "symbols_total": len(symbols),
        "symbols_stale": len(stale_symbols),
        "symbols_loaded": int(update_result.get("symbols_loaded", 0)),
        "symbols_skipped": int(update_result.get("symbols_skipped", 0)),
        "start_date": str(update_result.get("start_date", start_date.isoformat())),
        "end_date": str(update_result.get("end_date", end_date.isoformat())),
        "staleness_days": staleness_days,
        "force_full": force_full,
    }
