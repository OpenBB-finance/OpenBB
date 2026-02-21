"""Tests for signal contract schema helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from openbb_quant_ml.service.signal_schema import (
    REQUIRED_SIGNAL_COLUMNS,
    build_signal_contract,
    validate_signal_contract,
)


def test_build_signal_contract_has_required_columns() -> None:
    rows = pd.DataFrame(
        [
            {"symbol": "AAPL", "predicted_return": 0.02, "confidence": 0.8, "z_score": 1.2},
            {"symbol": "MSFT", "predicted_return": 0.01, "confidence": 0.7, "z_score": 0.7},
        ]
    )
    out = build_signal_contract(
        signal_rows=rows,
        as_of_date="2026-02-21",
        model_version="m1",
        feature_set_version="f1",
    )
    assert list(out.columns) == list(REQUIRED_SIGNAL_COLUMNS)
    assert out.loc[0, "ticker"] == "AAPL"
    assert int(out.loc[0, "rank"]) == 1


def test_validate_signal_contract_raises_on_missing_columns() -> None:
    frame = pd.DataFrame([{"ticker": "AAPL"}])
    with pytest.raises(ValueError):
        validate_signal_contract(frame)

