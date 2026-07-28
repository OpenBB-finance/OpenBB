"""Tests for the relative-rotation router shell."""

from __future__ import annotations

import pandas as pd
import pytest

from openbb_technical.indicators.relative_rotation import relative_rotation
from openbb_technical.relative_rotation import (
    RelativeRotationData,
    RelativeRotationQueryParams,
)


@pytest.fixture(scope="module")
def multi_symbol_records() -> list[dict]:
    """3-symbol × 600-day synthetic price history; matches the existing relative-rotation tests."""
    dates = pd.date_range("2020-01-01", periods=600, freq="D")
    records: list[dict] = []
    for offset, symbol in enumerate(["AAPL", "MSFT", "SPY"]):
        for i, dt in enumerate(dates):
            records.append(
                {
                    "date": dt.strftime("%Y-%m-%d"),
                    "symbol": symbol,
                    "close": float(100 + offset * 10 + i * (1 + offset * 0.1)),
                    "volume": float(
                        1_000_000 + offset * 50_000 + i * (10 + offset * 3)
                    ),
                }
            )
    return records


class TestRelativeRotationRouter:
    @pytest.mark.asyncio
    async def test_returns_relative_rotation_data(self, multi_symbol_records):
        result = await relative_rotation(
            RelativeRotationQueryParams(data=multi_symbol_records, benchmark="SPY")
        )
        assert isinstance(result.results, RelativeRotationData)
        assert result.results.benchmark == "SPY"
        assert "AAPL" in result.results.symbols
