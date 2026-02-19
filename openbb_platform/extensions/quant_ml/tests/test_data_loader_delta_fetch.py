"""Delta fetch behavior tests for market data loader."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from openbb_quant_ml.service import data_loader as dl


def _cached_frame(start: str, end: str, symbol: str = "AAPL") -> pd.DataFrame:
    dates = pd.date_range(start, end, freq="B")
    return pd.DataFrame(
        {
            "date": dates,
            "open": 100.0,
            "high": 101.0,
            "low": 99.0,
            "close": 100.5,
            "volume": 1_000_000.0,
            "symbol": symbol,
        }
    )


def test_load_symbol_prices_uses_delta_window_when_cache_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    cache_path = tmp_path / "AAPL.parquet"
    _cached_frame("2024-01-01", "2025-03-01").to_parquet(cache_path, index=False)

    monkeypatch.setattr(dl, "_cache_path", lambda symbol: cache_path)
    monkeypatch.setattr(dl, "_ensure_ssl_bundle_path", lambda: None)

    called: dict[str, str] = {}

    def _download(**kwargs):
        called["start"] = str(kwargs.get("start"))
        called["end"] = str(kwargs.get("end"))
        idx = pd.date_range("2025-02-20", "2025-03-20", freq="B")
        return pd.DataFrame(
            {
                "Open": 100.0,
                "High": 101.0,
                "Low": 99.0,
                "Close": 100.5,
                "Volume": 1_000_000.0,
            },
            index=idx,
        )

    monkeypatch.setattr(dl.yf, "download", _download)

    output = dl.load_symbol_prices(
        symbol="AAPL",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 3, 10),
    )
    assert not output.empty
    assert called["start"] == "2025-02-21"


def test_load_symbol_prices_skips_download_when_cache_covers_range(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    cache_path = tmp_path / "MSFT.parquet"
    _cached_frame("2024-01-01", "2025-12-31", symbol="MSFT").to_parquet(
        cache_path, index=False
    )

    monkeypatch.setattr(dl, "_cache_path", lambda symbol: cache_path)
    monkeypatch.setattr(dl, "_ensure_ssl_bundle_path", lambda: None)

    def _unexpected_download(**kwargs):
        raise AssertionError("download should not be called when cache has coverage")

    monkeypatch.setattr(dl.yf, "download", _unexpected_download)

    output = dl.load_symbol_prices(
        symbol="MSFT",
        start_date=date(2025, 5, 1),
        end_date=date(2025, 5, 31),
    )
    assert not output.empty
    assert pd.Timestamp(output["date"].min()).date() >= date(2025, 5, 1)
