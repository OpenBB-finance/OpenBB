"""Trading market-data service wrappers."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd

from openbb_quant_ml.service.data_loader import load_market_data


def load_trading_market_data(
    *,
    symbols: list[str],
    lookback_days: int,
    provider: str,
    max_workers: int,
) -> tuple[dict[str, pd.DataFrame], list[str]]:
    """Load recent OHLCV history for one trading scan."""
    end_date = date.today()
    start_date = end_date - timedelta(days=max(lookback_days, 120))
    return load_market_data(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        provider=provider,
        max_workers=max_workers,
    )
