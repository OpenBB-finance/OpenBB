"""Macro regime and alert tests."""

from __future__ import annotations

import numpy as np
import pandas as pd

from openbb_quant_ml.service import macro_alerts, macro_regime


def _resolver(symbol: str) -> pd.Series:
    idx = pd.date_range("2023-01-01", periods=520, freq="B")
    if symbol in {"SPY", "IEF", "GLD"}:
        base = {"SPY": 100.0, "IEF": 95.0, "GLD": 80.0}[symbol]
        values = base + np.cumsum(np.random.default_rng(42).normal(0.02, 0.5, len(idx)))
        return pd.Series(values, index=idx, dtype=float)

    macro_map = {
        "FRED:VIXCLS": (18.0, 2.0),
        "FRED:BAMLH0A0HYM2": (4.5, 0.8),
        "FRED:CPIAUCSL": (250.0, 1.5),
        "FRED:PCEPILFE": (120.0, 0.8),
        "FRED:T10YIE": (2.2, 0.15),
        "FRED:INDPRO": (100.0, 0.6),
        "FRED:PAYEMS": (140.0, 0.9),
        "FRED:RSAFS": (400.0, 2.0),
        "FRED:M2SL": (15000.0, 60.0),
        "FRED:NFCI": (0.0, 0.1),
        "FRED:BAA10Y": (2.0, 0.3),
    }
    if symbol in macro_map:
        mean, std = macro_map[symbol]
        m_idx = pd.date_range("2015-01-31", periods=130, freq="ME")
        values = mean + np.cumsum(np.random.default_rng(7).normal(0.0, std, len(m_idx)))
        return pd.Series(values, index=m_idx, dtype=float)
    raise ValueError(symbol)


def test_regime_score_range():
    frame = macro_regime.compute_regime_scores(resolver=_resolver, freq="W", fill="ffill")
    assert not frame.empty
    assert set(frame.columns) == {
        "risk_on_score",
        "inflation_score",
        "growth_score",
        "liquidity_score",
        "credit_stress_score",
    }
    latest = frame.iloc[-1]
    for key in frame.columns:
        value = float(latest[key])
        assert 0.0 <= value <= 100.0


def test_alert_eval_non_crash():
    frame = macro_regime.compute_regime_scores(resolver=_resolver, freq="W", fill="ffill")
    current = macro_alerts.evaluate_alerts(frame, resolver=_resolver)
    assert isinstance(current, list)
