"""Macro market symbol-alias tests."""

from __future__ import annotations

import pandas as pd
from openbb_quant_ml.service import macro_market as mm


def test_market_symbol_alias_fetch_and_storage(monkeypatch):
    calls: list[str] = []
    upserted: dict[str, str] = {}
    idx = pd.date_range("2025-01-01", periods=5, freq="B")

    def _mock_cfg():
        return {
            "defaults": {
                "market_fallback_order": ["yfinance", "cache"],
                "market_symbol_aliases": {"GC": "GC=F", "HG": "HG=F"},
            }
        }

    def _mock_fetch(symbol: str, start, end):  # noqa: ANN001
        calls.append(symbol)
        return pd.Series([10.0, 10.5, 11.0, 10.9, 11.1], index=idx, dtype=float)

    def _mock_upsert(source: str, series_id: str, rows):  # noqa: ANN001
        upserted["source"] = source
        upserted["series_id"] = series_id
        upserted["count"] = str(len(rows))

    monkeypatch.setattr(mm, "load_macro_config", _mock_cfg)
    monkeypatch.setattr(mm, "_fetch_yfinance", _mock_fetch)
    monkeypatch.setattr(mm, "load_observations", lambda *args, **kwargs: [])
    monkeypatch.setattr(mm, "upsert_observations", _mock_upsert)

    out, source, warning = mm.get_market_series("GC", start=None, end=None)
    assert source == "yfinance"
    assert warning is None
    assert calls == ["GC=F"]
    assert out.name == "GC"
    assert upserted["source"] == "MARKET"
    assert upserted["series_id"] == "GC"
