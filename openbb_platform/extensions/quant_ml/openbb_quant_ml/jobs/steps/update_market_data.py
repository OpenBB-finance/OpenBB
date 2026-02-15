"""Step: incremental market data update."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from openbb_quant_ml.service.data_loader import load_market_data
from openbb_quant_ml.service.universe import get_symbols_for_universe


def run(config: dict[str, Any]) -> dict[str, Any]:
    universe_id = config.get("universe_id")
    symbols = get_symbols_for_universe(universe_id)
    lookback_years = int(config.get("lookback_years", 5))
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * lookback_years)
    datasets, skipped = load_market_data(symbols, start_date=start_date, end_date=end_date)
    return {
        "symbols_requested": len(symbols),
        "symbols_loaded": len(datasets),
        "symbols_skipped": len(skipped),
    }
