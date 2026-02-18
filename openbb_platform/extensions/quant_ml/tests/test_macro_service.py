"""Macro service payload tests."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd
from openbb_quant_ml.macro_models import MacroExpressionRequest, MacroSeriesQuery
from openbb_quant_ml.service import macro_service as ms


def test_get_series_response_with_stub(monkeypatch):
    idx = pd.date_range("2025-01-01", periods=10, freq="D")
    series = pd.Series(range(10), index=idx, dtype=float)

    monkeypatch.setattr(
        ms,
        "_get_series",
        lambda key, start, end: (
            series,
            {
                "key": key,
                "title": key,
                "units": "level",
                "frequency": "daily",
                "source": "stub",
                "lag_applied": "P0D",
            },
            None,
        ),
    )

    payload = ms.get_series_response(
        MacroSeriesQuery(key="TEST", transform="level", freq="D", fill="ffill")
    )
    assert payload.status == "ok"
    assert len(payload.data) == 10


def test_expression_response_error():
    payload = ms.evaluate_expression_response(
        MacroExpressionRequest(expr="__import__('os')", freq="D", fill="ffill", transform="level")
    )
    assert payload.status in {"error", "insufficient_data"}


def test_unknown_symbol_defaults_to_market():
    source, series_id = ms._normalize_key("GLD")
    assert source == "MARKET"
    assert series_id == "GLD"


def test_get_series_response_error_payload_is_shape_stable(monkeypatch):
    def raise_no_data(key, start, end):  # noqa: ANN001
        raise ValueError("No market observations found for symbol: GLD")

    monkeypatch.setattr(ms, "_get_series", raise_no_data)
    payload = ms.get_series_response(MacroSeriesQuery(key="GLD", transform="level", freq="D", fill="ffill"))
    assert payload.status == "insufficient_data"
    assert payload.data == []
    assert payload.stats is not None


def test_expression_hg_gc_succeeds_with_market_alias(monkeypatch):
    idx = pd.date_range("2024-01-01", periods=40, freq="B")

    def _mock_market_series(symbol: str, start, end):  # noqa: ANN001
        key = symbol.upper()
        if key == "HG":
            values = 16.0 + np.linspace(0, 1, len(idx))
        elif key == "GC":
            values = 2.0 + np.linspace(0, 0.1, len(idx))
        else:
            values = 1.0 + np.linspace(0, 0.1, len(idx))
        return pd.Series(values, index=idx, dtype=float), "mock", None

    monkeypatch.setattr(ms, "get_market_series", _mock_market_series)
    payload = ms.evaluate_expression_response(
        MacroExpressionRequest(
            expr="((HG/16)/(GC*0.911458))*1000",
            start=date(2024, 1, 1),
            end=date(2024, 3, 31),
            freq="W",
            fill="ffill",
            transform="level",
        )
    )
    assert payload.status == "ok"
    assert len(payload.data) > 5


def test_get_copper_gold_preset_response(monkeypatch):
    idx = pd.date_range("2023-01-06", periods=60, freq="W-FRI")

    def _resolver_factory(start, end, freq, fill):  # noqa: ANN001
        def _resolver(symbol: str) -> pd.Series:
            key = symbol.upper()
            if key == "HG":
                return pd.Series(np.linspace(10.0, 20.0, len(idx)), index=idx, dtype=float)
            if key == "GC":
                return pd.Series(np.linspace(2.0, 4.0, len(idx)), index=idx, dtype=float)
            if key == "FRED:DGS10":
                return pd.Series(np.linspace(4.0, 2.0, len(idx)), index=idx, dtype=float)
            raise ValueError(symbol)

        return _resolver

    monkeypatch.setattr(ms, "_resolver_factory", _resolver_factory)
    payload = ms.get_copper_gold_preset_response(
        start=date(2023, 1, 1),
        end=date(2024, 3, 1),
        freq="W",
        fill="ffill",
        include_corr=True,
    )
    assert payload.status == "ok"
    ids = {item.id for item in payload.series}
    assert {"copper_gold_ratio", "dgs10", "rolling_corr"} <= ids
