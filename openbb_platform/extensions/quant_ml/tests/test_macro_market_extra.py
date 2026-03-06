"""Additional coverage tests for macro market data loader."""

from __future__ import annotations

from datetime import date

import pandas as pd
from openbb_quant_ml.service import macro_market as mm


def test_row_series_converters_roundtrip() -> None:
    rows = [
        {"date": "2026-01-02", "value": 100.0},
        {"date": "2026-01-03", "value": 101.5},
    ]
    series = mm._parse_rows_to_series(rows)
    assert len(series) == 2
    out = mm._rows_from_series(series)
    assert len(out) == 2
    assert out[0]["date"] == "2026-01-02"


def test_get_market_series_uses_cache_fallback(monkeypatch) -> None:
    idx = pd.date_range("2026-01-01", periods=3, freq="D")
    cached = pd.Series([10.0, 11.0, 12.0], index=idx, dtype=float)
    cached_rows = mm._rows_from_series(cached)

    monkeypatch.setattr(
        mm,
        "load_macro_config",
        lambda: {
            "defaults": {
                "market_fallback_order": ["yfinance", "cache"],
                "market_symbol_aliases": {},
            }
        },
    )
    monkeypatch.setattr(mm, "load_observations", lambda *args, **kwargs: cached_rows)
    monkeypatch.setattr(mm, "_fetch_yfinance", lambda *args, **kwargs: pd.Series(dtype=float))
    monkeypatch.setattr(mm, "upsert_observations", lambda *args, **kwargs: None)

    series, source, warning = mm.get_market_series("SPY", start=None, end=None)
    assert source == "cache"
    assert not series.empty
    assert warning == "market_yfinance_fetch_failed"


def test_get_market_series_handles_futures_alias_for_openbb_http(monkeypatch) -> None:
    monkeypatch.setattr(
        mm,
        "load_macro_config",
        lambda: {
            "defaults": {
                "market_fallback_order": ["openbb_http", "cache"],
                "market_symbol_aliases": {"VIXCLS": "^VIX=F"},
            }
        },
    )
    monkeypatch.setattr(mm, "load_observations", lambda *args, **kwargs: [])
    monkeypatch.setattr(mm, "upsert_observations", lambda *args, **kwargs: None)
    monkeypatch.setattr(mm, "_fetch_openbb_http", lambda *args, **kwargs: pd.Series(dtype=float))

    series, source, warning = mm.get_market_series(
        "VIXCLS", start=date(2026, 1, 1), end=date(2026, 1, 31)
    )
    assert series.empty
    assert source == "unavailable"
    assert warning in {"futures_symbol_openbb_http_not_supported", "market_data_unavailable"}
