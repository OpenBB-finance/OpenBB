"""Step: incremental market data update."""

from __future__ import annotations

import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from openbb_quant_ml.jobs.logging import append_heartbeat
from openbb_quant_ml.service.data_loader import load_market_data
from openbb_quant_ml.service.universe import get_symbols_for_universe


def run(config: dict[str, Any]) -> dict[str, Any]:
    universe_id = config.get("universe_id")
    symbols = get_symbols_for_universe(universe_id)
    lookback_years = int(config.get("lookback_years", 5))
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * lookback_years)
    run_dir_raw = str(config.get("_job_run_dir", "")).strip()
    run_dir = Path(run_dir_raw) if run_dir_raw else None

    timeout_sec = int(config.get("market_data_timeout_sec", 20))
    retry = int(config.get("market_data_retry", 2))
    workers = int(config.get("market_data_workers", 6))
    backoff = float(config.get("market_data_backoff_base", 2.0))
    heartbeat_interval = int(config.get("heartbeat_interval_sec", 30))

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
                    step="update_market_data",
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
        "symbols_requested": len(symbols),
        "symbols_loaded": len(datasets),
        "symbols_skipped": len(skipped),
        "market_data_timeout_sec": timeout_sec,
        "market_data_retry": retry,
        "market_data_workers": workers,
    }
