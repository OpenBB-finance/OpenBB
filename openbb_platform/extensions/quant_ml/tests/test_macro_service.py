"""Macro service payload tests."""

from __future__ import annotations

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
