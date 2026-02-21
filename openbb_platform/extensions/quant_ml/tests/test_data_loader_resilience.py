"""Tests for resilient market data loading controls."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd
import pytest
from openbb_quant_ml.service import data_loader as dl


def _sample_frame(days: int = 140) -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=days, freq="D")
    return pd.DataFrame(
        {
            "Open": 100.0,
            "High": 101.0,
            "Low": 99.0,
            "Close": 100.0,
            "Volume": 1_000_000,
        },
        index=idx,
    )


def test_load_symbol_prices_retries_after_download_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = {"count": 0}
    cache_path = tmp_path / "AAPL.parquet"
    monkeypatch.setattr(dl, "_cache_path", lambda symbol: cache_path)

    def _download(**kwargs):  # noqa: ANN001, ARG001
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("transient")
        return _sample_frame()

    monkeypatch.setattr(dl.yf, "download", _download)

    out = dl.load_symbol_prices(
        symbol="AAPL",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 4, 1),
        retry=2,
        timeout_sec=1,
    )
    assert not out.empty
    assert calls["count"] == 2


def test_load_market_data_reports_progress_with_workers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _load_symbol_prices(symbol: str, **kwargs):  # noqa: ANN001, ARG001
        if symbol == "BAD":
            raise RuntimeError("broken")
        size = 130 if symbol == "GOOD" else 40
        dates = pd.date_range("2024-01-01", periods=size, freq="D")
        return pd.DataFrame(
            {
                "date": dates,
                "open": 1.0,
                "high": 1.0,
                "low": 1.0,
                "close": 1.0,
                "volume": 1.0,
                "symbol": symbol,
            }
        )

    monkeypatch.setattr(dl, "load_symbol_prices", _load_symbol_prices)
    progress_events: list[tuple[int, int, str, bool]] = []

    datasets, skipped = dl.load_market_data(
        ["GOOD", "SHORT", "BAD"],
        start_date=date(2024, 1, 1),
        end_date=date(2024, 6, 1),
        max_workers=3,
        progress_callback=lambda p, t, s, ok: progress_events.append((p, t, s, ok)),
    )

    assert "GOOD" in datasets
    assert "SHORT" in skipped
    assert "BAD" in skipped
    assert len(progress_events) == 3
