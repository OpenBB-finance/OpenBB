"""OpenBB-core-first data loader tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from openbb_quant_ml.service import data_loader as dl


def _price_frame(start: str, periods: int = 30) -> pd.DataFrame:
    idx = pd.date_range(start, periods=periods, freq="B")
    return pd.DataFrame(
        {
            "date": idx,
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.5,
            "volume": 1_000_000.0,
            "symbol": "AAPL",
        }
    )


def test_load_symbol_prices_uses_provider_source_when_core_fetch_succeeds(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "AAPL.parquet"
    monkeypatch.setattr(dl, "_cache_path", lambda _symbol: cache_path)
    monkeypatch.setattr(dl, "_fetch_obb_prices", lambda **_kwargs: _price_frame("2025-01-01"))
    monkeypatch.setattr(dl, "_fetch_yfinance_prices", lambda **_kwargs: (pd.DataFrame(), None))

    seen_sources: list[str] = []

    def _capture(symbol: str, frame: pd.DataFrame, source: str = "yfinance") -> None:  # noqa: ARG001
        seen_sources.append(source)

    monkeypatch.setattr(dl, "update_data_version", _capture)

    output = dl.load_symbol_prices(
        symbol="AAPL",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 2, 28),
        provider="fmp",
    )
    assert not output.empty
    assert seen_sources and seen_sources[-1] == "fmp"


def test_load_symbol_prices_falls_back_to_yfinance_when_core_fetch_empty(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    cache_path = tmp_path / "AAPL.parquet"
    monkeypatch.setattr(dl, "_cache_path", lambda _symbol: cache_path)
    monkeypatch.setattr(dl, "_fetch_obb_prices", lambda **_kwargs: pd.DataFrame())
    monkeypatch.setattr(
        dl,
        "_fetch_yfinance_prices",
        lambda **_kwargs: (_price_frame("2025-01-01"), None),
    )

    seen_sources: list[str] = []

    def _capture(symbol: str, frame: pd.DataFrame, source: str = "yfinance") -> None:  # noqa: ARG001
        seen_sources.append(source)

    monkeypatch.setattr(dl, "update_data_version", _capture)

    output = dl.load_symbol_prices(
        symbol="AAPL",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 2, 28),
        provider="polygon",
    )
    assert not output.empty
    assert seen_sources and seen_sources[-1] == "yfinance"
