"""Macro expression parser tests."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from openbb_quant_ml.service.macro_expression import MacroExpressionError, evaluate_expression


def _resolver(symbol: str) -> pd.Series:
    idx = pd.date_range("2025-01-01", periods=120, freq="B")
    if symbol in {"GLD", "SPY"}:
        base = 100.0 if symbol == "SPY" else 50.0
        values = base + np.linspace(0, 10, len(idx))
        return pd.Series(values, index=idx, dtype=float)
    if symbol == "FRED:UNRATE":
        m_idx = pd.date_range("2020-01-31", periods=60, freq="ME")
        values = np.linspace(3.5, 5.0, len(m_idx))
        return pd.Series(values, index=m_idx, dtype=float)
    raise MacroExpressionError(f"unknown symbol {symbol}")


def test_basic_expressions():
    ratio = evaluate_expression("GLD/SPY", resolver=_resolver)
    assert ratio.series.dropna().shape[0] > 10
    assert "GLD" in ratio.dependencies
    assert "SPY" in ratio.dependencies

    z = evaluate_expression("zscore(GLD/SPY)", resolver=_resolver)
    assert z.series.dropna().shape[0] > 10

    corr = evaluate_expression("rolling_corr(GLD,SPY,60)", resolver=_resolver)
    assert corr.series.dropna().shape[0] > 10


def test_fred_expression():
    out = evaluate_expression("FRED:UNRATE", resolver=_resolver)
    assert out.series.dropna().shape[0] > 12
    assert out.dependencies == ["FRED:UNRATE"]


def test_forbidden_expression():
    with pytest.raises(MacroExpressionError):
        evaluate_expression("__import__('os').system('whoami')", resolver=_resolver)


def test_equals_token_is_not_allowed():
    with pytest.raises(MacroExpressionError):
        evaluate_expression("GC=F", resolver=_resolver)
